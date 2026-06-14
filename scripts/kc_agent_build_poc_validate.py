#!/usr/bin/env python3
"""Prove agent-building PoC — Bracket, BlackMask, Guardian/Identi, LPM/LPH, MAO, KPEFS."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.agent_build_poc_validate import validate_agent_build_poc  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--no-write", action="store_true", help="Skip report file + main brain")
    p.add_argument("--json-only", action="store_true")
    args = p.parse_args()

    report = validate_agent_build_poc(write_report=not args.no_write)
    if args.json_only:
        print(json.dumps(report, indent=2))
    else:
        print(f"VERDICT: {report['verdict']} ({report['passed']}/{report['total']})")
        if report.get("failed_checks"):
            print(f"FAILED: {', '.join(report['failed_checks'])}")
        for c in report["checks"]:
            mark = "ok" if c["verdict"] == "PASS" else "FAIL"
            print(f"  [{mark}] {c['check']}: {c.get('detail', '')[:80]}")
        print(f"\nReport: {report.get('report_path')}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
