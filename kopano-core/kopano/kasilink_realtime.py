"""KasiLink adapter for the canonical KPGS realtime event plane.

This module makes the existing domain workflow observable. It does not own
KasiLink business state and cannot authorize business mutations.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
import uuid
from typing import Any

from fastapi import APIRouter, Header, HTTPException, WebSocket, WebSocketDisconnect

from .operator_auth import resolve_bearer
from .realtime_event_plane import (
    CursorExpired,
    EventScope,
    RealtimeEventError,
    RealtimeEventPlane,
    UnauthorizedScope,
    make_event,
)

router = APIRouter()

realtime_event_plane = RealtimeEventPlane(
    Path(os.environ.get("KPGS_REALTIME_DB", ".orch_data/realtime-events.db")),
    max_events_per_stream=int(os.environ.get("KPGS_REALTIME_HISTORY", "1000")),
    queue_limit=int(os.environ.get("KPGS_REALTIME_QUEUE_LIMIT", "64")),
)


def _principal(authorization: str | None) -> dict[str, Any]:
    user = resolve_bearer(authorization)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="A valid Kopano session is required for realtime state.",
        )
    principal = dict(user)
    principal.update(
        tenant_id="kopano",
        domain_id="kasilink",
        allowed_domains=("kasilink",),
    )
    return principal


def _publish(
    *,
    kind: str,
    ids: dict[str, str],
    suffix: str,
    payload: dict[str, Any],
    **canonical_fields: Any,
):
    return realtime_event_plane.publish(
        make_event(
            event_id=f"kasilink-{ids['task_id']}-{suffix}",
            event_kind=kind,
            tenant_id="kopano",
            domain_id="kasilink",
            session_id=ids["session_id"],
            task_id=ids["task_id"],
            correlation_id=ids["correlation_id"],
            renter_id="kasilink.domain-adapter",
            lease_id="lease:kasilink-domain-adapter",
            idempotency_key=f"{ids['task_id']}:{suffix}",
            payload=payload,
            governing_spec_ref="governance/kpgs-vnext/realtime/EVENT_PLANE.md",
            **canonical_fields,
        )
    )


def begin_match(
    session_id: str | None = None,
    task_id: str | None = None,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    """Start observable state for the existing KasiLink gig-match workflow."""

    ids = {
        "session_id": session_id or f"session-{uuid.uuid4().hex}",
        "task_id": task_id or f"match-{uuid.uuid4().hex}",
        "correlation_id": correlation_id or f"corr-{uuid.uuid4().hex}",
    }
    accepted = _publish(
        kind="task.accepted",
        ids=ids,
        suffix="accepted",
        payload={"state": "working", "workflow": "gig-match"},
    )
    _publish(
        kind="task.started",
        ids=ids,
        suffix="started",
        payload={"state": "working", "workflow": "gig-match"},
    )
    return {**ids, "resume_cursor": accepted.cursor}


def complete_match(ids: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    completed = _publish(
        kind="task.completed",
        ids=ids,
        suffix="completed",
        payload={"state": "done", "workflow": "gig-match", "result": result},
    )
    return {
        "session_id": ids["session_id"],
        "task_id": ids["task_id"],
        "correlation_id": ids["correlation_id"],
        "resume_cursor": completed.cursor,
        "transport_authority": "none",
    }


def fail_match(ids: dict[str, Any], exc: Exception) -> None:
    _publish(
        kind="task.failed",
        ids=ids,
        suffix="failed",
        payload={"state": "failed", "workflow": "gig-match"},
        failure={
            "code": "execution_failed",
            "recoverability": "retry",
            "message": type(exc).__name__,
        },
    )


@router.get("/events")
def polling_fallback(
    session_id: str,
    task_id: str | None = None,
    after_cursor: int = 0,
    limit: int = 200,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    scope = EventScope("kopano", "kasilink", session_id, task_id)
    try:
        return realtime_event_plane.polling_fallback(
            _principal(authorization),
            scope,
            after_cursor=after_cursor,
            limit=limit,
        )
    except UnauthorizedScope as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except CursorExpired as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "resume_cursor_expired",
                "oldest_cursor": exc.oldest_cursor,
                "canonical_snapshot_required": True,
                "next_action": "refresh the domain workflow before resuming deltas",
            },
        ) from exc
    except RealtimeEventError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.websocket("/events/ws")
async def websocket_events(websocket: WebSocket) -> None:
    """WebSocket-first stream with first-message auth, replay and heartbeat."""

    session_id = websocket.query_params.get("session_id", "").strip()
    task_id = websocket.query_params.get("task_id")
    try:
        after_cursor = int(websocket.query_params.get("after_cursor", "0"))
    except ValueError:
        await websocket.close(code=4400)
        return
    if not session_id:
        await websocket.close(code=4400)
        return

    await websocket.accept()
    try:
        auth = await asyncio.wait_for(websocket.receive_json(), timeout=8)
    except (asyncio.TimeoutError, WebSocketDisconnect):
        await websocket.close(code=4401)
        return
    if auth.get("type") != "auth":
        await websocket.close(code=4401)
        return

    user = resolve_bearer(f"Bearer {str(auth.get('access_token', ''))}")
    if not user:
        await websocket.send_json({"type": "auth_failed", "state": "offline"})
        await websocket.close(code=4401)
        return
    principal = dict(user)
    principal.update(
        tenant_id="kopano",
        domain_id="kasilink",
        allowed_domains=("kasilink",),
    )
    scope = EventScope("kopano", "kasilink", session_id, task_id)
    subscription_id = f"ws-{uuid.uuid4().hex}"

    try:
        subscription, replay = realtime_event_plane.subscribe(
            principal,
            scope,
            after_cursor=after_cursor,
            subscription_id=subscription_id,
        )
    except UnauthorizedScope:
        await websocket.send_json({"type": "scope_denied", "state": "offline"})
        await websocket.close(code=4403)
        return
    except CursorExpired as exc:
        await websocket.send_json(
            {
                "type": "snapshot_required",
                "state": "reconnecting",
                "oldest_cursor": exc.oldest_cursor,
            }
        )
        await websocket.close(code=4409)
        return

    highwater = after_cursor
    for event in replay:
        await websocket.send_json({"type": "event", "event": event.as_dict()})
        highwater = max(highwater, event.cursor)
    await websocket.send_json(
        {
            "type": "ready",
            "state": "ready",
            "resume_cursor": highwater,
            "transport": "websocket",
        }
    )

    receive_task = asyncio.create_task(websocket.receive_json())
    event_task = asyncio.create_task(subscription.queue.get())
    try:
        while True:
            if subscription.overflowed:
                await websocket.send_json(
                    {
                        "type": "reconnect_required",
                        "state": "reconnecting",
                        "reason": "backpressure",
                        "resume_cursor": subscription.last_cursor,
                    }
                )
                await websocket.close(code=1013)
                return

            done, _ = await asyncio.wait(
                {receive_task, event_task},
                timeout=20,
                return_when=asyncio.FIRST_COMPLETED,
            )
            if not done:
                await websocket.send_json(
                    {
                        "type": "heartbeat",
                        "state": "ready",
                        "resume_cursor": subscription.last_cursor,
                    }
                )
                continue

            if receive_task in done:
                try:
                    message = receive_task.result()
                except WebSocketDisconnect:
                    return
                receive_task = asyncio.create_task(websocket.receive_json())
                kind = message.get("type")
                if kind == "ack":
                    try:
                        realtime_event_plane.acknowledge(
                            subscription, int(message.get("cursor", -1))
                        )
                    except (RealtimeEventError, TypeError, ValueError) as exc:
                        await websocket.send_json(
                            {"type": "ack_rejected", "reason": str(exc)}
                        )
                elif kind == "reauth":
                    refreshed = resolve_bearer(
                        f"Bearer {str(message.get('access_token', ''))}"
                    )
                    if not refreshed:
                        await websocket.close(code=4401)
                        return
                    check = dict(refreshed)
                    check.update(
                        tenant_id="kopano",
                        domain_id="kasilink",
                        allowed_domains=("kasilink",),
                    )
                    if not realtime_event_plane.authorizer(check, scope):
                        await websocket.close(code=4403)
                        return
                    await websocket.send_json(
                        {"type": "reauthenticated", "state": "ready"}
                    )
                elif kind == "ping":
                    await websocket.send_json(
                        {"type": "pong", "state": "ready"}
                    )
                else:
                    await websocket.send_json(
                        {
                            "type": "command_rejected",
                            "reason": "business mutations require a governed command endpoint",
                        }
                    )

            if event_task in done:
                event = event_task.result()
                event_task = asyncio.create_task(subscription.queue.get())
                if event.cursor <= highwater:
                    continue
                await websocket.send_json(
                    {"type": "event", "event": event.as_dict()}
                )
    finally:
        receive_task.cancel()
        event_task.cancel()
        realtime_event_plane.unsubscribe(subscription_id)
