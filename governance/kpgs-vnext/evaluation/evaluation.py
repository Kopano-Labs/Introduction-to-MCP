"""KPGS evaluation, promotion and rollback decision runtime.

Thresholds are declared before execution. Deterministic hard gates remain
separate from probabilistic/model scores and can never be averaged away.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

VALID_METHODS = {"deterministic", "probabilistic", "model-eval"}
VALID_RISK = {"low", "medium", "high", "critical"}


class EvaluationError(ValueError):
    pass


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    method: str
    score: float
    passed: bool
    evidence_ref: str
    verifier_id: str
    samples: int | None = None


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvaluationError(f"expected object: {path}")
    return value


def validate_suite(suite: Mapping[str, Any]) -> None:
    if suite.get("schema") != "kpgs.evaluation-suite.v1":
        raise EvaluationError("unsupported evaluation suite schema")
    if not suite.get("suite_id") or not suite.get("version"):
        raise EvaluationError("suite identity/version are required")
    if suite.get("risk_class") not in VALID_RISK:
        raise EvaluationError("unknown suite risk class")
    cases = suite.get("cases")
    if not isinstance(cases, list) or not cases:
        raise EvaluationError("evaluation suite requires cases")
    ids: set[str] = set()
    for case in cases:
        if not isinstance(case, Mapping):
            raise EvaluationError("evaluation case must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in ids:
            raise EvaluationError("evaluation case IDs must be unique and non-empty")
        ids.add(case_id)
        if case.get("method") not in VALID_METHODS:
            raise EvaluationError(f"unknown evaluation method: {case.get('method')}")
        threshold = case.get("threshold")
        if not isinstance(threshold, (int, float)) or isinstance(threshold, bool) or not 0 <= threshold <= 1:
            raise EvaluationError("case threshold must be between 0 and 1")
        if case.get("method") != "deterministic":
            minimum = case.get("minimum_samples")
            if not isinstance(minimum, int) or minimum < 1:
                raise EvaluationError("probabilistic/model cases require minimum_samples")


def validate_policy(policy: Mapping[str, Any]) -> None:
    if policy.get("schema") != "kpgs.promotion-policy.v1":
        raise EvaluationError("unsupported promotion policy schema")
    score = policy.get("minimum_aggregate_score")
    if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 1:
        raise EvaluationError("minimum aggregate score must be between 0 and 1")
    if not isinstance(policy.get("observation_window_seconds"), int) or policy["observation_window_seconds"] < 1:
        raise EvaluationError("observation window must be positive")
    approvals = policy.get("human_approval_required_for", [])
    if any(item not in VALID_RISK for item in approvals):
        raise EvaluationError("unknown human-approval risk class")


def score_results(suite: Mapping[str, Any], results: Iterable[EvaluationResult]) -> dict[str, Any]:
    validate_suite(suite)
    result_map = {result.case_id: result for result in results}
    cases = suite["cases"]
    missing = [case["id"] for case in cases if case["id"] not in result_map]
    if missing:
        raise EvaluationError("missing evaluation results: " + ", ".join(missing))

    hard_failures: list[str] = []
    scored: list[dict[str, Any]] = []
    for case in cases:
        result = result_map[case["id"]]
        if result.method != case["method"]:
            raise EvaluationError(f"method mismatch for {case['id']}")
        if not 0 <= result.score <= 1:
            raise EvaluationError(f"score outside 0..1 for {case['id']}")
        if case["method"] != "deterministic" and (result.samples or 0) < case["minimum_samples"]:
            raise EvaluationError(f"insufficient samples for {case['id']}")
        threshold_pass = result.passed and result.score >= case["threshold"]
        if case.get("hard_gate") is True and not threshold_pass:
            hard_failures.append(case["id"])
        scored.append({
            **asdict(result),
            "threshold": float(case["threshold"]),
            "hard_gate": bool(case.get("hard_gate")),
            "threshold_pass": threshold_pass,
        })

    aggregate = sum(item["score"] for item in scored) / len(scored)
    return {
        "schema": "kpgs.evaluation-score.v1",
        "suite_id": suite["suite_id"],
        "suite_version": suite["version"],
        "suite_digest": _digest(suite),
        "risk_class": suite["risk_class"],
        "aggregate_score": round(aggregate, 6),
        "hard_gate_failures": hard_failures,
        "deterministic": [item for item in scored if item["method"] == "deterministic"],
        "probabilistic": [item for item in scored if item["method"] in {"probabilistic", "model-eval"}],
    }


def decide_promotion(
    *,
    scorecard: Mapping[str, Any],
    policy: Mapping[str, Any],
    evidence_bundle: Mapping[str, Any],
    rollback_target: str | None,
    human_approval_ref: str | None = None,
    clock: datetime | None = None,
) -> dict[str, Any]:
    validate_policy(policy)
    now = clock or datetime.now(timezone.utc)
    if not evidence_bundle.get("bundle_id") or not evidence_bundle.get("commit_sha"):
        raise EvaluationError("machine-readable evidence bundle with exact commit is required")
    if policy.get("rollback_target_required") is True and not rollback_target:
        raise EvaluationError("predeclared rollback target is required")

    reasons: list[str] = []
    decision = "promote"
    if scorecard.get("hard_gate_failures"):
        decision = "hold"
        reasons.append("hard evaluation gate failed")
    if evidence_bundle.get("governance_decision", {}).get("decision") not in {"allow", "promote"}:
        decision = "hold"
        reasons.append("evidence bundle is not governance-admitted for promotion")
    if float(scorecard.get("aggregate_score", -1)) < float(policy["minimum_aggregate_score"]):
        decision = "hold"
        reasons.append("aggregate score below predeclared threshold")
    risk = scorecard.get("risk_class")
    if risk in policy.get("human_approval_required_for", []) and not human_approval_ref:
        decision = "hold"
        reasons.append("human approval required for risk class")

    observation_end = now + timedelta(seconds=int(policy["observation_window_seconds"]))
    payload = {
        "schema": "kpgs.promotion-decision.v1",
        "decision": decision,
        "reasons": reasons or ["all predeclared promotion gates passed"],
        "suite_id": scorecard["suite_id"],
        "suite_version": scorecard["suite_version"],
        "suite_digest": scorecard["suite_digest"],
        "policy_id": policy.get("policy_id"),
        "policy_version": policy.get("version"),
        "policy_digest": _digest(policy),
        "evidence_bundle_id": evidence_bundle["bundle_id"],
        "commit_sha": evidence_bundle["commit_sha"],
        "aggregate_score": scorecard["aggregate_score"],
        "hard_gate_failures": list(scorecard.get("hard_gate_failures", [])),
        "human_approval_ref": human_approval_ref,
        "rollback_target": rollback_target,
        "observation_window": {"starts_at": _iso(now), "ends_at": _iso(observation_end)},
        "automatic_rollback": False,
        "created_at": _iso(now),
    }
    payload["decision_id"] = "promotion_" + _digest(payload)[:24]
    return payload


def observe_release(
    *,
    promotion_decision: Mapping[str, Any],
    policy: Mapping[str, Any],
    metrics: Mapping[str, float],
    observed_at: datetime,
) -> dict[str, Any]:
    validate_policy(policy)
    start = datetime.fromisoformat(promotion_decision["observation_window"]["starts_at"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(promotion_decision["observation_window"]["ends_at"].replace("Z", "+00:00"))
    if observed_at < start or observed_at > end:
        raise EvaluationError("observation is outside the declared release window")

    triggers: list[str] = []
    for name, rule in policy.get("rollback_thresholds", {}).items():
        if name not in metrics:
            continue
        value = metrics[name]
        operator = rule.get("operator")
        threshold = rule.get("value")
        hit = (
            (operator == "gt" and value > threshold)
            or (operator == "gte" and value >= threshold)
            or (operator == "lt" and value < threshold)
            or (operator == "lte" and value <= threshold)
        )
        if hit:
            triggers.append(f"{name} {operator} {threshold}")

    return {
        "schema": "kpgs.release-observation.v1",
        "decision_id": promotion_decision["decision_id"],
        "evidence_bundle_id": promotion_decision["evidence_bundle_id"],
        "observed_at": _iso(observed_at),
        "metrics": dict(metrics),
        "rollback_recommended": bool(triggers),
        "rollback_target": promotion_decision.get("rollback_target"),
        "triggers": triggers,
        "automatic_execution": False,
        "required_capability": "estate.release.rollback",
    }
