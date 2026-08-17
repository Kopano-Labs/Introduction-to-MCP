from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

import pytest

from kopano.stateless_renter import (
    CapabilityLease,
    IdempotencyRecord,
    StatelessRenter,
    StepOutcome,
    TaskContext,
)


class MemoryHubStore:
    """Test double for Hub-owned canonical state; it is deliberately external to renters."""

    def __init__(self) -> None:
        self.checkpoints: dict[tuple[str, str, str], dict[str, Any]] = {}
        self.idempotency: dict[tuple[str, str, str, str], IdempotencyRecord] = {}
        self.effects: dict[str, int] = {}

    @staticmethod
    def _task_key(context: TaskContext) -> tuple[str, str, str]:
        return (context.tenant_id, context.domain_id, context.task_id)

    def load_checkpoint(self, context: TaskContext) -> Mapping[str, Any] | None:
        checkpoint = self.checkpoints.get(self._task_key(context))
        return dict(checkpoint) if checkpoint is not None else None

    def save_checkpoint(self, context: TaskContext, checkpoint: Mapping[str, Any]) -> str:
        self.checkpoints[self._task_key(context)] = dict(checkpoint)
        return f"hub://checkpoint/{context.tenant_id}/{context.domain_id}/{context.task_id}"

    def get_idempotency(self, context: TaskContext, idempotency_key: str) -> IdempotencyRecord | None:
        return self.idempotency.get((*self._task_key(context), idempotency_key))

    def put_idempotency(
        self,
        context: TaskContext,
        idempotency_key: str,
        record: IdempotencyRecord,
    ) -> None:
        self.idempotency[(*self._task_key(context), idempotency_key)] = record

    def record_effect(self, key: str) -> int:
        self.effects[key] = self.effects.get(key, 0) + 1
        return self.effects[key]


def make_context(domain_id: str, task_id: str) -> TaskContext:
    return TaskContext(
        tenant_id="tenant-kopano",
        domain_id=domain_id,
        session_id=f"session-{task_id}",
        task_id=task_id,
        correlation_id=f"corr-{task_id}",
        governing_spec_ref="governance/kpgs-vnext/stateless-renter/PROTOCOL.md",
        skill_versions={"kpgs-audit-verify-govern": "0.1.0"},
    )


def make_lease(context: TaskContext, operation: str, resource: str, *, expires_in_minutes: int = 5) -> CapabilityLease:
    return CapabilityLease(
        lease_id=f"lease-{context.task_id}",
        tenant_id=context.tenant_id,
        domain_id=context.domain_id,
        task_id=context.task_id,
        allowed_operations=frozenset({operation}),
        allowed_resources=frozenset({resource}),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes),
    )


def assert_envelope_provenance(event: Mapping[str, Any], context: TaskContext) -> None:
    assert event["protocol_version"] == "1.0"
    assert event["tenant_id"] == context.tenant_id
    assert event["domain_id"] == context.domain_id
    assert event["session_id"] == context.session_id
    assert event["task_id"] == context.task_id
    assert event["correlation_id"] == context.correlation_id
    assert event["governing_spec_ref"] == context.governing_spec_ref
    assert event["skill_versions"] == dict(context.skill_versions)
    assert event["event_id"].startswith("evt-")
    assert event["lease_id"]
    datetime.fromisoformat(event["issued_at"])


@pytest.mark.parametrize(
    ("domain_id", "operation", "resource", "payload"),
    [
        ("bookings", "booking.reserve", "arena:five-a-side", {"slot": "18:00"}),
        ("documents", "document.publish", "document:kpgs-dts", {"version": "1.0.0"}),
    ],
)
def test_same_conformance_harness_survives_destroy_recreate_for_two_workloads(
    domain_id: str,
    operation: str,
    resource: str,
    payload: Mapping[str, Any],
):
    hub = MemoryHubStore()
    context = make_context(domain_id, f"task-{domain_id}")
    lease = make_lease(context, operation, resource)

    def first_step(checkpoint: Mapping[str, Any] | None, incoming: Mapping[str, Any]) -> StepOutcome:
        assert checkpoint is None
        hub.record_effect(f"{domain_id}:first")
        return StepOutcome(
            payload={"accepted": dict(incoming)},
            checkpoint={"stage": 1, "input": dict(incoming)},
            completed=False,
            evidence=({"kind": "checkpoint", "ref": f"hub://evidence/{context.task_id}/1"},),
        )

    renter_a = StatelessRenter("renter-before-eviction", hub)
    first_event = renter_a.execute(
        context=context,
        lease=lease,
        operation=operation,
        resource=resource,
        payload=payload,
        handler=first_step,
        idempotency_key=f"{context.task_id}:step-1",
    )

    assert first_event["event_kind"] == "task.checkpointed"
    assert first_event["checkpoint_ref"].startswith("hub://checkpoint/")
    assert_envelope_provenance(first_event, context)

    del renter_a

    def resumed_step(checkpoint: Mapping[str, Any] | None, incoming: Mapping[str, Any]) -> StepOutcome:
        assert checkpoint == {"stage": 1, "input": dict(payload)}
        hub.record_effect(f"{domain_id}:finish")
        return StepOutcome(
            payload={"completed": True, "input": dict(incoming)},
            checkpoint={"stage": 2, "input": dict(incoming)},
            completed=True,
            evidence=({"kind": "completion", "ref": f"hub://evidence/{context.task_id}/2"},),
        )

    renter_b = StatelessRenter("renter-after-eviction", hub)
    completion_event = renter_b.execute(
        context=context,
        lease=lease,
        operation=operation,
        resource=resource,
        payload=payload,
        handler=resumed_step,
        idempotency_key=f"{context.task_id}:step-2",
    )

    assert completion_event["event_kind"] == "task.completed"
    assert completion_event["renter_id"] == "renter-after-eviction"
    assert hub.checkpoints[(context.tenant_id, context.domain_id, context.task_id)]["stage"] == 2
    assert hub.effects == {f"{domain_id}:first": 1, f"{domain_id}:finish": 1}
    assert_envelope_provenance(completion_event, context)


