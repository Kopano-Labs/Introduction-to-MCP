from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
from typing import Any, Mapping

MCP_PROTOCOL_VERSION = "2026-07-28"
MCP_TASK_EXTENSION = "io.modelcontextprotocol/tasks"


class ContractError(ValueError):
    pass


class TaskState(StrEnum):
    ACCEPTED = "accepted"
    STARTED = "started"
    AWAITING_APPROVAL = "awaiting_approval"
    CHECKPOINTED = "checkpointed"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    HELD = "held"


TERMINAL_STATES = {TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED}
_ALLOWED_TRANSITIONS = {
    TaskState.ACCEPTED: {TaskState.STARTED, TaskState.FAILED, TaskState.CANCELLED, TaskState.HELD},
    TaskState.STARTED: {
        TaskState.AWAITING_APPROVAL,
        TaskState.CHECKPOINTED,
        TaskState.COMPLETED,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.HELD,
    },
    TaskState.AWAITING_APPROVAL: {TaskState.STARTED, TaskState.FAILED, TaskState.CANCELLED, TaskState.HELD},
    TaskState.CHECKPOINTED: {TaskState.STARTED, TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED},
    TaskState.HELD: {TaskState.STARTED, TaskState.FAILED, TaskState.CANCELLED},
    TaskState.COMPLETED: set(),
    TaskState.FAILED: set(),
    TaskState.CANCELLED: set(),
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


@dataclass(frozen=True)
class PrincipalEnvelope:
    principal_id: str
    principal_type: str
    identity_scheme: str
    identity_subject: str
    accountable_principal_id: str | None = None
    public_key_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.principal_id.strip():
            raise ContractError("principal_id is required")
        if not self.identity_subject.strip():
            raise ContractError("identity_subject is required")


@dataclass(frozen=True)
class CapabilityGrant:
    grant_id: str
    principal_id: str
    operations: frozenset[str]
    resources: frozenset[str]
    expires_at: str | None = None
    parent_grant_id: str | None = None
    revocation_ref: str | None = None

    def allows(self, *, operation: str, resource: str) -> bool:
        return ("*" in self.operations or operation in self.operations) and (
            "*" in self.resources or resource in self.resources
        )

    def assert_valid_for(
        self,
        *,
        principal: PrincipalEnvelope,
        operation: str,
        resource: str,
        now: datetime | None = None,
    ) -> None:
        if self.principal_id != principal.principal_id:
            raise ContractError("capability principal does not match task principal")
        if self.expires_at is not None:
            instant = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
            current = now or datetime.now(timezone.utc)
            if instant <= current:
                raise ContractError("capability grant has expired")
        if not self.allows(operation=operation, resource=resource):
            raise ContractError("capability does not authorize operation/resource")


@dataclass(frozen=True)
class EvidenceRef:
    sha256: str
    ref: str | None = None
    content_captured: bool = False


@dataclass(frozen=True)
class TaskReceipt:
    task_id: str
    receipt_id: str
    sequence: int
    tenant_id: str
    domain_id: str
    principal_id: str
    capability_grant_id: str
    governing_spec_ref: str
    policy_version: str
    state: TaskState
    idempotency_key: str
    operation: str
    resource: str
    created_at: str
    updated_at: str
    protocol: str = "local"
    protocol_version: str | None = None
    transport: str | None = None
    external_task_id: str | None = None
    checkpoint_ref: str | None = None
    result_ref: str | None = None
    failure_code: str | None = None
    previous_receipt_sha256: str | None = None
    evidence_refs: tuple[EvidenceRef, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "kpgs.task_receipt.v0.1",
            "task_id": self.task_id,
            "receipt_id": self.receipt_id,
            "sequence": self.sequence,
            "tenant_id": self.tenant_id,
            "domain_id": self.domain_id,
            "principal_id": self.principal_id,
            "capability_grant_id": self.capability_grant_id,
            "governing_spec_ref": self.governing_spec_ref,
            "policy_version": self.policy_version,
            "state": self.state.value,
            "idempotency_key": self.idempotency_key,
            "operation": self.operation,
            "resource": self.resource,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "protocol": {
                "name": self.protocol,
                "version": self.protocol_version,
                "transport": self.transport,
                "external_task_id": self.external_task_id,
            },
            "checkpoint_ref": self.checkpoint_ref,
            "result_ref": self.result_ref,
            "failure_code": self.failure_code,
            "previous_receipt_sha256": self.previous_receipt_sha256,
            "evidence_refs": [
                {"sha256": item.sha256, "ref": item.ref, "content_captured": item.content_captured}
                for item in self.evidence_refs
            ],
        }

    @property
    def sha256(self) -> str:
        return canonical_sha256(self.as_dict())


class InMemoryTaskLedger:
    """POC canonical-store interface used by adapter conformance tests.

    Production storage MUST replace this class. The important property is that
    adapter instances do not own the task truth.
    """

    def __init__(self) -> None:
        self._latest: dict[str, TaskReceipt] = {}
        self._history: dict[str, list[TaskReceipt]] = {}
        self._idempotency: dict[str, str] = {}

    def get(self, task_id: str) -> TaskReceipt:
        try:
            return self._latest[task_id]
        except KeyError as exc:
            raise ContractError(f"unknown task_id: {task_id}") from exc

    def get_by_idempotency_key(self, key: str) -> TaskReceipt | None:
        task_id = self._idempotency.get(key)
        return self._latest.get(task_id) if task_id else None

    def append(self, receipt: TaskReceipt) -> TaskReceipt:
        current = self._latest.get(receipt.task_id)
        if current is None:
            if receipt.sequence != 0:
                raise ContractError("first receipt sequence must be 0")
            if receipt.previous_receipt_sha256 is not None:
                raise ContractError("first receipt cannot point to a previous receipt")
            existing = self._idempotency.get(receipt.idempotency_key)
            if existing is not None and existing != receipt.task_id:
                raise ContractError("idempotency key already belongs to another task")
            self._idempotency[receipt.idempotency_key] = receipt.task_id
            self._history[receipt.task_id] = [receipt]
        else:
            if receipt.sequence != current.sequence + 1:
                raise ContractError("receipt sequence is not continuous")
            if receipt.previous_receipt_sha256 != current.sha256:
                raise ContractError("receipt hash chain is broken")
            self._history[receipt.task_id].append(receipt)
        self._latest[receipt.task_id] = receipt
        return receipt

    def history(self, task_id: str) -> tuple[TaskReceipt, ...]:
        return tuple(self._history.get(task_id, ()))


def evidence_ref(payload: Any, *, ref: str | None = None) -> EvidenceRef:
    """Create a metadata-only evidence reference. Raw content is not retained."""
    return EvidenceRef(sha256=canonical_sha256(payload), ref=ref, content_captured=False)


class MCP20260728Adapter:
    """Map MCP 2026-07-28 interactions onto protocol-neutral KPGS tasks.

    The adapter owns no durable task authority. A connection, process, request,
    or MCP external task handle may disappear without invalidating KPGS state.
    """

    def __init__(self, ledger: InMemoryTaskLedger) -> None:
        self._ledger = ledger

    @staticmethod
    def request_meta(
        *,
        client_name: str,
        client_version: str,
        client_capabilities: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "io.modelcontextprotocol/protocolVersion": MCP_PROTOCOL_VERSION,
            "io.modelcontextprotocol/clientInfo": {"name": client_name, "version": client_version},
            "io.modelcontextprotocol/clientCapabilities": dict(client_capabilities or {}),
        }

    @classmethod
    def discover_request(
        cls,
        *,
        request_id: str,
        client_name: str,
        client_version: str,
        client_capabilities: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "server/discover",
            "params": {
                "_meta": cls.request_meta(
                    client_name=client_name,
                    client_version=client_version,
                    client_capabilities=client_capabilities,
                )
            },
        }

    def accept_task(
        self,
        *,
        tenant_id: str,
        domain_id: str,
        principal: PrincipalEnvelope,
        capability: CapabilityGrant,
        operation: str,
        resource: str,
        governing_spec_ref: str,
        policy_version: str,
        idempotency_key: str,
        external_task_id: str | None = None,
        transport: str | None = None,
        now: datetime | None = None,
    ) -> TaskReceipt:
        capability.assert_valid_for(principal=principal, operation=operation, resource=resource, now=now)
        identity = {
            "tenant_id": tenant_id,
            "domain_id": domain_id,
            "principal_id": principal.principal_id,
            "capability_grant_id": capability.grant_id,
            "operation": operation,
            "resource": resource,
            "governing_spec_ref": governing_spec_ref,
            "policy_version": policy_version,
            "idempotency_key": idempotency_key,
        }
        task_id = f"kpgs-task-{canonical_sha256(identity)[:24]}"
        existing = self._ledger.get_by_idempotency_key(idempotency_key)
        if existing is not None:
            if existing.task_id != task_id:
                raise ContractError("idempotency key replay does not match original governed task")
            return existing
        timestamp = (now or datetime.now(timezone.utc)).isoformat().replace("+00:00", "Z")
        receipt = TaskReceipt(
            task_id=task_id,
            receipt_id=f"{task_id}-r0000",
            sequence=0,
            tenant_id=tenant_id,
            domain_id=domain_id,
            principal_id=principal.principal_id,
            capability_grant_id=capability.grant_id,
            governing_spec_ref=governing_spec_ref,
            policy_version=policy_version,
            state=TaskState.ACCEPTED,
            idempotency_key=idempotency_key,
            operation=operation,
            resource=resource,
            created_at=timestamp,
            updated_at=timestamp,
            protocol="mcp",
            protocol_version=MCP_PROTOCOL_VERSION,
            transport=transport,
            external_task_id=external_task_id,
        )
        return self._ledger.append(receipt)

    def transition(
        self,
        task_id: str,
        *,
        state: TaskState,
        evidence: Any | None = None,
        evidence_uri: str | None = None,
        checkpoint_ref: str | None = None,
        result_ref: str | None = None,
        failure_code: str | None = None,
        external_task_id: str | None = None,
        now: datetime | None = None,
    ) -> TaskReceipt:
        current = self._ledger.get(task_id)
        if current.state in TERMINAL_STATES:
            raise ContractError("terminal task cannot transition")
        if state not in _ALLOWED_TRANSITIONS[current.state]:
            raise ContractError(f"invalid task transition: {current.state.value} -> {state.value}")
        refs = current.evidence_refs
        if evidence is not None:
            refs = (*refs, evidence_ref(evidence, ref=evidence_uri))
        timestamp = (now or datetime.now(timezone.utc)).isoformat().replace("+00:00", "Z")
        next_sequence = current.sequence + 1
        next_receipt = replace(
            current,
            receipt_id=f"{current.task_id}-r{next_sequence:04d}",
            sequence=next_sequence,
            state=state,
            updated_at=timestamp,
            external_task_id=external_task_id or current.external_task_id,
            checkpoint_ref=checkpoint_ref or current.checkpoint_ref,
            result_ref=result_ref or current.result_ref,
            failure_code=failure_code,
            previous_receipt_sha256=current.sha256,
            evidence_refs=refs,
        )
        return self._ledger.append(next_receipt)

    def resume(self, task_id: str) -> TaskReceipt:
        """Return canonical task state after adapter/process recreation."""
        return self._ledger.get(task_id)
