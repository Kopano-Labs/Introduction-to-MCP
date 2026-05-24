#!/usr/bin/env python3
"""Emit CF LPM comms-log activation block for created swarm agents + Main Brain receipt."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = REPO_ROOT / "docs" / "swarm-ops" / "agents" / "SWARM_AGENTS.json"
SEED = REPO_ROOT / "kopano-core" / "config" / "orch_agents.seed.json"
WIT = REPO_ROOT / "docs" / "swarm-ops" / "agents" / "cassy_wit_25.json"
FRAGMENTS = REPO_ROOT / "docs" / "swarm-ops" / "comms-log-fragments"
VAULT_COMMS = REPO_ROOT / "Schematics" / "04-Updates" / "comms-log.md"
COMPARE = (
    "https://github.com/Kopano-Labs/Introduction-to-MCP/"
    "compare/master...codex/kc-sovereign-gui-full-dev?expand=1"
)
ACTIONS = "https://github.com/Kopano-Labs/Introduction-to-MCP/actions"
PY = sys.executable

# Orch seed excludes doctrine-only roles (ledger, swarm slots, CF LPM).
ORCH_EXCLUDED = frozenset(
    {"kc", "mirror_warden", "kc_apprentice", "operational_general", "pipeline_drone", "cf_cloud"}
)


def _inventory(registry: dict, orch_ids: set[str]) -> dict:
    agents = registry.get("agents", [])
    slots = [a for a in agents if a.get("swarm_slot")]
    mesh = [a for a in agents if a.get("role") == "mesh"]
    triad = [a for a in agents if a.get("id") in {"cassy", "cassey", "kc"}]
    wit_n = 0
    if WIT.is_file():
        wit_n = int(json.loads(WIT.read_text(encoding="utf-8")).get("task_count", 0))

    return {
        "registry_total": len(agents),
        "triad": len(triad),
        "swarm_slots": len(slots),
        "mesh": len(mesh),
        "orch_runnable": len(orch_ids),
        "orch_excluded_doctrine": len(ORCH_EXCLUDED),
        "wit_tasks": wit_n,
        "lead_student": registry.get("lead_student", "cassy"),
        "operator_cf": "cf_cloud",
        "agents": [
            {
                "n": i + 1,
                "id": a["id"],
                "display_name": a.get("display_name", a["id"]),
                "role": a.get("role"),
                "swarm_slot": a.get("swarm_slot"),
                "orch_runnable": a["id"] in orch_ids,
                "cf_activate_via": (
                    "orch_agents.seed.json"
                    if a["id"] in orch_ids
                    else ("comms_lpm" if a["id"] == "cf_cloud" else "doctrine_registry")
                ),
            }
            for i, a in enumerate(agents)
        ],
    }


def _comms_markdown(inv: dict, *, git_sha: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    day = ts[:10]
    rows = "\n".join(
        f"| {a['n']} | `{a['id']}` | {a.get('swarm_slot') or '—'} | {a['role']} | "
        f"{'yes' if a['orch_runnable'] else 'no'} | {a['cf_activate_via']} |"
        for a in inv["agents"]
    )
    return f"""## {day} — CF LPM — swarm agent activation (BlackMass v2.0)

**Operator:** `CF_cloud` (Main Brain roadmap) · **Lead student:** `{inv['lead_student']}`  
**Status:** ACTIVATE — orch-runnable agents seeded; doctrine slots registered for CF orchestration.  
**Git:** `{git_sha[:12]}` · **UTC:** `{ts}`

### Counts (honest)

| Metric | Number |
|--------|--------|
| Registry agents (`SWARM_AGENTS.json`) | **{inv['registry_total']}** |
| Triad (Cassy / Cassey / KC) | **{inv['triad']}** |
| Swarm slots 001–004 | **{inv['swarm_slots']}** |
| Mesh (claude, grok, gemini, copilot) | **{inv['mesh']}** |
| Orch-runnable (`orch_agents.seed.json`) | **{inv['orch_runnable']}** |
| Doctrine-only (KC ledger + slots + CF) | **{inv['orch_excluded_doctrine']}** |
| Cassy WIT diaspora band | **{inv['wit_tasks']}** tasks |

