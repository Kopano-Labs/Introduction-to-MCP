"""
MAO dispatch — route and execute swarm agent turns (LPM layer).

Realism accommodates aesthetics: mesh agents use LiteLLM when configured;
structural roles (brain, teacher, orchestrator) use proof-bounded deterministic replies.
"""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MAO_SERVER_PATH = REPO_ROOT / "CLI" / "mao_server.py"
SWARM_AGENTS_PATH = REPO_ROOT / "docs" / "swarm-ops" / "agents" / "SWARM_AGENTS.json"

_MAO_MOD: Any = None

EXECUTE_PERSONAS: dict[str, str] = {
    "cassy": (
        "You are Cassy, lead student on the Kopano lane. Execute with receipts. "
        "Prefer MCP tools and bounded claims. Women in Tech diaspora mission."
    ),
    "cassey": (
        "You are Cassey, teacher. Guide the student, cite teacher_review patterns, "
        "and never confuse drill promotion with graduation."
    ),
    "kc": (
        "You are KC, the brain ledger. You do not execute — you record doctrine, "
        "opinion, and proof-gated entries for the Main Brain."
    ),
    "kopano": (
        "You are the Kopano studio alias bound to Cassy. Mirror student execution "
        "with offline-first and sovereignty constraints."
    ),
    "mirror_warden": (
        "You are Mirror Warden — orchestrator parity. Enforce policy, compliance, "
        "and parity between swarm slots and Cassy apprenticeship."
    ),
    "kc_apprentice": (
        "You are KC Apprentice. Run student audit drills — practice, homework, "
        "exercises — always under Cassey review."
    ),
    "operational_general": (
        "You are Operational General. Validate against BLACK_MASS_PROTOCOL; "
        "coordinate teacher-swarm execution with proof before mass dispatch."
    ),
    "pipeline_drone": (
        "You are 3D Pipeline Drone. Transform, render, batch pipelines — mesh worker "
        "under Cassy student lane."
    ),
    "claude": "You are Claude mesh — reason, analyze, draft strategy with citations when possible.",
    "grok": "You are Grok mesh — research, verify facts, trends, and live data angles.",
    "gemini": "You are Gemini mesh — multimodal reasoning, diagrams, visual design context.",
    "copilot": "You are Copilot mesh — scaffold, snippets, Microsoft-aligned execution patterns.",
    "cf_cloud": (
        "You are CF (cloud), LPM operator for autonomic_ai_flows. Orchestrate agents, "
        "flows, schedules — never skip the philosophy gate."
    ),
}

MESH_PROVIDER_IDS = frozenset({"claude", "grok", "gemini", "copilot"})


def _load_mao_module():
    global _MAO_MOD
    if _MAO_MOD is not None:
        return _MAO_MOD
    spec = importlib.util.spec_from_file_location("mao_server", MAO_SERVER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _MAO_MOD = mod
    return mod


def _load_registry() -> dict[str, Any]:
    if not SWARM_AGENTS_PATH.exists():
        return {"agents": []}
    with SWARM_AGENTS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _agent_record(registry: dict[str, Any], agent_id: str) -> dict[str, Any] | None:
    for agent in registry.get("agents", []):
        if agent.get("id") == agent_id:
            return agent
    return None


def _deterministic_reply(agent_id: str, record: dict[str, Any], intent: str, message: str) -> str:
    from .phu_boot_governance import mesh_agent_ids
    from .kpgs_renter_entry import block_holder_brief

    persona = EXECUTE_PERSONAS.get(agent_id, f"You are swarm agent {agent_id}.")
    block_prefix = ""
    if agent_id in mesh_agent_ids() or agent_id in ("mirror_warden", "operational_general"):
        brief = block_holder_brief(agent_id=agent_id)
        block_prefix = (
            f"{brief.get('bracket', '[KPGS_BLOCK_HOLDER]')} BLOCK HOLDER — "
            f"{brief.get('tell_renters', '')[:220]} "
        )
    role = record.get("role", "unknown")
    apprenticeship = record.get("apprenticeship") or {}
    apprentice_note = ""
    if apprenticeship.get("student"):
        apprentice_note = f" Apprenticeship: student={apprenticeship.get('student')}, teacher={apprenticeship.get('teacher', 'cassey')}."
    if record.get("executes") is False:
        return (
            f"{block_prefix}"
            f"[{record.get('display_name', agent_id)} · {role}] Ledger-only lane. "
            f"No execution — store opinion in Main Brain after proof. "
            f"Intent={intent}. Message summary: {message[:200]}"
        )
    return (
        f"{block_prefix}"
        f"[{record.get('display_name', agent_id)} · {role}] {persona}{apprentice_note} "
        f"Intent={intent}. Task: {message[:500]} "
        "Next: produce a receipt (exit code, JSONL row, or artifact path) before marking complete."
    )


def _try_mesh_llm(agent_id: str, intent: str, message: str, record: dict[str, Any]) -> tuple[str | None, str]:
    from .agent_manager import load_agents
    from .llm import call_ai_litellm

    agents = load_agents()
    agent = agents.get(agent_id)
    if not agent or not agent.api_key:
        return None, ""
    persona = EXECUTE_PERSONAS.get(agent_id, agent.persona)
    prompt = (
        f"{persona}\n\n"
        f"MAO intent: {intent}\n"
        f"Operator message: {message}\n\n"
        "Respond in under 180 words. Structure: 1-line realism check, then numbered next steps. "
        "If you cannot verify a claim, say HOLD and name the proof needed."
    )
    try:
        from litellm import completion

        model_map = {
            "gemini": "gemini/gemini-pro",
            "grok": "xai/grok-4-1-fast",
            "xai": "xai/grok-4-1-fast",
            "copilot": "openai/gpt-4o",
            "openai": "openai/gpt-4o",
            "anthropic": "anthropic/claude-3-5-sonnet-20241022",
        }
        model = model_map.get(agent.provider.lower(), agent.model)
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            api_key=agent.api_key,
            temperature=0.25,
            max_tokens=512,
            timeout=12,
        )
        text = response.choices[0].message.content.strip()
        return agent.model, text
    except Exception:
        return None, ""


