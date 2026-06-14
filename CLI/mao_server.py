"""
MAO — Multi Agent Orchestrator (MCP Server)
Evolution: LLM → LPM (Large Production Model)

Principles (from SERVITUDE_TRIAD.md):
  - Realism accommodates Aesthetics
  - Local-first, offline-capable, proof-gated
  - STEM validates what creativity stems

Author: Kholofelo Robyn Rababalela
Org: Kopano Labs
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

REPO_ROOT = Path(__file__).resolve().parents[1]
SWARM_AGENTS_PATH = REPO_ROOT / "docs" / "swarm-ops" / "agents" / "SWARM_AGENTS.json"
BRAIN_LOG_PATH = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
LOCAL_DB_PATH = Path(os.environ.get(
    "MAO_DB_PATH",
    str(Path.home() / ".kopano" / "mao_state.db"),
))
AUDIT_LOG_PATH = Path(os.environ.get(
    "MAO_AUDIT_LOG",
    str(REPO_ROOT / "docs" / "swarm-ops" / "logs" / "mao_audit.jsonl"),
))

sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

mcp = FastMCP("MAO", log_level="ERROR")


def _ensure_db() -> sqlite3.Connection:
    LOCAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(LOCAL_DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_state (
            agent_id TEXT PRIMARY KEY,
            last_routed_at TEXT,
            total_routes INTEGER DEFAULT 0,
            last_context TEXT,
            status TEXT DEFAULT 'idle'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS routing_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            intent TEXT,
            message_hash TEXT,
            outcome TEXT,
            confidence REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS context_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            stored_at TEXT NOT NULL,
            UNIQUE(agent_id, key)
        )
    """)
    conn.commit()
    return conn


def _log_audit(event_type: str, payload: dict) -> None:
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "kind": event_type,
        "payload": payload,
    }
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _load_swarm_registry() -> dict[str, Any]:
    if not SWARM_AGENTS_PATH.exists():
        return {"agents": [], "triad": [], "philosophy": {}}
    with SWARM_AGENTS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _get_agent_capabilities(agent: dict) -> list[str]:
    """Derive capabilities from agent role and metadata."""
    role = agent.get("role", "")
    caps = []
    if "student" in role:
        caps.extend(["execute", "learn", "build"])
    if "teacher" in role:
        caps.extend(["review", "guide", "validate"])
    if role == "brain":
        caps.extend(["ledger", "opinion", "audit"])
    if role == "mesh":
        caps.extend(["generate", "reason", "research"])
    if "orchestrator" in role:
        caps.extend(["coordinate", "dispatch", "monitor"])
    if "lpm_operator" in role:
        caps.extend(["autonomic", "flow", "orchestrate"])
    if "mesh_worker" in role:
        caps.extend(["pipeline", "render", "transform"])
    return caps


AGENT_KEYWORDS: dict[str, list[str]] = {
    "cassy": ["build", "implement", "code", "ship", "deploy", "feature", "bug", "fix", "test",
              "speech", "language", "translate", "tts", "stt", "zulu", "xhosa", "afrikaans",
              "creative", "canvas", "ui", "wireframe", "citation", "source", "reference"],
    "cassey": ["teach", "review", "guide", "mentor", "explain", "assess", "grade", "feedback"],
    "kc": ["brain", "ledger", "record", "log", "opinion", "doctrine", "philosophy", "proof"],
    "kopano": ["memory", "context", "recall", "history", "relationship", "legacy", "persistence"],
    "mirror_warden": ["guard", "validate", "check", "enforce", "policy", "compliance"],
    "kc_apprentice": ["learn", "practice", "drill", "homework", "exercise", "study"],
    "operational_general": ["ops", "deploy", "monitor", "health", "uptime", "incident"],
    "pipeline_drone": ["pipeline", "etl", "transform", "batch", "process", "render"],
    "claude": ["reason", "analyze", "write", "summarize", "plan", "draft", "strategy"],
    "grok": ["research", "search", "news", "trend", "data", "fact", "verify"],
    "gemini": ["multimodal", "image", "vision", "diagram", "visual", "design"],
    "copilot": ["autocomplete", "snippet", "boilerplate", "scaffold", "template"],
    "cf_cloud": ["orchestrate", "flow", "automate", "schedule", "cron", "agent", "autonomic"],
}

