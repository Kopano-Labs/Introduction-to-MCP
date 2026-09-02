"""
Unit tests for Observable Cognition Surface & Governance Trace Engine
====================================================================
Verifies:
- Trace creation and lifecycle
- Recording searches, memory, validations, and evidence
- Epistemic state categorization (PROVEN, SUPPORTED, INFERRED, UNKNOWN)
- Visual card rendering for Desktop UI Activity Ledger

I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import pytest
from kopano.governance_trace import (
    GovernanceTraceEngine,
    GovernanceTrace,
    EpistemicState,
    EvidenceItem
)


def test_governance_trace_lifecycle():
    engine = GovernanceTraceEngine()
    trace = engine.start_trace(
        speaker_seat="SEAT_01_KC",
        question_or_intent="Why do we remember the 10-Seat RTC canonical order?",
        which_brain="LOCAL_MAO_BLACK_BEAST"
    )
    assert trace.trace_id.startswith("trace:")
    assert trace.speaker_seat == "SEAT_01_KC"

    # Record search sources
    engine.record_search(trace, "Personalized Intelligence & Vault")
    engine.record_search(trace, "Schematics/21-KOPANO-PHU GOVERNANCE SYSTEMS/MAIN-BRAIN/AGENT_SWARM_REGISTRY.md")
    engine.record_search(trace, "Cloud GSMB: RobynAwesome/Introduction-to-MCP")

    # Record memories & validations
    engine.record_memory(trace, "Master Robyn audited and corrected the 10 RTC seats (KC, CASSEY, CASSIE, KESSA, YASSIE, APEX, THARI, KHELOS, ANCHOR, ANTIGRAVITY).")
    engine.record_validation(trace, "531/531 master suite passed on physical metal.")
    engine.record_validation(trace, "Zero-FOC check confirmed.")

    # Add evidence
    engine.add_evidence(
        trace,
        source_type="METAL_TEST",
        path_or_uri="tests/test_kpgs_master_mission_control_bridge.py",
        description="Deterministic 5/5 unit test pass"
    )
    engine.add_evidence(
        trace,
        source_type="LOCAL_GSMB",
        path_or_uri="Schematics/21-KOPANO-PHU/MAIN-BRAIN/AGENT_SWARM_REGISTRY.md",
        description="Canonical Tier 0 & 10 RTC Seats definition"
    )

    # Seal trace
    sealed = engine.seal_trace(
        trace,
        state=EpistemicState.PROVEN,
        why_trust="Physical test receipts verified on local metal + immutable Schematics registry."
    )

    assert sealed.epistemic_state == EpistemicState.PROVEN
    assert len(sealed.evidence_items) == 2
    assert len(sealed.where_looked) == 3

    # Verify visual card rendering
    card = sealed.to_visual_card()
    assert "OBSERVABLE COGNITION SURFACE — RTC ACTIVITY LEDGER" in card
    assert "SEAT_01_KC" in card
    assert "[PROVEN]" in card
    assert "AGENT_SWARM_REGISTRY.md" in card
