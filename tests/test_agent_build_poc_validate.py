"""Agent-building PoC integration — Bracket, BlackMask, Guardian/Identi, LPM, KPEFS."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.agent_build_poc_validate import validate_agent_build_poc  # noqa: E402


@pytest.mark.integration
def test_agent_build_poc_all_gates_pass() -> None:
    report = validate_agent_build_poc(write_report=False)
    assert report["verdict"] == "PASS", report.get("failed_checks", report["checks"])
    assert report["passed"] == report["total"]
    assert report["total"] >= 15


def test_agent_build_poc_logic_proven_list() -> None:
    report = validate_agent_build_poc(write_report=False)
    proven = report.get("logic_proven") or []
    assert any("Bracket" in x for x in proven)
    assert any("BlackMask" in x for x in proven)
    assert any("Guardian" in x for x in proven)
    assert any("Identi" in x for x in proven)
    assert any("Operating mesh" in x for x in proven)
    assert any("Graduation bar" in x for x in proven)
