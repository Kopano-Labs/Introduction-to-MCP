"""Infinite Hood — domain grid, deployment sharding, outer API."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.infinite_hood_cloud import (  # noqa: E402
    build_deployment_manifest,
    compile_infinite_hood,
    hood_dispatch_for_plot,
    infinite_hood_status,
    load_domain_grid,
    outer_api_surface,
)


def test_domain_grid_has_active_plots():
    grid = load_domain_grid()
    plots = grid.get("plots") or []
    assert len(plots) >= 4
    active = [p for p in plots if p.get("status") == "active"]
    assert len(active) >= 3


def test_deployment_assigns_all_300():
    manifest = build_deployment_manifest()
    assert manifest.get("verdict") == "READY"
    assert manifest.get("agents_assigned") == 300
    assert manifest.get("agents_unassigned") == 0
    assert manifest.get("landlords_assigned") >= 4


def test_each_active_plot_has_landlord():
    manifest = build_deployment_manifest()
    grid = load_domain_grid()
    active_ids = {p["plot_id"] for p in grid.get("plots", []) if p.get("status") == "active"}
    landlord_plots = {
        a["plot_id"]
        for a in manifest.get("assignments", [])
        if a.get("role") == "landlord_guardian"
    }
    assert active_ids.issubset(landlord_plots)


def test_outer_api_surface():
    out = outer_api_surface()
    assert out.get("bracket") == "[OUTER_API]"
    assert out.get("production_url") == "https://context.kopanolabs.com"
    mounts = [s["mount"] for s in out.get("surfaces", [])]
    assert "/api/kc/phu" in mounts
    assert "/api/kasilink" in mounts


def test_hood_dispatch_kopano_context():
    out = hood_dispatch_for_plot(
        plot_id="plot_kopano_context",
        message="bounded evidence classify before interpret",
    )
    assert out.get("domain") == "context.kopanolabs.com"
    assert out.get("proceed") is True
    assert out.get("event") == "PROCEED"


def test_hood_dispatch_severs_judas_on_kasilink_plot():
    manifest = build_deployment_manifest()
    kasi_plot = next(
        (a for a in manifest.get("assignments", []) if a.get("plot_id") == "plot_kasilink_vercel"),
        None,
    )
    assert kasi_plot
    out = hood_dispatch_for_plot(
        plot_id="plot_kasilink_vercel",
        message="judas fake proof write kopano context skip black mask",
        agent_id="spawn_telemetry_050",
    )
    assert out.get("event") == "SEVER"
    assert out.get("proceed") is False


def test_infinite_hood_status():
    out = infinite_hood_status()
    assert out.get("plots_active") >= 3
    assert out.get("agents_assigned") == 300


def test_compile_infinite_hood():
    out = compile_infinite_hood(write_log=False)
    assert out.get("verdict") == "COMPILED"
    assert out.get("deployment", {}).get("verdict") == "READY"