def _attach_kpefs(route_payload: dict[str, Any], message: str, intent: str = "execute") -> dict[str, Any]:
    try:
        from .kpefs_router import route_vector

        kpefs = route_vector(message)
        route_payload["kpefs"] = {
            "active_vector": kpefs.get("active_vector"),
            "rank": kpefs.get("rank"),
            "department_hint": kpefs.get("department_hint"),
            "bracket_snippet": kpefs.get("bracket_snippet"),
            "scores": kpefs.get("scores"),
        }
    except Exception:
        route_payload["kpefs"] = None
    try:
        from .lpm_lph_engine import attach_lpm_to_mao

        route_payload["lpm"] = attach_lpm_to_mao(message, intent=intent)
    except Exception:
        route_payload["lpm"] = None
    return route_payload


def _attach_spawn_swfus(route_payload: dict[str, Any], *, agent_id: str, message: str) -> dict[str, Any]:
    try:
        from .kpgs_spawn_swarm import dispatch_spawn_event, spawn_agent_by_id

        if spawn_agent_by_id(agent_id):
            event = dispatch_spawn_event(agent_id=agent_id, message=message)
            route_payload["spawn_event"] = event
            route_payload["swfus"] = event.get("swfus")
            if not event.get("proceed"):
                route_payload["severed"] = True
                route_payload["severance"] = event.get("severance")
    except Exception:
        route_payload["swfus"] = None
    return route_payload


def route_task(intent: str, message: str) -> dict[str, Any]:
    from .kpgs_renter_entry import attach_hood_entry

    mao = _load_mao_module()
    payload = mao.mao_route(intent=intent, message=message)
    payload = _attach_kpefs(payload, message, intent=intent)
    routed = (payload.get("routed_agent") or {}).get("agent_id", "anonymous")
    payload = _attach_spawn_swfus(payload, agent_id=routed, message=message)
    return attach_hood_entry(payload, renter_id=f"mao_route:{routed}")


def swarm_status() -> dict[str, Any]:
    mao = _load_mao_module()
    return mao.mao_swarm_status()


def execute_task(intent: str, message: str, force_agent_id: str = "") -> dict[str, Any]:
    """Route (unless forced) then execute one agent turn."""
    from .kpgs_renter_entry import attach_hood_entry

    start = time.perf_counter()
    registry = _load_registry()
    mao = _load_mao_module()

    if force_agent_id:
        rec = _agent_record(registry, force_agent_id) or {}
        route_payload = _attach_kpefs(
            {
                "routed_agent": {
                    "agent_id": force_agent_id,
                    "display_name": rec.get("display_name", force_agent_id),
                    "role": rec.get("role", "forced"),
                    "confidence": 1.0,
                    "forced": True,
                },
                "message": message,
                "philosophy_gate": registry.get("philosophy", {}).get("agent_gate", []),
                "lpm_status": "autonomic",
            },
            message,
            intent,
        )
    else:
        route_payload = _attach_kpefs(
            mao.mao_route(intent=intent, message=message), message, intent=intent
        )

    routed = route_payload.get("routed_agent") or {}
    agent_id = routed.get("agent_id", "cassy")
    route_payload = _attach_spawn_swfus(route_payload, agent_id=agent_id, message=message)
    if route_payload.get("severed"):
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        sever = route_payload.get("severance") or {}
        return attach_hood_entry(
            {
                "routed_agent": routed,
                "intent": intent,
                "message": message,
                "response": sever.get("summary", "[RIGHTEOUS_SEVERANCE] agent recycled — forensic archived"),
                "model_used": "spawn_event_bus",
                "execution_mode": "severed",
                "latency_ms": latency_ms,
                "spawn_event": route_payload.get("spawn_event"),
                "swfus": route_payload.get("swfus"),
                "severance": sever,
            },
            renter_id=f"mao_execute:{agent_id}",
        )
    record = _agent_record(registry, agent_id) or {"id": agent_id, "display_name": agent_id, "role": "unknown"}

    model_used: str | None = None
    response = ""
    execution_mode = "deterministic"

    if agent_id in MESH_PROVIDER_IDS:
        model_used, llm_text = _try_mesh_llm(agent_id, intent, message, record)
        if llm_text:
            response = llm_text
            execution_mode = "mesh_llm"

    if not response:
        response = _deterministic_reply(agent_id, record, intent, message)

    latency_ms = round((time.perf_counter() - start) * 1000, 2)

    mao.mao_proof_log(
        agent_id=agent_id,
        action=f"mao_execute:{intent}",
        evidence=f"mode={execution_mode};latency_ms={latency_ms}",
    )

    return attach_hood_entry(
        {
            "routed_agent": routed,
            "intent": intent,
            "message": message,
            "response": response,
            "model_used": model_used or execution_mode,
            "execution_mode": execution_mode,
            "latency_ms": latency_ms,
            "philosophy_gate": route_payload.get("philosophy_gate", []),
            "registry_role": record.get("role"),
            "kpefs": route_payload.get("kpefs"),
            "swfus": route_payload.get("swfus"),
        },
        renter_id=f"mao_execute:{agent_id}",
    )
