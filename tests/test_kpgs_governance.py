"""Tests for KPGS governance — Schematics MAIN BRAIN bridge."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_governance import (  # noqa: E402
    classify_submission,
    compile_kpgs_governance,
    governance_status,
    load_main_brain_governance,
)


def test_main_brain_registry_loads():
    reg = load_main_brain_governance()
    assert reg.get("schema") == "kpgs_main_brain_governance_v1"
    assert reg.get("authority") == "Schematics MAIN BRAIN"
    assert "sector_02_eddie" in (reg.get("sectors") or {})


def test_classify_submission_not_blocked_by_default():
    out = classify_submission(action="deploy kasilink", evidence="vercel preview PASS")
    assert out.get("blocked") is False
    assert out.get("classification", {}).get("verdict") in ("ACCEPT", "ROUTED", "RECLASSIFY")


def test_compile_kpgs_governance():
    out = compile_kpgs_governance(write_log=False)
    assert out.get("verdict") in ("COMPILED", "INCOMPLETE")
    assert out.get("thesis", {}).get("verdict") == "COMPILED"
    assert out.get("black_beast", {}).get("verdict") == "COMPILED"


def test_governance_status_shape():
    st = governance_status()
    assert st.get("schema") == "kpgs_governance_status_v1"
    assert st.get("registry_present") is True
    assert "mesh_overall" in st