INTENT_TO_CAP = {
    "build": ["build", "execute", "pipeline"],
    "review": ["review", "validate", "audit"],
    "research": ["research", "reason", "generate"],
    "teach": ["guide", "review", "validate"],
    "execute": ["execute", "build", "pipeline"],
    "orchestrate": ["orchestrate", "coordinate", "dispatch"],
    "translate": ["execute", "build"],
    "audit": ["audit", "ledger", "opinion"],
    "coding": ["build", "execute", "pipeline"],
    "language": ["execute", "build"],
    "creative": ["generate", "render", "transform"],
    "memory": ["ledger", "opinion", "audit"],
}


def _score_by_keywords(message: str) -> dict[str, float]:
    """Score each agent by keyword presence in the message."""
    msg_lower = message.lower()
    scores: dict[str, float] = {}
    for agent_id, keywords in AGENT_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in msg_lower)
        if hits > 0:
            scores[agent_id] = hits / len(keywords)
    return scores


def _route_to_agent(intent: str, registry: dict, message: str = "") -> dict[str, Any]:
    """Route an intent to the best-fit agent using capability + keyword matching."""
    intent_lower = intent.lower()
    agents = registry.get("agents", [])

    required_caps = INTENT_TO_CAP.get(intent_lower, ["execute", "build"])
    keyword_scores = _score_by_keywords(message) if message else {}

    scored: list[tuple[float, dict]] = []
    for agent in agents:
        agent_id = agent.get("id", "")
        caps = _get_agent_capabilities(agent)
        cap_overlap = len(set(caps) & set(required_caps))
        cap_score = cap_overlap / len(required_caps) if required_caps else 0

        kw_score = keyword_scores.get(agent_id, 0.0)

        combined = (cap_score * 0.6) + (kw_score * 0.4)

        if agent_id == "cassy":
            combined += 0.05

        if combined > 0:
            scored.append((combined, agent))

    scored.sort(key=lambda x: x[0], reverse=True)

    if scored:
        best_score, best_agent = scored[0]
        return {
            "agent_id": best_agent["id"],
            "display_name": best_agent.get("display_name", best_agent["id"]),
            "role": best_agent.get("role", "unknown"),
            "confidence": round(best_score, 3),
            "capabilities": _get_agent_capabilities(best_agent),
        }

    return {
        "agent_id": "cassy",
        "display_name": "Cassy",
        "role": "student_primary",
        "confidence": 0.5,
        "capabilities": ["execute", "learn", "build"],
        "fallback": True,
    }


# ─── MCP TOOLS ───────────────────────────────────────────────────────────────


@mcp.tool(
    name="mao_route",
    description="Route a task to the best-fit swarm agent based on intent. "
    "Returns the recommended agent and confidence score.",
)
def mao_route(
    intent: str = Field(description="The intent category: build, review, research, teach, execute, orchestrate, translate, audit, coding, language, creative, memory"),
    message: str = Field(description="The task or message to route"),
) -> dict[str, Any]:
    _intent = intent if isinstance(intent, str) else str(intent)
    _message = message if isinstance(message, str) else str(message)
    registry = _load_swarm_registry()
    result = _route_to_agent(_intent, registry, _message)

    conn = _ensure_db()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """INSERT OR REPLACE INTO agent_state (agent_id, last_routed_at, total_routes, status)
           VALUES (?, ?, COALESCE((SELECT total_routes FROM agent_state WHERE agent_id = ?), 0) + 1, 'active')""",
        (result["agent_id"], now, result["agent_id"]),
    )
    conn.execute(
        "INSERT INTO routing_log (ts, agent_id, intent, outcome, confidence) VALUES (?, ?, ?, ?, ?)",
        (now, result["agent_id"], intent, "routed", result["confidence"]),
    )
    conn.commit()
    conn.close()

    _log_audit("mao_route", {"intent": intent, "routed_to": result["agent_id"], "confidence": result["confidence"]})

    payload = {
        "routed_agent": result,
        "message": message,
        "philosophy_gate": registry.get("philosophy", {}).get("agent_gate", []),
        "lpm_status": "autonomic",
    }
    try:
        import sys
        from pathlib import Path

        kroot = Path(__file__).resolve().parents[1] / "kopano-core"
        if str(kroot) not in sys.path:
            sys.path.insert(0, str(kroot))
        from kopano.kpefs_router import route_vector

        kpefs = route_vector(_message)
        payload["kpefs"] = {
            "active_vector": kpefs.get("active_vector"),
            "rank": kpefs.get("rank"),
            "department_hint": kpefs.get("department_hint"),
            "bracket_snippet": kpefs.get("bracket_snippet"),
            "scores": kpefs.get("scores"),
        }
    except Exception:
        payload["kpefs"] = None
    return payload


