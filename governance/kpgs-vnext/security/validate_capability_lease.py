"""Dependency-free validator for the executable KPGS capability lease boundary."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SCHEMA = HERE / "capability-lease.schema.json"
RUNTIME = HERE / "capability_lease.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"KPGS-LEASE FAIL: {message}")


def load_runtime():
    spec = importlib.util.spec_from_file_location("kpgs_lease_validator_runtime", RUNTIME)
    require(spec is not None and spec.loader is not None, "lease runtime cannot load")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = set(schema.get("required", []))
    require("nonce" in required, "lease nonce must be structurally required")
    require("audit" in required, "lease audit correlation must be structurally required")
    audit_required = set(schema["properties"]["audit"].get("required", []))
    require(
        {"correlation_id", "evidence_ref"} <= audit_required,
        "audit must preserve correlation and evidence refs",
    )
    secret_pattern = schema["properties"]["secret_provider_refs"]["items"].get("pattern", "")
    require("://" in secret_pattern, "secret provider refs must remain URI-like references")

    runtime = load_runtime()
    fixed_now = datetime(2026, 8, 18, 9, 0, tzinfo=timezone.utc)
    ring = runtime.KeyRing({"validator-k1": b"k" * 32}, "validator-k1")
    authority = runtime.CapabilityLeaseAuthority(
        ring,
        clock=lambda: fixed_now,
        max_ttl_seconds=300,
    )
    token = authority.issue(
        subject_id="renter:validator",
        subject_kind="renter",
        tenant_id="tenant:validator",
        domain_id="KopanoLabs.com",
        task_id="task:validator",
        capabilities=[
            {
                "name": "estate.registry.read",
                "resource_scope": "estate:kopano-labs",
            }
        ],
        policy_decision_ref="policy://validator/allow",
        governing_spec_ref="spec://validator/v1",
        ttl_seconds=120,
        secret_provider_refs=("vault://validator/reference",),
        correlation_id="corr:validator",
        evidence_ref="evidence://validator/lease",
    )
    decision = authority.authorize(
        token,
        tenant_id="tenant:validator",
        domain_id="KopanoLabs.com",
        task_id="task:validator",
        capability="estate.registry.read",
        resource_scope="estate:kopano-labs",
        operation_nonce="validator-operation-001",
        correlation_id="corr:validator-use",
    )
    require(decision.key_id == "validator-k1", "lease key id was not verified")

    try:
        authority.authorize(
            token,
            tenant_id="tenant:other",
            domain_id="KopanoLabs.com",
            task_id="task:validator",
            capability="estate.registry.read",
            resource_scope="estate:kopano-labs",
            operation_nonce="validator-operation-002",
            correlation_id="corr:validator-deny",
        )
    except runtime.LeaseDenied:
        pass
    else:
        raise SystemExit("KPGS-LEASE FAIL: cross-tenant request was admitted")

    audit_text = json.dumps(authority.audit_events(), sort_keys=True)
    require(token not in audit_text, "raw lease token leaked into audit")
    require("vault://validator/reference" not in audit_text, "secret-provider reference leaked into use audit")
    require("kkkkkkkk" not in audit_text, "signing material leaked into audit")

    ring.rotate("validator-k2", b"z" * 32)
    old_payload, old_kid = authority.verify(token)
    require(old_payload["lease_id"] == decision.lease_id, "old live lease changed after rotation")
    require(old_kid == "validator-k1", "old live lease did not retain its original key id")

    print(
        "KPGS-LEASE PASS: short-lived signed authority is exact-scoped, "
        "replay/revocation-ready, auditable and rotation-safe."
    )


if __name__ == "__main__":
    main()
