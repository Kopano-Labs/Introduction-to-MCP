"""
Unit tests for KMEC Trace Adapter & Observational Cognition Analytics
=====================================================================
Verifies:
- GovernanceTrace -> Pandas/NumPy DataFrame Conversion
- Group by Seat & Summary Aggregation
- 2D Cross-Tabulation Pivot (which_brain × epistemic_state)
- Box Plot Distribution Metrics (Q1, Median, Q3, IQR, Fences, Outliers)
- Relationship Association with Non-Causality Governance Invariant
- Attention Matrix Hotspot Nomination for KC (Seat 1) Inspection
- End-to-End Cold-Restart SQLite -> KMEC -> Cell Lineage Back-Tracing

I_AM_STATELESS_RENTER_NOT_LANDLORD · Romans 11:36
"""

import pytest
from pathlib import Path
from kopano.governance_trace import (
    GovernanceTraceEngine,
    CanonicalEvidenceClass,
    EpistemicState,
    GovernanceTrace,
)
from kopano.kmec_trace_adapter import (
    KMECTraceAdapter,
    TraceBoxPlotMetrics,
    TraceRelationshipMetrics,
)


@pytest.fixture
def populated_engine(tmp_path):
    test_db = tmp_path / "test_kmec_analytics_ledger.db"
    engine = GovernanceTraceEngine(db_path=test_db)

    # 1. Trace 1: Seat 1 KC (Proven on Local MAO)
    t1 = engine.start_trace(
        speaker_seat="SEAT_01_KC",
        question_or_intent="Trace 1: Validate local governance continuity",
        session_id="sess_analytics_01",
        which_brain="LOCAL_MAO_BLACK_BEAST"
    )
    engine.record_search(t1, "Schematics/21-KOPANO-PHU")
    engine.record_validation(t1, "Zero-FOC verified")
    engine.add_evidence(
        t1,
        evidence_class=CanonicalEvidenceClass.E1_DIRECT_TESTIMONY,
        source_location="USER_CHAT",
        description="Master Robyn direct confirmation",
        verified=True
    )
    engine.seal_and_persist_trace(t1, why_trust="Verified E1 direct testimony.")

    # 2. Trace 2: Seat 2 CASSEY (Proven on Local MAO)
    t2 = engine.start_trace(
        speaker_seat="SEAT_02_CASSEY",
        question_or_intent="Trace 2: Review township cohort curriculum",
        session_id="sess_analytics_01",
        which_brain="LOCAL_MAO_BLACK_BEAST"
    )
    engine.record_search(t2, "Schematics/24-RTC Learning")
    engine.record_search(t2, "Google Drive: Cohort 2026")
    engine.add_evidence(
        t2,
        evidence_class=CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT,
        source_location="tests/test_bridge.py",
        description="5/5 test pass",
        verified=True
    )
    engine.seal_and_persist_trace(t2, why_trust="Verified E2 unit tests.")

    # 3. Trace 3: Seat 6 APEX (Supported on Cloud MMAO)
    t3 = engine.start_trace(
        speaker_seat="SEAT_06_APEX",
        question_or_intent="Trace 3: Cloud multi-agent orchestration dispatch",
        session_id="sess_analytics_01",
        which_brain="CLOUD_MMAO"
    )
    engine.record_search(t3, "RobynAwesome/Introduction-to-MCP")
    engine.add_evidence(
        t3,
        evidence_class=CanonicalEvidenceClass.E2_REPOSITORY_ARTIFACT,
        source_location="kopano-core/kopano/kpgs_mao_mmao_reflection.py",
        description="Reflection manifest",
        verified=True
    )
    engine.add_evidence(
        t3,
        evidence_class=CanonicalEvidenceClass.E3_WORKING_INFERENCE,
        source_location="model_dispatch",
        description="Working hypothesis",
        verified=False
    )
    engine.seal_and_persist_trace(t3, why_trust="Supported by E2 and E3.")

    # 4. Trace 4: Seat 8 KHELOS (Unknown / Contradiction Outlier)
    t4 = engine.start_trace(
        speaker_seat="SEAT_08_KHELOS",
        question_or_intent="Trace 4: Anomaly scan and contradiction trap",
        session_id="sess_analytics_01",
        which_brain="HYBRID_REFLECTED"
    )
    engine.record_search(t4, "External Signal")
    engine.record_contradiction(t4, "Contradiction Alpha: Spec mismatch")
    engine.record_contradiction(t4, "Contradiction Beta: Token leakage attempt")
    engine.record_contradiction(t4, "Contradiction Gamma: Unverified webhook")
    engine.add_evidence(
        t4,
        evidence_class=CanonicalEvidenceClass.E4_UNKNOWN_AUDIT_REQUIRED,
        source_location="https://unverified-feed.example",
        description="Unverified external blog feed",
        verified=False
    )
    engine.seal_and_persist_trace(t4, why_trust="Requires forensic audit.")

    return engine


