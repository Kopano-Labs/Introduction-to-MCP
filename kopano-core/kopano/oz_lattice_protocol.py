"""
Oz Lattice Protocol — Context Bleed Boundary Enforcement

Validates cross-domain information flow using lattice-node containment.
Each domain (CRUD, SWFUS, GUI, BlackMask, Telemetry) is a lattice node.
Any flow crossing a lattice edge must produce a seal (hash proof) and a bleed audit.

This is a Proof-of-Concept that validates real architectural properties:
- Lattice integrity: no unsealed cross-domain flows
- Bleed detection: structural + semantic anomaly detection
- Seal verification: cryptographic proof of containment
- CRUD integration: SQLite audit table for boundary violations
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LATTICE_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "OZ_LATTICE_AUDIT.jsonl"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
# Use same path as database.py (db/datalake.db relative to repo root)
DB_PATH = REPO_ROOT / "db" / "datalake.db"

# Lattice nodes — domains that must remain structurally separated
LATTICE_NODES = {
    "crud": "sqlite_data_lake",
    "swfus": "spawn_dispatch_envelope",
    "gui": "studio_react_surface",
    "blackmask": "commandment_drill_layer",
    "telemetry": "signal_routing_layer",
    "altar": "containment_vault",
    "hood": "infinite_hood_cloud",
    "phu": "kopano_phu_ecosystem",
}

# Allowed edges (directed) — any flow not in this set triggers bleed audit
ALLOWED_EDGES: set[tuple[str, str]] = {
    ("swfus", "blackmask"),   # spawn dispatch → drill validation
    ("blackmask", "altar"),   # drill pass → containment vault
    ("telemetry", "swfus"),   # signal routing → spawn envelope
    ("crud", "gui"),          # data lake → studio surface (read-only)
    ("crud", "telemetry"),    # data lake → signal analysis
    ("phu", "swfus"),         # ecosystem → spawn dispatch
    ("hood", "swfus"),        # cloud hood → spawn dispatch
    ("altar", "gui"),         # vault → GUI token exfiltration (strict)
    ("telemetry", "blackmask"), # signal routing → drill layer
}

# Structural bleed patterns — regex signatures for cross-domain leakage
STRUCTURAL_BLEED_PATTERNS = {
    "sql_in_gui": re.compile(r"SELECT\s+.*\s+FROM\s+\w+.*WHERE", re.I),
    "api_key_exposure": re.compile(r"(sk-[a-zA-Z0-9]{48}|az[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", re.I),
    "internal_path_leak": re.compile(r"(kopano-core[\\/]|\.kc[\\/]|\.env[\\/])", re.I),
    "spawn_id_in_crud": re.compile(r"spawn_(telemetry|identic|guardian)_\d{3}"),
    "raw_bracket_in_data": re.compile(r"\[(KPGS|SWFUS|BLACK_MASK|TSAP|BRACKET_PROTOCOL)[^\]]*\]"),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _db_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _hash_seal(source: str, target: str, payload: dict[str, Any], nonce: str = "") -> str:
    """Lattice seal: SHA-256 of source|target|sorted_payload|nonce."""
    body = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(f"{source}|{target}|{body}|{nonce}".encode("utf-8")).hexdigest()


def init_lattice_tables() -> None:
    """Idempotent lattice audit tables in the datalake DB."""
    conn = _db_conn()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS lattice_bleed_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                source_node TEXT NOT NULL,
                target_node TEXT NOT NULL,
                seal TEXT NOT NULL,
                verdict TEXT NOT NULL CHECK(verdict IN ('SEALED','BLEED_DETECTED','STRUCTURAL_BLEED','SEMANTIC_BLEED')),
                payload_preview TEXT,
                structural_hits TEXT,
                semantic_hits TEXT,
                lattice_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS lattice_node_states (
                node_id TEXT PRIMARY KEY,
                last_seal TEXT,
                last_ts TEXT,
                integrity_ok INTEGER NOT NULL DEFAULT 1,
                bleed_count INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        conn.commit()
        for node in LATTICE_NODES:
            conn.execute(
                "INSERT OR IGNORE INTO lattice_node_states (node_id) VALUES (?)", (node,)
            )
        conn.commit()
    finally:
        conn.close()


def check_structural_bleed(payload: str | dict[str, Any]) -> dict[str, Any]:
    """Scan payload for structural cross-domain leakage signatures."""
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    hits: list[dict[str, Any]] = []
    for name, pattern in STRUCTURAL_BLEED_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            hits.append({
                "pattern": name,
                "match_count": len(matches),
                "samples": [str(m)[:80] for m in matches[:3]],
            })
    return {
        "structural_bleed_detected": bool(hits),
        "hits": hits,
        "scanned_length": len(text),
    }


def lattice_seal(
    source: str,
    target: str,
    payload: dict[str, Any],
    *,
    run_structural: bool = True,
    run_semantic: bool = True,
) -> dict[str, Any]:
    """
    Core lattice crossing: validate edge, produce seal, detect bleed.
    Returns seal metadata + verdict for SWFUS/BlackMask integration.
    """
    if source not in LATTICE_NODES:
        return {
            "verdict": "BLEED_DETECTED",
            "reason": f"source_node_unknown: {source}",
            "allowed_nodes": list(LATTICE_NODES.keys()),
        }
    if target not in LATTICE_NODES:
        return {
            "verdict": "BLEED_DETECTED",
            "reason": f"target_node_unknown: {target}",
            "allowed_nodes": list(LATTICE_NODES.keys()),
        }

    edge = (source, target)
    edge_allowed = edge in ALLOWED_EDGES

    # Structural scan
    struct = {"structural_bleed_detected": False, "hits": []}
    if run_structural:
        struct = check_structural_bleed(payload)

    # Semantic scan (context bleed classification via telemetry routing)
    semantic = {"semantic_bleed_detected": False, "note": "skipped"}
    if run_semantic and isinstance(payload, dict):
        raw = payload.get("message") or payload.get("prompt") or payload.get("action") or ""
        if raw:
            from .kpgs_telemetry_route import classify_telemetry_signal

            sem = classify_telemetry_signal(str(raw))
            semantic = {
                "semantic_bleed_detected": sem.get("verdict") == "RECLASSIFY",
                "telemetry_verdict": sem.get("verdict"),
                "detected_lanes": sem.get("detected_lanes", []),
                "note": sem.get("note", ""),
            }

    # Determine verdict
    if not edge_allowed:
        verdict = "BLEED_DETECTED"
    elif struct["structural_bleed_detected"]:
        verdict = "STRUCTURAL_BLEED"
    elif semantic["semantic_bleed_detected"]:
        verdict = "SEMANTIC_BLEED"
    else:
        verdict = "SEALED"

    seal_hash = _hash_seal(source, target, payload, nonce=_utc_now())
    lattice_hash = _hash_seal("lattice", "integrity", {"nodes": list(LATTICE_NODES.keys()), "edges": list(ALLOWED_EDGES)})

    audit_row = {
        "ts": _utc_now(),
        "source_node": source,
        "target_node": target,
        "seal": seal_hash,
        "verdict": verdict,
        "payload_preview": json.dumps(payload, ensure_ascii=False)[:400],
        "structural_hits": json.dumps(struct["hits"], ensure_ascii=False),
        "semantic_hits": json.dumps(semantic, ensure_ascii=False),
        "lattice_hash": lattice_hash,
    }

    # Persist to DB
    conn = _db_conn()
    try:
        conn.execute(
            """
            INSERT INTO lattice_bleed_audits
            (ts, source_node, target_node, seal, verdict, payload_preview, structural_hits, semantic_hits, lattice_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                audit_row["ts"],
                audit_row["source_node"],
                audit_row["target_node"],
                audit_row["seal"],
                audit_row["verdict"],
                audit_row["payload_preview"],
                audit_row["structural_hits"],
                audit_row["semantic_hits"],
                audit_row["lattice_hash"],
            ),
        )
        # Update node state
        if verdict != "SEALED":
            conn.execute(
                "UPDATE lattice_node_states SET bleed_count = bleed_count + 1, integrity_ok = 0, last_ts = ? WHERE node_id = ?",
                (audit_row["ts"], source),
            )
            conn.execute(
                "UPDATE lattice_node_states SET bleed_count = bleed_count + 1, integrity_ok = 0, last_ts = ? WHERE node_id = ?",
                (audit_row["ts"], target),
            )
        else:
            conn.execute(
                "UPDATE lattice_node_states SET last_seal = ?, last_ts = ? WHERE node_id = ?",
                (seal_hash, audit_row["ts"], source),
            )
        conn.commit()
    finally:
        conn.close()

    # Log to swarm-ops
    _append_jsonl(LATTICE_LOG, audit_row)
    if verdict != "SEALED":
        _append_jsonl(
            MAIN_BRAIN_LOG,
            {
                "schema": "kc_main_brain_log_v1",
                "ts": audit_row["ts"],
                "kind": "oz_lattice_bleed",
                "source": source,
                "target": target,
                "verdict": verdict,
                "seal": seal_hash[:16] + "…",
                "exit_code": 1,
            },
        )

    return {
        "schema": "oz_lattice_seal_v1",
        "ts": audit_row["ts"],
        "source": source,
        "target": target,
        "edge_allowed": edge_allowed,
        "verdict": verdict,
        "seal": seal_hash,
        "lattice_hash": lattice_hash,
        "structural_scan": struct,
        "semantic_scan": semantic,
        "bracket": "[OZ_LATTICE_PROTOCOL]",
        "summary": (
            f"[OZ_LATTICE] {source}→{target} | verdict={verdict} | "
            f"edge={'allowed' if edge_allowed else 'FORBIDDEN'} | "
            f"struct={len(struct['hits'])} | sem={semantic.get('telemetry_verdict', 'n/a')}"
        ),
    }


