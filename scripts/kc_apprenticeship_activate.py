#!/usr/bin/env python3
"""Activate KC Student Apprenticeship: write 150-task manifest and seed local KC store."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from kopano.kc_training_store import KcTrainingStore  # noqa: E402

from kc_apprenticeship_manifest import MANIFEST_PATH, write_manifest  # noqa: E402


def load_manifest(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    tasks = payload.get("tasks", [])
    if len(tasks) != 150:
        raise SystemExit(f"manifest must contain 150 tasks, found {len(tasks)}")
    return tasks


def seed_store(store_path: Path, tasks: list[dict[str, str]], replace: bool) -> int:
    if replace and store_path.exists():
        store_path.unlink()
    store = KcTrainingStore(store_path)
    if store.records and not replace:
        print(f"store already has {len(store.records)} records; use --replace to reseed")
        return 0
    items = [{"title": t["title"], "teacher_context": t["teacher_context"]} for t in tasks]
    return store.bulk_create_assigned(items)


def append_activation_receipt(manifest_path: Path, store_path: Path, seeded: int) -> None:
    log_script = REPO_ROOT / "scripts" / "kc_log_append.py"
    if not log_script.exists():
        return
    import subprocess

    note = (
        f"KC Student Apprenticeship 150 activated. manifest={manifest_path.name} "
        f"seeded={seeded} store={store_path}"
    )
    subprocess.run(
        [
            sys.executable,
            str(log_script),
            "mainbrain",
            "--note",
            note,
            "--scope",
            "apprenticeship-150",
        ],
        check=False,
        cwd=REPO_ROOT,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Activate KC apprenticeship 150 tasks")
    parser.add_argument(
        "--store",
        type=Path,
        default=REPO_ROOT / "kopano-core" / ".kc" / "context_store.json",
        help="KC context store JSON path",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_PATH,
        help="Manifest JSON path (written if missing unless --manifest-only)",
    )
    parser.add_argument("--replace", action="store_true", help="Replace existing store")
    parser.add_argument("--manifest-only", action="store_true", help="Only write manifest JSON")
    parser.add_argument("--no-log", action="store_true", help="Skip Main Brain log append")
    args = parser.parse_args()

    manifest_path = write_manifest(args.manifest)
    print(f"manifest: {manifest_path} ({manifest_path.stat().st_size} bytes)")

    if args.manifest_only:
        return 0

    tasks = load_manifest(manifest_path)
    seeded = seed_store(args.store, tasks, args.replace)
    print(f"store: {args.store} seeded={seeded} total_after={len(KcTrainingStore(args.store).records)}")

    if not args.no_log and seeded:
        append_activation_receipt(manifest_path, args.store, seeded)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
