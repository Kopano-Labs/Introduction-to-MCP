#!/usr/bin/env python3
"""Reset Watch-reviewed apprenticeship records and re-run steward with --promote."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.kc_training_store import KcTrainingStore  # noqa: E402

from kc_apprenticeship_manifest import MANIFEST_PATH  # noqa: E402


def reset_watch_records(store: KcTrainingStore) -> list[str]:
    reset_ids: list[str] = []
    for rid, record in store.records.items():
        review = record.teacher_review or ""
        if record.status == "reviewed" and review.startswith("Watch"):
            record.status = "assigned"
            record.student_response = None
            record.teacher_review = None
            record.updated_at = record.created_at
            reset_ids.append(rid)
    if reset_ids:
        store.save()
    return reset_ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--store",
        type=Path,
        default=REPO_ROOT / "kopano-core" / ".kc" / "context_store.json",
    )
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--max-phase", type=int, default=10)
    parser.add_argument("--checkpoint-every", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    store = KcTrainingStore(args.store)
    reset_ids = reset_watch_records(store)
    print(f"reset {len(reset_ids)} Watch records: {', '.join(reset_ids) or '(none)'}")

    if args.dry_run or not reset_ids:
        return 0

    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "kc_apprenticeship_steward.py"),
        "--store",
        str(args.store),
        "--manifest",
        str(args.manifest),
        "--max-phase",
        str(args.max_phase),
        "--promote",
        "--no-checkpoint-log",
    ]
    if args.checkpoint_every:
        cmd.extend(["--checkpoint-every", str(args.checkpoint_every)])
    return subprocess.call(cmd, cwd=REPO_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
