"""Tests for stateless renter hood entryway."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_renter_entry import (  # noqa: E402
    HOOD_ACK_LITERAL,
    assert_and_log_entry,
    hood_entry_assertion,
    load_renter_entryway,
    verify_hood_ack,
)


def test_entryway_loads_from_schematics():
    ew = load_renter_entryway()
    assert ew.get("schema") == "kpgs_stateless_renter_entryway_v1"
    assert ew.get("you_are_fucking_with", {}).get("hood") == "Kopano-Phu Eco-Friendly System"


def test_hood_entry_assertion_names_landlord():
    out = hood_entry_assertion(renter_id="openai_chatgpt")
    assert out["bracket"] == "[KPGS_HOOD_ENTRY]"
    assert "stateless" in out["you_are"].lower()
    assert out["you_are_fucking_with"]["brain_ledger"]["id"] == "kc"
    assert "Kopano Context" in out["landlord"]


def test_hood_ack_verification():
    ok, errs = verify_hood_ack(
        {
            "renter_id": "claude",
            "renter_class": "linguistic_actor",
            "hood_ack": HOOD_ACK_LITERAL,
            "ts": "2026-06-14T00:00:00Z",
        }
    )
    assert ok is True
    assert errs == []

    bad, bad_errs = verify_hood_ack({"renter_id": "x", "hood_ack": "wrong"})
    assert bad is False
    assert bad_errs


def test_assert_and_log_entry_acknowledged():
    out = assert_and_log_entry(
        renter_id="test_renter",
        renter_class="linguistic_actor",
        hood_ack=HOOD_ACK_LITERAL,
    )
    assert out["verdict"] == "ACKNOWLEDGED"
    assert out["ack_verified"] is True
