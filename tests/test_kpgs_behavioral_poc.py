"""Mechanical KPGS behavioral PoC — hood dispatch, context bleed, sim tick."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_behavioral_poc import (  # noqa: E402
    proof_context_bleed_classify,
    proof_hood_dispatch_proceed,
    proof_hood_dispatch_sever,
    run_kpgs_behavioral_poc,
)


def test_context_bleed_reclassify_pressure():
    p = proof_context_bleed_classify()
    assert p["ok"] is True


def test_hood_dispatch_proceed():
    p = proof_hood_dispatch_proceed()
    assert p["ok"] is True


def test_hood_dispatch_sever_exfil():
    p = proof_hood_dispatch_sever()
    assert p["ok"] is True


def test_behavioral_poc_pipeline():
    from kopano.kpgs_activation_gate import check_kpgs_activation_gate

    gate = check_kpgs_activation_gate()
    report = run_kpgs_behavioral_poc(write_report=False)
    assert report["schema"] == "kpgs_behavioral_poc_v1"
    if gate.get("activation_allowed"):
        assert report["verdict"] in ("PASS", "FAIL")
        assert report.get("measurand", {}).get("independent_of_catalog_count") is True
    else:
        assert report["verdict"] == "BLOCKED"
