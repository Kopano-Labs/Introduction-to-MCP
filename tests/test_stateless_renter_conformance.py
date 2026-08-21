from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

import pytest

from kopano.stateless_renter import (
    CapabilityLease,
    IdempotencyRecord,
    KPGSTrustGrant,
    RenterFailure,
    StatelessRenter,
    StepOutcome,
    TaskContext,
)


class MemoryHubStore:
    """External canonical-store test double shared across disposable renters."""

    def __init__(self) -> None:
        self.checkpoints: dict[tuple[str, str, str], dict[str, Any]] = {}
        self.idempotency: dict[tuple[str, str, str, str], IdempotencyRecord] = {}
        self.effects: dict[str, int] = {}

    @staticmethod
    def task_key(context: TaskContext) -> tuple[str, str, str]:
        return (context.tenant_id, context.domain_id, context.task_id)

    def load_checkpoint(self, context: TaskContext) -> Mapping[str, Any] | None:
        checkpoint = self.checkpoints.get(self.task_key(context))
        return dict(checkpoint) if checkpoint is not None else None

    def save_checkpoint(self, context: TaskContext, checkpoint: Mapping[str, Any]) -> str:
        self.checkpoints[self.task_key(context)] = dict(checkpoint)
        return f"hub://checkpoint/{context.tenant_id}/{context.domain_id}/{context.task_id}"

    def get_idempotency(self, context: TaskContext, key: str) -> IdempotencyRecord | None:
        return self.idempotency.get((*self.task_key(context), key))

    def put_idempotency(self, context: TaskContext, key: str, record: IdempotencyRecord) -> None:
        self.idempotency[(*self.task_key(context), key)] = record

    def record_effect(self, key: str) -> int:
        self.effects[key] = self.effects.get(key, 0) + 1
        return self.effects[key]


def make_context(
    domain: str,
    *,
    orchestration_cycle: str | None = None,
    decision_domain: str | None = None,
    consequence_class: str | None = None,
    authority_mode: str = "execution",
) -> TaskContext:
    if orchestration_cycle:
        decision_domain = decision_domain or "software_delivery"
        consequence_class = consequence_class or "technical_change"
    return TaskContext(
        tenant_id="tenant-kopano",
        domain_id=domain,
        session_id=f"session-{domain}",
        task_id=f"task-{domain}",
        correlation_id=f"corr-{domain}",
        governing_spec_ref="governance/kpgs-vnext/stateless-renter/PROTOCOL.md",
        skill_versions={"kpgs-audit-verify-govern": "0.1.0"},
        orchestration_cycle=orchestration_cycle,
        decision_domain=decision_domain,
        consequence_class=consequence_class,
        authority_mode=authority_mode,
    )


def make_lease(context: TaskContext, operation: str, resource: str) -> CapabilityLease:
    return CapabilityLease(
        lease_id=f"lease-{context.task_id}",
        tenant_id=context.tenant_id,
        domain_id=context.domain_id,
        task_id=context.task_id,
        allowed_operations=frozenset({operation}),
        allowed_resources=frozenset({resource}),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )


def make_trust_grant(
    context: TaskContext,
    *,
    renter_id: str,
    cycle: str,
    expires_in: timedelta = timedelta(minutes=5),
    allowed_decision_domains: frozenset[str] | None = None,
    allowed_consequence_classes: frozenset[str] | None = None,
    allowed_authority_modes: frozenset[str] | None = None,
) -> KPGSTrustGrant:
    return KPGSTrustGrant(
        grant_id=f"trust-{renter_id}-{cycle}",
        renter_id=renter_id,
        tenant_id=context.tenant_id,
        domain_id=context.domain_id,
        allowed_cycles=frozenset({cycle}),
        allowed_decision_domains=allowed_decision_domains
        or frozenset({context.decision_domain or "software_delivery"}),
        allowed_consequence_classes=allowed_consequence_classes
        or frozenset({context.consequence_class or "technical_change"}),
        allowed_authority_modes=allowed_authority_modes
        or frozenset({context.authority_mode}),
        evidence_refs=(
            f"hub://evidence/{renter_id}/blackmask-ship",
            f"hub://evidence/{renter_id}/teacher-review",
        ),
        expires_at=datetime.now(timezone.utc) + expires_in,
    )


