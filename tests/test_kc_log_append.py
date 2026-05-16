"""Tests for scripts/kc_log_append.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "kc_log_append.py"


def _run_append(tmp_root: Path, *cli_args: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT), "--repo-root", str(tmp_root), *cli_args]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def test_append_review_and_mainbrain(tmp_path: Path) -> None:
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    review = tmp_path / "docs/swarm-ops/logs/KC Review Log.jsonl"
    mainb = tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl"
    review.write_text("", encoding="utf-8")
    mainb.write_text("", encoding="utf-8")

    r1 = _run_append(
        tmp_path,
        "review",
        "--role",
        "student",
        "--phase",
        "audit",
        "--summary",
        "smoke ok",
        "--commands",
        "python",
        "scripts/x.py",
        "--exit-code",
        "0",
        "--git-sha",
        "deadbeef",
    )
    assert r1.returncode == 0, r1.stderr

    r2 = _run_append(
        tmp_path,
        "mainbrain",
        "--kind",
        "swarm_ack",
        "--summary",
        "kimi ack",
        "--payload-ref",
        "vault/payload.md",
    )
    assert r2.returncode == 0, r2.stderr

    lines_r = review.read_text(encoding="utf-8").strip().splitlines()
    lines_m = mainb.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines_r) == 1
    assert len(lines_m) == 1

    row_r = json.loads(lines_r[0])
    assert row_r["schema"] == "kc_review_log_v1"
    assert row_r["role"] == "student"
    assert row_r["phase"] == "audit"
    assert row_r["commands"] == ["python", "scripts/x.py"]
    assert row_r["exit_code"] == 0
    assert row_r["git_sha"] == "deadbeef"

    row_m = json.loads(lines_m[0])
    assert row_m["schema"] == "kc_main_brain_log_v1"
    assert row_m["kind"] == "swarm_ack"
    assert row_m["payload_ref"] == "vault/payload.md"
