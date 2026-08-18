"""Executable KPGS evidence bundles and governance scorecards.

One canonical evidence bundle feeds both engineering and everyday governance
views. Hard policy/security gates are evaluated separately from aggregate
scores and can never be averaged away.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Callable, Iterable, Mapping

DECISIONS = {"allow", "deny", "promote", "rollback", "hold"}
TRACE_LAYERS = {
    "pwa",
    "adapter",
    "sovereign-hub",
    "renter",
    "skill",
    "verifier",
    "deployment",
}
REQUIRED_USER_TRACE_LAYERS = {
    "pwa",
    "adapter",
    "sovereign-hub",
    "renter",
    "skill",
    "verifier",
}
ARTIFACT_KINDS = {
    "specification",
    "policy-decision",
    "capability-lease",
    "execution",
    "verification",
    "security",
    "performance",
    "accessibility",
    "deployment",
    "rollback",
    "user-outcome",
}
PROMOTION_ARTIFACT_KINDS = {
    "specification",
    "policy-decision",
    "capability-lease",
    "execution",
    "verification",
    "security",
    "accessibility",
    "deployment",
    "user-outcome",
}
METRIC_NAMES = {
    "latency",
    "realtime-health",
    "cost",
    "usage",
    "reliability",
    "error-rate",
    "recovery-rate",
    "task-completion",
    "task-abandonment",
    "accessibility",
    "mobile",
}
PROMOTION_METRICS = {
    "latency",
    "realtime-health",
    "reliability",
    "error-rate",
    "task-completion",
    "task-abandonment",
    "accessibility",
    "mobile",
}
FORBIDDEN_METADATA_KEYS = {
    "authorization",
    "password",
    "passwd",
    "secret",
    "token",
    "credential",
    "credentials",
    "cookie",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
}
SECRET_VALUE_PATTERNS = (
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}", re.IGNORECASE),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{12,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)


class EvidenceError(Exception):
    pass


class EvidenceCorrelationError(EvidenceError):
    pass


class HardGateFailure(EvidenceError):
    pass


def _iso8601(value: datetime) -> str:
    normalized = value.astimezone(timezone.utc).replace(microsecond=0)
    return normalized.isoformat().replace("+00:00", "Z")


def _parse_time(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError(f"{field_name} is required")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceError(f"{field_name} is invalid") from exc
    if parsed.tzinfo is None:
        raise EvidenceError(f"{field_name} must include timezone")
    return _iso8601(parsed)


def _require_ref(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError(f"{field_name} is required")
    cleaned = value.strip()
    if "://" not in cleaned:
        raise EvidenceError(f"{field_name} must be a governed reference")
    return cleaned


def _assert_secret_safe(value: Any, path: str = "evidence") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized_key = str(key).strip().casefold().replace("-", "_")
            if normalized_key in FORBIDDEN_METADATA_KEYS:
                raise EvidenceError(f"secret-bearing field forbidden at {path}.{key}")
            _assert_secret_safe(child, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_secret_safe(child, f"{path}[{index}]")
        return
    if isinstance(value, str):
        for pattern in SECRET_VALUE_PATTERNS:
            if pattern.search(value):
                raise EvidenceError(f"secret-like material forbidden at {path}")


def _commit_sha(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-fA-F0-9]{40}", value):
        raise EvidenceCorrelationError("exact 40-character release commit SHA is required")
    return value.lower()


def hard_gate_failures(bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        deepcopy(item)
        for item in bundle.get("verifications", [])
        if isinstance(item, Mapping)
        and item.get("hard_gate") is True
        and item.get("passed") is False
    ]


class EvidenceBundleBuilder:
    """Build one canonical, secret-safe correlation bundle."""

    def __init__(
        self,
        *,
        estate_property: str,
        release_ref: str,
        commit_sha: str,
        adapter: Mapping[str, str],
        renter: Mapping[str, str],
        skills: Iterable[Mapping[str, str]],
        task_id: str,
        session_id: str,
        correlation_id: str,
        governing_spec_ref: str,
        retention_policy_ref: str,
        redaction_policy_ref: str,
        clock: Callable[[], datetime] | None = None,
    ):
        for label, value in {
            "estate_property": estate_property,
            "release_ref": release_ref,
            "task_id": task_id,
            "session_id": session_id,
            "correlation_id": correlation_id,
        }.items():
            if not isinstance(value, str) or not value.strip():
                raise EvidenceCorrelationError(f"{label} is required")
        if "." not in estate_property:
            raise EvidenceCorrelationError("estate_property must be a DNS property")

        adapter_copy = deepcopy(dict(adapter))
        renter_copy = deepcopy(dict(renter))
        skill_list = [deepcopy(dict(item)) for item in skills]
        if not adapter_copy.get("implementation") or not adapter_copy.get("version"):
            raise EvidenceCorrelationError("adapter implementation/version are required")
        if not renter_copy.get("renter_id") or not renter_copy.get("protocol_version"):
            raise EvidenceCorrelationError("renter identity/protocol are required")
        if not skill_list or any(not item.get("name") or not item.get("version") for item in skill_list):
            raise EvidenceCorrelationError("at least one named/versioned skill is required")

        _assert_secret_safe(adapter_copy, "adapter")
        _assert_secret_safe(renter_copy, "renter")
        _assert_secret_safe(skill_list, "skills")

        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._base = {
            "created_at": _iso8601(self._clock()),
            "estate_property": estate_property.strip(),
            "release_ref": release_ref.strip(),
            "commit_sha": _commit_sha(commit_sha),
            "adapter": adapter_copy,
            "renter": renter_copy,
            "skills": skill_list,
            "task_id": task_id.strip(),
            "session_id": session_id.strip(),
            "correlation_id": correlation_id.strip(),
            "governing_spec_ref": _require_ref(governing_spec_ref, "governing_spec_ref"),
            "capability_lease_refs": [],
            "trace_hops": [],
            "artifacts": [],
            "verifications": [],
            "metrics": [],
            "aggregate_scores": {},
            "retention_policy_ref": _require_ref(retention_policy_ref, "retention_policy_ref"),
            "redaction_policy_ref": _require_ref(redaction_policy_ref, "redaction_policy_ref"),
        }

    def add_capability_lease_ref(self, ref: str) -> "EvidenceBundleBuilder":
        cleaned = _require_ref(ref, "capability_lease_ref")
        if cleaned not in self._base["capability_lease_refs"]:
            self._base["capability_lease_refs"].append(cleaned)
        return self

    def add_trace_hop(
        self,
        *,
        layer: str,
        ref: str,
        status: str,
        at: str,
        duration_ms: float | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "EvidenceBundleBuilder":
        if layer not in TRACE_LAYERS:
            raise EvidenceCorrelationError("unknown trace layer")
        if status not in {
            "started",
            "succeeded",
            "failed",
            "blocked",
            "recovered",
            "abandoned",
        }:
            raise EvidenceCorrelationError("unknown trace status")
        if not isinstance(ref, str) or not ref.strip():
            raise EvidenceCorrelationError("trace ref is required")
        if duration_ms is not None and duration_ms < 0:
            raise EvidenceCorrelationError("trace duration cannot be negative")
        metadata_copy = deepcopy(dict(metadata or {}))
        _assert_secret_safe(metadata_copy, f"trace.{layer}.metadata")
        self._base["trace_hops"].append(
            {
                "layer": layer,
                "ref": ref.strip(),
                "status": status,
                "at": _parse_time(at, "trace.at"),
                "duration_ms": duration_ms,
                "metadata": metadata_copy,
            }
        )
        return self

    def add_artifact(
        self,
        *,
        kind: str,
        ref: str,
        sha256: str | None = None,
    ) -> "EvidenceBundleBuilder":
        if kind not in ARTIFACT_KINDS:
            raise EvidenceError("unknown evidence artifact kind")
        if not isinstance(ref, str) or not ref.strip():
            raise EvidenceError("artifact ref is required")
        if sha256 is not None and not re.fullmatch(r"[a-fA-F0-9]{64}", sha256):
            raise EvidenceError("artifact sha256 must contain 64 hex characters")
        _assert_secret_safe(ref, f"artifact.{kind}.ref")
        self._base["artifacts"].append(
            {
                "kind": kind,
                "ref": ref.strip(),
                "sha256": sha256.lower() if sha256 else None,
            }
        )
        return self

    def add_verification(
        self,
        *,
        verifier_id: str,
        criterion_id: str,
        method: str,
        hard_gate: bool,
        passed: bool,
        evidence_ref: str,
        score: float | None = None,
    ) -> "EvidenceBundleBuilder":
        if method not in {
            "unit",
            "integration",
            "e2e",
            "schema",
            "security",
            "performance",
            "accessibility",
            "human-review",
            "model-eval",
        }:
            raise EvidenceError("unknown verification method")
        if not verifier_id.strip() or not criterion_id.strip() or not evidence_ref.strip():
            raise EvidenceError("verification identity, criterion and evidence are required")
        self._base["verifications"].append(
            {
                "verifier_id": verifier_id.strip(),
                "criterion_id": criterion_id.strip(),
                "method": method,
                "hard_gate": bool(hard_gate),
                "passed": bool(passed),
                "score": score,
                "evidence_ref": evidence_ref.strip(),
            }
        )
        return self

    def add_metric(
        self,
        *,
        name: str,
        value: float | str | bool,
        evidence_ref: str,
        unit: str | None = None,
    ) -> "EvidenceBundleBuilder":
        if name not in METRIC_NAMES:
            raise EvidenceError("unknown metric name")
        if not isinstance(value, (int, float, str, bool)):
            raise EvidenceError("metric value must be scalar")
        if not evidence_ref.strip():
            raise EvidenceError("metric evidence ref is required")
        self._base["metrics"].append(
            {
                "name": name,
                "value": value,
                "unit": unit,
                "evidence_ref": evidence_ref.strip(),
            }
        )
        return self

    def set_aggregate_score(self, dimension: str, score: float) -> "EvidenceBundleBuilder":
        if not isinstance(dimension, str) or not dimension.strip():
            raise EvidenceError("aggregate score dimension is required")
        if not isinstance(score, (int, float)):
            raise EvidenceError("aggregate score must be numeric")
        self._base["aggregate_scores"][dimension.strip()] = float(score)
        return self

    def _validate_correlation(self) -> None:
        if not self._base["capability_lease_refs"]:
            raise EvidenceCorrelationError("capability lease correlation is required")
        if not self._base["verifications"]:
            raise EvidenceCorrelationError("at least one verifier result is required")
        layers = {item["layer"] for item in self._base["trace_hops"]}
        missing = REQUIRED_USER_TRACE_LAYERS - layers
        if missing:
            raise EvidenceCorrelationError(
                "user-task trace is missing layers: " + ", ".join(sorted(missing))
            )
        verifier_ids = {item["verifier_id"] for item in self._base["verifications"]}
        trace_verifiers = {
            item["ref"]
            for item in self._base["trace_hops"]
            if item["layer"] == "verifier"
        }
        if verifier_ids.isdisjoint(trace_verifiers):
            raise EvidenceCorrelationError("verifier trace does not match verifier evidence")

    def _validate_promotion_evidence(self) -> None:
        kinds = {item["kind"] for item in self._base["artifacts"]}
        missing_artifacts = PROMOTION_ARTIFACT_KINDS - kinds
        if missing_artifacts:
            raise EvidenceCorrelationError(
                "promotion evidence missing artifact kinds: "
                + ", ".join(sorted(missing_artifacts))
            )
        metric_names = {item["name"] for item in self._base["metrics"]}
        missing_metrics = PROMOTION_METRICS - metric_names
        if missing_metrics:
            raise EvidenceCorrelationError(
                "promotion evidence missing metric classes: "
                + ", ".join(sorted(missing_metrics))
            )
        if not any(item["layer"] == "deployment" for item in self._base["trace_hops"]):
            raise EvidenceCorrelationError("promotion requires deployment trace hop")

    def finalize(
        self,
        *,
        decision: str,
        reason: str,
        decision_ref: str | None = None,
        next_action: str | None = None,
    ) -> dict[str, Any]:
        if decision not in DECISIONS:
            raise EvidenceError("unknown governance decision")
        if not isinstance(reason, str) or not reason.strip():
            raise EvidenceError("governance decision reason is required")
        self._validate_correlation()
        failures = hard_gate_failures(self._base)
        if failures and decision in {"allow", "promote"}:
            criteria = ", ".join(item["criterion_id"] for item in failures)
            raise HardGateFailure(
                f"{decision} forbidden while hard gates fail: {criteria}"
            )
        if decision == "promote":
            self._validate_promotion_evidence()

        bundle = deepcopy(self._base)
        bundle["governance_decision"] = {
            "decision": decision,
            "reason": reason.strip(),
            "decided_at": _iso8601(self._clock()),
            "decision_ref": decision_ref,
            "next_action": next_action,
        }
        _assert_secret_safe(bundle)
        digest_input = json.dumps(
            bundle,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        bundle["bundle_id"] = (
            "evidence_"
            + hashlib.sha256(digest_input.encode("utf-8")).hexdigest()[:24]
        )
        return bundle


def engineering_scorecard(bundle: Mapping[str, Any]) -> dict[str, Any]:
    failures = hard_gate_failures(bundle)
    return {
        "schema": "kpgs.engineering-scorecard.v1",
        "bundle_id": bundle["bundle_id"],
        "estate_property": bundle["estate_property"],
        "release_ref": bundle["release_ref"],
        "commit_sha": bundle["commit_sha"],
        "correlation_id": bundle["correlation_id"],
        "hard_gate_failures": failures,
        "hard_gate_clear": not failures,
        "verifications": deepcopy(bundle.get("verifications", [])),
        "metrics": deepcopy(bundle.get("metrics", [])),
        "aggregate_scores": deepcopy(bundle.get("aggregate_scores", {})),
        "trace_hops": deepcopy(bundle.get("trace_hops", [])),
        "artifacts": deepcopy(bundle.get("artifacts", [])),
        "governance_decision": deepcopy(bundle["governance_decision"]),
        "retention_policy_ref": bundle["retention_policy_ref"],
        "redaction_policy_ref": bundle["redaction_policy_ref"],
    }


def everyday_scorecard(bundle: Mapping[str, Any]) -> dict[str, Any]:
    failures = hard_gate_failures(bundle)
    decision = bundle["governance_decision"]
    decision_name = decision["decision"]
    if failures:
        health = "blocked"
        risk = "high"
    elif decision_name in {"deny", "hold", "rollback"}:
        health = "attention"
        risk = "elevated"
    elif decision_name == "promote":
        health = "ready"
        risk = "governed"
    else:
        health = "active"
        risk = "governed"

    failure_text = [item["criterion_id"] for item in failures]
    next_action = decision.get("next_action")
    if not next_action:
        if failures:
            next_action = "Resolve failed hard gates before promotion or privileged continuation."
        elif decision_name == "rollback":
            next_action = "Execute the recorded rollback procedure and re-verify the release."
        elif decision_name == "hold":
            next_action = "Gather the missing evidence and request another governance decision."
        else:
            next_action = "Continue governed observation."

    return {
        "schema": "kpgs.everyday-governance-scorecard.v1",
        "bundle_id": bundle["bundle_id"],
        "property": bundle["estate_property"],
        "status": health,
        "risk": risk,
        "what_changed": (
            f"Release {bundle['release_ref']} at commit {bundle['commit_sha'][:12]}."
        ),
        "decision": decision_name,
        "why": decision["reason"],
        "hard_gate_failures": failure_text,
        "next_action": next_action,
        "correlation_id": bundle["correlation_id"],
    }


def rollback_recommendation(
    bundle: Mapping[str, Any],
    metric_thresholds: Mapping[str, Mapping[str, float | str]] | None = None,
) -> dict[str, Any]:
    """Derive a rollback signal without silently performing rollback.

    Hard-gate failure always triggers a recommendation. Optional numeric metric
    thresholds may add reasons. The caller/Sovereign Hub still needs an exact
    rollback capability lease and recorded rollback target to execute it.
    """

    reasons = [
        f"hard gate failed: {item['criterion_id']}"
        for item in hard_gate_failures(bundle)
    ]
    thresholds = metric_thresholds or {}
    for metric in bundle.get("metrics", []):
        rule = thresholds.get(metric.get("name"))
        value = metric.get("value")
        if not rule or not isinstance(value, (int, float)) or isinstance(value, bool):
            continue
        operator = rule.get("operator")
        threshold = rule.get("value")
        if not isinstance(threshold, (int, float)):
            raise EvidenceError("metric threshold value must be numeric")
        triggered = (
            operator == "gt" and value > threshold
        ) or (
            operator == "gte" and value >= threshold
        ) or (
            operator == "lt" and value < threshold
        ) or (
            operator == "lte" and value <= threshold
        )
        if operator not in {"gt", "gte", "lt", "lte"}:
            raise EvidenceError("unknown metric threshold operator")
        if triggered:
            reasons.append(
                f"metric {metric['name']} {operator} threshold {threshold}"
            )

    return {
        "schema": "kpgs.rollback-recommendation.v1",
        "bundle_id": bundle["bundle_id"],
        "triggered": bool(reasons),
        "reasons": reasons,
        "automatic_execution": False,
        "required_capability": "estate.release.rollback",
        "correlation_id": bundle["correlation_id"],
    }
