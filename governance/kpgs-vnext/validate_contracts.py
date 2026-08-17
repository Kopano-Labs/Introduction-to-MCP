#!/usr/bin/env python3
"""Dependency-free structural gate for the current KPGS vNext governance contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def load_json(relative: str) -> Any:
    path = ROOT / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"KPGS-VNEXT FAIL: missing {relative}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"KPGS-VNEXT FAIL: invalid JSON in {relative}: {exc}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"KPGS-VNEXT FAIL: {message}")


def validate_schema(schema: dict[str, Any], name: str, required: set[str]) -> None:
    require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", f"{name} must use JSON Schema draft 2020-12")
    require(schema.get("type") == "object", f"{name} root must be an object")
    require(schema.get("additionalProperties") is False, f"{name} root must reject undeclared properties")
    declared = set(schema.get("required", []))
    require(required <= declared, f"{name} missing required fields: {sorted(required - declared)}")
    require(declared <= set(schema.get("properties", {})), f"{name} requires properties it does not declare")


def validate_security() -> None:
    schema = load_json("security/capability-lease.schema.json")
    validate_schema(
        schema,
        "capability lease schema",
        {
            "lease_id",
            "subject",
            "tenant_id",
            "domain_id",
            "task_id",
            "capabilities",
            "issued_at",
            "expires_at",
            "policy_decision_ref",
            "governing_spec_ref",
        },
    )
    capability_item = schema["properties"]["capabilities"]["items"]
    require({"name", "resource_scope"} <= set(capability_item.get("required", [])), "capability lease must bind capability name to resource scope")
    require("secret_provider_refs" in schema["properties"], "capability lease must reference secret providers instead of embedding durable secrets")


def validate_estate() -> None:
    schema = load_json("estate-registry/estate-registry.schema.json")
    estate = load_json("estate-registry/estate.json")
    validate_schema(schema, "estate registry schema", {"schema_version", "estate_id", "properties"})

    expected_domains = {
        "KasiLink.com",
        "FivesArena.com",
        "starfallsalvage.kopanolabs.com",
        "crisisconnect.kopanolabs.com",
        "KopanoLabs.com",
        "KRRababalela.com",
    }
    entries = estate.get("properties", [])
    domains = [entry.get("domain") for entry in entries]
    require(set(domains) == expected_domains, f"seed estate mismatch: missing={sorted(expected_domains - set(domains))}, extra={sorted(set(domains) - expected_domains)}")
    require(len(domains) == len(set(domains)), "estate registry domains must be unique")

    for entry in entries:
        status = entry.get("status")
        evidence = entry.get("ownership_evidence", [])
        if status in {"witnessed", "registered", "staging", "production"}:
            require(bool(evidence), f"{entry['domain']} cannot be {status} without ownership/control evidence")
        if status == "declared_pending_witness":
            require(entry.get("release", {}).get("live_ref") is None, f"{entry['domain']} must not claim a governed live release before witnessing")


def validate_evidence() -> None:
    schema = load_json("evidence/evidence-bundle.schema.json")
    validate_schema(
        schema,
        "evidence bundle schema",
        {
            "bundle_id",
            "created_at",
            "estate_property",
            "release_ref",
            "task_id",
            "correlation_id",
            "artifacts",
            "verifications",
            "governance_decision",
        },
    )
    verifications = schema["properties"]["verifications"]["items"]
    required_verifier_fields = {"verifier_id", "criterion_id", "method", "hard_gate", "passed", "evidence_ref"}
    require(required_verifier_fields <= set(verifications.get("required", [])), "evidence verifications must preserve hard-gate provenance")
    require(bool(schema.get("allOf")), "evidence schema must contain a structural promotion/hard-gate constraint")


def validate_skills() -> None:
    schema = load_json("skills/skill-manifest.schema.json")
    validate_schema(
        schema,
        "skill manifest schema",
        {
            "name",
            "version",
            "description",
            "category",
            "state",
            "runtime",
            "inputs",
            "outputs",
            "required_capabilities",
            "dependencies",
            "provenance",
            "validation",
            "failures",
        },
    )

    skill_dir = ROOT / "skills/core/kpgs-audit-verify-govern"
    manifest = json.loads((skill_dir / "skill.json").read_text(encoding="utf-8"))
    skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")

    require(skill_md.startswith("---\nname: kpgs-audit-verify-govern\n"), "canonical skill SKILL.md must start with declared frontmatter")
    require(manifest["name"] == "kpgs-audit-verify-govern", "skill manifest and SKILL.md identity must match")
    require(manifest["runtime"]["renter_protocol"] == "1.0", "canonical skill must declare renter protocol compatibility")

    license_status = manifest["provenance"]["license_status"]
    if license_status in {"unknown", "pending", "incompatible"}:
        require(manifest["state"] not in {"validated", "approved"}, "skill cannot be validated/approved while license status blocks promotion")

    for key in ("inputs", "outputs"):
        ref = manifest[key].get("schema_ref")
        if ref:
            resolved = (skill_dir / ref).resolve()
            require(resolved.is_file(), f"skill {key} schema_ref does not resolve: {ref}")
            require(ROOT in resolved.parents, f"skill {key} schema_ref escapes the KPGS vNext governance root")

    required_capabilities = manifest.get("required_capabilities", [])
    require(all(item.get("resource_scope") for item in required_capabilities), "every skill capability must declare a resource scope")


def validate_realtime() -> None:
    schema = load_json("realtime/connection-session.schema.json")
    validate_schema(
        schema,
        "realtime connection schema",
        {"connection_id", "tenant_id", "domain_id", "session_id", "transport", "user_state", "connected_at"},
    )
    transports = set(schema["properties"]["transport"]["enum"])
    require({"websocket", "sse", "polling"} <= transports, "realtime contract must include streaming and constrained-network fallback transports")
    user_states = set(schema["properties"]["user_state"]["enum"])
    require({"working", "waiting-for-approval", "offline", "reconnecting", "done", "failed"} <= user_states, "realtime contract is missing an everyday recovery/status state")
    require("resume_cursor" in schema["properties"], "realtime contract must support resume cursor semantics")
    require("checkpoint_ref" in schema["properties"], "realtime contract must link to canonical checkpoint state")


def validate_pwa() -> None:
    schema = load_json("pwa/interaction-profile.schema.json")
    validate_schema(schema, "interaction profile schema", {"profile_version", "preferences", "storage", "updated_at"})

    preferences = schema["properties"]["preferences"]
    expected_preferences = {"warmth", "formality", "detail_density", "pace", "initiative", "explanation_style"}
    require(expected_preferences <= set(preferences.get("required", [])), "interaction profile must keep bounded adaptation dimensions explicit")

    model_gateway = schema["properties"]["model_gateway"]["properties"]
    require(model_gateway.get("model_weight_training", {}).get("const") is False, "runtime interaction profile must explicitly forbid representing preference adaptation as model-weight training")

    storage = schema["properties"]["storage"]["properties"]
    require(storage.get("resettable", {}).get("const") is True, "interaction preferences must be resettable")
    require(bool(schema.get("allOf")), "account-synced interaction preferences must have a consent constraint")


def main() -> None:
    validate_security()
    validate_estate()
    validate_evidence()
    validate_skills()
    validate_realtime()
    validate_pwa()
    print("KPGS-VNEXT PASS: governance/runtime-facing contracts are structurally coherent.")
    print("Validated: capability leases, DNS estate seed, evidence, governed skills, realtime recovery, adaptive PWA profile.")


if __name__ == "__main__":
    main()
