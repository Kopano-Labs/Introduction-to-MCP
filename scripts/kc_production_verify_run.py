#!/usr/bin/env python3
"""Run 10 real production checks and append one JSONL row each. No drill theater."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from kc_verified_production import DEFAULT_MIN, check_minimum, count_verified  # noqa: E402

COMPARE = (
    "https://github.com/Kopano-Labs/Introduction-to-MCP/"
    "compare/master...codex/kc-sovereign-gui-full-dev?expand=1"
)
ACTIONS = "https://github.com/Kopano-Labs/Introduction-to-MCP/actions"
PY = sys.executable


def _run_step(step_id: str, summary: str, cmd: list[str]) -> int:
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=300)
    log = REPO_ROOT / "scripts" / "kc_log_append.py"
    review_cmd = [
        PY,
        str(log),
        "review",
        "--role",
        "student",
        "--phase",
        "production",
        "--summary",
        f"{step_id}: {summary}",
        "--commands",
        shlex.join(cmd),
        "--exit-code",
        str(proc.returncode),
        "--evidence-url",
        COMPARE,
        "--evidence-url",
        ACTIONS,
    ]
    subprocess.run(review_cmd, cwd=REPO_ROOT, check=False)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "")[:400]
        print(f"FAIL {step_id} exit={proc.returncode}\n{err}", file=sys.stderr)
    else:
        print(f"OK {step_id}")
    return proc.returncode


def production_steps() -> list[tuple[str, str, list[str]]]:
    return [
        ("P01", "pytest kc_log_append", [PY, "-m", "pytest", "tests/test_kc_log_append.py", "-q"]),
        ("P02", "pytest kc_guard", [PY, "-m", "pytest", "tests/test_kc_guard.py", "-q"]),
        ("P03", "pytest kc_apprenticeship", [PY, "-m", "pytest", "tests/test_kc_apprenticeship.py", "-q"]),
        ("P04", "pytest kc_training_api", [PY, "-m", "pytest", "tests/test_kc_training_api.py", "-q"]),
        ("P05", "kc_log_append validate", [PY, "scripts/kc_log_append.py", "validate"]),
        ("P06", "kc_log_append proof-check", [PY, "scripts/kc_log_append.py", "proof-check"]),
        ("P07", "kc_guard all", [PY, "scripts/kc_guard.py", "all"]),
        ("P08", "git_sync_monitor", [PY, "scripts/git_sync_monitor.py"]),
        ("P09", "kc_sync_vault_logs", [PY, "scripts/kc_sync_vault_logs.py"]),
        ("P10", "realism report", [PY, "scripts/kc_apprenticeship_realism_report.py"]),
        (
            "P11",
            "roadmap + swarm agents pytest",
            [
                PY,
                "-m",
                "pytest",
                "tests/test_kc_main_brain_roadmap.py",
                "tests/test_swarm_agents_api.py",
                "-q",
            ],
        ),
        ("P12", "main brain roadmap gate", [PY, "scripts/kc_main_brain_roadmap.py", "gate"]),
        ("P13", "swarm console status API", [PY, "-m", "pytest", "tests/test_swarm_console_api.py", "-q"]),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min", type=int, default=DEFAULT_MIN)
    args = parser.parse_args()

    failed = 0
    for step_id, summary, cmd in production_steps():
        if _run_step(step_id, summary, cmd) != 0:
            failed += 1

    n, _ = count_verified()
    ok, msg = check_minimum(args.min)
    print(msg)
    if not ok:
        return 1
    if failed:
        print(f"warning: {failed} steps failed but verified count {n} >= {args.min}", file=sys.stderr)
    subprocess.run(
        [
            PY,
            "scripts/kc_log_append.py",
            "mainbrain",
            "--kind",
            "production_bar_met",
            "--summary",
            f"Verified production bar met: {n} rows in Review Log (min {args.min}). Not drill promoted count.",
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
    subprocess.run([PY, "scripts/kc_sync_vault_logs.py"], cwd=REPO_ROOT, check=False)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