@mcp.tool(
    name="mao_swarm_status",
    description="Get the current status of all swarm agents — registry, state, and routing history.",
)
def mao_swarm_status() -> dict[str, Any]:
    registry = _load_swarm_registry()
    conn = _ensure_db()

    states = conn.execute("SELECT agent_id, last_routed_at, total_routes, status FROM agent_state").fetchall()
    state_map = {row[0]: {"last_routed": row[1], "total_routes": row[2], "status": row[3]} for row in states}

    recent_routes = conn.execute(
        "SELECT ts, agent_id, intent, confidence FROM routing_log ORDER BY id DESC LIMIT 10"
    ).fetchall()
    conn.close()

    agents_summary = []
    for agent in registry.get("agents", []):
        aid = agent["id"]
        state = state_map.get(aid, {"last_routed": None, "total_routes": 0, "status": "idle"})
        agents_summary.append({
            "id": aid,
            "display_name": agent.get("display_name", aid),
            "role": agent.get("role", "unknown"),
            "capabilities": _get_agent_capabilities(agent),
            **state,
        })

    return {
        "total_agents": len(registry.get("agents", [])),
        "triad": registry.get("triad", []),
        "philosophy": registry.get("philosophy", {}),
        "agents": agents_summary,
        "recent_routing": [
            {"ts": r[0], "agent": r[1], "intent": r[2], "confidence": r[3]}
            for r in recent_routes
        ],
        "lpm_mode": "autonomic",
        "offline_capable": True,
    }


@mcp.tool(
    name="mao_store_context",
    description="Store a key-value context for an agent in local persistent memory. "
    "Offline-first — no cloud dependency.",
)
def mao_store_context(
    agent_id: str = Field(description="The agent ID to store context for"),
    key: str = Field(description="Context key (e.g., 'current_task', 'last_decision')"),
    value: str = Field(description="Context value to persist locally"),
) -> dict[str, str]:
    conn = _ensure_db()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO context_memory (agent_id, key, value, stored_at) VALUES (?, ?, ?, ?)",
        (agent_id, key, value, now),
    )
    conn.commit()
    conn.close()
    _log_audit("context_store", {"agent_id": agent_id, "key": key})
    return {"status": "stored", "agent_id": agent_id, "key": key, "stored_at": now}


@mcp.tool(
    name="mao_recall_context",
    description="Recall stored context for an agent from local persistent memory.",
)
def mao_recall_context(
    agent_id: str = Field(description="The agent ID to recall context for"),
    key: str = Field(default="", description="Specific key to recall, or empty for all context"),
) -> dict[str, Any]:
    conn = _ensure_db()
    if key:
        row = conn.execute(
            "SELECT key, value, stored_at FROM context_memory WHERE agent_id = ? AND key = ?",
            (agent_id, key),
        ).fetchone()
        conn.close()
        if row:
            return {"agent_id": agent_id, "context": {"key": row[0], "value": row[1], "stored_at": row[2]}}
        return {"agent_id": agent_id, "context": None, "message": "No context found for this key."}

    rows = conn.execute(
        "SELECT key, value, stored_at FROM context_memory WHERE agent_id = ? ORDER BY stored_at DESC",
        (agent_id,),
    ).fetchall()
    conn.close()
    return {
        "agent_id": agent_id,
        "context_entries": [{"key": r[0], "value": r[1], "stored_at": r[2]} for r in rows],
        "total": len(rows),
    }


@mcp.tool(
    name="mao_proof_log",
    description="Append a proof entry to the MAO audit log. Every agent action must produce evidence.",
)
def mao_proof_log(
    agent_id: str = Field(description="Agent that performed the action"),
    action: str = Field(description="What was done"),
    evidence: str = Field(description="Proof of completion (exit code, file path, hash, URL)"),
) -> dict[str, str]:
    now = datetime.now(timezone.utc).isoformat()
    _log_audit("proof", {"agent_id": agent_id, "action": action, "evidence": evidence, "ts": now})
    return {"status": "logged", "ts": now, "agent_id": agent_id}


