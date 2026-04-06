#!/usr/bin/env python
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GUI_DIR = ROOT / "orch" / "gui"


@dataclass
class CheckResult:
    name: str
    command: list[str]
    returncode: int
    skipped: bool = False


def run_check(name: str, command: list[str], cwd: Path) -> CheckResult:
    completed = subprocess.run(command, cwd=cwd)
    return CheckResult(name=name, command=command, returncode=completed.returncode)


def skip_check(name: str, command: list[str]) -> CheckResult:
    return CheckResult(name=name, command=command, returncode=0, skipped=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run demo-day readiness checks for the repo.")
    parser.add_argument("--quick", action="store_true", help="Skip slower optional checks and focus on core readiness.")
    args = parser.parse_args()

    checks: list[CheckResult] = []

    checks.append(run_check("Python tests", [sys.executable, "-m", "pytest", "-q"], ROOT))
    checks.append(run_check("Compile sanity", [sys.executable, "-m", "compileall", "orch/orch"], ROOT))

    npm = shutil.which("npm")
    if npm:
        checks.append(run_check("GUI lint", [npm, "run", "lint"], GUI_DIR))
        checks.append(run_check("GUI build", [npm, "run", "build"], GUI_DIR))
        if not args.quick:
            checks.append(run_check("GUI smoke", [npm, "run", "test:ui"], GUI_DIR))
    else:
        checks.append(skip_check("GUI lint", ["npm", "run", "lint"]))
        checks.append(skip_check("GUI build", ["npm", "run", "build"]))
        if not args.quick:
            checks.append(skip_check("GUI smoke", ["npm", "run", "test:ui"]))

    failures = [check for check in checks if not check.skipped and check.returncode != 0]

    print("\nDemo Day Readiness Summary")
    print("==========================")
    for check in checks:
        if check.skipped:
            status = "SKIPPED"
        elif check.returncode == 0:
            status = "PASS"
        else:
            status = "FAIL"
        print(f"{status:7} {check.name}: {' '.join(check.command)}")

    print("\nCanonical demo commands")
    print("-----------------------")
    print("1. orch agents list")
    print("2. orch serve api --host 127.0.0.1 --port 8000")
    print('3. orch serve launch --topic "The future of AI in South African fintech" --agents "gemini-pro" --moderator "grok-mod" --max-rounds 3')
    print("4. Open http://127.0.0.1:8000")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
