#!/usr/bin/env python3
"""KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1 — status, apply, BlackMask dry run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.phu_boot_governance import (  # noqa: E402
    apply_boot,
    blackmask_dry_run,
    boot_status,
    mesh_summary,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Kopano-Phu BOOT v1 governance")
    p.add_argument("command", choices=["status", "apply", "blackmask-dry-run", "mesh"], nargs="?")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    cmd = args.command or "status"

    if cmd == "status":
        out = boot_status()
    elif cmd == "apply":
        out = apply_boot()
    elif cmd == "blackmask-dry-run":
        out = blackmask_dry_run()
    else:
        out = mesh_summary()

    if args.json:
        print(json.dumps(out, indent=2))
    elif cmd == "blackmask-dry-run":
        print(f"BlackMask dry run — agents: {out['agents_total']} | SHIP: {out['ship']} | HOLD: {out['hold']}")
        for r in out.get("results", [])[:5]:
            print(f"  {r['agent_id']}: {r['verdict']}")
        if out["agents_total"] > 5:
            print(f"  ... +{out['agents_total'] - 5} more")
    elif cmd == "mesh":
        m = out
        print(f"Core: {m.get('governance_core')}")
        print(f"BlackMask agents: {m.get('blackmask_agent_count')}")
    else:
        print(json.dumps(out.get("mesh_summary", {}), indent=2))

    if cmd == "blackmask-dry-run":
        return 0 if out.get("all_ship") else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
