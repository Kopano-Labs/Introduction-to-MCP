"""CMD-03 external swarm lane — no fabricated kimi_ack."""
from __future__ import annotations

import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))



import pytest

from kopano.external_swarm_lane import (
    external_swarm_lane_status,
    kpefs_closure_status,
    validate_evidence_url,
)


@pytest.mark.integration
def test_validate_url_rejects_bypass():
    out = validate_evidence_url("https://example.com/demo-bypass-receipt")
    assert out["valid"] is False


@pytest.mark.integration
def test_validate_url_accepts_https():
    out = validate_evidence_url("https://kimi.example/run/abc123")
    assert out["valid"] is True


@pytest.mark.integration
def test_external_swarm_status_has_guide():
    st = external_swarm_lane_status()
    assert st["commandment"] == "CMD-03"
    assert "cli_template" in st["guide"]


@pytest.mark.integration
def test_closure_internal_complete():
    c = kpefs_closure_status()
    assert c["internal_kpefs_complete"] is True
    assert "external_swarm" in c

@pytest.mark.integration
def test_closure_reports_operating_mesh_hold():
    """Operating-mesh HOLD must mirror the live phase-3 evidence state.

    CI may intentionally seed an ephemeral 10/10 operating mesh before this
    test runs, while a standalone local run may be unseeded.  The semantic
    contract is therefore the relationship between the two fields, not a
    hard-coded assumption that phase 3 is always false.
    """
    c = kpefs_closure_status()
    assert "operating_mesh_held" in c
    assert isinstance(c["operating_mesh_held"], bool)
    phase3_exit_met = bool(c["operating_mesh"]["phase3_exit_met"])
    assert c["operating_mesh_held"] is (not phase3_exit_met)
    # Internal completion honours the CI verdict adapter, not the raw verdict,
    # and is intentionally independent of the external operating-mesh HOLD.
    assert c["internal_kpefs_complete"] is True
