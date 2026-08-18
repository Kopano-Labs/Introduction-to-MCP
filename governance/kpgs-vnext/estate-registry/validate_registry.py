"""Dependency-free validator for the KPGS Sovereign Estate Registry runtime."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ESTATE = HERE / "estate.json"
REGISTRY_SCHEMA = HERE / "estate-registry.schema.json"
CANDIDATE_SCHEMA = HERE / "discovery-candidate.schema.json"
REGISTRY_RUNTIME = HERE / "registry.py"
LEASE_RUNTIME = HERE.parent / "security" / "capability_lease.py"

INITIAL_DOMAINS = {
    "KasiLink.com",
    "FivesArena.com",
    "starfallsalvage.kopanolabs.com",
    "crisisconnect.kopanolabs.com",
    "KopanoLabs.com",
    "KRRababalela.com",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"KPGS-ESTATE FAIL: {message}")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    estate = json.loads(ESTATE.read_text(encoding="utf-8"))
    registry_schema = json.loads(REGISTRY_SCHEMA.read_text(encoding="utf-8"))
    candidate_schema = json.loads(CANDIDATE_SCHEMA.read_text(encoding="utf-8"))

    domains = {item["domain"] for item in estate["properties"]}
    require(domains == INITIAL_DOMAINS, "initial canonical DNS estate drifted")
    require(
        all(item["status"] == "declared_pending_witness" for item in estate["properties"]),
        "unwitnessed initial property was silently promoted",
    )

    property_schema = registry_schema["properties"]["properties"]["items"]["properties"]
    for required_link in (
        "repositories",
        "deployment",
        "adapter",
        "renter_compatibility",
        "governance",
        "capabilities",
        "health_endpoints",
        "release",
        "rollback",
    ):
        require(required_link in property_schema, f"registry linkage missing {required_link}")
    require(
        "://" in property_schema["secret_provider_refs"]["items"]["pattern"],
        "secret provider fields no longer require references",
    )

    candidate_states = set(candidate_schema["properties"]["status"]["enum"])
    require(
        candidate_states == {"unwitnessed", "witnessed", "classified", "rejected", "registered"},
        "candidate review states drifted",
    )

    lease_mod = load_module("kpgs_estate_validator_lease", LEASE_RUNTIME)
    registry_mod = load_module("kpgs_estate_validator_runtime", REGISTRY_RUNTIME)
    fixed_now = datetime(2026, 8, 18, 9, 45, tzinfo=timezone.utc)
    authority = lease_mod.CapabilityLeaseAuthority(
        lease_mod.KeyRing({"estate-validator": b"v" * 32}, "estate-validator"),
        clock=lambda: fixed_now,
        max_ttl_seconds=600,
    )
    token = authority.issue(
        subject_id="service:validator-hub",
        subject_kind="service",
        tenant_id="tenant:kopano",
        domain_id="KopanoLabs.com",
        task_id="task:estate-validator",
        capabilities=[
            {
                "name": "estate.discovery.write",
                "resource_scope": "estate:kopano-sovereign-estate",
            },
            {
                "name": "estate.registry.witness",
                "resource_scope": "dns:validator.example.org",
            },
            {
                "name": "estate.registry.classify",
                "resource_scope": "dns:validator.example.org",
            },
        ],
        policy_decision_ref="policy://validator/estate",
        governing_spec_ref="spec://validator/estate/v1",
        ttl_seconds=300,
        correlation_id="corr:estate-validator",
        evidence_ref="evidence://estate-validator/lease",
    )
    registry = registry_mod.SovereignEstateRegistry(
        estate,
        authority,
        clock=lambda: fixed_now,
    )

    def context(nonce: str):
        return registry_mod.MutationContext(
            token=token,
            tenant_id="tenant:kopano",
            domain_id="KopanoLabs.com",
            task_id="task:estate-validator",
            operation_nonce=nonce,
            correlation_id=f"corr:{nonce}",
        )

    candidate = registry.discover_candidate(
        "validator.example.org",
        provenance={
            "kind": "dns",
            "ref": "dns://validator/observed",
            "observed_at": "2026-08-18T09:44:00Z",
        },
        context=context("validator-discover"),
    )
    require(candidate["status"] == "unwitnessed", "discovery self-promoted")
    require(
        "validator.example.org" not in {item["domain"] for item in registry.snapshot()["properties"]},
        "unwitnessed candidate entered canonical property registry",
    )

    witnessed = registry.witness_candidate(
        candidate["candidate_id"],
        {
            "kind": "domain-control",
            "ref": "witness://validator/control",
            "verified_at": "2026-08-18T09:45:00+00:00",
        },
        context=context("validator-witness"),
    )
    require(witnessed["status"] == "witnessed", "candidate witness transition failed")
    classified = registry.classify_candidate(
        candidate["candidate_id"],
        owner_ref="owner://validator",
        governance_tier="T1",
        risk_class="R1",
        context=context("validator-classify"),
    )
    require(classified["status"] == "classified", "candidate classification failed")

    pending_answer = registry.explain_property("FivesArena.com")
    for phrase in (
        "declared_pending_witness",
        "Repositories: not witnessed",
        "Capabilities: not granted",
        "Live version: not promoted",
        "Rollback target: not recorded",
    ):
        require(phrase in pending_answer, f"plain-language answer lost: {phrase}")

    events = registry.events()
    require(len(events) == 3, "review queue did not emit governed events")
    require(
        all(event["transport_grants_authority"] is False for event in events),
        "event distribution widened authority",
    )
    require(
        all(event["canonical_registry_changed"] is False for event in events),
        "candidate review mutated canonical property registry",
    )

    print(
        "KPGS-ESTATE PASS: discovery is unwitnessed-by-default, lease-scoped, "
        "promotion-gated and plain-language queryable."
    )


if __name__ == "__main__":
    main()
