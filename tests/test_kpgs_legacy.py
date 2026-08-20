"""Tests for KC — Kopano Context Legacy runtime governance."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_legacy import (  # noqa: E402
    RENTER_ASSERTION,
    evaluate_legacy_impact,
    legacy_packet_template,
    legacy_status,
    load_legacy_contract,
)


def _complete_claim() -> dict:
    return {
        "claim": "A bounded local capability pathway produced observed economic participation.",
        "geography": "test-locality",
        "cohort": "test-cohort",
        "denominator": 10,
        "time_window": "2026-Q3",
        "baseline": "0 validated pathway completions",
        "observed_change": "3 validated pathway completions",
        "methodology": "receipt-linked cohort observation",
        "evidence_refs": ["receipt:test:001"],
        "attribution_basis": "bounded programme contribution; not sole causality",
    }


def test_legacy_contract_loads_from_main_brain():
    contract = load_legacy_contract()
    assert contract["schema"] == "kpgs_kopano_context_legacy_v1"
    assert contract["invariants"]["kc"] == "Kopano Context Legacy"
    assert contract["invariants"]["precedence"] == "KPGS_LEGACY > RENTER_IDENTITY"


def test_legacy_status_keeps_mission_bounded():
    status = legacy_status()
    assert status["kc"] == "Kopano Context Legacy"
    assert status["renter_assertion"] == RENTER_ASSERTION
    assert status["mission_is_not_completion_claim"] is True


def test_unknown_packet_holds():
    result = evaluate_legacy_impact(legacy_packet_template())
    assert result["disposition"] == "KC_HOLD"
    assert result["missing_or_unknown"]
    assert result["mission_completion_claim_allowed"] is False


def test_complete_unverified_packet_is_only_poc_candidate():
    result = evaluate_legacy_impact(
        {
            "renter_assertion": RENTER_ASSERTION,
            "impact_claim": _complete_claim(),
            "verification": {},
        }
    )
    assert result["disposition"] == "KC_POC_CANDIDATE"
    assert result["runtime_proves_external_evidence"] is False


def test_verified_capability_and_pathway_can_reach_aligned_poc():
    result = evaluate_legacy_impact(
        {
            "renter_assertion": RENTER_ASSERTION,
            "impact_claim": _complete_claim(),
            "verification": {
                "verifier_receipt": "verifier:test:001",
                "evidence_verified": True,
                "capability_validated": True,
                "economic_pathway_observed": True,
            },
        }
    )
    assert result["disposition"] == "KC_ALIGNED_POC"
    assert result["next_proof_required"] == []


def test_claim_exceeds_evidence_routes_to_foc_candidate():
    result = evaluate_legacy_impact(
        {
            "impact_claim": _complete_claim(),
            "verification": {"claim_exceeds_evidence": True},
        }
    )
    assert result["disposition"] == "KC_FOC_CANDIDATE"


def test_fabricated_or_unverifiable_proof_blocks():
    result = evaluate_legacy_impact(
        {
            "impact_claim": _complete_claim(),
            "verification": {"proof_fabricated_or_unverifiable": True},
        }
    )
    assert result["disposition"] == "KC_FOC_BLOCK"
