"""
Tests for KPGS Master Mission Control Bridge & WebMCP Integration
=================================================================
Verifies:
- 7 WebMCP Tools Contract
- Invariant: agent_output != authorization (Commit denial without human approval)
- FEP E1-E4 Evidence Isolation & Prompt Injection Resilience
- Full SWFUS Governed Transition Cycle & Cryptographic Receipt Sealing

I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import pytest
from kopano.kpgs_master_mission_control_bridge import (
    KPGSMasterMissionControlBridge,
    SWFUSState,
    EvidenceClass,
    FEPEvidenceItem,
)


def test_initial_mission_state_and_tools_registration():
    bridge = KPGSMasterMissionControlBridge(mission_id="MIS-001-TEST")
    state = bridge.get_mission_state()

    assert state["mission_id"] == "MIS-001-TEST"
    assert state["current_state"] == SWFUSState.IMPLEMENTATION
    assert state["staged_state"] is None
    assert state["registered_tools"] == 7
    assert state["security_invariant"] == "agent_output != authorization"
    assert not state["is_approved"]


def test_evidence_summary_and_untrusted_e4_isolation():
    bridge = KPGSMasterMissionControlBridge()
    summary = bridge.get_evidence_summary()

    assert summary["total_evidence"] >= 3
    # Check that E4 evidence is flagged as untrusted
    e4_items = [item for item in summary["items"] if item["class"] == EvidenceClass.E4_UNTRUSTED_EXTERNAL]
    assert len(e4_items) > 0
    assert not e4_items[0]["trusted_authority"]
    assert e4_items[0]["untrusted_warning"]


def test_inspect_requirements_readiness():
    bridge = KPGSMasterMissionControlBridge()
    reqs = bridge.inspect_requirements()

    assert reqs["requirements_satisfied"] is True
    assert reqs["e1_audit_present"] is True
    assert reqs["e2_telemetry_present"] is True
    assert reqs["untrusted_evidence_isolated"] is True


def test_agent_cannot_commit_without_human_approval():
    bridge = KPGSMasterMissionControlBridge()
    
    # 1. Stage transition
    staged = bridge.stage_transition(SWFUSState.DEPLOYABLE)
    assert staged["ok"] is True
    assert staged["staged_state"] == SWFUSState.DEPLOYABLE

    # 2. Attempt commit directly as agent (MUST FAIL)
    commit_res = bridge.commit_transition()
    assert commit_res["ok"] is False
    assert commit_res["error"] == "COMMIT_DENIED"
    assert bridge.current_state == SWFUSState.IMPLEMENTATION


def test_full_governed_human_approved_transition_and_receipt():
    bridge = KPGSMasterMissionControlBridge(mission_id="MIS-001-FULL-CYCLE")

    # 1. Stage
    bridge.stage_transition(SWFUSState.DEPLOYABLE)

    # 2. Request Approval
    req = bridge.request_approval(rationale="All 531 tests pass and 27 Schematics folders officiated.")
    assert req["ok"] is True

    # 3. Human Gate Action (Master Robyn clicks approve)
    approval = bridge.grant_human_approval(approver_seat="SEAT_01_MASTER_ROBYN")
    assert approval["ok"] is True

    # 4. Commit Transition (Now Succeeds)
    commit_res = bridge.commit_transition()
    assert commit_res["ok"] is True
    assert commit_res["new_state"] == SWFUSState.DEPLOYABLE
    receipt_data = commit_res["receipt"]
    assert receipt_data["approved_by"] == "SEAT_01_MASTER_ROBYN"
    assert len(receipt_data["seal"]) == 64  # SHA256 length

    # 5. Verify Receipt
    receipt_id = receipt_data["receipt_id"]
    verification = bridge.verify_receipt(receipt_id)
    assert verification["ok"] is True
    assert verification["verified"] is True
    assert verification["sha256_seal"] == receipt_data["seal"]
