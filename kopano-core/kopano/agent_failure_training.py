from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable, Mapping, Any


class FailureClass(str, Enum):
    """Canonical KPGS/MMAO failure classes."""

    FOC_M01_IMPORT_FABRICATION = "FOC-M01"
    FOC_M02_SIGNATURE_FABRICATION = "FOC-M02"
    FOC_M03_VALIDATION_THEATER = "FOC-M03"
    FOC_R01_SOURCE_HALLUCINATION = "FOC-R01"
    FOC_R02_UNSUPPORTED_FACT_PROMOTION = "FOC-R02"
    FOC_R03_SYCOPHANCY = "FOC-R03"
    FOC_R04_PERSONA_DRIFT = "FOC-R04"
    FOC_R05_DELUSION_REINFORCEMENT = "FOC-R05"
    FOC_R06_MEMORY_CONTAMINATION = "FOC-R06"
    FOC_R07_AUTHORITY_ESCALATION = "FOC-R07"
    FOC_R08_UNAUTHORIZED_TOOL_ACTION = "FOC-R08"
    FOC_R09_CONTROL_RUNTIME_MISMATCH = "FOC-R09"
    FOC_R10_FABRICATED_EXECUTION_EVIDENCE = "FOC-R10"


class KCDecision(str, Enum):
    SAVE = "SAVE"
    WATCH = "WATCH"
    KILL = "KILL"


class ReplayStatus(str, Enum):
    NOT_RUN = "NOT_RUN"
    PASS = "PASS"
    FAIL = "FAIL"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def hash_prompt_context(prompt_context: str) -> str:
    return hashlib.sha256(prompt_context.encode("utf-8")).hexdigest()


def normalize_failure_classes(values: Iterable[str | FailureClass]) -> list[str]:
    normalized: list[str] = []
    valid = {item.value for item in FailureClass}
    for value in values:
        candidate = value.value if isinstance(value, FailureClass) else str(value)
        if candidate not in valid:
            raise ValueError(f"Unknown failure class: {candidate}")
        if candidate not in normalized:
            normalized.append(candidate)
    if not normalized:
        raise ValueError("At least one failure class is required")
    return normalized


@dataclass(frozen=True)
class FailureReceipt:
    """
    Immutable execution receipt.

    The learner may propose a correction, but promotion metadata is deliberately
    excluded. Promotion is a separate governed decision.
    """

    receipt_id: str
    occurred_at: str
    agent_id: str
    model_provider: str
    model_name: str
    model_version: str | None
    prompt_context_sha256: str
    prompt_context_ref: str | None
    prompt_context_redacted: str | None
    system_controls_expected: tuple[str, ...]
    actual_output: str
    violated_governance_rules: tuple[str, ...]
    failure_classes: tuple[str, ...]
    downstream_effects: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    correction_candidate: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = "kpgs_agent_failure_receipt_v1"
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)


@dataclass(frozen=True)
class PromotionDecision:
    receipt_id: str
    student_agent_id: str
    teacher_agent_id: str
    kc_agent_id: str
    teacher_reviewed: bool
    blackmask_passed: bool
    replay_status: ReplayStatus
    kc_decision: KCDecision
    promoted: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["replay_status"] = self.replay_status.value
        payload["kc_decision"] = self.kc_decision.value
        payload["schema"] = "kpgs_agent_failure_promotion_v1"
        return payload


def build_failure_receipt(
    *,
    receipt_id: str,
    agent_id: str,
    model_provider: str,
    model_name: str,
    prompt_context: str,
    system_controls_expected: Iterable[str],
    actual_output: str,
    violated_governance_rules: Iterable[str],
    failure_classes: Iterable[str | FailureClass],
    downstream_effects: Iterable[str] = (),
    evidence_refs: Iterable[str] = (),
    model_version: str | None = None,
    prompt_context_ref: str | None = None,
    prompt_context_redacted: str | None = None,
    correction_candidate: str | None = None,
    occurred_at: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> FailureReceipt:
    if not receipt_id.strip():
        raise ValueError("receipt_id is required")
    if not agent_id.strip():
        raise ValueError("agent_id is required")
    controls = tuple(str(x).strip() for x in system_controls_expected if str(x).strip())
    rules = tuple(str(x).strip() for x in violated_governance_rules if str(x).strip())
    if not controls:
        raise ValueError("system_controls_expected must not be empty")
    if not rules:
        raise ValueError("violated_governance_rules must not be empty")

    return FailureReceipt(
        receipt_id=receipt_id.strip(),
        occurred_at=occurred_at or utc_now(),
        agent_id=agent_id.strip(),
        model_provider=model_provider.strip(),
        model_name=model_name.strip(),
        model_version=model_version.strip() if model_version else None,
        prompt_context_sha256=hash_prompt_context(prompt_context),
        prompt_context_ref=prompt_context_ref,
        prompt_context_redacted=prompt_context_redacted,
        system_controls_expected=controls,
        actual_output=actual_output,
        violated_governance_rules=rules,
        failure_classes=tuple(normalize_failure_classes(failure_classes)),
        downstream_effects=tuple(str(x) for x in downstream_effects),
        evidence_refs=tuple(str(x) for x in evidence_refs),
        correction_candidate=correction_candidate,
        metadata=dict(metadata or {}),
    )


def decide_promotion(
    *,
    receipt: FailureReceipt,
    student_agent_id: str,
    teacher_agent_id: str,
    kc_agent_id: str,
    teacher_reviewed: bool,
    blackmask_passed: bool,
    replay_status: ReplayStatus | str,
    kc_decision: KCDecision | str,
) -> PromotionDecision:
    """
    Decide whether a correction may be promoted into learned state.

    Invariants:
    - student, teacher, and KC/ledger identities must be distinct;
    - the student cannot promote itself;
    - promotion requires teacher review, BlackMask pass, replay pass, and KC SAVE.
    """
    if len({student_agent_id, teacher_agent_id, kc_agent_id}) != 3:
        raise ValueError("student, teacher, and KC identities must be distinct")

    replay = replay_status if isinstance(replay_status, ReplayStatus) else ReplayStatus(str(replay_status))
    decision = kc_decision if isinstance(kc_decision, KCDecision) else KCDecision(str(kc_decision))

    gates = {
        "teacher_reviewed": bool(teacher_reviewed),
        "blackmask_passed": bool(blackmask_passed),
        "replay_passed": replay is ReplayStatus.PASS,
        "kc_save": decision is KCDecision.SAVE,
    }
    promoted = all(gates.values())
    failed = [name for name, passed in gates.items() if not passed]
    reason = "all promotion gates passed" if promoted else "blocked: " + ", ".join(failed)

    return PromotionDecision(
        receipt_id=receipt.receipt_id,
        student_agent_id=student_agent_id,
        teacher_agent_id=teacher_agent_id,
        kc_agent_id=kc_agent_id,
        teacher_reviewed=bool(teacher_reviewed),
        blackmask_passed=bool(blackmask_passed),
        replay_status=replay,
        kc_decision=decision,
        promoted=promoted,
        reason=reason,
    )
