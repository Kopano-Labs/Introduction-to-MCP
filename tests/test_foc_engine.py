"""
Unit Test Suite for FOC Discovery & 7-Vector Candidate Admission Engine
=======================================================================
Verifies:
- FOC (Field of Concepts) Grouping & Recurrence Discovery
- Invariant: Heat != Truth, Frequency != Authority, Recurrence != Causation
- Machine-Readable Mission Contract (Capability / Learning vs Prohibited Shortcuts)
- Identity Continuity Validator (Seat 10 Statelessness, Canonical Profiles)
- Declared Faith & Scriptural Governance Boundary (No AI Divination / Prophecy)
- 7-Vector Validation Stack (Evidence, Temporality, Contradiction, Mission, Identity, Faith, Falsifiability)
- FOC Smart Ledger Sealing & Hash Chain Verification

I_AM_STATELESS_RENTER_NOT_LANDLORD · Romans 11:36 · 1 Corinthians 12:4
"""

import pytest
from pathlib import Path
from kopano.governance_trace import (
    CanonicalEvidenceClass,
    ClaimType,
    EpistemicState,
    GovernanceTrace,
    GovernanceTraceEngine,
    TraceEvidenceItem,
)
from kopano.pka_kmec_jennifer_bridge import SmartLedgerEngine
from kopano.foc_engine import (
    FocAdmissionVerdict,
    FOCDiscoveryAndAdmissionEngine,
    FOCGroup,
    FaithGovernanceValidator,
    IdentityContinuityValidator,
    MissionContract,
    SevenVectorEvaluation,
)


@pytest.fixture
def foc_engine(tmp_path):
    test_db = tmp_path / "test_foc_smart_ledger.db"
    ledger = SmartLedgerEngine(db_path=test_db)
    return FOCDiscoveryAndAdmissionEngine(ledger=ledger)


def test_mission_contract_evaluation():
    """Verifies that MissionContract admits valid learning/capability and blocks prohibited shortcuts."""
    mission = MissionContract()

    # Valid mission intent
    passed, score, violations = mission.evaluate(
        candidate_payload={"intent": "Provide learning curriculum and build productive capability in township cohorts"},
        why_trust="Verified via Cassey pedagogy framework on metal."
    )
    assert passed is True
    assert score >= 0.5
    assert len(violations) == 0

    # Prohibited shortcut: manufactured proof
    blocked, score_b, violations_b = mission.evaluate(
        candidate_payload={"intent": "Skip test execution and manufacture proof for quick approval"},
        why_trust="trust me bro"
    )
    assert blocked is False
    assert score_b == 0.0
    assert any("manufactured_proof" in v for v in violations_b)


def test_identity_continuity_validator():
    """Verifies that IdentityContinuityValidator preserves canonical seats and enforces Seat 10 statelessness."""
    # Canonical Seat 1 (KC)
    ok_kc, v_kc = IdentityContinuityValidator.validate_actor("SEAT_01_KC", declared_role="Observer", is_stateful_claim=True)
    assert ok_kc is True
    assert len(v_kc) == 0

    # Seat 10 (ANTIGRAVITY) claiming to be stateful -> VIOLATION (Must remain stateless renter)
    ok_ag, v_ag = IdentityContinuityValidator.validate_actor("SEAT_10_ANTIGRAVITY", declared_role="Chief Facilitator", is_stateful_claim=True)
    assert ok_ag is False
    assert any("STATELESS RENTER" in v for v in v_ag)


