"""
Integration tests for new API endpoints in Kopano Control Plane:
- Governance Traces & Observable Cognition Surface
- Google Drive MCP search & read
- RTC Voice turn processing & seat switching
"""

import pytest
from fastapi.testclient import TestClient
from kopano.api import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_gdrive_db = tmp_path / "test_api_gdrive.db"
    test_voice_db = tmp_path / "test_api_voice.db"
    monkeypatch.setenv("DRIVE_CACHE_DB", str(test_gdrive_db))
    monkeypatch.setenv("RTC_VOICE_DB", str(test_voice_db))
    with TestClient(app) as test_client:
        yield test_client


def test_api_governance_traces_flow(client):
    # 1. Create a trace
    res = client.post("/api/governance-traces", json={
        "speaker_seat": "SEAT_02_CASSEY",
        "question_or_intent": "How do we teach township students the stateless invariant?",
        "which_brain": "LOCAL_MAO_BLACK_BEAST",
        "sources": ["Schematics/24-RTC Learning", "Google Drive: Township Cohort 2026"],
        "validations": ["Zero-FOC Passed", "Invariant Sealed"],
        "why_trust": "Verified in Cassey teaching curriculum on metal.",
        "epistemic_state": "PROVEN"
    })
    assert res.status_code == 200
    data = res.json()
    assert "trace" in data
    assert "visual_card" in data
    assert data["trace"]["speaker_seat"] == "SEAT_02_CASSEY"
    assert "OBSERVABLE COGNITION SURFACE" in data["visual_card"]


def test_api_gdrive_search_flow(client):
    # Pre-cache a document
    from kopano.tools.google_drive_mcp import GoogleDriveMCPTool, DriveDocument
    tool = GoogleDriveMCPTool()
    tool.cache_document(DriveDocument(
        file_id="api_gdoc_001",
        name="Township Hardware Sensor Schematics",
        mime_type="application/pdf",
        content_text="Physical sensor wiring and pinout specs for Black Beast Altar."
    ))

    # Search via API
    res = client.get("/api/gdrive/search?query=Sensor")
    assert res.status_code == 200
    results = res.json()["results"]
    assert len(results) == 1
    assert results[0]["file_id"] == "api_gdoc_001"

    # Read via API
    read_res = client.get("/api/gdrive/read/api_gdoc_001")
    assert read_res.status_code == 200
    assert "wiring and pinout" in read_res.json()["content"]


def test_api_rtc_voice_and_seat_switch(client):
    # Switch seat
    res_switch = client.post("/api/rtc/switch-seat?seat_id=SEAT_01_KC")
    assert res_switch.status_code == 200
    assert res_switch.json()["active_seat"] == "SEAT_01_KC"

    # Post voice turn
    res_turn = client.post("/api/rtc/voice-turn", json={
        "session_id": "test_sess_100",
        "user_input": "Council report on system readiness.",
        "speaker": "MASTER_ROBYN",
        "modality": "text"
    })
    assert res_turn.status_code == 200
    turn_data = res_turn.json()
    assert turn_data["foc_check_passed"] is True
    assert "gemini_live_payload" in turn_data