@mcp.tool(
    name="mao_language_route",
    description="Route a message through the SA Language Engine — detect language, "
    "translate labels, and return multilingual response envelope.",
)
def mao_language_route(
    message: str = Field(description="The message to process"),
    preferred_language: str = Field(default="", description="Preferred language ID (e.g., 'zu-za', 'xh-za', 'af-za')"),
    domain: str = Field(default="general", description="Domain context: general, jobs, utilities"),
) -> dict[str, Any]:
    _msg = message if isinstance(message, str) else str(message)
    _pref = preferred_language if isinstance(preferred_language, str) else ""
    _domain = domain if isinstance(domain, str) else "general"
    try:
        from kopano.language_runtime import detect_language, build_multilingual_response
        from kopano.sa_access import build_access_plan

        lang_response = build_multilingual_response(
            _msg,
            preferred_language=_pref or None,
            domain=_domain,
        )
        access_plan = build_access_plan(preferred_language=_pref or None)

        _log_audit("language_route", {
            "detected": lang_response["language"]["id"],
            "domain": _domain,
        })

        return {
            "language": lang_response["language"],
            "translation": lang_response["translation"],
            "labels": lang_response["response_labels"],
            "glossary": lang_response["glossary_terms"],
            "access_mode": access_plan["recommended_mode"],
            "quality": lang_response["quality"],
        }
    except ImportError:
        return {
            "error": "kopano.language_runtime not available — run from repo root",
            "fallback": "en-za",
        }


@mcp.tool(
    name="mao_philosophy_check",
    description="Run the agent philosophy gate against a proposed action. "
    "Returns pass/fail against the three-question realism gate.",
)
def mao_philosophy_check(
    action_description: str = Field(description="Describe the proposed action"),
    has_proof: bool = Field(description="Does this action produce verifiable evidence?"),
    survives_constraints: bool = Field(description="Does this survive offline/load-shedding/data-residency?"),
) -> dict[str, Any]:
    registry = _load_swarm_registry()
    philosophy = registry.get("philosophy", {})
    gate = philosophy.get("agent_gate", [])

    accommodates_realism = has_proof and survives_constraints
    passes = accommodates_realism

    return {
        "action": action_description,
        "gate_questions": gate,
        "answers": {
            "accommodates_realism": accommodates_realism,
            "has_proof": has_proof,
            "survives_constraints": survives_constraints,
        },
        "verdict": "SHIP" if passes else "HOLD — fails realism gate",
        "hierarchy": philosophy.get("hierarchy", "Realism > Aesthetics (accommodates, not versus)"),
    }


# ─── TSAP (Teacher–Student Apprenticeship — MAO lane) ───────────────────────


def _tsap_str(v: Any, default: str = "") -> str:
    return v if isinstance(v, str) else default


@mcp.tool(
    name="mao_tsap_student_turn",
    description="MAO Student lane (Cassy): route + execute student turn for a Kopano-Phu department.",
)
def mao_tsap_student_turn(
    department_id: str = Field(description="kopano_labs_experimentation | ama_phu_creativity"),
    message: str = Field(description="Student task message"),
    intent: str = Field(default="execute", description="MAO routing intent"),
) -> dict[str, Any]:
    from kopano.phu_apprenticeship import departments_from_config, student_submit
    from kopano.mao_dispatch import execute_task

    dept_id = _tsap_str(department_id)
    msg = _tsap_str(message)
    exec_result = execute_task(_tsap_str(intent, "execute"), msg)
    submit = student_submit(
        department_id=dept_id,
        student_agent="cassy",
        action=msg,
        evidence=f"mao_execute:{exec_result.get('execution_mode')}",
        lane="mao",
    )
    return {"execute": exec_result, "tsap_submit": submit}


@mcp.tool(
    name="mao_tsap_teacher_turn",
    description="MAO Teacher lane (Cassey / Operational General): teacher review for department.",
)
def mao_tsap_teacher_turn(
    department_id: str = Field(description="Department id"),
    approve: bool = Field(description="Approve student work"),
    teacher_note: str = Field(default="", description="Teacher note"),
) -> dict[str, Any]:
    from kopano.phu_apprenticeship import departments_from_config, teacher_review
    from kopano.mao_dispatch import execute_task

    dept = next((d for d in departments_from_config() if d["id"] == _tsap_str(department_id)), None)
    teacher_id = (dept or {}).get("mao_teacher", "cassey")
    intent = "teach" if approve else "review"
    exec_result = execute_task(intent, _tsap_str(teacher_note) or f"Review department {department_id}")
    review = teacher_review(
        department_id=_tsap_str(department_id),
        teacher_agent=teacher_id,
        approve=approve,
        teacher_note=_tsap_str(teacher_note),
        lane="mao",
    )
    return {"execute": exec_result, "tsap_review": review}


