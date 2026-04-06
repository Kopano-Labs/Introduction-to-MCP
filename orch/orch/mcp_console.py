from __future__ import annotations

import time
from typing import Any

from .agent_manager import load_agents
from .database import get_db_connection, init_db
from .labs_registry import CLOUD_STACKS, CONNECTOR_WORKFLOWS, ORCH_INTERFACES
from .llm import call_ai_litellm


TOPIC_RULES = [
    {
        "topic": "ide",
        "keywords": ["ide", "vscode", "cursor", "editor", "jetbrains", "xcode"],
        "summary": "Use Orch Labs as the control plane and connect the IDE as a workspace-aware client.",
        "actions": [
            "Install the target IDE and link it to Orch Labs as the active workspace surface.",
            "Route repo-aware help through Orch Code so guidance stays grounded in current files.",
            "Use Forge rooms to coordinate edits, review, and open-file handoff.",
        ],
    },
    {
        "topic": "os",
        "keywords": ["windows", "mac", "linux", "ubuntu", "operating system", "os"],
        "summary": "Use the same Orch workflow across Windows, macOS, and Linux with runtime-aware install and command guidance.",
        "actions": [
            "Detect the operating system before suggesting shell or installer steps.",
            "Keep install instructions explicit for IDE, CLI, and connector setup.",
            "Use Orch Labs to normalize path, shell, and approval differences.",
        ],
    },
    {
        "topic": "cli",
        "keywords": ["cli", "terminal", "command", "shell"],
        "summary": "Use the CLI for direct execution, approvals, and automation while Orch Labs keeps the higher-level workflow visible.",
        "actions": [
            "Use `orch` as the execution entry point for launch, agents, tools, and logs.",
            "Keep shell actions tied to the current OS and project context.",
            "Show the narrowest working command instead of generic terminal advice.",
        ],
    },
    {
        "topic": "skills",
        "keywords": ["skill", "skills", "workflow", "skill.md"],
        "summary": "Treat skills as reusable operating knowledge that can be taught, discovered, and applied from Orch Labs.",
        "actions": [
            "Map each request to a focused skill rather than a broad capability bucket.",
            "Store reusable instructions in `SKILL.md` with trigger rules and references.",
            "Separate exploration, execution, verification, and review workflows.",
        ],
    },
    {
        "topic": "connectors",
        "keywords": ["connector", "connectors", "integration", "integrations"],
        "summary": "Use connector workflows for MCP, cloud, docs, and external systems with Orch Labs as the routing layer.",
        "actions": [
            "Select the connector based on the user goal, not the underlying vendor first.",
            "Keep approvals, credentials, and telemetry visible in Labs.",
            "Track which connectors accelerate creator throughput and demo readiness.",
        ],
    },
    {
        "topic": "cloud",
        "keywords": ["azure", "aws", "cloud", "demo day", "deployment"],
        "summary": "Use Azure as the primary demo-day expansion path and AWS as the secondary portability path.",
        "actions": [
            "Prioritize Azure interfaces for hosting, identity, search, and observability.",
            "Keep AWS support available for expansion, procurement flexibility, and event workloads.",
            "Document cloud workflows as connector-backed playbooks inside Orch Labs.",
        ],
    },
    {
        "topic": "mcp",
        "keywords": ["mcp", "server", "tool", "tools"],
        "summary": "Use MCP as the expansion layer for tools, connectors, and cross-system execution.",
        "actions": [
            "Recommend the right surface first: Labs UI, Forge, Orch Code, CLI, or MCP.",
            "Ground every reply in current repo capabilities and next implementation steps.",
            "Use model-backed orchestration when configured, with deterministic fallback when not.",
        ],
    },
]


def _pick_topic(message: str) -> dict[str, Any]:
    lower_message = message.lower()
    for rule in TOPIC_RULES:
        if any(keyword in lower_message for keyword in rule["keywords"]):
            return rule
    return {
        "topic": "general",
        "summary": "Use Orch Labs as the front door, Forge for creator execution, Orch Code for coding, and CLI/MCP for controlled execution.",
        "actions": [
            "Clarify whether the task is about install, execution, skills, connectors, or cloud rollout.",
            "Route the user to the narrowest working surface.",
            "Keep the answer operational and phase-oriented.",
        ],
    }


