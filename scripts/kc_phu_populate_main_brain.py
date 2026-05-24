#!/usr/bin/env python3
"""Populate Main Brain from Schematics + Bracket Protocol receipt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.phu_ecosystem import populate_main_brain  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Kopano-Phu Main Brain populate")
    parser.add_argument("--no-sync", action="store_true", help="Skip kc_sync_vault_logs")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = populate_main_brain(sync_vault_logs=not args.no_sync)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        bp = result["bracket_protocol"]
        print(
            f"Main Brain index: {result['main_brain_index']['present']}/"
            f"{result['main_brain_index']['total']} "
            f"({result['main_brain_index']['population_ratio']})"
        )
        print(f"Bracket Protocol breaking_point: {bp['breaking_point']}")
        for step in result["steps"]:
            print(f"  - {step['step']}: exit {step.get('exit_code', 'ok')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
