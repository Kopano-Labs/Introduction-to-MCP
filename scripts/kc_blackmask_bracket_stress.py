#!/usr/bin/env python3
"""CF tranche — heavy BlackMask + bracket protocol stress test."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.blackmask_bracket_stress import run_blackmask_bracket_stress  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true", help="Print full report JSON")
    p.add_argument("--no-report-file", action="store_true")
    p.add_argument(
        "--operator",
        default="CF_cloud",
        help="CF dispatch operator tag (e.g. CF{CODEX})",
    )
    args = p.parse_args()

    report = run_blackmask_bracket_stress(
        write_report=not args.no_report_file,
        operator=args.operator,
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"BlackMask+bracket stress: {report['verdict']}")
        print(f"  checks: {report['passed']}/{report['total']}")
        if report.get("failed_checks"):
            print(f"  failed: {', '.join(report['failed_checks'])}")
        print(f"  mesh drilled: {report.get('mesh_agents_drilled')}")
        print(f"  report: {report.get('report_path')}")

    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
