"""
KPGS governance orchestrator — Schematics MAIN BRAIN authority bridge.

Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/MAIN-BRAIN/KPGS_GOVERNANCE_CORE.json
is the governance registry; this module compiles doctrine and propagates gates
across boot, apprenticeship, LD-LPM, operating mesh, and API surfaces.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMATICS_ROOT = REPO_ROOT / "Schematics"
MAIN_BRAIN_GOVERNANCE_JSON = (
    SCHEMATICS_ROOT
    / "21-KOPANO-PHU GOVERNACE SYSTEMS"
    / "MAIN-BRAIN"
    / "KPGS_GOVERNANCE_CORE.json"
)
SCHEMATICS_COMMS_LOG = SCHEMATICS_ROOT / "04-Updates" / "comms-log.md"
RUNTIME_MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_main_brain_governance() -> dict[str, Any]:
    """Load Schematics MAIN BRAIN governance registry."""
    if not MAIN_BRAIN_GOVERNANCE_JSON.is_file():
        return {
            "schema": "kpgs_main_brain_governance_v1",
            "error": "main_brain_registry_missing",
            "expected": str(MAIN_BRAIN_GOVERNANCE_JSON.relative_to(REPO_ROOT)),
        }
    return json.loads(MAIN_BRAIN_GOVERNANCE_JSON.read_text(encoding="utf-8"))


def classify_submission(*, action: str, evidence: str) -> dict[str, Any]:
    """Classify student/LD submission text before interpretation."""
    from .kpgs_telemetry_route import classify_telemetry_signal

    combined = f"{action or ''} | {evidence or ''}".strip()
    classification = classify_telemetry_signal(combined)
    registry = load_main_brain_governance()
    strict = bool((registry.get("gates") or {}).get("ld_lpm_tranche_strict", False))
    blocked = classification.get("verdict") == "RECLASSIFY" and strict
    return {
        "schema": "kpgs_submission_telemetry_v1",
        "ts": _utc_now(),
        "classification": classification,
        "combined_preview": combined[:240],
        "strict_mode": strict,
        "blocked": blocked,
        "gate": "RECLASSIFY" if classification.get("verdict") == "RECLASSIFY" else "PASS",
    }


def telemetry_gate_allows(*, action: str, evidence: str) -> tuple[bool, dict[str, Any]]:
    """Return (allowed, routing_payload). Blocks only when strict + RECLASSIFY."""
    routing = classify_submission(action=action, evidence=evidence)
    return not routing.get("blocked"), routing


def compile_kpgs_governance(*, write_log: bool = True) -> dict[str, Any]:
    """Compile full KPGS governance stack anchored to Schematics MAIN BRAIN."""
    from .kpgs_agent_validate import compile_kpgs_thesis, validate_kpgs_mesh
    from .kpgs_telemetry_route import compile_black_beast_thesis

    registry = load_main_brain_governance()
    thesis = compile_kpgs_thesis(write_log=False)
    beast = compile_black_beast_thesis(write_log=False)
    mesh = validate_kpgs_mesh(write_report=False)

    errors: list[str] = []
    if registry.get("error"):
        errors.append(str(registry["error"]))
    if thesis.get("verdict") != "COMPILED":
        errors.extend(thesis.get("errors") or ["thesis not compiled"])
    if beast.get("verdict") != "COMPILED":
        errors.extend(beast.get("errors") or ["black beast not compiled"])
    if mesh.get("verdict") != "PASS":
        errors.append(
            f"mesh poc: {mesh.get('ship', 0)} SHIP / {mesh.get('reject', 0)} REJECT"
        )

    from .kpgs_spawn_swarm import compile_spawn_swarm

    spawn = compile_spawn_swarm(write_log=False)
    if spawn.get("verdict") != "COMPILED":
        sv = spawn.get("spawn_validation") or {}
        errors.append(
            f"spawn swarm: {sv.get('ship', 0)} SHIP / {sv.get('hold', 0)} HOLD "
            f"of {sv.get('agents_total', 0)}"
        )

    verdict = "COMPILED" if not errors else "INCOMPLETE"
    summary = (
        f"[KPGS_MAIN_BRAIN] authority: Schematics | verdict: {verdict} | "
        f"thesis: {thesis.get('verdict')} | beast: {beast.get('verdict')} | "
        f"mesh: {mesh.get('verdict')} ({mesh.get('ship', 0)}/{mesh.get('agents_total', 0)} SHIP) | "
        f"spawn: {spawn.get('verdict')} ({(spawn.get('spawn_validation') or {}).get('ship', 0)}/300 SHIP)"
    )
    out = {
        "schema": "kpgs_governance_compile_v1",
        "ts": _utc_now(),
        "authority": registry.get("authority", "Schematics MAIN BRAIN"),
        "registry_path": str(MAIN_BRAIN_GOVERNANCE_JSON.relative_to(REPO_ROOT)),
        "verdict": verdict,
        "errors": errors,
        "thesis": thesis,
        "black_beast": beast,
        "mesh": {
            "overall": mesh.get("verdict"),
            "ship": mesh.get("ship"),
            "hold": mesh.get("hold"),
            "reject": mesh.get("reject"),
            "agents_total": mesh.get("agents_total"),
        },
        "spawn_swarm": {
            "verdict": spawn.get("verdict"),
            "ship": (spawn.get("spawn_validation") or {}).get("ship"),
            "agents_total": (spawn.get("spawn_validation") or {}).get("agents_total"),
            "hood_objective": spawn.get("hood_objective"),
        },
        "doctrine_stack": registry.get("doctrine_stack"),
        "summary": summary,
    }
    if write_log and verdict == "COMPILED":
        _append_jsonl(
            RUNTIME_MAIN_BRAIN_LOG,
            {
                "schema": "kc_main_brain_log_v1",
                "ts": _utc_now(),
                "kind": "kpgs_governance_compile",
                "summary": summary,
                "exit_code": 0,
                "payload_ref": str(MAIN_BRAIN_GOVERNANCE_JSON.relative_to(REPO_ROOT)),
            },
        )
        append_schematics_comms(
            title="KPGS MAIN BRAIN governance compile — COMPILED",
            body=summary,
        )
    return out


def governance_status() -> dict[str, Any]:
    """Full governance status for boot API / steward / graduation surfaces."""
    registry = load_main_brain_governance()
    compiled = compile_kpgs_governance(write_log=False)
    from .kpgs_renter_entry import load_renter_entryway

    entryway = load_renter_entryway()
    from .kpgs_spawn_swarm import spawn_swarm_status

    spawn_status = spawn_swarm_status()
    return {
        "schema": "kpgs_governance_status_v1",
        "ts": _utc_now(),
        "authority": registry.get("authority", "Schematics MAIN BRAIN"),
        "registry_present": "error" not in registry,
        "registry_path": str(MAIN_BRAIN_GOVERNANCE_JSON.relative_to(REPO_ROOT)),
        "renter_entryway": {
            "document_id": entryway.get("document_id"),
            "bracket": entryway.get("bracket"),
            "you_are": (entryway.get("paradigm") or {}).get("you_are"),
            "hood": (entryway.get("you_are_fucking_with") or {}).get("hood"),
            "entryway_path": entryway.get("_source"),
        },
        "compile_verdict": compiled.get("verdict"),
        "thesis_verdict": (compiled.get("thesis") or {}).get("verdict"),
        "black_beast_verdict": (compiled.get("black_beast") or {}).get("verdict"),
        "mesh_overall": (compiled.get("mesh") or {}).get("overall"),
        "mesh_ship": (compiled.get("mesh") or {}).get("ship"),
        "mesh_total": (compiled.get("mesh") or {}).get("agents_total"),
        "gates": registry.get("gates"),
        "sectors": registry.get("sectors"),
        "one_line": registry.get("one_line"),
        "summary": compiled.get("summary"),
        "spawn_swarm": spawn_status,
    }


def append_schematics_comms(*, title: str, body: str) -> None:
    """Append a dated entry to Schematics comms-log (MAIN BRAIN human ledger)."""
    if not SCHEMATICS_COMMS_LOG.parent.is_dir():
        return
    stamp = _utc_now()[:10]
    block = f"\n---\n\n## {stamp} — {title}\n\n{body}\n"
    try:
        existing = SCHEMATICS_COMMS_LOG.read_text(encoding="utf-8") if SCHEMATICS_COMMS_LOG.is_file() else ""
        SCHEMATICS_COMMS_LOG.write_text(block + existing, encoding="utf-8")
    except OSError:
        pass


def propagate_governance_marker(*, operator: str = "kc_kpgs_governance") -> dict[str, Any]:
    """Mark governance propagation — compile + comms + return status."""
    compiled = compile_kpgs_governance(write_log=True)
    status = governance_status()
    append_schematics_comms(
        title="[KPGS_MAIN_BRAIN] governance propagated to runtime stack",
        body=(
            f"**Operator:** `{operator}`\n\n"
            f"**Compile:** {compiled.get('verdict')}\n\n"
            f"**Mesh:** {(compiled.get('mesh') or {}).get('overall')} "
            f"({(compiled.get('mesh') or {}).get('ship')}/"
            f"{(compiled.get('mesh') or {}).get('agents_total')} SHIP)\n\n"
            f"**Registry:** `{MAIN_BRAIN_GOVERNANCE_JSON.relative_to(REPO_ROOT)}`"
        ),
    )
    return {"propagated": True, "compile": compiled, "status": status}
