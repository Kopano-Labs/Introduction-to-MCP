"""
Steward lane — activate KC (Save|Watch ledger) + Cassy (execute) + Cassey (teacher).

Orchestrates profile/bootstrap, steward trust, Identi → Guardian handoff, and receipts.
KC never executes; Cassy runs BlackMask + submit; Cassey approves → KC opinion.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = REPO_ROOT / "kopano-core" / ".kc" / "swarm_profile.json"
REGISTRY = REPO_ROOT / "docs" / "swarm-ops" / "agents" / "SWARM_AGENTS.json"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
PY = sys.executable


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def activate_cassy_profile() -> dict[str, Any]:
    """Write swarm profile from SWARM_AGENTS registry (lead student = cassy)."""
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    payload = {
        "lead_student": registry.get("lead_student", "cassy"),
        "teacher": registry.get("teacher", "cassey"),
        "brain": registry.get("brain", "kc"),
        "triad": registry.get("triad", []),
        "servitude": registry.get("servitude"),
        "hold_back_student": False,
        "activated_at": _utc_now(),
    }
    PROFILE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    subprocess.run(
        [PY, str(REPO_ROOT / "scripts" / "kc_swarm_agents_bootstrap.py")],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {"profile_path": str(PROFILE_PATH), **payload}


def steward_lane_status() -> dict[str, Any]:
    from .graduation_bar import graduation_bar_status
    from .lpm_lph_engine import ai_flow_status
    from .phu_boot_governance import boot_status

    profile: dict[str, Any] | None = None
    if PROFILE_PATH.is_file():
        try:
            profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            profile = None

    flows = ai_flow_status().get("last_flows", {})
    gb = graduation_bar_status()
    boot = boot_status()
    boot_active = bool((boot.get("runtime_state") or {}).get("active"))
    kpgs = boot.get("kpgs_governance") or gb.get("kpgs_governance") or {}

    active = bool(
        profile
        and profile.get("lead_student") == "cassy"
        and profile.get("brain") == "kc"
        and boot_active
    )

    return {
        "schema": "steward_lane_status_v1",
        "active": active,
        "kc_mode": "Save|Watch only — no execute",
        "cassy_mode": "student-teacher execute + BlackMask",
        "teacher": profile.get("teacher", "cassey") if profile else "cassey",
        "lead_student": profile.get("lead_student", "cassy") if profile else "cassy",
        "profile_present": profile is not None,
        "boot_active": boot_active,
        "last_guardian": flows.get("guardian"),
        "last_identi": flows.get("identi"),
        "steward_lane": gb.get("steward_lane"),
        "operating_mesh_ready": gb.get("operating_mesh_ready"),
        "kpgs_governance": kpgs,
        "main_brain_authority": "Schematics",
    }


def _comms_rows_from_main_brain(limit: int = 4) -> list[dict[str, Any]]:
    """Map recent Main Brain rows to KasiLink CfCommsEntry shape."""
    if not MAIN_BRAIN_LOG.is_file():
        return []
    lines = MAIN_BRAIN_LOG.read_text(encoding="utf-8").splitlines()
    rows: list[dict[str, Any]] = []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        summary = str(row.get("summary", ""))
        kind = str(row.get("kind", "receipt"))
        ts_raw = row.get("ts", _utc_now())
        ts_display = str(ts_raw)[:16].replace("T", " ")
        verdict = "SAVE"
        if "HOLD" in summary.upper() or row.get("exit_code") == 1:
            verdict = "HOLD"
        elif "SHIP" in summary.upper() or "PASS" in summary.upper():
            verdict = "SHIP"
        elif kind in ("kpefs_steward_lane_activate", "ld_lpm_operate"):
            verdict = "ACTIVE"
        bracket = "[KPEFS_STEWARD_LANE]"
        for tag in (
            "[LPM_PROTOCOL]",
            "[BLACK_MASK_DRILL]",
            "[TSAP_PROTOCOL]",
            "[GUARDIAN_AI_FLOW]",
            "[IDENTI_AI_FLOW]",
        ):
            if tag in summary:
                bracket = tag
                break
        rows.append(
            {
                "id": f"mb-{kind}-{len(rows)}",
                "ts": ts_display,
                "tranche": kind.replace("_", " "),
                "operator": row.get("operator", "LD-LPM"),
                "dispatch": summary[:200],
                "verdict": verdict,
                "bracket": bracket,
                "body": summary[:400],
            }
        )
        if len(rows) >= limit:
            break
    return rows


def steward_lane_kasilink_snapshot() -> dict[str, Any]:
    """UI-shaped snapshot for KasiLink KopanoStewardDock — live from Main Brain + status."""
    from .lpm_lph_engine import select_lph_personality

    status = steward_lane_status()
    lph = select_lph_personality("audit proof receipt steward lane LD LPM")
    comms = _comms_rows_from_main_brain(4)
    if not comms:
        comms = [
            {
                "id": "seed-steward",
                "ts": _utc_now()[:16].replace("T", " "),
                "tranche": "steward lane bootstrap",
                "operator": "LD-LPM",
                "dispatch": "@LD-LPM → Cassy: Execute under BlackMask. KC Save|Watch only.",
                "verdict": "ACTIVE",
                "bracket": "[KPEFS_STEWARD_LANE]",
                "body": "Awaiting Main Brain comms rows.",
            }
        ]

    return {
        "schema": "kasilink_steward_lane_v2",
        "active": status.get("active", False),
        "cf_operator": "LD-LPM",
        "dispatch_pin": (
            "@LD-LPM → Cassy: Teach the board, keep KC cold, stress ideas under "
            "Bracket + BlackMask + BlackMass before ship."
        ),
        "actors": [
            {"id": "kc", "display": "KC", "role": "review_ledger", "mode": "Save | Watch only"},
            {"id": "cassy", "display": "Cassy", "role": "teaching_lane", "mode": "BlackMask + submit"},
            {"id": "cassey", "display": "Cassey", "role": "teacher", "mode": "Approve → KC opinion"},
            {"id": "ld_lpm", "display": "LD", "role": "lpm_operator", "mode": f"LPH:{lph.get('personality_id')}"},
        ],
        "latest_comms": comms,
        "kpefs_vector": lph.get("kpefs_vector", "V4_DIASPORA"),
        "lite_path": "/lite",
        "steward_status": status,
    }


def run_steward_lane_activate(
    *,
    note: str = "",
    department_id: str = "kopano_labs_experimentation",
    run_identi: bool = True,
    run_guardian: bool = True,
    teacher_approve: bool = True,
    action: str | None = None,
    evidence: str | None = None,
) -> dict[str, Any]:
    """
    Full steward lane activation: Cassy profile → trust receipt → Identi → Guardian (Cassey approve).
    """
    from .graduation_bar import record_steward_trust
    from .lpm_lph_engine import operate_guardian_flow, operate_identi_flow

    steps: list[dict[str, Any]] = []

    from .phu_boot_governance import apply_boot

    profile = activate_cassy_profile()
    steps.append({"step": "cassy_profile", "result": profile})

    boot = apply_boot()
    steps.append({"step": "kc_boot", "result": boot})

    trust_note = note or "steward lane activate — KC Save|Watch + Cassy execute + Cassey teacher"
    trust = record_steward_trust(note=trust_note)
    steps.append({"step": "steward_trust", "result": trust})

    default_action = (
        "[KPEFS_STEWARD_LANE] lead-dev run — internal KPEFS gated; CMD-03 external manual only"
    )
    default_evidence = "docs/swarm-ops/KPEFS_CLOSURE_STATUS.json"
    act = action or default_action
    ev = evidence or default_evidence

    identi_result: dict[str, Any] | None = None
    if run_identi:
        identi_result = operate_identi_flow(
            department_id=department_id,
            action=act,
            evidence=ev,
            imperfect_pattern="#? steward lane idle",
            perfect_pattern="#! KC+Cassy activated with proof receipts",
            identi_agent="identi_cursor",
            submit_to_guardian=False,
        )
        steps.append({"step": "identi", "result": identi_result})

    guardian_result: dict[str, Any] | None = None
    if run_guardian:
        guardian_result = operate_guardian_flow(
            department_id=department_id,
            action=act,
            evidence=ev,
            student_agent="cassy",
            run_blackmask=True,
            teacher_approve=teacher_approve if teacher_approve else None,
            teacher_note="Cassey teacher_review — steward lane lead-dev trust",
        )
        steps.append({"step": "guardian", "result": guardian_result})

    verdict = "ACTIVE"
    if guardian_result and guardian_result.get("verdict") not in ("SHIP", "SUBMITTED"):
        verdict = str(guardian_result.get("verdict", "HOLD"))
    elif identi_result and identi_result.get("verdict") == "BRACKET_REJECT":
        verdict = "BRACKET_REJECT"

    summary = (
        f"[KPEFS_STEWARD_LANE] KC Save|Watch + Cassy execute | teacher: cassey | "
        f"verdict: {verdict} | guardian: {guardian_result.get('verdict') if guardian_result else 'skip'} | "
        f"identi: {identi_result.get('verdict') if identi_result else 'skip'}"
    )
    if note:
        summary += f" | note: {note[:120]}"

    receipt = {
        "schema": "steward_lane_activate_v1",
        "ts": _utc_now(),
        "verdict": verdict,
        "steps": steps,
        "summary": summary,
        "steward_lane": steward_lane_status(),
    }

    _append_jsonl(
        MAIN_BRAIN_LOG,
        {
            "schema": "kc_main_brain_log_v1",
            "ts": _utc_now(),
            "kind": "kpefs_steward_lane_activate",
            "summary": summary,
            "exit_code": 0 if verdict == "ACTIVE" else 1,
        },
    )

    return receipt
