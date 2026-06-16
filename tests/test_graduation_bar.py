"""Phase 5 graduation bar — verified production vs operating mesh."""
from __future__ import annotations

import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))



import pytest

from kopano.graduation_bar import (
    graduation_bar_status,
    graduation_claim_allowed,
    record_steward_trust,
)


@pytest.mark.integration
def test_graduation_status_shape():
    st = graduation_bar_status()
    assert "verified_production" in st
    assert st["operating_is_not_graduation"] is True
    assert st["public_graduation_bar"] >= 10


@pytest.mark.integration
def test_rejects_graduation_from_operating_alone():
    out = graduation_claim_allowed(claim="we graduated from operating mesh alone")
    assert out["allowed"] is False
    assert out["reasons"]


@pytest.mark.integration
def test_steward_trust_receipt():
    row = record_steward_trust(note="pytest steward trust")
    assert row.get("stored") is True
    assert "kpefs_steward_trust" in row.get("kind", "") or row.get("kind") == "kpefs_steward_trust"