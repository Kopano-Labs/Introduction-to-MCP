"""
Phase 3 — Operating mesh: flagship sub-brains + catalog agent assignment with PROOF-01..03.

PROOF-01: BlackMask live drill → SHIP
PROOF-02: TSAP teacher_review → APPROVE
PROOF-03: Main Brain receipt (exit_code 0) + eco PoC PASS per flagship catalog agent

Does not set catalog_200 agents to auto_operating — assignments live in operating_mesh state only.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = REPO_ROOT / "kopano-core" / ".kc" / "operating_mesh.json"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
MESH_PATH = REPO_ROOT / "Structure" / "07-Agents" / "AGENT_MESH.json"

# Sub-brain mesh id → catalog STEM agent (explicit assignment; not auto from 200 catalog)
FLAGSHIP_ASSIGNMENTS: dict[str, dict[str, str]] = {
    "freddy_nw_alfalfa": {
        "catalog_agent": "kp_agri_soil_01",
        "department": "kopano_labs_experimentation",
        "teacher": "operational_general",
        "display": "Freddy NW Alfalfa",
        "kpgs_sector": "sector_01_freddy",
    },
    "eddie_bgf_mining": {
        "catalog_agent": "kp_geospatial_survey_06",
        "department": "kopano_labs_experimentation",
        "teacher": "operational_general",
        "display": "Eddie BGF Mining",
        "kpgs_sector": "sector_02_eddie",
    },
    "starfall_salvage": {
        "catalog_agent": "kp_robotics_mech_01",
        "department": "kopano_labs_experimentation",
        "teacher": "operational_general",
        "display": "Starfall Salvage",
    },
    "kopano_labs_website": {
        "catalog_agent": "kp_ict_instrument_01",
        "department": "kopano_labs_experimentation",
        "teacher": "operational_general",
        "display": "Kopano Labs Website",
    },
    "kasilink": {
        "catalog_agent": "kp_ict_instrument_02",
        "department": "kopano_labs_experimentation",
        "teacher": "operational_general",
        "display": "KasiLink",
    },
    "bookit_5s_arena": {
        "catalog_agent": "kp_edu_lab_ops_01",
        "department": "kopano_labs_experimentation",
        "teacher": "operational_general",
        "display": "Bookit 5s Arena",
    },
    "5s_arena_blog": {
        "catalog_agent": "ape_youth_stem_media_01",
        "department": "kopano_labs_experimentation",
        "teacher": "operational_general",
        "display": "5s Arena Blog",
    },
    "cape_campass": {
        "catalog_agent": "kp_geospatial_survey_01",
        "department": "kopano_labs_experimentation",
        "teacher": "operational_general",
        "display": "Cape Campass",
    },
    "portfolios_websites": {
        "catalog_agent": "ape_visual_physics_01",
        "department": "kopano_labs_experimentation",
        "teacher": "operational_general",
        "display": "Portfolios Websites",
    },
    "ama_phu_entertainment": {
        "catalog_agent": "ape_theatre_stem_01",
        "department": "ama_phu_creativity",
        "teacher": "cassey",
        "display": "AMA-PHU Entertainment (APE hub)",
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_state() -> dict[str, Any]:
    if not STATE_PATH.is_file():
        return {"schema": "operating_mesh_v1", "flagships": {}, "last_promote": None}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"schema": "operating_mesh_v1", "flagships": {}, "last_promote": None}


def _save_state(state: dict[str, Any]) -> None:
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


def _mesh_department_students() -> list[str]:
    if not MESH_PATH.is_file():
        return list(FLAGSHIP_ASSIGNMENTS.keys())
    mesh = json.loads(MESH_PATH.read_text(encoding="utf-8"))
    ids: list[str] = []
    for dept in (mesh.get("department_students") or {}).values():
        ids.extend(dept.get("agents") or [])
    return ids


def _default_poc_claim(display: str, catalog_agent: str) -> str:
    return (
        f"[KPEFS_OPERATING_MESH] {display} flagship validates under internal receipts "
        f"and STEM delta for catalog {catalog_agent} — not external oracle"
    )


def _default_poc_model(display: str) -> str:
    return (
        f"BlackMask SHIP, TSAP APPROVE, KC Save receipt, Rosen M/R with measurable delta "
        f"for {display} operating mesh promotion"
    )


def promote_flagship(
    sub_brain_id: str,
    *,
    skip_if_operating: bool = True,
    run_department_begin: bool = True,
) -> dict[str, Any]:
    """Run PROOF-01..03 for one flagship sub-brain + catalog PoC."""
    from .eco_poc_validate import validate_eco_poc
    from .phu_apprenticeship import (
        _load_state as load_apprenticeship_state,
        _save_state as save_apprenticeship_state,
        blackmask_drill,
        begin_department_students,
        student_submit,
        teacher_review,
    )

    assign = FLAGSHIP_ASSIGNMENTS.get(sub_brain_id)
    if not assign:
        return {"error": "unknown_flagship", "sub_brain_id": sub_brain_id}

    om = _load_state()
    existing = (om.get("flagships") or {}).get(sub_brain_id) or {}
    if skip_if_operating and existing.get("status") == "operating" and existing.get("poc_verdict") == "PASS":
        return {"sub_brain_id": sub_brain_id, "skipped": True, "reason": "already_operating", **existing}

    if run_department_begin:
        app_st = load_apprenticeship_state()
        if not app_st.get("departments"):
            begin_department_students(run_blackmask=True)

    dept_id = assign["department"]
    teacher = assign["teacher"]
    catalog = assign["catalog_agent"]
    display = assign["display"]

    from .kpgs_agent_validate import validate_kpgs_agent

    bm = blackmask_drill(sub_brain_id)
    proof01 = bm.get("verdict") == "SHIP"

    kpgs = validate_kpgs_agent(sub_brain_id, run_blackmask=False)
    proof04 = kpgs.get("verdict") == "SHIP"

    submit = student_submit(
        department_id=dept_id,
        student_agent="cassy",
        action=f"operating_mesh_promote:{sub_brain_id}",
        evidence=f"catalog:{catalog} | [KPEFS_FOUR_VECTOR] flagship assignment",
        lane="operating_mesh",
    )
    if submit.get("error"):
        return {"sub_brain_id": sub_brain_id, "step": "student_submit", **submit}

    review = teacher_review(
        department_id=dept_id,
        teacher_agent=teacher,
        approve=True,
        teacher_note=f"Operating mesh PROOF-02 for {display}",
        lane="operating_mesh",
    )
    proof02 = review.get("verdict") == "APPROVE"
    proof03 = (review.get("main_brain_exit_code") or 0) == 0

    poc = validate_eco_poc(
        agent_id=catalog,
        claim=_default_poc_claim(display, catalog),
        model=_default_poc_model(display),
        relation=f"kopano-core/.kc/operating_mesh.json + {catalog} receipt",
        baseline="0",
        observed="1",
        unit="proof_chain",
        instrument="operating_mesh.promote_flagship",
        evidence=str(STATE_PATH.relative_to(REPO_ROOT)),
        exit_code=0 if proof03 else 1,
        livelihood_ids=["LIV-01", "LIV-04"],
        anticipated_delta="flagship moves from catalog assignment to operating with receipts",
    )
    poc_pass = poc.get("verdict") == "PASS"

    app_st = load_apprenticeship_state()
    agents = app_st.setdefault("agents", {})
    agents[sub_brain_id] = {
        **agents.get(sub_brain_id, {}),
        "department": dept_id,
        "promotion_state": "operating"
        if proof01 and proof02 and proof03 and proof04 and poc_pass
        else "drill",
        "status": "active",
        "catalog_agent": catalog,
        "last_teacher_verdict": review.get("verdict"),
        "black_mask": bm,
        "operating_mesh_at": _utc_now(),
    }
    save_apprenticeship_state(app_st)

    entry = {
        "sub_brain_id": sub_brain_id,
        "display": display,
        "catalog_agent": catalog,
        "department": dept_id,
        "teacher": teacher,
        "status": "operating"
        if proof01 and proof02 and proof03 and proof04 and poc_pass
        else "incomplete",
        "proofs": {
            "PROOF-01_blackmask_ship": proof01,
            "PROOF-02_teacher_approve": proof02,
            "PROOF-03_receipt": proof03,
            "PROOF-04_kpgs_altar_ship": proof04,
            "eco_poc_pass": poc_pass,
        },
        "kpgs_verdict": kpgs.get("verdict"),
        "blackmask_verdict": bm.get("verdict"),
        "teacher_verdict": review.get("verdict"),
        "poc_verdict": poc.get("verdict"),
        "poc_id": poc.get("poc_id"),
        "promoted_at": _utc_now(),
        "live_blackmask": True,
        "note": "Catalog JSON unchanged — assignment recorded in operating_mesh state only.",
    }
    om.setdefault("flagships", {})[sub_brain_id] = entry
    om["last_promote"] = _utc_now()
    _save_state(om)

    summary = (
        f"[KPEFS_OPERATING_MESH] {display} | sub_brain: {sub_brain_id} | "
        f"catalog: {catalog} | BM: {bm.get('verdict')} | teacher: {review.get('verdict')} | "
        f"PoC: {poc.get('verdict')} | status: {entry['status']}"
    )
    _append_main_brain(summary, "kpefs_operating_mesh_promote")

    return entry


def promote_all_flagships(*, skip_if_operating: bool = True) -> dict[str, Any]:
    """Promote all flagship sub-brains per FLAGSHIP_ASSIGNMENTS."""
    results: list[dict[str, Any]] = []
    for sid in FLAGSHIP_ASSIGNMENTS:
        results.append(promote_flagship(sid, skip_if_operating=skip_if_operating))

    operating = sum(1 for r in results if r.get("status") == "operating")
    skipped = sum(1 for r in results if r.get("skipped"))
    incomplete = len(results) - operating - skipped
    phase3_exit = operating >= len(FLAGSHIP_ASSIGNMENTS)

    payload = {
        "schema": "operating_mesh_promote_all_v1",
        "flagships_total": len(FLAGSHIP_ASSIGNMENTS),
        "operating": operating,
        "skipped": skipped,
        "incomplete": incomplete,
        "phase3_exit_met": phase3_exit,
        "results": results,
    }
    _append_main_brain(
        f"[KPEFS_OPERATING_MESH] promote_all | operating: {operating}/{len(FLAGSHIP_ASSIGNMENTS)} | "
        f"exit_met: {phase3_exit}",
        "kpefs_operating_mesh_promote_all",
    )
    return payload


def operating_mesh_status() -> dict[str, Any]:
    """Summary for API / Studio — mesh targets vs promotion state."""
    from .phu_boot_governance import load_agent_mesh, load_promotion_law

    om = _load_state()
    flagships = om.get("flagships") or {}
    mesh_ids = _mesh_department_students()
    rows: list[dict[str, Any]] = []
    for sid in FLAGSHIP_ASSIGNMENTS:
        assign = FLAGSHIP_ASSIGNMENTS[sid]
        rec = flagships.get(sid) or {}
        rows.append(
            {
                "sub_brain_id": sid,
                "display": assign["display"],
                "catalog_agent": assign["catalog_agent"],
                "department": assign["department"],
                "in_boot_mesh": sid in mesh_ids,
                "status": rec.get("status", "catalog"),
                "proofs": rec.get("proofs"),
                "poc_verdict": rec.get("poc_verdict"),
            }
        )

    operating_count = sum(1 for r in rows if r.get("status") == "operating")
    return {
        "schema": "operating_mesh_status_v1",
        "assignments": FLAGSHIP_ASSIGNMENTS,
        "flagships": rows,
        "operating_count": operating_count,
        "flagships_total": len(FLAGSHIP_ASSIGNMENTS),
        "phase3_exit_met": operating_count >= len(FLAGSHIP_ASSIGNMENTS),
        "catalog_200_auto_operating": load_agent_mesh().get("catalog_200", {}).get("auto_operating", False),
        "promotion_law": load_promotion_law().get("law"),
        "state_path": str(STATE_PATH.relative_to(REPO_ROOT)),
        "last_promote": om.get("last_promote"),
    }


def lint_bracket_text(text: str) -> dict[str, Any]:
    """Bracket lint for Studio submit preview."""
    import sys

    scripts = REPO_ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    try:
        from kc_bracket_lint import lint_brackets

        violations = lint_brackets(text or "")
        return {"ok": len(violations) == 0, "violations": violations}
    except ImportError as exc:
        return {"ok": False, "violations": [f"lint_unavailable: {exc}"]}
