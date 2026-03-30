import logging
import json
from pathlib import Path
from datetime import datetime

# Create a base directory for audit logs
AUDIT_DIR = Path("audit_logs")
AUDIT_DIR.mkdir(exist_ok=True)

def _setup_logger(name: str, filename: str) -> logging.Logger:
    """
    Internal helper to configure a logger that writes JSON lines to a file.
    Each logger is dedicated to one type of log (reasoning or execution).
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # File handler writes to audit_logs/<filename>
    fh = logging.FileHandler(AUDIT_DIR / filename, mode="a", encoding="utf-8")
    formatter = logging.Formatter('%(message)s')  # raw JSON lines
    fh.setFormatter(formatter)

    # Avoid duplicate handlers if logger already exists
    if not logger.handlers:
        logger.addHandler(fh)

    return logger

# Two separate loggers: one for reasoning, one for execution
reasoning_logger = _setup_logger("reasoning", "reasoning.jsonl")
execution_logger = _setup_logger("execution", "execution.jsonl")

def log_reasoning(agent: str, step: str, content: str) -> None:
    """
    Record a reasoning step taken by an agent.
    Example: ORCH thinking about mentor responses.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent,
        "step": step,
        "reasoning": content
    }
    reasoning_logger.info(json.dumps(entry))

def log_execution(agent: str, action: str, result: str) -> None:
    """
    Record an execution step taken by an agent.
    Example: ORCH calling a mentor and capturing the response.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent,
        "action": action,
        "result": result
    }
    execution_logger.info(json.dumps(entry))
