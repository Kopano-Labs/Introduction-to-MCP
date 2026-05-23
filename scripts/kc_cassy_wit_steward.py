#!/usr/bin/env python3
"""Steward Cassy Women-in-Tech band (phase 11) — student teacher apprenticeship."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from kopano.kc_training_store import KcTrainingStore  # noqa: E402

from kc_apprenticeship_steward import _git_sha  # noqa: E402
from kc_wit_handlers import wit_handlers  # noqa: E402

WIT_MANIFEST = REPO_ROOT / "docs" / "swarm-ops" / "agents" / "cassy_wit_25.json"
DEFAULT_STORE = REPO_ROOT / "kopano-core" / ".kc" / "context_store.json"
COMPARE = (
    "https://github.com/Kopano-Labs/Introduction-to-MCP/"
    "compare/master...codex/kc-sovereign-gui-full-dev?expand=1"
)
ACTIONS = "https://github.com/Kopano-Labs/Introduction-to-MCP/actions"
PY = sys.executable


def _rid_by_title(store: KcTrainingStore, tasks: list[dict]) -> dict[str, str]:
    title_to_rid = {r.title: r.id for r in store.records.values()}
    return {t["code"]: title_to_rid[t["title"]] for t in tasks if t["title"] in title_to_rid}


def steward_wit(store: KcTrainingStore, tasks: list[dict], promote: bool) -> dict[str, int]:
    hmap = wit_handlers(REPO_ROOT, _git_sha(), store.path)
    code_to_rid = _rid_by_title(store, tasks)
    stats = {"skipped": 0, "submitted": 0, "reviewed": 0, "promoted": 0, "no_handler": 0, "missing": 0}

    for task in tasks:
        code = task["code"]
        rid = code_to_rid.get(code)
        if not rid:
            stats["missing"] += 1
            continue
        record = store.records[rid]
        if record.status in {"reviewed", "promoted"}:
            stats["skipped"] += 1
            continue
        handler = hmap.get(code)
        if not handler:
            stats["no_handler"] += 1
            continue
        student, teacher = handler()
        store.submit(rid, student)
        stats["submitted"] += 1
        store.review(rid, teacher)
        stats["reviewed"] += 1
        if promote and teacher.startswith("Save"):
            store.promote(rid)
            stats["promoted"] += 1
    return stats


def append_receipt(stats: dict[str, int]) -> None:
    summary = (
        f"Cassy WIT phase 11 steward: submitted={stats['submitted']} reviewed={stats['reviewed']} "
        f"promoted={stats.get('promoted', 0)} missing={stats.get('missing', 0)} "
        "— student teacher apprenticeship, not corporate-role ceiling."
    )
    subprocess.run(
        [
            PY,
            str(REPO_ROOT / "scripts/kc_log_append.py"),
            "review",
            "--role",
            "student",
            "--phase",
            "production",
            "--summary",
            summary,
            "--commands",
            shlex_join([PY, "scripts/kc_cassy_wit_steward.py", "--promote"]),
            "--exit-code",
            "0",
            "--evidence-url",
            COMPARE,
            "--evidence-url",
            ACTIONS,
        ],
        cwd=REPO_ROOT,
        check=False,
    )


def shlex_join(parts: list[str]) -> str:
    import shlex

    return shlex.join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE)
    parser.add_argument("--manifest", type=Path, default=WIT_MANIFEST)
    parser.add_argument("--promote", action="store_true")
    parser.add_argument("--no-log", action="store_true")
    args = parser.parse_args()

    if not args.manifest.is_file():
        print(f"missing manifest: {args.manifest}", file=sys.stderr)
        return 1
    if not args.store.is_file():
        print("store empty; run kc_cassy_activate.py --seed-wit first", file=sys.stderr)
        return 1

    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    tasks = payload["tasks"]
    store = KcTrainingStore(args.store)
    stats = steward_wit(store, tasks, args.promote)
    print(json.dumps({"stats": stats, "wit_tasks": len(tasks)}, indent=2))

    if not args.no_log and stats["reviewed"]:
        append_receipt(stats)
        subprocess.run([PY, "scripts/kc_sync_vault_logs.py"], cwd=REPO_ROOT, check=False)
    return 0 if stats["missing"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