@pytest.mark.parametrize(
    ("domain", "operation", "resource", "payload"),
    [
        ("bookings", "booking.reserve", "arena:five-a-side", {"slot": "18:00"}),
        ("documents", "document.publish", "document:kpgs-dts", {"version": "1.0.0"}),
    ],
)
def test_destroy_recreate_resumes_two_workloads_without_local_canonical_state(
    domain: str,
    operation: str,
    resource: str,
    payload: Mapping[str, Any],
):
    hub = MemoryHubStore()
    context = make_context(domain)
    lease = make_lease(context, operation, resource)

    first = StatelessRenter("renter-before-eviction", hub).execute(
        context=context,
        lease=lease,
        operation=operation,
        resource=resource,
        payload=payload,
        idempotency_key=f"{domain}:step-1",
        handler=lambda checkpoint, incoming: StepOutcome(
            payload={"accepted": dict(incoming)},
            checkpoint={"stage": 1, "input": dict(incoming)},
            evidence=({"kind": "checkpoint", "ref": f"hub://evidence/{domain}/1"},),
        ),
    )
    assert first["event_kind"] == "task.checkpointed"
    assert first["checkpoint_ref"].startswith("hub://checkpoint/")

    def finish(checkpoint: Mapping[str, Any] | None, incoming: Mapping[str, Any]) -> StepOutcome:
        assert checkpoint == {"stage": 1, "input": dict(payload)}
        hub.record_effect(f"{domain}:finish")
        return StepOutcome(
            payload={"completed": True, "input": dict(incoming)},
            checkpoint={"stage": 2, "input": dict(incoming)},
            completed=True,
            evidence=({"kind": "completion", "ref": f"hub://evidence/{domain}/2"},),
        )

    second = StatelessRenter("renter-after-eviction", hub).execute(
        context=context,
        lease=lease,
        operation=operation,
        resource=resource,
        payload=payload,
        idempotency_key=f"{domain}:step-2",
        handler=finish,
    )
    assert second["event_kind"] == "task.completed"
    assert second["renter_id"] == "renter-after-eviction"
    assert second["session_id"] == context.session_id
    assert second["correlation_id"] == context.correlation_id
    assert second["governing_spec_ref"] == context.governing_spec_ref
    assert hub.effects[f"{domain}:finish"] == 1


def test_replay_does_not_duplicate_durable_side_effect():
    hub = MemoryHubStore()
    context = make_context("payments")
    lease = make_lease(context, "invoice.issue", "invoice:42")

    def issue(_checkpoint: Mapping[str, Any] | None, _payload: Mapping[str, Any]) -> StepOutcome:
        return StepOutcome(payload={"effect_count": hub.record_effect("invoice:42")}, completed=True)

    first = StatelessRenter("renter-one", hub).execute(
        context=context,
        lease=lease,
        operation="invoice.issue",
        resource="invoice:42",
        payload={},
        handler=issue,
        idempotency_key="invoice-42-once",
    )
    replay = StatelessRenter("renter-two", hub).execute(
        context=context,
        lease=lease,
        operation="invoice.issue",
        resource="invoice:42",
        payload={},
        handler=issue,
        idempotency_key="invoice-42-once",
    )
    assert first["payload"]["replayed"] is False
    assert replay["payload"]["replayed"] is True
    assert hub.effects["invoice:42"] == 1


def test_capability_scope_is_enforced_before_handler_execution():
    hub = MemoryHubStore()
    context = make_context("bookings")
    lease = make_lease(context, "booking.read", "booking:123")
    called = False

    def forbidden(_checkpoint: Mapping[str, Any] | None, _payload: Mapping[str, Any]) -> StepOutcome:
        nonlocal called
        called = True
        return StepOutcome(payload={}, completed=True)

    event = StatelessRenter("renter-denied", hub).execute(
        context=context,
        lease=lease,
        operation="booking.delete",
        resource="booking:123",
        payload={},
        handler=forbidden,
        idempotency_key="delete-123",
    )
    assert event["event_kind"] == "policy.denied"
    assert event["failure"]["code"] == "policy_denied"
    assert called is False


