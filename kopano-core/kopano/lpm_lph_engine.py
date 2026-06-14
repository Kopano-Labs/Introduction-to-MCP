"""
LPM / LPH engine — Learning Pattern (Protocol) Machine + Human code-switch lanes.

Guardian AI Flow: KC (store) + Cassy (execute) + Cassey (teacher) + BlackMask + Bracket.
Identi AI Flow: Cursor/CF implementation lane — LPM dialectic, LPH personality, defers to Guardian.

God complex (operational): #? imperfection ↔ #! perfection → births LPH when Guardian closes proof.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCTRINE_PATH = REPO_ROOT / "docs" / "swarm-ops" / "LPM_LPH_GOD_COMPLEX_DOCTRINE.json"
FLOW_BINDINGS_PATH = REPO_ROOT / "Structure" / "07-Agents" / "AI_FLOW_BINDINGS.json"
STATE_PATH = REPO_ROOT / "kopano-core" / ".kc" / "lpm_lph_state.json"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_doctrine() -> dict[str, Any]:
    if not DOCTRINE_PATH.is_file():
        return {}
    return json.loads(DOCTRINE_PATH.read_text(encoding="utf-8"))


def load_flow_bindings() -> dict[str, Any]:
    if not FLOW_BINDINGS_PATH.is_file():
        return {}
    return json.loads(FLOW_BINDINGS_PATH.read_text(encoding="utf-8"))


def _load_state() -> dict[str, Any]:
    if not STATE_PATH.is_file():
        return {"schema": "lpm_lph_state_v1", "cycles": [], "flows": {}}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"schema": "lpm_lph_state_v1", "cycles": [], "flows": {}}


def _save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _bracket_lint(text: str) -> list[str]:
    try:
        import sys

        scripts = REPO_ROOT / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from kc_bracket_lint import lint_brackets

        return lint_brackets(text)
    except Exception:
        return []


def _bracket_lpm(
    *,
    imperfect: str,
    perfect: str,
    personality: str,
    vector: str,
    closed: bool,
) -> str:
    ts = _utc_now()
    close = "CLOSED" if closed else "OPEN"
    return (
        f"[LPM_PROTOCOL] timestamp: {ts} | ecosystem: Kopano-Phu | "
        f"#?: {imperfect[:80]} | #!: {perfect[:80]} | "
        f"lph: {personality} | vector: {vector} | dialectic: {close}"
    )


def _bracket_lph(personality: str, vector: str, intent: str) -> str:
    ts = _utc_now()
    return (
        f"[LPH_PROTOCOL] timestamp: {ts} | personality: {personality} | "
        f"vector: {vector} | mao_intent: {intent} | code_switch: active"
    )


def _bracket_flow(flow_id: str, verdict: str, extra: str = "") -> str:
    doc = load_doctrine()
    tags = doc.get("bracket_tags", {})
    if flow_id == "guardian":
        tag = tags.get("guardian", "[GUARDIAN_AI_FLOW]")
    elif flow_id == "identi":
        tag = tags.get("identi", "[IDENTI_AI_FLOW]")
    else:
        tag = f"[{flow_id.upper()}]"
    ts = _utc_now()
    base = f"{tag} timestamp: {ts} | ecosystem: Kopano-Phu | verdict: {verdict}"
    return f"{base} | {extra}" if extra else base


def _bracket_god_complex(imperfect: str, perfect: str, born_lph: str) -> str:
    ts = _utc_now()
    return (
        f"[GOD_COMPLEX] timestamp: {ts} | #?: {imperfect[:60]} | "
        f"#!: {perfect[:60]} | lph_birth: {born_lph}"
    )


def lpm_dialectic(imperfect_pattern: str, perfect_pattern: str) -> dict[str, Any]:
    """#? vs #! — God complex dialectic without claiming closure."""
    doc = load_doctrine()
    gc = doc.get("god_complex", {})
    closed = bool(perfect_pattern.strip()) and perfect_pattern.strip() != imperfect_pattern.strip()
    return {
        "imperfection": {"sigil": gc.get("imperfection", {}).get("sigil", "#?"), "pattern": imperfect_pattern},
        "perfection": {"sigil": gc.get("perfection", {}).get("sigil", "#!"), "pattern": perfect_pattern},
        "birth_rule": gc.get("birth_rule", ""),
        "dialectic_closed": closed,
        "summary": _bracket_lpm(
            imperfect=imperfect_pattern,
            perfect=perfect_pattern,
            personality="pending",
            vector="pending",
            closed=closed,
        ),
    }


