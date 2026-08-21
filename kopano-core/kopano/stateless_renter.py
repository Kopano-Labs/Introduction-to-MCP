"""Reference implementation of the KPGS Stateless Renter Protocol vNext.

The renter intentionally owns no canonical task database. Durable checkpoints and
idempotency records are delegated to a caller-supplied canonical store so replacing
this process does not transfer or lose authority.

MAO/MMAO admission is fail-closed: a stateless renter must present an earned,
evidence-backed KPGS trust grant before an orchestration cycle may execute.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Protocol
from uuid import uuid4

PROTOCOL_VERSION = "1.1"
ORCHESTRATION_CYCLES = frozenset({"mao", "mmao"})
TRUST_STATE = "trusted"
FAILURE_CODES = {
    "input_invalid",
    "policy_denied",
    "trust_not_earned",
    "capability_expired",
    "dependency_unavailable",
    "timeout",
    "execution_failed",
    "verification_failed",
    "cancelled",
}
RECOVERABILITY_VALUES = {"retry", "rehydrate", "user_action", "operator_action", "not_recoverable"}


@dataclass(frozen=True)
class TaskContext:
    tenant_id: str
    domain_id: str
    session_id: str
    task_id: str
    correlation_id: str
    governing_spec_ref: str
    skill_versions: Mapping[str, str] = field(default_factory=dict)
    orchestration_cycle: str | None = None


@dataclass(frozen=True)
class KPGSTrustGrant:
    """Evidence-backed admission grant issued after KPGS trust is earned.

    Trust is bound to a renter identity, tenant/domain boundary and explicit
    orchestration cycles. A model name, benchmark score, provider reputation or
    successful discovery handshake is never sufficient admission evidence.
    """

    grant_id: str
    renter_id: str
    tenant_id: str
    domain_id: str
    allowed_cycles: frozenset[str]
    evidence_refs: tuple[str, ...]
    expires_at: datetime
    issuer: str = "kpgs"
    trust_state: str = TRUST_STATE

    def authorization_failure(
        self,
        context: TaskContext,
        *,
        renter_id: str,
        cycle: str,
        now: datetime,
    ) -> str | None:
        if self.expires_at.tzinfo is None:
            raise ValueError("KPGSTrustGrant.expires_at must be timezone-aware")
        if now >= self.expires_at:
            return "KPGS trust grant has expired"
        if self.trust_state != TRUST_STATE:
            return f"KPGS trust_state must be {TRUST_STATE!r}"
        if not self.grant_id:
            return "KPGS trust grant_id is required"
        if self.issuer.lower() != "kpgs":
            return "KPGS trust grant must be issued by KPGS"
        if self.renter_id != renter_id:
            return "KPGS trust grant is bound to a different renter"
        if (self.tenant_id, self.domain_id) != (context.tenant_id, context.domain_id):
            return "KPGS trust grant is bound to a different tenant/domain"
        if cycle not in self.allowed_cycles:
            return f"KPGS trust grant does not authorize {cycle.upper()} entry"
        if not self.evidence_refs or any(not ref.strip() for ref in self.evidence_refs):
            return "KPGS trust requires at least one non-empty proof receipt"
        return None


@dataclass(frozen=True)
class CapabilityLease:
    lease_id: str
    tenant_id: str
    domain_id: str
    task_id: str
    allowed_operations: frozenset[str]
    allowed_resources: frozenset[str]
    expires_at: datetime

    def authorization_failure(
        self,
        context: TaskContext,
        *,
        operation: str,
        resource: str,
        now: datetime,
    ) -> tuple[str, str] | None:
        """Return failure kind/reason when this lease cannot authorize the action."""
        if self.expires_at.tzinfo is None:
            raise ValueError("CapabilityLease.expires_at must be timezone-aware")
        if now >= self.expires_at:
            return ("capability.expired", "capability lease has expired")
        if (self.tenant_id, self.domain_id, self.task_id) != (
            context.tenant_id,
            context.domain_id,
            context.task_id,
        ):
            return ("policy.denied", "capability lease is bound to a different tenant/domain/task")
        if operation not in self.allowed_operations:
            return ("policy.denied", f"operation {operation!r} is outside the capability lease")
        if resource not in self.allowed_resources:
            return ("policy.denied", f"resource {resource!r} is outside the capability lease")
        return None


@dataclass(frozen=True)
class StepOutcome:
    """Result returned by a bounded workload handler."""

    payload: Mapping[str, Any]
    checkpoint: Mapping[str, Any] | None = None
    completed: bool = False
    evidence: tuple[Mapping[str, str], ...] = ()


@dataclass(frozen=True)
class IdempotencyRecord:
    """Canonical result recorded after a side-effecting operation commits."""

    payload: Mapping[str, Any]
    checkpoint_ref: str | None
    completed: bool
    evidence: tuple[Mapping[str, str], ...] = ()


class RenterFailure(Exception):
    """Typed workload failure that maps directly onto the protocol failure envelope."""

    def __init__(self, code: str, recoverability: str, message: str) -> None:
        if code not in FAILURE_CODES:
            raise ValueError(f"unsupported renter failure code: {code}")
        if recoverability not in RECOVERABILITY_VALUES:
            raise ValueError(f"unsupported renter recoverability: {recoverability}")
        super().__init__(message)
        self.code = code
        self.recoverability = recoverability
        self.message = message[:2000]


class CanonicalRenterStore(Protocol):
    """Minimal Hub/domain-store contract required by the reference renter."""

    def load_checkpoint(self, context: TaskContext) -> Mapping[str, Any] | None: ...

    def save_checkpoint(self, context: TaskContext, checkpoint: Mapping[str, Any]) -> str: ...

    def get_idempotency(self, context: TaskContext, idempotency_key: str) -> IdempotencyRecord | None: ...

    def put_idempotency(
        self,
        context: TaskContext,
        idempotency_key: str,
        record: IdempotencyRecord,
    ) -> None: ...


WorkloadHandler = Callable[[Mapping[str, Any] | None, Mapping[str, Any]], StepOutcome]


class StatelessRenter:
    """Disposable worker that borrows context and authority for one bounded action."""

    def __init__(self, renter_id: str, store: CanonicalRenterStore, *, protocol_version: str = PROTOCOL_VERSION) -> None:
        if not renter_id:
            raise ValueError("renter_id is required")
        self.renter_id = renter_id
        self.store = store
        self.protocol_version = protocol_version
        self._accepting_work = True

    def readiness(self) -> dict[str, Any]:
        """Return process-local readiness without claiming canonical task ownership."""
        return {
            "renter_id": self.renter_id,
            "protocol_version": self.protocol_version,
            "accepting_work": self._accepting_work,
            "state_authority": "external-canonical-store",
            "orchestration_entry_policy": "kpgs-earned-trust-required-for-mao-mmao",
        }

    def begin_eviction(self) -> None:
        """Stop accepting new work; replacement renters can hydrate from the external store."""
        self._accepting_work = False

    def execute(
        self,
        *,
        context: TaskContext,
        lease: CapabilityLease,
        operation: str,
        resource: str,
        payload: Mapping[str, Any],
        handler: WorkloadHandler,
        idempotency_key: str | None,
        side_effecting: bool = True,
        now: datetime | None = None,
        trust_grant: KPGSTrustGrant | None = None,
    ) -> dict[str, Any]:
        """Execute one governed step and return a typed protocol event envelope.

        The caller supplies all task authority and durable state dependencies. The
        renter keeps no checkpoint or deduplication ledger of its own.

        If ``context.orchestration_cycle`` is MAO or MMAO, an earned KPGS trust
        grant is required before capability-scope evaluation or handler execution.
        """
        event_time = now or datetime.now(timezone.utc)
        if event_time.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        cycle = (context.orchestration_cycle or "").strip().lower()
        if context.orchestration_cycle and cycle not in ORCHESTRATION_CYCLES:
            return self._event(
                event_kind="policy.denied",
                context=context,
                lease=lease,
                payload={"operation": operation, "resource": resource},
                now=event_time,
                orchestration_cycle=cycle,
                failure={
                    "code": "input_invalid",
                    "recoverability": "operator_action",
                    "message": (
                        f"unsupported orchestration_cycle {context.orchestration_cycle!r}; "
                        f"expected one of {sorted(ORCHESTRATION_CYCLES)}"
                    ),
                },
            )

        trust_grant_id: str | None = None
        if cycle in ORCHESTRATION_CYCLES:
            if trust_grant is None:
                return self._event(
                    event_kind="policy.denied",
                    context=context,
                    lease=lease,
                    payload={"operation": operation, "resource": resource},
                    now=event_time,
                    orchestration_cycle=cycle,
                    failure={
                        "code": "trust_not_earned",
                        "recoverability": "operator_action",
                        "message": (
                            f"{cycle.upper()} entry denied: stateless renter must earn KPGS trust "
                            "and present an evidence-backed trust grant"
                        ),
                    },
                )
            trust_failure = trust_grant.authorization_failure(
                context,
                renter_id=self.renter_id,
                cycle=cycle,
                now=event_time,
            )
            if trust_failure:
                return self._event(
                    event_kind="policy.denied",
                    context=context,
                    lease=lease,
                    payload={"operation": operation, "resource": resource},
                    now=event_time,
                    orchestration_cycle=cycle,
                    trust_grant_id=trust_grant.grant_id or None,
                    failure={
                        "code": "trust_not_earned",
                        "recoverability": "operator_action",
                        "message": trust_failure,
                    },
                )
            trust_grant_id = trust_grant.grant_id

        if not self._accepting_work:
            return self._event(
                event_kind="task.failed",
                context=context,
                lease=lease,
                payload={"operation": operation, "resource": resource},
                now=event_time,
                orchestration_cycle=cycle or None,
                trust_grant_id=trust_grant_id,
                failure={
                    "code": "cancelled",
                    "recoverability": "rehydrate",
                    "message": "renter is draining for eviction; retry on a replacement renter",
                },
            )

        authorization_failure = lease.authorization_failure(
            context,
            operation=operation,
            resource=resource,
            now=event_time,
        )
        if authorization_failure:
            event_kind, message = authorization_failure
            failure_code = "capability_expired" if event_kind == "capability.expired" else "policy_denied"
            recoverability = "rehydrate" if event_kind == "capability.expired" else "operator_action"
            return self._event(
                event_kind=event_kind,
                context=context,
                lease=lease,
                payload={"operation": operation, "resource": resource},
                now=event_time,
                orchestration_cycle=cycle or None,
                trust_grant_id=trust_grant_id,
                failure={
                    "code": failure_code,
                    "recoverability": recoverability,
                    "message": message,
                },
            )

        if side_effecting and not idempotency_key:
            return self._event(
                event_kind="policy.denied",
                context=context,
                lease=lease,
                payload={"operation": operation, "resource": resource},
                now=event_time,
                orchestration_cycle=cycle or None,
                trust_grant_id=trust_grant_id,
                failure={
                    "code": "policy_denied",
                    "recoverability": "operator_action",
                    "message": "side-effecting operations require an idempotency_key",
                },
            )

        if idempotency_key:
            existing = self.store.get_idempotency(context, idempotency_key)
            if existing is not None:
                return self._event(
                    event_kind="task.completed" if existing.completed else "task.checkpointed",
                    context=context,
                    lease=lease,
                    payload={**existing.payload, "replayed": True},
                    now=event_time,
                    idempotency_key=idempotency_key,
                    checkpoint_ref=existing.checkpoint_ref,
                    evidence=existing.evidence,
                    orchestration_cycle=cycle or None,
                    trust_grant_id=trust_grant_id,
                )

        checkpoint = self.store.load_checkpoint(context)
        try:
            outcome = handler(checkpoint, payload)
        except RenterFailure as exc:
            return self._event(
                event_kind="task.failed",
                context=context,
                lease=lease,
                payload={"operation": operation, "resource": resource},
                now=event_time,
                idempotency_key=idempotency_key,
                orchestration_cycle=cycle or None,
                trust_grant_id=trust_grant_id,
                failure={
                    "code": exc.code,
                    "recoverability": exc.recoverability,
                    "message": exc.message,
                },
            )
        except Exception as exc:
            return self._event(
                event_kind="task.failed",
                context=context,
                lease=lease,
                payload={"operation": operation, "resource": resource},
                now=event_time,
                idempotency_key=idempotency_key,
                orchestration_cycle=cycle or None,
                trust_grant_id=trust_grant_id,
                failure={
                    "code": "execution_failed",
                    "recoverability": "retry",
                    "message": str(exc)[:2000],
                },
            )

        checkpoint_ref = None
        if outcome.checkpoint is not None:
            checkpoint_ref = self.store.save_checkpoint(context, outcome.checkpoint)

        if idempotency_key:
            self.store.put_idempotency(
                context,
                idempotency_key,
                IdempotencyRecord(
                    payload=dict(outcome.payload),
                    checkpoint_ref=checkpoint_ref,
                    completed=outcome.completed,
                    evidence=outcome.evidence,
                ),
            )

        return self._event(
            event_kind="task.completed" if outcome.completed else "task.checkpointed",
            context=context,
            lease=lease,
            payload={**outcome.payload, "replayed": False},
            now=event_time,
            idempotency_key=idempotency_key,
            checkpoint_ref=checkpoint_ref,
            evidence=outcome.evidence,
            orchestration_cycle=cycle or None,
            trust_grant_id=trust_grant_id,
        )

    def _event(
        self,
        *,
        event_kind: str,
        context: TaskContext,
        lease: CapabilityLease,
        payload: Mapping[str, Any],
        now: datetime,
        idempotency_key: str | None = None,
        checkpoint_ref: str | None = None,
        evidence: tuple[Mapping[str, str], ...] = (),
        failure: Mapping[str, str] | None = None,
        orchestration_cycle: str | None = None,
        trust_grant_id: str | None = None,
    ) -> dict[str, Any]:
        envelope: dict[str, Any] = {
            "protocol_version": self.protocol_version,
            "event_id": f"evt-{uuid4().hex}",
            "event_kind": event_kind,
            "tenant_id": context.tenant_id,
            "domain_id": context.domain_id,
            "session_id": context.session_id,
            "task_id": context.task_id,
            "renter_id": self.renter_id,
            "correlation_id": context.correlation_id,
            "lease_id": lease.lease_id,
            "issued_at": now.isoformat(),
            "governing_spec_ref": context.governing_spec_ref,
            "skill_versions": dict(context.skill_versions),
            "payload": dict(payload),
            "evidence": [dict(item) for item in evidence],
        }
        if orchestration_cycle:
            envelope["orchestration_cycle"] = orchestration_cycle
        if trust_grant_id:
            envelope["trust_grant_id"] = trust_grant_id
        if idempotency_key:
            envelope["idempotency_key"] = idempotency_key
        if checkpoint_ref:
            envelope["checkpoint_ref"] = checkpoint_ref
        if failure:
            envelope["failure"] = dict(failure)
        return envelope
