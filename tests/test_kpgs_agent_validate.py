"""KPGS Altar agent validation."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_agent_validate import (  # noqa: E402
    compile_kpgs_thesis,
    load_kpgs_thesis,
    synthesize_agent_manifest,
    validate_kpgs_agent,
    verify_commandments,
    verify_five_pillars,
)
from kopano.kpgs_telemetry_route import synthesize_telemetry_routing  # noqa: E402


def _good_manifest(agent_id: str = "test_agent") -> dict:
    proof = "docs/swarm-ops/KPEFS_CLOSURE_STATUS.json"
    base = synthesize_agent_manifest(agent_id)
    return {
        "schema": "kpgs_agent_manifest_v1",
        "agent_id": agent_id,
        "kc_executes": False,
        "pillars": base["pillars"],
        "telemetry_routing": synthesize_telemetry_routing(agent_id),
        "execution": {"uses_public_api": False},
        "evidence": {"proof_artifact_path": proof},
        "block_holder": base.get("block_holder"),
        "hood_entry": base.get("hood_entry"),
        "bracket_receipt": base.get(
            "bracket_receipt",
            f"[KPGS_BLOCK_HOLDER] agent: {agent_id} | brief_renters: yes | "
            f"[KPGS_AGENT_INIT] agent: {agent_id} | altar: ok",
        ),
    }


def test_verify_five_pillars_rejects_missing():
    ok, errs = verify_five_pillars({"pillars": {}})
    assert not ok
    assert errs


def test_verify_commandments_rejects_public_api():
    m = _good_manifest()
    m["execution"]["uses_public_api"] = True
    ok, errs = verify_commandments(m)
    assert not ok
    assert any("public API" in e for e in errs)


def test_kc_exempt_skips_pillars():
    m = synthesize_agent_manifest("kc")
    ok, _ = verify_five_pillars(m)
    assert ok


def test_validate_synthetic_eddie_mining():
    out = validate_kpgs_agent("eddie_bgf_mining", manifest=synthesize_agent_manifest("eddie_bgf_mining"))
    assert out["verdict"] == "SHIP"
    assert "rock|mining" in out["manifest"]["pillars"]["ground_awareness"]["telemetry_class"]


def test_validate_rejects_bad_bracket():
    m = _good_manifest("bad_bracket_agent")
    m["bracket_receipt"] = "[ONE_WORLD_ORDER] sacred caps bad"
    ok, errs = verify_commandments(m)
    assert not ok
    assert errs


def test_thesis_compiles():
    out = compile_kpgs_thesis(write_log=False)
    assert out["verdict"] == "COMPILED"
    thesis = load_kpgs_thesis()
    assert thesis["document_id"] == "KPGS-THESIS-2026-X8020"
    assert len(thesis["constitutional_framework"]["commandments"]) == 15


def test_block_holder_brief_mesh_agent():
    from kopano.kpgs_renter_entry import block_holder_brief

    brief = block_holder_brief(agent_id="eddie_bgf_mining")
    assert brief.get("holds_pillar_blocks") is True
    assert brief.get("brief_renters_on_entry") is True
    assert "stateless" in brief.get("tell_renters", "").lower() or "renter" in brief.get("tell_renters", "").lower()
    assert brief.get("bracket") == "[KPGS_BLOCK_HOLDER]"


def test_synthesize_agent_manifest_includes_block_holder():
    m = synthesize_agent_manifest("eddie_bgf_mining")
    assert m.get("block_holder", {}).get("brief_renters_on_entry") is True
    assert m.get("hood_entry", {}).get("hood_ack_required_from_renters") == "I_AM_STATELESS_RENTER_NOT_LANDLORD"


def test_validate_kpgs_agent_block_holder_gate():
    m = synthesize_agent_manifest("eddie_bgf_mining")
    r = validate_kpgs_agent("eddie_bgf_mining", manifest=m)
    block_check = next(c for c in r["checks"] if c["check"] == "kpgs_block_holder_brief")
    assert block_check["verdict"] == "PASS"
