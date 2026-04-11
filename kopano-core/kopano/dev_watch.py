from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings


SESSION_RULES = [
    "Acknowledge assignment before starting work.",
    "Post progress updates at meaningful milestones.",
    "Record blockers immediately with concrete next steps.",
    "Do not bypass review and verification steps.",
    "Log final outcome with evidence (tests/build/output).",
]


def _normalize_owner(owner: str) -> str:
    value = owner.strip().upper()
    if value == "DEV_S":
        return "DEV_3 (BACKGROUND)"
    return value


def _watch_target(owner: str) -> bool:
    expected = _normalize_owner(settings.dev_watch_owner)
    return _normalize_owner(owner) == expected


def _ensure_session_rules_file() -> None:
    target = Path(settings.dev_watch_session_rules_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return
    content = "# Orch Session Rules\n\n" + "\n".join(f"- {rule}" for rule in SESSION_RULES) + "\n"
    target.write_text(content, encoding="utf-8")


def _record_communication_request(*, room_id: int | None, task_id: int | None, owner: str, event_type: str) -> None:
    _ensure_session_rules_file()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "owner": owner,
        "room_id": room_id,
        "task_id": task_id,
        "event_type": event_type,
        "request": "Please confirm compliance with Orch session rules and post your progress update.",
        "session_rules_file": settings.dev_watch_session_rules_path,
    }
    target = Path(settings.dev_watch_comms_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def record_dev_activity(
    *,
    event_type: str,
    room_id: int | None,
    task_id: int | None,
    owner: str,
    payload: dict[str, Any] | None = None,
) -> None:
    if not _watch_target(owner):
        return

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "room_id": room_id,
        "task_id": task_id,
        "owner": owner,
        "payload": payload or {},
    }
    target = Path(settings.dev_watch_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    _record_communication_request(room_id=room_id, task_id=task_id, owner=owner, event_type=event_type)


def read_recent_dev_activity(limit: int = 50) -> list[dict[str, Any]]:
    target = Path(settings.dev_watch_path)
    if not target.exists():
        return []
    lines = target.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    return rows[-limit:]


def read_recent_comms(limit: int = 50) -> list[dict[str, Any]]:
    target = Path(settings.dev_watch_comms_path)
    if not target.exists():
        return []
    lines = target.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    return rows[-limit:]

