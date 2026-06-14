"""
Infinite Hood — cloud territory layer for KPGS 300-agent swarm.

Kernel stays on Black Beast; agents deploy to domain plots via sharded assignment.
Outer API (/api/kc/phu, /api/kasilink) is the client-facing shell for PWAs and giants.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCTRINE_PATH = REPO_ROOT / "docs" / "swarm-ops" / "INFINITE_HOOD_CLOUD_DOCTRINE.json"
GRID_PATH = REPO_ROOT / "docs" / "swarm-ops" / "DOMAIN_GRID_INVENTORY.json"
DEPLOYMENT_PATH = REPO_ROOT / "docs" / "swarm-ops" / "INFINITE_HOOD_DEPLOYMENT.json"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"error": "missing", "_source": str(path.relative_to(REPO_ROOT)).replace("\\", "/")}
    data = json.loads(path.read_text(encoding="utf-8"))
    data["_source"] = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    return data


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_infinite_hood_doctrine() -> dict[str, Any]:
    return _read_json(DOCTRINE_PATH)


def load_domain_grid() -> dict[str, Any]:
    grid = _read_json(GRID_PATH)
    extend = grid.get("operator_extend") or {}
    extra = extend.get("domains") or []
    if extra:
        plots = list(grid.get("plots") or [])
        for item in extra:
            if isinstance(item, dict) and item.get("domain"):
                plots.append(item)
        grid["plots"] = plots
        grid["extended_plot_count"] = len(extra)
    return grid


def load_deployment_manifest() -> dict[str, Any]:
    return _read_json(DEPLOYMENT_PATH)


def _plots_for_assignment(grid: dict[str, Any]) -> list[dict[str, Any]]:
    plots = list(grid.get("plots") or [])
    return [p for p in plots if p.get("status") not in ("dormant_dns", "retired")]


def _lane_mix(doctrine: dict[str, Any], lane_id: str) -> dict[str, float]:
    lanes = doctrine.get("product_lanes") or {}
    lane = lanes.get(lane_id) or lanes.get("parked_plot") or {}
    mix = lane.get("agent_mix") or {"telemetry": 0.33, "identic": 0.33, "guardian": 0.34}
    return {k: float(v) for k, v in mix.items()}


def build_deployment_manifest(*, max_landlords: int = 50) -> dict[str, Any]:
    """Assign 300 spawn agents across domain plots — landlords first, then utilities."""
    from .kpgs_spawn_swarm import agents_by_cohort, load_spawn_catalog

    doctrine = load_infinite_hood_doctrine()
    grid = load_domain_grid()
    catalog = load_spawn_catalog()
    if catalog.get("error"):
        return {"verdict": "INCOMPLETE", "error": "spawn_catalog_missing"}

    plots = _plots_for_assignment(grid)
    if not plots:
        return {"verdict": "INCOMPLETE", "error": "no_plots_in_grid"}

    guardians = agents_by_cohort("guardian")
    telemetry = agents_by_cohort("telemetry")
    identic = agents_by_cohort("identic")

    landlord_plots = plots[:max_landlords]
    assignments: list[dict[str, Any]] = []
    assigned_ids: set[str] = set()

    for i, plot in enumerate(landlord_plots):
        guardian = guardians[i % len(guardians)]
        gid = guardian["id"]
        assigned_ids.add(gid)
        assignments.append(
            {
                "plot_id": plot.get("plot_id"),
                "domain": plot.get("domain"),
                "status": plot.get("status"),
                "product_lane": plot.get("product_lane"),
                "role": "landlord_guardian",
                "agent_id": gid,
                "spawn_slot": guardian.get("spawn_slot"),
                "altar_layer": guardian.get("altar_layer"),
                "outer_api_mount": plot.get("outer_api_mount"),
            }
        )

    active_plots = [p for p in plots if p.get("status") == "active"]
    utility_plots = active_plots if active_plots else landlord_plots

    def _pool(cohort: str) -> list[dict[str, Any]]:
        pool = agents_by_cohort(cohort)
        return [a for a in pool if a["id"] not in assigned_ids]

    tel_pool = _pool("telemetry")
    id_pool = _pool("identic")
    gua_pool = [a for a in guardians if a["id"] not in assigned_ids]

    plot_weights: list[tuple[dict[str, Any], float]] = []
    for plot in utility_plots:
        mix = _lane_mix(doctrine, str(plot.get("product_lane", "parked_plot")))
        weight = 0.1 + mix.get("telemetry", 0) + mix.get("identic", 0) + mix.get("guardian", 0)
        plot_weights.append((plot, weight))
    total_w = sum(w for _, w in plot_weights) or 1.0

    tel_i = id_i = gua_i = 0
    for plot, weight in plot_weights:
        share = max(1, int(round((weight / total_w) * (len(tel_pool) + len(id_pool) + len(gua_pool)) / max(len(plot_weights), 1))))
        mix = _lane_mix(doctrine, str(plot.get("product_lane", "parked_plot")))
        n_tel = min(len(tel_pool) - tel_i, max(0, int(share * mix.get("telemetry", 0.33))))
        n_id = min(len(id_pool) - id_i, max(0, int(share * mix.get("identic", 0.33))))
        n_gua = min(len(gua_pool) - gua_i, max(0, int(share * mix.get("guardian", 0.34))))

        for _ in range(n_tel):
            if tel_i >= len(tel_pool):
                break
            a = tel_pool[tel_i]
            tel_i += 1
            assigned_ids.add(a["id"])
            assignments.append(_utility_row(plot, a, "telemetry_utility"))
        for _ in range(n_id):
            if id_i >= len(id_pool):
                break
            a = id_pool[id_i]
            id_i += 1
            assigned_ids.add(a["id"])
            assignments.append(_utility_row(plot, a, "identic_utility"))
        for _ in range(n_gua):
            if gua_i >= len(gua_pool):
                break
            a = gua_pool[gua_i]
            gua_i += 1
            assigned_ids.add(a["id"])
            assignments.append(_utility_row(plot, a, "guardian_utility"))

    # Round-robin any remaining agents onto active plots
    remainder = [a for a in catalog.get("agents", []) if a["id"] not in assigned_ids]
    for j, agent in enumerate(remainder):
        plot = utility_plots[j % len(utility_plots)]
        cohort = agent.get("cohort", "telemetry")
        role = f"{cohort}_overflow"
        assignments.append(_utility_row(plot, agent, role))
        assigned_ids.add(agent["id"])

    by_plot: dict[str, list[str]] = {}
    by_role: dict[str, int] = {}
    for row in assignments:
        pid = row.get("plot_id", "unknown")
        by_plot.setdefault(pid, []).append(row["agent_id"])
        by_role[row.get("role", "unknown")] = by_role.get(row.get("role", "unknown"), 0) + 1

    manifest = {
        "schema": "infinite_hood_deployment_v1",
        "ts": _utc_now(),
        "title": "Infinite Hood — Domain-Sharded Agent Deployment",
        "doctrine_ref": doctrine.get("_source"),
        "grid_ref": grid.get("_source"),
        "spawn_catalog_ref": catalog.get("_source"),
        "spawn_counts": catalog.get("counts", {}),
        "plots_total": len(plots),
        "plots_active": len(active_plots),
        "landlords_assigned": by_role.get("landlord_guardian", 0),
        "agents_assigned": len(assignments),
        "agents_unassigned": max(0, len(catalog.get("agents", [])) - len(assigned_ids)),
        "by_role": by_role,
        "by_plot_agent_count": {k: len(v) for k, v in by_plot.items()},
        "assignments": assignments,
        "verdict": "READY" if len(assigned_ids) == len(catalog.get("agents", [])) else "PARTIAL",
    }
    return manifest


def _utility_row(plot: dict[str, Any], agent: dict[str, Any], role: str) -> dict[str, Any]:
    return {
        "plot_id": plot.get("plot_id"),
        "domain": plot.get("domain"),
        "status": plot.get("status"),
        "product_lane": plot.get("product_lane"),
        "role": role,
        "agent_id": agent["id"],
        "spawn_slot": agent.get("spawn_slot"),
        "cohort": agent.get("cohort"),
        "altar_layer": agent.get("altar_layer"),
        "outer_api_mount": plot.get("outer_api_mount"),
    }


def outer_api_surface() -> dict[str, Any]:
    """Client ingress map — outer babies: PWAs, Microsoft, Google land here."""
    return {
        "schema": "infinite_hood_outer_api_v1",
        "ts": _utc_now(),
        "bracket": "[OUTER_API]",
        "production_url": "https://context.kopanolabs.com",
        "verified_endpoints_ref": "docs/swarm-ops/VERIFIED_ENDPOINTS.md",
        "surfaces": [
            {
                "mount": "/api/kc/phu",
                "module": "kopano-core/kopano/kc_phu_legacy_api.py",
                "clients": ["kopano_context_pwa", "google_workspace", "internal_console"],
                "hood_routes": [
                    "GET /kpgs/entry",
                    "GET /kpgs/governance",
                    "GET /kpgs/spawn/status",
                    "POST /kpgs/spawn/compile",
                    "GET /kpgs/hood/status",
                    "GET /kpgs/hood/domains",
                    "GET /kpgs/hood/outer-api",
                    "POST /kpgs/hood/dispatch",
                    "POST /kpgs/hood/compile",
                ],
            },
            {
                "mount": "/api/kasilink",
                "module": "kopano-core/kopano/kasilink_api.py",
                "clients": ["kasilink_pwa", "vercel_preview", "za_mobile"],
                "routes": ["/health", "/match", "/sentiment", "/forecast", "/loadshedding", "/moderate", "/notify"],
            },
        ],
        "giant_integrations": {
            "microsoft_partner_blade_id": "6962519",
            "microsoft": ["copilot", "azure_openai", "graph_webhook_ingress"],
            "google": ["workspace_addon", "google_app_store_pwa", "oauth_client"],
        },
        "dispatch_note": "All client traffic through hood dispatch — SWFUS → Jethro → WWJD before agent cook",
    }


def hood_dispatch_for_plot(
    *,
    plot_id: str,
    message: str,
    agent_id: str = "",
) -> dict[str, Any]:
    """Route client message through plot landlord or specified agent."""
    from .kpgs_spawn_swarm import dispatch_spawn_event, spawn_agent_by_id

    manifest = load_deployment_manifest()
    if manifest.get("error"):
        manifest = build_deployment_manifest()

    plot_rows = [a for a in manifest.get("assignments", []) if a.get("plot_id") == plot_id]
    if not plot_rows:
        return {"verdict": "REJECT", "error": "plot_not_found", "plot_id": plot_id}

    resolved_agent = agent_id
    if not resolved_agent:
        landlord = next((r for r in plot_rows if r.get("role") == "landlord_guardian"), plot_rows[0])
        resolved_agent = landlord.get("agent_id", "")

    if not spawn_agent_by_id(resolved_agent):
        return {"verdict": "REJECT", "error": "agent_not_in_spawn_catalog", "agent_id": resolved_agent}

    domain = plot_rows[0].get("domain")
    event = dispatch_spawn_event(agent_id=resolved_agent, message=message, intent=f"hood_plot:{plot_id}")
    return {
        "schema": "infinite_hood_dispatch_v1",
        "ts": _utc_now(),
        "plot_id": plot_id,
        "domain": domain,
        "agent_id": resolved_agent,
        "proceed": event.get("proceed"),
        "event": event.get("event"),
        "spawn_event": event,
        "outer_api_bracket": "[OUTER_API→SWFUS→KPGS]",
    }


def infinite_hood_status() -> dict[str, Any]:
    doctrine = load_infinite_hood_doctrine()
    grid = load_domain_grid()
    manifest = load_deployment_manifest()
    if manifest.get("error"):
        manifest = build_deployment_manifest()

    plots = grid.get("plots") or []
    return {
        "schema": "infinite_hood_status_v1",
        "ts": _utc_now(),
        "hood_objective": doctrine.get("hood_objective"),
        "plots_total": len(plots),
        "plots_active": sum(1 for p in plots if p.get("status") == "active"),
        "plots_parked": sum(1 for p in plots if p.get("status") == "parked"),
        "microsoft_partner_blade_id": (grid.get("cloud_backbone") or {}).get("microsoft_partner_blade_id"),
        "deployment_verdict": manifest.get("verdict"),
        "agents_assigned": manifest.get("agents_assigned"),
        "landlords_assigned": manifest.get("landlords_assigned"),
        "by_plot_agent_count": manifest.get("by_plot_agent_count"),
        "outer_api": outer_api_surface(),
        "spawn_note": "300 agents shard across plots — nobody dormant on active plots",
    }


def write_deployment_manifest(manifest: dict[str, Any]) -> Path:
    DEPLOYMENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEPLOYMENT_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return DEPLOYMENT_PATH


def compile_infinite_hood(*, write_log: bool = True) -> dict[str, Any]:
    from .kpgs_spawn_swarm import compile_spawn_swarm

    spawn = compile_spawn_swarm(write_log=False)
    if spawn.get("verdict") != "COMPILED":
        return {
            "verdict": "INCOMPLETE",
            "error": "spawn_swarm_not_compiled",
            "spawn": spawn,
        }

    manifest = build_deployment_manifest()
    write_deployment_manifest(manifest)
    verdict = "COMPILED" if manifest.get("verdict") == "READY" else "INCOMPLETE"
    summary = (
        f"[INFINITE_HOOD] compile | verdict={verdict} | "
        f"plots={manifest.get('plots_total')} active={manifest.get('plots_active')} | "
        f"agents={manifest.get('agents_assigned')} landlords={manifest.get('landlords_assigned')}"
    )
    out = {
        "schema": "infinite_hood_compile_v1",
        "ts": _utc_now(),
        "verdict": verdict,
        "deployment": manifest,
        "spawn_compile": {"verdict": spawn.get("verdict")},
        "outer_api": outer_api_surface(),
        "summary": summary,
    }
    if write_log and verdict == "COMPILED":
        _append_jsonl(
            MAIN_BRAIN_LOG,
            {
                "schema": "kc_main_brain_log_v1",
                "ts": _utc_now(),
                "kind": "infinite_hood_compile",
                "summary": summary,
                "exit_code": 0,
                "payload_ref": str(DEPLOYMENT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            },
        )
    return out
