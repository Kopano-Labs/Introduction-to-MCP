"""
Bookit 5s — Venue Steward (Tier-2 agentic helpers).

Local SQLite lock cache + optional HTTP probe to Next.js API (BOOKIT_API_BASE).
WWJD / Protocol 13: no silent success; fixed JSON contracts; bounded HTTP timeouts.
"""
from __future__ import annotations

import json
import math
import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

UTC = timezone.utc


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _local_db_path() -> Path:
    env = os.environ.get("BOOKIT_LOCAL_SQLITE")
    if env:
        return Path(env).expanduser().resolve()
    return (_repo_root() / "db" / "bookit_agent.db").resolve()


def _api_base() -> str:
    return (os.environ.get("BOOKIT_API_BASE") or "").rstrip("/")


def _http_timeout_s() -> float:
    return float(os.environ.get("BOOKIT_HTTP_TIMEOUT_S", "5"))


def init_bookit_db() -> None:
    path = _local_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS court_locks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venue_id TEXT NOT NULL,
                date TEXT NOT NULL,
                timeslot TEXT NOT NULL,
                correlation_id TEXT NOT NULL UNIQUE,
                user_id TEXT,
                status TEXT NOT NULL CHECK (
                    status IN ('pending', 'confirmed', 'released', 'expired')
                ),
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_court_locks_venue_slot
                ON court_locks (venue_id, date, timeslot, status);
            CREATE TABLE IF NOT EXISTS checkin_tokens (
                token_id TEXT PRIMARY KEY,
                venue_id TEXT NOT NULL,
                date TEXT NOT NULL,
                timeslot TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                user_id TEXT,
                issued_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                status TEXT NOT NULL CHECK (
                    status IN ('active', 'redeemed', 'revoked', 'expired')
                ),
                redeemed_at TEXT,
                redeemed_by_scanner TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_checkin_tokens_correlation
                ON checkin_tokens (correlation_id);
            CREATE INDEX IF NOT EXISTS idx_checkin_tokens_venue_date
                ON checkin_tokens (venue_id, date, status);
            """
        )
        conn.commit()
    finally:
        conn.close()


def _expire_stale_pending() -> None:
    now = datetime.now(UTC).isoformat()
    conn = sqlite3.connect(str(_local_db_path()))
    try:
        conn.execute(
            "UPDATE court_locks SET status = 'expired' WHERE status = 'pending' AND expires_at < ?",
            (now,),
        )
        conn.commit()
    finally:
        conn.close()


def _expire_stale_checkin_tokens() -> None:
    now = datetime.now(UTC).isoformat()
    conn = sqlite3.connect(str(_local_db_path()))
    try:
        conn.execute(
            """
            UPDATE checkin_tokens
            SET status = 'expired'
            WHERE status = 'active' AND expires_at < ?
            """,
            (now,),
        )
        conn.commit()
    finally:
        conn.close()


def _expires_at_passed(expires_at_raw: str | None, now_dt: datetime) -> bool:
    if not expires_at_raw:
        return False
    try:
        exp = datetime.fromisoformat(str(expires_at_raw).replace("Z", "+00:00"))
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=UTC)
        return exp < now_dt
    except (ValueError, TypeError):
        return False


def _active_lock_count(venue_id: str, date: str, timeslot: str) -> int:
    conn = sqlite3.connect(str(_local_db_path()))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(
            """
            SELECT COUNT(*) AS c FROM court_locks
            WHERE venue_id = ? AND date = ? AND timeslot = ?
              AND status IN ('pending', 'confirmed')
            """,
            (venue_id, date, timeslot),
        )
        return int(cur.fetchone()["c"])
    finally:
        conn.close()


def _day_lock_rows(venue_id: str, date: str) -> list[dict[str, Any]]:
    conn = sqlite3.connect(str(_local_db_path()))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(
            """
            SELECT timeslot, status, correlation_id, expires_at
            FROM court_locks
            WHERE venue_id = ? AND date = ?
              AND status IN ('pending', 'confirmed')
            ORDER BY timeslot
            """,
            (venue_id, date),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def _http_availability(venue_id: str, date: str, timeslot: str) -> dict[str, Any] | None:
    base = _api_base()
    if not base or not timeslot:
        return None
    qs = urlencode({"venue_id": venue_id, "date": date, "timeslot": timeslot})
    url = f"{base}/api/v1/availability?{qs}"
    req = Request(url, method="GET", headers={"Accept": "application/json"})
    try:
        with urlopen(req, timeout=_http_timeout_s()) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return {"ok": True, "parsed": json.loads(body)}
            except json.JSONDecodeError:
                return {"ok": True, "raw": body[:2000]}
    except URLError as exc:
        return {"ok": False, "error": str(exc.reason or exc)}


def poisson_pmf(lambda_: float, k: int) -> float:
    """Poisson PMF P(X=k); for planning / peak-friction heuristics only — λ must be estimated from data."""
    if lambda_ < 0 or k < 0:
        return float("nan")
    k = min(int(k), 200)
    return float(math.exp(-lambda_) * (lambda_**k) / math.factorial(k))


def bookit_poisson_peak_friction_json(lambda_: float, k: int) -> str:
    pmf = poisson_pmf(lambda_, k)
    return json.dumps(
        {
            "ok": True,
            "lambda": lambda_,
            "k": k,
            "pmf": pmf,
            "disclaimer": "λ is not auto-estimated from production traffic in this tool — supply empirically or via analytics pipeline.",
        },
        indent=2,
    )


def check_court_availability(venue_id: str, date: str, timeslot: str = "") -> str:
    """
    Local lock check first (Capacitor / anti-double-book), then optional Next.js probe.
    If `timeslot` is empty, returns **day-level** active locks for the venue+date (no remote probe).
    """
    init_bookit_db()
    _expire_stale_pending()
    slot = (timeslot or "").strip()
    if not slot:
        rows = _day_lock_rows(venue_id, date)
        return json.dumps(
            {
                "ok": True,
                "venue_id": venue_id,
                "date": date,
                "timeslot": None,
                "mode": "day_scan",
                "active_locks": rows,
                "remote_probe": None,
                "note": "Pass timeslot for slot-level lock + optional BOOKIT_API_BASE probe.",
                "db_path": str(_local_db_path()),
                "generated_at": datetime.now(UTC).isoformat(),
            },
            indent=2,
        )

    locks = _active_lock_count(venue_id, date, slot)
    local_available = locks == 0
    remote: dict[str, Any] | None = _http_availability(venue_id, date, slot)
    payload: dict[str, Any] = {
        "ok": True,
        "venue_id": venue_id,
        "date": date,
        "timeslot": slot,
        "local_lock_active": not local_available,
        "local_available": local_available,
        "remote_probe": remote,
        "db_path": str(_local_db_path()),
        "generated_at": datetime.now(UTC).isoformat(),
    }
    if remote and isinstance(remote, dict) and remote.get("ok") is False:
        payload["note"] = "remote_probe_failed_local_still_authoritative_for_locks"
    return json.dumps(payload, indent=2)


def initiate_booking(user_id: str, venue_id: str, date: str, timeslot: str) -> str:
    """
    Insert pending row; Event-Broker ACK is Owner/Next.js responsibility until wired.
    """
    init_bookit_db()
    _expire_stale_pending()
    cid = str(uuid.uuid4())
    now = datetime.now(UTC)
    expires = now + timedelta(minutes=int(os.environ.get("BOOKIT_PENDING_TTL_MIN", "15")))
    conn = sqlite3.connect(str(_local_db_path()))
    try:
        conn.execute("BEGIN IMMEDIATE")
        cur = conn.execute(
            """
            SELECT COUNT(*) AS c FROM court_locks
            WHERE venue_id = ? AND date = ? AND timeslot = ?
              AND status IN ('pending', 'confirmed')
            """,
            (venue_id, date, timeslot),
        )
        if int(cur.fetchone()[0]) > 0:
            conn.rollback()
            return json.dumps(
                {
                    "ok": False,
                    "error": "slot_locked",
                    "venue_id": venue_id,
                    "date": date,
                    "timeslot": timeslot,
                },
                indent=2,
            )
        conn.execute(
            """
            INSERT INTO court_locks (
                venue_id, date, timeslot, correlation_id, user_id, status, created_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
            """,
            (
                venue_id,
                date,
                timeslot,
                cid,
                user_id,
                now.isoformat(),
                expires.isoformat(),
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        return json.dumps(
            {"ok": False, "error": "integrity_conflict", "correlation_id": cid},
            indent=2,
        )
    finally:
        conn.close()

    return json.dumps(
        {
            "ok": True,
            "status": "pending_ack",
            "correlation_id": cid,
            "venue_id": venue_id,
            "date": date,
            "timeslot": timeslot,
            "expires_at": expires.isoformat(),
            "note": "Awaiting Next.js/UI ACK to promote to confirmed or release on timeout.",
        },
        indent=2,
    )


def issue_checkin_token(correlation_id: str) -> str:
    """
    Mint an opaque venue-entry token bound to an existing court_locks row (Project Alpha / Bookit 5s Arena).
    Next.js or steward tooling calls this after a lock exists; QR payload should embed `token_id` only.
    """
    init_bookit_db()
    _expire_stale_pending()
    _expire_stale_checkin_tokens()
    cid = (correlation_id or "").strip()
    if not cid:
        return json.dumps({"ok": False, "error": "missing_correlation_id"}, indent=2)

    conn = sqlite3.connect(str(_local_db_path()))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(
            """
            SELECT venue_id, date, timeslot, user_id, status, expires_at
            FROM court_locks WHERE correlation_id = ?
            """,
            (cid,),
        )
        row = cur.fetchone()
        if not row:
            return json.dumps({"ok": False, "error": "unknown_correlation_id"}, indent=2)
        st = str(row["status"])
        if st in ("released", "expired"):
            return json.dumps(
                {"ok": False, "error": "lock_not_eligible", "status": st},
                indent=2,
            )
        require = os.environ.get("BOOKIT_QR_ISSUE_MIN_STATUS", "pending").strip().lower()
        order = ("pending", "confirmed")
        if require not in order:
            require = "pending"
        min_i = order.index(require)
        if st not in order or order.index(st) < min_i:
            return json.dumps(
                {
                    "ok": False,
                    "error": "lock_status_below_minimum",
                    "status": st,
                    "required_min": require,
                },
                indent=2,
            )

        cur2 = conn.execute(
            "SELECT token_id FROM checkin_tokens WHERE correlation_id = ? AND status = 'active'",
            (cid,),
        )
        existing = cur2.fetchone()
        if existing:
            tid = str(existing["token_id"])
            return json.dumps(
                {
                    "ok": True,
                    "reused": True,
                    "token": tid,
                    "correlation_id": cid,
                    "note": "Active check-in token already issued for this lock.",
                },
                indent=2,
            )

        token_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        ttl_min = int(os.environ.get("BOOKIT_CHECKIN_TTL_MIN", "360"))
        until = now + timedelta(minutes=ttl_min)
        try:
            lock_exp = datetime.fromisoformat(str(row["expires_at"]).replace("Z", "+00:00"))
            if lock_exp.tzinfo is None:
                lock_exp = lock_exp.replace(tzinfo=UTC)
            until = max(until, lock_exp)
        except (ValueError, TypeError):
            pass

        conn.execute(
            """
            INSERT INTO checkin_tokens (
                token_id, venue_id, date, timeslot, correlation_id, user_id,
                issued_at, expires_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """,
            (
                token_id,
                str(row["venue_id"]),
                str(row["date"]),
                str(row["timeslot"]),
                cid,
                row["user_id"],
                now.isoformat(),
                until.isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return json.dumps(
        {
            "ok": True,
            "reused": False,
            "token": token_id,
            "venue_id": str(row["venue_id"]),
            "date": str(row["date"]),
            "timeslot": str(row["timeslot"]),
            "correlation_id": cid,
            "expires_at": until.isoformat(),
            "qr_payload_hint": f"bookit5s://checkin?token={token_id}",
        },
        indent=2,
    )


def validate_qr_checkin(
    token: str,
    venue_id: str = "",
    scanner_device_id: str = "",
) -> str:
    """
    Gate validation: first redeem wins; repeat scans return `already_redeemed` (idempotent for stewards).
    Optional `venue_id` enforces gate/venue match (defense in depth).
    """
    init_bookit_db()
    _expire_stale_checkin_tokens()
    tid = (token or "").strip()
    if not tid:
        return json.dumps({"ok": False, "error": "missing_token"}, indent=2)

    gate_venue = (venue_id or "").strip()
    scanner = (scanner_device_id or "").strip() or None
    now_dt = datetime.now(UTC)
    now = now_dt.isoformat()

    conn = sqlite3.connect(str(_local_db_path()))
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("BEGIN IMMEDIATE")
        cur = conn.execute(
            "SELECT * FROM checkin_tokens WHERE token_id = ?",
            (tid,),
        )
        row = cur.fetchone()
        if not row:
            conn.rollback()
            return json.dumps({"ok": False, "error": "unknown_token"}, indent=2)

        def _row_payload(r: sqlite3.Row, *, outcome: str) -> dict[str, Any]:
            return {
                "ok": True,
                "outcome": outcome,
                "venue_id": str(r["venue_id"]),
                "date": str(r["date"]),
                "timeslot": str(r["timeslot"]),
                "correlation_id": str(r["correlation_id"]),
                "user_id": r["user_id"],
                "issued_at": str(r["issued_at"]),
                "expires_at": str(r["expires_at"]),
                "redeemed_at": r["redeemed_at"],
                "redeemed_by_scanner": r["redeemed_by_scanner"],
            }

        st = str(row["status"])
        if st == "revoked":
            conn.rollback()
            return json.dumps({"ok": False, "error": "token_revoked"}, indent=2)
        if st == "expired" or _expires_at_passed(row["expires_at"], now_dt):
            conn.rollback()
            snap = _row_payload(row, outcome="expired")
            snap.pop("ok", None)
            return json.dumps({"ok": False, "error": "token_expired", **snap}, indent=2)
        if gate_venue and str(row["venue_id"]) != gate_venue:
            conn.rollback()
            return json.dumps(
                {
                    "ok": False,
                    "error": "venue_mismatch",
                    "expected_venue_id": str(row["venue_id"]),
                    "scanner_venue_id": gate_venue,
                },
                indent=2,
            )
        if st == "redeemed":
            conn.rollback()
            payload = _row_payload(row, outcome="already_redeemed")
            payload["admit"] = True
            return json.dumps(payload, indent=2)

        cur2 = conn.execute(
            """
            UPDATE checkin_tokens
            SET status = 'redeemed', redeemed_at = ?, redeemed_by_scanner = ?
            WHERE token_id = ? AND status = 'active'
            """,
            (now, scanner, tid),
        )
        if cur2.rowcount == 0:
            conn.rollback()
            cur3 = conn.execute(
                "SELECT * FROM checkin_tokens WHERE token_id = ?",
                (tid,),
            )
            row2 = cur3.fetchone()
            if row2 and str(row2["status"]) == "redeemed":
                p = _row_payload(row2, outcome="already_redeemed")
                p["admit"] = True
                return json.dumps(p, indent=2)
            return json.dumps({"ok": False, "error": "concurrent_redeem_race"}, indent=2)

        conn.commit()
        cur4 = conn.execute("SELECT * FROM checkin_tokens WHERE token_id = ?", (tid,))
        final = cur4.fetchone()
        assert final is not None
        payload = _row_payload(final, outcome="first_redeem")
        payload["admit"] = True
        return json.dumps(payload, indent=2)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def dispatch(tool_name: str, tool_input: dict[str, Any]) -> str:
    if tool_name == "bookit_check_court_availability":
        return check_court_availability(
            str(tool_input.get("venue_id", "")).strip(),
            str(tool_input.get("date", "")).strip(),
            str(tool_input.get("timeslot", "")).strip(),
        )
    if tool_name == "bookit_poisson_peak_friction":
        return bookit_poisson_peak_friction_json(
            float(tool_input.get("lambda", 0)),
            int(tool_input.get("k", 0)),
        )
    if tool_name == "bookit_initiate_booking":
        return initiate_booking(
            str(tool_input.get("user_id", "")).strip(),
            str(tool_input.get("venue_id", "")).strip(),
            str(tool_input.get("date", "")).strip(),
            str(tool_input.get("timeslot", "")).strip(),
        )
    if tool_name == "bookit_issue_checkin_token":
        return issue_checkin_token(str(tool_input.get("correlation_id", "")).strip())
    if tool_name in ("bookit_validate_qr_checkin", "validate_qr_checkin"):
        return validate_qr_checkin(
            str(tool_input.get("token", "")).strip(),
            str(tool_input.get("venue_id", "")).strip(),
            str(tool_input.get("scanner_device_id", "")).strip(),
        )
    raise ValueError(f"unknown bookit tool: {tool_name}")


_BOOKIT_QR_VALIDATE_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "token": {
            "type": "string",
            "description": "Opaque token_id from QR (e.g. bookit5s://checkin?token=<uuid>).",
        },
        "venue_id": {
            "type": "string",
            "description": "Optional; if set, must equal the token's venue_id (wrong gate = venue_mismatch).",
        },
        "scanner_device_id": {
            "type": "string",
            "description": "Optional steward handset / scanner id stored on first redeem for audit.",
        },
    },
    "required": ["token"],
}


def tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "bookit_check_court_availability",
            "description": "Bookit 5s: check local SQLite slot locks, optional GET BOOKIT_API_BASE/api/v1/availability (5s timeout).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "venue_id": {"type": "string"},
                    "date": {"type": "string", "description": "ISO date YYYY-MM-DD"},
                    "timeslot": {
                        "type": "string",
                        "description": "e.g. 18:00-19:00; omit or empty string for day-level lock scan",
                    },
                },
                "required": ["venue_id", "date"],
            },
        },
        {
            "name": "bookit_poisson_peak_friction",
            "description": "Deterministic Poisson PMf P(X=k) for demand modelling — λ is caller-supplied (not inferred here).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "lambda": {"type": "number", "description": "Mean bookings / window (λ ≥ 0)"},
                    "k": {"type": "integer", "description": "Observed count k (capped at 200)"},
                },
                "required": ["lambda", "k"],
            },
        },
        {
            "name": "bookit_initiate_booking",
            "description": "Bookit 5s: create pending lock row (correlation_id) pending UI/API ACK.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "venue_id": {"type": "string"},
                    "date": {"type": "string"},
                    "timeslot": {"type": "string"},
                },
                "required": ["user_id", "venue_id", "date", "timeslot"],
            },
        },
        {
            "name": "bookit_issue_checkin_token",
            "description": (
                "Project Alpha / Bookit 5s Arena: mint an opaque QR token for venue entry, "
                "bound to an existing court_locks.correlation_id. Reuses active token if already issued."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "correlation_id": {
                        "type": "string",
                        "description": "UUID from bookit_initiate_booking (or confirmed lock in DB).",
                    },
                },
                "required": ["correlation_id"],
            },
        },
        {
            "name": "bookit_validate_qr_checkin",
            "description": (
                "Project Alpha / Bookit 5s Arena: validate venue-entry QR (opaque token). "
                "First redeem sets redeemed_at; repeats return outcome already_redeemed with admit=true. "
                "Optional venue_id must match token when provided (steward gate). "
                "Canonical short name for clients: validate_qr_checkin."
            ),
            "input_schema": _BOOKIT_QR_VALIDATE_INPUT_SCHEMA,
        },
        {
            "name": "validate_qr_checkin",
            "description": (
                "Project Alpha (Bookit 5s Arena): same as bookit_validate_qr_checkin — "
                "physical venue entry + audit trail for May 2026 tournament operations."
            ),
            "input_schema": _BOOKIT_QR_VALIDATE_INPUT_SCHEMA,
        },
    ]


if __name__ == "__main__":
    import sys

    init_bookit_db()
    if len(sys.argv) >= 4 and sys.argv[1] == "check":
        vid, d = sys.argv[2], sys.argv[3]
        ts = sys.argv[4] if len(sys.argv) >= 5 else ""
        print(check_court_availability(vid, d, ts))
    elif len(sys.argv) >= 6 and sys.argv[1] == "book":
        uid, vid, d, ts = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
        print(initiate_booking(uid, vid, d, ts))
    elif len(sys.argv) >= 3 and sys.argv[1] == "issue-checkin":
        print(issue_checkin_token(sys.argv[2]))
    elif len(sys.argv) >= 3 and sys.argv[1] == "validate":
        v = sys.argv[3] if len(sys.argv) >= 4 else ""
        s = sys.argv[4] if len(sys.argv) >= 5 else ""
        print(validate_qr_checkin(sys.argv[2], v, s))
    else:
        print(
            json.dumps(
                {
                    "usage": "python bookit_tools.py check <venue_id> <date> <timeslot>",
                    "usage2": "python bookit_tools.py book <user_id> <venue_id> <date> <timeslot>",
                    "usage3": "python bookit_tools.py issue-checkin <correlation_id>",
                    "usage4": "python bookit_tools.py validate <token> [venue_id] [scanner_device_id]",
                }
            ),
            file=sys.stderr,
        )
        raise SystemExit(2)