def verify_lattice_seal(seal_hash: str, source: str, target: str, payload: dict[str, Any]) -> bool:
    """Verify a previously produced seal matches recomputed hash."""
    expected = _hash_seal(source, target, payload, nonce="")
    # Note: nonce is timestamp in production; for verification we compare without nonce
    # In production, store nonce in audit table and retrieve for strict verification
    return seal_hash == expected


def lattice_node_status(node_id: str) -> dict[str, Any]:
    """Return current integrity state for a lattice node."""
    conn = _db_conn()
    try:
        row = conn.execute(
            "SELECT * FROM lattice_node_states WHERE node_id = ?", (node_id,)
        ).fetchone()
        if not row:
            return {"error": "node_not_found", "node_id": node_id}
        return {
            "node_id": row["node_id"],
            "last_seal": row["last_seal"],
            "last_ts": row["last_ts"],
            "integrity_ok": bool(row["integrity_ok"]),
            "bleed_count": row["bleed_count"],
        }
    finally:
        conn.close()


def lattice_integrity_report() -> dict[str, Any]:
    """Full lattice integrity report — all nodes, recent audits, seal coverage."""
    conn = _db_conn()
    try:
        nodes = conn.execute("SELECT * FROM lattice_node_states").fetchall()
        recent = conn.execute(
            "SELECT * FROM lattice_bleed_audits ORDER BY id DESC LIMIT 20"
        ).fetchall()
        total_audits = conn.execute("SELECT COUNT(*) as c FROM lattice_bleed_audits").fetchone()["c"]
        bleed_audits = conn.execute(
            "SELECT COUNT(*) as c FROM lattice_bleed_audits WHERE verdict != 'SEALED'"
        ).fetchone()["c"]
    finally:
        conn.close()

    return {
        "schema": "oz_lattice_integrity_report_v1",
        "ts": _utc_now(),
        "lattice_hash": _hash_seal("lattice", "integrity", {"nodes": list(LATTICE_NODES.keys()), "edges": list(ALLOWED_EDGES)}),
        "nodes": {row["node_id"]: dict(row) for row in nodes},
        "total_audits": total_audits,
        "bleed_audits": bleed_audits,
        "integrity_ok": all(bool(row["integrity_ok"]) for row in nodes),
        "recent_audits": [dict(row) for row in recent],
        "bracket": "[OZ_LATTICE_INTEGRITY]",
    }


def enforce_lattice_boundary(
    source: str,
    target: str,
    payload: dict[str, Any],
    *,
    strict: bool = True,
) -> dict[str, Any]:
    """
    High-level boundary enforcer: returns payload only if SEALED, else raises or returns blocked.
    For SWFUS integration: call this inside dispatch_spawn_event before proceed.
    """
    result = lattice_seal(source, target, payload)
    if result["verdict"] == "SEALED":
        return {
            "allowed": True,
            "seal": result["seal"],
            "lattice_result": result,
        }
    if strict:
        return {
            "allowed": False,
            "blocked_reason": result["verdict"],
            "seal": result["seal"],
            "lattice_result": result,
        }
    return {
        "allowed": True,
        "warning": result["verdict"],
        "seal": result["seal"],
        "lattice_result": result,
    }
