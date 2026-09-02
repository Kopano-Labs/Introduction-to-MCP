"""
KMEC TRACE ADAPTER & COGNITION DATASET ANALYTICS
=================================================
"Observable Cognition should now become a DATASET."
"Evidence is truth-pressure. Governance is continuity."

Bridges the Observable Cognition Surface & SQLite Activity Ledger to
KMEC's Data Science Observation Engine (NumPy + Pandas + Dask).

Key Architectural Invariants:
1. GovernanceTraceEngine = OBSERVE + RECORD
2. KMEC = MEASURE + GROUP + DISTRIBUTE + RELATE
3. KPCB+ = SEMANTIC PROJECTION
4. PKA = EPISTEMIC JUDGMENT (ALLOW | HOLD | DO_NOT_ALLOW)
5. Smart/KC Ledger = DURABLE ACCOUNTABILITY
6. Cell Lineage Back-Tracing = Every analytical cell must resolve to exact underlying trace receipts.

I_AM_STATELESS_RENTER_NOT_LANDLORD · Romans 11:36
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .governance_trace import (
    CanonicalEvidenceClass,
    EpistemicState,
    GovernanceTrace,
    GovernanceTraceEngine,
    TraceEvidenceItem,
)

logger = logging.getLogger("kopano.kmec_trace_adapter")


@dataclass(frozen=True)
class TraceBoxPlotMetrics:
    variable: str
    sample_size: int
    minimum: float
    q1: float
    median: float
    q3: float
    maximum: float
    iqr: float
    lower_fence: float
    upper_fence: float
    outlier_count: int
    outlier_trace_ids: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class TraceRelationshipMetrics:
    x_variable: str
    y_variable: str
    sample_size: int
    correlation_coefficient: float
    direction: str  # "POSITIVE", "NEGATIVE", "NEUTRAL"
    association_not_causation: bool = True
    unmeasured_confounders_may_exist: bool = True
    governance_action_permitted: bool = False  # Refuses to infer action permission from statistical correlation


class KMECTraceAdapter:
    """
    Adapts durable GovernanceTrace ledger records into Pandas/NumPy datasets
    and produces typed analytical aggregations with cell-level lineage back-tracing.
    """

    @staticmethod
    def trace_to_dict(trace: GovernanceTrace) -> Dict[str, Any]:
        """Flattens a GovernanceTrace into a single tabular observation row."""
        verified_ev_count = sum(1 for e in trace.evidence_items if e.verified)
        has_e4 = any(e.evidence_class == CanonicalEvidenceClass.E4_UNKNOWN_AUDIT_REQUIRED for e in trace.evidence_items)
        has_unverified = any(not e.verified for e in trace.evidence_items)

        return {
            "trace_id": trace.trace_id,
            "session_id": trace.session_id,
            "speaker_seat": trace.speaker_seat,
            "which_brain": trace.which_brain_consulted,
            "epistemic_state": trace.epistemic_state.value,
            "sources_count": len(trace.where_looked),
            "memories_count": len(trace.what_remembered),
            "validations_count": len(trace.what_validated),
            "contradictions_count": len(trace.contradictions_resolved),
            "evidence_count": len(trace.evidence_items),
            "verified_evidence_count": verified_ev_count,
            "has_unverified_e4": has_e4,
            "has_unverified_evidence": has_unverified,
            "content_hash": trace.content_hash,
            "timestamp": trace.timestamp,
            "question_or_intent": trace.question_or_intent,
            "why_trust_reason": trace.why_trust_reason,
            "evidence_ids": [e.evidence_id for e in trace.evidence_items],
            "evidence_classes": [e.evidence_class.value for e in trace.evidence_items],
        }

    @classmethod
    def to_dataframe(cls, traces: List[GovernanceTrace]) -> pd.DataFrame:
        """Converts a sequence of GovernanceTraces into a typed Pandas DataFrame."""
        if not traces:
            return pd.DataFrame(columns=[
                "trace_id", "session_id", "speaker_seat", "which_brain", "epistemic_state",
                "sources_count", "memories_count", "validations_count", "contradictions_count",
                "evidence_count", "verified_evidence_count", "has_unverified_e4", "has_unverified_evidence",
                "content_hash", "timestamp", "question_or_intent", "why_trust_reason",
                "evidence_ids", "evidence_classes"
            ])
        rows = [cls.trace_to_dict(t) for t in traces]
        df = pd.DataFrame(rows)
        # Type coercions
        df["sources_count"] = df["sources_count"].astype(int)
        df["evidence_count"] = df["evidence_count"].astype(int)
        df["contradictions_count"] = df["contradictions_count"].astype(int)
        return df

    @classmethod
    def group_summary_by_seat(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Groups trace observations by speaker seat, computing counts and mean metrics."""
        if df.empty:
            return []
        grouped = df.groupby("speaker_seat").agg(
            total_turns=("trace_id", "count"),
            avg_sources=("sources_count", "mean"),
            avg_evidence=("evidence_count", "mean"),
            total_contradictions=("contradictions_count", "sum"),
            proven_count=("epistemic_state", lambda s: (s == EpistemicState.PROVEN.value).sum()),
            unknown_count=("epistemic_state", lambda s: (s == EpistemicState.UNKNOWN.value).sum()),
        ).reset_index()
        return grouped.to_dict(orient="records")

    @classmethod
    def pivot_brain_by_epistemic_state(cls, traces: List[GovernanceTrace]) -> Dict[str, Any]:
        """
        Generates a 2D Pivot Table of (which_brain × epistemic_state)
        along with complete Cell Lineage Back-Tracing mapping.
        """
        df = cls.to_dataframe(traces)
        if df.empty:
            return {"pivot_table": {}, "cell_lineage": {}}

        # Cross-tabulation count
        ctab = pd.crosstab(df["which_brain"], df["epistemic_state"])
        pivot_dict = ctab.to_dict(orient="index")

        # Cell lineage back-tracing: mapping (brain, state) -> List[trace_id]
        lineage_map: Dict[str, List[str]] = {}
        for t in traces:
            key = f"{t.which_brain_consulted}::{t.epistemic_state.value}"
            if key not in lineage_map:
                lineage_map[key] = []
            lineage_map[key].append(t.trace_id)

        return {
            "pivot_table": pivot_dict,
            "cell_lineage": lineage_map
        }

    @classmethod
    def compute_distribution_metrics(cls, df: pd.DataFrame, column: str) -> Optional[TraceBoxPlotMetrics]:
        """
        Computes box plot distribution metrics: Q1, Median, Q3, IQR, Lower/Upper Fences, and Outliers.
        """
        if df.empty or column not in df.columns:
            return None

        series = df[column].dropna().astype(float)
        n = len(series)
        if n == 0:
            return None

        q1 = float(np.percentile(series, 25))
        median = float(np.percentile(series, 50))
        q3 = float(np.percentile(series, 75))
        iqr = q3 - q1
        lower_fence = float(q1 - 1.5 * iqr)
        upper_fence = float(q3 + 1.5 * iqr)
        minimum = float(series.min())
        maximum = float(series.max())

        # Outlier identification
        outlier_mask = (series < lower_fence) | (series > upper_fence)
        outlier_traces = tuple(df.loc[outlier_mask, "trace_id"].tolist())
        outlier_count = int(outlier_mask.sum())

        return TraceBoxPlotMetrics(
            variable=column,
            sample_size=n,
            minimum=minimum,
            q1=q1,
            median=median,
            q3=q3,
            maximum=maximum,
            iqr=iqr,
            lower_fence=lower_fence,
            upper_fence=upper_fence,
            outlier_count=outlier_count,
            outlier_trace_ids=outlier_traces
        )

    @classmethod
    def compute_relationship_metrics(cls, df: pd.DataFrame, x_col: str, y_col: str) -> Optional[TraceRelationshipMetrics]:
        """
        Computes statistical correlation while explicitly carrying non-causality governance boundaries.
        """
        if df.empty or x_col not in df.columns or y_col not in df.columns:
            return None

        sub = df[[x_col, y_col]].dropna()
        n = len(sub)
        if n < 2:
            return None

        corr = float(sub[x_col].corr(sub[y_col]))
        if np.isnan(corr):
            corr = 0.0

        if corr > 0.1:
            direction = "POSITIVE"
        elif corr < -0.1:
            direction = "NEGATIVE"
        else:
            direction = "NEUTRAL"

        return TraceRelationshipMetrics(
            x_variable=x_col,
            y_variable=y_col,
            sample_size=n,
            correlation_coefficient=corr,
            direction=direction,
            association_not_causation=True,
            unmeasured_confounders_may_exist=True,
            governance_action_permitted=False
        )

    @classmethod
    def generate_attention_matrix(cls, traces: List[GovernanceTrace]) -> Dict[str, Any]:
        """
        Generates the Communication Attention Matrix identifying hotspot clusters:
        - Outlier contradictions
        - EpistemicState.UNKNOWN traces
        - Unverified E4 artifacts
        Nominates exact trace IDs for Landlord (Seat 1) or Validator (Seat 8) inspection.
        """
        df = cls.to_dataframe(traces)
        if df.empty:
            return {
                "nominated_for_kc_inspection": [],
                "unknown_count": 0,
                "contradiction_outliers": [],
                "unverified_e4_traces": [],
            }

        unknown_traces = df.loc[df["epistemic_state"] == EpistemicState.UNKNOWN.value, "trace_id"].tolist()
        e4_traces = df.loc[df["has_unverified_e4"] == True, "trace_id"].tolist()

        dist_contra = cls.compute_distribution_metrics(df, "contradictions_count")
        contra_outliers = list(dist_contra.outlier_trace_ids) if dist_contra else []

        # Deduplicate inspection nominations
        nominated = list(dict.fromkeys(unknown_traces + e4_traces + contra_outliers))

        return {
            "nominated_for_kc_inspection": nominated,
            "unknown_count": len(unknown_traces),
            "contradiction_outliers": contra_outliers,
            "unverified_e4_traces": e4_traces,
            "attention_verdict": "ATTENTION_REQUIRED" if nominated else "ATTENTION_CLEAR"
        }

    @classmethod
    def trace_cell_lineage(cls, traces: List[GovernanceTrace], trace_ids: List[str]) -> Dict[str, Any]:
        """
        Performs exact backward provenance reconstruction from aggregate analytical cells
        to underlying raw cryptographic receipts.
        """
        id_set = set(trace_ids)
        matched_traces = [t for t in traces if t.trace_id in id_set]

        all_evidence = []
        for t in matched_traces:
            for e in t.evidence_items:
                all_evidence.append({
                    "trace_id": t.trace_id,
                    "evidence_id": e.evidence_id,
                    "evidence_class": e.evidence_class.value,
                    "source_location": e.source_location,
                    "verified": e.verified,
                    "description": e.description
                })

        return {
            "requested_trace_ids": trace_ids,
            "matched_trace_count": len(matched_traces),
            "traces": [t.to_dict() for t in matched_traces],
            "surviving_evidence": all_evidence,
            "content_hashes": [t.content_hash for t in matched_traces],
            "lineage_sealed": True
        }
