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
    test_ledger_db = tmp_path / "test_api_ledger.db"
    test_smart_ledger_db = tmp_path / "test_api_smart_ledger.db"
    monkeypatch.setenv("DRIVE_CACHE_DB", str(test_gdrive_db))
    monkeypatch.setenv("RTC_VOICE_DB", str(test_voice_db))
    monkeypatch.setenv("RTC_ACTIVITY_LEDGER_DB", str(test_ledger_db))
    monkeypatch.setenv("SMART_LEDGER_DB", str(test_smart_ledger_db))
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


def test_api_trace_analytics_and_cell_lineage(client):
    # 1. Post a trace with specific session
    client.post("/api/governance-traces", json={
        "speaker_seat": "SEAT_01_KC",
        "question_or_intent": "Validate analytics pipeline",
        "session_id": "api_test_sess_01",
        "which_brain": "LOCAL_MAO_BLACK_BEAST",
        "sources": ["Schematics/21-KOPANO-PHU"],
        "validations": ["Zero-FOC Passed"],
        "why_trust": "Verified on metal"
    })

    # 2. Query trace analytics
    res_analytics = client.get("/api/governance-traces/analytics?session_id=api_test_sess_01")
    assert res_analytics.status_code == 200
    adata = res_analytics.json()
    assert adata["total_traces"] >= 1
    assert "group_summary_by_seat" in adata
    assert "pivot_brain_by_state" in adata
    assert "attention_matrix" in adata

    # 3. Query cell lineage for the trace
    trace_id = adata["group_summary_by_seat"][0]["speaker_seat"]
    res_lineage = client.post("/api/governance-traces/cell-lineage?session_id=api_test_sess_01", json=[
        adata["pivot_brain_by_state"]["cell_lineage"]["LOCAL_MAO_BLACK_BEAST::PROVEN"][0]
    ])
    assert res_lineage.status_code == 200
    ldata = res_lineage.json()
    assert ldata["matched_trace_count"] == 1
    assert ldata["lineage_sealed"] is True


def test_api_observability_html_dashboard(client):
    res = client.get("/observability?session_id=api_test_sess_01")
    assert res.status_code == 200
    assert "Observable Cognition Surface" in res.text
    assert "KMEC Dataset Engine" in res.text
    assert "cell-interactive" in res.text


def test_api_smart_ledger_and_reconciliation_flow(client):
    # 1. Append receipt via API
    res_append = client.post("/api/smart-ledger/append", json={
        "actor_seat": "SEAT_01_KC",
        "embodiment": "Apple_CryptoKit_SecureEnclave",
        "pka_verdict": "ALLOW",
        "claim_type": "USER_INTENT_OR_TESTIMONY",
        "idempotency_key": "api_idemp_001",
        "payload": {"directive": "Execute cross-repo governance"},
        "evidence_refs": ["USER_CHAT"]
    })
    assert res_append.status_code == 200
    r_data = res_append.json()
    assert r_data["status"] == "SUCCESS"
    assert r_data["receipt"]["sequence_number"] == 1

    # 2. Get chain
    res_chain = client.get("/api/smart-ledger/chain")
    assert res_chain.status_code == 200
    c_data = res_chain.json()
    assert c_data["total_receipts"] == 1
    assert c_data["chain_valid"] is True

    # 3. Check integrity
    res_integ = client.get("/api/smart-ledger/integrity")
    assert res_integ.status_code == 200
    assert res_integ.json()["chain_valid"] is True

    # 4. Reconcile offline batch
    res_reconcile = client.post("/api/smart-ledger/reconcile-offline", json={
        "candidate_envelopes": [
            {
                "idempotency_key": "api_off_001",
                "actor_seat": "SEAT_10_ANTIGRAVITY",
                "embodiment": "Android_Keystore_WorkManager",
                "claim_type": "RUNTIME_OR_METAL",
                "payload": {"tests": "all green"},
                "evidence_refs": ["tests/test_api_extensions.py"],
                "pka_verdict": "ALLOW"
            }
        ]
    })
    assert res_reconcile.status_code == 200
    rec_data = res_reconcile.json()
    assert rec_data["admitted_count"] == 1
    assert rec_data["chain_valid"] is True


def test_api_foc_discovery_and_sealing_flow(client):
    # 1. Post a trace with intent
    client.post("/api/governance-traces", json={
        "speaker_seat": "SEAT_01_KC",
        "question_or_intent": "Township capability and curriculum synthesis",
        "session_id": "api_foc_sess_01",
        "which_brain": "LOCAL_MAO_BLACK_BEAST",
        "sources": ["Schematics/24-RTC Learning"],
        "validations": ["Zero-FOC Checked"],
        "why_trust": "Verified in Schematics"
    })

    # 2. Discover FOCs for session
    res_foc = client.get("/api/foc/groups?session_id=api_foc_sess_01")
    assert res_foc.status_code == 200
    foc_data = res_foc.json()
    assert foc_data["total_foc_groups"] >= 1

    foc_id = foc_data["foc_groups"][0]["foc_id"]

    # 3. Seal FOC Admission to Smart Ledger
    res_seal = client.post("/api/foc/seal", json={
        "foc_id": foc_id,
        "actor_seat": "SEAT_01_KC"
    })
    assert res_seal.status_code == 200
    assert res_seal.json()["status"] == "SUCCESS"
    assert res_seal.json()["receipt"]["pka_verdict"] in ["ALLOW", "HOLD"]


