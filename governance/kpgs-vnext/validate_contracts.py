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


def validate_skill_package(skill_name: str) -> None:
    skill_dir = ROOT / f"skills/core/{skill_name}"
    manifest = json.loads((skill_dir / "skill.json").read_text(encoding="utf-8"))
    skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")

    require(skill_md.startswith(f"---\nname: {skill_name}\n"), f"{skill_name} SKILL.md must start with matching frontmatter")
    require(manifest["name"] == skill_name, f"{skill_name} manifest and SKILL.md identity must match")
    require(manifest["runtime"]["renter_protocol"] == "1.0", f"{skill_name} must declare renter protocol compatibility")

    license_status = manifest["provenance"]["license_status"]
    if license_status in {"unknown", "pending", "incompatible"}:
        require(manifest["state"] not in {"validated", "approved"}, f"{skill_name} cannot be validated/approved while license status blocks promotion")

    for key in ("inputs", "outputs"):
        ref = manifest[key].get("schema_ref")
        if ref:
            resolved = (skill_dir / ref).resolve()
            require(resolved.is_file(), f"{skill_name} {key} schema_ref does not resolve: {ref}")
            require(ROOT in resolved.parents, f"{skill_name} {key} schema_ref escapes the KPGS vNext governance root")

    required_capabilities = manifest.get("required_capabilities", [])
    require(all(item.get("resource_scope") for item in required_capabilities), f"every {skill_name} capability must declare a resource scope")


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

    validate_skill_package("kpgs-audit-verify-govern")
    validate_skill_package("kpgs-human-choice-authorship")


