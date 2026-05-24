"""
Read-only SQLite audit helpers for KC / Cassy datalake (Protocol 13 evidence lane).

No writes. Fixed SQL only — no user-supplied query fragments.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

# log_type CHECK on audit_logs (must stay in sync with database.py)
_AUDIT_LOG_TYPES = frozenset(
    {
        "reasoning",
        "execution",
        "tool_call",
        "tool_result",
        "system",
        "security_alert",
        "execution_correction",
    }
)


def _repo_root() -> Path:
    """kopano-core/ directory (parent of kopano package)."""
    return Path(__file__).resolve().parents[2]


def resolve_db_path() -> Path:
    env = os.environ.get("KC_SQLITE_PATH") or os.environ.get("KC_SQLITE_AUDIT_PATH")
    if env:
        return Path(env).expanduser().resolve()
    try:
        from kopano.config import settings

        p = Path(settings.db_path)
        if not p.is_absolute():
            p = (_repo_root() / p).resolve()
        return p
    except Exception:
        return (_repo_root() / "db" / "datalake.db").resolve()


def connect_readonly() -> sqlite3.Connection:
    path = resolve_db_path()
    if not path.exists():
        raise FileNotFoundError(f"SQLite database not found at {path}")
    uri = f"file:{path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def _cap(n: int, *, hi: int = 500) -> int:
    return max(1, min(int(n), hi))


def audit_logs_tail_json(last_n: int = 50) -> str:
    n = _cap(last_n)
    conn = connect_readonly()
    try:
        cur = conn.execute(
            """
            SELECT id, discussion_id, round_num, model, agent_id, log_type,
                   length(message) AS message_len,
                   length(prompt) AS prompt_len,
                   value_score, override_score, timestamp
            FROM audit_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (n,),
        )
        rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
    return json.dumps({"ok": True, "db": str(resolve_db_path()), "rows": rows}, indent=2)


def audit_logs_by_type_json(log_type: str, last_n: int = 50) -> str:
    if log_type not in _AUDIT_LOG_TYPES:
        return json.dumps(
            {
                "ok": False,
                "error": "invalid_log_type",
                "allowed": sorted(_AUDIT_LOG_TYPES),
            },
            indent=2,
        )
    n = _cap(last_n)
    conn = connect_readonly()
    try:
        cur = conn.execute(
            """
            SELECT id, discussion_id, round_num, model, agent_id,
                   substr(message, 1, 400) AS message_preview,
                   substr(prompt, 1, 200) AS prompt_preview,
                   timestamp
            FROM audit_logs
            WHERE log_type = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (log_type, n),
        )
        rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
    return json.dumps({"ok": True, "log_type": log_type, "rows": rows}, indent=2)


def mcp_console_tail_json(last_n: int = 50) -> str:
    n = _cap(last_n)
    conn = connect_readonly()
    try:
        cur = conn.execute(
            """
            SELECT m.id, m.session_id, m.role, m.topic,
                   length(m.content) AS content_len,
                   m.latency_ms, m.model_used, m.created_at
            FROM mcp_console_messages m
            ORDER BY m.id DESC
            LIMIT ?
            """,
            (n,),
        )
        rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
    return json.dumps({"ok": True, "rows": rows}, indent=2)


def sqlite_schema_snapshot_json() -> str:
    conn = connect_readonly()
    try:
        cur = conn.execute(
            "SELECT name, type FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
        )
        objects = [dict(r) for r in cur.fetchall()]
        cur2 = conn.execute("PRAGMA page_count")
        page_count = cur2.fetchone()[0]
        cur3 = conn.execute("PRAGMA page_size")
        page_size = cur3.fetchone()[0]
    finally:
        conn.close()
    approx_bytes = page_count * page_size
    return json.dumps(
        {
            "ok": True,
            "db": str(resolve_db_path()),
            "objects": objects,
            "approx_size_bytes": approx_bytes,
        },
        indent=2,
    )


def dispatch(tool_name: str, tool_input: dict[str, Any]) -> str:
    if tool_name == "kc_sqlite_audit_logs_tail":
        return audit_logs_tail_json(int(tool_input.get("last_n", 50)))
    if tool_name == "kc_sqlite_audit_logs_by_type":
        return audit_logs_by_type_json(
            str(tool_input.get("log_type", "")).strip(),
            int(tool_input.get("last_n", 50)),
        )
    if tool_name == "kc_sqlite_mcp_console_tail":
        return mcp_console_tail_json(int(tool_input.get("last_n", 50)))
    if tool_name == "kc_sqlite_schema_snapshot":
        return sqlite_schema_snapshot_json()
    raise ValueError(f"unknown sqlite audit tool: {tool_name}")


def tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "kc_sqlite_audit_logs_tail",
            "description": "Read-only tail of audit_logs (reasoning/execution/tool rows) from the KC SQLite datalake.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "last_n": {
                        "type": "integer",
                        "description": "Max rows (1-500)",
                        "default": 50,
                    },
                },
            },
        },
        {
            "name": "kc_sqlite_audit_logs_by_type",
            "description": "Read-only filtered tail of audit_logs for one log_type (fixed enum; no raw SQL).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "log_type": {
                        "type": "string",
                        "description": "One of: reasoning, execution, tool_call, tool_result, system, security_alert, execution_correction",
                    },
                    "last_n": {"type": "integer", "default": 50},
                },
                "required": ["log_type"],
            },
        },
        {
            "name": "kc_sqlite_mcp_console_tail",
            "description": "Read-only tail of mcp_console_messages joined path (session metadata minimal).",
            "input_schema": {
                "type": "object",
                "properties": {"last_n": {"type": "integer", "default": 50}},
            },
        },
        {
            "name": "kc_sqlite_schema_snapshot",
            "description": "List sqlite_master objects + approximate DB size (read-only PRAGMA).",
            "input_schema": {"type": "object", "properties": {}},
        },
    ]


if __name__ == "__main__":
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "schema").lower()
    if cmd == "schema":
        print(sqlite_schema_snapshot_json())
    elif cmd == "audit":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        print(audit_logs_tail_json(n))
    elif cmd == "mcp":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        print(mcp_console_tail_json(n))
    else:
        print(
            json.dumps({"usage": "python sqlite_audit.py [schema|audit|mcp] [last_n]"}),
            file=sys.stderr,
        )
        raise SystemExit(2)
