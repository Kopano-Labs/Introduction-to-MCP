#!/usr/bin/env python3
"""Print what is real (gates, logs) vs machine-drill theater (bulk Save counts)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from kc_apprenticeship_manifest import MANIFEST_PATH, PUBLIC_GRADUATION_BAR  # noqa: E402
from kc_verified_production import check_minimum, count_verified  # noqa: E402
from kopano.kc_training_store import KcTrainingStore  # noqa: E402

DEFAULT_STORE = REPO_ROOT / "kopano-core" / ".kc" / "context_store.json"


def _run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=120)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()[:500]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    mode = manifest.get("mode", "unknown")
    task_count = manifest.get("task_count", len(manifest.get("tasks", [])))

    print("=== KC apprenticeship realism report ===\n")
    print(f"manifest: {args.manifest.name}")
    print(f"mode: {mode}  (NOT a graduation diploma)")
    print(f"drill_tasks: {task_count}")
    print(f"public_graduation_bar: {PUBLIC_GRADUATION_BAR} verified production tasks (protocol)")

    verified_n, _ = count_verified()
    bar_ok, bar_msg = check_minimum(PUBLIC_GRADUATION_BAR)
    print(f"review_log: {bar_msg} ({'BAR MET' if bar_ok else 'BAR NOT MET'})\n")

    if args.store.exists():
        store = KcTrainingStore(args.store)
        counts = {}
        save = watch = 0
        for r in store.records.values():
            counts[r.status] = counts.get(r.status, 0) + 1
            tr = (r.teacher_review or "").strip().lower()
            if tr.startswith("save"):
                save += 1
            elif tr.startswith("watch"):
                watch += 1
        print("local store (gitignored):")
        print(f"  records: {len(store.records)}")
        print(f"  status_counts: {counts}")
        print(f"  teacher_review Save/Watch: {save}/{watch}")
        print("  -> promoted count is drill completion, not Chief Architect graduation.\n")
    else:
        print("local store: missing (no drill counts on this machine)\n")

    print("real gates (run now):")
    for label, cmd in [
        ("validate", [sys.executable, "scripts/kc_log_append.py", "validate"]),
        ("proof-check", [sys.executable, "scripts/kc_log_append.py", "proof-check"]),
        (
            "kc_guard all + verified production",
            [
                sys.executable,
                "scripts/kc_guard.py",
                "all",
                "--require-verified-production",
                str(PUBLIC_GRADUATION_BAR),
            ],
        ),
    ]:
        code, _ = _run(cmd)
        print(f"  {label}: exit {code} ({'OK' if code == 0 else 'FAIL'})")

    print("\nread: docs/swarm-ops/apprenticeship/REALISM.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
