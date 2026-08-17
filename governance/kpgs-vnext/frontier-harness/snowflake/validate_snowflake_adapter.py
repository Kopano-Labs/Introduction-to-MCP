#!/usr/bin/env python3
"""Dependency-free gate for the KPGS Snowflake v0.2 adapter."""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"KPGS-SNOWFLAKE FAIL: {message}")


def load_adapter():
    spec = importlib.util.spec_from_file_location("kpgs_snowflake_adapter", ROOT / "sql_api_adapter.py")
    require(spec is not None and spec.loader is not None, "adapter must be importable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    adapter = load_adapter()
    now = datetime(2026, 8, 17, 15, 30, tzinfo=timezone.utc)
    lease = {
        "lease_id": "lease_snowflake_test_001",
        "subject": {"id": "frontier-snowflake-adapter", "kind": "adapter"},
        "tenant_id": "kopano-labs",
        "domain_id": "Introduction-to-MCP",
        "task_id": "frontier-snowflake-v0.2-test",
        "capabilities": [{"name": "snowflake.telemetry.append", "resource_scope": "KPGS_FRONTIER.EVIDENCE.FRONTIER_TELEMETRY", "constraints": ["append-only", "metadata-and-digests-only"]}],
        "issued_at": (now - timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
        "expires_at": (now + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        "policy_decision_ref": "policy://frontier-snowflake-v0.2/test",
        "governing_spec_ref": "kpgs-frontier-harness-snowflake-v0.2",
        "secret_provider_refs": ["env://KPGS_SNOWFLAKE_PAT"],
    }
    row = {
        "event_schema": "kpgs.frontier_telemetry.v1",
        "request_id": "req_frontier_validation_001",
        "source_provider": "fillout",
        "capability": "reasoning",
        "selected_provider": "google-ai",
        "output_digest": "a" * 64,
        "data_classification": "synthetic",
        "external_processing_allowed": True,
    }
    target = adapter.SnowflakeTarget("org-account", "KPGS_FRONTIER_WH", "KPGS_FRONTIER_INGEST")
    prepared = adapter.prepare_telemetry_insert(row, lease, target, now=now)
    receipt = prepared.safe_receipt()
    serialized = json.dumps(prepared.body, sort_keys=True).lower()
    require(prepared.endpoint.endswith(".snowflakecomputing.com/api/v2/statements"), "wrong SQL API endpoint")
    require(len(prepared.body["bindings"]) == 8, "insert must bind exactly eight telemetry values")
    require("semantic_input" not in serialized and "private_payload" not in serialized, "prepared request leaked forbidden content")
    require("kpgs_snowflake_pat" not in serialized, "prepared SQL body must not contain secret reference or token")
    require(receipt["contains_secret"] is False, "safe receipt must exclude secrets")

    blocked = dict(row)
    blocked["semantic_input"] = "must never leave sovereign boundary"
    try:
        adapter.prepare_telemetry_insert(blocked, lease, target, now=now)
    except adapter.GovernanceError:
        pass
    else:
        raise SystemExit("KPGS-SNOWFLAKE FAIL: semantic input was not rejected")

    expired = dict(lease)
    expired["issued_at"] = "2026-08-16T00:00:00Z"
    expired["expires_at"] = "2026-08-16T00:10:00Z"
    try:
        adapter.prepare_telemetry_insert(row, expired, target, now=now)
    except adapter.GovernanceError:
        pass
    else:
        raise SystemExit("KPGS-SNOWFLAKE FAIL: expired lease was accepted")

    print("KPGS-SNOWFLAKE PASS: adapter is fail-closed, capability-leased and secret-external.")
    print(f"Prepared: {prepared.request_id} -> {prepared.endpoint}")


if __name__ == "__main__":
    main()
