#!/usr/bin/env python3
"""Dependency-free structural gate for KPGS vNext Phase 0 contracts."""

from __future__ import annotations

import json
import re
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


def validate_schema_shape(schema: dict[str, Any], name: str, required_keys: set[str]) -> None:
    require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", f"{name} must use draft 2020-12")
    require(schema.get("type") == "object", f"{name} root type must be object")
    require(schema.get("additionalProperties") is False, f"{name} root must reject undeclared properties")
    declared_required = set(schema.get("required", []))
    missing = required_keys - declared_required
    require(not missing, f"{name} missing required keys: {sorted(missing)}")
    properties = set(schema.get("properties", {}).keys())
    require(declared_required <= properties, f"{name} requires properties it does not declare")


def validate_renter() -> None:
    schema = load_json("stateless-renter/renter-envelope.schema.json")
    event = load_json("examples/renter-progress-event.json")

    required = {
        "protocol_version",
        "event_id",
        "event_kind",
        "tenant_id",
        "domain_id",
        "task_id",
        "renter_id",
        "correlation_id",
        "lease_id",
        "issued_at",
        "payload",
    }
    validate_schema_shape(schema, "renter envelope schema", required)
    require(required <= set(event), "reference renter event does not satisfy required envelope fields")
    require(re.fullmatch(r"[0-9]+\.[0-9]+", event["protocol_version"]) is not None, "invalid renter protocol version")
    require(event["event_kind"] in schema["properties"]["event_kind"]["enum"], "reference renter event kind is undeclared")
    require(bool(event.get("idempotency_key")), "reference renter event must demonstrate idempotency key usage")
    require(bool(event.get("governing_spec_ref")), "reference renter event must link its governing specification")


def validate_build_spec() -> None:
    schema = load_json("agent-governance/build-spec.schema.json")
    spec = load_json("examples/phase0-build-spec.json")

    required = {
        "spec_id",
        "title",
        "outcome",
        "scope",
        "interfaces",
        "constraints",
        "acceptance_criteria",
        "verification_plan",
        "rollback_plan",
        "risk_class",
        "required_capabilities",
        "lifecycle_state",
    }
    validate_schema_shape(schema, "build specification schema", required)
    require(required <= set(spec), "Phase 0 build spec does not contain every required governance field")
    require(spec["risk_class"] in {"R0", "R1", "R2", "R3"}, "invalid Phase 0 risk class")
    require(spec["lifecycle_state"] in {"draft", "verified", "approved", "released", "rejected", "rolled-back"}, "invalid lifecycle state")

    criteria = spec.get("acceptance_criteria", [])
    require(criteria, "Phase 0 build spec needs acceptance criteria")
    criterion_ids = [item.get("id") for item in criteria]
    require(len(criterion_ids) == len(set(criterion_ids)), "acceptance criterion IDs must be unique")
    require(all(item.get("verification_methods") for item in criteria), "every acceptance criterion needs a verification method")

    plan_ids = {item.get("criterion_id") for item in spec.get("verification_plan", [])}
    require(set(criterion_ids) <= plan_ids, "verification plan must cover every acceptance criterion")
    require(bool(spec.get("rollback_plan", {}).get("procedure")), "rollback procedure is required")


def validate_fork_matrix() -> None:
    matrix = load_json("fork-assimilation/evolution-matrix.json")
    forks = matrix.get("forks", [])

    expected = {
        "RobynAwesome/sketchbook",
        "RobynAwesome/DesignerNewsApp",
        "RobynAwesome/kage",
        "RobynAwesome/claude-code-templates",
        "RobynAwesome/my-react-app",
        "RobynAwesome/paws-and-potjie",
        "RobynAwesome/Skills",
        "RobynAwesome/JavaScriptMastery-skills",
        "RobynAwesome/jwt-auth",
        "RobynAwesome/towers",
        "RobynAwesome/adk_tutorial",
        "RobynAwesome/cars4mars-project",
        "RobynAwesome/OmniRoute",
        "RobynAwesome/JavaScriptMastery-gsap-cc-starter",
        "RobynAwesome/generative-ai",
    }
    repos = [item.get("repository") for item in forks]
    require(len(forks) == 15, f"fork matrix must contain exactly 15 repositories; found {len(forks)}")
    require(len(repos) == len(set(repos)), "fork matrix repository entries must be unique")
    require(set(repos) == expected, f"fork matrix inventory mismatch: missing={sorted(expected - set(repos))}, extra={sorted(set(repos) - expected)}")

    required_fields = {
        "repository",
        "upstream",
        "role",
        "target_layers",
        "disposition",
        "provenance_status",
        "license_status",
        "security_status",
        "notes",
    }
    forbidden_auto_import = {"import", "vendor", "canonical-import"}
    unverified_license_states = {"pending_audit", "unverified_reference_only", "no_github_detected_license"}
    for item in forks:
        require(required_fields <= set(item), f"{item.get('repository')} missing assimilation fields")
        require(item["target_layers"], f"{item['repository']} needs at least one target layer")
        if item["license_status"] in unverified_license_states:
            require(item["disposition"] not in forbidden_auto_import, f"{item['repository']} cannot be imported before license verification")

    kage = next(item for item in forks if item["repository"] == "RobynAwesome/kage")
    require(kage["disposition"] == "no-import", "kage must remain no-import while reuse rights are unverified")
    require(kage["license_status"] == "unverified_reference_only", "kage license state must explicitly block reuse")


def main() -> None:
    validate_renter()
    validate_build_spec()
    validate_fork_matrix()
    print("KPGS-VNEXT PASS: Phase 0 truth/contracts are structurally governed.")
    print("Validated: Stateless Renter envelope, build specification, 15-repository fork assimilation matrix.")


if __name__ == "__main__":
    main()
