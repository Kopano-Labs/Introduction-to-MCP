#!/usr/bin/env python3
"""Unified guard: git sync summary + JSONL validate + proof-check (optional extras).

Delegates to existing tools so rules stay in one place:
  - scripts/git_sync_monitor.py
  - scripts/kc_log_append.py validate | proof-check

Exit codes (``all`` / single commands that run checks):
  0 — all invoked checks passed
  1 — a delegated tool returned non-zero (see stderr; maps to CI failure)
  2 — not a git repo (sync only) or invalid usage
  3 — optional doctrine check failed (e.g. --require-swarm-ack)

Examples:
  python scripts/kc_guard.py status
  python scripts/kc_guard.py status --fetch
  python scripts/kc_guard.py validate
  python scripts/kc_guard.py proof
  python scripts/kc_guard.py all
  python scripts/kc_guard.py all --strict-unpushed
  python scripts/kc_guard.py all --require-swarm-ack
  python scripts/kc_guard.py watch --interval 10
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

EXIT_USAGE = 2
EXIT_DOCTRINE = 3

DEFAULT_REQUIRED_FILES = (
    "docs/swarm-ops/SWARM_OPERATIONS.md",
    "docs/swarm-ops/logs/KC Review Log.jsonl",
    "docs/swarm-ops/logs/KC Main Brain Log.jsonl",
)


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parent


def _repo_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    return _scripts_dir().parent


def _run_py(
    root: Path,
    script: str,
    args: list[str],
    *,
    timeout: int = 300,
) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(_scripts_dir() / script), "--repo-root", str(root), *args]
    return subprocess.run(
        cmd,
        cwd=root,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def cmd_status(root: Path, *, strict_unpushed: bool, fetch: bool) -> int:
    if fetch:
        subprocess.run(
            ["git", "fetch", "--all", "--prune"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=120,
        )
    extra = ["--strict-unpushed"] if strict_unpushed else []
    cp = subprocess.run(
        [sys.executable, str(_scripts_dir() / "git_sync_monitor.py"), "--repo-root", str(root), *extra],
        cwd=root,
    )
    if cp.returncode not in (0, 1):
        return 2
    missing = check_required_files(root)
    if missing:
        print("\n=== REQUIRED FILES (kc_guard) ===", file=sys.stderr)
        for m in missing:
            print(f" - MISSING: {m}", file=sys.stderr)
        return 1
    return int(cp.returncode)


def check_required_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in DEFAULT_REQUIRED_FILES:
        if not (root / rel).is_file():
            missing.append(rel)
    return missing


def cmd_validate(root: Path) -> int:
    cp = _run_py(root, "kc_log_append.py", ["validate"])
    if cp.stdout:
        sys.stdout.write(cp.stdout)
    if cp.stderr:
        sys.stderr.write(cp.stderr)
    return cp.returncode if cp.returncode is not None else 1


def cmd_proof(root: Path) -> int:
    cp = _run_py(root, "kc_log_append.py", ["proof-check"])
    if cp.stdout:
        sys.stdout.write(cp.stdout)
    if cp.stderr:
        sys.stderr.write(cp.stderr)
    return cp.returncode if cp.returncode is not None else 1


def _mainbrain_log(root: Path) -> Path:
    return root / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"


def check_swarm_ack_evidence(root: Path) -> tuple[bool, str]:
    """Return (ok, message). Requires at least one kc_main_brain row with kind swarm_ack and evidence_urls."""
    path = _mainbrain_log(root)
    if not path.is_file():
        return False, f"main brain log missing: {path.relative_to(root)}"
    found = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        if obj.get("schema") != "kc_main_brain_log_v1":
            continue
        if obj.get("kind") != "swarm_ack":
            continue
        urls = obj.get("evidence_urls")
        if isinstance(urls, list) and any(isinstance(u, str) and u.strip() for u in urls):
            found = True
            break
        if isinstance(urls, str) and urls.strip():
            found = True
            break
    if not found:
        return False, "no swarm_ack row with non-empty evidence_urls (use --require-swarm-ack off for bootstrap repos)"
    return True, "swarm_ack + evidence_urls present"


def cmd_doctrine_swarm_ack(root: Path) -> int:
    ok, msg = check_swarm_ack_evidence(root)
    print(f"kc_guard doctrine: {msg}", flush=True)
    return 0 if ok else EXIT_DOCTRINE


def cmd_all(
    root: Path,
    *,
    strict_unpushed: bool,
    fetch: bool,
    require_swarm_ack: bool,
) -> int:
    code = cmd_status(root, strict_unpushed=strict_unpushed, fetch=fetch)
    if code != 0:
        return code
    v = cmd_validate(root)
    if v != 0:
        return v
    p = cmd_proof(root)
    if p != 0:
        return p
    if require_swarm_ack:
        return cmd_doctrine_swarm_ack(root)
    return 0


def cmd_watch(root: Path, interval: float, **kwargs: object) -> int:
    strict_unpushed = bool(kwargs.get("strict_unpushed"))
    fetch = bool(kwargs.get("fetch"))
    require_swarm_ack = bool(kwargs.get("require_swarm_ack"))
    try:
        while True:
            if os.name == "nt":
                os.system("cls")  # noqa: S605,S607
            else:
                os.system("clear")  # noqa: S605,S607
            code = cmd_all(
                root,
                strict_unpushed=strict_unpushed,
                fetch=fetch,
                require_swarm_ack=require_swarm_ack,
            )
            print(f"\n[kc_guard watch] exit code {code} (next in {interval}s, Ctrl+C to stop)", flush=True)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[kc_guard watch] stopped.", flush=True)
        return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: parent of scripts/)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_sync_flags(sp: argparse.ArgumentParser) -> None:
        sp.add_argument(
            "--fetch",
            action="store_true",
            help="Run git fetch --all --prune before sync.",
        )
        sp.add_argument(
            "--strict-unpushed",
            action="store_true",
            help="Forward to git_sync_monitor.py (fail if ahead of upstream).",
        )

    ps = sub.add_parser("status", help="Sync monitor + required doctrine files on disk")
    add_sync_flags(ps)

    sub.add_parser("validate", help="kc_log_append.py validate")
    sub.add_parser("proof", help="kc_log_append.py proof-check")
    sub.add_parser("doctrine-swarm-ack", help="Only check swarm_ack + evidence_urls (no git sync)")

    pa = sub.add_parser("all", help="status + validate + proof (+ optional doctrine)")
    add_sync_flags(pa)
    pa.add_argument(
        "--require-swarm-ack",
        action="store_true",
        help="After proof-check, require swarm_ack + evidence_urls in Main Brain log.",
    )

    pw = sub.add_parser("watch", help="Loop: all (same flags as all)")
    add_sync_flags(pw)
    pw.add_argument("--interval", type=float, default=5.0, help="Seconds between runs (default: 5)")
    pw.add_argument(
        "--require-swarm-ack",
        action="store_true",
        help="After proof-check, require swarm_ack + evidence_urls in Main Brain log.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    p = _build_parser()
    args = p.parse_args(argv)
    root = _repo_root(args.repo_root)

    fetch = bool(getattr(args, "fetch", False))
    strict = bool(getattr(args, "strict_unpushed", False))
    require_ack = bool(getattr(args, "require_swarm_ack", False))

    if args.cmd == "status":
        return cmd_status(root, strict_unpushed=strict, fetch=fetch)
    if args.cmd == "validate":
        return cmd_validate(root)
    if args.cmd == "proof":
        return cmd_proof(root)
    if args.cmd == "doctrine-swarm-ack":
        return cmd_doctrine_swarm_ack(root)
    if args.cmd == "all":
        return cmd_all(
            root,
            strict_unpushed=strict,
            fetch=fetch,
            require_swarm_ack=require_ack,
        )
    if args.cmd == "watch":
        return cmd_watch(
            root,
            args.interval,
            strict_unpushed=strict,
            fetch=fetch,
            require_swarm_ack=require_ack,
        )
    return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
