"""Tests for KPGS activation gate."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_activation_gate import (  # noqa: E402
    REQUIRED_AGENT_COUNT,
    check_kpgs_activation_gate,
)


def test_activation_gate_structure():
    gate = check_kpgs_activation_gate()
    assert gate["schema"] == "kpgs_activation_gate_v1"
    assert "activation_allowed" in gate
    assert "checks" in gate
    assert gate["required_agents"] == REQUIRED_AGENT_COUNT
    assert len(gate["checks"]) >= 6


def test_activation_gate_allow_when_guild_ship():
    gate = check_kpgs_activation_gate(write_report=False)
    if gate["activation_allowed"]:
        assert gate["verdict"] == "ALLOW"
        assert gate["failed_checks"] == []
        assert gate["checks_passed"] == gate["checks_total"]
    else:
        assert gate["verdict"] == "BLOCK"
        assert len(gate["failed_checks"]) > 0


def test_activation_gate_writes_report(tmp_path, monkeypatch):
    from kopano import kpgs_activation_gate as mod

    report_path = tmp_path / "KPGS_ACTIVATION_GATE.json"
    monkeypatch.setattr(mod, "GATE_REPORT_PATH", report_path)
    gate = check_kpgs_activation_gate(write_report=True)
    assert report_path.is_file()
    assert gate.get("report_path")
