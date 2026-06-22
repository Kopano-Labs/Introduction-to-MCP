import logging
import json
from pathlib import Path
from datetime import datetime, UTC

# Create a base directory for audit logs
AUDIT_DIR = Path("audit_logs")
AUDIT_DIR.mkdir(exist_ok=True)

def _log_path(filename: str) -> Path:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    return AUDIT_DIR / filename


def _write_line(filename: str, entry: dict) -> None:
    path = _log_path(filename)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")

def log_reasoning(agent: str, step: str, content: str) -> None:
    """
    Record a reasoning step taken by an agent.
    Example: ORCH thinking about mentor responses.
    """
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "agent": agent,
        "step": step,
        "reasoning": content
    }
    _write_line("reasoning.jsonl", entry)

def log_execution(agent: str, action: str, result: str) -> None:
    """
    Record an execution step taken by an agent.
    Example: ORCH calling a mentor and capturing the response.
    """
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "agent": agent,
        "action": action,
        "result": result
    }
    _write_line("execution.jsonl", entry)
