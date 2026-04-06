from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GUI_DIST = ROOT / "orch" / "gui" / "dist" / "index.html"
ENV_FILE = ROOT / ".env"
DB_FILE = ROOT / "db" / "datalake.db"
AGENTS_FILE = Path.home() / ".orch" / "agents.json"


def check_file(path: Path, label: str) -> tuple[bool, str]:
    if path.exists():
        return True, f"PASS {label}: {path}"
    return False, f"WARN {label}: missing {path}"


def check_imports() -> list[tuple[bool, str]]:
    checks: list[tuple[bool, str]] = []
    try:
        from orch.orch.api import app as _api_app  # noqa: F401

        checks.append((True, "PASS API import: orch.orch.api"))
    except Exception as exc:
        checks.append((False, f"WARN API import failed: {exc}"))

    try:
        from orch.orch.cli import app as _cli_app  # noqa: F401

        checks.append((True, "PASS CLI import: orch.orch.cli"))
    except Exception as exc:
        checks.append((False, f"WARN CLI import failed: {exc}"))

    return checks


def check_agents() -> tuple[bool, str]:
    if not AGENTS_FILE.exists():
        return False, f"WARN agent registry: missing {AGENTS_FILE}"

    try:
        data = json.loads(AGENTS_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"WARN agent registry unreadable: {exc}"

    if not isinstance(data, dict) or not data:
        return False, f"WARN agent registry empty: {AGENTS_FILE}"

    return True, f"PASS agent registry: {len(data)} configured agent(s)"


def run_checks() -> list[tuple[bool, str]]:
    checks = [
        (sys.version_info >= (3, 11), f"{'PASS' if sys.version_info >= (3, 11) else 'WARN'} Python version: {sys.version.split()[0]}"),
        check_file(ENV_FILE, ".env"),
        check_file(DB_FILE, "database file"),
        check_file(GUI_DIST, "GUI build"),
        check_agents(),
    ]
    checks.extend(check_imports())
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Demo-day smoke checks for orch.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when any warning is present.")
    parser.add_argument("--json", action="store_true", help="Emit checks as JSON.")
    args = parser.parse_args()

    checks = run_checks()
    failed = [message for ok, message in checks if not ok]

    if args.json:
        print(json.dumps([{"ok": ok, "message": message} for ok, message in checks], indent=2))
    else:
        print("Demo Day Smoke Check")
        print("====================")
        for _, message in checks:
            print(message)

    if failed and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
