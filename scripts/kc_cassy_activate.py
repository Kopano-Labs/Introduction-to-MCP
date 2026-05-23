#!/usr/bin/env python3
"""Activate Cassy as lead student — Women in Tech band + swarm profile."""

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

WIT_MANIFEST = REPO_ROOT / "docs" / "swarm-ops" / "agents" / "cassy_wit_25.json"
REGISTRY = REPO_ROOT / "docs" / "swarm-ops" / "agents" / "SWARM_AGENTS.json"
PROFILE_PATH = REPO_ROOT / "kopano-core" / ".kc" / "swarm_profile.json"
DEFAULT_STORE = REPO_ROOT / "kopano-core" / ".kc" / "context_store.json"
PY = sys.executable


def write_profile() -> Path:
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    payload = {
        "lead_student": registry.get("lead_student", "cassy"),
        "teacher": registry.get("teacher", "cassey"),
        "brain": registry.get("brain", "kc"),
        "triad": registry.get("triad", []),
        "servitude": registry.get("servitude"),
        "wit_manifest": str(WIT_MANIFEST.relative_to(REPO_ROOT)).replace("\\", "/"),
        "hold_back_student": False,
    }
    PROFILE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return PROFILE_PATH


def seed_wit_tasks(store_path: Path) -> int:
    wit = json.loads(WIT_MANIFEST.read_text(encoding="utf-8"))
    store = KcTrainingStore(store_path)
    existing = {r.title for r in store.records.values()}
    items = [
        {"title": t["title"], "teacher_context": t["teacher_context"]}
        for t in wit["tasks"]
        if t["title"] not in existing
    ]
    if not items:
        return 0
    return store.bulk_create_assigned(items)


def append_activation_receipt(seeded: int) -> None:
    subprocess.run(
        [
            PY,
            str(REPO_ROOT / "scripts" / "kc_log_append.py"),
            "mainbrain",
            "--kind",
            "cassy_activated",
            "--summary",
            f"Cassy lead student activated: WIT band seeded={seeded} profile=swarm_profile.json "
            "Servitude Triad; not corporate-role limited.",
            "--exit-code",
            "0",
            "--evidence-url",
            "https://github.com/Kopano-Labs/Introduction-to-MCP/"
            "compare/master...codex/kc-sovereign-gui-full-dev?expand=1",
            "--evidence-url",
            "https://github.com/Kopano-Labs/Introduction-to-MCP/actions",
        ],
        cwd=REPO_ROOT,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE)
    parser.add_argument("--seed-wit", action="store_true", help="Append 25 Women in Tech tasks to store")
    parser.add_argument("--no-log", action="store_true")
    args = parser.parse_args()

    profile = write_profile()
    print(f"profile: {profile}")

    seeded = 0
    if args.seed_wit:
        if not args.store.exists():
            print("store missing; run kc_apprenticeship_activate.py first", file=sys.stderr)
            return 1
        seeded = seed_wit_tasks(args.store)
        print(f"wit_tasks_seeded={seeded} total={len(KcTrainingStore(args.store).records)}")

    if not args.no_log:
        append_activation_receipt(seeded)

    subprocess.run([PY, str(REPO_ROOT / "scripts" / "kc_swarm_agents_bootstrap.py")], cwd=REPO_ROOT, check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
