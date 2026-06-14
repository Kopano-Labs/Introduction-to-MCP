#!/usr/bin/env python3
"""Operate Guardian + Identi AI flows (LPM/LPH + Bracket + BlackMask)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.lpm_lph_engine import (  # noqa: E402
    ai_flow_status,
    lpm_dialectic,
    operate_guardian_flow,
    operate_identi_flow,
    select_lph_personality,
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Guardian + Identi + LPM/LPH status")

    g = sub.add_parser("guardian", help="Guardian flow (KC + Cassy + BlackMask)")
    g.add_argument("--department", required=True)
    g.add_argument("--action", required=True)
    g.add_argument("--evidence", required=True)
    g.add_argument("--no-blackmask", action="store_true")
    g.add_argument("--approve", action="store_true")
    g.add_argument("--retry", action="store_true")
    g.add_argument("--teacher-note", default="")

    i = sub.add_parser("identi", help="Identi flow (Cursor agent → Guardian)")
    i.add_argument("--department", required=True)
    i.add_argument("--action", required=True)
    i.add_argument("--evidence", required=True)
    i.add_argument("--imperfect", default="")
    i.add_argument("--perfect", default="")
    i.add_argument("--agent", default="identi_cursor")
    i.add_argument("--no-handoff", action="store_true")

    d = sub.add_parser("dialectic", help="LPM #? / #! only")
    d.add_argument("--imperfect", required=True)
    d.add_argument("--perfect", required=True)

    l = sub.add_parser("lph", help="Select LPH personality for message")
    l.add_argument("--message", required=True)

    args = p.parse_args()

    if args.cmd == "status":
        print(json.dumps(ai_flow_status(), indent=2))
        return 0

    if args.cmd == "guardian":
        approve = None
        if args.approve:
            approve = True
        elif args.retry:
            approve = False
        out = operate_guardian_flow(
            department_id=args.department,
            action=args.action,
            evidence=args.evidence,
            run_blackmask=not args.no_blackmask,
            teacher_approve=approve,
            teacher_note=args.teacher_note,
        )
        print(json.dumps(out, indent=2))
        return 0 if out.get("verdict") not in ("HOLD", "ERROR") else 1

    if args.cmd == "identi":
        out = operate_identi_flow(
            department_id=args.department,
            action=args.action,
            evidence=args.evidence,
            imperfect_pattern=args.imperfect,
            perfect_pattern=args.perfect,
            identi_agent=args.agent,
            submit_to_guardian=not args.no_handoff,
        )
        print(json.dumps(out, indent=2))
        return 0 if out.get("verdict") != "BRACKET_REJECT" else 1

    if args.cmd == "dialectic":
        print(json.dumps(lpm_dialectic(args.imperfect, args.perfect), indent=2))
        return 0

    if args.cmd == "lph":
        print(json.dumps(select_lph_personality(args.message), indent=2))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