def test_expired_lease_and_missing_idempotency_key_fail_closed():
    hub = MemoryHubStore()
    context = make_context("documents")
    expired = CapabilityLease(
        lease_id="lease-expired",
        tenant_id=context.tenant_id,
        domain_id=context.domain_id,
        task_id=context.task_id,
        allowed_operations=frozenset({"document.write"}),
        allowed_resources=frozenset({"document:1"}),
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    expired_event = StatelessRenter("renter-expired", hub).execute(
        context=context,
        lease=expired,
        operation="document.write",
        resource="document:1",
        payload={},
        handler=lambda _checkpoint, _payload: StepOutcome(payload={}, completed=True),
        idempotency_key="doc-1",
    )
    assert expired_event["event_kind"] == "capability.expired"

    valid = make_lease(context, "document.write", "document:1")
    no_key = StatelessRenter("renter-no-key", hub).execute(
        context=context,
        lease=valid,
        operation="document.write",
        resource="document:1",
        payload={},
        handler=lambda _checkpoint, _payload: StepOutcome(payload={}, completed=True),
        idempotency_key=None,
    )
    assert no_key["event_kind"] == "policy.denied"
    assert "idempotency_key" in no_key["failure"]["message"]


def test_failure_classification_and_graceful_eviction_are_deterministic():
    hub = MemoryHubStore()
    context = make_context("recovery")
    lease = make_lease(context, "work.execute", "work:item")

    def fail(_checkpoint: Mapping[str, Any] | None, _payload: Mapping[str, Any]) -> StepOutcome:
        raise RenterFailure("verification_failed", "operator_action", "evidence mismatch")

    failed = StatelessRenter("renter-failure", hub).execute(
        context=context,
        lease=lease,
        operation="work.execute",
        resource="work:item",
        payload={},
        handler=fail,
        idempotency_key="failure-once",
    )
    assert failed["failure"] == {
        "code": "verification_failed",
        "recoverability": "operator_action",
        "message": "evidence mismatch",
    }

    draining = StatelessRenter("renter-draining", hub)
    draining.begin_eviction()
    denied = draining.execute(
        context=context,
        lease=lease,
        operation="work.execute",
        resource="work:item",
        payload={},
        handler=lambda _checkpoint, _payload: StepOutcome(payload={}, completed=True),
        idempotency_key="draining",
    )
    assert denied["failure"]["code"] == "cancelled"
    assert denied["failure"]["recoverability"] == "rehydrate"


@pytest.mark.parametrize("cycle", ["mao", "mmao"])
def test_orchestration_cycle_denies_untrusted_stateless_renter_before_handler(cycle: str):
    hub = MemoryHubStore()
    context = make_context("orchestration", orchestration_cycle=cycle)
    lease = make_lease(context, "work.execute", "work:item")
    called = False

    def should_not_run(_checkpoint: Mapping[str, Any] | None, _payload: Mapping[str, Any]) -> StepOutcome:
        nonlocal called
        called = True
        return StepOutcome(payload={"should": "not run"}, completed=True)

    event = StatelessRenter("renter-candidate", hub).execute(
        context=context,
        lease=lease,
        operation="work.execute",
        resource="work:item",
        payload={},
        handler=should_not_run,
        idempotency_key=f"{cycle}-candidate",
    )

    assert event["event_kind"] == "policy.denied"
    assert event["failure"]["code"] == "trust_not_earned"
    assert event["orchestration_cycle"] == cycle
    assert called is False


def test_earned_kpgs_trust_allows_mmao_entry_and_receipts_role_fit():
    hub = MemoryHubStore()
    context = make_context("orchestration", orchestration_cycle="mmao")
    lease = make_lease(context, "work.execute", "work:item")
    renter_id = "renter-proven"
    trust = make_trust_grant(context, renter_id=renter_id, cycle="mmao")

    event = StatelessRenter(renter_id, hub).execute(
        context=context,
        lease=lease,
        operation="work.execute",
        resource="work:item",
        payload={},
        handler=lambda _checkpoint, _payload: StepOutcome(payload={"ok": True}, completed=True),
        idempotency_key="mmao-proven",
        trust_grant=trust,
    )

    assert event["event_kind"] == "task.completed"
    assert event["orchestration_cycle"] == "mmao"
    assert event["decision_domain"] == "software_delivery"
    assert event["consequence_class"] == "technical_change"
    assert event["authority_mode"] == "execution"
    assert event["trust_grant_id"] == trust.grant_id


@pytest.mark.parametrize(
    "grant_mutation",
    ["wrong_renter", "wrong_cycle", "expired", "missing_evidence"],
)
def test_kpgs_trust_is_identity_scoped_cycle_scoped_fresh_and_evidence_backed(grant_mutation: str):
    hub = MemoryHubStore()
    context = make_context("orchestration", orchestration_cycle="mao")
    lease = make_lease(context, "work.execute", "work:item")
    renter_id = "renter-scoped"
    base = make_trust_grant(context, renter_id=renter_id, cycle="mao")

    values = {
        "grant_id": base.grant_id,
        "renter_id": base.renter_id,
        "tenant_id": base.tenant_id,
        "domain_id": base.domain_id,
        "allowed_cycles": base.allowed_cycles,
        "allowed_decision_domains": base.allowed_decision_domains,
        "allowed_consequence_classes": base.allowed_consequence_classes,
        "allowed_authority_modes": base.allowed_authority_modes,
        "evidence_refs": base.evidence_refs,
        "expires_at": base.expires_at,
        "issuer": base.issuer,
        "trust_state": base.trust_state,
    }
    if grant_mutation == "wrong_renter":
        values["renter_id"] = "someone-else"
    elif grant_mutation == "wrong_cycle":
        values["allowed_cycles"] = frozenset({"mmao"})
    elif grant_mutation == "expired":
        values["expires_at"] = datetime.now(timezone.utc) - timedelta(seconds=1)
    elif grant_mutation == "missing_evidence":
        values["evidence_refs"] = ()

    event = StatelessRenter(renter_id, hub).execute(
        context=context,
        lease=lease,
        operation="work.execute",
        resource="work:item",
        payload={},
        handler=lambda _checkpoint, _payload: StepOutcome(payload={"should": "not run"}, completed=True),
        idempotency_key=f"mao-{grant_mutation}",
        trust_grant=KPGSTrustGrant(**values),
    )

    assert event["event_kind"] == "policy.denied"
    assert event["failure"]["code"] == "trust_not_earned"


@pytest.mark.parametrize(
    ("context_kwargs", "grant_kwargs"),
    [
        (
            {"decision_domain": "forensic_sociology"},
            {"allowed_decision_domains": frozenset({"software_delivery"})},
        ),
        (
            {"consequence_class": "human_welfare"},
            {"allowed_consequence_classes": frozenset({"technical_change"})},
        ),
    ],
)
def test_trusted_renter_is_denied_when_role_fit_does_not_match_consequence(
    context_kwargs: dict[str, str],
    grant_kwargs: dict[str, frozenset[str]],
):
    hub = MemoryHubStore()
    context = make_context(
        "orchestration",
        orchestration_cycle="mmao",
        **context_kwargs,
    )
    lease = make_lease(context, "work.execute", "work:item")
    renter_id = "renter-trusted-wrong-role"
    trust = make_trust_grant(
        context,
        renter_id=renter_id,
        cycle="mmao",
        **grant_kwargs,
    )
    called = False

    def should_not_run(_checkpoint: Mapping[str, Any] | None, _payload: Mapping[str, Any]) -> StepOutcome:
        nonlocal called
        called = True
        return StepOutcome(payload={"should": "not run"}, completed=True)

    event = StatelessRenter(renter_id, hub).execute(
        context=context,
        lease=lease,
        operation="work.execute",
        resource="work:item",
        payload={},
        handler=should_not_run,
        idempotency_key="wrong-role",
        trust_grant=trust,
    )

    assert event["event_kind"] == "policy.denied"
    assert event["failure"]["code"] == "role_not_fit"
    assert called is False


def test_validation_authority_is_peer_surface_not_execution_authority():
    hub = MemoryHubStore()
    renter_id = "renter-validator"

    validation_context = make_context(
        "orchestration",
        orchestration_cycle="mmao",
        decision_domain="forensic_sociology",
        consequence_class="human_welfare",
        authority_mode="validation",
    )
    validation_lease = make_lease(validation_context, "review.validate", "case:42")
    validation_trust = make_trust_grant(
        validation_context,
        renter_id=renter_id,
        cycle="mmao",
        allowed_decision_domains=frozenset({"forensic_sociology"}),
        allowed_consequence_classes=frozenset({"human_welfare"}),
        allowed_authority_modes=frozenset({"validation"}),
    )

    validated = StatelessRenter(renter_id, hub).execute(
        context=validation_context,
        lease=validation_lease,
        operation="review.validate",
        resource="case:42",
        payload={},
        handler=lambda _checkpoint, _payload: StepOutcome(
            payload={"disposition": "independent_validation"},
            completed=True,
        ),
        idempotency_key="validate-case-42",
        trust_grant=validation_trust,
    )
    assert validated["event_kind"] == "task.completed"
    assert validated["authority_mode"] == "validation"

    execution_context = make_context(
        "orchestration",
        orchestration_cycle="mmao",
        decision_domain="forensic_sociology",
        consequence_class="human_welfare",
        authority_mode="execution",
    )
    execution_lease = make_lease(execution_context, "case.mutate", "case:42")
    executed = False

    def should_not_execute(_checkpoint: Mapping[str, Any] | None, _payload: Mapping[str, Any]) -> StepOutcome:
        nonlocal executed
        executed = True
        return StepOutcome(payload={"mutated": True}, completed=True)

    denied = StatelessRenter(renter_id, hub).execute(
        context=execution_context,
        lease=execution_lease,
        operation="case.mutate",
        resource="case:42",
        payload={},
        handler=should_not_execute,
        idempotency_key="mutate-case-42",
        trust_grant=validation_trust,
    )

    assert denied["event_kind"] == "policy.denied"
    assert denied["failure"]["code"] == "role_not_fit"
    assert executed is False
