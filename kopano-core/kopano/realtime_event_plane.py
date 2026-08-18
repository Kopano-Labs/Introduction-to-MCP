"""Persistent, transport-neutral KPGS realtime event plane.

The event plane is an observable distribution surface. It never owns canonical
business state and never retries CRUD mutations. Durable journal persistence
supports reconnect/resume while live transports remain disposable.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import threading
from typing import Any, Callable, Iterable, Mapping


class RealtimeEventError(ValueError):
    """Base event-plane contract error."""


class UnauthorizedScope(RealtimeEventError):
    """Raised when a principal requests an unauthorized stream scope."""


class EventConflict(RealtimeEventError):
    """Raised when an event/idempotency key is reused for different content."""


class CursorExpired(RealtimeEventError):
    """Raised when a resume cursor predates retained replay history."""

    def __init__(self, oldest_cursor: int):
        super().__init__(
            f"resume cursor expired; oldest available cursor is {oldest_cursor}"
        )
        self.oldest_cursor = oldest_cursor


@dataclass(frozen=True)
class EventScope:
    tenant_id: str
    domain_id: str
    session_id: str
    task_id: str | None = None

    def validate(self) -> None:
        for name in ("tenant_id", "domain_id", "session_id"):
            if not str(getattr(self, name)).strip():
                raise RealtimeEventError(f"{name} is required")
        if self.task_id is not None and not str(self.task_id).strip():
            raise RealtimeEventError("task_id cannot be blank")


@dataclass(frozen=True)
class PersistedEvent:
    """Canonical renter envelope plus a server-issued replay cursor."""

    cursor: int
    envelope: Mapping[str, Any]

    @property
    def event_id(self) -> str:
        return str(self.envelope["event_id"])

    @property
    def event_kind(self) -> str:
        return str(self.envelope["event_kind"])

    @property
    def tenant_id(self) -> str:
        return str(self.envelope["tenant_id"])

    @property
    def domain_id(self) -> str:
        return str(self.envelope["domain_id"])

    @property
    def session_id(self) -> str:
        return str(self.envelope["session_id"])

    @property
    def task_id(self) -> str:
        return str(self.envelope["task_id"])

    def as_dict(self) -> dict[str, Any]:
        data = dict(self.envelope)
        data["cursor"] = self.cursor
        # The renter schema's optional sequence belongs to the producer. If it
        # is absent, expose the replay cursor as transport ordering metadata.
        data.setdefault("sequence", self.cursor)
        return data


@dataclass
class Subscription:
    subscription_id: str
    scope: EventScope
    queue: asyncio.Queue[PersistedEvent]
    last_cursor: int
    overflowed: bool = False
    dropped_noncritical: int = 0


Authorizer = Callable[[Mapping[str, Any], EventScope], bool]


def default_scope_authorizer(
    principal: Mapping[str, Any], scope: EventScope
) -> bool:
    """Fail closed unless the principal can observe this tenant/domain."""

    if not principal or not principal.get("is_active", True):
        return False
    if principal.get("god_mode") or principal.get("role") == "admin":
        return True
    if principal.get("tenant_id") != scope.tenant_id:
        return False
    allowed = principal.get("allowed_domains", ())
    return (
        principal.get("domain_id") == scope.domain_id
        or "*" in allowed
        or scope.domain_id in allowed
    )


class RealtimeEventPlane:
    """SQLite replay journal with bounded, non-authoritative live fan-out."""

    NONCRITICAL_EVENT_KINDS = {"task.progress", "presence", "domain.health"}
    REQUIRED_FIELDS = (
        "event_id",
        "event_kind",
        "tenant_id",
        "domain_id",
        "session_id",
        "task_id",
        "renter_id",
        "correlation_id",
        "lease_id",
        "payload",
    )

    def __init__(
        self,
        database_path: str | Path = ":memory:",
        *,
        max_events_per_stream: int = 1000,
        queue_limit: int = 64,
        authorizer: Authorizer = default_scope_authorizer,
    ) -> None:
        if max_events_per_stream < 1:
            raise ValueError("max_events_per_stream must be >= 1")
        if queue_limit < 1:
            raise ValueError("queue_limit must be >= 1")
        self.database_path = str(database_path)
        if self.database_path != ":memory:":
            Path(self.database_path).expanduser().resolve().parent.mkdir(
                parents=True, exist_ok=True
            )
        self.max_events_per_stream = max_events_per_stream
        self.queue_limit = queue_limit
        self.authorizer = authorizer
        self._lock = threading.RLock()
        self._subscribers: dict[str, Subscription] = {}
        self._connection = sqlite3.connect(
            self.database_path, check_same_thread=False
        )
        self._connection.row_factory = sqlite3.Row
        self._init_db()

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def _init_db(self) -> None:
        with self._lock:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS realtime_events (
                    tenant_id TEXT NOT NULL,
                    domain_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    cursor INTEGER NOT NULL,
                    event_id TEXT NOT NULL UNIQUE,
                    idempotency_key TEXT,
                    fingerprint TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, domain_id, session_id, cursor)
                );
                CREATE UNIQUE INDEX IF NOT EXISTS ux_realtime_idempotency
                    ON realtime_events(
                        tenant_id, domain_id, session_id, idempotency_key
                    )
                    WHERE idempotency_key IS NOT NULL;
                CREATE INDEX IF NOT EXISTS ix_realtime_stream
                    ON realtime_events(
                        tenant_id, domain_id, session_id, cursor
                    );
                CREATE INDEX IF NOT EXISTS ix_realtime_task_stream
                    ON realtime_events(
                        tenant_id, domain_id, session_id, task_id, cursor
                    );
                """
            )
            self._connection.commit()

    @staticmethod
    def _fingerprint(envelope: Mapping[str, Any]) -> str:
        # issued_at is observation time, not idempotency identity. A retried
        # producer may reconstruct the same governed event later without turning
        # that harmless timestamp difference into an event conflict.
        canonical = {
            key: value
            for key, value in envelope.items()
            if key not in {"cursor", "issued_at"}
        }
        encoded = json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @classmethod
    def _validate_envelope(cls, envelope: Mapping[str, Any]) -> None:
        missing = [field for field in cls.REQUIRED_FIELDS if field not in envelope]
        if missing:
            raise RealtimeEventError(
                f"missing required event fields: {', '.join(missing)}"
            )
        for field in cls.REQUIRED_FIELDS[:-1]:
            if not str(envelope[field]).strip():
                raise RealtimeEventError(f"{field} cannot be blank")
        if not isinstance(envelope["payload"], Mapping):
            raise RealtimeEventError("payload must be an object")

    @staticmethod
    def _stream(scope: EventScope) -> tuple[str, str, str]:
        scope.validate()
        return scope.tenant_id, scope.domain_id, scope.session_id

    @staticmethod
    def _decode(row: sqlite3.Row | Mapping[str, Any]) -> PersistedEvent:
        payload = json.loads(str(row["event_json"]))
        cursor = int(payload.pop("cursor"))
        return PersistedEvent(cursor=cursor, envelope=payload)

    def publish(self, envelope: Mapping[str, Any]) -> PersistedEvent:
        """Persist one observation and fan it out without blocking producers."""

        self._validate_envelope(envelope)
        scope = EventScope(
            str(envelope["tenant_id"]),
            str(envelope["domain_id"]),
            str(envelope["session_id"]),
        )
        stream = self._stream(scope)
        fingerprint = self._fingerprint(envelope)
        event_id = str(envelope["event_id"])
        idempotency_key = (
            str(envelope["idempotency_key"])
            if envelope.get("idempotency_key")
            else None
        )

        with self._lock:
            existing = self._connection.execute(
                "SELECT fingerprint, event_json FROM realtime_events WHERE event_id = ?",
                (event_id,),
            ).fetchone()
            if existing is None and idempotency_key is not None:
                existing = self._connection.execute(
                    """SELECT fingerprint, event_json FROM realtime_events
                       WHERE tenant_id = ? AND domain_id = ? AND session_id = ?
                         AND idempotency_key = ?""",
                    (*stream, idempotency_key),
                ).fetchone()
            if existing is not None:
                if str(existing["fingerprint"]) != fingerprint:
                    raise EventConflict(
                        "event or idempotency key was reused with different content"
                    )
                return self._decode(existing)

            next_cursor = int(
                self._connection.execute(
                    """SELECT COALESCE(MAX(cursor), 0) + 1 AS next_cursor
                       FROM realtime_events
                       WHERE tenant_id = ? AND domain_id = ? AND session_id = ?""",
                    stream,
                ).fetchone()["next_cursor"]
            )
            stored = dict(envelope)
            stored.setdefault("protocol_version", "1.0")
            stored["issued_at"] = str(
                envelope.get("issued_at")
                or datetime.now(timezone.utc).isoformat()
            )
            stored["cursor"] = next_cursor
            event_json = json.dumps(
                stored, sort_keys=True, separators=(",", ":"), default=str
            )
            self._connection.execute(
                """INSERT INTO realtime_events
                   (tenant_id, domain_id, session_id, task_id, cursor,
                    event_id, idempotency_key, fingerprint, event_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    *stream,
                    str(envelope["task_id"]),
                    next_cursor,
                    event_id,
                    idempotency_key,
                    fingerprint,
                    event_json,
                ),
            )
            self._connection.execute(
                """DELETE FROM realtime_events
                   WHERE tenant_id = ? AND domain_id = ? AND session_id = ?
                     AND cursor <= (
                       SELECT COALESCE(MAX(cursor), 0) - ?
                       FROM realtime_events
                       WHERE tenant_id = ? AND domain_id = ? AND session_id = ?
                     )""",
                (*stream, self.max_events_per_stream, *stream),
            )
            self._connection.commit()
            event = PersistedEvent(
                cursor=next_cursor,
                envelope={key: value for key, value in stored.items() if key != "cursor"},
            )
            subscribers = tuple(self._subscribers.values())

        for subscription in subscribers:
            if not self._matches(subscription.scope, event):
                continue
            try:
                subscription.queue.put_nowait(event)
            except asyncio.QueueFull:
                if event.event_kind in self.NONCRITICAL_EVENT_KINDS:
                    subscription.dropped_noncritical += 1
                else:
                    # The event is durable. Force reconnect/replay instead of
                    # blocking producer work or pretending delivery succeeded.
                    subscription.overflowed = True
        return event

    @staticmethod
    def _matches(scope: EventScope, event: PersistedEvent) -> bool:
        return (
            scope.tenant_id == event.tenant_id
            and scope.domain_id == event.domain_id
            and scope.session_id == event.session_id
            and (scope.task_id is None or scope.task_id == event.task_id)
        )

    def replay(
        self,
        scope: EventScope,
        *,
        after_cursor: int = 0,
        limit: int = 200,
    ) -> list[PersistedEvent]:
        """Replay retained observations after a server-issued stream cursor."""

        stream = self._stream(scope)
        if after_cursor < 0:
            raise RealtimeEventError("after_cursor must be >= 0")
        if limit < 1 or limit > 1000:
            raise RealtimeEventError("limit must be between 1 and 1000")

        with self._lock:
            bounds = self._connection.execute(
                """SELECT MIN(cursor) AS oldest, MAX(cursor) AS newest
                   FROM realtime_events
                   WHERE tenant_id = ? AND domain_id = ? AND session_id = ?""",
                stream,
            ).fetchone()
            oldest = bounds["oldest"]
            if (
                oldest is not None
                and after_cursor > 0
                and after_cursor < int(oldest) - 1
            ):
                raise CursorExpired(int(oldest))

            if scope.task_id is None:
                rows = self._connection.execute(
                    """SELECT event_json FROM realtime_events
                       WHERE tenant_id = ? AND domain_id = ? AND session_id = ?
                         AND cursor > ?
                       ORDER BY cursor ASC LIMIT ?""",
                    (*stream, after_cursor, limit),
                ).fetchall()
            else:
                rows = self._connection.execute(
                    """SELECT event_json FROM realtime_events
                       WHERE tenant_id = ? AND domain_id = ? AND session_id = ?
                         AND task_id = ? AND cursor > ?
                       ORDER BY cursor ASC LIMIT ?""",
                    (*stream, scope.task_id, after_cursor, limit),
                ).fetchall()
        return [self._decode(row) for row in rows]

    def latest_cursor(self, scope: EventScope) -> int:
        stream = self._stream(scope)
        with self._lock:
            if scope.task_id is None:
                row = self._connection.execute(
                    """SELECT COALESCE(MAX(cursor), 0) AS cursor
                       FROM realtime_events
                       WHERE tenant_id = ? AND domain_id = ? AND session_id = ?""",
                    stream,
                ).fetchone()
            else:
                row = self._connection.execute(
                    """SELECT COALESCE(MAX(cursor), 0) AS cursor
                       FROM realtime_events
                       WHERE tenant_id = ? AND domain_id = ? AND session_id = ?
                         AND task_id = ?""",
                    (*stream, scope.task_id),
                ).fetchone()
        return int(row["cursor"])

    def subscribe(
        self,
        principal: Mapping[str, Any],
        scope: EventScope,
        *,
        after_cursor: int = 0,
        subscription_id: str,
    ) -> tuple[Subscription, list[PersistedEvent]]:
        scope.validate()
        if not self.authorizer(principal, scope):
            raise UnauthorizedScope(
                "principal is not authorized for requested realtime scope"
            )
        if not subscription_id.strip():
            raise RealtimeEventError("subscription_id is required")

        subscription = Subscription(
            subscription_id=subscription_id,
            scope=scope,
            queue=asyncio.Queue(maxsize=self.queue_limit),
            last_cursor=after_cursor,
        )
        # Register first. A racing event may appear both in replay and the live
        # queue, but a duplicate is recoverable; registering after replay would
        # create an unrecoverable event-loss window.
        with self._lock:
            self._subscribers[subscription_id] = subscription
        try:
            replay = self.replay(scope, after_cursor=after_cursor)
        except Exception:
            self.unsubscribe(subscription_id)
            raise
        return subscription, replay

    def unsubscribe(self, subscription_id: str) -> None:
        with self._lock:
            self._subscribers.pop(subscription_id, None)

    def acknowledge(self, subscription: Subscription, cursor: int) -> None:
        if cursor < subscription.last_cursor:
            raise RealtimeEventError("acknowledged cursor cannot move backwards")
        if cursor > self.latest_cursor(subscription.scope):
            raise RealtimeEventError(
                "acknowledged cursor is ahead of the server stream"
            )
        subscription.last_cursor = cursor

    def polling_fallback(
        self,
        principal: Mapping[str, Any],
        scope: EventScope,
        *,
        after_cursor: int = 0,
        limit: int = 200,
    ) -> dict[str, Any]:
        if not self.authorizer(principal, scope):
            raise UnauthorizedScope(
                "principal is not authorized for requested realtime scope"
            )
        events = self.replay(scope, after_cursor=after_cursor, limit=limit)
        latest = self.latest_cursor(scope)
        resume_cursor = events[-1].cursor if events else after_cursor
        return {
            "transport": "polling",
            "events": [event.as_dict() for event in events],
            "resume_cursor": resume_cursor,
            "latest_cursor": latest,
            "caught_up": resume_cursor >= latest,
        }


def make_event(
    *,
    event_id: str,
    event_kind: str,
    tenant_id: str,
    domain_id: str,
    session_id: str,
    task_id: str,
    correlation_id: str,
    payload: Mapping[str, Any],
    renter_id: str = "kpgs.control-plane",
    lease_id: str = "lease:local-control-plane",
    idempotency_key: str | None = None,
    evidence: Iterable[Mapping[str, Any]] = (),
    **canonical_fields: Any,
) -> dict[str, Any]:
    """Construct a renter-compatible event without claiming provider execution."""

    event: dict[str, Any] = {
        "protocol_version": "1.0",
        "event_id": event_id,
        "event_kind": event_kind,
        "tenant_id": tenant_id,
        "domain_id": domain_id,
        "session_id": session_id,
        "task_id": task_id,
        "renter_id": renter_id,
        "correlation_id": correlation_id,
        "lease_id": lease_id,
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "payload": dict(payload),
        "evidence": [dict(item) for item in evidence],
    }
    if idempotency_key:
        event["idempotency_key"] = idempotency_key
    for key, value in canonical_fields.items():
        if key not in {"cursor", "issued_at"} and value is not None:
            event[key] = value
    return event
