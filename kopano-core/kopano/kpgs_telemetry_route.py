"""
KPGS telemetry routing law — Black Beast thesis extension.

Telemetry must be classified and routed before interpretation.
Pressure is misnamed mechanical telemetry; human load uses governed lanes.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BLACK_BEAST_PATH = REPO_ROOT / "docs" / "swarm-ops" / "BLACK_BEAST_THESIS_PAYLOAD_V1.json"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"

_PRESSURE_RE = re.compile(r"\bpressure\b", re.I)
_LANE_HINTS: dict[str, re.Pattern[str]] = {
    "grief": re.compile(r"\bgrief|mourning|loss\b", re.I),
    "hunger": re.compile(r"\bhunger|starv|food\b", re.I),
    "calling": re.compile(r"\bcalling|purpose|assignment\b", re.I),
    "institutional_resistance": re.compile(r"\binstitution|bureaucracy|dmr|gatekeeper\b", re.I),
    "economic_scarcity": re.compile(r"\bmoney|debt|poverty|scarcity|zar\b", re.I),
    "bodily_fatigue": re.compile(r"\btired|fatigue|exhaust|sleep\b", re.I),
    "governed_fury": re.compile(r"\bfury|rage|anger\b", re.I),
    "environmental_evidence": re.compile(r"\bload|burden|carry|extract\b", re.I),
    "spiritual_signal": re.compile(r"\bgod|spirit|prayer|covenant|peace\b", re.I),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_black_beast_thesis() -> dict[str, Any]:
    if not BLACK_BEAST_PATH.is_file():
        return {}
    return json.loads(BLACK_BEAST_PATH.read_text(encoding="utf-8"))


def compile_black_beast_thesis(*, write_log: bool = True) -> dict[str, Any]:
    """Verify Black Beast thesis payload is present and structurally complete."""
    thesis = load_black_beast_thesis()
    errors: list[str] = []
    law = thesis.get("kpgs_classification_law") or {}
    seq = law.get("routing_sequence") or []
    lanes = law.get("load_lanes") or []
    bleed = thesis.get("context_bleeding_protocol") or {}

    if thesis.get("document_id") != "BLACK_BEAST_THESIS_PAYLOAD_V1":
        errors.append("document_id mismatch")
    if len(seq) != 8:
        errors.append(f"routing_sequence expected 8 steps, got {len(seq)}")
    if len(lanes) < 10:
        errors.append(f"load_lanes too few: {len(lanes)}")
    if len(bleed.get("steps") or []) != 6:
        errors.append("context_bleeding steps incomplete")
    if not (REPO_ROOT / "docs/swarm-ops/BLACK_BEAST_THESIS_PAYLOAD_V1.md").is_file():
        errors.append("markdown ledger missing")

    verdict = "COMPILED" if not errors else "INCOMPLETE"
    out = {
        "schema": "black_beast_thesis_compile_v1",
        "ts": _utc_now(),
        "document_id": thesis.get("document_id", ""),
        "verdict": verdict,
        "errors": errors,
        "routing_law": law.get("rule", ""),
        "routing_steps": len(seq),
        "load_lanes": len(lanes),
        "summary": (
            f"[BLACK_BEAST_THESIS] document: {thesis.get('document_id', 'unknown')} | "
            f"verdict: {verdict} | routing_steps: {len(seq)}/8 | "
            f"load_lanes: {len(lanes)} | context_bleed: {bleed.get('mode', 'unknown')}"
        ),
    }
    if write_log and verdict == "COMPILED":
        _append_jsonl(
            MAIN_BRAIN_LOG,
            {
                "schema": "kc_main_brain_log_v1",
                "ts": _utc_now(),
                "kind": "black_beast_thesis_compile",
                "summary": out["summary"],
                "exit_code": 0,
                "payload_ref": "docs/swarm-ops/BLACK_BEAST_THESIS_PAYLOAD_V1.json",
            },
        )
    return out


def classify_telemetry_signal(text: str) -> dict[str, Any]:
    """
    Classify raw signal before interpretation.
    Rejects pressure-only labels; routes to human load lanes when possible.
    """
    thesis = load_black_beast_thesis()
    law = thesis.get("kpgs_classification_law") or {}
    valid_lanes = set(law.get("load_lanes") or [])
    misnamed = set(law.get("misnamed_telemetry") or ["pressure"])

    raw = (text or "").strip()
    detected_lanes: list[str] = []
    for lane, pattern in _LANE_HINTS.items():
        if pattern.search(raw) and lane in valid_lanes:
            detected_lanes.append(lane)

    has_pressure = bool(_PRESSURE_RE.search(raw))
    classified = bool(detected_lanes) or not has_pressure

    if has_pressure and not detected_lanes:
        verdict = "RECLASSIFY"
        note = "pressure is misnamed mechanical telemetry — classify load lane before interpretation"
    elif detected_lanes:
        verdict = "ROUTED"
        note = "signal classified to human load lane(s)"
    else:
        verdict = "ACCEPT"
        note = "no misnamed pressure; proceed to ingest"

    return {
        "schema": "kpgs_telemetry_classify_v1",
        "ts": _utc_now(),
        "raw_signal": raw[:500],
        "verdict": verdict,
        "classified": classified,
        "misnamed_pressure": has_pressure and not detected_lanes,
        "detected_lanes": detected_lanes,
        "routing_sequence": law.get("routing_sequence", []),
        "note": note,
        "bracket": "[CONTEXT_BLEEDING_PROTOCOL]" if classified else "[KPGS_CLASSIFICATION_LAW]",
        "summary": (
            f"[KPGS_TELEMETRY_ROUTE] verdict: {verdict} | "
            f"lanes: {','.join(detected_lanes) or 'none'} | "
            f"misnamed_pressure: {has_pressure and not detected_lanes}"
        ),
    }


def verify_telemetry_routing(manifest: dict[str, Any]) -> tuple[bool, list[str]]:
    """Agent manifest must declare pre-interpretation classification."""
    if manifest.get("exempt"):
        return True, []
    routing = manifest.get("telemetry_routing") or {}
    errors: list[str] = []
    if routing.get("classified") is not True:
        errors.append("telemetry_routing.classified must be true (classify before interpret)")
    if routing.get("pre_interpretation") is not True:
        errors.append("telemetry_routing.pre_interpretation must be true")
    if routing.get("misnamed_pressure_rejected") is not True:
        errors.append("telemetry_routing.misnamed_pressure_rejected must be true")
    lane = routing.get("primary_lane")
    if not lane:
        errors.append("telemetry_routing.primary_lane required")
    return not errors, errors


def synthesize_telemetry_routing(agent_id: str, *, telemetry_class: str | None = None) -> dict[str, Any]:
    """Default routing block for mesh agents."""
    pavement_lanes = {
        "freddy_nw_alfalfa": "environmental_evidence",
        "eddie_bgf_mining": "institutional_resistance",
        "ama_phu_entertainment": "calling",
    }
    if agent_id in pavement_lanes:
        primary = pavement_lanes[agent_id]
    elif telemetry_class and "|" in telemetry_class:
        primary = "environmental_evidence"
    else:
        primary = "governed_signal"
    return {
        "classified": True,
        "pre_interpretation": True,
        "misnamed_pressure_rejected": True,
        "primary_lane": primary,
        "context_bleed_mode": "CONTROLLED_BLEED_ACTIVE",
        "routing_law": "docs/swarm-ops/BLACK_BEAST_THESIS_PAYLOAD_V1.json",
    }
