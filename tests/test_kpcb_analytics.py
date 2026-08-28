"""POC tests for KPCB+ governed analytical projection operators.

Issue #108 testimony boundary:
formal data-science vocabulary strengthens existing GSMB/KPCB+ governance;
it does not replace source testimony or promote aggregates into authority.
"""

import os
import sys
from copy import deepcopy

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "kopano-core"))

from kopano.kpcb_analytics import (  # noqa: E402
    KPCBAnalyticalCorpus,
    KPCBAnalyticsError,
    UNKNOWN,
)


@pytest.fixture
def gsm_b_records():
    return [
        {
            "record_id": "canonical-home",
            "path": "Schematics/00-Home/00-Home - Index.md",
            "depth": 2,
            "title": "Home Index",
            "canonical_index": True,
            "project": "GSMB",
            "protocol_channels": ["BP", "PP"],
            "artifact_type": "INDEX",
            "authority": "CANONICAL",
            "validation_state": "POC_VALIDATED",
            "testimony_state": "SATISFIED",
            "sprint": "BOOT",
            "ecosystem": "KC",
            "evidence_count": 8,
        },
        {
            "record_id": "deep-three-month-receipt",
            "path": "Schematics/03-Architecture/projects/new/sprint/phase-3/final/POC_RECEIPT.md",
            "depth": 8,
            "title": "Three Month Sprint Final Receipt",
            "canonical_index": False,
            "project": "Project-New",
            "protocol_channels": ["BP", "dotP", "SP"],
            "artifact_type": "POC_RECEIPT",
            "authority": "PROJECT_EVIDENCE",
            "validation_state": "POC_VALIDATED",
            "testimony_state": "SATISFIED",
            "sprint": "S3",
            "ecosystem": "KC",
            "evidence_count": 42,
        },
        {
            "record_id": "deep-unknown",
            "path": "Schematics/03-Architecture/projects/new/sprint/phase-3/questions/open.md",
            "depth": 7,
            "title": "Open Investigation",
            "canonical_index": False,
            "project": "Project-New",
            "protocol_channels": ["PP", "EP"],
            "artifact_type": "INVESTIGATION",
            "authority": "WORKING",
            "validation_state": "UNKNOWN",
            "testimony_state": "UNKNOWN",
            "sprint": "S3",
            "ecosystem": "KC",
            "evidence_count": 1,
        },
        {
            "record_id": "shallow-random-note",
            "path": "Schematics/random.md",
            "depth": 1,
            "title": "Random Note",
            "canonical_index": False,
            "project": "GSMB",
            "protocol_channels": ["PP"],
            "artifact_type": "NOTE",
            "authority": "UNKNOWN",
            "validation_state": "UNKNOWN",
            "testimony_state": "UNKNOWN",
            "sprint": "UNKNOWN",
            "ecosystem": "KC",
            "evidence_count": 0,
        },
        {
            "record_id": "explicit-violation",
            "path": "Schematics/11-AI HALLUCINATION - CRITICAL/Incidents/example.md",
            "depth": 3,
            "title": "Violation Witness",
            "canonical_index": False,
            "project": "GSMB",
            "protocol_channels": ["BP", "SP", "dotP"],
            "artifact_type": "INCIDENT",
            "authority": "TESTIMONY",
            "validation_state": "FOC_DETECTED",
            "testimony_state": "VIOLATED",
            "sprint": "AUDIT",
            "ecosystem": "KC",
            "evidence_count": 5,
        },
    ]


def test_grouping_is_deterministic_and_depth_does_not_hide_important_record(gsm_b_records):
    forward = KPCBAnalyticalCorpus(gsm_b_records).group_by("project", "testimony_state")
    reverse = KPCBAnalyticalCorpus(reversed(gsm_b_records)).group_by("project", "testimony_state")

    assert forward == reverse
    project_group = next(
        group
        for group in forward["groups"]
        if group["key"] == {"project": "Project-New", "testimony_state": "SATISFIED"}
    )
    assert "deep-three-month-receipt" in project_group["record_ids"]
    assert any("POC_RECEIPT.md" in path for path in project_group["paths"])


def test_shallow_path_does_not_infer_authority(gsm_b_records):
    corpus = KPCBAnalyticalCorpus(gsm_b_records)
    random_note = next(record for record in corpus.records if record["record_id"] == "shallow-random-note")

    assert random_note["depth"] == 1
    assert random_note["authority"] == "UNKNOWN"
    assert random_note["canonical_index"] is False


