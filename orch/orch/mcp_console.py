from __future__ import annotations

from typing import Any


TOPIC_RULES = [
    {
        "topic": "ide",
        "keywords": ["ide", "vscode", "cursor", "editor", "jetbrains", "xcode"],
        "summary": "Use Orch Labs as the control plane and connect the IDE as a workspace-aware client.",
        "actions": [
            "Open Orch Forge for room-level coordination and task dispatch.",
            "Use Orch Code for repo-aware learning and coding guidance.",
            "Keep tool calls and skill usage visible through the Labs API layer.",
        ],
    },
    {
        "topic": "os",
        "keywords": ["windows", "mac", "linux", "ubuntu", "operating system", "os"],
        "summary": "Use the same MCP-facing orchestration flow across Windows, macOS, and Linux, with Orch acting as the stable layer above OS differences.",
        "actions": [
            "Keep IDE and shell commands environment-aware.",
            "Expose universal chat, skills, and CLI guidance from Orch Labs.",
            "Avoid OS-specific assumptions in workflows until runtime selection is explicit.",
        ],
    },
    {
        "topic": "cli",
        "keywords": ["cli", "terminal", "command", "shell"],
        "summary": "Use the CLI for direct execution, automation, and low-friction power-user flows.",
        "actions": [
            "Use `orch serve launch` for simulations.",
            "Use `orch agents` to manage configured agents.",
            "Surface common commands in the MCP console reply when users ask how to do something.",
        ],
    },
    {
        "topic": "skills",
        "keywords": ["skill", "skills", "command pack", "workflow"],
        "summary": "Treat skills as reusable operating knowledge that can be discovered, taught, and applied consistently.",
        "actions": [
            "Show which skill family the user likely needs.",
            "Tie skill suggestions back to Orch Code and the Labs registry.",
            "Preserve a clean boundary between planning, execution, and review skills.",
        ],
    },
    {
        "topic": "mcp",
        "keywords": ["mcp", "connector", "connectors", "tool", "tools", "server"],
        "summary": "Use MCP as the expansion layer for tools, connectors, and cross-system actions.",
        "actions": [
            "Recommend the right API or tool surface first.",
            "Explain whether the workflow belongs in MCP, CLI, or Labs UI.",
            "Keep the user-facing reply grounded in current repo capabilities.",
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
        "summary": "Use Orch Labs as the front door, Orch Forge for collaboration, Orch Code for coding, and MCP/CLI for execution.",
        "actions": [
            "Clarify whether the user is asking about IDE use, OS setup, CLI commands, skills, or MCP tools.",
            "Route them to the narrowest working surface.",
            "Keep the answer execution-oriented instead of abstract.",
        ],
    }


def answer_mcp_console(message: str) -> dict[str, Any]:
    rule = _pick_topic(message)
    response = (
        f"{rule['summary']} "
        f"Recommended next moves: 1. {rule['actions'][0]} 2. {rule['actions'][1]} 3. {rule['actions'][2]}"
    )
    return {
        "input": message,
        "topic": rule["topic"],
        "response": response,
        "suggested_actions": rule["actions"],
        "surfaces": ["Orch Labs", "Orch Forge", "Orch Code", "CLI", "MCP"],
    }
