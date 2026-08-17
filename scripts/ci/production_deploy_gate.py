#!/usr/bin/env python3
"""Classify changed repository paths before authorizing an Azure production deploy.

WYC-01 keeps invocation provenance separate from defect provenance: a changed file may
surface a deployment defect without itself being production-affecting. This module is
the canonical path contract used by the deployment workflow.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import PurePosixPath
from typing import Iterable


ROOT_RUNTIME_FILES = {
    "Dockerfile",
    "kpgs_config.json",
    "main.py",
    "package-lock.json",
    "package.json",
    "pyproject.toml",
    "uv.lock",
}

PRODUCTION_PREFIXES = (
    "infra/",
    "kopano-core/",
    "src/",
)

PRODUCTION_SUFFIXES = {
    ".bicep",
    ".cs",
    ".csproj",
    ".js",
    ".json",
    ".jsx",
    ".lock",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}


def normalize_path(path: str) -> str:
    """Normalize a Git diff path into repository-relative POSIX form."""
    return path.strip().replace("\\", "/").lstrip("./")


def is_production_affecting(path: str) -> bool:
    """Return True only when *path* belongs to the declared production contract."""
    normalized = normalize_path(path)
    if not normalized:
        return False

    if normalized in ROOT_RUNTIME_FILES:
        return True

    if not normalized.startswith(PRODUCTION_PREFIXES):
        return False

    return PurePosixPath(normalized).suffix.lower() in PRODUCTION_SUFFIXES


def production_affecting_paths(paths: Iterable[str]) -> list[str]:
    """Return normalized production-affecting paths, preserving input order."""
    matched: list[str] = []
    for path in paths:
        normalized = normalize_path(path)
        if normalized and is_production_affecting(normalized):
            matched.append(normalized)
    return matched


def authorize_deploy(paths: Iterable[str], *, explicit_release: bool = False) -> tuple[bool, str, list[str]]:
    """Evaluate deploy authorization and provide machine/human-readable provenance."""
    if explicit_release:
        return True, "explicit workflow_dispatch release intent", []

    matched = production_affecting_paths(paths)
    if matched:
        return True, "production-affecting diff", matched

    return False, "diff is outside the declared production path contract", []


def write_github_output(path: str, *, authorized: bool, reason: str, matched: list[str]) -> None:
    """Write stable one-line outputs for GitHub Actions job gating."""
    with open(path, "a", encoding="utf-8") as output:
        output.write(f"authorized={'true' if authorized else 'false'}\n")
        output.write(f"reason={reason}\n")
        output.write(f"production_paths={','.join(matched)}\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Repository-relative changed paths. Defaults to newline-delimited stdin.")
    parser.add_argument("--explicit-release", action="store_true", help="Authorize explicit operator release intent.")
    parser.add_argument("--github-output", help="Append authorized/reason/production_paths outputs to this file.")
    args = parser.parse_args(argv)

    paths = args.paths if args.paths else [line for line in sys.stdin.read().splitlines() if line.strip()]
    authorized, reason, matched = authorize_deploy(paths, explicit_release=args.explicit_release)

    if args.github_output:
        write_github_output(args.github_output, authorized=authorized, reason=reason, matched=matched)
    else:
        print(f"authorized={'true' if authorized else 'false'}")
        print(f"reason={reason}")
        print(f"production_paths={','.join(matched)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
