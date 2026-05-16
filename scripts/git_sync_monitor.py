#!/usr/bin/env python3
"""Git remote + sync diagnostics for multi-remote / fork / ignored-tree workflows.

Exits 0 with warnings on stderr unless --strict-unpushed (then exit 1 if ahead of @{u}).

Examples:
  python scripts/git_sync_monitor.py
  python scripts/git_sync_monitor.py --repo-root .
  python scripts/git_sync_monitor.py --strict-unpushed
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(
    argv: list[str],
    *,
    cwd: Path,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
        timeout=120,
    )


def _lines(s: str) -> list[str]:
    return [ln for ln in s.splitlines() if ln.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root (default: parent of scripts/)",
    )
    p.add_argument(
        "--strict-unpushed",
        action="store_true",
        help="Exit 1 if this branch is ahead of its upstream (unpushed commits).",
    )
    args = p.parse_args()
    root: Path = args.repo_root.resolve()
    exit_code = 0
    warn: list[str] = []

    if not (root / ".git").exists() and not (root / ".git").is_file():
        print(f"error: not a git repository: {root}", file=sys.stderr)
        return 2

    r = _run(["git", "remote", "-v"], cwd=root)
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        return r.returncode or 1
    remotes = _lines(r.stdout)
    if not remotes:
        print("error: no git remotes configured", file=sys.stderr)
        return 1
    print("=== git remote -v ===", flush=True)
    print(r.stdout.rstrip() or "(empty)", flush=True)

    br = _run(["git", "branch", "--show-current"], cwd=root)
    branch = (br.stdout or "").strip() or "(detached)"
    print(f"\n=== current branch ===\n{branch}", flush=True)

    upstream_ref = f"{branch}@{{upstream}}"
    u = _run(["git", "rev-parse", "--abbrev-ref", upstream_ref], cwd=root)
    if u.returncode == 0:
        up = u.stdout.strip()
        print(f"\n=== upstream ===\n{up}", flush=True)
        cnt = _run(
            ["git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
            cwd=root,
        )
        if cnt.returncode == 0 and cnt.stdout.strip():
            left, right = cnt.stdout.strip().split("\t", 1)
            ahead, behind = int(left), int(right)
            print(f"\n=== vs upstream (ahead / behind) ===\n{ahead} / {behind}", flush=True)
            if ahead:
                warn.append(
                    f"This branch is {ahead} commit(s) AHEAD of {up} - not visible on that remote until you push."
                )
                if args.strict_unpushed:
                    exit_code = 1
            if behind:
                warn.append(
                    f"This branch is {behind} commit(s) BEHIND {up} - pull/rebase before push if you expect a fast-forward."
                )
    else:
        warn.append("No upstream configured for this branch (git push -u origin <branch> once).")

    head = _run(["git", "rev-parse", "HEAD"], cwd=root)
    if head.returncode == 0:
        print(f"\n=== HEAD ===\n{head.stdout.strip()}", flush=True)

    # Schematics: .gitignore vs still-tracked (common footgun)
    ig_path = root / ".gitignore"
    if ig_path.is_file():
        ig = ig_path.read_text(encoding="utf-8", errors="replace")
        if "Schematics/" in ig or "Schematics\n" in ig:
            ls = _run(["git", "ls-files", "Schematics"], cwd=root)
            n = len(_lines(ls.stdout)) if ls.returncode == 0 else 0
            print("\n=== Schematics / .gitignore ===", flush=True)
            print(f".gitignore mentions Schematics; tracked files under Schematics/: {n}", flush=True)
            if n:
                warn.append(
                    "Schematics/ is ignored for *new* files, but many paths remain *tracked* from before "
                    "the ignore rule - `git add Schematics/...` still stages them. Prefer docs/swarm-ops/ for "
                    "committed doctrine."
                )

        st = _run(["git", "status", "--porcelain", "Schematics"], cwd=root)
        if st.returncode == 0 and st.stdout.strip():
            k = len(_lines(st.stdout))
            warn.append(f"Working tree: {k} Schematics-related status line(s) (noise risk for focused commits).")

    # Heuristic: public fork often not the same URL as origin
    origin_url = ""
    for ln in remotes:
        if ln.startswith("origin\t") and "(fetch)" in ln:
            origin_url = ln.split()[1]
            break
    if "Kopano-Labs" in origin_url and "github.com" in origin_url:
        warn.append(
            "origin points at Kopano-Labs. If your *personal public fork* is RobynAwesome/Introduction-to-MCP, "
            "add it explicitly:  git remote add fork https://github.com/RobynAwesome/Introduction-to-MCP.git  "
            "then push there for receipts visible on your GitHub profile."
        )

    if warn:
        print("\n=== WARNINGS ===", file=sys.stderr)
        for w in warn:
            print(f" - {w}", file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
