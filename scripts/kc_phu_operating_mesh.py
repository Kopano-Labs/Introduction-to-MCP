#!/usr/bin/env python3
"""Phase 3 operating mesh — promote flagship sub-brains with PROOF-01..03."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.operating_mesh import (  # noqa: E402
    promote_all_flagships,
    promote_flagship,
    operating_mesh_status,
)


def main() -> int:
    p = argparse.ArgumentParser(description="KPEFS operating mesh (Phase 3)")
    p.add_argument(
        "command",
        choices=["status", "promote-all", "promote-one"],
        nargs="?",
        default="status",
    )
    p.add_argument("--agent-id", help="Sub-brain id for promote-one")
    p.add_argument("--force", action="store_true", help="Re-run promotion even if operating")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    skip = not args.force
    if args.command == "status":
        out = operating_mesh_status()
    elif args.command == "promote-all":
        out = promote_all_flagships(skip_if_operating=skip)
    else:
        if not args.agent_id:
            print("promote-one requires --agent-id", file=sys.stderr)
            return 2
        out = promote_flagship(args.agent_id, skip_if_operating=skip)

    if args.json:
        print(json.dumps(out, indent=2))
    elif args.command == "status":
        print(
            f"Operating mesh: {out['operating_count']}/{out['flagships_total']} | "
            f"phase3_exit: {out['phase3_exit_met']}"
        )
        for row in out.get("flagships", []):
            print(f"  {row['sub_brain_id']}: {row.get('status')} | PoC {row.get('poc_verdict') or '—'}")
    elif args.command == "promote-all":
        print(
            f"Promote all — operating: {out['operating']}/{out['flagships_total']} | "
            f"exit: {out['phase3_exit_met']}"
        )
    else:
        print(f"{out.get('sub_brain_id')}: {out.get('status', out.get('error', '—'))}")

    if args.command == "promote-all":
        return 0 if out.get("phase3_exit_met") else 1
    if args.command == "promote-one" and out.get("status") != "operating" and not out.get("skipped"):
        return 1 if out.get("error") or out.get("status") == "incomplete" else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