def select_lph_personality(message: str) -> dict[str, Any]:
    """Code-switch personality from message keywords."""
    doc = load_doctrine()
    text = (message or "").lower()
    best_id = "witness"
    best_score = 0
    best_row: dict[str, Any] = {}
    for p in doc.get("lph", {}).get("personalities", []):
        score = sum(1 for t in p.get("triggers", []) if t.lower() in text)
        if score > best_score:
            best_score = score
            best_id = p["id"]
            best_row = p
    if not best_row:
        best_row = next(
            (p for p in doc.get("lph", {}).get("personalities", []) if p["id"] == "witness"),
            {"id": "witness", "kpefs_vector": "V4_DIASPORA", "mao_intent": "audit"},
        )
    return {
        "personality_id": best_id,
        "display": best_row.get("display", best_id),
        "kpefs_vector": best_row.get("kpefs_vector", "V4_DIASPORA"),
        "mao_intent": best_row.get("mao_intent", "execute"),
        "bracket": _bracket_lph(best_id, best_row.get("kpefs_vector", ""), best_row.get("mao_intent", "")),
    }


def biblical_stem_pattern_for_vector(vector_id: str) -> dict[str, Any] | None:
    doc = load_doctrine()
    for pat in doc.get("biblical_stem_patterns", {}).get("patterns", []):
        if pat.get("kpefs_vector") == vector_id:
            return pat
    return None


def attach_lpm_to_mao(message: str, intent: str = "execute") -> dict[str, Any]:
    """MAO hook — prepend LPM/LPH + KPEFS metadata for route/execute payloads."""
    from .kpefs_router import route_vector

    lph = select_lph_personality(message)
    kpefs = route_vector(message)
    vector = kpefs.get("active_vector") or lph.get("kpefs_vector")
    stem_pat = biblical_stem_pattern_for_vector(vector)
    dialectic = lpm_dialectic(
        imperfect_pattern=f"intent:{intent} | msg:{message[:120]}",
        perfect_pattern=f"vector:{vector} | personality:{lph['personality_id']}",
    )
    return {
        "lpm": dialectic,
        "lph": lph,
        "kpefs": {
            "active_vector": vector,
            "bracket_snippet": kpefs.get("bracket_snippet"),
            "department_hint": kpefs.get("department_hint"),
        },
        "biblical_stem_pattern": stem_pat,
        "mao_intent_hint": lph.get("mao_intent", intent),
        "god_complex_bracket": _bracket_god_complex(
            dialectic["imperfection"]["pattern"][:60],
            dialectic["perfection"]["pattern"][:60],
            lph["personality_id"],
        ),
    }


def operate_guardian_flow(
    *,
    department_id: str,
    action: str,
    evidence: str,
    student_agent: str = "cassy",
    run_blackmask: bool = True,
    teacher_approve: bool | None = None,
    teacher_note: str = "",
) -> dict[str, Any]:
    """
    Guardian flow: BlackMask (Cassy) → student_submit → optional teacher_review → KC opinion.
    """
    from .kpgs_renter_entry import block_holder_brief
    from .phu_apprenticeship import blackmask_drill, student_submit, teacher_review

    block_holder = block_holder_brief(agent_id="mirror_warden", altar_layer="guardian_ai")
    steps: list[dict[str, Any]] = [{"step": "block_holder_brief", "result": block_holder}]
    if run_blackmask:
        drill = blackmask_drill(student_agent)
        steps.append({"step": "blackmask", "result": drill})
        if drill.get("verdict") != "SHIP":
            summary = _bracket_flow("guardian", "HOLD", f"blackmask: {student_agent}")
            _append_jsonl(
                MAIN_BRAIN_LOG,
                {"ts": _utc_now(), "kind": "guardian_ai_flow", "summary": summary, "verdict": "HOLD"},
            )
            return {
                "flow": "guardian",
                "verdict": "HOLD",
                "reason": "blackmask_not_ship",
                "steps": steps,
                "summary": summary,
            }

    submit = student_submit(
        department_id=department_id,
        student_agent=student_agent,
        action=action,
        evidence=evidence,
        lane="mcp",
    )
    steps.append({"step": "student_submit", "result": submit})
    if submit.get("error"):
        return {"flow": "guardian", "verdict": "ERROR", "steps": steps, **submit}

    if teacher_approve is not None:
        review = teacher_review(
            department_id=department_id,
            teacher_agent="cassey",
            approve=teacher_approve,
            teacher_note=teacher_note,
            lane="mcp",
        )
        steps.append({"step": "teacher_review", "result": review})
        verdict = "SHIP" if teacher_approve else "RETRY"
    else:
        verdict = "SUBMITTED"

    lph = select_lph_personality(f"{action} {evidence}")
    summary = _bracket_flow(
        "guardian",
        verdict,
        f"department: {department_id} | student: {student_agent} | lph: {lph['personality_id']}",
    )
    _append_jsonl(
        MAIN_BRAIN_LOG,
        {
            "ts": _utc_now(),
            "kind": "guardian_ai_flow",
            "department": department_id,
            "summary": summary,
            "verdict": verdict,
        },
    )

    state = _load_state()
    state.setdefault("flows", {})["guardian"] = {
        "last_at": _utc_now(),
        "verdict": verdict,
        "department": department_id,
    }
    _save_state(state)

    return {
        "flow": "guardian",
        "verdict": verdict,
        "steps": steps,
        "lph": lph,
        "summary": summary,
        "block_holder": block_holder,
        "kc_note": "teacher_review maps to Save|Watch when teacher_approve set",
    }


