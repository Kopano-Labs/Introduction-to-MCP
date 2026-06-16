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