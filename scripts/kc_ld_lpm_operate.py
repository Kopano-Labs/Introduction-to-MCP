#!/usr/bin/env python3
"""LD operates as LPM — stress ideas under Bracket + BlackMask + BlackMass."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.ld_lpm_operate import run_ld_lpm_tranche, stress_idea  # noqa: E402
from kopano.lpm_lph_engine import ai_flow_status  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="AI flow + LPM/LPH status")

    s = sub.add_parser("stress", help="Stress one idea through protocol stack")
    s.add_argument("--idea", required=True, help="Idea id slug")
    s.add_argument("--action", required=True)
    s.add_argument("--evidence", required=True)

    t = sub.add_parser("tranche", help="Full LD tranche: stress → Identi → Guardian")
    t.add_argument("--idea", required=True)
    t.add_argument("--action", required=True)
    t.add_argument("--evidence", required=True)
    t.add_argument("--department", default="kopano_labs_experimentation")
    t.add_argument("--operator", default="LD-LPM")
    t.add_argument("--no-approve", action="store_true")

    args = p.parse_args()

    if args.cmd == "status":
        print(json.dumps(ai_flow_status(), indent=2))
        return 0

    if args.cmd == "stress":
        out = stress_idea(idea_id=args.idea, action=args.action, evidence=args.evidence)
        print(json.dumps(out, indent=2))
        return 0 if out.get("verdict") == "SHIP" else 1

    out = run_ld_lpm_tranche(
        idea_id=args.idea,
        action=args.action,
        evidence=args.evidence,
        department_id=args.department,
        operator=args.operator,
        teacher_approve=not args.no_approve,
    )
    print(json.dumps(out, indent=2))
    return 0 if out.get("verdict") == "SHIP" else 1


if __name__ == "__main__":
    raise SystemExit(main())
