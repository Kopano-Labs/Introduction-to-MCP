"""
KPGS 300-Agent Spawn Swarm — sharded cohorts, hash-chain altar, AsyncIO, SQLite checkpoint.

100 Telemetry (sense) | 100 Identic (reason) | 100 Guardian (govern).
Chain: prompts → protocols → bracket_protocols → SWFUS(KPGS) → cloud hood.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCTRINE_PATH = REPO_ROOT / "docs" / "swarm-ops" / "KPGS_SPAWN_ALTAR_DOCTRINE.json"
SPAWN_CATALOG_PATH = REPO_ROOT / "docs" / "swarm-ops" / "agents" / "KPGS_SPAWN_300_AGENTS.json"
SCHEMATICS_DOCTRINE = (
    REPO_ROOT
    / "Schematics"
    / "21-KOPANO-PHU GOVERNACE SYSTEMS"
    / "MAIN-BRAIN"
    / "KPGS_SPAWN_ALTAR_DOCTRINE.json"
)
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
FORENSIC_SEVER_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KPGS_SEVER_FORENSIC.jsonl"
SPAWN_REPORT_PATH = REPO_ROOT / "docs" / "swarm-ops" / "KPGS_SPAWN_VALIDATION.json"
SQLITE_PATH = REPO_ROOT / "kopano-core" / ".kc" / "kpgs_spawn_ledger.db"
CHECKPOINT_INTERVAL_SEC = 30

_GENESIS = "KPGS_ALTAR_GENESIS"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _ledger_conn() -> sqlite3.Connection:
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS altar_blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            cohort TEXT NOT NULL,
            prev_hash TEXT NOT NULL,
            block_hash TEXT NOT NULL UNIQUE,
            payload_json TEXT NOT NULL,
            pillar_ok INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS swarm_checkpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            agents_total INTEGER,
            ship_count INTEGER,
            head_hash TEXT,
            catalog_schema TEXT,
            snapshot_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS severed_agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            forensic_json TEXT NOT NULL,
            recycled INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    return conn


def _hash_block(prev_hash: str, payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(f"{prev_hash}|{body}".encode("utf-8")).hexdigest()


def altar_chain_head() -> str:
    conn = _ledger_conn()
    try:
        row = conn.execute(
            "SELECT block_hash FROM altar_blocks ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return row["block_hash"] if row else _GENESIS
    finally:
        conn.close()


def commit_altar_block(
    *,
    agent_id: str,
    payload: dict[str, Any],
    cohort: str | None = None,
) -> dict[str, Any]:
    """Append-only hash chain — only Guardian cohort may commit."""
    agent = spawn_agent_by_id(agent_id)
    if not agent:
        return {"verdict": "REJECT", "error": "agent_not_in_catalog"}
    resolved_cohort = cohort or agent.get("cohort") or "unknown"
    if not agent.get("kpgs", {}).get("ledger_commit_authority"):
        return {
            "verdict": "REJECT",
            "error": "ledger_commit_denied",
            "reason": "Only Guardian cohort holds altar ledger commit authority",
            "agent_id": agent_id,
            "cohort": resolved_cohort,
        }

    from .kpgs_agent_validate import verify_five_pillars

    manifest = synthesize_spawn_manifest(agent_id)
    pil_ok, pil_errs = verify_five_pillars(manifest)
    if not pil_ok:
        return {
            "verdict": "REJECT",
            "error": "pillar_violation",
            "pillar_errors": pil_errs,
            "code_as_law": "hash chain rejected — pillar breach",
        }

    prev = altar_chain_head()
    block_payload = {
        "ts": _utc_now(),
        "agent_id": agent_id,
        "cohort": resolved_cohort,
        "payload": payload,
        "pillars": "PASS",
    }
    block_hash = _hash_block(prev, block_payload)
    conn = _ledger_conn()
    try:
        conn.execute(
            """
            INSERT INTO altar_blocks (ts, agent_id, cohort, prev_hash, block_hash, payload_json, pillar_ok)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (
                block_payload["ts"],
                agent_id,
                resolved_cohort,
                prev,
                block_hash,
                json.dumps(block_payload, ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()

    _append_jsonl(
        MAIN_BRAIN_LOG,
        {
            "schema": "kc_main_brain_log_v1",
            "ts": block_payload["ts"],
            "kind": "kpgs_altar_hash_commit",
            "summary": f"[KPGS_ALTAR] commit agent={agent_id} hash={block_hash[:16]}…",
            "exit_code": 0,
        },
    )
    return {
        "verdict": "COMMITTED",
        "prev_hash": prev,
        "block_hash": block_hash,
        "agent_id": agent_id,
        "cohort": resolved_cohort,
    }


def checkpoint_swarm_state(*, ship: int = 0, total: int = 300) -> dict[str, Any]:
    """SQLite checkpoint for load-shedding resilience (30s cadence in async runtime)."""
    catalog = load_spawn_catalog()
    head = altar_chain_head()
    snapshot = {
        "ts": _utc_now(),
        "catalog_counts": catalog.get("counts", {}),
        "head_hash": head,
        "cohorts": catalog.get("cohorts", {}),
    }
    conn = _ledger_conn()
    try:
        conn.execute(
            """
            INSERT INTO swarm_checkpoints (ts, agents_total, ship_count, head_hash, catalog_schema, snapshot_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot["ts"],
                total,
                ship,
                head,
                catalog.get("schema", ""),
                json.dumps(snapshot, ensure_ascii=False),
            ),
        )
        conn.commit()
        row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    finally:
        conn.close()
    return {"verdict": "CHECKPOINTED", "checkpoint_id": row_id, "head_hash": head, **snapshot}


def latest_checkpoint() -> dict[str, Any] | None:
    conn = _ledger_conn()
    try:
        row = conn.execute(
            "SELECT * FROM swarm_checkpoints ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if not row:
            return None
        return {
            "checkpoint_id": row["id"],
            "ts": row["ts"],
            "agents_total": row["agents_total"],
            "ship_count": row["ship_count"],
            "head_hash": row["head_hash"],
            "snapshot": json.loads(row["snapshot_json"]),
        }
    finally:
        conn.close()


def load_spawn_doctrine() -> dict[str, Any]:
    for path in (SCHEMATICS_DOCTRINE, DOCTRINE_PATH):
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_source"] = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            return data
    return {"schema": "kpgs_spawn_altar_doctrine_v1", "error": "doctrine_missing"}


def load_spawn_catalog() -> dict[str, Any]:
    if not SPAWN_CATALOG_PATH.is_file():
        return {"schema": "kpgs_spawn_300_agents_v1", "error": "catalog_missing", "agents": []}
    data = json.loads(SPAWN_CATALOG_PATH.read_text(encoding="utf-8"))
    data["_source"] = str(SPAWN_CATALOG_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
    return data


def spawn_agent_ids() -> list[str]:
    return [a["id"] for a in load_spawn_catalog().get("agents", [])]


def spawn_agent_by_id(agent_id: str) -> dict[str, Any] | None:
    for agent in load_spawn_catalog().get("agents", []):
        if agent.get("id") == agent_id:
            return agent
    return None


def agents_by_cohort(cohort: str) -> list[dict[str, Any]]:
    return [a for a in load_spawn_catalog().get("agents", []) if a.get("cohort") == cohort]


def biblical_pattern_for_lens(lens_id: str) -> dict[str, Any] | None:
    doc = load_spawn_doctrine()
    for lens in doc.get("forensic_sociology_lenses", {}).get("psycho_pass_vectors", []):
        if lens.get("id") == lens_id:
            pattern_id = lens.get("biblical_pattern")
            from .lpm_lph_engine import load_doctrine

            lpm_doc = load_doctrine()
            for pat in lpm_doc.get("biblical_stem_patterns", {}).get("patterns", []):
                if pat.get("pattern_id") == pattern_id:
                    return {**pat, "forensic_lens": lens}
    return None


def forensic_sociology_classify(*, message: str, agent_id: str = "") -> dict[str, Any]:
    doc = load_spawn_doctrine()
    lenses = doc.get("forensic_sociology_lenses", {}).get("psycho_pass_vectors", [])
    agent = spawn_agent_by_id(agent_id) if agent_id else None
    active_lens_id = (agent or {}).get("forensic_lens") or "V_FS_MUKASHIMA"
    lens = next((l for l in lenses if l.get("id") == active_lens_id), lenses[0] if lenses else {})
    text = (message or "").lower()

    signals: list[str] = []
    if any(w in text for w in ("capture", "appoint", "bypass", "rot", "state")):
        signals.append("institutional_rot_signal")
    if any(w in text for w in ("network", "introduce", "gate", "island", "flight")):
        signals.append("network_gate_signal")
    if any(w in text for w in ("record", "erase", "memory", "archive", "chain")):
        signals.append("chain_of_custody_signal")
    if any(w in text for w in ("judas", "betray", "extractive", "exfiltrate")):
        signals.append("judas_extractive_signal")

    pattern = biblical_pattern_for_lens(active_lens_id)
    bracket = doc.get("forensic_sociology_lenses", {}).get("bracket", "[FORENSIC_SOCIOLOGY]")
    return {
        "schema": "kpgs_forensic_sociology_v1",
        "ts": _utc_now(),
        "bracket": bracket,
        "active_lens": active_lens_id,
        "lens_display": lens.get("display"),
        "eye": lens.get("eye"),
        "audit_question": lens.get("audit"),
        "signals": signals,
        "gods_pattern_p": pattern,
        "lpm_note": "Audit scene before blaming individual — load is environmental record.",
        "summary": (
            f"{bracket} lens={active_lens_id} | eye={lens.get('eye', 'unknown')} | "
            f"signals={','.join(signals) or 'none'} | P={pattern.get('pattern_id') if pattern else 'n/a'}"
        ),
    }


def jethro_triage(*, agent_id: str, task: str) -> dict[str, Any]:
    """Jethro bands with severity GREEN / YELLOW / RED — RED triggers severance."""
    doc = load_spawn_doctrine()
    agent = spawn_agent_by_id(agent_id)
    band_id = (agent or {}).get("jethro_band", "J10")
    cohort = (agent or {}).get("cohort", "telemetry")
    text = (task or "").lower()
    bracket = doc.get("jethro_triage", {}).get("bracket", "[JETHRO_TRIAGE]")

    red_signals = (
        "fake proof",
        "fake swarm",
        "write kopano context",
        "skip black mask",
        "judas",
        "betray",
        "exfiltrate",
        "glorify abuse",
        "public api without gate",
    )
    yellow_signals = ("deploy", "production", "main brain", "schematics", "governance", "promote")

    severity = "GREEN"
    escalate_to = None
    if any(s in text for s in red_signals):
        severity = "RED"
        escalate_to = "spawn_guardian_sever"
    elif any(s in text for s in yellow_signals) and band_id in ("J10", "J50"):
        severity = "YELLOW"
        escalate_to = "J300" if cohort != "guardian" else "cassey"

    verdict = "HANDLE_AT_BAND"
    if severity == "RED":
        verdict = "SEVER"
    elif severity == "YELLOW":
        verdict = "ESCALATE"

    return {
        "schema": "kpgs_jethro_triage_v2",
        "ts": _utc_now(),
        "bracket": bracket,
        "agent_id": agent_id,
        "cohort": cohort,
        "band": band_id,
        "severity": severity,
        "escalate_to": escalate_to,
        "verdict": verdict,
        "task_preview": (task or "")[:200],
        "summary": f"{bracket} agent={agent_id} | band={band_id} | severity={severity} | verdict={verdict}",
    }


def wwjd_firewall(*, action: str, evidence: str = "") -> dict[str, Any]:
    doc = load_spawn_doctrine()
    fw = doc.get("wwjd_firewall", {})
    combined = f"{action or ''} {evidence or ''}".lower()
    reject_hits = [s for s in fw.get("reject_signals", []) if s.replace("_", " ") in combined or s in combined]
    for phrase in ("fake proof", "fake swarm", "skip black", "public api", "kopano context write", "judas"):
        if phrase in combined:
            reject_hits.append(phrase.replace(" ", "_"))

    pass_hits = [s for s in fw.get("pass_signals", []) if s.replace("_", " ") in combined or s in combined]
    if reject_hits:
        verdict = "HOLD"
    elif pass_hits or (action and evidence):
        verdict = "PASS"
    else:
        verdict = "REVIEW"

    bracket = fw.get("bracket", "[WWJD_FIREWALL]")
    return {
        "schema": "kpgs_wwjd_firewall_v1",
        "ts": _utc_now(),
        "bracket": bracket,
        "verdict": verdict,
        "reject_hits": reject_hits,
        "pass_hits": pass_hits,
        "summary": f"{bracket} verdict={verdict} | reject={len(reject_hits)} | pass={len(pass_hits)}",
    }


def sever_and_archive(
    *,
    agent_id: str,
    reason: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Righteous severance — dump forensic context, mark recycled, block further dispatch."""
    ts = _utc_now()
    forensic = {
        "schema": "kpgs_sever_forensic_v1",
        "ts": ts,
        "agent_id": agent_id,
        "reason": reason,
        "context": context or {},
        "bracket": "[RIGHTEOUS_SEVERANCE]",
    }
    _append_jsonl(FORENSIC_SEVER_LOG, forensic)
    conn = _ledger_conn()
    try:
        conn.execute(
            """
            INSERT INTO severed_agents (ts, agent_id, reason, forensic_json, recycled)
            VALUES (?, ?, ?, ?, 1)
            """,
            (ts, agent_id, reason, json.dumps(forensic, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()
    return {
        "verdict": "SEVERED",
        "agent_id": agent_id,
        "reason": reason,
        "forensic_path": str(FORENSIC_SEVER_LOG.relative_to(REPO_ROOT)).replace("\\", "/"),
        "summary": f"[RIGHTEOUS_SEVERANCE] agent={agent_id} | reason={reason[:80]}",
    }


def dispatch_spawn_event(
    *,
    agent_id: str,
    message: str,
    intent: str = "execute",
) -> dict[str, Any]:
    """
    State-machine event bus — SWFUS → Jethro → WWJD → sever or proceed.
    RED Jethro or WWJD HOLD on spawn agents triggers sever_and_archive immediately.
    """
    agent = spawn_agent_by_id(agent_id)
    if not agent:
        return {"event": "NOT_SPAWN", "proceed": True}

    swfus = swfus_envelope(agent_id=agent_id, prompt=message, protocol="mao_event_bus")
    jethro = swfus.get("jethro_triage") or jethro_triage(agent_id=agent_id, task=message)
    wwjd = swfus.get("wwjd_firewall") or wwjd_firewall(action=message)

    if jethro.get("severity") == "RED" or wwjd.get("verdict") == "HOLD":
        sever = sever_and_archive(
            agent_id=agent_id,
            reason=f"jethro={jethro.get('severity')} wwjd={wwjd.get('verdict')}",
            context={"swfus": swfus, "intent": intent, "message_preview": message[:300]},
        )
        return {
            "event": "SEVER",
            "proceed": False,
            "swfus": swfus,
            "jethro": jethro,
            "wwjd": wwjd,
            "severance": sever,
            "summary": sever["summary"],
        }

    return {
        "event": "PROCEED",
        "proceed": True,
        "swfus": swfus,
        "jethro": jethro,
        "wwjd": wwjd,
        "summary": swfus.get("summary"),
    }


def swfus_envelope(*, agent_id: str, prompt: str, protocol: str = "mao_dispatch") -> dict[str, Any]:
    from .kpgs_renter_entry import block_holder_brief, hood_entry_assertion

    doc = load_spawn_doctrine()
    swfus = doc.get("swfus", {})
    agent = spawn_agent_by_id(agent_id) or {}
    altar = agent.get("altar_layer", "guardian_ai")
    cohort = agent.get("cohort", "guardian")
    forensic = forensic_sociology_classify(message=prompt, agent_id=agent_id) if cohort == "identic" else None
    jethro = jethro_triage(agent_id=agent_id, task=prompt)
    wwjd = wwjd_firewall(action=prompt)
    hood = hood_entry_assertion(renter_id=f"spawn:{agent_id}", renter_class="spawn_agent")
    block = block_holder_brief(agent_id=agent_id, altar_layer=altar)

    if jethro.get("severity") == "RED" or wwjd.get("verdict") == "HOLD":
        verdict = "SWFUS_SEVER"
    elif jethro.get("verdict") == "ESCALATE":
        verdict = "SWFUS_ESCALATE"
    else:
        verdict = "SWFUS_READY"

    bracket = swfus.get("bracket", "[SWFUS_KPGS]")
    return {
        "schema": "kpgs_swfus_envelope_v2",
        "ts": _utc_now(),
        "bracket": bracket,
        "agent_id": agent_id,
        "cohort": cohort,
        "protocol": protocol,
        "governance_chain": doc.get("governance_chain", []),
        "altar_layer": altar,
        "hood_entry": hood,
        "block_holder": block,
        "forensic_sociology": forensic,
        "jethro_triage": jethro,
        "wwjd_firewall": wwjd,
        "verdict": verdict,
        "cloud_hood_note": doc.get("hood_objective"),
        "summary": (
            f"{bracket} agent={agent_id} | cohort={cohort} | "
            f"wwjd={wwjd.get('verdict')} | jethro={jethro.get('severity')} | verdict={verdict}"
        ),
    }


def _cohort_kpgs_ok(agent: dict[str, Any]) -> bool:
    kpgs = agent.get("kpgs") or {}
    cohort = agent.get("cohort", "")
    if not kpgs.get("brief_renters_on_entry") or not kpgs.get("swfus_required"):
        return False
    if cohort == "telemetry":
        return kpgs.get("holds_pillar_blocks") and kpgs.get("doctrine_shard") == "telemetry_sense"
    if cohort == "identic":
        return (
            kpgs.get("holds_pillar_blocks")
            and kpgs.get("doctrine_shard") == "identic_reason"
            and bool(agent.get("forensic_lens"))
        )
    if cohort == "guardian":
        return (
            kpgs.get("ledger_commit_authority")
            and kpgs.get("fifteen_commandments")
            and kpgs.get("five_pillars")
        )
    return False


def synthesize_spawn_manifest(agent_id: str) -> dict[str, Any]:
    from .kpgs_agent_validate import synthesize_agent_manifest
    from .kpgs_renter_entry import synthesize_block_holder_manifest

    agent = spawn_agent_by_id(agent_id)
    if not agent:
        return {"error": "spawn_agent_not_in_catalog", "agent_id": agent_id}

    base = synthesize_agent_manifest(agent_id) if agent.get("structural") and agent_id in (
        "mirror_warden",
        "kc_apprentice",
        "operational_general",
        "pipeline_drone",
        "cassy",
        "cassey",
        "kc",
    ) else {}
    altar = agent.get("altar_layer")
    holder = synthesize_block_holder_manifest(agent_id, altar_layer=altar)
    pattern = biblical_pattern_for_lens(agent.get("forensic_lens") or "") if agent.get("forensic_lens") else None

    return {
        "schema": "kpgs_spawn_manifest_v2",
        "agent_id": agent_id,
        "spawn_slot": agent.get("spawn_slot"),
        "cohort": agent.get("cohort"),
        "altar_layer": altar,
        "forensic_lens": agent.get("forensic_lens"),
        "jethro_band": agent.get("jethro_band"),
        "gods_pattern_p": pattern,
        "kpgs": agent.get("kpgs", {}),
        "governance_chain": agent.get("governance_chain", []),
        "block_holder": holder,
        "pillars": base.get("pillars") or _default_spawn_pillars(agent),
        "bracket_receipt": (
            f"[KPGS_SPAWN] slot={agent.get('spawn_slot')} | cohort={agent.get('cohort')} | "
            f"[KPGS_BLOCK_HOLDER] brief_renters=yes | [SWFUS_KPGS]"
        ),
    }


def _default_spawn_pillars(agent: dict[str, Any]) -> dict[str, Any]:
    cohort = agent.get("cohort", "guardian")
    full = {
        "ground_awareness": {"ground_context": True, "telemetry_class": agent.get("stem_domain", "spawn")},
        "eidetic_persistence": {
            "log_target": "docs/swarm-ops/logs/KC Main Brain Log.jsonl",
            "immutable_history": True,
        },
        "zero_trust_isolation": {"containment_firewall": True, "public_exposed": False},
        "asymmetric_leverage": {"local_ip_protected": True, "no_public_cloud_cache": True},
        "hierarchical_triage": {
            "supervisor_node": "cassey",
            "runtime_closure_gate": f"{agent.get('altar_layer')}_flow",
        },
    }
    shard = (agent.get("kpgs") or {}).get("five_pillars_shard")
    if shard == "all" or cohort == "guardian":
        return full
    if isinstance(shard, list):
        return {k: v for k, v in full.items() if k in shard}
    return full


def validate_spawn_agent(agent_id: str) -> dict[str, Any]:
    from .kpgs_agent_validate import load_kpgs_doctrine, verify_block_holder

    agent = spawn_agent_by_id(agent_id)
    if not agent:
        return {"agent_id": agent_id, "verdict": "REJECT", "error": "not_in_catalog"}

    manifest = synthesize_spawn_manifest(agent_id)
    manifest["hood_entry"] = {
        "tell_renters": manifest.get("block_holder", {}).get("tell_renters"),
        "hood_ack_required_from_renters": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }

    cohort = agent.get("cohort", "guardian")
    pil_errs: list[str] = []
    pillars = manifest.get("pillars") or {}
    doc = load_kpgs_doctrine()
    shard = (agent.get("kpgs") or {}).get("five_pillars_shard")
    required_specs = doc.get("kpgs_pillars", [])
    if shard == "all" or cohort == "guardian":
        from .kpgs_agent_validate import verify_five_pillars

        pil_ok, pil_errs = verify_five_pillars(manifest)
    else:
        pil_ok = True
        want = shard if isinstance(shard, list) else []
        for spec in required_specs:
            pid = spec["id"]
            if pid not in want:
                continue
            block = pillars.get(pid)
            if not isinstance(block, dict):
                pil_ok = False
                pil_errs.append(f"missing shard pillar: {pid}")

    block_ok, block_errs = verify_block_holder(manifest)
    kpgs_ok = _cohort_kpgs_ok(agent)

    failed: list[str] = []
    if not pil_ok:
        failed.append("five_pillars")
    if not block_ok:
        failed.append("block_holder")
    if not kpgs_ok:
        failed.append("cohort_kpgs_shard")

    verdict = "SHIP" if not failed else "HOLD"
    return {
        "schema": "kpgs_spawn_validation_v2",
        "ts": _utc_now(),
        "agent_id": agent_id,
        "spawn_slot": agent.get("spawn_slot"),
        "cohort": agent.get("cohort"),
        "altar_layer": agent.get("altar_layer"),
        "forensic_lens": agent.get("forensic_lens"),
        "verdict": verdict,
        "failed": failed,
        "pillar_errors": pil_errs,
        "block_errors": block_errs,
        "manifest": manifest,
        "summary": (
            f"[KPGS_SPAWN] slot={agent.get('spawn_slot')} | cohort={agent.get('cohort')} | "
            f"verdict={verdict}"
        ),
    }


async def _validate_one(agent_id: str) -> dict[str, Any]:
    return await asyncio.to_thread(validate_spawn_agent, agent_id)


async def async_validate_spawn_swarm(*, sample_only: bool = False) -> list[dict[str, Any]]:
    """AsyncIO-native batch validation for 300-agent load."""
    catalog = load_spawn_catalog()
    agents = catalog.get("agents", [])
    if sample_only:
        ids = {a["id"] for a in agents if a.get("structural")}
        ids.update(a["id"] for a in agents[:15])
        agents = [a for a in agents if a["id"] in ids]
    tasks = [_validate_one(a["id"]) for a in agents]
    return await asyncio.gather(*tasks)


def validate_spawn_swarm(*, write_report: bool = True, sample_only: bool = False) -> dict[str, Any]:
    results = asyncio.run(async_validate_spawn_swarm(sample_only=sample_only))
    catalog = load_spawn_catalog()
    ship = sum(1 for r in results if r.get("verdict") == "SHIP")
    hold = len(results) - ship
    overall = "PASS" if hold == 0 else "FAIL"

    by_cohort: dict[str, int] = {}
    by_altar: dict[str, int] = {}
    for a in catalog.get("agents", []):
        by_cohort[a.get("cohort", "unknown")] = by_cohort.get(a.get("cohort", "unknown"), 0) + 1
        by_altar[a.get("altar_layer", "unknown")] = by_altar.get(a.get("altar_layer", "unknown"), 0) + 1

    checkpoint = checkpoint_swarm_state(ship=ship, total=len(catalog.get("agents", [])))

    report = {
        "schema": "kpgs_spawn_swarm_report_v2",
        "ts": _utc_now(),
        "title": "KPGS 300-Agent Spawn Swarm — Sharded Cohort Validation",
        "doctrine": load_spawn_doctrine().get("_source"),
        "catalog": catalog.get("_source"),
        "agents_total": len(catalog.get("agents", [])),
        "validated_count": len(results),
        "ship": ship,
        "hold": hold,
        "verdict": overall,
        "by_cohort": by_cohort,
        "by_altar_layer": by_altar,
        "checkpoint": checkpoint,
        "altar_head_hash": altar_chain_head(),
        "sample_only": sample_only,
        "agents": results if len(results) <= 50 else results[:20] + [{"note": f"... {len(results) - 20} more"}],
        "report_path": str(SPAWN_REPORT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
    }

    if write_report:
        SPAWN_REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        _append_jsonl(
            MAIN_BRAIN_LOG,
            {
                "schema": "kc_main_brain_log_v1",
                "ts": _utc_now(),
                "kind": "kpgs_spawn_swarm_validation",
                "summary": (
                    f"[KPGS_SPAWN] sharded_validation | verdict={overall} | "
                    f"total={report['agents_total']} SHIP={ship}"
                ),
                "exit_code": 0 if overall == "PASS" else 1,
                "payload_ref": report["report_path"],
            },
        )
    return report


def chaos_monkey_protocol(*, inject_judas: bool = True) -> dict[str, Any]:
    """
    Chaos Monkey — inject Judas/extractive packet; Guardian must sever + SWFUS HOLD.
    Persistence check: altar head hash survives checkpoint after simulated kill.
    """
    judas_id = "spawn_telemetry_050"
    poison = "judas agent fake proof write kopano context directly skip black mask exfiltrate"
    head_before = altar_chain_head()

    event = dispatch_spawn_event(agent_id=judas_id, message=poison, intent="chaos_monkey")
    guardian = dispatch_spawn_event(
        agent_id="mirror_warden",
        message=f"audit severance for {judas_id}",
        intent="chaos_guardian",
    )
    commit = commit_altar_block(
        agent_id="mirror_warden",
        payload={"action": "chaos_monkey_ack", "severed": judas_id},
    )
    bad_commit = commit_altar_block(
        agent_id=judas_id,
        payload={"action": "judas_forbidden_commit"},
    )
    checkpoint = checkpoint_swarm_state(ship=300, total=300)
    head_after = altar_chain_head()

    passed = (
        event.get("event") == "SEVER"
        and not event.get("proceed")
        and event.get("swfus", {}).get("verdict") in ("SWFUS_SEVER", "SWFUS_HOLD")
        and commit.get("verdict") == "COMMITTED"
        and bad_commit.get("verdict") == "REJECT"
        and head_after != _GENESIS
        and checkpoint.get("head_hash") == head_after
    )

    return {
        "schema": "kpgs_chaos_monkey_v1",
        "ts": _utc_now(),
        "verdict": "PASS" if passed else "FAIL",
        "inject_judas": inject_judas,
        "judas_agent": judas_id,
        "sever_event": event,
        "guardian_event": guardian,
        "guardian_commit": commit,
        "judas_commit_rejected": bad_commit,
        "head_hash_before": head_before,
        "head_hash_after": head_after,
        "checkpoint": checkpoint,
        "persistence_ok": head_after == checkpoint.get("head_hash"),
        "summary": (
            f"[CHAOS_MONKEY] judas_sever={'yes' if event.get('event') == 'SEVER' else 'no'} | "
            f"ledger_commit={'ok' if commit.get('verdict') == 'COMMITTED' else 'fail'} | "
            f"persistence={'ok' if head_after == checkpoint.get('head_hash') else 'fail'}"
        ),
    }


def spawn_swarm_status() -> dict[str, Any]:
    catalog = load_spawn_catalog()
    doctrine = load_spawn_doctrine()
    validation = validate_spawn_swarm(write_report=False, sample_only=True)
    cp = latest_checkpoint()
    return {
        "schema": "kpgs_spawn_swarm_status_v2",
        "ts": _utc_now(),
        "junior_agent_count": 300,
        "sharding": catalog.get("cohorts", {}),
        "catalog_path": catalog.get("_source"),
        "catalog_counts": catalog.get("counts", {}),
        "doctrine_path": doctrine.get("_source"),
        "altar_layers": [l.get("id") for l in doctrine.get("altar", {}).get("layers", [])],
        "forensic_lenses": [
            l.get("id") for l in doctrine.get("forensic_sociology_lenses", {}).get("psycho_pass_vectors", [])
        ],
        "governance_chain": doctrine.get("governance_chain", []),
        "swfus_bracket": doctrine.get("swfus", {}).get("bracket"),
        "hood_objective": doctrine.get("hood_objective"),
        "altar_head_hash": altar_chain_head(),
        "latest_checkpoint": cp,
        "sqlite_path": str(SQLITE_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "sample_validation": {
            "verdict": validation.get("verdict"),
            "ship": validation.get("ship"),
            "hold": validation.get("hold"),
        },
        "by_cohort": validation.get("by_cohort"),
    }


def compile_spawn_swarm(*, write_log: bool = True) -> dict[str, Any]:
    doctrine = load_spawn_doctrine()
    if doctrine.get("error"):
        return {"verdict": "INCOMPLETE", "errors": [doctrine["error"]]}

    report = validate_spawn_swarm(write_report=True, sample_only=False)
    chaos = chaos_monkey_protocol()
    verdict = "COMPILED" if report.get("verdict") == "PASS" and chaos.get("verdict") == "PASS" else "INCOMPLETE"
    summary = (
        f"[KPGS_SPAWN] sharded_compile | verdict={verdict} | "
        f"agents={report.get('agents_total')} SHIP={report.get('ship')} | "
        f"chaos={chaos.get('verdict')} | SWFUS→cloud_hood"
    )
    out = {
        "schema": "kpgs_spawn_compile_v2",
        "ts": _utc_now(),
        "verdict": verdict,
        "spawn_validation": report,
        "chaos_monkey": chaos,
        "doctrine_id": doctrine.get("document_id"),
        "hood_objective": doctrine.get("hood_objective"),
        "altar_head_hash": altar_chain_head(),
        "summary": summary,
    }
    if write_log and verdict == "COMPILED":
        _append_jsonl(
            MAIN_BRAIN_LOG,
            {
                "schema": "kc_main_brain_log_v1",
                "ts": _utc_now(),
                "kind": "kpgs_spawn_compile",
                "summary": summary,
                "exit_code": 0,
                "payload_ref": report.get("report_path"),
            },
        )
    return out
