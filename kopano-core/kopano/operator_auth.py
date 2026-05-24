"""Local operator sessions for Super God Mode (whole PWA + monorepo)."""

from __future__ import annotations

import json
import secrets
from pathlib import Path
from typing import Any

from fastapi import Header, HTTPException

from .runtime import is_frozen_runtime, user_data_dir

_sessions: dict[str, dict[str, Any]] = {}


def _session_file() -> Path:
    return user_data_dir() / "operator.session.json"


def create_session(user: dict[str, Any]) -> str:
    token = secrets.token_urlsafe(32)
    payload = {
        "id": user["id"],
        "email": user["email"],
        "full_name": user.get("full_name"),
        "role": user.get("role", "user"),
        "god_mode": bool(user.get("god_mode")),
        "is_active": bool(user.get("is_active", True)),
    }
    _sessions[token] = payload
    return token


def persist_desktop_session(token: str, user: dict[str, Any]) -> None:
    path = _session_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "access_token": token,
                "user": {
                    "id": user.get("id"),
                    "email": user["email"],
                    "role": user.get("role"),
                    "god_mode": bool(user.get("god_mode")),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def load_persisted_desktop_session() -> dict[str, Any] | None:
    path = _session_file()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    token = data.get("access_token")
    if not token or not isinstance(token, str):
        return None
    user = data.get("user")
    if isinstance(user, dict):
        _sessions[token] = {
            "id": user.get("id", 0),
            "email": user.get("email", ""),
            "full_name": user.get("full_name"),
            "role": user.get("role", "admin"),
            "god_mode": bool(user.get("god_mode")),
            "is_active": True,
        }
    return data


def resolve_bearer(authorization: str | None) -> dict[str, Any] | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        return None
    return _sessions.get(token)


def require_operator(
    authorization: str | None = Header(default=None, alias="Authorization"),
    *,
    god_only: bool = False,
) -> dict[str, Any]:
    user = resolve_bearer(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Super God sign-in required.")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account inactive.")
    if god_only and not user.get("god_mode"):
        raise HTTPException(status_code=403, detail="Super God Mode required for this action.")
    if god_only is False and user.get("role") != "admin" and not user.get("god_mode"):
        raise HTTPException(status_code=403, detail="Admin or God Mode required.")
    return user
