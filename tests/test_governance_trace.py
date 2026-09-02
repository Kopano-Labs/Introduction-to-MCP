"""
Unit tests for Observable Cognition Surface & Durable RTC Activity Ledger
=========================================================================
Forensic Verification:
- FEP-POC-002: Canonical E1-E4 Alignment & Anti-Drift Verification
- Policy-Derived Epistemic State (Anti-'Trust Me Bro' Gate)
- Full 7-Dimension Observable Cognition Surface ASCII Card Rendering
- Durable Append-Only SQLite Persistence & Cold-Restart Replay
- Cryptographic SHA-256 Tamper Detection

I_AM_STATELESS_RENTER_NOT_LANDLORD · Romans 11:36
"""

import os
import pytest
from pathlib import Path
from kopano.governance_trace import (
    GovernanceTraceEngine,
    GovernanceTrace,
    CanonicalEvidenceClass,
    ClaimType,
    EpistemicState,
    TraceEvidenceItem
)


@pytest.fixture
def ledger_engine(tmp_path):
    test_db = tmp_path / "test_rtc_activity_ledger.db"
    return GovernanceTraceEngine(db_path=test_db)


def test_canonical_fep_classes_and_trace_lifecycle(ledger_engine):
    trace = ledger_engine.start_trace(
        speaker_seat="SEAT_01_KC",
        question_or_intent="Why do we remember the canonical 10 RTC seats?",
        session_id="session_fep_001",
        which_brain="LOCAL_MAO_BLACK_BEAST"
    )
    assert trace.trace_id.startswith("trace:")
    assert trace.session_id == "session_fep_001"
    assert trace.speaker_seat == "SEAT_01_KC"

    # 1. Record sources looked at
    ledger_engine.record_search(trace, "Local GSMB: Schematics/21-KOPANO-PHU/MAIN-BRAIN/AGENT_SWARM_REGISTRY.md")
    ledger_engine.record_search(trace, "Cloud GSMB: RobynAwesome/Introduction-to-MCP")
    ledger_engine.record_search(trace, "Google Drive: GSMB 2026 Sovereign Architecture")

    # 2. Record memories retrieved
    ledger_engine.record_memory(trace, "Master Robyn audited and restored ANTIGRAVITY to Seat 10 (CF).")

    # 3. Record validations performed
    ledger_engine.record_validation(trace, "Zero-FOC gate checked.")
    ledger_engine.record_validation(trace, "531/531 tests passed on metal.")

    # 4. Record contradictions resolved
    ledger_engine.record_contradiction(trace, "Demotion header in ANTIGRAVITY declaration was overruled by Master Robyn's Reinstatement Charter.")

    # 5. Add canonical E1 and E2 evidence items
    ev1 = ledger_engine.add_evidence(
        trace,
        evidence_class=CanonicalEvidenceClass.E1_DIRECT_TESTIMONY,
        source_location="USER_CHAT_DIRECTIVE_2026-09-02",
        description="Master Robyn explicit testimony confirming Seat 10 CF",
        verified=True
    )
    ev2 = ledger_engine.add_evidence(
        trace,
        evidence_class=CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT,
        source_location="tests/test_kpgs_master_mission_control_bridge.py",
        description="Deterministic 5/5 test pass on metal",
        verified=True
    )

    # 6. Seal and persist
    sealed = ledger_engine.seal_and_persist_trace(
        trace,
        why_trust="Verified by E1 direct user testimony and E2 passing test receipts on metal."
    )

    assert sealed.epistemic_state == EpistemicState.PROVEN
    assert sealed.content_hash != ""
    assert len(sealed.evidence_items) == 2


