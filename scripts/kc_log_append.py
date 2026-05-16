#!/usr/bin/env python3
"""Append one JSON line to KC Review Log or KC Main Brain Log (docs/swarm-ops)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REVIEW_REL = Path("docs/swarm-ops/logs/KC Review Log.jsonl")
MAIN_REL = Path("docs/swarm-ops/logs/KC Main Brain Log.jsonl")


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _utc_now_iso() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha(root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        sha = out.stdout.strip()
        return sha or None
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def _append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def cmd_review(args: argparse.Namespace, root: Path) -> int:
    record = {
        "schema": "kc_review_log_v1",
        "ts": _utc_now_iso(),
        "role": args.role,
        "phase": args.phase,
        "agent_id": args.agent_id,
        "summary": args.summary,
        "commands": args.commands or None,
        "exit_code": args.exit_code,
        "git_sha": args.git_sha or _git_sha(root),
        "branch": args.branch,
        "evidence_urls": args.evidence_url or None,
        "ref_review_id": args.ref_review_id,
        "teacher_verdict": args.teacher_verdict,
    }
    _append_jsonl(root / REVIEW_REL, record)
    return 0


def cmd_mainbrain(args: argparse.Namespace, root: Path) -> int:
    urls = args.evidence_url or None
    record = {
        "schema": "kc_main_brain_log_v1",
        "ts": _utc_now_iso(),
        "kind": args.kind,
        "summary": args.summary,
        "commands": args.commands or None,
        "exit_code": args.exit_code,
        "git_sha": args.git_sha or _git_sha(root),
        "evidence_urls": urls,
        "payload_ref": args.payload_ref,
    }
    _append_jsonl(root / MAIN_REL, record)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: parent of scripts/)",
    )
    sub = p.add_subparsers(dest="target", required=True)

    pr = sub.add_parser("review", help="Append KC Review Log (student / teacher)")
    pr.set_defaults(func=cmd_review)
    pr.add_argument("--role", required=True, choices=("student", "teacher"))
    pr.add_argument("--phase", required=True, help="e.g. propose, audit, review_decision")
    pr.add_argument("--summary", required=True)
    pr.add_argument("--agent-id", default=None)
    pr.add_argument(
        "--commands",
        nargs="*",
        default=None,
        help="Command lines executed (space-separated tokens become one argv each unless quoted by shell)",
    )
    pr.add_argument("--exit-code", type=int, default=None)
    pr.add_argument("--git-sha", default=None)
    pr.add_argument("--branch", default=None)
    pr.add_argument("--evidence-url", action="append", default=None, metavar="URL")
    pr.add_argument("--ref-review-id", default=None)
    pr.add_argument(
        "--teacher-verdict",
        default=None,
        choices=("approved", "rejected"),
    )

    pm = sub.add_parser("mainbrain", help="Append KC Main Brain Log (orchestrator / chief)")
    pm.set_defaults(func=cmd_mainbrain)
    pm.add_argument("--kind", required=True, help="e.g. swarm_ack, swarm_event, mirror_warden, manual")
    pm.add_argument("--summary", required=True)
    pm.add_argument("--commands", nargs="*", default=None)
    pm.add_argument("--exit-code", type=int, default=None)
    pm.add_argument("--git-sha", default=None)
    pm.add_argument("--evidence-url", action="append", default=None, metavar="URL")
    pm.add_argument("--payload-ref", default=None)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    root = args.repo_root or _repo_root()
    return int(args.func(args, root))


if __name__ == "__main__":
    raise SystemExit(main())
