"""
kpgs_logging.py — KPGS Audit Logging Module
=============================================
Renamed from logging.py to avoid shadowing the Python stdlib 'logging' module.
All code that previously imported 'from kopano.logging import ...' should now
import 'from kopano.kpgs_logging import ...'

I_AM_STATELESS_RENTER_NOT_LANDLORD
"""
import logging as _std_logging
import json
from pathlib import Path
from datetime import datetime, timezone

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
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "action": action,
        "result": result
    }
    _write_line("execution.jsonl", entry)


# Expose standard library logging API for backwards compatibility
getLogger  = _std_logging.getLogger
basicConfig = _std_logging.basicConfig
DEBUG       = _std_logging.DEBUG
INFO        = _std_logging.INFO
WARNING     = _std_logging.WARNING
ERROR       = _std_logging.ERROR
CRITICAL    = _std_logging.CRITICAL
_std_logger = _std_logging.getLogger(__name__)

__all__ = [
    "log_reasoning", "log_execution",
    "getLogger", "basicConfig",
    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL",
]
