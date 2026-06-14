"""LD-LPM operate — stress ideas under protocol stack."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.ld_lpm_operate import stress_idea  # noqa: E402
from kopano.steward_lane import steward_lane_kasilink_snapshot  # noqa: E402


def test_stress_idea_bracket_rejects_sacred():
    out = stress_idea(
        idea_id="bad_bracket",
        action="[ONE_WORLD_ORDER] fake",
        evidence="should fail",
        run_blackmask=False,
    )
    assert out["verdict"] == "HOLD"
    assert "bracket_lint_idea" in out["failed_checks"]


def test_stress_idea_canonical_passes_lint():
    out = stress_idea(
        idea_id="good_bracket",
        action="[LPM_PROTOCOL] LD operates as LPM",
        evidence="docs/swarm-ops/LD_LPM_OPERATE.json",
        run_blackmask=False,
    )
    lint = next(c for c in out["checks"] if c["check"] == "bracket_lint_idea")
    assert lint["verdict"] == "PASS"


def test_kasilink_snapshot_shape():
    snap = steward_lane_kasilink_snapshot()
    assert snap["schema"] == "kasilink_steward_lane_v2"
    assert "actors" in snap
    assert "latest_comms" in snap
    assert len(snap["latest_comms"]) >= 1