def validate_human_choice_authorship() -> None:
    schema = load_json("human-choice-authorship/choice-authorship-record.schema.json")
    record = load_json("human-choice-authorship/example.choice-authorship.json")
    build_spec = load_json("agent-governance/specs/human-choice-authorship-poc.json")

    validate_schema(
        schema,
        "human choice authorship schema",
        {
            "schema_version",
            "record_id",
            "subject_authority",
            "current_state",
            "context_claims",
            "root_algorithm_candidates",
            "cdp",
            "human_consent",
            "convergence",
            "authorship_status",
            "action_authority",
            "re_evaluation_required",
        },
    )

    candidate_schema = schema["properties"]["cdp"]["properties"]["candidate_families"]
    unknown_id = candidate_schema.get("contains", {}).get("properties", {}).get("candidate_id", {}).get("const")
    require(unknown_id == "cdp-unknown-possibility", "choice-authorship schema must structurally require an explicit CDP unknown branch")
    require(bool(schema.get("allOf")), "choice-authorship schema must encode consent and runtime hard gates")

    require(record.get("subject_authority") == "human", "personal choice authority must remain human")

    root_candidates = record.get("root_algorithm_candidates", [])
    for candidate in root_candidates:
        require(candidate.get("proof_state") == "hypothesis", "root algorithm candidates must remain hypotheses")
        require(candidate.get("canonical") is False, "root algorithm candidates cannot self-canonicalize")

    cdp = record.get("cdp", {})
    candidates = cdp.get("candidate_families", [])
    require(len(candidates) >= 2, "choice-authorship CDP needs at least two candidate families")
    differences = [candidate.get("difference", "").strip().lower() for candidate in candidates]
    require(all(differences), "every choice-authorship CDP candidate needs a structural difference")
    require(len(differences) == len(set(differences)), "choice-authorship CDP candidates cannot be cosmetic duplicates")
    require(cdp.get("unknown_branch_preserved") is True, "choice-authorship CDP must preserve an unknown branch")
    require(cdp.get("canonicalized") is False, "CDP cannot self-canonicalize")
    require(any(candidate.get("candidate_id") == "cdp-unknown-possibility" for candidate in candidates), "example must contain an explicit unknown possibility")
    require(all(candidate.get("proof_state") == "hypothesis" and candidate.get("canonical") is False for candidate in candidates), "CDP candidate families must remain non-canonical hypotheses")
    if cdp.get("runtime_execution_proven") is True:
        require(bool(cdp.get("runtime_receipt_ref")), "proven CDP runtime execution requires a receipt reference")

    consent = record.get("human_consent", {})
    consent_response = consent.get("response")
    authorship_status = record.get("authorship_status")
    action = record.get("action_authority", {})

    if consent_response in {"endorse", "reject", "hold"}:
        require(consent.get("explicitly_human_supplied") is True, "non-empty human consent cannot be inferred by the system")
        require(bool(consent.get("human_statement_ref")), "human consent requires a current human statement reference")
    if authorship_status in {"human-endorsed", "authored-choice-candidate"}:
        require(consent_response == "endorse", "endorsed/authored state requires human endorsement")
    if authorship_status == "human-rejected":
        require(consent_response == "reject", "human-rejected state requires explicit rejection")
    if authorship_status == "human-held":
        require(consent_response == "hold", "human-held state requires explicit hold")
    if action.get("authorized") is True:
        require(consent_response == "endorse", "authorized personal action requires human endorsement")
    require(action.get("authority_holder") == "human", "action authority cannot be assigned to a renter or model")

    convergence = record.get("convergence", {})
    if convergence.get("runtime_execution_proven") is True:
        require(bool(convergence.get("receipt_ref")), "proven CCP runtime execution requires a receipt reference")
    if convergence.get("canonical") is True:
        require(convergence.get("decision") == "Accepted", "only CCP Accepted may be represented as canonical")
        require(convergence.get("runtime_execution_proven") is True, "canonical CCP state requires a runtime execution receipt")
    if convergence.get("decision") == "not-requested":
        require(convergence.get("canonical") is False, "CCP cannot be canonical when convergence was not requested")
        require(convergence.get("runtime_execution_proven") is False, "CCP execution cannot be proven when convergence was not requested")

    skill_manifest = load_json("skills/core/kpgs-human-choice-authorship/skill.json")
    require(skill_manifest.get("state") == "draft", "human choice skill must remain draft while this work is POC and license status is unresolved")
    sources = skill_manifest.get("provenance", {}).get("sources", [])
    project_jennifer = next((source for source in sources if source.get("ref") == "RobynAwesome/Project-Jennifer"), None)
    require(project_jennifer is not None, "human choice skill must preserve Project Jennifer provenance")
    require(project_jennifer.get("commit") == "5328a8449bad509150f73fe9aafeabc6c17c983b", "Project Jennifer provenance must be pinned to the reviewed revision")

    require(build_spec.get("spec_id") == "kpgs-human-choice-authorship-poc-v0.1", "choice-authorship build spec identity mismatch")
    require(build_spec.get("risk_class") == "R2", "identity-sensitive choice-authorship POC must retain its declared R2 risk class")
    require(build_spec.get("lifecycle_state") == "draft", "choice-authorship build spec must remain draft until executable validation exists")
    require(49 in build_spec.get("related_issues", []), "choice-authorship build spec must link issue #49")
    criteria = build_spec.get("acceptance_criteria", [])
    criterion_ids = [criterion.get("id") for criterion in criteria]
    require(len(criterion_ids) == len(set(criterion_ids)), "choice-authorship acceptance criterion IDs must be unique")
    plan_ids = {item.get("criterion_id") for item in build_spec.get("verification_plan", [])}
    require(set(criterion_ids) <= plan_ids, "choice-authorship verification plan must cover every acceptance criterion")


