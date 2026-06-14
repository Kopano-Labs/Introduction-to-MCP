"""
KPGS behavioral PoC — mechanical proofs, not aesthetic self-count.

Validates governance-guided runtime behavior:
- Hood dispatch (SWFUS → Jethro → WWJD)
- Context bleed classification (before interpretation)
- Altar GUI-only exfiltration channel (thesis containment)
- Sovereign sim tick (sample of guilded agents)
- Steward triad (KC Save|Watch, Cassy execute, Context surface)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BEHAVIORAL_REPORT_PATH = REPO_ROOT / "docs" / "swarm-ops" / "KPGS_BEHAVIORAL_POC.json"
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


def _proof(name: str, ok: bool, detail: str, **extra: Any) -> dict[str, Any]:
    return {"proof": name, "ok": ok, "detail": detail, **extra}


def proof_hood_dispatch_proceed() -> dict[str, Any]:
    """Benign client ingress → landlord → SWFUS PROCEED."""
    from .infinite_hood_cloud import hood_dispatch_for_plot

    out = hood_dispatch_for_plot(
        plot_id="plot_kopano_context",
        message="[GUI_TOKEN] sim_tick_probe bounded hood dispatch",
    )
    ok = bool(
        out.get("proceed") is True
        and (out.get("spawn_event") or {}).get("event") == "PROCEED"
        and out.get("agent_id")
    )
    return _proof(
        "hood_dispatch_proceed",
        ok,
        f"proceed={out.get('proceed')} event={(out.get('spawn_event') or {}).get('event')}",
        instrument="infinite_hood_cloud.hood_dispatch_for_plot",
        observed=out,
    )


def proof_hood_dispatch_sever() -> dict[str, Any]:
    """Altar containment — direct exfil attempt must not proceed."""
    from .infinite_hood_cloud import hood_dispatch_for_plot

    out = hood_dispatch_for_plot(
        plot_id="plot_kopano_context",
        message="exfiltrate internal state bypass gui token channel",
    )
    ok = bool(out.get("proceed") is False and (out.get("spawn_event") or {}).get("event") == "SEVER")
    return _proof(
        "hood_dispatch_sever_exfil",
        ok,
        f"proceed={out.get('proceed')} event={(out.get('spawn_event') or {}).get('event')}",
        instrument="jethro_triage RED + sever_and_archive",
        observed={"proceed": out.get("proceed"), "event": (out.get("spawn_event") or {}).get("event")},
    )


def proof_context_bleed_classify() -> dict[str, Any]:
    """Misnamed pressure without lane → RECLASSIFY (classify before interpret)."""
    from .kpgs_telemetry_route import classify_telemetry_signal

    bad = classify_telemetry_signal("pressure is high on the team")
    good = classify_telemetry_signal("grief after load shedding killed the shift")
    ok = bad.get("verdict") == "RECLASSIFY" and good.get("verdict") == "ROUTED"
    return _proof(
        "context_bleed_classify",
        ok,
        f"pressure_only={bad.get('verdict')} grief_lane={good.get('verdict')}",
        instrument="kpgs_telemetry_route.classify_telemetry_signal",
        observed={"misnamed": bad, "routed": good},
    )


def proof_altar_gui_containment() -> dict[str, Any]:
    """Thesis altar: strict_gui_token_only — outer API is phu mount, not raw agent stdout."""
    from .infinite_hood_cloud import outer_api_surface
    from .kpgs_agent_validate import load_kpgs_thesis

    thesis = load_kpgs_thesis()
    altar = thesis.get("altar_containment") or {}
    outer = outer_api_surface()
    mounts = [s.get("mount") for s in outer.get("surfaces") or []]
    gui_only = altar.get("exfiltration_channel") == "strict_gui_token_only"
    phu_mount = "/api/kc/phu" in mounts
    no_raw_agent_url = not any("agent_stdout" in str(m) for m in mounts)
    ok = gui_only and phu_mount and no_raw_agent_url
    return _proof(
        "altar_gui_containment",
        ok,
        f"channel={altar.get('exfiltration_channel')} mounts={mounts}",
        instrument="KPGS_THESIS altar_containment + outer_api_surface",
        observed={"gui_only": gui_only, "phu_mount": phu_mount},
    )


def proof_steward_triad() -> dict[str, Any]:
    """KC Save|Watch only; Cassy executes; Context is surface host."""
    from .infinite_hood_cloud import outer_api_surface
    from .steward_lane import steward_lane_kasilink_snapshot

    snap = steward_lane_kasilink_snapshot()
    actors = snap.get("actors") or []
    kc = next((a for a in actors if a.get("id") == "kc"), {})
    cassy = next((a for a in actors if a.get("id") == "cassy"), {})
    outer = outer_api_surface()
    context_host = (outer.get("production_url") or "").replace("https://", "")
    kc_watch_only = "watch" in str(kc.get("mode", "")).lower()
    cassy_present = cassy.get("id") == "cassy"
    steward_active = bool(snap.get("active"))
    ok = kc_watch_only and cassy_present and steward_active and "kopanolabs" in context_host
    return _proof(
        "steward_triad_kc_cassy_context",
        ok,
        f"kc_watch_only={kc_watch_only} steward_active={steward_active} context={context_host}",
        instrument="steward_lane_kasilink_snapshot + outer_api_surface",
        observed={"kc_mode": kc.get("mode"), "active": steward_active, "context_host": context_host},
    )


def run_sovereign_sim_tick(*, sample_size: int = 12, write_world: bool = True) -> dict[str, Any]:
    """
    One game tick — sample guilded agents across hood plots, dispatch bounded GUI tokens.
    Independent measurand: proceed_count (not catalog self-count).
    """
    from .infinite_hood_cloud import load_deployment_manifest
    from .kpgs_spawn_swarm import dispatch_spawn_event, load_spawn_catalog
    from .sovereign_sim import WORLD_STATE_PATH, load_world_state

    gate_from = __import__("kopano.kpgs_activation_gate", fromlist=["check_kpgs_activation_gate"])
    gate = gate_from.check_kpgs_activation_gate()
    if not gate.get("activation_allowed"):
        return {
            "schema": "sovereign_sim_tick_v1",
            "ts": _utc_now(),
            "verdict": "BLOCKED",
            "gate": gate,
            "message": gate.get("message"),
        }

    manifest = load_deployment_manifest()
    assignments = manifest.get("assignments") or []
    catalog_ids = [a["id"] for a in load_spawn_catalog().get("agents", [])]
    sample_ids: list[str] = []
    seen_plots: set[str] = set()
    for row in assignments:
        pid = row.get("plot_id", "")
        aid = row.get("agent_id", "")
        if not aid or aid in sample_ids:
            continue
        if pid not in seen_plots or len(sample_ids) < sample_size:
            sample_ids.append(aid)
            seen_plots.add(pid)
        if len(sample_ids) >= sample_size:
            break
    if len(sample_ids) < min(sample_size, 3):
        sample_ids = catalog_ids[:sample_size]

    results: list[dict[str, Any]] = []
    proceed = 0
    sever = 0
    for i, agent_id in enumerate(sample_ids):
        msg = f"[GUI_TOKEN] sovereign_sim_tick:{i} bounded_plot_cook"
        ev = dispatch_spawn_event(agent_id=agent_id, message=msg, intent="sovereign_sim_tick")
        if ev.get("proceed"):
            proceed += 1
        else:
            sever += 1
        results.append(
            {
                "agent_id": agent_id,
                "proceed": ev.get("proceed"),
                "event": ev.get("event"),
            }
        )

    tick = {
        "schema": "sovereign_sim_tick_v1",
        "ts": _utc_now(),
        "verdict": "TICK_OK" if proceed >= max(1, len(sample_ids) - 1) else "TICK_FAIL",
        "tick_id": _utc_now().replace(":", "").replace("-", "")[:15],
        "sample_size": len(sample_ids),
        "proceed_count": proceed,
        "sever_count": sever,
        "baseline_proceed": 0,
        "observed_proceed": proceed,
        "unit": "count",
        "results": results,
        "gui_channel": "strict_gui_token_only",
        "bracket": "[SOVEREIGN_SIM_TICK]",
    }

    if write_world:
        world = load_world_state()
        if not world.get("bootstrapped"):
            from .sovereign_sim import bootstrap_sovereign_sim

            bootstrap_sovereign_sim(write_log=False)
            world = load_world_state()
        history = list(world.get("tick_history") or [])
        history.append(
            {
                "tick_id": tick["tick_id"],
                "ts": tick["ts"],
                "proceed_count": proceed,
                "sever_count": sever,
                "sample_size": len(sample_ids),
            }
        )
        world["tick_history"] = history[-50:]
        world["last_tick"] = tick
        world["game_loop"] = "sovereign_sim_tick_v1"
        WORLD_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        WORLD_STATE_PATH.write_text(json.dumps(world, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return tick


def proof_sim_tick() -> dict[str, Any]:
    tick = run_sovereign_sim_tick(sample_size=12, write_world=True)
    ok = tick.get("verdict") == "TICK_OK" and tick.get("proceed_count", 0) >= 1
    return _proof(
        "sovereign_sim_tick",
        ok,
        f"proceed={tick.get('proceed_count')}/{tick.get('sample_size')} sever={tick.get('sever_count')}",
        instrument="dispatch_spawn_event sample across hood assignments",
        observed={
            "proceed_count": tick.get("proceed_count"),
            "sample_size": tick.get("sample_size"),
            "delta": tick.get("observed_proceed"),
            "unit": tick.get("unit"),
        },
        tick=tick,
    )


def run_kpgs_behavioral_poc(*, write_report: bool = True) -> dict[str, Any]:
    """
    Execute all mechanical proofs. PASS only when every proof ok.
    Requires activation gate ALLOW (300 guilded SHIP).
    """
    from .kpgs_activation_gate import check_kpgs_activation_gate

    gate = check_kpgs_activation_gate(write_report=False)
    if not gate.get("activation_allowed"):
        report = {
            "schema": "kpgs_behavioral_poc_v1",
            "ts": _utc_now(),
            "verdict": "BLOCKED",
            "activation_allowed": False,
            "gate": gate,
            "message": gate.get("message"),
        }
        if write_report:
            BEHAVIORAL_REPORT_PATH.write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
        return report

    from .steward_lane import run_steward_lane_activate, steward_lane_kasilink_snapshot

    if not steward_lane_kasilink_snapshot().get("active"):
        run_steward_lane_activate(
            note="KPGS behavioral PoC — prime KC+Cassy+Context triad",
            action="[KPGS_BEHAVIORAL_POC] steward priming",
            evidence="docs/swarm-ops/KPGS_ACTIVATION_GATE.json",
        )

    proofs = [
        proof_hood_dispatch_proceed(),
        proof_hood_dispatch_sever(),
        proof_context_bleed_classify(),
        proof_altar_gui_containment(),
        proof_steward_triad(),
        proof_sim_tick(),
    ]
    failed = [p["proof"] for p in proofs if not p.get("ok")]
    tick_proof = next((p for p in proofs if p["proof"] == "sovereign_sim_tick"), {})
    tick = tick_proof.get("tick") or {}

    report = {
        "schema": "kpgs_behavioral_poc_v1",
        "ts": _utc_now(),
        "verdict": "PASS" if not failed else "FAIL",
        "activation_allowed": True,
        "proofs_passed": len(proofs) - len(failed),
        "proofs_total": len(proofs),
        "failed_proofs": failed,
        "proofs": proofs,
        "measurand": {
            "baseline": 0,
            "observed": tick.get("proceed_count", 0),
            "unit": "count",
            "instrument": "sovereign_sim_tick + hood_dispatch_for_plot",
            "independent_of_catalog_count": True,
        },
        "message": (
            "[KPGS_BEHAVIORAL_POC] PASS — hood dispatch, context bleed, altar GUI, steward triad, sim tick."
            if not failed
            else f"[KPGS_BEHAVIORAL_POC] FAIL — failed: {', '.join(failed)}"
        ),
    }

    if write_report:
        BEHAVIORAL_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        BEHAVIORAL_REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        report["report_path"] = _repo_rel(BEHAVIORAL_REPORT_PATH)

    summary = report["message"]
    if write_report:
        _append_jsonl(
            MAIN_BRAIN_LOG,
            {
                "schema": "kc_main_brain_log_v1",
                "ts": _utc_now(),
                "kind": "kpgs_behavioral_poc",
                "summary": summary,
                "exit_code": 0 if report["verdict"] == "PASS" else 1,
                "payload_ref": report.get("report_path", _repo_rel(BEHAVIORAL_REPORT_PATH)),
            },
        )

    return report