def _get_or_create_session(session_id: int | None) -> int:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    if session_id is None:
        cursor.execute("INSERT INTO mcp_console_sessions (surface) VALUES (?)", ("orch_labs",))
        session_id = cursor.lastrowid
        conn.commit()
    conn.close()
    return session_id


def _store_message(session_id: int, role: str, content: str, topic: str, latency_ms: int = 0, model_used: str | None = None) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO mcp_console_messages (session_id, role, topic, content, latency_ms, model_used)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (session_id, role, topic, content, latency_ms, model_used),
    )
    conn.commit()
    conn.close()


def _build_context(topic: str) -> str:
    interface_names = ", ".join(interface["name"] for interface in ORCH_INTERFACES)
    connector_names = ", ".join(workflow["name"] for workflow in CONNECTOR_WORKFLOWS)
    cloud_names = ", ".join(f"{stack['provider']}: {stack['name']}" for stack in CLOUD_STACKS)
    return (
        "You are Orch Labs MCP Console. "
        "Answer like an execution-oriented orchestration planner. "
        "Keep replies concise and practical. "
        f"Current Orch interfaces: {interface_names}. "
        f"Current connector workflows: {connector_names}. "
        f"Current cloud stacks: {cloud_names}. "
        f"Current topic: {topic}. "
        "Always include concrete next moves for IDE, OS, CLI, skills, and connectors when relevant. "
        "Prioritize Azure for demo-day readiness when cloud is relevant."
    )


def _model_backed_answer(message: str, topic: str) -> tuple[str | None, str]:
    agents = load_agents()
    preferred = ["orch", "copilot", "openai", "claude", "gemini"]
    for agent_id in preferred:
        agent = agents.get(agent_id)
        if not agent or not agent.api_key:
            continue
        prompt = (
            f"{_build_context(topic)}\n\n"
            f"User request: {message}\n\n"
            "Respond in under 170 words. "
            "Structure the answer as a short operational summary followed by compact numbered next steps."
        )
        return agent.model, call_ai_litellm(agent, prompt, temperature=0.2)
    return None, ""


def _fallback_answer(rule: dict[str, Any], message: str) -> str:
    actions = " ".join(f"{idx}. {action}" for idx, action in enumerate(rule["actions"], start=1))
    return (
        f"{rule['summary']} "
        "Orch should expose the same working mechanics across IDE, OS, CLI, skills, and connectors from Labs. "
        f"Recommended next moves: {actions}"
    )


def get_console_analytics() -> dict[str, Any]:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS count FROM mcp_console_sessions")
    sessions = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) AS count FROM mcp_console_messages WHERE role = 'user'")
    requests = cursor.fetchone()["count"]
    cursor.execute("SELECT AVG(latency_ms) AS average_latency_ms FROM mcp_console_messages WHERE role = 'assistant'")
    average_latency = cursor.fetchone()["average_latency_ms"] or 0
    cursor.execute(
        """
        SELECT topic, COUNT(*) AS count
        FROM mcp_console_messages
        WHERE role = 'user'
        GROUP BY topic
        ORDER BY count DESC, topic ASC
        """
    )
    topics = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {
        "sessions": sessions,
        "requests": requests,
        "average_latency_ms": round(float(average_latency), 2),
        "top_topics": topics,
    }


def answer_mcp_console(message: str, session_id: int | None = None) -> dict[str, Any]:
    rule = _pick_topic(message)
    session_id = _get_or_create_session(session_id)
    _store_message(session_id, "user", message, rule["topic"])
    started = time.perf_counter()
    model_used, response = _model_backed_answer(message, rule["topic"])
    if not response:
        response = _fallback_answer(rule, message)
    latency_ms = int((time.perf_counter() - started) * 1000)
    _store_message(session_id, "assistant", response, rule["topic"], latency_ms=latency_ms, model_used=model_used)
    return {
        "session_id": session_id,
        "input": message,
        "topic": rule["topic"],
        "response": response,
        "suggested_actions": rule["actions"],
        "surfaces": ["Orch Labs", "Orch Forge", "Orch Code", "CLI", "MCP", "Azure", "AWS"],
        "model_used": model_used or "deterministic-fallback",
        "analytics": get_console_analytics(),
    }
