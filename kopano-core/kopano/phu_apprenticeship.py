"""
Kopano-Phu Teacher–Student Apprenticeship Protocol (TSAP) runtime.

MCP lane: tool-first teacher/student (Cassey / Cassy).
MAO lane: orchestrated teacher/student turns per department.
Black Mask: 15 Commandments + 5 Pillars drill before department operation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
COMMANDMENTS_PATH = REPO_ROOT / "docs" / "swarm-ops" / "BLACK_MASK_COMMANDMENTS.json"
REVIEW_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Review Log.jsonl"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
STATE_PATH = REPO_ROOT / "kopano-core" / ".kc" / "phu_apprenticeship.json"
PY = sys.executable

from .phu_ecosystem import CONFIG_PATH, load_ecosystem_config, merge_sub_brain_rows  # noqa: E402


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_black_mask_doctrine() -> dict[str, Any]:
    if not COMMANDMENTS_PATH.is_file():
        return {"commandments": [], "pillars": []}
    return json.loads(COMMANDMENTS_PATH.read_text(encoding="utf-8"))


def _load_state() -> dict[str, Any]:
    if not STATE_PATH.is_file():
        return {"schema": "phu_apprenticeship_v1", "departments": {}, "agents": {}}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"schema": "phu_apprenticeship_v1", "departments": {}, "agents": {}}


def _save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _bracket_tsap(
    *,
    lane: str,
    role: str,
    department: str,
    verdict: str,
    student: str = "cassy",
    teacher: str = "cassey",
    extra: str = "",
) -> str:
    ts = _utc_now()
    base = (
        f"[TSAP_PROTOCOL] timestamp: {ts} | ecosystem: Kopano-Phu | "
        f"lane: {lane} | role: {role} | department: {department} | "
        f"student: {student} | teacher: {teacher} | verdict: {verdict}"
    )
    return f"{base} | {extra}" if extra else base


def _bracket_blackmask(agent_id: str, cmd_pass: int, cmd_total: int, pil_pass: int, pil_total: int, verdict: str) -> str:
    ts = _utc_now()
    return (
        f"[BLACK_MASK_DRILL] timestamp: {ts} | ecosystem: Kopano-Phu | "
        f"agent: {agent_id} | commandments_pass: {cmd_pass}/{cmd_total} | "
        f"pillars_pass: {pil_pass}/{pil_total} | verdict: {verdict}"
    )


def _students_for_parent(cfg: dict[str, Any], parent_id: str) -> list[str]:
    return [row["id"] for row in cfg.get("sub_brains", []) if row.get("parent") == parent_id]


def departments_from_config() -> list[dict[str, Any]]:
    cfg = load_ecosystem_config()
    dept_defs = cfg.get("departments") or []
    if not dept_defs:
        dept_defs = [
            {
                "id": "kopano_labs_experimentation",
                "display_name": "Kopano Labs — Experimentation",
                "parent": "kopano_labs",
                "lane": "experimentation",
                "mcp_teacher": "cassey",
                "mcp_student": "cassy",
                "mao_teacher": "operational_general",
                "mao_student": "cassy",
            },
            {
                "id": "ama_phu_creativity",
                "display_name": "Ama-Phu — Creativity",
                "parent": "ama_phu",
                "lane": "creativity",
                "mcp_teacher": "cassey",
                "mcp_student": "cassy",
                "mao_teacher": "cassey",
                "mao_student": "cassy",
                "mirror_warden_focus": True,
            },
        ]

    enriched: list[dict[str, Any]] = []
    for dept in dept_defs:
        parent = dept.get("parent", "kopano_labs")
        students = dept.get("students") or _students_for_parent(cfg, parent)
        enriched.append({**dept, "students": students})
    return enriched


def blackmask_drill(
    agent_id: str,
    *,
    commandments_ack: list[str] | None = None,
    pillars_ack: list[str] | None = None,
) -> dict[str, Any]:
    """Drill agent against 15 Commandments + 5 Pillars. All must be acknowledged to SHIP."""
    doctrine = load_black_mask_doctrine()
    commandments = doctrine.get("commandments", [])
    pillars = doctrine.get("pillars", [])
    ack_cmd = set(commandments_ack or [c["id"] for c in commandments])
    ack_pil = set(pillars_ack or [p["id"] for p in pillars])

    cmd_results = [
        {"id": c["id"], "text": c["text"], "passed": c["id"] in ack_cmd}
        for c in commandments
    ]
    pil_results = [
        {"id": p["id"], "name": p["name"], "text": p["text"], "passed": p["id"] in ack_pil}
        for p in pillars
    ]
    cmd_pass = sum(1 for r in cmd_results if r["passed"])
    pil_pass = sum(1 for r in pil_results if r["passed"])
    all_pass = cmd_pass == len(commandments) and pil_pass == len(pillars)
    verdict = "SHIP" if all_pass else "HOLD"

    summary = _bracket_blackmask(
        agent_id, cmd_pass, len(commandments), pil_pass, len(pillars), verdict
    )
    _append_jsonl(
        MAIN_BRAIN_LOG,
        {
            "ts": _utc_now(),
            "kind": "black_mask_drill",
            "agent_id": agent_id,
            "summary": summary,
            "verdict": verdict,
        },
    )

    state = _load_state()
    agents = state.setdefault("agents", {})
    agents[agent_id] = {
        **agents.get(agent_id, {}),
        "black_mask": {
            "verdict": verdict,
            "commandments_pass": cmd_pass,
            "pillars_pass": pil_pass,
            "drilled_at": _utc_now(),
        },
    }
    _save_state(state)

    return {
        "agent_id": agent_id,
        "verdict": verdict,
        "commandments": cmd_results,
        "pillars": pil_results,
        "summary": summary,
        "drill_complete": all_pass,
    }


def student_submit(
    *,
    department_id: str,
    student_agent: str,
    action: str,
    evidence: str,
    lane: str = "mcp",
) -> dict[str, Any]:
    """Student proposes work — logs to Review Log + TSAP bracket."""
    dept = next((d for d in departments_from_config() if d["id"] == department_id), None)
    if not dept:
        return {"error": f"Unknown department: {department_id}"}

    from .kpgs_governance import classify_submission

    telemetry = classify_submission(action=action, evidence=evidence)
    if telemetry.get("blocked"):
        return {
            "error": "telemetry_routing_gate",
            "reason": "misnamed_pressure_requires_lane_before_interpretation",
            "telemetry_routing": telemetry,
        }

    summary = _bracket_tsap(
        lane=lane,
        role="student",
        department=department_id,
        verdict="SUBMITTED",
        student=student_agent,
        teacher=dept.get("mcp_teacher", "cassey"),
        extra=f"action: {action[:120]} | evidence: {evidence[:120]}",
    )

    review_row = {
        "ts": _utc_now(),
        "kind": "student_audit",
        "department": department_id,
        "student": student_agent,
        "action": action,
        "evidence": evidence,
        "summary": summary,
        "status": "pending_teacher",
        "telemetry_routing": telemetry,
    }
    try:
        import sys
        scripts = REPO_ROOT / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from kc_bracket_lint import lint_brackets

        errs = lint_brackets(summary)
        if errs:
            return {"error": "bracket_linguistic_violation", "violations": errs, "summary": summary}
    except ImportError:
        pass

    _append_jsonl(REVIEW_LOG, review_row)

    state = _load_state()
    pending = state.setdefault("pending_reviews", [])
    pending.append(review_row)
    _save_state(state)

    return {
        "status": "submitted",
        "department": department_id,
        "student": student_agent,
        "summary": summary,
        "telemetry_routing": telemetry,
        "next": "Teacher review via tsap_teacher_review or mao_tsap_teacher_turn",
    }


def teacher_review(
    *,
    department_id: str,
    teacher_agent: str,
    approve: bool,
    teacher_note: str = "",
    lane: str = "mcp",
) -> dict[str, Any]:
    """Teacher validates latest student work for department."""
    dept = next((d for d in departments_from_config() if d["id"] == department_id), None)
    if not dept:
        return {"error": f"Unknown department: {department_id}"}

    verdict = "APPROVE" if approve else "RETRY"
    summary = _bracket_tsap(
        lane=lane,
        role="teacher",
        department=department_id,
        verdict=verdict,
        student=dept.get("mcp_student", "cassy"),
        teacher=teacher_agent,
        extra=f"note: {teacher_note[:160]}",
    )

    _append_jsonl(
        MAIN_BRAIN_LOG,
        {
            "ts": _utc_now(),
            "kind": "teacher_review",
            "department": department_id,
            "teacher": teacher_agent,
            "verdict": verdict,
            "summary": summary,
            "teacher_note": teacher_note,
        },
    )

    kc_opinion: dict[str, Any] = {}
    try:
        from .phu_boot_governance import record_kc_teacher_review, tsap_to_kc_opinion

        kc_opinion = record_kc_teacher_review(
            opinion=tsap_to_kc_opinion(approve, teacher_note),
            ref=f"tsap:{department_id}:{verdict}",
            department=department_id,
        )
    except ImportError:
        kc_opinion = {"skipped": "phu_boot_governance not loaded"}

    if approve:
        proc = subprocess.run(
            [
                PY,
                str(REPO_ROOT / "scripts" / "kc_log_append.py"),
                "mainbrain",
                "--kind",
                "tsap_teacher_approve",
                "--summary",
                summary,
                "--exit-code",
                "0",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        exit_code = proc.returncode
    else:
        exit_code = 0

    return {
        "status": "reviewed",
        "department": department_id,
        "teacher": teacher_agent,
        "verdict": verdict,
        "summary": summary,
        "main_brain_exit_code": exit_code,
        "kc_teacher_review": kc_opinion,
    }


def begin_department_students(*, run_blackmask: bool = True) -> dict[str, Any]:
    """Begin student operation in each Kopano-Phu department."""
    cfg = load_ecosystem_config()
    departments = departments_from_config()
    state = _load_state()
    started: list[dict[str, Any]] = []

    for dept in departments:
        dept_id = dept["id"]
        student_ids = dept.get("students") or []
        drills: list[dict[str, Any]] = []

        for sid in student_ids:
            agent_state: dict[str, Any] = {"department": dept_id, "status": "active", "started_at": _utc_now()}
            if run_blackmask:
                drill = blackmask_drill(sid)
                agent_state["black_mask"] = drill
                drills.append({"agent_id": sid, "verdict": drill["verdict"]})
            state.setdefault("agents", {})[sid] = agent_state

        dept_entry = {
            "id": dept_id,
            "display_name": dept.get("display_name"),
            "lane": dept.get("lane"),
            "parent": dept.get("parent"),
            "student_count": len(student_ids),
            "students": student_ids,
            "mcp_teacher": dept.get("mcp_teacher", "cassey"),
            "mcp_student": dept.get("mcp_student", "cassy"),
            "mao_teacher": dept.get("mao_teacher", "operational_general"),
            "mao_student": dept.get("mao_student", "cassy"),
            "blackmask_drills": drills,
            "status": "operating",
            "started_at": _utc_now(),
        }
        state.setdefault("departments", {})[dept_id] = dept_entry
        started.append(dept_entry)

        tsap_summary = _bracket_tsap(
            lane="ecosystem",
            role="coordinator",
            department=dept_id,
            verdict="BEGIN",
            extra=f"students: {len(student_ids)} | blackmask: {run_blackmask}",
        )
        _append_jsonl(
            MAIN_BRAIN_LOG,
            {
                "ts": _utc_now(),
                "kind": "department_students_begin",
                "department": dept_id,
                "summary": tsap_summary,
            },
        )

    state["last_begin"] = _utc_now()
    state["protocol"] = "TEACHER_STUDENT_APPRENTICESHIP_PROTOCOL"
    state["ecosystem"] = cfg.get("title", "Kopano-Phu Ecosystem")
    _save_state(state)

    sub_brains = merge_sub_brain_rows()
    return {
        "schema": "department_students_begin_v1",
        "ecosystem": "Kopano-Phu Eco-Friendly System",
        "parents": cfg.get("parents", []),
        "breaking_point_protocol": cfg.get("breaking_point_protocol", "Bracket Protocol"),
        "departments_started": started,
        "sub_brains_attached": sum(1 for r in sub_brains if r.get("attachment") == "attached"),
        "sub_brains_total": len(sub_brains),
        "state_path": str(STATE_PATH.relative_to(REPO_ROOT)),
    }


def apprenticeship_status() -> dict[str, Any]:
    cfg = load_ecosystem_config()
    state = _load_state()
    doctrine = load_black_mask_doctrine()
    return {
        "schema": "phu_apprenticeship_status_v1",
        "protocol": "TEACHER_STUDENT_APPRENTICESHIP_PROTOCOL",
        "bracket_tags": ["[TSAP_PROTOCOL]", "[BLACK_MASK_DRILL]", "[BRACKET_PROTOCOL]"],
        "ecosystem": cfg.get("title"),
        "subtitle": cfg.get("subtitle"),
        "parents": cfg.get("parents", []),
        "teaching_surfaces": cfg.get("teaching_surfaces", {}),
        "departments": departments_from_config(),
        "commandments_count": len(doctrine.get("commandments", [])),
        "pillars_count": len(doctrine.get("pillars", [])),
        "runtime": state,
        "docs": {
            "tsap": "docs/swarm-ops/apprenticeship/TEACHER_STUDENT_APPRENTICESHIP_PROTOCOL.md",
            "commandments": "docs/swarm-ops/BLACK_MASK_COMMANDMENTS.json",
            "bracket": "docs/swarm-ops/BRACKET_PROTOCOL.md",
        },
    }