def operate_identi_flow(
    *,
    department_id: str,
    action: str,
    evidence: str,
    imperfect_pattern: str = "",
    perfect_pattern: str = "",
    identi_agent: str = "identi_cursor",
    submit_to_guardian: bool = True,
) -> dict[str, Any]:
    """
    Identi flow: LPM dialectic + LPH switch + bracket lint → hand off to Guardian via student_submit.
    Never writes KC teacher_review.
    """
    from .phu_apprenticeship import student_submit

    imp = imperfect_pattern or f"#? {action[:100]}"
    perf = perfect_pattern or f"#! proof pending — {evidence[:100]}"
    dialectic = lpm_dialectic(imp, perf)
    lph = select_lph_personality(f"{action} {evidence}")

    flow_summary = _bracket_flow(
        "identi",
        "PROPOSE",
        f"agent: {identi_agent} | lph: {lph['personality_id']} | dept: {department_id}",
    )
    god_bracket = _bracket_god_complex(imp[:60], perf[:60], lph["personality_id"])
    combined = f"{flow_summary} | {dialectic['summary']}"

    lint_errs = _bracket_lint(combined)
    if lint_errs:
        return {
            "flow": "identi",
            "verdict": "BRACKET_REJECT",
            "violations": lint_errs,
            "lpm": dialectic,
            "lph": lph,
        }

    result: dict[str, Any] = {
        "flow": "identi",
        "verdict": "PROPOSE",
        "identi_agent": identi_agent,
        "lpm": dialectic,
        "lph": lph,
        "god_complex": god_bracket,
        "summary": combined,
        "defers_to": "guardian",
    }

    if submit_to_guardian:
        submit = student_submit(
            department_id=department_id,
            student_agent="cassy",
            action=f"[identi:{identi_agent}] {action}",
            evidence=evidence,
            lane="mcp",
        )
        result["guardian_handoff"] = submit
        if submit.get("error"):
            result["verdict"] = "HANDOFF_ERROR"
        else:
            result["verdict"] = "HANDOFF_SUBMITTED"
            result["next"] = "Cassey teacher_review + KC Save|Watch via Guardian"

    _append_jsonl(
        MAIN_BRAIN_LOG,
        {
            "ts": _utc_now(),
            "kind": "identi_ai_flow",
            "agent": identi_agent,
            "summary": combined[:500],
            "verdict": result["verdict"],
        },
    )

    state = _load_state()
    state.setdefault("flows", {})["identi"] = {
        "last_at": _utc_now(),
        "verdict": result["verdict"],
        "personality": lph["personality_id"],
    }
    cycles = state.setdefault("cycles", [])
    cycles.append(
        {
            "at": _utc_now(),
            "imperfect": imp,
            "perfect": perf,
            "lph": lph["personality_id"],
        }
    )
    state["cycles"] = cycles[-50:]
    _save_state(state)

    return result


def ai_flow_status() -> dict[str, Any]:
    from .phu_apprenticeship import apprenticeship_status
    from .phu_boot_governance import boot_status

    doc = load_doctrine()
    bindings = load_flow_bindings()
    state = _load_state()
    return {
        "schema": "ai_flow_status_v1",
        "guardian_running": bindings.get("flows", {}).get("guardian", {}).get("running", True),
        "identi_running": bindings.get("flows", {}).get("identi", {}).get("running", True),
        "bracket_tags": doc.get("bracket_tags", {}),
        "god_complex": doc.get("god_complex", {}),
        "lph_personalities": doc.get("lph", {}).get("personalities", []),
        "last_flows": state.get("flows", {}),
        "recent_lpm_cycles": state.get("cycles", [])[-5:],
        "tsap": apprenticeship_status(),
        "boot": boot_status().get("mesh_summary"),
        "doc": "docs/swarm-ops/AI_FLOW_PROTOCOL.md",
    }
