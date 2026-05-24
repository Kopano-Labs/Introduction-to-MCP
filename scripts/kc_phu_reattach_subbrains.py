#!/usr/bin/env python3
"""Reattach detached Kopano-Phu sub-brains to Cassy legacy lane."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.phu_ecosystem import reattach_detached_subbrains  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = reattach_detached_subbrains(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Reattached: {', '.join(result['reattached']) or '(none)'}")
        print(f"Skipped: {', '.join(result['skipped']) or '(none)'}")
        print(f"Total attached: {result['total_attached']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
