from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "governance" / "kpgs-vnext" / "adaptive-progressive-updates"


def test_portable_fixture_matches_canonical_wire_shape():
    schema = json.loads((CONTRACT_DIR / "swfus-update.schema.json").read_text(encoding="utf-8"))
    fixture = json.loads((CONTRACT_DIR / "example.swfus-update.json").read_text(encoding="utf-8"))

    assert schema["properties"]["schema"]["const"] == "kpgs.swfus.update.v1"
    assert fixture["schema"] == "kpgs.swfus.update.v1"
    assert fixture["action"] in schema["properties"]["action"]["enum"]
    assert fixture["nodeId"]
    assert isinstance(fixture["data"], dict)
    assert -100 <= fixture["telemetryValue"] <= 100
    assert fixture["expectedRevision"] >= 0


def test_receipt_wire_contract_separates_acceptance_from_sync_state():
    schema = json.loads((CONTRACT_DIR / "swfus-update.schema.json").read_text(encoding="utf-8"))
    receipt = schema["$defs"]["receipt"]

    assert "accepted" in receipt["required"]
    assert "syncState" in receipt["required"]
    assert set(receipt["properties"]["syncState"]["enum"]) == {
        "synced",
        "pending_sync",
        "severed",
    }
