#!/usr/bin/env python3
"""CMD-03 external swarm lane — status, evidence URL preflight, KPEFS closure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.external_swarm_lane import (  # noqa: E402
    external_swarm_lane_status,
    kpefs_closure_status,
    validate_evidence_url,
)


def main() -> int:
    p = argparse.ArgumentParser(description="CMD-03 external swarm (Kimi manual receipt)")
    p.add_argument(
        "command",
        choices=["status", "closure", "validate-url", "guide"],
        nargs="?",
        default="status",
    )
    p.add_argument("--url", default="", help="Evidence URL for validate-url")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.command == "status":
        out = external_swarm_lane_status()
    elif args.command == "closure":
        out = kpefs_closure_status()
    elif args.command == "guide":
        out = external_swarm_lane_status()["guide"]
    else:
        out = validate_evidence_url(args.url)

    if args.json:
        print(json.dumps(out, indent=2))
    elif args.command == "status":
        r = out["receipt"]
        print(f"CMD-03 manual required: {out['manual_execution_required']}")
        print(f"Receipt on file: {r.get('receipt_present')} (count {r.get('receipt_count', 0)})")
        print(out["guide"]["cli_template"])
    elif args.command == "closure":
        print(f"Internal KPEFS: {out['internal_kpefs_complete']}")
        print(f"External swarm receipt: {out['external_swarm_receipt']}")
        print(f"Full closure: {out['full_closure']}")
        if out.get("next_human_step"):
            print(out["next_human_step"])
    elif args.command == "guide":
        for i, step in enumerate(out.get("steps", []), 1):
            print(f"{i}. {step}")
    else:
        print(f"valid: {out.get('valid')} — {out.get('reason')}")

    if args.command == "validate-url":
        return 0 if out.get("valid") else 1
    if args.command == "closure":
        return 0 if out.get("full_closure") else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
