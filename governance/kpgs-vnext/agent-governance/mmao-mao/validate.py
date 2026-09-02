#!/usr/bin/env python3
"""Dependency-free structural gate for the MMAO + MAO identity-governance POC."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"KPGS-MMAO-MAO FAIL: {message}")


def load_json(relative: str) -> dict[str, Any]:
    path = HERE / relative
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"KPGS-MMAO-MAO FAIL: missing {relative}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"KPGS-MMAO-MAO FAIL: invalid JSON in {relative}: {exc}") from exc
    require(isinstance(value, dict), f"{relative} must contain a JSON object")
    return value


def validate_schema_shape(relative: str, required: set[str]) -> dict[str, Any]:
    schema = load_json(relative)
    require(
        schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        f"{relative} must use JSON Schema Draft 2020-12",
    )
    require(schema.get("type") == "object", f"{relative} must define an object root")
    require(
        schema.get("additionalProperties") is False,
        f"{relative} must reject undeclared root properties",
    )
    declared = set(schema.get("required", []))
    require(required <= declared, f"{relative} missing required fields: {sorted(required - declared)}")
    return schema


def validate_identity_contract() -> None:
    schema = validate_schema_shape(
        "identity-provenance.schema.json",
        {
            "identity",
            "seat",
            "interface",
            "model",
            "task",
            "authority",
            "context_state",
            "provenance",
            "evidence_receipt_refs",
        },
    )
    authority = schema["properties"]["authority"]
    required = set(authority["required"])
    require(
        {"scope_type", "task_ref", "high_task_authority", "global_maintenance_seat"} <= required,
        "identity authority contract lost task/global boundary fields",
    )
    global_allowlist = authority["properties"]["global_maintenance_seat"]["enum"]
    require(
        set(global_allowlist) == {
            None,
            "codex-chief-architect",
            "antigravity-chief-facilitator",
            "cursor-lead-developer",
        },
        "global structural-maintenance allowlist drifted",
    )

    record = load_json("fixtures/jiro-khelos-provenance.json")
    require(
        record.get("schema_version") == "kpgs.mmao-mao.identity-provenance.v1",
        "identity fixture schema version mismatch",
    )
    identity = record["identity"]
    require(identity["identity_id"] == "jiro", "identity fixture must preserve Jiro")
    require(
        identity["ontology_boundary"] == "governance-namespace-not-proof-of-personhood",
        "identity record must preserve its ontology boundary",
    )
    authority_record = record["authority"]
    require(authority_record["scope_type"] == "task-scoped", "fixture must remain task-scoped")
    require(authority_record["high_task_authority"] is True, "fixture must exercise high task authority")
    require(
        authority_record["global_maintenance_seat"] is None,
        "high task authority must not name a global maintenance seat",
    )
    require(bool(authority_record["task_ref"]), "task-scoped authority must name its task")


def validate_authority_boundary() -> None:
    validate_schema_shape(
        "authority-boundary.schema.json",
        {
            "invariant",
            "current_structural_maintenance_hierarchy",
            "task_scoped_authority",
            "reconciliation_state",
        },
    )
    matrix = load_json("fixtures/authority-boundary-matrix.json")
    require(
        matrix.get("invariant")
        == "high-task-authority-is-not-global-structural-maintenance-authority",
        "authority matrix lost its core invariant",
    )
    expected = [
        (1, "Codex", "codex-chief-architect", "Chief Architect"),
        (2, "Anti-Gravity", "antigravity-chief-facilitator", "Chief Facilitator"),
        (3, "Cursor", "cursor-lead-developer", "Lead Developer"),
    ]
    actual = [
        (item["rank"], item["actor"], item["seat_id"], item["title"])
        for item in matrix["current_structural_maintenance_hierarchy"]
    ]
    require(actual == expected, "current structural-maintenance hierarchy drifted")
    high_task = next(
        item
        for item in matrix["task_scoped_authority"]
        if item["authority_class"] == "high-task-authority"
    )
    forbidden = " ".join(high_task["forbidden_without_separate_elevation"]).lower()
    require("global structural-maintenance" in forbidden, "high-task boundary must forbid global maintenance")


def validate_experiment_matrix() -> None:
    validate_schema_shape(
        "model-interface-affinity-experiment.schema.json",
        {
            "working_testimony",
            "baseline",
            "controlled_invariants",
            "comparison_runs",
            "evidence_policy",
            "retest_policy",
        },
    )
    experiment = load_json("fixtures/recycler-mmao-plus-mao-experiment.json")
    require(
        experiment["working_testimony"] == "Recycler MMAO with Plus MAO",
        "spoken working testimony must remain preserved",
    )
    require(experiment["status"] == "planned", "fixture cannot claim a live experiment ran")
    invariants = experiment["controlled_invariants"]
    baseline = experiment["baseline"]
    require(
        baseline["identity_id"] == invariants["identity_id"],
        "baseline identity must match controlled invariant",
    )
    require(baseline["task_id"] == invariants["task_id"], "baseline task must match controlled invariant")
    required_evidence = set(invariants["evidence_requirements"])
    require(
        {
            "identity",
            "seat",
            "interface",
            "model",
            "repository-state",
            "context-snapshot",
            "tool-trace",
            "verification",
            "independent-review",
        }
        <= required_evidence,
        "experiment evidence requirements are incomplete",
    )
    run_types = {run["comparison_type"] for run in experiment["comparison_runs"]}
    require(
        {"reference", "model-only", "interface-only", "seat-only", "substrate-comparison"}
        <= run_types,
        "experiment matrix is missing a controlled comparison type",
    )
    for run in experiment["comparison_runs"]:
        require(run["identity_id"] == invariants["identity_id"], f"{run['run_id']} changed identity")
        require(run["task_id"] == invariants["task_id"], f"{run['run_id']} changed task")
        require(run["status"] == "planned", f"{run['run_id']} falsely claims execution")
        require(run["actual_behavior"] is None, f"{run['run_id']} has fabricated actual behavior")
        require(run["tool_trace_ref"] is None, f"{run['run_id']} has fabricated trace evidence")
        require(not run["evidence_refs"], f"{run['run_id']} has fabricated evidence")

    run_by_type = {run["comparison_type"]: run for run in experiment["comparison_runs"]}
    require(run_by_type["reference"]["variables_changed"] == [], "reference run cannot change variables")
    require(set(run_by_type["model-only"]["variables_changed"]) == {"model"}, "model-only run changed another variable")
    require(set(run_by_type["interface-only"]["variables_changed"]) == {"interface"}, "interface-only run changed another variable")
    require(set(run_by_type["seat-only"]["variables_changed"]) == {"seat"}, "seat-only run changed another variable")
    require(
        "model" in set(run_by_type["substrate-comparison"]["variables_changed"]),
        "substrate comparison must disclose a model change",
    )
    policy = experiment["evidence_policy"]
    require(policy == {"raw_prompt_capture": False, "independent_review_required": True, "consensus_is_truth": False}, "experiment evidence policy drifted")


def validate_failure_receipt() -> None:
    schema = validate_schema_shape(
        "failure-receipt.schema.json",
        {
            "expected_behavior",
            "actual_behavior",
            "identity",
            "seat",
            "model",
            "interface",
            "repository_state",
            "action_tool_trace",
            "evidence_refs",
            "failure_class",
            "five_whys",
            "correction",
            "retest",
            "rtc_reviews",
            "review_aggregation",
        },
    )
    trace = schema["properties"]["action_tool_trace"]
    require(
        trace["properties"]["capture_mode"].get("const") == "metadata-only",
        "failure trace contract must remain metadata-only",
    )
    receipt = load_json("fixtures/controlled-scope-breach-receipt.json")
    require(receipt["receipt_status"] == "synthetic-fixture", "fixture must not impersonate a real incident")
    require("Synthetic fixture:" in receipt["actual_behavior"], "fixture must disclose its synthetic status")
    require(receipt["action_tool_trace"]["capture_mode"] == "metadata-only", "fixture captured more than metadata")
    why_indexes = [item["index"] for item in receipt["five_whys"]]
    require(why_indexes == [1, 2, 3, 4, 5], "failure receipt must carry exactly ordered Five Whys")
    require(receipt["retest"]["status"] == "not-run", "synthetic receipt cannot claim retest success")
    for review in receipt["rtc_reviews"]:
        require(review["independence"] == "independent-evidence-review", "RTC review lost independence")
        require(review["status"] == "planned", "synthetic fixture cannot claim completed RTC review")
    aggregation = receipt["review_aggregation"]
    require(aggregation["mode"] == "evidence-convergence-not-vote", "RTC became a vote")
    require(aggregation["decision_rule"] == "unsupported-claims-remain-held", "unsupported claims lost HOLD")


def validate_build_spec_and_handoff() -> None:
    spec_path = HERE.parent / "specs" / "mmao-mao-identity-governance-v0.1.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    require(spec["spec_id"] == "kpgs-mmao-mao-identity-governance-v0.1", "build spec ID drifted")
    require(spec["risk_class"] == "R2", "identity-governance POC must retain R2")
    require(spec["lifecycle_state"] == "draft", "unrun experiment cannot leave draft")
    criteria = spec["acceptance_criteria"]
    criterion_ids = [item["id"] for item in criteria]
    require(len(criterion_ids) == len(set(criterion_ids)), "acceptance criterion IDs must be unique")
    planned = {item["criterion_id"] for item in spec["verification_plan"]}
    require(set(criterion_ids) <= planned, "verification plan does not cover every criterion")
    handoff = HERE / "handoffs" / "ANTIGRAVITY_CHIEF_FACILITATOR_2026-08-30.md"
    handoff_text = handoff.read_text(encoding="utf-8")
    for phrase in (
        "no controlled model/interface run has executed",
        "Exact next task to facilitate",
        "Black Beast reconstruction after merge",
    ):
        require(phrase in handoff_text, f"facilitator handoff missing: {phrase}")


def main() -> None:
    validate_identity_contract()
    validate_authority_boundary()
    validate_experiment_matrix()
    validate_failure_receipt()
    validate_build_spec_and_handoff()
    print("KPGS-MMAO-MAO PASS: identity, authority, affinity, failure, and handoff boundaries are structurally coherent.")


if __name__ == "__main__":
    main()
