"""Kopano-Phu Ecosystem — Cassy legacy lane, Main Brain (Schematics), sub-brain reattach."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "kopano-core" / "config" / "kopano_phu_ecosystem.json"
STATE_PATH = REPO_ROOT / "kopano-core" / ".kc" / "phu_subbrains.json"
SUB_BRAIN_VAULT = (
    "21-KOPANO LABS ECOSYSTEM/Operations General/SUB-BRAIN"
)
RETURN_GATE_REGISTRY = f"{SUB_BRAIN_VAULT}/RETURN-GATE-REGISTRY.md"
MAIN_BRAIN_LOG_REPO = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
PY = sys.executable


def schematics_root() -> Path:
    env = os.environ.get("KOPANO_SCHEMATICS_ROOT", "").strip()
    if env:
        return Path(env).resolve()
    return (REPO_ROOT / "Schematics").resolve()


def load_ecosystem_config() -> dict:
    if not CONFIG_PATH.is_file():
        return {"schema": "kopano_phu_ecosystem_v1", "sub_brains": []}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _sub_brain_vault_dir() -> Path:
    return schematics_root() / SUB_BRAIN_VAULT.replace("/", os.sep)


def _vault_folder_exists(folder: str) -> bool:
    return (_sub_brain_vault_dir() / folder).is_dir()


def _load_runtime_state() -> dict:
    if not STATE_PATH.is_file():
        return {"schema": "phu_subbrains_runtime_v1", "sub_brains": {}}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"schema": "phu_subbrains_runtime_v1", "sub_brains": {}}


def _save_runtime_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _parse_return_gate_table(text: str) -> dict[str, str]:
    """Parse RETURN-GATE-REGISTRY markdown table rows → sub-brain name → state."""
    gates: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line or "Sub-Brain" in line:
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) < 3:
            continue
        name = cells[0]
        state = cells[2].upper().replace("**", "")
        if name and state:
            gates[name] = state
    return gates


def merge_sub_brain_rows() -> list[dict]:
    """Config sub-brains + vault presence + runtime attachment."""
    cfg = load_ecosystem_config()
    runtime = _load_runtime_state()
    runtime_map: dict = runtime.get("sub_brains") or {}

    vault_gates: dict[str, str] = {}
    reg_path = schematics_root() / RETURN_GATE_REGISTRY.replace("/", os.sep)
    if reg_path.is_file():
        vault_gates = _parse_return_gate_table(reg_path.read_text(encoding="utf-8"))

    rows: list[dict] = []
    for sb in cfg.get("sub_brains", []):
        sid = sb["id"]
        folder = sb.get("vault_folder", "")
        display = sb.get("display_name", sid)
        vault_ok = _vault_folder_exists(folder) if folder else False
        rt = runtime_map.get(sid, {})
        if rt.get("attachment") == "attached":
            attachment = "attached"
        elif not vault_ok:
            attachment = "orphan"
        else:
            attachment = "detached"
        return_gate = vault_gates.get(display, sb.get("return_gate_default", "LOCKED"))
        rows.append(
            {
                **sb,
                "vault_present": vault_ok,
                "vault_path": str(_sub_brain_vault_dir() / folder) if folder else "",
                "return_gate": return_gate,
                "attachment": attachment,
                "cassy_lane": rt.get("cassy_lane", attachment != "detached"),
                "reattached_at": rt.get("reattached_at"),
            }
        )
    return rows


def reattach_detached_subbrains(*, dry_run: bool = False) -> dict:
    """Reattach unused/detached sub-brains to Cassy legacy lane under Kopano-Phu."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    state = _load_runtime_state()
    sub_map: dict = dict(state.get("sub_brains") or {})
    reattached: list[str] = []
    skipped: list[str] = []

    for row in merge_sub_brain_rows():
        sid = row["id"]
        if row["attachment"] == "attached" and sub_map.get(sid, {}).get("attachment") == "attached":
            skipped.append(sid)
            continue
        if not row["vault_present"]:
            skipped.append(sid)
            continue
        reattached.append(sid)
        if not dry_run:
            sub_map[sid] = {
                "attachment": "attached",
                "cassy_lane": True,
                "parent": row.get("parent"),
                "return_gate": row.get("return_gate"),
                "reattached_at": now,
            }

    if not dry_run:
        state["sub_brains"] = sub_map
        state["last_reattach"] = now
        _save_runtime_state(state)

    return {
        "schema": "phu_reattach_v1",
        "dry_run": dry_run,
        "reattached": reattached,
        "skipped": skipped,
        "total_attached": sum(1 for s in sub_map.values() if s.get("attachment") == "attached"),
    }


def main_brain_index() -> dict:
    """Index key Main Brain paths under Schematics (populate / audit surface)."""
    root = schematics_root()
    cfg = load_ecosystem_config()
    mb = cfg.get("main_brain", {})
    entries: list[dict] = []

    def add(rel: str, kind: str) -> None:
        p = root / rel.replace("/", os.sep)
        entries.append(
            {
                "rel": rel,
                "kind": kind,
                "exists": p.is_file() or p.is_dir(),
                "path": str(p),
            }
        )

    for rel in mb.get("canonical_logs", []):
        add(rel, "log")
    add(mb.get("registry", RETURN_GATE_REGISTRY), "registry")
    add(mb.get("roadmap_master", ""), "roadmap")
    add("18-PROTOCOLS/Kopano Context Master Protocol Ledger And Sovereign Architecture.md", "protocol")
    add("00-Home/Now.md", "home")
    add("04-Updates/comms-log.md", "comms")

    present = sum(1 for e in entries if e["exists"])
    return {
        "schema": "main_brain_index_v1",
        "schematics_root": str(root),
        "entries": entries,
        "present": present,
        "total": len(entries),
        "population_ratio": round(present / len(entries), 3) if entries else 0.0,
    }


