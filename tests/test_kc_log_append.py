"""Tests for scripts/kc_log_append.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "kc_log_append.py"


def _run(tmp_root: Path, *cli_args: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT), "--repo-root", str(tmp_root), *cli_args]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def test_append_review_and_mainbrain(tmp_path: Path) -> None:
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    review = tmp_path / "docs/swarm-ops/logs/KC Review Log.jsonl"
    mainb = tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl"
    review.write_text("", encoding="utf-8")
    mainb.write_text("", encoding="utf-8")

    r1 = _run(
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

    r2 = _run(
        tmp_path,
        "mainbrain",
        "--kind",
        "swarm_ack",
        "--summary",
        "kimi ack",
        "--payload-ref",
        "vault/payload.md",
        "--exit-code",
        "0",
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
    assert row_m["exit_code"] == 0
    assert row_m["kimi_ack"] is None


def test_strict_proof_requires_evidence(tmp_path: Path) -> None:
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    (tmp_path / "docs/swarm-ops/logs/KC Review Log.jsonl").write_text("", encoding="utf-8")
    r = _run(
        tmp_path,
        "review",
        "--strict-proof",
        "--role",
        "student",
        "--phase",
        "audit",
        "--summary",
        "no urls",
        "--exit-code",
        "0",
    )
    assert r.returncode == 1
    assert "strict-proof" in r.stderr


def test_strict_proof_rejects_demo_bypass_url(tmp_path: Path) -> None:
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    (tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl").write_text("", encoding="utf-8")
    r = _run(
        tmp_path,
        "kimi-ack",
        "--payload-ref",
        "docs/swarm-ops/PAYLOAD.md",
        "--status",
        "acknowledged",
        "--exit-code",
        "0",
        "--evidence-url",
        "https://context.kopanolabs.com/demo-bypass-receipt-placeholder",
        "--strict-proof",
    )
    assert r.returncode == 1
    assert "demo bypass" in r.stderr.lower()


def test_validate_and_proof_check(tmp_path: Path) -> None:
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    review = tmp_path / "docs/swarm-ops/logs/KC Review Log.jsonl"
    mainb = tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl"
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

    v = _run(tmp_path, "validate")
    assert v.returncode == 0, v.stderr

    pc = _run(tmp_path, "proof-check")
    assert pc.returncode == 0, pc.stderr


def test_legacy_telemetry_is_valid_but_not_selected_as_proof(tmp_path: Path) -> None:
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    review = tmp_path / "docs/swarm-ops/logs/KC Review Log.jsonl"
    mainb = tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl"
    review.write_text(
        '{"schema":"kc_review_log_v1","ts":"2026-05-16T12:01:00Z","role":"student",'
        '"phase":"audit","agent_id":"t","summary":"audit","commands":["pytest"],'
        '"exit_code":0,"git_sha":"abc","branch":null,'
        '"evidence_urls":["https://example.com/review"],"ref_review_id":null,'
        '"teacher_verdict":null}\n'
        '{"ts":"2026-06-04T23:23:34Z","kind":"student_audit",'
        '"summary":"legacy telemetry","status":"pending_teacher"}\n',
        encoding="utf-8",
    )
    mainb.write_text(
        '{"schema":"kc_main_brain_log_v1","ts":"2026-06-14T12:27:39Z",'
        '"kind":"receipt","summary":"proof","commands":null,"exit_code":0,'
        '"git_sha":"abc","evidence_urls":["https://example.com/main"],'
        '"payload_ref":null,"kimi_ack":null}\n'
        '{"ts":"2026-06-22T05:09:12Z","kind":"identi_ai_flow",'
        '"summary":"legacy operational telemetry","verdict":"HANDOFF_SUBMITTED"}\n',
        encoding="utf-8",
    )

    validated = _run(tmp_path, "validate")
    assert validated.returncode == 0, validated.stderr

    proof = _run(tmp_path, "proof-check")
    assert proof.returncode == 0, proof.stderr


def test_validate_rejects_unknown_explicit_schema(tmp_path: Path) -> None:
    path = tmp_path / "unknown.jsonl"
    path.write_text(
        '{"schema":"future_without_contract","ts":"2026-06-22T05:09:12Z",'
        '"kind":"event","summary":"not governed"}\n',
        encoding="utf-8",
    )
    result = _run(tmp_path, "validate", path)
    assert result.returncode == 1
    assert "unknown schema" in result.stderr


def test_validate_accepts_historical_mainbrain_extensions(tmp_path: Path) -> None:
    path = tmp_path / "historical.jsonl"
    path.write_text(
        '{"schema":"kc_main_brain_log_v1","ts":"2026-06-14T18:26:08Z",'
        '"kind":"oz_lattice_bleed","source":"gui","target":"crud",'
        '"verdict":"BLEED_DETECTED","exit_code":1}\n'
        '{"schema":"kc_main_brain_log_v1","ts":"%Y-%m-%dT%H:%M:%SZ",'
        '"kind":"council_kc_conclusion","summary":"historical import"}\n',
        encoding="utf-8",
    )
    result = _run(tmp_path, "validate", path)
    assert result.returncode == 0, result.stderr


def test_proof_check_fails_without_student_audit(tmp_path: Path) -> None:
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    (tmp_path / "docs/swarm-ops/logs/KC Review Log.jsonl").write_text(
        '{"schema":"kc_review_log_v1","ts":"2026-05-16T12:00:00Z","role":"system",'
        '"phase":"bootstrap","agent_id":null,"summary":"boot","commands":null,'
        '"exit_code":null,"git_sha":null,"branch":null,"evidence_urls":null,'
        '"ref_review_id":null,"teacher_verdict":null}\n',
        encoding="utf-8",
    )
    (tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl").write_text(
        '{"schema":"kc_main_brain_log_v1","ts":"2026-05-16T12:00:00Z","kind":"bootstrap",'
        '"summary":"boot","commands":null,"exit_code":null,"git_sha":null,'
        '"evidence_urls":null,"payload_ref":null,"kimi_ack":null}\n',
        encoding="utf-8",
    )
    pc = _run(tmp_path, "proof-check")
    assert pc.returncode == 2


def test_kimi_ack_appends_structured_block(tmp_path: Path) -> None:
    (tmp_path / "docs/swarm-ops/logs").mkdir(parents=True)
    (tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl").write_text("", encoding="utf-8")
    r = _run(
        tmp_path,
        "kimi-ack",
        "--payload-ref",
        "docs/swarm-ops/PAYLOAD.md",
        "--status",
        "acknowledged",
        "--notes",
        "done",
        "--timestamp",
        "2026-05-16T15:00:00Z",
        "--exit-code",
        "0",
        "--evidence-url",
        "https://ci.example/job/1",
        "--strict-proof",
        "--git-sha",
        "abc123",
    )
    assert r.returncode == 0, r.stderr
    line = (tmp_path / "docs/swarm-ops/logs/KC Main Brain Log.jsonl").read_text(encoding="utf-8").strip()
    row = json.loads(line)
    assert row["kind"] == "kimi_ack"
    assert "[KIMI_ACK]" in row["summary"]
    assert row["kimi_ack"]["status"] == "acknowledged"
    assert row["kimi_ack"]["payload_ref"] == "docs/swarm-ops/PAYLOAD.md"
    assert row["evidence_urls"] == ["https://ci.example/job/1"]
