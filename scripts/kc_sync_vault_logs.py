#!/usr/bin/env python3
"""Mirror machine JSONL logs from docs/swarm-ops/logs to Schematics vault (local only)."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL = REPO_ROOT / "docs" / "swarm-ops" / "logs"
VAULT_LOGS = REPO_ROOT / "Schematics" / "04-Updates" / "logs"

FILES = (
    "KC Main Brain Log.jsonl",
    "KC Review Log.jsonl",
)


def sync_logs(vault_dir: Path, *, dry_run: bool = False) -> list[str]:
    vault_dir.mkdir(parents=True, exist_ok=True)
    actions: list[str] = []
    for name in FILES:
        src = CANONICAL / name
        dst = vault_dir / name
        if not src.is_file():
            actions.append(f"SKIP missing canonical {src}")
            continue
        if dry_run:
            actions.append(f"WOULD copy {src} -> {dst}")
            continue
        shutil.copy2(src, dst)
        actions.append(f"copied {name} ({src.stat().st_size} bytes)")
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vault-logs",
        type=Path,
        default=VAULT_LOGS,
        help="Schematics mirror directory (default: Schematics/04-Updates/logs)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    for line in sync_logs(args.vault_logs, dry_run=args.dry_run):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
