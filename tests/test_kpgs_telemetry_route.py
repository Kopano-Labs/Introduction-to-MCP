"""KPGS telemetry routing — Black Beast thesis extension."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_agent_validate import synthesize_agent_manifest, validate_kpgs_agent  # noqa: E402
from kopano.kpgs_telemetry_route import (  # noqa: E402
    classify_telemetry_signal,
    compile_black_beast_thesis,
    verify_telemetry_routing,
)


def test_black_beast_thesis_compiles():
    out = compile_black_beast_thesis(write_log=False)
    assert out["verdict"] == "COMPILED"
    assert out["routing_steps"] == 8


def test_classify_rejects_pressure_only():
    out = classify_telemetry_signal("I am under pressure")
    assert out["verdict"] == "RECLASSIFY"
    assert out["misnamed_pressure"] is True


def test_classify_routes_grief_lane():
    out = classify_telemetry_signal("I carry grief and institutional resistance from DMR")
    assert out["verdict"] == "ROUTED"
    assert "grief" in out["detected_lanes"]
    assert "institutional_resistance" in out["detected_lanes"]


def test_manifest_requires_telemetry_routing():
    m = synthesize_agent_manifest("kasilink")
    ok, _ = verify_telemetry_routing(m)
    assert ok
    del m["telemetry_routing"]
    ok, errs = verify_telemetry_routing(m)
    assert not ok
    assert errs


def test_mesh_agent_passes_routing_gate():
    out = validate_kpgs_agent("eddie_bgf_mining", manifest=synthesize_agent_manifest("eddie_bgf_mining"))
    assert out["verdict"] == "SHIP"
    routing_check = next(c for c in out["checks"] if c["check"] == "kpgs_telemetry_routing")
    assert routing_check["verdict"] == "PASS"