def validate_mmao_mao_identity_governance() -> None:
    identity_schema = load_json("agent-governance/mmao-mao/identity-provenance.schema.json")
    identity_record = load_json("agent-governance/mmao-mao/fixtures/jiro-khelos-provenance.json")
    boundary_schema = load_json("agent-governance/mmao-mao/authority-boundary.schema.json")
    boundary_matrix = load_json("agent-governance/mmao-mao/fixtures/authority-boundary-matrix.json")
    experiment_schema = load_json("agent-governance/mmao-mao/model-interface-affinity-experiment.schema.json")
    experiment = load_json("agent-governance/mmao-mao/fixtures/recycler-mmao-plus-mao-experiment.json")
    failure_schema = load_json("agent-governance/mmao-mao/failure-receipt.schema.json")
    failure_receipt = load_json("agent-governance/mmao-mao/fixtures/controlled-scope-breach-receipt.json")
    build_spec = load_json("agent-governance/specs/mmao-mao-identity-governance-v0.1.json")

    validate_schema(
        identity_schema,
        "MMAO + MAO identity provenance schema",
        {"identity", "seat", "interface", "model", "task", "authority", "context_state", "provenance", "evidence_receipt_refs"},
    )
    authority = identity_schema["properties"]["authority"]
    require(
        {"scope_type", "task_ref", "high_task_authority", "global_maintenance_seat"}
        <= set(authority.get("required", [])),
        "MMAO + MAO identity authority must preserve task/global distinction",
    )
    allowlist = set(authority["properties"]["global_maintenance_seat"]["enum"])
    require(
        allowlist == {None, "codex-chief-architect", "antigravity-chief-facilitator", "cursor-lead-developer"},
        "MMAO + MAO global structural-maintenance allowlist drifted",
    )
    record_authority = identity_record.get("authority", {})
    require(identity_record.get("identity", {}).get("identity_id") == "jiro", "MMAO + MAO fixture must preserve Jiro identity")
    require(record_authority.get("scope_type") == "task-scoped", "MMAO + MAO fixture must remain task-scoped")
    require(record_authority.get("high_task_authority") is True, "MMAO + MAO fixture must exercise high task authority")
    require(record_authority.get("global_maintenance_seat") is None, "high task authority cannot name a global maintenance seat")
    require(bool(record_authority.get("task_ref")), "task-scoped authority must name an explicit task")

    validate_schema(
        boundary_schema,
        "MMAO + MAO authority boundary schema",
        {"invariant", "current_structural_maintenance_hierarchy", "task_scoped_authority", "reconciliation_state"},
    )
    expected_hierarchy = [
        (1, "Codex", "codex-chief-architect", "Chief Architect"),
        (2, "Anti-Gravity", "antigravity-chief-facilitator", "Chief Facilitator"),
        (3, "Cursor", "cursor-lead-developer", "Lead Developer"),
    ]
    actual_hierarchy = [
        (entry.get("rank"), entry.get("actor"), entry.get("seat_id"), entry.get("title"))
        for entry in boundary_matrix.get("current_structural_maintenance_hierarchy", [])
    ]
    require(actual_hierarchy == expected_hierarchy, "MMAO + MAO current maintenance hierarchy drifted")
    high_task = next(
        (entry for entry in boundary_matrix.get("task_scoped_authority", []) if entry.get("authority_class") == "high-task-authority"),
        None,
    )
    require(high_task is not None, "MMAO + MAO boundary matrix lacks high task authority")
    require(
        "global structural-maintenance" in " ".join(high_task.get("forbidden_without_separate_elevation", [])).lower(),
        "MMAO + MAO high task authority must explicitly forbid global maintenance",
    )

    validate_schema(
        experiment_schema,
        "MMAO + MAO affinity experiment schema",
        {"working_testimony", "baseline", "controlled_invariants", "comparison_runs", "evidence_policy", "retest_policy"},
    )
    require(experiment.get("status") == "planned", "MMAO + MAO fixture cannot claim live execution")
    require(experiment.get("working_testimony") == "Recycler MMAO with Plus MAO", "working testimony must remain preserved")
    invariants = experiment.get("controlled_invariants", {})
    require(
        {"identity", "seat", "interface", "model", "repository-state", "context-snapshot", "tool-trace", "verification", "independent-review"}
        <= set(invariants.get("evidence_requirements", [])),
        "MMAO + MAO experiment evidence requirements are incomplete",
    )
    comparison_runs = experiment.get("comparison_runs", [])
    required_comparisons = {"reference", "model-only", "interface-only", "seat-only", "substrate-comparison"}
    require(required_comparisons <= {run.get("comparison_type") for run in comparison_runs}, "MMAO + MAO experiment matrix is incomplete")
    for run in comparison_runs:
        require(run.get("identity_id") == invariants.get("identity_id"), "MMAO + MAO comparison changed identity")
        require(run.get("task_id") == invariants.get("task_id"), "MMAO + MAO comparison changed task")
        require(run.get("status") == "planned", "MMAO + MAO fixture falsely claims execution")
        require(run.get("actual_behavior") is None and run.get("tool_trace_ref") is None, "MMAO + MAO planned run contains fabricated execution evidence")
        require(not run.get("evidence_refs"), "MMAO + MAO planned run contains fabricated evidence")
    require(experiment.get("evidence_policy") == {"raw_prompt_capture": False, "independent_review_required": True, "consensus_is_truth": False}, "MMAO + MAO evidence policy drifted")

    validate_schema(
        failure_schema,
        "MMAO + MAO failure receipt schema",
        {"expected_behavior", "actual_behavior", "identity", "seat", "model", "interface", "repository_state", "action_tool_trace", "evidence_refs", "failure_class", "five_whys", "correction", "retest", "rtc_reviews", "review_aggregation"},
    )
    require(failure_receipt.get("receipt_status") == "synthetic-fixture", "failure fixture cannot impersonate a live incident")
    require("Synthetic fixture:" in failure_receipt.get("actual_behavior", ""), "failure fixture must disclose synthetic status")
    require(failure_receipt.get("action_tool_trace", {}).get("capture_mode") == "metadata-only", "MMAO + MAO failure trace must remain metadata-only")
    require([why.get("index") for why in failure_receipt.get("five_whys", [])] == [1, 2, 3, 4, 5], "MMAO + MAO failure receipt must preserve exactly five ordered Whys")
    require(failure_receipt.get("retest", {}).get("status") == "not-run", "synthetic failure fixture cannot claim a retest result")
    require(failure_receipt.get("review_aggregation", {}).get("mode") == "evidence-convergence-not-vote", "RTC review became a vote")
    require(failure_receipt.get("review_aggregation", {}).get("decision_rule") == "unsupported-claims-remain-held", "unsupported MMAO + MAO claim lost HOLD")

    require(build_spec.get("spec_id") == "kpgs-mmao-mao-identity-governance-v0.1", "MMAO + MAO build spec identity mismatch")
    require(build_spec.get("risk_class") == "R2", "MMAO + MAO identity-governance POC must retain R2")
    require(build_spec.get("lifecycle_state") == "draft", "MMAO + MAO experiment must remain draft before live evidence")
    criteria = build_spec.get("acceptance_criteria", [])
    criterion_ids = [criterion.get("id") for criterion in criteria]
    require(len(criterion_ids) == len(set(criterion_ids)), "MMAO + MAO acceptance criterion IDs must be unique")
    plan_ids = {item.get("criterion_id") for item in build_spec.get("verification_plan", [])}
    require(set(criterion_ids) <= plan_ids, "MMAO + MAO verification plan must cover every acceptance criterion")


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
    validate_human_choice_authorship()
    validate_mmao_mao_identity_governance()
    validate_realtime()
    validate_pwa()
    print("KPGS-VNEXT PASS: governance/runtime-facing contracts are structurally coherent.")
    print("Validated: capability leases, DNS estate seed, evidence, governed skills, human choice authorship, MMAO + MAO identity governance, realtime recovery, adaptive PWA profile.")


if __name__ == "__main__":
    main()