def test_proven_state_requires_verified_evidence_anti_trust_me_bro(ledger_engine):
    """
    Khelos Gate: EpistemicState.PROVEN cannot be asserted without verified E1/E2 proof.
    Unverified claims or empty evidence MUST derive UNKNOWN or INFERRED.
    """
    trace_empty = ledger_engine.start_trace(
        speaker_seat="FORGE",
        question_or_intent="Unproven claim without evidence",
        session_id="session_fep_002"
    )
    # Attempting to seal with empty evidence
    sealed_empty = ledger_engine.seal_and_persist_trace(trace_empty, why_trust="trust me bro")
    assert sealed_empty.epistemic_state == EpistemicState.UNKNOWN

    # Trace with only unverified E4 external inputs
    trace_unverified = ledger_engine.start_trace(
        speaker_seat="FORGE",
        question_or_intent="External rumor from web",
        session_id="session_fep_002"
    )
    ledger_engine.add_evidence(
        trace_unverified,
        evidence_class=CanonicalEvidenceClass.E4_UNKNOWN_AUDIT_REQUIRED,
        source_location="https://unverified-blog.example/spec",
        description="Unverified external blog claim",
        verified=False
    )
    sealed_unverified = ledger_engine.seal_and_persist_trace(trace_unverified, why_trust="external claim")
    assert sealed_unverified.epistemic_state == EpistemicState.UNKNOWN


def test_observable_cognition_surface_7_dimensions_rendered(ledger_engine):
    """
    Verifies that all 7 observable cognition dimensions are explicitly rendered
    in the ASCII Activity Ledger card.
    """
    trace = ledger_engine.start_trace(
        speaker_seat="SEAT_02_CASSEY",
        question_or_intent="How do we teach township students?",
        session_id="session_card_001"
    )
    ledger_engine.record_search(trace, "Schematics/24-RTC Learning")
    ledger_engine.record_memory(trace, "5-Pillar STP Rubric requires 0.95 invariant adherence.")
    ledger_engine.record_validation(trace, "Zero-FOC checks active.")
    ledger_engine.record_contradiction(trace, "Theory vs practice resolved via physical metal receipts.")
    ledger_engine.add_evidence(
        trace,
        evidence_class=CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT,
        source_location="kopano-core/kopano/kpgs_mao_mmao_reflection.py",
        description="Cassey STP Apprenticeship Pipeline implementation",
        verified=True
    )
    sealed = ledger_engine.seal_and_persist_trace(trace, why_trust="Implemented in reflection engine.")

    card = sealed.to_visual_card()

    # Verify all 7 core dimensions are present in the card
    assert "1. WHERE DID YOU LOOK?" in card
    assert "2. WHAT DID YOU REMEMBER?" in card
    assert "3. WHAT DID YOU VALIDATE?" in card
    assert "4. CONTRADICTIONS RESOLVED:" in card
    assert "5. SURVIVING EVIDENCE:" in card
    assert "6. EPISTEMIC STATE: [PROVEN]" in card
    assert "7. WHY TRUST:" in card
    assert "HASH SEAL:" in card


