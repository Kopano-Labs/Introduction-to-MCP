from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

from .config import settings
from .database import record_creator_event


def _mask(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def status() -> Dict[str, Any]:
    observation_base = settings.observation_braintrust_base_url or settings.braintrust_base_url
    observation_path = settings.observation_braintrust_events_path or settings.braintrust_events_path
    return {
        "braintrust": {
            "configured": bool(settings.braintrust_api_key and settings.braintrust_project_id),
            "project_id": settings.braintrust_project_id,
            "default_project": settings.braintrust_default_project or settings.braintrust_project_id,
            "api_key_masked": _mask(settings.braintrust_api_key),
            "endpoint": (
                f"{settings.braintrust_base_url.rstrip('/')}{settings.braintrust_events_path}"
                if settings.braintrust_events_path
                else None
            ),
        },
        "observation": {
            "configured": bool(
                settings.observation_braintrust_api_key and settings.observation_braintrust_project_id
            ),
            "project_id": settings.observation_braintrust_project_id,
            "api_key_masked": _mask(settings.observation_braintrust_api_key),
            "endpoint": f"{observation_base.rstrip('/')}{observation_path}" if observation_path else None,
        },
    }


def _post_event(
    *,
    api_key: str,
    project_id: str,
    base_url: str,
    path: str,
    event: Dict[str, Any],
) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}{path}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"project_id": project_id, "event": event}
    with httpx.Client(timeout=20) as client:
        response = client.post(url, headers=headers, json=payload)
    return {
        "ok": response.is_success,
        "status_code": response.status_code,
        "url": url,
        "response_text": response.text[:1000],
    }


def log_eval(
    *,
    name: str,
    input_text: str,
    output_text: str,
    score: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    event = {
        "type": "eval",
        "name": name,
        "input": input_text,
        "output": output_text,
        "score": score,
        "metadata": metadata or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    record_creator_event("braintrust_eval", metadata=json.dumps(event, ensure_ascii=False))

    if not (settings.braintrust_api_key and settings.braintrust_project_id):
        return {"ok": True, "remote_skipped": True, "reason": "Braintrust Phase 5 config missing in environment.", "event": event}
    if not settings.braintrust_events_path:
        return {
            "ok": True,
            "remote_skipped": True,
            "reason": "Set BRAINTRUST_EVENTS_PATH in .env to enable remote posting.",
            "event": event,
        }

    try:
        remote = _post_event(
            api_key=settings.braintrust_api_key,
            project_id=settings.braintrust_project_id,
            base_url=settings.braintrust_base_url,
            path=settings.braintrust_events_path,
            event=event,
        )
        return {"ok": remote["ok"], "remote": remote, "event": event}
    except Exception as e:
        return {"ok": False, "error": f"Remote Braintrust eval failed: {e}", "event": event}


def log_observation(
    *,
    event_name: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    event = {
        "type": "observation",
        "name": event_name,
        "metadata": metadata or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    record_creator_event("braintrust_observation", metadata=json.dumps(event, ensure_ascii=False))

    api_key = settings.observation_braintrust_api_key
    project_id = settings.observation_braintrust_project_id
    if not (api_key and project_id):
        return {
            "ok": True,
            "remote_skipped": True,
            "reason": "Observation Braintrust Phase 6 config missing in environment.",
            "event": event,
        }

    base_url = settings.observation_braintrust_base_url or settings.braintrust_base_url
    path = settings.observation_braintrust_events_path or settings.braintrust_events_path
    if not path:
        return {
            "ok": True,
            "remote_skipped": True,
            "reason": "Set OBSERVATION_BRAINTRUST_EVENTS_PATH or BRAINTRUST_EVENTS_PATH in .env to enable remote posting.",
            "event": event,
        }
    try:
        remote = _post_event(
            api_key=api_key,
            project_id=project_id,
            base_url=base_url,
            path=path,
            event=event,
        )
        return {"ok": remote["ok"], "remote": remote, "event": event}
    except Exception as e:
        return {"ok": False, "error": f"Remote Braintrust observation failed: {e}", "event": event}