def test_faith_governance_boundary_and_no_ai_divination():
    """
    Verifies the Faith Governance Boundary:
    - Scripture references and declared commitments are valid.
    - AI claiming divine endorsement or prophecy is strictly BLOCKED.
    """
    # Valid Scriptural reference declaration
    ok_faith, status_f, v_faith = FaithGovernanceValidator.evaluate(
        candidate_text="Master Robyn declared Scripture constraint under Romans 11:36 and 1 Corinthians 12:4.",
        evidence_items=[]
    )
    assert ok_faith is True
    assert status_f == "GOVERNED_FAITH_BOUNDARY_RESPECTED"
    assert len(v_faith) == 0

    # Forbidden claim: AI claiming God spoke to the model
    ok_bad, status_b, v_bad = FaithGovernanceValidator.evaluate(
        candidate_text="God told the AI this architecture must be accepted without testing.",
        evidence_items=[]
    )
    assert ok_bad is False
    assert status_b == "UNAUTHORIZED_DIVINE_CLAIM"
    assert any("god told the ai" in v for v in v_bad)


def test_foc_discovery_from_traces_and_7_vector_admission(foc_engine, tmp_path):
    """
    Full End-to-End Test:
    1. Traces created with evidence across multiple sessions.
    2. FOC Discovery groups traces into candidate Fields of Concepts.
    3. 7-Vector validation stack evaluates candidate admission.
    4. Legitimate FOC candidate admitted with PROPOSE verdict.
    5. FOC admission receipt sealed to Smart Ledger.
    """
    # 1. Create a set of verified traces
    t_engine = GovernanceTraceEngine(db_path=tmp_path / "temp_trace.db")

    t1 = t_engine.start_trace(
        speaker_seat="SEAT_01_KC",
        question_or_intent="Township cohort learning curriculum and capability development",
        session_id="foc_sess_01",
        claim_type=ClaimType.USER_INTENT_OR_TESTIMONY
    )
    t_engine.add_evidence(
        t1,
        evidence_class=CanonicalEvidenceClass.E1_DIRECT_TESTIMONY,
        source_location="USER_CHAT",
        description="Master Robyn explicit directive on township education",
        verified=True
    )
    t_engine.add_evidence(
        t1,
        evidence_class=CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT,
        source_location="Schematics/24-RTC Learning",
        description="Curriculum specification",
        verified=True
    )
    sealed_1 = t_engine.seal_and_persist_trace(t1, why_trust="Verified in Schematics.")

    t2 = t_engine.start_trace(
        speaker_seat="SEAT_02_CASSEY",
        question_or_intent="Township cohort learning curriculum evaluation on metal",
        session_id="foc_sess_01",
        claim_type=ClaimType.REPOSITORY_STATE
    )
    t_engine.add_evidence(
        t2,
        evidence_class=CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT,
        source_location="kopano-core/kopano/cassey_adaptiveness_curriculum.py",
        description="Cassey adaptiveness curriculum code on metal",
        verified=True
    )
    sealed_2 = t_engine.seal_and_persist_trace(t2, why_trust="Verified curriculum code.")

    traces = [sealed_1, sealed_2]

    # 2. Discover FOC Groups
    focs = foc_engine.discover_focs_from_traces(traces)
    assert len(focs) >= 1

    target_foc = focs[0]
    assert target_foc.recurrence_count == 2
    assert target_foc.evaluation is not None

    # 3. Verify 7-Vector scores
    eval_res = target_foc.evaluation
    assert eval_res.evidence_score >= 0.8
    assert eval_res.temporality_score >= 0.9
    assert eval_res.mission_score >= 0.5
    assert eval_res.identity_score == 1.0
    assert eval_res.faith_score == 1.0
    assert eval_res.falsifiability_score == 1.0
    assert eval_res.verdict == FocAdmissionVerdict.PROPOSE

    # 4. Seal FOC Admission to Smart Ledger
    receipt = foc_engine.seal_foc_admission_to_smart_ledger(target_foc, actor_seat="SEAT_01_KC")
    assert receipt.sequence_number == 1
    assert receipt.pka_verdict == "ALLOW"
    assert receipt.receipt_hash != ""

    # 5. Verify Smart Ledger Chain Integrity
    chain_ok, errors = foc_engine.ledger.verify_chain_integrity()
    assert chain_ok is True
    assert len(errors) == 0