def bracket_protocol_status() -> dict:
    """
    Bracket Protocol — The Breaking Point.

    Breaking when: Main Brain index populated, flagship sub-brains attached,
    and a bracket receipt exists in Main Brain log.
    """
    index = main_brain_index()
    rows = merge_sub_brain_rows()
    attached = [r for r in rows if r["attachment"] == "attached"]
    detached = [r for r in rows if r["attachment"] == "detached"]
    flagship = [r for r in rows if r.get("flagship")]
    flagship_attached = [r for r in flagship if r["attachment"] == "attached"]

    bracket_receipt = False
    last_bracket: dict | None = None
    if MAIN_BRAIN_LOG_REPO.is_file():
        for raw in reversed(MAIN_BRAIN_LOG_REPO.read_text(encoding="utf-8").splitlines()):
            raw = raw.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError:
                continue
            summary = str(row.get("summary", ""))
            kind = str(row.get("kind", ""))
            if kind in {"bracket_protocol", "kimi_ack", "main_brain_audit"} or "[BRACKET" in summary.upper():
                bracket_receipt = True
                last_bracket = {
                    "kind": kind,
                    "ts": row.get("ts"),
                    "summary": summary[:240],
                }
                break

    population_ok = index["population_ratio"] >= 0.85
    subbrains_ok = len(detached) == 0 and len(attached) >= len(rows) - 1
    flagship_ok = len(flagship_attached) >= 1
    breaking_point = population_ok and subbrains_ok and bracket_receipt

    return {
        "schema": "bracket_protocol_v1",
        "name": "Bracket Protocol",
        "tagline": "The Breaking Point",
        "ecosystem": "Kopano-Phu",
        "parents": ["Kopano Labs", "Ama-Phu Entertainment"],
        "cassy_legacy": load_ecosystem_config().get("cassy_legacy", {}),
        "breaking_point": breaking_point,
        "criteria": {
            "main_brain_populated": population_ok,
            "sub_brains_attached": subbrains_ok,
            "bracket_receipt": bracket_receipt,
            "flagship_attached": flagship_ok,
        },
        "counts": {
            "sub_brains_total": len(rows),
            "attached": len(attached),
            "detached": len(detached),
        },
        "main_brain_index": index,
        "last_bracket_receipt": last_bracket,
        "bracket_format": "[BRACKET_PROTOCOL] timestamp: … | ecosystem: Kopano-Phu | status: …",
    }


def populate_main_brain(*, sync_vault_logs: bool = True) -> dict:
    """Sync vault logs, reattach sub-brains, append Bracket Protocol receipt."""
    steps: list[dict] = []

    if sync_vault_logs:
        proc = subprocess.run(
            [PY, str(REPO_ROOT / "scripts" / "kc_sync_vault_logs.py")],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=180,
        )
        steps.append(
            {
                "step": "sync_vault_logs",
                "exit_code": proc.returncode,
                "tail": (proc.stdout or proc.stderr or "")[-800:],
            }
        )

    reattach = reattach_detached_subbrains(dry_run=False)
    steps.append({"step": "reattach_subbrains", **reattach})

    index = main_brain_index()
    bracket = bracket_protocol_status()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summary = (
        f"[BRACKET_PROTOCOL] timestamp: {ts} | ecosystem: Kopano-Phu | "
        f"status: {'breaking_point' if bracket['breaking_point'] else 'arming'} | "
        f"main_brain_ratio: {index['population_ratio']} | "
        f"attached: {reattach.get('total_attached', 0)}"
    )

    compare_url = (
        "https://github.com/Kopano-Labs/Introduction-to-MCP/"
        "compare/master...codex/kc-sovereign-gui-full-dev?expand=1"
    )
    actions_url = "https://github.com/Kopano-Labs/Introduction-to-MCP/actions"
    proc2 = subprocess.run(
        [
            PY,
            str(REPO_ROOT / "scripts" / "kc_log_append.py"),
            "mainbrain",
            "--kind",
            "bracket_protocol",
            "--summary",
            summary,
            "--exit-code",
            "0",
            "--evidence-url",
            compare_url,
            "--evidence-url",
            actions_url,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    steps.append(
        {
            "step": "main_brain_receipt",
            "exit_code": proc2.returncode,
            "summary": summary,
            "tail": (proc2.stdout or proc2.stderr or "")[-400:],
        }
    )

    return {
        "schema": "populate_main_brain_v1",
        "schematics_root": str(schematics_root()),
        "main_brain_index": index,
        "bracket_protocol": bracket_protocol_status(),
        "steps": steps,
    }


def ecosystem_payload() -> dict:
    cfg = load_ecosystem_config()
    rows = merge_sub_brain_rows()
    return {
        "schema": "kopano_phu_ecosystem_status_v1",
        "title": cfg.get("title"),
        "subtitle": cfg.get("subtitle"),
        "breaking_point_protocol": cfg.get("breaking_point_protocol"),
        "schematics_root": str(schematics_root()),
        "parents": cfg.get("parents", []),
        "cassy_legacy": cfg.get("cassy_legacy", {}),
        "sub_brains": rows,
        "main_brain": main_brain_index(),
        "bracket_protocol": bracket_protocol_status(),
        "runtime_state_path": str(STATE_PATH.relative_to(REPO_ROOT)),
        "docs": {
            "ecosystem": "docs/swarm-ops/KOPANO_PHU_ECOSYSTEM.md",
            "bracket": "docs/swarm-ops/BRACKET_PROTOCOL.md",
            "legacy_orch": "docs/swarm-ops/LEGACY_ORCH.md",
        },
    }
