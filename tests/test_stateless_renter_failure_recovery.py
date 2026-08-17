from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

import pytest

from kopano.stateless_renter import (
    CapabilityLease,
    IdempotencyRecord,
    RenterFailure,
    StatelessRenter,
    StepOutcome,
    TaskContext,
)


class RecoveryStore:
    def __init__(self) -> None:
        self.checkpoint: dict[str, Any] | None = None
        self.idempotency: dict[str, IdempotencyRecord] = {}

    def load_checkpoint(self, _context: TaskContext) -> Mapping[str, Any] | None:
        return dict(self.checkpoint) if self.checkpoint is not None else None

    def save_checkpoint(self, context: TaskContext, checkpoint: Mapping[str, Any]) -> str:
        self.checkpoint = dict(checkpoint)
        return f"hub://checkpoint/{context.task_id}"

    def get_idempotency(self, _context: TaskContext, idempotency_key: str) -> IdempotencyRecord | None:
        return self.idempotency.get(idempotency_key)

    def put_idempotency(
        self,
        _context: TaskContext,
        idempotency_key: str,
        record: IdempotencyRecord,
    ) -> None:
        self.idempotency[idempotency_key] = record


def context() -> TaskContext:
    return TaskContext(
        tenant_id="tenant-1",
        domain_id="recovery",
        task_id="task-recovery",
        correlation_id="corr-recovery",
        governing_spec_ref="governance/kpgs-vnext/stateless-renter/PROTOCOL.md",
    )


def lease(task: TaskContext) -> CapabilityLease:
    return CapabilityLease(
        lease_id="lease-recovery",
        tenant_id=task.tenant_id,
        domain_id=task.domain_id,
        task_id=task.task_id,
        allowed_operations=frozenset({"work.execute"}),
        allowed_resources=frozenset({"work:item"}),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )


@pytest.mark.parametrize(
    ("code", "recoverability"),
    [
        ("input_invalid", "user_action"),
        ("dependency_unavailable", "retry"),
        ("timeout", "retry"),
        ("verification_failed", "operator_action"),
        ("cancelled", "rehydrate"),
    ],
)
def test_typed_workload_failures_emit_deterministic_recovery_contract(code: str, recoverability: str):
    store = RecoveryStore()
    task = context()

    def fail(_checkpoint: Mapping[str, Any] | None, _payload: Mapping[str, Any]) -> StepOutcome:
        raise RenterFailure(code, recoverability, f"deterministic {code}")

    event = StatelessRenter("renter-failure", store).execute(
        context=task,
        lease=lease(task),
        operation="work.execute",
        resource="work:item",
        payload={},
        handler=fail,
        idempotency_key="failure-once",
    )

    assert event["event_kind"] == "task.failed"
    assert event["failure"] == {
        "code": code,
        "recoverability": recoverability,
        "message": f"deterministic {code}",
    }
    assert event["correlation_id"] == task.correlation_id
    assert event["governing_spec_ref"] == task.governing_spec_ref


def test_untyped_exception_is_classified_as_execution_failed():
    store = RecoveryStore()
    task = context()

    def explode(_checkpoint: Mapping[str, Any] | None, _payload: Mapping[str, Any]) -> StepOutcome:
        raise RuntimeError("boom")

    event = StatelessRenter("renter-exception", store).execute(
        context=task,
        lease=lease(task),
        operation="work.execute",
        resource="work:item",
        payload={},
        handler=explode,
        idempotency_key="exception-once",
    )

    assert event["event_kind"] == "task.failed"
    assert event["failure"]["code"] == "execution_failed"
    assert event["failure"]["recoverability"] == "retry"


def test_graceful_eviction_stops_new_work_and_replacement_can_continue():
    store = RecoveryStore()
    task = context()
    capability = lease(task)
    renter = StatelessRenter("renter-draining", store)

    assert renter.readiness() == {
        "renter_id": "renter-draining",
        "protocol_version": "1.0",
        "accepting_work": True,
        "state_authority": "external-canonical-store",
    }

    renter.begin_eviction()
    assert renter.readiness()["accepting_work"] is False

    denied = renter.execute(
        context=task,
        lease=capability,
        operation="work.execute",
        resource="work:item",
        payload={},
        handler=lambda _checkpoint, _payload: StepOutcome(payload={"should_not_run": True}, completed=True),
        idempotency_key="draining",
    )
    assert denied["failure"]["code"] == "cancelled"
    assert denied["failure"]["recoverability"] == "rehydrate"

    replacement = StatelessRenter("renter-replacement", store)
    completed = replacement.execute(
        context=task,
        lease=capability,
        operation="work.execute",
        resource="work:item",
        payload={},
        handler=lambda _checkpoint, _payload: StepOutcome(payload={"continued": True}, completed=True),
        idempotency_key="replacement",
    )
    assert completed["event_kind"] == "task.completed"
    assert completed["renter_id"] == "renter-replacement"