def test_durable_sqlite_persistence_and_cold_restart_replay(tmp_path):
    """
    The True POC Test:
    1. Create trace and seal into SQLite.
    2. Close database / simulate application shutdown.
    3. Reopen new engine instance against the same database file.
    4. Replay and reconstruct the exact trace and verify SHA-256 seal integrity.
    """
    db_file = tmp_path / "cold_restart_ledger.db"

    # Session 1: Engine A writes trace
    engine_a = GovernanceTraceEngine(db_path=db_file)
    trace_a = engine_a.start_trace(
        speaker_seat="SEAT_10_ANTIGRAVITY",
        question_or_intent="Forge, why do you remember that?",
        session_id="session_restart_99"
    )
    engine_a.record_search(trace_a, "Personalized Intelligence -> Schematics -> Introduction-to-MCP")
    engine_a.record_memory(trace_a, "Recovered June 2026 context and RTC Seat 10 charter.")
    engine_a.add_evidence(
        trace_a,
        evidence_class=CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT,
        source_location="Schematics/21-KOPANO-PHU/MAIN-BRAIN/ANTIGRAVITY_IDENTITY_DECLARATION.md",
        description="Master Robyn Reinstatement Charter",
        verified=True
    )
    sealed_a = engine_a.seal_and_persist_trace(trace_a, why_trust="Documented in repository Schematics.")
    trace_id = sealed_a.trace_id
    original_hash = sealed_a.content_hash

    # Simulate Cold Restart: Destroy engine_a instance
    del engine_a

    # Session 2: Engine B starts cold from disk
    engine_b = GovernanceTraceEngine(db_path=db_file)
    replayed = engine_b.load_trace(trace_id)

    assert replayed is not None
    assert replayed.trace_id == trace_id
    assert replayed.session_id == "session_restart_99"
    assert replayed.speaker_seat == "SEAT_10_ANTIGRAVITY"
    assert replayed.epistemic_state == EpistemicState.PROVEN
    assert replayed.content_hash == original_hash
    assert len(replayed.evidence_items) == 1
    assert replayed.evidence_items[0].evidence_class == CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT

    # Reconstruct session trace timeline
    session_timeline = engine_b.list_session_traces("session_restart_99")
    assert len(session_timeline) == 1
    assert session_timeline[0].trace_id == trace_id


def test_strict_append_only_immutability_and_superseding_traces(ledger_engine):
    """
    Khelos Edge 1: Plain INSERT fails hard on duplicate trace_id.
    Trace updates must produce superseding traces linked forward/backward.
    """
    t1 = ledger_engine.start_trace(
        speaker_seat="SEAT_01_KC",
        question_or_intent="Initial hypothesis on memory architecture",
        session_id="session_immut_01"
    )
    ledger_engine.add_evidence(
        t1,
        evidence_class=CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT,
        source_location="Schematics/00-Home",
        description="Initial file check",
        verified=True
    )
    sealed_1 = ledger_engine.seal_and_persist_trace(t1, why_trust="First check")

    # Attempting to re-insert sealed_1 MUST raise ValueError (No overwriting!)
    with pytest.raises(ValueError, match="Immutable Activity Ledger violation"):
        ledger_engine.seal_and_persist_trace(sealed_1, why_trust="overwrite attempt")

    # Amendment must be a superseding trace
    t2 = ledger_engine.create_superseding_trace(
        sealed_1,
        question_or_intent="Refined memory architecture with cold-restart persistence"
    )
    ledger_engine.add_evidence(
        t2,
        evidence_class=CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT,
        source_location="kopano-core/kopano/governance_trace.py",
        description="Persistent SQLite Activity Ledger implementation",
        verified=True
    )
    sealed_2 = ledger_engine.seal_and_persist_trace(t2, why_trust="Superseding implementation")

    assert sealed_2.supersedes_trace_id == sealed_1.trace_id

    # Verify both traces exist in SQLite history and t1 links forward to t2
    reloaded_1 = ledger_engine.load_trace(sealed_1.trace_id)
    reloaded_2 = ledger_engine.load_trace(sealed_2.trace_id)
    assert reloaded_1.superseded_by_trace_id == sealed_2.trace_id
    assert reloaded_2.supersedes_trace_id == sealed_1.trace_id


