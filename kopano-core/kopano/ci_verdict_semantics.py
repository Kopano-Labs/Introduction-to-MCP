"""CI adapter for KPGS governance receipts.

The governance layer classifies concepts; CI classifies execution.  A governed
FOC decline, or an evidence state that is intentionally held outside the PoC
scope, must not be confused with a validator crash.

Invariant:
    GOVERNANCE_VERDICT != CI_EXECUTION_STATUS
"""

from __future__ import annotations

from typing import Any, Mapping

# These checks describe evidence that is intentionally outside the internal
# Agent Build PoC.  Their absence is a governed HOLD, not proof that the
# internal validator failed to execute.
NON_BLOCKING_EXTERNAL_EVIDENCE = frozenset({"graduation_bar_met"})


def _check_name(check: Mapping[str, Any]) -> str:
    return str(check.get("check") or "unknown_check")


def _is_pass(check: Mapping[str, Any]) -> bool:
    return str(check.get("verdict") or "").upper() == "PASS"


def _is_expected_decline(check: Mapping[str, Any]) -> bool:
    """Return True when a governance decline is the expected test outcome.

    This is intentionally opt-in.  A negative result only becomes a green CI
    receipt when the check declares the same expected governance verdict.
    """

    actual = str(check.get("governance_verdict") or "").upper()
    expected = str(check.get("expected_governance_verdict") or "").upper()
    return bool(actual) and actual == expected and actual in {
        "FOC",
        "FOC_DECLINED",
        "FOC_SEALED",
        "HELD",
        "HELD_FOR_REVIEW",
        "HELD_SEALED",
    }


def classify_agent_build_ci(report: Mapping[str, Any]) -> dict[str, Any]:
    """Translate an Agent Build governance report into CI process semantics.

    The raw report is preserved.  This adapter only decides whether CI should
    be green or red for the *execution contract*.
    """

    checks = list(report.get("checks") or [])
    blocking_failures: list[str] = []
    expected_declines: list[str] = []
    held_external_evidence: list[str] = []

    for raw_check in checks:
        if not isinstance(raw_check, Mapping):
            blocking_failures.append("malformed_check")
            continue

        name = _check_name(raw_check)
        if _is_pass(raw_check):
            continue
        if _is_expected_decline(raw_check):
            expected_declines.append(name)
            continue
        if name in NON_BLOCKING_EXTERNAL_EVIDENCE:
            held_external_evidence.append(name)
            continue
        blocking_failures.append(name)

    ci_status = "PASS" if not blocking_failures else "FAIL"
    execution_status = "SUCCESS" if ci_status == "PASS" else "ERROR"
    evidence_status = (
        "HELD_FOR_EXTERNAL_PROOF" if held_external_evidence else "COMPLETE"
    )

    # A green internal PoC receipt does not claim production graduation.  The
    # external-evidence HOLD remains explicit in the receipt.
    governance_verdict = "POC_VALIDATED" if ci_status == "PASS" else "UNRESOLVED"

    return {
        "schema": "kpgs_ci_verdict_semantics_v1",
        "invariant": "GOVERNANCE_VERDICT != CI_EXECUTION_STATUS",
        "raw_verdict": report.get("verdict", "UNKNOWN"),
        "governance_verdict": governance_verdict,
        "execution_status": execution_status,
        "ci_status": ci_status,
        "evidence_status": evidence_status,
        "blocking_failures": blocking_failures,
        "expected_declines": expected_declines,
        "held_external_evidence": held_external_evidence,
        "exit_code": 0 if ci_status == "PASS" else 1,
    }
