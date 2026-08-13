"""CCP Economic Consequence Validator (CCP-ECV-01).

A deterministic, dependency-free gate that converts an accepted canonical CCP
receipt plus measured workflow economics into a PKA-compatible disposition.

Invariants:
    CCP_ACCEPTED != PKA_ADMITTED
    PKA_PROPOSE != DOWNSTREAM_EXECUTION_AUTHORITY
    UNKNOWN != FALSE
    PERSIST_RECEIPTS_NOT_RENTER_MEMORY
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import argparse
import hashlib
import json
import math
import sys
from typing import Any, Iterable, Mapping


class Disposition(str, Enum):
    """PKA-compatible outcome for the economic consequence gate."""

    HOLD = "MAYBE_HOLD"
    PROPOSE = "POC_CANDIDATE_PROPOSE"
    BLOCK = "FOC_CANDIDATE_BLOCK"


@dataclass(frozen=True)
class EconomicPolicy:
    """Versioned governance thresholds. Change policy, not hidden model memory."""

    policy_id: str = "ccp-ecv-policy-v1"
    min_measured_cases: int = 30
    min_reliability: float = 0.95
    min_net_value: float = 0.0
    require_evidence_ids: bool = True


@dataclass(frozen=True)
class ConsequenceCase:
    """Observed workflow economics attached to one canonical CCP decision."""

    case_id: str
    caller_repo: str
    ccp_receipt_id: str
    ccp_decision: str
    canonical: bool

    frequency_per_period: float
    manual_cost_per_case: float
    ai_task_fit: float
    reliability: float
    adoption: float
    failure_cost_per_failure: float
    supervision_cost_per_case: float
    compute_cost_per_case: float

    measured_cases: int
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    invariant_ids: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ConsequenceCase":
        data = dict(raw)
        data["evidence_ids"] = tuple(data.get("evidence_ids") or ())
        data["invariant_ids"] = tuple(data.get("invariant_ids") or ())
        return cls(**data)


@dataclass(frozen=True)
class EconomicMetrics:
    manual_baseline_cost: float
    attributable_avoided_manual_cost: float
    expected_failure_cost: float
    supervision_cost: float
    compute_cost: float
    total_ai_operating_cost: float
    net_economic_value: float
    value_per_case: float
    benefit_cost_ratio: float | None


@dataclass(frozen=True)
class ConsequenceReceipt:
    schema: str
    receipt_id: str
    action_id: str
    evaluated_at: str
    policy_id: str
    case_id: str
    caller_repo: str
    ccp_receipt_id: str
    disposition: str
    reasons: tuple[str, ...]
    metrics: EconomicMetrics | None
    evidence_ids: tuple[str, ...]
    invariant_ids: tuple[str, ...]
    evaluation_hash: str
    consequential_execution_authority: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ValidationError(ValueError):
    pass


def _finite_non_negative(name: str, value: float) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValidationError(f"{name} must be numeric")
    if not math.isfinite(float(value)) or float(value) < 0:
        raise ValidationError(f"{name} must be finite and >= 0")


def _ratio(name: str, value: float) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValidationError(f"{name} must be numeric")
    if not math.isfinite(float(value)) or not 0 <= float(value) <= 1:
        raise ValidationError(f"{name} must be between 0 and 1")


def validate_case(case: ConsequenceCase, policy: EconomicPolicy) -> None:
    for name in ("case_id", "caller_repo", "ccp_receipt_id", "ccp_decision"):
        if not str(getattr(case, name)).strip():
            raise ValidationError(f"{name} is required")

    for name in (
        "frequency_per_period",
        "manual_cost_per_case",
        "failure_cost_per_failure",
        "supervision_cost_per_case",
        "compute_cost_per_case",
    ):
        _finite_non_negative(name, getattr(case, name))

    for name in ("ai_task_fit", "reliability", "adoption"):
        _ratio(name, getattr(case, name))

    if not isinstance(case.measured_cases, int) or isinstance(case.measured_cases, bool):
        raise ValidationError("measured_cases must be an integer")
    if case.measured_cases < 0:
        raise ValidationError("measured_cases must be >= 0")

    if policy.min_measured_cases < 0:
        raise ValidationError("policy.min_measured_cases must be >= 0")
    _ratio("policy.min_reliability", policy.min_reliability)
    if not math.isfinite(float(policy.min_net_value)):
        raise ValidationError("policy.min_net_value must be finite")


def compute_metrics(case: ConsequenceCase) -> EconomicMetrics:
    baseline = case.frequency_per_period * case.manual_cost_per_case

    # Only attributable value survives the gate: task fit x reliability x adoption.
    avoided = baseline * case.ai_task_fit * case.reliability * case.adoption

    failure = (
        case.frequency_per_period
        * case.adoption
        * (1.0 - case.reliability)
        * case.failure_cost_per_failure
    )
    supervision = (
        case.frequency_per_period
        * case.adoption
        * case.supervision_cost_per_case
    )
    compute = (
        case.frequency_per_period
        * case.adoption
        * case.compute_cost_per_case
    )
    operating = failure + supervision + compute
    net = avoided - operating
    value_per_case = net / case.frequency_per_period if case.frequency_per_period else 0.0
    bcr = avoided / operating if operating > 0 else None

    return EconomicMetrics(
        manual_baseline_cost=baseline,
        attributable_avoided_manual_cost=avoided,
        expected_failure_cost=failure,
        supervision_cost=supervision,
        compute_cost=compute,
        total_ai_operating_cost=operating,
        net_economic_value=net,
        value_per_case=value_per_case,
        benefit_cost_ratio=bcr,
    )


def _canonical_hash(case: ConsequenceCase, policy: EconomicPolicy) -> str:
    canonical = {
        "case": asdict(case),
        "policy": asdict(policy),
        "invariants": [
            "CCP_ACCEPTED != PKA_ADMITTED",
            "PKA_PROPOSE != DOWNSTREAM_EXECUTION_AUTHORITY",
            "UNKNOWN != FALSE",
        ],
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def evaluate(
    case: ConsequenceCase,
    policy: EconomicPolicy = EconomicPolicy(),
    *,
    evaluated_at: str | None = None,
) -> ConsequenceReceipt:
    validate_case(case, policy)

    reasons: list[str] = []
    disposition = Disposition.HOLD
    metrics: EconomicMetrics | None = None

    if case.ccp_decision != "Accepted" or case.canonical is not True:
        reasons.append("CCP receipt is not Accepted + canonical; PKA economic admission remains HOLD")
    elif policy.require_evidence_ids and not case.evidence_ids:
        reasons.append("No provenance-bearing evidence_ids supplied")
    elif case.measured_cases < policy.min_measured_cases:
        reasons.append(
            f"Measured cases {case.measured_cases} below governed minimum {policy.min_measured_cases}"
        )
    else:
        metrics = compute_metrics(case)
        if case.reliability < policy.min_reliability:
            disposition = Disposition.BLOCK
            reasons.append(
                f"Reliability {case.reliability:.6f} below governed minimum {policy.min_reliability:.6f}"
            )
        elif metrics.net_economic_value <= policy.min_net_value:
            disposition = Disposition.BLOCK
            reasons.append(
                f"Net economic value {metrics.net_economic_value:.6f} does not exceed governed minimum "
                f"{policy.min_net_value:.6f}"
            )
        else:
            disposition = Disposition.PROPOSE
            reasons.append("Governance evidence and measured economics satisfy proposal gate")

    evaluation_hash = _canonical_hash(case, policy)
    return ConsequenceReceipt(
        schema="ccp_economic_consequence_receipt_v1",
        receipt_id=f"ccp-ecv:{evaluation_hash[:16]}",
        action_id=f"ccp-ecv:{case.caller_repo}:{case.ccp_receipt_id}",
        evaluated_at=evaluated_at or datetime.now(timezone.utc).isoformat(),
        policy_id=policy.policy_id,
        case_id=case.case_id,
        caller_repo=case.caller_repo,
        ccp_receipt_id=case.ccp_receipt_id,
        disposition=disposition.value,
        reasons=tuple(reasons),
        metrics=metrics,
        evidence_ids=case.evidence_ids,
        invariant_ids=case.invariant_ids,
        evaluation_hash=evaluation_hash,
        consequential_execution_authority=False,
    )


def _load_json(path: str | None) -> Mapping[str, Any]:
    if path in (None, "-"):
        raw = sys.stdin.read()
    else:
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read()
    loaded = json.loads(raw)
    if not isinstance(loaded, dict):
        raise ValidationError("input JSON must be an object")
    return loaded


def _build_policy(raw: Mapping[str, Any] | None) -> EconomicPolicy:
    return EconomicPolicy(**dict(raw or {}))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate CCP economic consequence evidence")
    parser.add_argument("input", nargs="?", default="-", help="JSON file, or - for stdin")
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        envelope = _load_json(args.input)
        case_raw = envelope.get("case", envelope)
        if not isinstance(case_raw, dict):
            raise ValidationError("case must be an object")
        policy_raw = envelope.get("policy")
        if policy_raw is not None and not isinstance(policy_raw, dict):
            raise ValidationError("policy must be an object")

        receipt = evaluate(ConsequenceCase.from_mapping(case_raw), _build_policy(policy_raw))
    except (ValidationError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": "ccp_economic_consequence_error_v1", "error": str(exc)}))
        return 4

    print(json.dumps(receipt.to_dict(), indent=2, sort_keys=True))
    if receipt.disposition == Disposition.PROPOSE.value:
        return 0
    if receipt.disposition == Disposition.HOLD.value:
        return 2
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
