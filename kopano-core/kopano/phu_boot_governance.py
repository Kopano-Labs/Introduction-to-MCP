"""
KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1 — agent governance layer.

Seeds: Structure/07-Agents/
KC: teacher_review Save | Watch only (no execute, no Kill auto).
Cassy: student-teacher apprenticeship.
BlackMask: required for mesh agents before operating claims.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / "Structure" / "07-Agents"
BOOT_PATH = AGENTS_DIR / "KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1.json"
STATE_PATH = REPO_ROOT / "kopano-core" / ".kc" / "phu_boot_v1.json"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"

_KC_VERDICT_RE = re.compile(r"^\s*(Save|Watch)\b", re.I)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_boot() -> dict[str, Any]:
    return _load_json(BOOT_PATH)


def load_role_bindings() -> dict[str, Any]:
    return _load_json(AGENTS_DIR / "ROLE_BINDINGS.json")


def load_agent_mesh() -> dict[str, Any]:
    return _load_json(AGENTS_DIR / "AGENT_MESH.json")


def load_promotion_law() -> dict[str, Any]:
    return _load_json(AGENTS_DIR / "PROMOTION_LAW.json")


def load_blackmask_gate() -> dict[str, Any]:
    return _load_json(AGENTS_DIR / "BLACKMASK_GATE.json")


def mesh_agent_ids() -> list[str]:
    """All agents that require BlackMask in boot mesh."""
    mesh = load_agent_mesh()
    ids: list[str] = []
    for dept in (mesh.get("department_students") or {}).values():
        ids.extend(dept.get("agents") or [])
    ids.extend(mesh.get("mesh_workers") or [])
    ids.extend(mesh.get("mesh_llm") or [])
    ids.extend(mesh.get("mesh_operator") or [])
    ow = mesh.get("orchestrator") or {}
    if "mirror_warden" in ow:
        ids.append("mirror_warden")
    # governance teachers validate but cassey/operational_general already in teachers — drill them too
    ids.extend(["cassey", "operational_general"])
    seen: set[str] = set()
    out: list[str] = []
    for aid in ids:
        if aid not in seen and aid != "kc":
            seen.add(aid)
            out.append(aid)
    return out


def validate_kc_teacher_review(verdict: str) -> dict[str, Any]:
    """KC may only store Save or Watch (leading token)."""
    bindings = load_role_bindings()
    allowed = bindings["bindings"]["kc"]["teacher_review_verdicts"]
    text = (verdict or "").strip()
    match = _KC_VERDICT_RE.match(text)
    token = match.group(1).capitalize() if match else None
    ok = token in allowed
    return {
        "valid": ok,
        "normalized": token,
        "allowed": allowed,
        "forbidden": bindings["bindings"]["kc"].get("teacher_review_forbidden", []),
    }


def tsap_to_kc_opinion(approve: bool, teacher_note: str = "") -> str:
    """Map TSAP teacher verdict to KC ledger opinion."""
    base = "Save" if approve else "Watch"
    note = (teacher_note or "").strip()
    return f"{base} — {note}" if note else base


def record_kc_teacher_review(
    *,
    opinion: str,
    ref: str,
    department: str = "",
) -> dict[str, Any]:
    """Persist KC opinion (Save|Watch only)."""
    check = validate_kc_teacher_review(opinion)
    if not check["valid"]:
        return {
            "error": "kc_teacher_review_forbidden",
            "allowed": check["allowed"],
            "received": opinion[:120],
        }
    row = {
        "ts": _utc_now(),
        "schema": "kc_teacher_review_v1",
        "opinion": opinion,
        "verdict_token": check["normalized"],
        "ref": ref,
        "department": department,
        "boot": "KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1",
    }
    state = _load_boot_state()
    opinions = state.setdefault("kc_opinions", [])
    opinions.append(row)
    state["last_kc_opinion"] = row
    _save_boot_state(state)
    return {"stored": True, **row}


def _load_boot_state() -> dict[str, Any]:
    if not STATE_PATH.is_file():
        return {"schema": "phu_boot_v1_state", "boot": "KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1"}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"schema": "phu_boot_v1_state", "boot": "KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1"}


def _save_boot_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _append_main_brain(summary: str, kind: str) -> None:
    MAIN_BRAIN_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "schema": "kc_main_brain_log_v1",
        "ts": _utc_now(),
        "kind": kind,
        "summary": summary,
    }
    with MAIN_BRAIN_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def blackmask_dry_run(*, agent_ids: list[str] | None = None) -> dict[str, Any]:
    """Simulate BlackMask for mesh agents — no state mutation in phu_apprenticeship."""
    from .phu_apprenticeship import load_black_mask_doctrine

    doctrine = load_black_mask_doctrine()
    commandments = doctrine.get("commandments", [])
    pillars = doctrine.get("pillars", [])
    targets = agent_ids or mesh_agent_ids()
    results: list[dict[str, Any]] = []

    for aid in targets:
        cmd_pass = len(commandments)
        pil_pass = len(pillars)
        verdict = "SHIP"
        summary = (
            f"[BLACK_MASK_DRILL_DRY] timestamp: {_utc_now()} | ecosystem: Kopano-Phu | "
            f"agent: {aid} | commandments_pass: {cmd_pass}/{len(commandments)} | "
            f"pillars_pass: {pil_pass}/{len(pillars)} | verdict: {verdict} | dry_run: true"
        )
        results.append(
            {
                "agent_id": aid,
                "verdict": verdict,
                "commandments_pass": cmd_pass,
                "pillars_pass": pil_pass,
                "summary": summary,
            }
        )

    ship = sum(1 for r in results if r["verdict"] == "SHIP")
    hold = len(results) - ship
    payload = {
        "schema": "blackmask_dry_run_v1",
        "boot": "KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1",
        "dry_run": True,
        "agents_total": len(results),
        "ship": ship,
        "hold": hold,
        "all_ship": hold == 0,
        "results": results,
    }
    state = _load_boot_state()
    state["last_blackmask_dry_run"] = {
        "at": _utc_now(),
        "ship": ship,
        "hold": hold,
        "agents_total": len(results),
    }
    _save_boot_state(state)
    _append_main_brain(
        f"[KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1] BlackMask dry run | "
        f"agents: {len(results)} | SHIP: {ship} | HOLD: {hold}",
        "blackmask_dry_run",
    )
    return payload


def promotion_allowed(agent_id: str) -> dict[str, Any]:
    """Check promotion law — no promotion without proof."""
    law = load_promotion_law()
    state_path = REPO_ROOT / "kopano-core" / ".kc" / "phu_apprenticeship.json"
    agent_state: dict[str, Any] = {}
    if state_path.is_file():
        try:
            st = json.loads(state_path.read_text(encoding="utf-8"))
            agent_state = (st.get("agents") or {}).get(agent_id) or {}
        except (json.JSONDecodeError, OSError):
            pass

    bm = agent_state.get("black_mask") or {}
    om_entry: dict[str, Any] = {}
    try:
        from .operating_mesh import _load_state as load_operating_mesh

        om_entry = (load_operating_mesh().get("flagships") or {}).get(agent_id) or {}
    except ImportError:
        pass

    teacher_ok = (
        agent_state.get("last_teacher_verdict") == "APPROVE"
        or om_entry.get("teacher_verdict") == "APPROVE"
    )
    receipt_ok = (
        om_entry.get("proofs", {}).get("PROOF-03_receipt") is True
        or om_entry.get("poc_verdict") == "PASS"
    )
    operating_ok = (
        agent_state.get("promotion_state") == "operating"
        or om_entry.get("status") == "operating"
        or agent_state.get("status") == "active"
    )
    checks = {
        "blackmask_ship": bm.get("verdict") == "SHIP" or om_entry.get("blackmask_verdict") == "SHIP",
        "teacher_approve": teacher_ok,
        "receipt": receipt_ok,
        "operating_flag": operating_ok,
    }
    allowed = all(checks.values())
    return {
        "agent_id": agent_id,
        "promotion_allowed": allowed,
        "law": law.get("law"),
        "checks": checks,
        "operating_mesh": om_entry.get("status"),
        "note": "Drill is not graduation — verified production is a separate bar.",
    }


def mesh_summary() -> dict[str, Any]:
    mesh = load_agent_mesh()
    bindings = load_role_bindings()
    return {
        "schema": "agent_mesh_summary_v1",
        "boot": "KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1",
        "governance_core": mesh.get("governance_core"),
        "cassy_binding": bindings["bindings"]["cassy"],
        "kc_binding": bindings["bindings"]["kc"],
        "mao_binding": bindings["bindings"]["mao"],
        "department_students": mesh.get("department_students"),
        "mesh_workers": mesh.get("mesh_workers"),
        "mesh_llm": mesh.get("mesh_llm"),
        "blackmask_agent_count": len(mesh_agent_ids()),
        "catalog_200_auto_operating": mesh.get("catalog_200", {}).get("auto_operating", False),
    }


def boot_status() -> dict[str, Any]:
    kpgs: dict[str, Any] = {}
    try:
        from .kpgs_governance import governance_status

        kpgs = governance_status()
    except ImportError:
        kpgs = {"error": "kpgs_governance_unavailable"}

    return {
        "boot": load_boot(),
        "role_bindings": load_role_bindings(),
        "promotion_law": load_promotion_law(),
        "mesh_summary": mesh_summary(),
        "runtime_state": _load_boot_state(),
        "seeds_dir": str(AGENTS_DIR.relative_to(REPO_ROOT)),
        "kpgs_governance": kpgs,
        "main_brain_authority": "Schematics",
        "main_brain_registry": "Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/MAIN-BRAIN/KPGS_GOVERNANCE_CORE.json",
    }


def apply_boot() -> dict[str, Any]:
    """Mark boot applied — governance layer active."""
    state = _load_boot_state()
    state["applied_at"] = _utc_now()
    state["active"] = True
    _save_boot_state(state)
    summary = (
        f"[KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1] applied | "
        f"KC: Save|Watch only | Cassy: student-teacher | "
        f"mesh_agents: {len(mesh_agent_ids())}"
    )
    _append_main_brain(summary, "kopano_phu_boot_v1")
    return {"applied": True, "summary": summary, "mesh_agents": len(mesh_agent_ids())}
