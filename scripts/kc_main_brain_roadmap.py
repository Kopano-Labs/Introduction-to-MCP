#!/usr/bin/env python3
"""Main Brain roadmap — production entry gate (Servitude Triad / Black Mass line)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ROADMAP_PATH = REPO_ROOT / "docs" / "swarm-ops" / "MAIN_BRAIN_ROADMAP.json"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
COMPARE = (
    "https://github.com/Kopano-Labs/Introduction-to-MCP/"
    "compare/master...codex/kc-sovereign-gui-full-dev?expand=1"
)
ACTIONS = "https://github.com/Kopano-Labs/Introduction-to-MCP/actions"
PY = sys.executable


def load_roadmap(path: Path | None = None) -> dict:
    p = path or ROADMAP_PATH
    return json.loads(p.read_text(encoding="utf-8"))


def _main_brain_kinds(path: Path | None = None) -> set[str]:
    log = path or MAIN_BRAIN_LOG
    kinds: set[str] = set()
    if not log.is_file():
        return kinds
    for line in log.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        k = row.get("kind")
        if k:
            kinds.add(str(k))
    return kinds


def check_entry_gate(roadmap: dict | None = None) -> tuple[bool, str]:
    roadmap = roadmap or load_roadmap()
    gate = roadmap.get("entry_gate", {})
    required_kinds = set(gate.get("required_main_brain_kinds", []))
    kinds = _main_brain_kinds()
    missing = sorted(required_kinds - kinds)
    if missing:
        return False, f"roadmap_gate missing main-brain kinds: {missing}"

    min_prod = int(gate.get("required_review_production_min", 10))
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from kc_verified_production import check_minimum

    ok, msg = check_minimum(min_prod)
    if not ok:
        return False, f"roadmap_gate {msg}"
    return True, f"roadmap_gate OK kinds={sorted(required_kinds)} {msg}"


def append_receipt(kind: str, summary: str) -> None:
    subprocess.run(
        [
            PY,
            str(REPO_ROOT / "scripts" / "kc_log_append.py"),
            "mainbrain",
            "--kind",
            kind,
            "--summary",
            summary,
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


def cmd_seed(phase: str) -> int:
    kind = "roadmap_seed_before" if phase == "before" else "roadmap_seed_after"
    summary = (
        f"Roadmap seed {phase}: Cassy lead student, Servitude Triad unified, "
        f"SWARM_AGENTS.json + cassy_wit_25 band."
    )
    append_receipt(kind, summary)
    print(f"appended {kind}")
    return 0


def cmd_receipt(milestone_id: str) -> int:
    roadmap = load_roadmap()
    milestone = next((m for m in roadmap.get("milestones", []) if m["id"] == milestone_id), None)
    if not milestone:
        print(f"unknown milestone: {milestone_id}", file=sys.stderr)
        return 1
    kind = milestone["main_brain_kind"]
    append_receipt(kind, f"Roadmap milestone {milestone_id}: {milestone['label']}")
    print(f"appended {kind}")
    return 0


def cmd_gate() -> int:
    ok, msg = check_entry_gate()
    print(msg)
    if ok:
        append_receipt("roadmap_gate_pass", msg)
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("seed", help="Append seed before/after main-brain row")
    ps.add_argument("--phase", choices=("before", "after"), required=True)

    pr = sub.add_parser("receipt", help="Append milestone main-brain row")
    pr.add_argument("--milestone", required=True, help="e.g. blackmass_v2_0")

    sub.add_parser("gate", help="Check entry gate; append roadmap_gate_pass on success")
    sub.add_parser("status", help="Print roadmap + kinds present")

    args = parser.parse_args()
    if args.cmd == "seed":
        return cmd_seed(args.phase)
    if args.cmd == "receipt":
        return cmd_receipt(args.milestone)
    if args.cmd == "gate":
        return cmd_gate()
    if args.cmd == "status":
        roadmap = load_roadmap()
        kinds = _main_brain_kinds()
        print(json.dumps({"roadmap": roadmap["milestones"], "main_brain_kinds": sorted(kinds)}, indent=2))
        ok, msg = check_entry_gate(roadmap)
        print(msg)
        return 0 if ok else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
