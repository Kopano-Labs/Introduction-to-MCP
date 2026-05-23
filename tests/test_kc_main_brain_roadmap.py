"""Tests for Main Brain roadmap gate."""

from __future__ import annotations

import json
from pathlib import Path

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from kc_main_brain_roadmap import check_entry_gate, load_roadmap  # noqa: E402


def test_roadmap_loads() -> None:
    roadmap = load_roadmap()
    assert roadmap["schema"] == "main_brain_roadmap_v1"
    assert roadmap["cassy"]["lead_student"] is True


def test_entry_gate_passes_on_repo_log() -> None:
    ok, msg = check_entry_gate()
    assert ok, msg


def test_swarm_agents_registry() -> None:
    reg = json.loads(
        (REPO_ROOT / "docs/swarm-ops/agents/SWARM_AGENTS.json").read_text(encoding="utf-8")
    )
    cassy = next(a for a in reg["agents"] if a["id"] == "cassy")
    assert cassy["apprenticeship"]["active"] is True
    mesh = [a for a in reg["agents"] if a["id"] == "claude"][0]
    assert mesh["apprenticeship"]["student"] == "cassy"
