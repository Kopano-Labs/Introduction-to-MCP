#!/usr/bin/env python3
"""Begin Kopano-Phu department student operations + Black Mask drills."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.phu_apprenticeship import apprenticeship_status, begin_department_students, blackmask_drill  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Begin Kopano-Phu department students (TSAP)")
    parser.add_argument("--no-blackmask", action="store_true", help="Skip BlackMask drill per agent")
    parser.add_argument("--drill-agent", default="", help="Drill single agent only (no begin)")
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    args = parser.parse_args()

    if args.drill_agent:
        result = blackmask_drill(args.drill_agent)
    else:
        result = begin_department_students(run_blackmask=not args.no_blackmask)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("=== Kopano-Phu TSAP — Department Students ===\n")
        if args.drill_agent:
            print(f"Agent: {args.drill_agent}")
            print(f"Verdict: {result.get('verdict')}")
            print(result.get("summary", ""))
        else:
            for dept in result.get("departments_started", []):
                print(f"- {dept.get('display_name')} ({dept.get('id')})")
                print(f"  students: {dept.get('student_count')}")
                drills = dept.get("blackmask_drills") or []
                if drills:
                    passed = sum(1 for d in drills if d.get("verdict") == "SHIP")
                    print(f"  blackmask: {passed}/{len(drills)} SHIP")
        status = apprenticeship_status()
        print(f"\nCommandments: {status.get('commandments_count')} | Pillars: {status.get('pillars_count')}")
        print(f"State: {status.get('runtime', {}).get('state_path', 'kopano-core/.kc/phu_apprenticeship.json')}")

    return 0 if result.get("verdict", "SHIP") != "HOLD" or args.drill_agent or result.get("departments_started") else 1


if __name__ == "__main__":
    raise SystemExit(main())
