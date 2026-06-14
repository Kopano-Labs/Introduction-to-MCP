"""
Eco-Friendly PoC validation — internal oracles (Rosen M,R + Δ), not world acceptance.

Founding doctrine: 32.8% unemployment (docs/swarm-ops/UNEMPLOYMENT_32_8_DOCTRINE.json).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCTRINE_PATH = REPO_ROOT / "docs" / "swarm-ops" / "UNEMPLOYMENT_32_8_DOCTRINE.json"
ROSEN_PATH = REPO_ROOT / "docs" / "swarm-ops" / "ROSEN_DELTA_TIP.json"
AGENTS_CATALOG = REPO_ROOT / "docs" / "swarm-ops" / "agents" / "KP_APE_200_AGENTS.json"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
STATE_PATH = REPO_ROOT / "kopano-core" / ".kc" / "eco_poc_records.json"

_UNIT_HINT = re.compile(
    r"\b(pH|kWh|kW|L/s|m³|mm|°C|dB|Hz|Pa|N|kg|mg/L|%|rpm|V|A|Ω|mol|CFU|NTU|μg|mg)\b",
    re.I,
)
_WORLD_ORACLE_MARKERS = (
    "world acceptance",
    "viral",
    "term sheet",
    "vc approved",
    "market loves",
    "industry standard says",
    "everyone agrees",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_unemployment_doctrine() -> dict[str, Any]:
    if not DOCTRINE_PATH.is_file():
        return {"rate_percent": 32.8, "livelihood_signals": []}
    return json.loads(DOCTRINE_PATH.read_text(encoding="utf-8"))


def load_rosen_tip() -> dict[str, Any]:
    if not ROSEN_PATH.is_file():
        return {}
    return json.loads(ROSEN_PATH.read_text(encoding="utf-8"))


def _load_state() -> dict[str, Any]:
    if not STATE_PATH.is_file():
        return {"schema": "eco_poc_records_v1", "records": []}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"schema": "eco_poc_records_v1", "records": []}


def _save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _append_main_brain(summary: str, payload: dict[str, Any]) -> None:
    MAIN_BRAIN_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "schema": "kc_main_brain_log_v1",
        "ts": _utc_now(),
        "kind": "eco_poc_validate",
        "summary": summary,
        "payload_ref": payload.get("poc_id"),
        "exit_code": 0 if payload.get("verdict") == "PASS" else 1,
    }
    with MAIN_BRAIN_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _bracket_poc(
    poc_id: str,
    agent_id: str,
    verdict: str,
    oracles_pass: int,
    oracles_total: int,
    delta_summary: str,
) -> str:
    ts = _utc_now()
    return (
        f"[ECO_POC_VALIDATE] timestamp: {ts} | ecosystem: Kopano-Phu | "
        f"doctrine: UNEMPLOYMENT_32_8 | poc_id: {poc_id} | agent: {agent_id} | "
        f"oracles_pass: {oracles_pass}/{oracles_total} | delta: {delta_summary} | "
        f"verdict: {verdict} | oracle: internal_not_world"
    )


def _catalog_agent(agent_id: str) -> dict[str, Any] | None:
    if not AGENTS_CATALOG.is_file():
        return None
    try:
        data = json.loads(AGENTS_CATALOG.read_text(encoding="utf-8"))
        for a in data.get("agents", []):
            if a.get("id") == agent_id:
                return a
    except (json.JSONDecodeError, OSError):
        return None
    return None


def _parse_float(s: str) -> float | None:
    try:
        return float(str(s).strip())
    except (TypeError, ValueError):
        return None


def validate_eco_poc(
    *,
    agent_id: str,
    claim: str,
    model: str,
    relation: str,
    baseline: str,
    observed: str,
    unit: str,
    instrument: str = "",
    evidence: str = "",
    exit_code: int | None = None,
    livelihood_ids: list[str] | None = None,
    anticipated_delta: str = "",
    reject_world_oracle_text: str = "",
) -> dict[str, Any]:
    """
    Validate PoC against internal oracles. World acceptance is not an input — only receipts.
    """
    doctrine = load_unemployment_doctrine()
    poc_id = f"poc_{agent_id}_{_utc_now().replace(':', '').replace('-', '')[:15]}"
    catalog = _catalog_agent(agent_id)

    combined_text = " ".join(
        [claim, model, relation, reject_world_oracle_text, anticipated_delta]
    ).lower()
    world_reject = any(m in combined_text for m in _WORLD_ORACLE_MARKERS)

    oracles: list[dict[str, Any]] = []

    # Rosen M
    oracles.append(
        {
            "id": "rosen_M",
            "name": "Model stated",
            "passed": len(model.strip()) >= 20,
            "note": "Model must describe procedure or state (≥20 chars).",
        }
    )
    # Rosen R
    oracles.append(
        {
            "id": "rosen_R",
            "name": "Relation to reality",
            "passed": len(relation.strip()) >= 10,
            "note": "Instrument, log, or artifact path required.",
        }
    )
    # Anticipation
    oracles.append(
        {
            "id": "rosen_anticipate",
            "name": "Anticipatory delta",
            "passed": len(anticipated_delta.strip()) >= 3 or len(model.strip()) >= 40,
            "note": "State expected change before run (anticipated_delta or detailed model).",
        }
    )
    # Delta numeric
    b = _parse_float(baseline)
    o = _parse_float(observed)
    delta_ok = b is not None and o is not None and unit.strip() != ""
    delta_val = (o - b) if delta_ok and b is not None and o is not None else None
    oracles.append(
        {
            "id": "measurable_delta",
            "name": "Measurable Δ",
            "passed": delta_ok,
            "baseline": baseline,
            "observed": observed,
            "unit": unit,
            "delta": delta_val,
        }
    )
    # Unit plausibility
    unit_ok = bool(unit.strip()) and (
        bool(_UNIT_HINT.search(unit)) or len(unit.strip()) <= 12
    )
    oracles.append(
        {
            "id": "stem_unit",
            "name": "STEM unit",
            "passed": unit_ok,
        }
    )
    # Receipt
    evidence_path = Path(evidence) if evidence else None
    evidence_ok = (
        (evidence_path is not None and evidence_path.is_file())
        or (exit_code is not None and exit_code == 0)
        or (evidence.startswith("http") and len(evidence) > 12)
        or evidence.endswith(".jsonl")
    )
    oracles.append(
        {
            "id": "receipt_stack",
            "name": "Receipt (file, exit 0, or JSONL)",
            "passed": evidence_ok,
            "evidence": evidence,
            "exit_code": exit_code,
        }
    )
    # Servitude triad (minimal)
    oracles.append(
        {
            "id": "servitude_grit",
            "name": "Grit — claim bounded",
            "passed": 0 < len(claim.strip()) <= 500,
        }
    )
    oracles.append(
        {
            "id": "servitude_realism",
            "name": "Realism — proof fields present",
            "passed": delta_ok and evidence_ok,
        }
    )
    oracles.append(
        {
            "id": "servitude_aesthetics",
            "name": "Aesthetics — stem present",
            "passed": len(claim.strip()) >= 10,
        }
    )
    # Livelihood under 32.8%
    valid_liv = {x["id"] for x in doctrine.get("livelihood_signals", [])}
    chosen = [x for x in (livelihood_ids or []) if x in valid_liv]
    if not chosen and catalog:
        chosen = ["LIV-03"]
    oracles.append(
        {
            "id": "livelihood_32_8",
            "name": "Livelihood signals (32.8% doctrine)",
            "passed": len(chosen) >= 1,
            "signals": chosen,
            "doctrine_rate": doctrine.get("rate_percent", 32.8),
        }
    )
    # Not world oracle
    oracles.append(
        {
            "id": "not_world_oracle",
            "name": "No world-acceptance worship",
            "passed": not world_reject,
        }
    )

    passed = sum(1 for o in oracles if o["passed"])
    total = len(oracles)
    all_pass = passed == total
    verdict = "REJECT_WORLD_ORACLE" if world_reject else ("PASS" if all_pass else "HOLD")

    delta_summary = f"{delta_val} {unit}" if delta_val is not None else "unmeasured"
    summary = _bracket_poc(poc_id, agent_id, verdict, passed, total, delta_summary)

    record = {
        "poc_id": poc_id,
        "agent_id": agent_id,
        "verdict": verdict,
        "oracles": oracles,
        "oracles_pass": passed,
        "oracles_total": total,
        "summary": summary,
        "catalog_functionality": (catalog or {}).get("functionality"),
        "doctrine": "[UNEMPLOYMENT_32_8_DOCTRINE]",
        "validated_at": _utc_now(),
    }

    state = _load_state()
    state.setdefault("records", []).append(record)
    _save_state(state)
    _append_main_brain(summary, record)

    return record


def poc_doctrine_payload() -> dict[str, Any]:
    """Guide + Rosen tip + unemployment doctrine for API/MCP."""
    return {
        "guide": "docs/swarm-ops/ECO_FRIENDLY_POC_GUIDE.md",
        "unemployment_doctrine": load_unemployment_doctrine(),
        "rosen_delta_tip": load_rosen_tip(),
        "validate_with": load_unemployment_doctrine().get("what_we_validate_with", []),
        "not_god": "world_acceptance",
    }
