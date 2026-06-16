"""Tests for scripts/kc_guard.py."""
from __future__ import annotations

import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))



import json
import subprocess
import sys
from pathlib import Path

GUARD = Path(__file__).resolve().parent.parent / "scripts" / "kc_guard.py"


def _run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(GUARD), "--repo-root", str(root), *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def _init_git(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@e"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "https://example.com/test/repo.git"],
        cwd=root,
        check=True,
        capture_output=True,
    )


def _good_logs(review: Path, mainb: Path) -> None:
    review.write_text(
        '{"schema":"kc_review_log_v1","ts":"2026-05-16T12:00:00Z","role":"system",'
        '"phase":"bootstrap","agent_id":null,"summary":"boot","commands":null,'
        '"exit_code":null,"git_sha":null,"branch":null,"evidence_urls":null,'
        '"ref_review_id":null,"teacher_verdict":null}\n'
        '{"schema":"kc_review_log_v1","ts":"2026-05-16T12:01:00Z","role":"student",'
        '"phase":"audit","agent_id":"t","summary":"audit","commands":["pytest"],'
        '"exit_code":0,"git_sha":null,"branch":null,"evidence_urls":["https://example.com"],'
        '"ref_review_id":null,"teacher_verdict":null}\n',
        encoding="utf-8",
    )
    mainb.write_text(
        '{"schema":"kc_main_brain_log_v1","ts":"2026-05-16T12:00:00Z","kind":"bootstrap",'
        '"summary":"boot","commands":null,"exit_code":null,"git_sha":null,'
        '"evidence_urls":null,"payload_ref":null,"kimi_ack":null}\n'
        '{"schema":"kc_main_brain_log_v1","ts":"2026-05-16T12:01:00Z","kind":"obedience",'
        '"summary":"r","commands":["x"],"exit_code":0,"git_sha":null,'
        '"evidence_urls":["https://example.com"],"payload_ref":null,"kimi_ack":null}\n',
        encoding="utf-8",
    )


def test_guard_validate_delegates(tmp_path: Path) -> None:
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    review = tmp_path / "docs/swarm-ops/logs/KC Review Log.jsonl"
    mainb = tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl"
    _good_logs(review, mainb)
    r = _run(tmp_path, "validate")
    assert r.returncode == 0, r.stderr


def _swarm_doctrine_files(tmp_path: Path) -> None:
    (tmp_path / "docs/swarm-ops").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/swarm-ops/SWARM_OPERATIONS.md").write_text("# x\n", encoding="utf-8")
    (tmp_path / "docs/swarm-ops/VERIFIED_ENDPOINTS.md").write_text(
        "| `https://context.kopanolabs.com/` | ok |\n", encoding="utf-8"
    )


def test_guard_all_without_swarm_ack_requirement(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _swarm_doctrine_files(tmp_path)
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    review = tmp_path / "docs/swarm-ops/logs/KC Review Log.jsonl"
    mainb = tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl"
    _good_logs(review, mainb)
    r = _run(tmp_path, "all")
    assert r.returncode == 0, r.stdout + r.stderr


def test_guard_require_swarm_ack_fails_without_row(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _swarm_doctrine_files(tmp_path)
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    review = tmp_path / "docs/swarm-ops/logs/KC Review Log.jsonl"
    mainb = tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl"
    _good_logs(review, mainb)
    r = _run(tmp_path, "all", "--require-swarm-ack")
    assert r.returncode == 3, r.stdout + r.stderr


def test_guard_require_swarm_ack_passes_with_row(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _swarm_doctrine_files(tmp_path)
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    review = tmp_path / "docs/swarm-ops/logs/KC Review Log.jsonl"
    mainb = tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl"
    _good_logs(review, mainb)
    extra = (
        '{"schema":"kc_main_brain_log_v1","ts":"2026-05-16T12:02:00Z","kind":"swarm_ack",'
        '"summary":"kimi","commands":null,"exit_code":0,"git_sha":null,'
        '"evidence_urls":["https://kimi.example/thread"],"payload_ref":"p.md","kimi_ack":null}\n'
    )
    mainb.write_text(mainb.read_text(encoding="utf-8") + extra, encoding="utf-8")
    r = _run(tmp_path, "all", "--require-swarm-ack")
    assert r.returncode == 0, r.stdout + r.stderr


def test_guard_require_swarm_ack_passes_with_kimi_ack_row(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _swarm_doctrine_files(tmp_path)
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    review = tmp_path / "docs/swarm-ops/logs/KC Review Log.jsonl"
    mainb = tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl"
    _good_logs(review, mainb)
    extra = (
        '{"schema":"kc_main_brain_log_v1","ts":"2026-05-16T12:02:00Z","kind":"kimi_ack",'
        '"summary":"kimi","commands":null,"exit_code":0,"git_sha":null,'
        '"evidence_urls":["https://kimi.example/thread"],"payload_ref":"p.md","kimi_ack":null}\n'
    )
    mainb.write_text(mainb.read_text(encoding="utf-8") + extra, encoding="utf-8")
    r = _run(tmp_path, "all", "--require-swarm-ack")
    assert r.returncode == 0, r.stdout + r.stderr


def test_doctrine_doc_hosts_rejects_dead_host(tmp_path: Path) -> None:
    (tmp_path / "docs/swarm-ops").mkdir(parents=True)
    (tmp_path / "docs/swarm-ops/VERIFIED_ENDPOINTS.md").write_text(
        "| `https://kopanocontext.kopanolabs.com/` | NXDOMAIN |\n", encoding="utf-8"
    )
    bad = tmp_path / "docs/swarm-ops/BAD.md"
    bad.write_text("Use https://kopanocontext.kopanolabs.com/ here\n", encoding="utf-8")
    r = _run(tmp_path, "doctrine-doc-hosts")
    assert r.returncode == 3, r.stdout + r.stderr


def test_doctrine_doc_hosts_allows_verified_context(tmp_path: Path) -> None:
    (tmp_path / "docs/swarm-ops").mkdir(parents=True)
    (tmp_path / "docs/swarm-ops/VERIFIED_ENDPOINTS.md").write_text(
        "| `https://context.kopanolabs.com/` | ok |\n", encoding="utf-8"
    )
    ok_doc = tmp_path / "docs/swarm-ops/OK.md"
    ok_doc.write_text("BFF: https://context.kopanolabs.com/\n", encoding="utf-8")
    r = _run(tmp_path, "doctrine-doc-hosts")
    assert r.returncode == 0, r.stderr


def test_doctrine_swarm_ack_subcommand(tmp_path: Path) -> None:
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    mainb = tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl"
    mainb.write_text(
        '{"schema":"kc_main_brain_log_v1","kind":"swarm_ack","summary":"x",'
        '"evidence_urls":["https://a"]}\n',
        encoding="utf-8",
    )
    r = _run(tmp_path, "doctrine-swarm-ack")
    assert r.returncode == 0, r.stderr