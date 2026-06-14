"""Tests for Kopano Sovereign SIM smoke PoC."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_activation_gate import check_kpgs_activation_gate  # noqa: E402
from kopano.sovereign_sim import (  # noqa: E402
    bootstrap_sovereign_sim,
    run_kpgs_smoke_poc,
    sovereign_sim_status,
    sovereign_sim_ui_snapshot,
)


def test_ui_snapshot_triad():
    ui = sovereign_sim_ui_snapshot()
    assert ui["schema"] == "sovereign_sim_ui_v1"
    assert "triad" in ui
    assert ui["triad"]["kc"]["mode"] == "Save|Watch"
    assert ui["kopano_context"]["host"] == "https://context.kopanolabs.com"


def test_bootstrap_blocked_when_gate_blocks(monkeypatch):
    monkeypatch.setattr(
        "kopano.kpgs_activation_gate.check_kpgs_activation_gate",
        lambda **kw: {"activation_allowed": False, "verdict": "BLOCK", "message": "test block"},
    )
    result = bootstrap_sovereign_sim(write_log=False)
    assert result["verdict"] == "BLOCKED"
    assert result["activation_allowed"] is False


def test_bootstrap_when_gate_allows(monkeypatch, tmp_path):
    from kopano import sovereign_sim as mod

    world_path = tmp_path / "sovereign_sim_world.json"
    monkeypatch.setattr(mod, "WORLD_STATE_PATH", world_path)

    gate = check_kpgs_activation_gate()
    if not gate.get("activation_allowed"):
        result = bootstrap_sovereign_sim(write_log=False)
        assert result["verdict"] == "BLOCKED"
        return

    result = bootstrap_sovereign_sim(write_log=False)
    assert result["verdict"] == "BOOTSTRAPPED"
    assert world_path.is_file()
    world = json.loads(world_path.read_text(encoding="utf-8"))
    assert world.get("bootstrapped") is True
    assert world.get("agent_total") == 300


def test_smoke_poc_pipeline(monkeypatch, tmp_path):
    from kopano import sovereign_sim as mod

    smoke_path = tmp_path / "KPGS_SMOKE_POC_VALIDATION.json"
    world_path = tmp_path / "sovereign_sim_world.json"
    monkeypatch.setattr(mod, "SMOKE_REPORT_PATH", smoke_path)
    monkeypatch.setattr(mod, "WORLD_STATE_PATH", world_path)
    monkeypatch.setattr(mod, "MAIN_BRAIN_LOG", tmp_path / "log.jsonl")

    gate = check_kpgs_activation_gate()
    report = run_kpgs_smoke_poc()
    assert report["schema"] == "kpgs_smoke_poc_v2"
    assert smoke_path.is_file()

    if gate.get("activation_allowed"):
        assert report["verdict"] in ("PASS", "HOLD")
        assert report["activation_allowed"] is True
        assert "ui_snapshot" in report
        assert any(s.get("step") == "behavioral_poc" for s in report.get("steps", []))
    else:
        assert report["verdict"] == "BLOCKED"


def test_sovereign_sim_status():
    status = sovereign_sim_status()
    assert status["schema"] == "sovereign_sim_status_v1"
    assert "gate_verdict" in status
    assert "ui" in status
