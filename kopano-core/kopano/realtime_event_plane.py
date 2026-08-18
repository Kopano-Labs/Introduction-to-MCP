"""Persistent, transport-neutral KPGS realtime event plane.

The event plane is a read/distribution surface. It never owns canonical business
state and never retries authoritative CRUD mutations. Events are persisted so a
socket disconnect can be recovered with a server-issued cursor.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import asyncio
import hashlib
import json
from pathlib import Path
import sqlite3
import threading
from typing import Any, Callable, Iterable, Mapping


class RealtimeEventError(ValueError):
    """Base event-plane contract error."""


class UnauthorizedScope(RealtimeEventError):
    """Raised when a principal requests a scope it is not allowed to observe."""


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
    cursor: int
    event_id: str
    event_kind: str
    tenant_id: str
    domain_id: str
    session_id: str
    task_id: str
    correlation_id: str
    renter_id: str
    lease_id: str
    issued_at: str
    payload: Mapping[str, Any]
    idempotency_key: str | None = None
    source_sequence: int | None = None
    checkpoint_ref: str | None = None
    evidence: tuple[Mapping[str, Any], ...] = ()
    extras: Mapping[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "protocol_version": "1.0",
            "event_id": self.event_id,
            "event_kind": self.event_kind,
            "tenant_id": self.tenant_id,
            "domain_id": self.domain_id,
            "session_id": self.session_id,
            "task_id": self.task_id,
            "renter_id": self.renter_id,
            "correlation_id": self.correlation_id,
            "lease_id": self.lease_id,
            "issued_at": self.issued_at,
            "payload": dict(self.payload),
            "cursor": self.cursor,
            "sequence": (
                self.source_sequence
                if self.source_sequence is not None
                else self.cursor
            ),
        }
        if self.idempotency_key:
            data["idempotency_key"] = self.idempotency_key
        if self.checkpoint_ref:
            data["checkpoint_ref"] = self.checkpoint_ref
        if self.evidence:
            data["evidence"] = [dict(item) for item in self.evidence]
        if self.extras:
            for key, value in self.extras.items():
                if key not in data and key != "cursor":
                    data[key] = value
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
    """Fail-closed default scope authorization.

    Admin/God principals may observe all domains. Other principals must carry a
    matching tenant and either an exact domain or an allowed_domains grant.
    """

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
    """SQLite-backed replay journal with bounded live subscribers."""

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
        canonical = dict(envelope)
        canonical.pop("cursor", None)
        encoded = json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @classmethod
    def _validate_envelope(cls, envelope: Mapping[str, Any]) -> None:
        missing = [
            field for field in cls.REQUIRED_FIELDS if field not in envelope
        ]
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
    def _stream_params(scope: EventScope) -> tuple[str, str, str]:
        scope.validate()
        return scope.tenant_id, scope.domain_id, scope.session_id

    def publish(self, envelope: Mapping[str, Any]) -> PersistedEvent:
        """Persist one observation and fan it out without blocking producer work."""

        self._validate_envelope(envelope)
        scope = EventScope(
            str(envelope["tenant_id"]),
            str(envelope["domain_id"]),
            str(envelope["session_id"]),
        )
        stream = self._stream_params(scope)
        fingerprint = self._fingerprint(envelope)
        idempotency_key = envelope.get("idempotency_key")

        with self._lock:
            existing = self._connection.execute(
                "SELECT fingerprint, event_json FROM realtime_events "
                "WHERE event_id = ?",
                (str(envelope["event_id"]),),
            ).fetchone()
            if existing is None and idempotency_key:
                existing = self._connection.execute(
                    """SELECT fingerprint, event_json FROM realtime_events
                       WHERE tenant_id = ? AND domain_id = ? AND session_id = ?
                         AND idempotency_key = ?""",
                    (*stream, str(idempotency_key)),
                ).fetchone()
            if existing is not None:
                if existing["fingerprint"] != fingerprint:
                    raise EventConflict(
                        "event or idempotency key was reused with different content"
                    )
                return self._event_from_json(existing["event_json"])

            next_cursor = int(
                self._connection.execute(
                    """SELECT COALESCE(MAX(cursor), 0) + 1 AS next_cursor
                       FROM realtime_events
                       WHERE tenant_id = ? AND domain_id = ? AND session_id = ?""",
                    stream,
                ).fetchone()["next_cursor"]
            )
            issued_at = str(
                envelope.get("issued_at")
                or datetime.now(timezone.utc).isoformat()
            )
            event = PersistedEvent(
                cursor=next_cursor,
                event_id=str(envelope["event_id"]),
                event_kind=str(envelope["event_kind"]),
                tenant_id=scope.tenant_id,
                domain_id=scope.domain_id,
                session_id=scope.session_id,
                task_id=str(envelope["task_id"]),
                renter_id=str(envelope["renter_id"]),
                correlation_id=str(envelope["correlation_id"]),
                lease_id=str(envelope["lease_id"]),
                issued_at=issued_at,
                payload=dict(envelope["payload"]),
                idempotency_key=(
                    str(idempotency_key) if idempotency_key else None
                ),
                source_sequence=(
                    int(envelope["sequence"])
                    if envelope.get("sequence") is not None
                    else None
                ),
                checkpoint_ref=(
                    str(envelope["checkpoint_ref"])
                    if envelope.get("checkpoint_ref")
                    else None
                ),
                evidence=tuple(
                    dict(item)
                    for item in envelope.get("evidence", ())
                    if isinstance(item, Mapping)
                ),
                extras={
                    key: value
                    for key, value in envelope.items()
                    if key
                    not in {
                        "protocol_version",
                        "event_id",
                        "event_kind",
                        "tenant_id",
                        "domain_id",
                        "session_id",
                        "task_id",
                        "renter_id",
                        "correlation_id",
                        "lease_id",
                        "issued_at",
                        "payload",
                        "idempotency_key",
                        "sequence",
                        "checkpoint_ref",
                        "evidence",
                        "cursor",
                    }
                },
            )
            event_json = json.dumps(
                event.as_dict(), sort_keys=True, separators=(",", ":")
            )
            self._connection.execute(
                """INSERT INTO realtime_events
                   (tenant_id, domain_id, session_id, task_id, cursor,
                    event_id, idempotency_key, fingerprint, event_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    *stream,
                    event.task_id,
                    next_cursor,
                    event.event_id,
                    event.idempotency_key,
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
                    # Never block an authoritative producer. A slow consumer
                    # reconnects and replays from its last acknowledged cursor.
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

    @staticmethod
    def _event_from_json(raw: str) -> PersistedEvent:
        data = json.loads(raw)
        known = {
            "protocol_version",
            "event_id",
            "event_kind",
            "tenant_id",
            "domain_id",
            "session_id",
            "task_id",
            "renter_id",
            "correlation_id",
            "lease_id",
            "issued_at",
            "payload",
            "idempotency_key",
            "sequence",
            "checkpoint_ref",
            "evidence",
            "cursor",
        }
        return PersistedEvent(
            cursor=int(data["cursor"]),
            event_id=data["event_id"],
            event_kind=data["event_kind"],
            tenant_id=data["tenant_id"],
            domain_id=data["domain_id"],
            session_id=data["session_id"],
            task_id=data["task_id"],
            renter_id=data["renter_id"],
            correlation_id=data["correlation_id"],
            lease_id=data["lease_id"],
            issued_at=data["issued_at"],
            payload=data.get("payload", {}),
            idempotency_key=data.get("idempotency_key"),
            source_sequence=data.get("sequence"),
            checkpoint_ref=data.get("checkpoint_ref"),
            evidence=tuple(data.get("evidence", ())),
            extras={key: value for key, value in data.items() if key not in known},
        )

    def replay(
        self,
        scope: EventScope,
        *,
        after_cursor: int = 0,
        limit: int = 200,
    ) -> list[PersistedEvent]:
        """Replay retained observations after a server-issued cursor."""

        stream = self._stream_params(scope)
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
        return [self._event_from_json(row["event_json"]) for row in rows]

    def latest_cursor(self, scope: EventScope) -> int:
        stream = self._stream_params(scope)
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

        # Register first. A concurrent publish may then be both in replay and
        # the live queue, but duplicates are safe; registering after replay
        # would create a loss window, which is not acceptable.
        subscription = Subscription(
            subscription_id=subscription_id,
            scope=scope,
            queue=asyncio.Queue(maxsize=self.queue_limit),
            last_cursor=after_cursor,
        )
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
            raise RealtimeEventError(
                "acknowledged cursor cannot move backwards"
            )
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
        if key != "cursor" and value is not None:
            event[key] = value
    return event