External Kimi 300 swarm remains **manual-execution-required** — no fake `kimi_ack`.

### Agent roster (send to CF)

| # | id | slot | role | orch | CF path |
|---|-----|------|------|------|---------|
{rows}

### CF activation commands (repo)

```bash
python scripts/kc_swarm_agents_bootstrap.py
python scripts/kc_cassy_activate.py --seed-wit
python scripts/kc_cf_comms_activate.py --emit-only
python scripts/kc_log_append.py mainbrain --kind cf_swarm_activation --summary "CF LPM: orch agents activated" ...
```

**Canonical paths:** `docs/swarm-ops/agents/SWARM_AGENTS.json`, `kopano-core/config/orch_agents.seed.json`, JSONL under `docs/swarm-ops/logs/`.

---
"""


def _git_sha() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return (proc.stdout or "").strip() or "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-only", action="store_true", help="Write fragment only; no vault prepend")
    parser.add_argument("--no-log", action="store_true", help="Skip Main Brain JSONL append")
    parser.add_argument("--prepend-vault", action="store_true", help="Prepend to Schematics/04-Updates/comms-log.md if present")
    args = parser.parse_args()

    if not REGISTRY.is_file():
        print(f"missing {REGISTRY}", file=sys.stderr)
        return 1

    subprocess.run([PY, str(REPO_ROOT / "scripts" / "kc_swarm_agents_bootstrap.py")], cwd=REPO_ROOT, check=False)

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    orch_ids: set[str] = set()
    if SEED.is_file():
        orch_ids = set(json.loads(SEED.read_text(encoding="utf-8")).keys())

    inv = _inventory(registry, orch_ids)
    sha = _git_sha()
    md = _comms_markdown(inv, git_sha=sha)

    FRAGMENTS.mkdir(parents=True, exist_ok=True)
    out = FRAGMENTS / "CF_AGENT_ACTIVATION.md"
    out.write_text(md, encoding="utf-8")
    print(f"wrote {out}")
    print(
        f"counts: registry={inv['registry_total']} orch={inv['orch_runnable']} "
        f"slots={inv['swarm_slots']} mesh={inv['mesh']} wit={inv['wit_tasks']}"
    )

    if args.prepend_vault and VAULT_COMMS.parent.exists():
        VAULT_COMMS.parent.mkdir(parents=True, exist_ok=True)
        prior = VAULT_COMMS.read_text(encoding="utf-8") if VAULT_COMMS.is_file() else ""
        VAULT_COMMS.write_text(md + "\n" + prior, encoding="utf-8")
        print(f"prepended {VAULT_COMMS}")

    if not args.no_log:
        summary = (
            f"CF LPM activation comms: {inv['registry_total']} registry agents, "
            f"{inv['orch_runnable']} orch-runnable, {inv['swarm_slots']} swarm slots, "
            f"{inv['mesh']} mesh; fragment={out.relative_to(REPO_ROOT).as_posix()}"
        )
        subprocess.run(
            [
                PY,
                str(REPO_ROOT / "scripts" / "kc_log_append.py"),
                "mainbrain",
                "--kind",
                "cf_swarm_activation",
                "--summary",
                summary,
                "--exit-code",
                "0",
                "--evidence-url",
                COMPARE,
                "--evidence-url",
                ACTIONS,
            ],
            cwd=REPO_ROOT,
            check=False,
        )
        subprocess.run([PY, str(REPO_ROOT / "scripts" / "kc_sync_vault_logs.py")], cwd=REPO_ROOT, check=False)

    if not args.emit_only:
        print("\n--- paste into Obsidian comms-log (or use --prepend-vault) ---\n")
        print(md)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