@mcp.tool(
    name="mao_blackmask_drill",
    description="Black Mask drill on swarm agent — 15 Commandments + 5 Pillars (MAO lane).",
)
def mao_blackmask_drill(
    agent_id: str = Field(description="Agent to drill"),
) -> dict[str, Any]:
    from kopano.phu_apprenticeship import blackmask_drill
    return blackmask_drill(_tsap_str(agent_id))


@mcp.tool(
    name="mao_department_status",
    description="Kopano-Phu department students + TSAP + BlackMask runtime status.",
)
def mao_department_status() -> dict[str, Any]:
    from kopano.phu_apprenticeship import apprenticeship_status
    return apprenticeship_status()


@mcp.tool(
    name="mao_begin_department_students",
    description="Begin student operations in all departments with BlackMask drills.",
)
def mao_begin_department_students(
    run_blackmask: bool = Field(default=True, description="Run BlackMask per student"),
) -> dict[str, Any]:
    from kopano.phu_apprenticeship import begin_department_students
    return begin_department_students(run_blackmask=run_blackmask)


@mcp.tool(
    name="mao_agent_build_poc_validate",
    description="Run 19-gate agent-building PoC proof (same as CI job agent-build-poc).",
)
def mao_agent_build_poc_validate() -> dict[str, Any]:
    from kopano.agent_build_poc_validate import validate_agent_build_poc
    return validate_agent_build_poc(write_report=True)


@mcp.tool(
    name="mao_kpefs_status",
    description="KPEFS status — vectors, operating mesh, graduation bar.",
)
def mao_kpefs_status() -> dict[str, Any]:
    from kopano.kpefs_router import kpefs_status
    return kpefs_status()


@mcp.tool(
    name="mao_operating_mesh_status",
    description="Phase 3 operating mesh — flagship assignments and PoC receipts.",
)
def mao_operating_mesh_status() -> dict[str, Any]:
    from kopano.operating_mesh import operating_mesh_status
    return operating_mesh_status()


@mcp.tool(
    name="mao_graduation_bar_status",
    description="Phase 5 graduation bar — verified production; drill/operating ≠ graduated.",
)
def mao_graduation_bar_status() -> dict[str, Any]:
    from kopano.graduation_bar import graduation_bar_status
    return graduation_bar_status()


@mcp.tool(
    name="mao_steward_lane_status",
    description="KC Save|Watch + Cassy execute steward lane status.",
)
def mao_steward_lane_status() -> dict[str, Any]:
    from kopano.steward_lane import steward_lane_status
    return steward_lane_status()


@mcp.tool(
    name="mao_steward_lane_activate",
    description="Activate KC+Cassy steward lane — profile, trust, Identi, Guardian.",
)
def mao_steward_lane_activate(
    note: str = Field(default="", description="Optional steward trust note"),
    department_id: str = Field(default="kopano_labs_experimentation"),
) -> dict[str, Any]:
    from kopano.steward_lane import run_steward_lane_activate
    return run_steward_lane_activate(note=note, department_id=department_id)


@mcp.tool(
    name="mao_external_swarm_status",
    description="CMD-03 Kimi/external swarm receipt lane status.",
)
def mao_external_swarm_status() -> dict[str, Any]:
    from kopano.external_swarm_lane import external_swarm_lane_status
    return external_swarm_lane_status()


@mcp.tool(
    name="mao_kpefs_closure_status",
    description="KPEFS internal vs external closure dashboard.",
)
def mao_kpefs_closure_status() -> dict[str, Any]:
    from kopano.external_swarm_lane import kpefs_closure_status
    return kpefs_closure_status()


@mcp.tool(
    name="mao_kpefs_full_gate",
    description="KPEFS Phases 0-5 full gate (bracket + mesh + graduation + PoC).",
)
def mao_kpefs_full_gate() -> dict[str, Any]:
    import json
    import subprocess
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    proc = subprocess.run(
        [sys.executable, str(root / "scripts" / "kc_kpefs_full_gate.py"), "--json"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=300,
    )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"verdict": "FAIL", "exit_code": proc.returncode, "stdout": (proc.stdout or "")[:400]}


@mcp.tool(
    name="mao_lpm_attach",
    description="Attach LPM/LPH + KPEFS + biblical STEM pattern metadata to a message (MAO logical layer).",
)
def mao_lpm_attach(
    message: str = Field(description="Task message"),
    intent: str = Field(default="execute", description="MAO intent hint"),
) -> dict[str, Any]:
    from kopano.lpm_lph_engine import attach_lpm_to_mao
    return attach_lpm_to_mao(_tsap_str(message), intent=_tsap_str(intent, "execute"))


