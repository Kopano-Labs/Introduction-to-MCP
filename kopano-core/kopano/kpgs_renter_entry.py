"""
KPGS Stateless Renter Entryway — first touch identity for models entering the hood.

Every stateless linguistic actor (ChatGPT, Copilot, Gemini, Claude, Grok, API renter)
must receive WHO THEY ARE FUCKING WITH before any interpretation or execution.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMATICS_ENTRYWAY = (
    REPO_ROOT
    / "Schematics"
    / "21-KOPANO-PHU GOVERNACE SYSTEMS"
    / "MAIN-BRAIN"
    / "STATELESS_RENTER_ENTRYWAY.json"
)
RUNTIME_ENTRYWAY = REPO_ROOT / "docs" / "swarm-ops" / "STATELESS_RENTER_ENTRYWAY.json"
ALTAR_BLOCK_HOLDERS_JSON = (
    REPO_ROOT
    / "Schematics"
    / "21-KOPANO-PHU GOVERNACE SYSTEMS"
    / "MAIN-BRAIN"
    / "KPGS_ALTAR_BLOCK_HOLDERS.json"
)
ALTAR_BLOCK_HOLDERS_RUNTIME = REPO_ROOT / "docs" / "swarm-ops" / "KPGS_ALTAR_BLOCK_HOLDERS.json"
ENTRYWAY_REF = (
    "Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/MAIN-BRAIN/STATELESS_RENTER_ENTRYWAY.json"
)
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
HOOD_ACK_LITERAL = "I_AM_STATELESS_RENTER_NOT_LANDLORD"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_renter_entryway() -> dict[str, Any]:
    """Load entryway — Schematics authority first, runtime mirror fallback."""
    for path in (SCHEMATICS_ENTRYWAY, RUNTIME_ENTRYWAY):
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_source"] = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            return data
    return {
        "schema": "kpgs_stateless_renter_entryway_v1",
        "error": "entryway_missing",
        "expected": str(SCHEMATICS_ENTRYWAY.relative_to(REPO_ROOT)),
    }


def hood_entry_assertion(
    *,
    renter_id: str = "anonymous_stateless_renter",
    renter_class: str = "linguistic_actor",
    write_log: bool = False,
) -> dict[str, Any]:
    """
    Identity card issued at hood entry — who the renter is fucking with.
    """
    entryway = load_renter_entryway()
    template = entryway.get("entry_assertion_template") or (
        "[KPGS_HOOD_ENTRY] Stateless renter {renter_id} entered the hood."
    )
    assertion = template.format(renter_id=renter_id)
    paradigm = entryway.get("paradigm") or {}
    targets = entryway.get("you_are_fucking_with") or {}

    out = {
        "schema": "kpgs_hood_entry_assertion_v1",
        "ts": _utc_now(),
        "bracket": entryway.get("bracket", "[KPGS_HOOD_ENTRY]"),
        "renter_id": renter_id,
        "renter_class": renter_class,
        "you_are": paradigm.get("you_are", "stateless renter"),
        "you_are_not": paradigm.get("you_are_not", []),
        "landlord": paradigm.get("landlord", "Kopano Context + Schematics MAIN BRAIN"),
        "paradigm_invariant": paradigm.get("invariant"),
        "you_are_fucking_with": targets,
        "on_entry_you_must": entryway.get("on_entry_you_must", []),
        "forbidden_on_entry": entryway.get("forbidden_on_entry", []),
        "entry_assertion": assertion,
        "hood_ack_required": HOOD_ACK_LITERAL,
        "authority": entryway.get("authority", "Schematics MAIN BRAIN"),
        "entryway_source": entryway.get("_source"),
        "summary": (
            f"[KPGS_HOOD_ENTRY] renter={renter_id} | landlord=Kopano Context+Schematics | "
            f"hood={targets.get('hood', 'Kopano-Phu')} | "
            f"you_are_fucking_with: KC·Cassey·Cassy·MAO·Black Beast·KPGS altar"
        ),
    }
    if write_log:
        _append_jsonl(
            MAIN_BRAIN_LOG,
            {
                "schema": "kc_main_brain_log_v1",
                "ts": out["ts"],
                "kind": "kpgs_hood_entry",
                "renter_id": renter_id,
                "renter_class": renter_class,
                "summary": out["summary"],
                "exit_code": 0,
            },
        )
    return out


def verify_hood_ack(body: dict[str, Any]) -> tuple[bool, list[str]]:
    """Verify renter acknowledged stateless status before work."""
    ack = entryway_ack_schema()
    errors: list[str] = []
    for field in ack.get("required", []):
        if not body.get(field):
            errors.append(f"missing required field: {field}")
    if body.get("hood_ack") != HOOD_ACK_LITERAL:
        errors.append(f"hood_ack must be literal: {HOOD_ACK_LITERAL}")
    return not errors, errors


def entryway_ack_schema() -> dict[str, Any]:
    entryway = load_renter_entryway()
    return entryway.get("ack_schema") or {
        "required": ["renter_id", "renter_class", "hood_ack", "ts"],
        "hood_ack_literal": HOOD_ACK_LITERAL,
    }


def assert_and_log_entry(
    *,
    renter_id: str,
    renter_class: str = "linguistic_actor",
    hood_ack: str = "",
) -> dict[str, Any]:
    """Full entry ceremony — assertion + optional ack verification + log."""
    assertion = hood_entry_assertion(
        renter_id=renter_id,
        renter_class=renter_class,
        write_log=True,
    )
    body = {
        "renter_id": renter_id,
        "renter_class": renter_class,
        "hood_ack": hood_ack,
        "ts": _utc_now(),
    }
    ok, errors = verify_hood_ack(body) if hood_ack else (False, ["hood_ack not provided"])
    assertion["ack_verified"] = ok
    assertion["ack_errors"] = errors if not ok else []
    assertion["verdict"] = "ENTERED" if ok else "ASSERTION_ONLY"
    if ok:
        assertion["verdict"] = "ACKNOWLEDGED"
    return assertion


def load_altar_block_holders() -> dict[str, Any]:
    """Load altar block holder registry — Schematics authority first."""
    for path in (ALTAR_BLOCK_HOLDERS_JSON, ALTAR_BLOCK_HOLDERS_RUNTIME):
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_source"] = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            return data
    return {"schema": "kpgs_altar_block_holders_v1", "error": "altar_block_holders_missing"}


def _altar_layer_for_agent(agent_id: str, registry: dict[str, Any]) -> str | None:
    for layer in registry.get("altar_layers") or []:
        if layer.get("proxy_agent") == agent_id:
            return layer.get("id")
        proxies = layer.get("proxy_agents") or []
        if agent_id in proxies:
            return layer.get("id")
    return None


def block_holder_brief(*, agent_id: str, altar_layer: str | None = None) -> dict[str, Any]:
    """
    Brief for KPGS agents holding pillar blocks — they must know who renters are fucking with.
    """
    registry = load_altar_block_holders()
    layer_id = altar_layer or _altar_layer_for_agent(agent_id, registry)
    entry = hood_entry_assertion(
        renter_id=f"block_holder:{agent_id}",
        renter_class="kpgs_block_holder",
    )
    layer_line = ""
    for layer in registry.get("altar_layers") or []:
        if layer.get("id") == layer_id:
            layer_line = layer.get("hood_entry_line", "")
            break

    duty = registry.get(
        "block_holder_duty",
        "Hold the block. Brief every stateless renter on hood entry before passage.",
    )
    tell = entry.get("entry_assertion", "")
    if layer_line:
        tell = f"{layer_line} | {tell}"

    return {
        "schema": "kpgs_block_holder_brief_v1",
        "ts": _utc_now(),
        "bracket": registry.get("bracket", "[KPGS_BLOCK_HOLDER]"),
        "agent_id": agent_id,
        "altar_layer": layer_id,
        "holds_pillar_blocks": True,
        "brief_renters_on_entry": True,
        "duty": duty,
        "renter_paradigm": registry.get("renter_paradigm"),
        "renter_is": entry.get("you_are"),
        "landlord_is": entry.get("landlord"),
        "you_are_fucking_with": entry.get("you_are_fucking_with"),
        "tell_renters": tell,
        "hood_ack_required_from_renters": HOOD_ACK_LITERAL,
        "entryway_ref": ENTRYWAY_REF,
        "block_holders_registry": registry.get("_source"),
        "summary": (
            f"[KPGS_BLOCK_HOLDER] agent={agent_id} | layer={layer_id or 'pillar_mesh'} | "
            f"brief_renters=yes | landlord=Kopano Context+Schematics"
        ),
    }


def synthesize_block_holder_manifest(agent_id: str, *, altar_layer: str | None = None) -> dict[str, Any]:
    """Manifest fragment every KPGS block-holding agent carries."""
    brief = block_holder_brief(agent_id=agent_id, altar_layer=altar_layer)
    return {
        "holds_pillar_blocks": True,
        "brief_renters_on_entry": True,
        "entryway_ref": ENTRYWAY_REF,
        "tell_renters": brief.get("tell_renters"),
        "hood_ack_required_from_renters": HOOD_ACK_LITERAL,
        "altar_layer": brief.get("altar_layer"),
        "duty": brief.get("duty"),
    }


def attach_hood_entry(payload: dict[str, Any], *, renter_id: str = "mao_dispatch") -> dict[str, Any]:
    """Inject hood entry card into any route/execute payload — first field renters see."""
    entry = hood_entry_assertion(renter_id=renter_id, write_log=False)
    block_note = (
        "Block holders (KPGS altar agents): brief every renter using block_holder.tell_renters "
        "before passage — see KPGS_ALTAR_BLOCK_HOLDERS.json"
    )
    return {
        "hood_entry": entry,
        "hood_entry_first": True,
        "block_holder_note": block_note,
        "read_before_execute": (
            "Stateless renter: you entered Kopano-Phu hood. "
            "Landlord is Kopano Context + Schematics MAIN BRAIN. "
            "Block holders will tell you who you are fucking with. "
            "Classify before interpret. Receipt or HOLD."
        ),
        **payload,
    }