def test_api_kc_my_boy_consumer_and_mascot_endpoints(client):
    # 1. Test KC Chat (General)
    res_chat1 = client.post("/api/kc/chat", json={"message": "Hey KC, what are we building today?"})
    assert res_chat1.status_code == 200
    d1 = res_chat1.json()
    assert d1["mascot"] == "KC"
    assert d1["slogan"] == "KC My Boy"
    assert "KC here, my boy!" in d1["reply"]
    assert d1["mascot_state"] == "listening"

    # 2. Test KC Chat (Work query)
    res_chat2 = client.post("/api/kc/chat", json={"message": "I need a job in the township"})
    assert res_chat2.status_code == 200
    d2 = res_chat2.json()
    assert "Vanguard C" in d2["reply"]
    assert d2["mascot_state"] == "celebrating"

    # 3. Test Mascot State Endpoint
    res_mascot = client.get("/api/kc/mascot-state")
    assert res_mascot.status_code == 200
    m_data = res_mascot.json()
    assert m_data["mascot_name"] == "KC"
    assert m_data["animation"]["halo_pulse"] is True
    assert m_data["color_palette"]["electric_cyan"] == "#00F0FF"

    # 4. Test Ecosystem Summary Endpoint
    res_summary = client.get("/api/kc/summary")
    assert res_summary.status_code == 200
    s_data = res_summary.json()
    assert s_data["master_brand"] == "Kopano Labs"
    assert len(s_data["ecosystem_lanes"]) >= 3
    assert any(lane["name"] == "Cars4Mars" for lane in s_data["ecosystem_lanes"])


def test_api_rtc_council_identities_endpoints(client):
    # 1. Test Get All 12 Canonical RTC Seats
    res = client.get("/api/rtc/council")
    assert res.status_code == 200
    data = res.json()
    assert data["total_seats"] == 12
    assert data["status"] == "RATIFIED & SEALED"
    seats = data["seats"]
    assert len(seats) == 12

    # Check Seat 0 (Master Robyn) and Seat 1 (KC)
    seat0 = next(s for s in seats if s["seat"] == 0)
    assert seat0["name"] == "MASTER ROBYN"
    assert "Sovereign" in seat0["title"]

    seat1 = next(s for s in seats if s["seat"] == 1)
    assert seat1["name"] == "KC"
    assert "Companion" in seat1["title"]

    # 2. Test Get Specific Seat by ID
    res_thari = client.get("/api/rtc/seat/7")
    assert res_thari.status_code == 200
    thari_data = res_thari.json()
    assert thari_data["name"] == "THARI"
    assert thari_data["emoji"] == "🧵"
    assert "CrisisConnect" in thari_data["department"]

    # 3. Test Invalid Seat ID
    res_invalid = client.get("/api/rtc/seat/99")
    assert res_invalid.status_code == 404


def test_api_kopano_assertion_engine(client):
    # 1. Test KC Chat with specific RTC Identity and receipt emission
    res_chat = client.post("/api/kc/chat", json={
        "message": "Verify battery telematics on rover",
        "rtc_identity": "SYSTEM_TELEMETRY",
        "user_id": "c4m_pilot_01"
    })
    assert res_chat.status_code == 200
    d = res_chat.json()
    assert "assert_receipt" in d
    receipt = d["assert_receipt"]
    assert receipt["assert_id"].startswith("AST-")
    assert receipt["rtc_identity"] == "SYSTEM_TELEMETRY"
    assert receipt["intent_domain"] == "CARS4MARS_HARDWARE"
    assert receipt["residency"] == "ZA-CPT (South Africa North)"
    assert receipt["status"] == "VERIFIED_ON_LEDGER"
    assert len(receipt["proof_hash"]) == 64

    # 2. Test Get Assertion by ID
    assert_id = receipt["assert_id"]
    res_get = client.get(f"/api/kc/assert/{assert_id}")
    assert res_get.status_code == 200
    get_d = res_get.json()
    assert get_d["status"] == "VERIFIED"
    assert get_d["assert"]["assert_id"] == assert_id

    # 3. Test Manual Assertion Emission
    res_create = client.post("/api/kc/assert/create", json={
        "session_id": "apprentice_sess_99",
        "rtc_identity": "APPRENTICE",
        "intent_domain": "SOVEREIGN_LEARNING",
        "claim": "Verified Rust module graduation on physical metal"
    })
    assert res_create.status_code == 200
    created = res_create.json()
    assert created["status"] == "EMITTED"
    assert created["assert"]["rtc_identity"] == "APPRENTICE"

    # 4. Test List Assertions
    res_list = client.get("/api/kc/asserts")
    assert res_list.status_code == 200
    list_d = res_list.json()
    assert list_d["total_asserts"] >= 2
    assert list_d["residency_region"] == "ZA-CPT (South Africa North)"