def test_replayed_side_effect_does_not_execute_twice():
    hub = MemoryHubStore()
    context = make_context("payments", "task-idempotent")
    lease = make_lease(context, "invoice.issue", "invoice:42")

    def issue_invoice(_checkpoint: Mapping[str, Any] | None, _payload: Mapping[str, Any]) -> StepOutcome:
        count = hub.record_effect("invoice:42")
        return StepOutcome(payload={"invoice_id": "42", "effect_count": count}, completed=True)

    renter = StatelessRenter("renter-one", hub)
    first = renter.execute(
        context=context,
        lease=lease,
        operation="invoice.issue",
        resource="invoice:42",
        payload={},
        handler=issue_invoice,
        idempotency_key="invoice-42-once",
    )

    replacement = StatelessRenter("renter-two", hub)
    replay = replacement.execute(
        context=context,
        lease=lease,
        operation="invoice.issue",
        resource="invoice:42",
        payload={},
        handler=issue_invoice,
        idempotency_key="invoice-42-once",
    )

    assert first["payload"]["replayed"] is False
    assert replay["payload"]["replayed"] is True
    assert replay["payload"]["effect_count"] == 1
    assert hub.effects["invoice:42"] == 1
    assert_envelope_provenance(replay, context)


def test_renter_cannot_act_outside_issued_capability_lease():
    hub = MemoryHubStore()
    context = make_context("bookings", "task-denied")
    lease = make_lease(context, "booking.read", "booking:123")
    handler_called = False

    def forbidden_handler(_checkpoint: Mapping[str, Any] | None, _payload: Mapping[str, Any]) -> StepOutcome:
        nonlocal handler_called
        handler_called = True
        return StepOutcome(payload={}, completed=True)

    event = StatelessRenter("renter-denied", hub).execute(
        context=context,
        lease=lease,
        operation="booking.delete",
        resource="booking:123",
        payload={},
        handler=forbidden_handler,
        idempotency_key="delete-123",
    )

    assert event["event_kind"] == "policy.denied"
    assert event["failure"]["code"] == "policy_denied"
    assert handler_called is False
    assert_envelope_provenance(event, context)


def test_expired_capability_lease_is_rejected_before_execution():
    hub = MemoryHubStore()
    context = make_context("documents", "task-expired")
    lease = CapabilityLease(
        lease_id="lease-expired",
        tenant_id=context.tenant_id,
        domain_id=context.domain_id,
        task_id=context.task_id,
        allowed_operations=frozenset({"document.write"}),
        allowed_resources=frozenset({"document:1"}),
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )

    event = StatelessRenter("renter-expired", hub).execute(
        context=context,
        lease=lease,
        operation="document.write",
        resource="document:1",
        payload={},
        handler=lambda _checkpoint, _payload: StepOutcome(payload={}, completed=True),
        idempotency_key="doc-1",
    )

    assert event["event_kind"] == "capability.expired"
    assert event["failure"]["code"] == "capability_expired"
    assert_envelope_provenance(event, context)


def test_side_effect_requires_idempotency_key():
    hub = MemoryHubStore()
    context = make_context("documents", "task-no-key")
    lease = make_lease(context, "document.write", "document:1")

    event = StatelessRenter("renter-no-key", hub).execute(
        context=context,
        lease=lease,
        operation="document.write",
        resource="document:1",
        payload={},
        handler=lambda _checkpoint, _payload: StepOutcome(payload={}, completed=True),
        idempotency_key=None,
        side_effecting=True,
    )

    assert event["event_kind"] == "policy.denied"
    assert "idempotency_key" in event["failure"]["message"]


def test_reference_events_satisfy_machine_envelope_required_contract():
    schema_path = Path("governance/kpgs-vnext/stateless-renter/renter-envelope.schema.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    hub = MemoryHubStore()
    context = make_context("documents", "task-schema")
    lease = make_lease(context, "document.read", "document:1")
    event = StatelessRenter("renter-schema", hub).execute(
        context=context,
        lease=lease,
        operation="document.read",
        resource="document:1",
        payload={},
        handler=lambda _checkpoint, _payload: StepOutcome(payload={"ok": True}, completed=True),
        idempotency_key=None,
        side_effecting=False,
    )

    assert set(schema["required"]) <= set(event)
    assert event["event_kind"] in schema["properties"]["event_kind"]["enum"]
    assert schema["properties"]["protocol_version"]["pattern"] == r"^[0-9]+\.[0-9]+$"
    assert_envelope_provenance(event, context)