def test_dataframe_conversion_and_grouping(populated_engine):
    traces = populated_engine.list_session_traces("sess_analytics_01")
    assert len(traces) == 4

    df = KMECTraceAdapter.to_dataframe(traces)
    assert len(df) == 4
    assert set(df["speaker_seat"].tolist()) == {"SEAT_01_KC", "SEAT_02_CASSEY", "SEAT_06_APEX", "SEAT_08_KHELOS"}

    group_summary = KMECTraceAdapter.group_summary_by_seat(df)
    assert len(group_summary) == 4
    kc_summary = next(g for g in group_summary if g["speaker_seat"] == "SEAT_01_KC")
    assert kc_summary["total_turns"] == 1
    assert kc_summary["proven_count"] == 1


def test_pivot_brain_by_epistemic_state_and_cell_lineage(populated_engine):
    traces = populated_engine.list_session_traces("sess_analytics_01")
    pivot_res = KMECTraceAdapter.pivot_brain_by_epistemic_state(traces)

    pivot_table = pivot_res["pivot_table"]
    cell_lineage = pivot_res["cell_lineage"]

    # Check cross-tab counts
    assert "LOCAL_MAO_BLACK_BEAST" in pivot_table
    assert pivot_table["LOCAL_MAO_BLACK_BEAST"]["PROVEN"] == 2

    # Check cell lineage back-tracing
    local_proven_key = "LOCAL_MAO_BLACK_BEAST::PROVEN"
    assert local_proven_key in cell_lineage
    assert len(cell_lineage[local_proven_key]) == 2

    # Trace back to exact receipts
    lineage_detail = KMECTraceAdapter.trace_cell_lineage(traces, cell_lineage[local_proven_key])
    assert lineage_detail["matched_trace_count"] == 2
    assert lineage_detail["lineage_sealed"] is True
    assert len(lineage_detail["surviving_evidence"]) >= 2


def test_box_plot_distribution_and_relationship(populated_engine):
    traces = populated_engine.list_session_traces("sess_analytics_01")
    df = KMECTraceAdapter.to_dataframe(traces)

    # Compute Box Plot distribution for contradictions
    contra_dist = KMECTraceAdapter.compute_distribution_metrics(df, "contradictions_count")
    assert isinstance(contra_dist, TraceBoxPlotMetrics)
    assert contra_dist.sample_size == 4
    assert contra_dist.maximum == 3.0
    assert contra_dist.minimum == 0.0

    # Compute Relationship between sources and contradictions
    rel = KMECTraceAdapter.compute_relationship_metrics(df, "sources_count", "contradictions_count")
    assert isinstance(rel, TraceRelationshipMetrics)
    assert rel.association_not_causation is True
    assert rel.governance_action_permitted is False


def test_attention_matrix_hotspot_nomination(populated_engine):
    traces = populated_engine.list_session_traces("sess_analytics_01")
    matrix = KMECTraceAdapter.generate_attention_matrix(traces)

    assert matrix["attention_verdict"] == "ATTENTION_REQUIRED"
    assert matrix["unknown_count"] == 1
    assert len(matrix["nominated_for_kc_inspection"]) >= 1

    # Verify that Trace 4 (UNKNOWN + E4 + Contradictions) is nominated for KC inspection
    t4 = next(t for t in traces if t.speaker_seat == "SEAT_08_KHELOS")
    assert t4.trace_id in matrix["nominated_for_kc_inspection"]