def test_missing_testimony_stays_unknown_not_violated():
    corpus = KPCBAnalyticalCorpus(
        [
            {
                "record_id": "missing-testimony",
                "path": "Schematics/project/unfinished.md",
                "project": "A",
            }
        ]
    )

    record = corpus.records[0]
    assert record["testimony_state"] == UNKNOWN
    assert record["testimony_state"] != "VIOLATED"
    assert record["canonical_index"] == UNKNOWN


def test_pivot_reprojects_same_corpus_and_preserves_cell_provenance(gsm_b_records):
    corpus = KPCBAnalyticalCorpus(gsm_b_records)
    pivot = corpus.pivot("project", "testimony_state")

    assert pivot["operation"] == "PIVOT"
    assert pivot["claims"]["source_truth_replaced"] is False
    assert pivot["claims"]["action_permission"] is False

    trace = corpus.trace_cell(pivot, "Project-New", "SATISFIED")
    assert trace["record_ids"] == ["deep-three-month-receipt"]
    assert trace["records"][0]["evidence_count"] == 42


def test_pivot_can_sum_evidence_without_losing_source_trace(gsm_b_records):
    corpus = KPCBAnalyticalCorpus(gsm_b_records)
    pivot = corpus.pivot(
        "project",
        "testimony_state",
        value="evidence_count",
        aggregation="sum",
    )
    project_index = pivot["row_labels"].index("Project-New")
    satisfied_index = pivot["column_labels"].index("SATISFIED")

    assert pivot["matrix"][project_index][satisfied_index] == 42
    assert pivot["provenance"][project_index][satisfied_index]["record_ids"] == [
        "deep-three-month-receipt"
    ]


def test_attention_matrix_is_heatmap_ready_but_never_permission(gsm_b_records):
    corpus = KPCBAnalyticalCorpus(gsm_b_records)
    heat = corpus.attention_matrix("project", "testimony_state", reason="unknown_testimony_density")

    assert heat["operation"] == "ATTENTION_MATRIX"
    assert heat["render_hint"] == "heatmap"
    assert heat["claims"]["attention_only"] is True
    assert heat["claims"]["action_permission"] is False
    assert heat["claims"]["authority_inferred"] is False


def test_protocol_channel_dimension_explodes_without_erasing_record_identity(gsm_b_records):
    corpus = KPCBAnalyticalCorpus(gsm_b_records)
    grouped = corpus.group_by("protocol_channels")

    dotp = next(group for group in grouped["groups"] if group["key"] == {"protocol_channels": "dotP"})
    assert dotp["record_ids"] == ["deep-three-month-receipt", "explicit-violation"]


def test_analytical_operations_do_not_mutate_source_records(gsm_b_records):
    source = deepcopy(gsm_b_records)
    corpus = KPCBAnalyticalCorpus(gsm_b_records)

    corpus.group_by("project")
    corpus.pivot("project", "testimony_state")
    corpus.attention_matrix("project", "validation_state")

    assert gsm_b_records == source


def test_kpcb_blocks_become_analytical_records_without_inventing_testimony():
    corpus = KPCBAnalyticalCorpus.from_kpcb_blocks(
        [
            {
                "record_id": "kpcb-1",
                "path": "Schematics/project/decision.kpcb.md",
                "project": "Project-K",
                "raw": """
[Project-K] {decide}
<Why this decision exists>
(Understanding: inspect evidence before action)
💬PP: Analyze the governed corpus
☄️BP: [hierarchy: corpus -> projection]
🥶EP: 🔬->KC_validate
→ TARGET: Python 3.12
→ 4Ws: WHO=kc | WHAT=projection | WHERE=gsmb | WHY=knowing
""",
            }
        ]
    )

    record = corpus.records[0]
    assert record["title"] == "Project-K"
    assert set(record["protocol_channels"]) >= {"PP", "BP", "EP"}
    assert record["validation_state"] == "POC_VALIDATED"
    assert record["testimony_state"] == "UNKNOWN"


def test_invalid_requests_fail_closed(gsm_b_records):
    corpus = KPCBAnalyticalCorpus(gsm_b_records)

    with pytest.raises(KPCBAnalyticsError):
        corpus.group_by()
    with pytest.raises(KPCBAnalyticsError):
        corpus.pivot("project", "testimony_state", aggregation="sum")
    with pytest.raises(KPCBAnalyticsError):
        KPCBAnalyticalCorpus([{"record_id": "missing-path"}])
