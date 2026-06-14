"""
Kopano Sovereign SIM — thesis-framed world builder using guilded 300-agent hood.

Blocked until kpgs_activation_gate passes. World = thesis sectors × infinite hood plots × spawn assignments.
KC Save|Watch · Cassy execute · Kopano Context = GUI exfiltration channel (altar containment).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
WORLD_STATE_PATH = REPO_ROOT / "kopano-core" / ".kc" / "sovereign_sim_world.json"
SMOKE_REPORT_PATH = REPO_ROOT / "docs" / "swarm-ops" / "KPGS_SMOKE_POC_VALIDATION.json"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _repo_rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _gate_block_response(gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "sovereign_sim_blocked_v1",
        "ts": _utc_now(),
        "verdict": "BLOCKED",
        "activation_allowed": False,
        "gate": gate,
        "message": gate.get("message"),
        "instruction": "Run: python scripts/kc_kpgs_smoke_poc.py gate — fix failures before world-build",
    }


def build_world_regions() -> list[dict[str, Any]]:
    """Thesis sector_matrix + hood plots → playable world regions."""
    from .kpgs_agent_validate import load_kpgs_thesis
    from .infinite_hood_cloud import load_deployment_manifest, load_domain_grid

    thesis = load_kpgs_thesis()
    grid = load_domain_grid()
    manifest = load_deployment_manifest()
    if manifest.get("error"):
        from .infinite_hood_cloud import build_deployment_manifest

        manifest = build_deployment_manifest()

    sectors = thesis.get("sector_matrix", {}).get("sectors", [])
    plots = grid.get("plots") or []
    assignments = manifest.get("assignments") or []

    by_plot: dict[str, list[dict[str, Any]]] = {}
    for row in assignments:
        pid = row.get("plot_id", "unknown")
        by_plot.setdefault(pid, []).append(row)

    regions: list[dict[str, Any]] = []

    for sector in sectors:
        sid = sector.get("id", "sector")
        regions.append(
            {
                "region_id": sid,
                "kind": "thesis_sector",
                "codename": sector.get("codename"),
                "domain_label": sector.get("domain"),
                "pavement_target": sector.get("pavement_target"),
                "mesh_agent": sector.get("mesh_agent"),
                "catalog_ref": sector.get("catalog_ref"),
                "agent_count": 0,
                "agents_sample": [],
                "gui_layer": "natural_ai_simulation",
            }
        )

    for plot in plots:
        if plot.get("status") in ("dormant_dns", "retired"):
            continue
        pid = plot.get("plot_id")
        plot_agents = by_plot.get(pid, [])
        landlord = next((a for a in plot_agents if a.get("role") == "landlord_guardian"), None)
        regions.append(
            {
                "region_id": pid,
                "kind": "hood_plot",
                "domain": plot.get("domain"),
                "status": plot.get("status"),
                "product_lane": plot.get("product_lane"),
                "landlord_agent": landlord.get("agent_id") if landlord else None,
                "agent_count": len(plot_agents),
                "telemetry": sum(1 for a in plot_agents if a.get("cohort") == "telemetry"),
                "identic": sum(1 for a in plot_agents if a.get("cohort") == "identic"),
                "guardian": sum(1 for a in plot_agents if a.get("cohort") == "guardian"),
                "agents_sample": [a["agent_id"] for a in plot_agents[:6]],
                "outer_api": plot.get("outer_api_mount"),
                "gui_layer": "altar_token_exfiltration",
            }
        )

    # Attach identic catalog agents to matching thesis sectors by catalog_ref
    from .kpgs_spawn_swarm import load_spawn_catalog

    for agent in load_spawn_catalog().get("agents", []):
        ref = agent.get("catalog_ref")
        if not ref or agent.get("cohort") != "identic":
            continue
        # match kp agent id to sector catalog_ref in thesis
        for sector in sectors:
            if sector.get("catalog_ref") and agent.get("id") == sector.get("catalog_ref"):
                rid = sector.get("id")
                for region in regions:
                    if region.get("region_id") == rid:
                        region["agent_count"] = region.get("agent_count", 0) + 1
                        sample = region.get("agents_sample") or []
                        if len(sample) < 8:
                            sample.append(agent["id"])
                        region["agents_sample"] = sample

    return regions


def sovereign_sim_ui_snapshot() -> dict[str, Any]:
    """GUI/UX representation — KC · Cassy · Kopano Context triad + world strip."""
    from .steward_lane import steward_lane_kasilink_snapshot
    from .kpgs_activation_gate import load_cached_activation_gate

    gate = load_cached_activation_gate()
    steward = steward_lane_kasilink_snapshot()
    world = load_world_state()

    behavioral: dict[str, Any] = {}
    try:
        from .kpgs_behavioral_poc import BEHAVIORAL_REPORT_PATH

        if BEHAVIORAL_REPORT_PATH.is_file():
            behavioral = json.loads(BEHAVIORAL_REPORT_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        behavioral = {}

    return {
        "schema": "sovereign_sim_ui_v1",
        "ts": _utc_now(),
        "activation_allowed": gate.get("activation_allowed"),
        "gate_verdict": gate.get("verdict"),
        "behavioral_poc_verdict": behavioral.get("verdict"),
        "behavioral_measurand": behavioral.get("measurand"),
        "failed_behavioral_proofs": behavioral.get("failed_proofs", []),
        "kopano_context": {
            "host": "https://context.kopanolabs.com",
            "role": "eidetic_memory_state_engine",
            "gui_channel": "strict_gui_token_only",
            "api_mount": "/api/kc/phu",
        },
        "triad": {
            "kc": {"mode": "Save|Watch", "executes": False, "role": "brain_ledger"},
            "cassy": {"mode": "student_execute", "role": "lead_student", "active": steward.get("active")},
            "cassey": {"mode": "teacher_review", "role": "teacher"},
            "kopano": {"mode": "context_surface", "host": "context.kopanolabs.com"},
        },
        "steward_lane": steward,
        "world": world,
        "agent_total": world.get("agent_total", 0),
        "regions": world.get("regions", [])[:12],
        "thesis_ref": "docs/swarm-ops/KPGS_THESIS_2026_X8020.json",
        "bracket": "[SOVEREIGN_SIM_GUI]",
    }


def load_world_state() -> dict[str, Any]:
    if not WORLD_STATE_PATH.is_file():
        return {"schema": "sovereign_sim_world_v1", "bootstrapped": False, "regions": []}
    try:
        return json.loads(WORLD_STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"schema": "sovereign_sim_world_v1", "bootstrapped": False, "error": "corrupt_world_file"}


def bootstrap_sovereign_sim(*, write_log: bool = True) -> dict[str, Any]:
    """Build world from thesis + hood — only when activation gate ALLOW."""
    from .kpgs_activation_gate import check_kpgs_activation_gate

    gate = check_kpgs_activation_gate(write_report=True)
    if not gate.get("activation_allowed"):
        return _gate_block_response(gate)

    from .kpgs_spawn_swarm import load_spawn_catalog

    regions = build_world_regions()
    catalog = load_spawn_catalog()
    world = {
        "schema": "sovereign_sim_world_v1",
        "ts": _utc_now(),
        "bootstrapped": True,
        "verdict": "WORLD_READY",
        "thesis_frame": "KPGS_THESIS_2026_X8020 sector_matrix + infinite_hood plots",
        "agent_total": len(catalog.get("agents", [])),
        "regions_count": len(regions),
        "regions": regions,
        "triad_active": True,
        "gui_represents": ["kc", "cassy", "cassey", "kopano_context"],
        "game_loop_note": "Agents cook on hood plots; player sees tokens via Kopano Context GUI only",
    }

    WORLD_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    WORLD_STATE_PATH.write_text(json.dumps(world, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = (
        f"[SOVEREIGN_SIM] bootstrap | regions={len(regions)} | agents={world['agent_total']} | "
        f"gate=ALLOW | thesis=KPGS sector_matrix"
    )
    if write_log:
        _append_jsonl(
            MAIN_BRAIN_LOG,
            {
                "schema": "kc_main_brain_log_v1",
                "ts": _utc_now(),
                "kind": "sovereign_sim_bootstrap",
                "summary": summary,
                "exit_code": 0,
                "payload_ref": _repo_rel(WORLD_STATE_PATH),
            },
        )

    return {
        "schema": "sovereign_sim_bootstrap_v1",
        "ts": _utc_now(),
        "verdict": "BOOTSTRAPPED",
        "gate": gate,
        "world_path": _repo_rel(WORLD_STATE_PATH),
        "world": world,
        "summary": summary,
    }


def run_kpgs_smoke_poc(*, activate_steward: bool = True, bootstrap_sim: bool = True) -> dict[str, Any]:
    """
    Full smoke / PoC validation guided by KPGS governance.
    Gate → governance → steward → behavioral proofs → sovereign sim → eco receipt.
    PASS requires behavioral mechanical proofs, not catalog self-count.
    """
    from .eco_poc_validate import validate_eco_poc
    from .kpgs_activation_gate import check_kpgs_activation_gate
    from .kpgs_behavioral_poc import run_kpgs_behavioral_poc
    from .kpgs_governance import compile_kpgs_governance
    from .steward_lane import run_steward_lane_activate

    steps: list[dict[str, Any]] = []

    gate = check_kpgs_activation_gate(write_report=True)
    steps.append({"step": "activation_gate", "result": gate})
    if not gate.get("activation_allowed"):
        report = {
            "schema": "kpgs_smoke_poc_v2",
            "ts": _utc_now(),
            "verdict": "BLOCKED",
            "activation_allowed": False,
            "steps": steps,
            "message": gate.get("message"),
        }
        SMOKE_REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return report

    gov = compile_kpgs_governance(write_log=True)
    steps.append({"step": "governance_compile", "result": {"verdict": gov.get("verdict"), "summary": gov.get("summary")}})

    steward_result: dict[str, Any] | None = None
    if activate_steward:
        steward_result = run_steward_lane_activate(
            note="KPGS smoke PoC — activate KC Save|Watch + Cassy execute + Kopano Context GUI",
            action="[KPGS_SMOKE_POC] steward + sovereign sim activation",
            evidence="docs/swarm-ops/KPGS_ACTIVATION_GATE.json",
        )
        steps.append({"step": "steward_lane_activate", "result": steward_result})

    behavioral = run_kpgs_behavioral_poc(write_report=True)
    steps.append({"step": "behavioral_poc", "result": behavioral})

    sim_result: dict[str, Any] | None = None
    if bootstrap_sim and behavioral.get("verdict") == "PASS":
        sim_result = bootstrap_sovereign_sim(write_log=True)
        steps.append({"step": "sovereign_sim_bootstrap", "result": {"verdict": sim_result.get("verdict")}})

    meas = behavioral.get("measurand") or {}
    poc = validate_eco_poc(
        agent_id="cassy",
        claim="KPGS behavioral PoC: hood dispatch proceed/sever, context bleed classify, altar GUI channel, sim tick",
        model="Governance guides SWFUS dispatch; independent measurand is dispatch_proceed count from sim tick sample",
        relation="hood_dispatch_for_plot and dispatch_spawn_event receipts in KPGS_BEHAVIORAL_POC.json",
        baseline=str(meas.get("baseline", 0)),
        observed=str(meas.get("observed", 0)),
        unit=str(meas.get("unit", "dispatch_proceed")),
        instrument=str(meas.get("instrument", "sovereign_sim_tick")),
        evidence="docs/swarm-ops/KPGS_BEHAVIORAL_POC.json",
        exit_code=0 if behavioral.get("verdict") == "PASS" else 1,
        anticipated_delta="benign_gui_tokens_proceed_exfil_attempts_sever",
        livelihood_ids=["LIV-03"],
    )
    steps.append({"step": "eco_poc_validate", "result": poc})

    steward_ok = (steward_result or {}).get("verdict") == "ACTIVE"
    behavioral_ok = behavioral.get("verdict") == "PASS"
    sim_ok = (sim_result or {}).get("verdict") == "BOOTSTRAPPED" if sim_result else behavioral_ok
    poc_ok = poc.get("verdict") == "PASS" and behavioral_ok
    verdict = (
        "PASS"
        if steward_ok and behavioral_ok and sim_ok and poc_ok and gov.get("verdict") == "COMPILED"
        else "HOLD"
    )

    summary = (
        f"[KPGS_SMOKE_POC] verdict={verdict} | gate=ALLOW | gov={gov.get('verdict')} | "
        f"behavioral={behavioral.get('verdict')} | "
        f"steward={(steward_result or {}).get('verdict', 'skip')} | sim={(sim_result or {}).get('verdict', 'skip')} | "
        f"poc={poc.get('verdict')} | delta={meas.get('observed')} {meas.get('unit')}"
    )

    report = {
        "schema": "kpgs_smoke_poc_v2",
        "ts": _utc_now(),
        "verdict": verdict,
        "activation_allowed": True,
        "summary": summary,
        "steps": steps,
        "behavioral_measurand": meas,
        "ui_snapshot": sovereign_sim_ui_snapshot(),
        "report_path": _repo_rel(SMOKE_REPORT_PATH),
    }

    SMOKE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SMOKE_REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    _append_jsonl(
        MAIN_BRAIN_LOG,
        {
            "schema": "kc_main_brain_log_v1",
            "ts": _utc_now(),
            "kind": "kpgs_smoke_poc",
            "summary": summary,
            "exit_code": 0 if verdict == "PASS" else 1,
            "payload_ref": report["report_path"],
        },
    )
    return report


def sovereign_sim_status() -> dict[str, Any]:
    from .kpgs_activation_gate import load_cached_activation_gate

    gate = load_cached_activation_gate()
    world = load_world_state()
    return {
        "schema": "sovereign_sim_status_v1",
        "ts": _utc_now(),
        "activation_allowed": gate.get("activation_allowed"),
        "gate_verdict": gate.get("verdict"),
        "world_bootstrapped": world.get("bootstrapped", False),
        "world_verdict": world.get("verdict"),
        "agent_total": world.get("agent_total"),
        "regions_count": world.get("regions_count"),
        "ui": sovereign_sim_ui_snapshot(),
    }