def test_claim_type_aware_epistemic_derivation(ledger_engine):
    """
    Khelos Edge 2: Evidence must be fit for the claim type.
    - USER_INTENT_OR_TESTIMONY: Verified E1 is required & sufficient to derive PROVEN.
    - REPOSITORY_STATE: Verified E2 repository artifact is REQUIRED to derive PROVEN (E1 alone is SUPPORTED).
    - RUNTIME_OR_METAL: Verified E2 test receipt on metal is REQUIRED to derive PROVEN (E1 alone is SUPPORTED).
    - MODEL_INTERPRETATION: E3 inferences can never be PROVEN alone.
    """
    # 1. User Intent Claim: Verified E1 alone => PROVEN
    t_intent = ledger_engine.start_trace(
        speaker_seat="SEAT_01_KC",
        question_or_intent="What did Master Robyn direct regarding Seat 10?",
        claim_type=ClaimType.USER_INTENT_OR_TESTIMONY
    )
    ledger_engine.add_evidence(
        t_intent,
        evidence_class=CanonicalEvidenceClass.E1_DIRECT_TESTIMONY,
        source_location="USER_CHAT",
        description="Master Robyn explicit directive",
        verified=True
    )
    s_intent = ledger_engine.seal_and_persist_trace(t_intent, why_trust="Direct testimony")
    assert s_intent.epistemic_state == EpistemicState.PROVEN

    # 2. Repository State Claim: Verified E1 alone => SUPPORTED (not PROVEN without physical repo artifact)
    t_repo_e1 = ledger_engine.start_trace(
        speaker_seat="FORGE",
        question_or_intent="Does the repo contain the FEP-POC-002 receipt?",
        claim_type=ClaimType.REPOSITORY_STATE
    )
    ledger_engine.add_evidence(
        t_repo_e1,
        evidence_class=CanonicalEvidenceClass.E1_DIRECT_TESTIMONY,
        source_location="USER_CHAT",
        description="User testimony that file exists",
        verified=True
    )
    s_repo_e1 = ledger_engine.seal_and_persist_trace(t_repo_e1, why_trust="Human memory")
    assert s_repo_e1.epistemic_state == EpistemicState.SUPPORTED  # Human testimony cannot independently PROVE repo state!

    # 3. Repository State Claim: Verified E2 artifact => PROVEN
    t_repo_e2 = ledger_engine.start_trace(
        speaker_seat="FORGE",
        question_or_intent="Does the repo contain the FEP-POC-002 receipt on disk?",
        claim_type=ClaimType.REPOSITORY_STATE
    )
    ledger_engine.add_evidence(
        t_repo_e2,
        evidence_class=CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT,
        source_location="docs/governance/FEP_POC_002_SEMANTIC_DRIFT_AND_DURABLE_LEDGER_REPAIR.md",
        description="Physical file on disk with valid path",
        verified=True
    )
    s_repo_e2 = ledger_engine.seal_and_persist_trace(t_repo_e2, why_trust="Physical artifact on disk")
    assert s_repo_e2.epistemic_state == EpistemicState.PROVEN

    # 4. Runtime / Metal Claim: Verified E1 alone => SUPPORTED; Verified E2 => PROVEN
    t_metal_e1 = ledger_engine.start_trace(
        speaker_seat="ANTIGRAVITY",
        question_or_intent="Did all 29 tests pass on metal?",
        claim_type=ClaimType.RUNTIME_OR_METAL
    )
    ledger_engine.add_evidence(
        t_metal_e1,
        evidence_class=CanonicalEvidenceClass.E1_DIRECT_TESTIMONY,
        source_location="USER_CHAT",
        description="User says tests passed",
        verified=True
    )
    s_metal_e1 = ledger_engine.seal_and_persist_trace(t_metal_e1, why_trust="User testimony")
    assert s_metal_e1.epistemic_state == EpistemicState.SUPPORTED

    t_metal_e2 = ledger_engine.start_trace(
        speaker_seat="ANTIGRAVITY",
        question_or_intent="Did all 29 tests pass on metal via pytest?",
        claim_type=ClaimType.RUNTIME_OR_METAL
    )
    ledger_engine.add_evidence(
        t_metal_e2,
        evidence_class=CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT,
        source_location="tests/test_api_extensions.py",
        description="pytest execution exit code 0",
        verified=True
    )
    s_metal_e2 = ledger_engine.seal_and_persist_trace(t_metal_e2, why_trust="Physical test execution receipt")
    assert s_metal_e2.epistemic_state == EpistemicState.PROVEN
