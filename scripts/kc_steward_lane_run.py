#!/usr/bin/env python3
"""Activate KC + Cassy steward lane — profile, trust, Identi, Guardian."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.steward_lane import (  # noqa: E402
    run_steward_lane_activate,
    steward_lane_status,
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="KC+Cassy steward lane status")

    act = sub.add_parser("activate", help="Activate profile + flows + trust receipt")
    act.add_argument("--note", default="", help="Optional note on steward trust")
    act.add_argument(
        "--department",
        default="kopano_labs_experimentation",
        help="Department for Identi/Guardian",
    )
    act.add_argument("--action", default="", help="Override default steward action")
    act.add_argument("--evidence", default="", help="Override default evidence path")
    act.add_argument("--no-identi", action="store_true")
    act.add_argument("--no-guardian", action="store_true")
    act.add_argument("--no-teacher-approve", action="store_true")

    args = p.parse_args()

    if args.cmd == "status":
        print(json.dumps(steward_lane_status(), indent=2))
        return 0

    out = run_steward_lane_activate(
        note=args.note,
        department_id=args.department,
        run_identi=not args.no_identi,
        run_guardian=not args.no_guardian,
        teacher_approve=not args.no_teacher_approve,
        action=args.action or None,
        evidence=args.evidence or None,
    )
    print(json.dumps(out, indent=2))
    return 0 if out.get("verdict") == "ACTIVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
