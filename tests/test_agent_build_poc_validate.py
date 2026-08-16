"""Agent-building PoC integration — governance evidence and CI semantics."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.agent_build_poc_validate import validate_agent_build_poc  # noqa: E402
from kopano.ci_verdict_semantics import classify_agent_build_ci  # noqa: E402


@pytest.mark.integration
def test_agent_build_poc_ci_has_no_internal_blockers() -> None:
    raw = validate_agent_build_poc(write_report=False)
    ci = classify_agent_build_ci(raw)

    assert ci["ci_status"] == "PASS", ci
    assert ci["execution_status"] == "SUCCESS"
    assert ci["blocking_failures"] == []
    assert ci["governance_verdict"] == "POC_VALIDATED"


def test_agent_build_poc_logic_proven_list() -> None:
    report = validate_agent_build_poc(write_report=False)
    proven = report.get("logic_proven") or []
    assert any("Bracket" in x for x in proven)
    assert any("BlackMask" in x for x in proven)
    assert any("Guardian" in x for x in proven)
    assert any("Identi" in x for x in proven)
    assert any("Operating mesh" in x for x in proven)
    assert any("Graduation bar" in x for x in proven)


def test_expected_foc_decline_is_green_ci() -> None:
    report = {
        "verdict": "FAIL",
        "checks": [
            {
                "check": "known_foc_fixture",
                "verdict": "FAIL",
                "governance_verdict": "FOC_DECLINED",
                "expected_governance_verdict": "FOC_DECLINED",
            }
        ],
    }

    ci = classify_agent_build_ci(report)

    assert ci["ci_status"] == "PASS"
    assert ci["execution_status"] == "SUCCESS"
    assert ci["expected_declines"] == ["known_foc_fixture"]
    assert ci["blocking_failures"] == []


def test_external_graduation_evidence_is_held_not_failed() -> None:
    report = {
        "verdict": "FAIL",
        "checks": [
            {
                "check": "graduation_bar_met",
                "verdict": "FAIL",
                "detail": "verified=0/required",
            }
        ],
    }

    ci = classify_agent_build_ci(report)

    assert ci["ci_status"] == "PASS"
    assert ci["evidence_status"] == "HELD_FOR_EXTERNAL_PROOF"
    assert ci["held_external_evidence"] == ["graduation_bar_met"]


def test_boundary_breach_governed_decline_is_green_ci() -> None:
    """A BOUNDARY_BREACH is the LPM-LPH engine enforcing a department contract
    before execution -- a governed decline, not a validator crash."""
    report = {
        "verdict": "FAIL",
        "checks": [
            {
                "check": "identi_flow_handoff",
                "verdict": "FAIL",
                "detail": "BOUNDARY_BREACH",
            },
            {
                "check": "guardian_flow_teacher_kc",
                "verdict": "FAIL",
                "detail": "BOUNDARY_BREACH",
            },
        ],
    }

    ci = classify_agent_build_ci(report)

    assert ci["ci_status"] == "PASS"
    assert ci["expected_declines"] == ["identi_flow_handoff", "guardian_flow_teacher_kc"]
    assert ci["blocking_failures"] == []


def test_optional_dep_missing_and_operating_mesh_hold_are_held_not_failed() -> None:
    """A missing optional runtime dep (mcp.server.fastmcp) and an unseeded
    operating mesh are external-evidence Holds, not CI blockers."""
    report = {
        "verdict": "FAIL",
        "checks": [
            {
                "check": "mao_dispatch",
                "verdict": "FAIL",
                "detail": "No module named 'mcp.server.fastmcp'",
            },
            {
                "check": "operating_mesh_phase3",
                "verdict": "FAIL",
                "detail": "operating=0/10",
            },
        ],
    }

    ci = classify_agent_build_ci(report)

    assert ci["ci_status"] == "PASS"
    assert ci["evidence_status"] == "HELD_FOR_EXTERNAL_PROOF"
    assert ci["held_external_evidence"] == ["mao_dispatch", "operating_mesh_phase3"]
    assert ci["blocking_failures"] == []


def test_real_validator_crash_stays_red() -> None:
    """A genuine internal exception (not a boundary breach, not an optional
    dep) must remain a CI blocker."""
    report = {
        "verdict": "FAIL",
        "checks": [
            {
                "check": "blackmask_drill",
                "verdict": "FAIL",
                "detail": "AttributeError: 'NoneType' object has no attribute 'verdict'",
            }
        ],
    }

    ci = classify_agent_build_ci(report)

    assert ci["ci_status"] == "FAIL"
    assert ci["blocking_failures"] == ["blackmask_drill"]


def test_unexpected_validator_failure_stays_red() -> None:
    report = {
        "verdict": "FAIL",
        "checks": [
            {
                "check": "bracket_lint_self_test",
                "verdict": "FAIL",
                "detail": "validator crashed",
            }
        ],
    }

    ci = classify_agent_build_ci(report)

    assert ci["ci_status"] == "FAIL"
    assert ci["execution_status"] == "ERROR"
    assert ci["blocking_failures"] == ["bracket_lint_self_test"]
    assert ci["exit_code"] == 1