@mcp.tool(
    name="mao_guardian_flow",
    description="Guardian AI Flow on MAO surface — same as tsap_guardian_flow.",
)
def mao_guardian_flow(
    department_id: str = Field(description="Department id"),
    action: str = Field(description="Action"),
    evidence: str = Field(description="Evidence"),
    run_blackmask: bool = Field(default=True),
    teacher_approve: bool | None = Field(default=None),
    teacher_note: str = Field(default=""),
) -> dict[str, Any]:
    from kopano.lpm_lph_engine import operate_guardian_flow
    return operate_guardian_flow(
        department_id=_tsap_str(department_id),
        action=_tsap_str(action),
        evidence=_tsap_str(evidence),
        run_blackmask=run_blackmask,
        teacher_approve=teacher_approve,
        teacher_note=_tsap_str(teacher_note),
    )


@mcp.tool(
    name="mao_identi_flow",
    description="Identi AI Flow on MAO surface — LPM/LPH then Guardian handoff.",
)
def mao_identi_flow(
    department_id: str = Field(description="Department id"),
    action: str = Field(description="Action"),
    evidence: str = Field(description="Evidence"),
    identi_agent: str = Field(default="identi_cursor"),
) -> dict[str, Any]:
    from kopano.lpm_lph_engine import operate_identi_flow
    return operate_identi_flow(
        department_id=_tsap_str(department_id),
        action=_tsap_str(action),
        evidence=_tsap_str(evidence),
        identi_agent=_tsap_str(identi_agent, "identi_cursor"),
    )


@mcp.tool(
    name="mao_eco_poc_guide",
    description="Eco-Friendly PoC guide — Rosen (M,R)+Δ, 32.8% doctrine; validate WITH internal oracles, not world acceptance.",
)
def mao_eco_poc_guide() -> dict[str, Any]:
    from kopano.eco_poc_validate import poc_doctrine_payload
    return poc_doctrine_payload()


@mcp.tool(
    name="mao_eco_poc_validate",
    description="Validate PoC on MAO lane — same internal oracles as TSAP eco_poc_validate.",
)
def mao_eco_poc_validate(
    agent_id: str = Field(description="KP or APE catalog agent id"),
    claim: str = Field(description="Bounded creative claim"),
    model: str = Field(description="Rosen M — model / procedure"),
    relation: str = Field(default="", description="Rosen R — instrument or observable"),
    baseline: str = Field(default=""),
    observed: str = Field(default=""),
    unit: str = Field(default=""),
    evidence: str = Field(default="", description="Receipt path or jsonl"),
    anticipated_delta: str = Field(default="", description="Rosen Δ tip — state before run"),
    livelihood_ids: list[str] = Field(default_factory=list),
) -> dict[str, Any]:
    from kopano.eco_poc_validate import validate_eco_poc
    return validate_eco_poc(
        agent_id=_tsap_str(agent_id),
        claim=_tsap_str(claim),
        model=_tsap_str(model),
        relation=_tsap_str(relation),
        baseline=_tsap_str(baseline),
        observed=_tsap_str(observed),
        unit=_tsap_str(unit),
        evidence=_tsap_str(evidence),
        anticipated_delta=_tsap_str(anticipated_delta),
        livelihood_ids=livelihood_ids or None,
    )


# ─── MCP RESOURCES ───────────────────────────────────────────────────────────


@mcp.resource(
    "resource://mao/registry",
    name="swarm_registry",
    description="The full swarm agent registry from SWARM_AGENTS.json",
)
def get_registry():
    return json.dumps(_load_swarm_registry(), indent=2)


@mcp.resource(
    "resource://mao/philosophy",
    name="agent_philosophy",
    description="The codified agent philosophy — Realism accommodates Aesthetics",
)
def get_philosophy():
    registry = _load_swarm_registry()
    return json.dumps(registry.get("philosophy", {}), indent=2)


@mcp.resource(
    "resource://mao/triad",
    name="servitude_triad",
    description="The Servitude Triad: grit, realism, aesthetics",
)
def get_triad():
    registry = _load_swarm_registry()
    return json.dumps({
        "triad": registry.get("triad", []),
        "servitude": registry.get("servitude", ""),
    }, indent=2)


# ─── ENTRYPOINT ──────────────────────────────────────────────────────────────


if __name__ == "__main__":
    mcp.run(transport="stdio")
