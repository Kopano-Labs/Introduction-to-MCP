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
LIVE_WITNESS_SCHEMA = HERE / "live-provider-witness.schema.json"
LIVE_WITNESS_DIR = HERE / "evidence"
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
    live_witness_schema = json.loads(LIVE_WITNESS_SCHEMA.read_text(encoding="utf-8"))

    domains = {item["domain"] for item in estate["properties"]}
    require(domains == INITIAL_DOMAINS, "initial canonical DNS estate drifted")

    allowed_property_states = set(
        registry_schema["properties"]["properties"]["items"]["properties"]["status"]["enum"]
    )
    for item in estate["properties"]:
        status = item.get("status")
        evidence = item.get("ownership_evidence") or []
        require(status in allowed_property_states, f"{item['domain']} has invalid lifecycle status")
        if status == "declared_pending_witness":
            require(not evidence, f"{item['domain']} is pending but already carries ownership evidence")
            require(
                item.get("release", {}).get("live_ref") is None,
                f"{item['domain']} must not claim a governed live release before witnessing",
            )
        elif status in {"witnessed", "registered", "staging", "production"}:
            require(bool(evidence), f"{item['domain']} cannot be {status} without ownership/control evidence")
        if status == "production":
            release = item.get("release") or {}
            rollback = item.get("rollback") or {}
            require(
                bool(release.get("live_ref") and release.get("evidence_ref")),
                f"{item['domain']} production state requires exact live/evidence refs",
            )
            require(
                bool(rollback.get("target_ref") and rollback.get("procedure_ref")),
                f"{item['domain']} production state requires rollback refs",
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

    require(
        live_witness_schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        "live provider witness schema must use draft 2020-12",
    )
    require(
        live_witness_schema.get("properties", {}).get("authority_effect", {}).get("const")
        == "witness-only",
        "live provider witness must remain non-promoting",
    )

    receipt_witnessed_domains: set[str] = set()
    for receipt_path in sorted(LIVE_WITNESS_DIR.glob("live-provider-witness-*.json")):
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        require(receipt.get("schema") == "kpgs.live-provider-witness.v1", f"invalid witness receipt schema in {receipt_path.name}")
        require(receipt.get("authority_effect") == "witness-only", f"{receipt_path.name} widened witness authority")
        require(
            isinstance(receipt.get("provider_mutation_performed"), bool),
            f"{receipt_path.name} must explicitly state provider mutation effect",
        )
        for observed in receipt.get("properties") or []:
            domain = observed.get("domain")
            require(domain in INITIAL_DOMAINS, f"{receipt_path.name} references unknown estate domain {domain}")
            require(bool(observed.get("domain_bindings")), f"{domain} witness lacks provider domain binding")
            require(bool(observed.get("deployments")), f"{domain} witness lacks deployment evidence")
            if observed.get("admission_recommendation") == "WITNESS":
                receipt_witnessed_domains.add(domain)

    estate_by_domain = {item["domain"]: item for item in estate["properties"]}
    for domain in receipt_witnessed_domains:
        require(
            estate_by_domain[domain]["status"] != "declared_pending_witness",
            f"{domain} has admitted witness receipt but registry was not advanced to witnessed-or-later",
        )
        require(
            bool(estate_by_domain[domain]["ownership_evidence"]),
            f"{domain} witness admission lost ownership/control evidence",
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
        "KPGS-ESTATE PASS: discovery is unwitnessed-by-default, connected witness "
        "receipts remain non-promoting, and lifecycle state is evidence-gated."
    )


if __name__ == "__main__":
    main()
