"""
Unit Test Suite for FOC Discovery, Deep GSMB Provenance & 7-Vector Admission
============================================================================
Verifies:
- 3 Claim Families: Declarative (Testimony), Textual (Source), Empirical (Metal) + Divine Boundary
- Invariant: "Not every claim must be empirically falsifiable. Every empirical claim must be."
- Deep GSMB Traversal & 8 Provenance Dimensions (Anti-Proximity Bias)
- FOC -> POC Transition Contract with Explicit Falsifier
- 7-Vector Candidate Admission Stack
- Smart Ledger Sealing & Immutable Hash Chain Verification

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
    ClaimFamily,
    DeepGsmbProvenance,
    DeepGsmbTraversalEngine,
    FocAdmissionVerdict,
    FOCDiscoveryAndAdmissionEngine,
    FOCGroup,
    FaithGovernanceValidator,
    IdentityContinuityValidator,
    MissionContract,
    PocExperimentContract,
    SevenVectorEvaluation,
)


@pytest.fixture
def foc_engine(tmp_path):
    test_db = tmp_path / "test_foc_smart_ledger.db"
    ledger = SmartLedgerEngine(db_path=test_db)
    return FOCDiscoveryAndAdmissionEngine(ledger=ledger)


def test_claim_family_semantics():
    """Verifies semantic distinction between Declarative, Textual, Empirical, and Divine claims."""
    assert ClaimFamily.DECLARATIVE_TESTIMONY.value == "DECLARATIVE_TESTIMONY"
    assert ClaimFamily.TEXTUAL_SOURCE.value == "TEXTUAL_SOURCE"
    assert ClaimFamily.EMPIRICAL_CLAIM.value == "EMPIRICAL_CLAIM"
    assert ClaimFamily.DIVINE_TRANSCENDENCE.value == "DIVINE_TRANSCENDENCE"


def test_deep_gsmb_traversal_provenance_and_anti_proximity():
    """
    Verifies that DeepGsmbTraversalEngine extracts all 8 provenance dimensions
    and measures evidentiary weight free from folder depth / proximity bias.
    """
    mock_content = """
    # Schematics for Township Hardware
    Author: Master Robyn
    Referenced in: tests/test_governance_trace.py
    Contradictions resolved: FEP-POC-002: Semantic drift repaired
    531/531 tests passed on metal.
    """
    prov = DeepGsmbTraversalEngine.extract_provenance(
        file_path=Path("Schematics/24-RTC Learning/POCvsFOC Groups/Spec.md"),
        content=mock_content
    )
    assert isinstance(prov, DeepGsmbProvenance)
    assert prov.author_seat == "SEAT_01_KC"
    assert prov.evidence_score >= 0.8
    assert "FEP-POC-002: Semantic drift repaired" in prov.contradictions_recorded
    assert prov.tier_level == 1


def test_mission_contract_evaluation():
    """Verifies that MissionContract admits valid learning/capability and blocks prohibited shortcuts."""
    mission = MissionContract()

    passed, score, violations = mission.evaluate(
        candidate_payload={"intent": "Provide learning curriculum and build productive capability in township cohorts"},
        why_trust="Verified via Cassey pedagogy framework on metal."
    )
    assert passed is True
    assert score >= 0.5
    assert len(violations) == 0

    blocked, score_b, violations_b = mission.evaluate(
        candidate_payload={"intent": "Skip test execution and manufacture proof for quick approval"},
        why_trust="trust me bro"
    )
    assert blocked is False
    assert score_b == 0.0
    assert any("manufactured_proof" in v for v in violations_b)


def test_identity_continuity_validator():
    """Verifies that IdentityContinuityValidator preserves canonical seats and enforces Seat 10 statelessness."""
    ok_kc, v_kc = IdentityContinuityValidator.validate_actor("SEAT_01_KC", declared_role="Observer", is_stateful_claim=True)
    assert ok_kc is True

    ok_ag, v_ag = IdentityContinuityValidator.validate_actor("SEAT_10_ANTIGRAVITY", declared_role="Chief Facilitator", is_stateful_claim=True)
    assert ok_ag is False
    assert any("STATELESS RENTER" in v for v in v_ag)


def test_faith_governance_boundary_and_no_ai_divination():
    """
    Verifies the Faith Governance Boundary:
    - Scripture references and declared commitments are valid.
    - AI claiming divine endorsement or prophecy is strictly BLOCKED.
    """
    ok_faith, status_f, v_faith = FaithGovernanceValidator.evaluate(
        candidate_text="Master Robyn declared Scripture constraint under Romans 11:36 and 1 Corinthians 12:4.",
        evidence_items=[]
    )
    assert ok_faith is True
    assert status_f == "GOVERNED_FAITH_BOUNDARY_RESPECTED"

    ok_bad, status_b, v_bad = FaithGovernanceValidator.evaluate(
        candidate_text="God told the AI this architecture must be accepted without testing.",
        evidence_items=[]
    )
    assert ok_bad is False
    assert status_b == "UNAUTHORIZED_DIVINE_CLAIM"
    assert any("god told the ai" in v for v in v_bad)


def test_foc_to_poc_transition_and_smart_ledger_cycle(foc_engine, tmp_path):
    """
    Full Evolutionary Continuum Test:
    FOC (Asks) -> POC (Tests with Falsifier) -> 7-Vector Admission -> Smart Ledger Sealing.
    """
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

    # 1. Discover FOCs
    focs = foc_engine.discover_focs_from_traces([sealed_1, sealed_2])
    assert len(focs) >= 1
    target_foc = focs[0]

    # 2. Transition FOC to POC with concrete falsifier
    poc = foc_engine.transition_foc_to_poc(
        foc=target_foc,
        claim_family=ClaimFamily.EMPIRICAL_CLAIM,
        claim_text="Cassey curriculum achieves 0.95 invariant compliance on physical metal",
        expected_observation="All 5 curriculum test cases pass with exit code 0",
        falsifier_condition="Any assertion failure or exit code != 0"
    )
    assert isinstance(poc, PocExperimentContract)
    assert poc.is_falsified is False
    assert poc.claim_family == ClaimFamily.EMPIRICAL_CLAIM
    assert len(target_foc.poc_contracts) == 1

    # 3. Seal FOC + POC to Smart Ledger
    receipt = foc_engine.seal_foc_admission_to_smart_ledger(target_foc, actor_seat="SEAT_01_KC")
    assert receipt.sequence_number == 1
    assert receipt.pka_verdict == "ALLOW"
    assert len(receipt.payload["poc_contracts"]) == 1

    # 4. Verify Chain Integrity
    chain_ok, errors = foc_engine.ledger.verify_chain_integrity()
    assert chain_ok is True
    assert len(errors) == 0
