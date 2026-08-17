from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "governance"
    / "kpgs-vnext"
    / "task-contract"
    / "adapter.py"
)
SPEC = importlib.util.spec_from_file_location("kpgs_task_contract_adapter", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
adapter_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = adapter_module
SPEC.loader.exec_module(adapter_module)

CapabilityGrant = adapter_module.CapabilityGrant
ContractError = adapter_module.ContractError
InMemoryTaskLedger = adapter_module.InMemoryTaskLedger
MCP20260728Adapter = adapter_module.MCP20260728Adapter
MCP_PROTOCOL_VERSION = adapter_module.MCP_PROTOCOL_VERSION
PrincipalEnvelope = adapter_module.PrincipalEnvelope
TaskState = adapter_module.TaskState
canonical_sha256 = adapter_module.canonical_sha256


FIXED_NOW = datetime(2026, 8, 17, 15, 0, tzinfo=timezone.utc)


def _principal() -> PrincipalEnvelope:
    return PrincipalEnvelope(
        principal_id="agent:forge",
        principal_type="agent",
        identity_scheme="local-key",
        identity_subject="forge-key-01",
        accountable_principal_id="human:owner",
        public_key_ref="keyref://forge",
    )


def _capability() -> CapabilityGrant:
    return CapabilityGrant(
        grant_id="cap:repo-write",
        principal_id="agent:forge",
        operations=frozenset({"repo.write", "repo.read"}),
        resources=frozenset({"repo:Introduction-to-MCP"}),
        expires_at="2099-01-01T00:00:00Z",
    )


def _accept(adapter: MCP20260728Adapter, *, idempotency_key: str = "idem-task-0001"):
    return adapter.accept_task(
        tenant_id="kopano",
        domain_id="governance",
        principal=_principal(),
        capability=_capability(),
        operation="repo.write",
        resource="repo:Introduction-to-MCP",
        governing_spec_ref="kpgs://task-contract/v0.1",
        policy_version="kpgs-vnext.phase0",
        idempotency_key=idempotency_key,
        external_task_id="mcp-task-123",
        transport="streamable-http",
        now=FIXED_NOW,
    )


def test_mcp_2026_07_28_uses_per_request_metadata_and_discovery():
    request = MCP20260728Adapter.discover_request(
        request_id="discover-1",
        client_name="kpgs",
        client_version="0.1.0",
    )

    assert request["method"] == "server/discover"
    meta = request["params"]["_meta"]
    assert meta["io.modelcontextprotocol/protocolVersion"] == MCP_PROTOCOL_VERSION
    assert "session_id" not in meta
    assert "initialize" not in request


def test_capability_is_checked_before_task_creation():
    ledger = InMemoryTaskLedger()
    adapter = MCP20260728Adapter(ledger)
    denied = CapabilityGrant(
        grant_id="cap:read-only",
        principal_id="agent:forge",
        operations=frozenset({"repo.read"}),
        resources=frozenset({"repo:Introduction-to-MCP"}),
        expires_at="2099-01-01T00:00:00Z",
    )

    with pytest.raises(ContractError, match="does not authorize"):
        adapter.accept_task(
            tenant_id="kopano",
            domain_id="governance",
            principal=_principal(),
            capability=denied,
            operation="repo.write",
            resource="repo:Introduction-to-MCP",
            governing_spec_ref="kpgs://task-contract/v0.1",
            policy_version="kpgs-vnext.phase0",
            idempotency_key="idem-denied-0001",
            now=FIXED_NOW,
        )

    assert ledger.get_by_idempotency_key("idem-denied-0001") is None


def test_duplicate_delivery_resolves_to_one_canonical_task():
    ledger = InMemoryTaskLedger()
    first_adapter = MCP20260728Adapter(ledger)
    first = _accept(first_adapter)

    duplicate_adapter = MCP20260728Adapter(ledger)
    duplicate = _accept(duplicate_adapter)

    assert duplicate.task_id == first.task_id
    assert duplicate.receipt_id == first.receipt_id
    assert len(ledger.history(first.task_id)) == 1


def test_idempotency_key_replay_cannot_change_governed_intent():
    ledger = InMemoryTaskLedger()
    adapter = MCP20260728Adapter(ledger)
    _accept(adapter)

    with pytest.raises(ContractError, match="replay does not match"):
        adapter.accept_task(
            tenant_id="kopano",
            domain_id="governance",
            principal=_principal(),
            capability=_capability(),
            operation="repo.read",
            resource="repo:Introduction-to-MCP",
            governing_spec_ref="kpgs://task-contract/v0.1",
            policy_version="kpgs-vnext.phase0",
            idempotency_key="idem-task-0001",
            now=FIXED_NOW,
        )


def test_task_survives_adapter_destruction_and_resumes_from_ledger():
    ledger = InMemoryTaskLedger()
    first_adapter = MCP20260728Adapter(ledger)
    accepted = _accept(first_adapter)

    del first_adapter
    replacement_adapter = MCP20260728Adapter(ledger)

    resumed = replacement_adapter.resume(accepted.task_id)
    assert resumed == accepted

    started = replacement_adapter.transition(
        accepted.task_id,
        state=TaskState.STARTED,
        checkpoint_ref="checkpoint://task/1",
        now=FIXED_NOW,
    )
    assert started.sequence == 1
    assert started.previous_receipt_sha256 == accepted.sha256


def test_external_mcp_handle_never_replaces_kpgs_task_identity():
    ledger = InMemoryTaskLedger()
    adapter = MCP20260728Adapter(ledger)
    accepted = _accept(adapter)

    started = adapter.transition(
        accepted.task_id,
        state=TaskState.STARTED,
        external_task_id="mcp-task-rebound",
        now=FIXED_NOW,
    )

    assert started.task_id == accepted.task_id
    assert started.external_task_id == "mcp-task-rebound"
    assert started.principal_id == accepted.principal_id
    assert started.capability_grant_id == accepted.capability_grant_id


def test_canonical_hash_is_order_independent_for_json_object_keys():
    left = {"task": {"b": 2, "a": 1}, "state": "started"}
    right = {"state": "started", "task": {"a": 1, "b": 2}}

    assert canonical_sha256(left) == canonical_sha256(right)


def test_evidence_is_hashed_without_content_capture():
    ledger = InMemoryTaskLedger()
    adapter = MCP20260728Adapter(ledger)
    accepted = _accept(adapter)

    started = adapter.transition(
        accepted.task_id,
        state=TaskState.STARTED,
        evidence={"private": "do-not-copy-into-telemetry"},
        evidence_uri="evidence://encrypted/object-1",
        now=FIXED_NOW,
    )

    item = started.evidence_refs[-1]
    assert len(item.sha256) == 64
    assert item.ref == "evidence://encrypted/object-1"
    assert item.content_captured is False
    assert "private" not in started.as_dict()["evidence_refs"][-1]


def test_terminal_state_cannot_silently_resume():
    ledger = InMemoryTaskLedger()
    adapter = MCP20260728Adapter(ledger)
    accepted = _accept(adapter)

    started = adapter.transition(
        accepted.task_id,
        state=TaskState.STARTED,
        now=FIXED_NOW,
    )
    completed = adapter.transition(
        started.task_id,
        state=TaskState.COMPLETED,
        result_ref="result://task/1",
        now=FIXED_NOW,
    )

    with pytest.raises(ContractError, match="terminal task"):
        adapter.transition(
            completed.task_id,
            state=TaskState.STARTED,
            now=FIXED_NOW,
        )
