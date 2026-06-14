#!/usr/bin/env python3
"""KC swarm JSONL: append, validate, proof-check (docs/swarm-ops)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REVIEW_REL = Path("docs/swarm-ops/logs/KC Review Log.jsonl")
MAIN_REL = Path("docs/swarm-ops/logs/KC Main Brain Log.jsonl")

REVIEW_KEYS = frozenset(
    {
        "schema",
        "ts",
        "role",
        "phase",
        "agent_id",
        "summary",
        "commands",
        "exit_code",
        "git_sha",
        "branch",
        "evidence_urls",
        "ref_review_id",
        "teacher_verdict",
    }
)
MAIN_KEYS = frozenset(
    {
        "schema",
        "ts",
        "kind",
        "summary",
        "commands",
        "exit_code",
        "git_sha",
        "evidence_urls",
        "payload_ref",
        "kimi_ack",
    }
)

_TS_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}T")


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _bracket_lint_summary(summary: str, label: str) -> int:
    """Return 1 if bracket lint fails."""
    try:
        scripts = Path(__file__).resolve().parent
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from kc_bracket_lint import lint_brackets

        errs = lint_brackets(summary)
        if errs:
            for e in errs:
                print(f"{label}bracket-lint: {e}", file=sys.stderr)
            return 1
    except Exception as exc:
        print(f"{label}bracket-lint: skipped ({exc})", file=sys.stderr)
    return 0


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


def _validate_ts(ts: object) -> list[str]:
    errs: list[str] = []
    if not isinstance(ts, str) or not _TS_PREFIX.match(ts):
        errs.append(f"invalid ts (expect ISO8601 UTC prefix): {ts!r}")
    return errs


def validate_review_record(obj: dict, line_no: int | None = None) -> list[str]:
    prefix = f"line {line_no}: " if line_no is not None else ""
    errs: list[str] = []
    extra = set(obj) - REVIEW_KEYS
    if extra:
        errs.append(f"{prefix}unknown keys: {sorted(extra)}")
    if obj.get("schema") != "kc_review_log_v1":
        errs.append(f"{prefix}schema must be kc_review_log_v1, got {obj.get('schema')!r}")
    errs.extend(_validate_ts(obj.get("ts", "")))
    role = obj.get("role")
    if role not in ("student", "teacher", "system"):
        errs.append(f"{prefix}role must be student|teacher|system, got {role!r}")
    phase = obj.get("phase")
    if not isinstance(phase, str) or not phase.strip():
        errs.append(f"{prefix}phase must be non-empty string")
    summary = obj.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        errs.append(f"{prefix}summary must be non-empty string")
    tv = obj.get("teacher_verdict")
    if tv is not None and tv not in ("approved", "rejected"):
        errs.append(f"{prefix}teacher_verdict must be approved|rejected|null, got {tv!r}")
    for key in ("commands", "evidence_urls"):
        v = obj.get(key)
        if v is not None and not isinstance(v, list):
            errs.append(f"{prefix}{key} must be array or null")
        elif isinstance(v, list) and not all(isinstance(x, str) for x in v):
            errs.append(f"{prefix}{key} items must be strings")
    ec = obj.get("exit_code")
    if ec is not None and not isinstance(ec, int):
        errs.append(f"{prefix}exit_code must be int or null")
    return errs


def validate_mainbrain_record(obj: dict, line_no: int | None = None) -> list[str]:
    prefix = f"line {line_no}: " if line_no is not None else ""
    errs: list[str] = []
    extra = set(obj) - MAIN_KEYS
    if extra:
        errs.append(f"{prefix}unknown keys: {sorted(extra)}")
    if obj.get("schema") != "kc_main_brain_log_v1":
        errs.append(f"{prefix}schema must be kc_main_brain_log_v1, got {obj.get('schema')!r}")
    errs.extend(_validate_ts(obj.get("ts", "")))
    kind = obj.get("kind")
    if not isinstance(kind, str) or not kind.strip():
        errs.append(f"{prefix}kind must be non-empty string")
    summary = obj.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        errs.append(f"{prefix}summary must be non-empty string")
    for key in ("commands", "evidence_urls"):
        v = obj.get(key)
        if v is not None and not isinstance(v, list):
            errs.append(f"{prefix}{key} must be array or null")
        elif isinstance(v, list) and not all(isinstance(x, str) for x in v):
            errs.append(f"{prefix}{key} items must be strings")
    ec = obj.get("exit_code")
    if ec is not None and not isinstance(ec, int):
        errs.append(f"{prefix}exit_code must be int or null")
    ka = obj.get("kimi_ack")
    if ka is not None:
        if not isinstance(ka, dict):
            errs.append(f"{prefix}kimi_ack must be object or null")
        else:
            for req in ("timestamp", "payload_ref", "status"):
                if not isinstance(ka.get(req), str) or not str(ka.get(req)).strip():
                    errs.append(f"{prefix}kimi_ack.{req} must be non-empty string")
            notes = ka.get("notes")
            if notes is not None and not isinstance(notes, str):
                errs.append(f"{prefix}kimi_ack.notes must be string or null")
            if set(ka) - {"timestamp", "payload_ref", "status", "notes"}:
                errs.append(f"{prefix}kimi_ack has unknown keys")
    return errs


def validate_jsonl_file(path: Path) -> list[str]:
    all_errs: list[str] = []
    if not path.is_file():
        all_errs.append(f"missing file: {path}")
        return all_errs
    with path.open(encoding="utf-8") as f:
        for i, raw in enumerate(f, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as e:
                all_errs.append(f"line {i}: invalid JSON: {e}")
                continue
            if not isinstance(obj, dict):
                all_errs.append(f"line {i}: record must be object")
                continue
            schema = obj.get("schema")
            if schema == "kc_review_log_v1":
                all_errs.extend(validate_review_record(obj, i))
            elif schema == "kc_main_brain_log_v1":
                all_errs.extend(validate_mainbrain_record(obj, i))
            else:
                all_errs.append(f"line {i}: unknown schema {schema!r}")
    return all_errs


_STRICT_PROOF_BYPASS_MARKERS = (
    "demo-bypass",
    "demo_bypass",
    "placeholder-receipt",
    "your-durable-evidence",
)


def _strict_proof_errors(record: dict, *, label: str) -> list[str]:
    errs: list[str] = []
    if record.get("exit_code") is None:
        errs.append(f"{label}strict-proof: exit_code is required")
    urls = record.get("evidence_urls")
    if not urls or not isinstance(urls, list) or len(urls) == 0:
        errs.append(f"{label}strict-proof: at least one --evidence-url is required")
    elif isinstance(urls, list):
        for u in urls:
            if not isinstance(u, str) or not u.strip():
                continue
            low = u.lower()
            if any(m in low for m in _STRICT_PROOF_BYPASS_MARKERS):
                errs.append(
                    f"{label}strict-proof: evidence URL looks like a demo bypass, not an "
                    f"external operator receipt ({u!r})",
                )
    return errs


def _strict_proof_warn_sha(record: dict, label: str) -> None:
    if not record.get("git_sha"):
        print(f"{label}strict-proof warning: git_sha missing (CI/local should set --git-sha)", file=sys.stderr)


def cmd_review(args: argparse.Namespace, root: Path) -> int:
    git_sha = args.git_sha or _git_sha(root)
    record = {
        "schema": "kc_review_log_v1",
        "ts": _utc_now_iso(),
        "role": args.role,
        "phase": args.phase,
        "agent_id": args.agent_id,
        "summary": args.summary,
        "commands": args.commands or None,
        "exit_code": args.exit_code,
        "git_sha": git_sha,
        "branch": args.branch,
        "evidence_urls": args.evidence_url or None,
        "ref_review_id": args.ref_review_id,
        "teacher_verdict": args.teacher_verdict,
    }
    pre = validate_review_record(record)
    if pre:
        for e in pre:
            print(e, file=sys.stderr)
        return 1
    if args.strict_proof:
        errs = _strict_proof_errors(record, label="review: ")
        if errs:
            for e in errs:
                print(e, file=sys.stderr)
            return 1
        _strict_proof_warn_sha(record, "review: ")
    if getattr(args, "bracket_lint", False):
        if _bracket_lint_summary(args.summary, "review: "):
            return 1
    _append_jsonl(root / REVIEW_REL, record)
    return 0


def cmd_mainbrain(args: argparse.Namespace, root: Path) -> int:
    git_sha = args.git_sha or _git_sha(root)
    urls = args.evidence_url or None
    record = {
        "schema": "kc_main_brain_log_v1",
        "ts": _utc_now_iso(),
        "kind": args.kind,
        "summary": args.summary,
        "commands": args.commands or None,
        "exit_code": args.exit_code,
        "git_sha": git_sha,
        "evidence_urls": urls,
        "payload_ref": args.payload_ref,
        "kimi_ack": None,
    }
    pre = validate_mainbrain_record(record)
    if pre:
        for e in pre:
            print(e, file=sys.stderr)
        return 1
    if args.strict_proof:
        errs = _strict_proof_errors(record, label="mainbrain: ")
        if errs:
            for e in errs:
                print(e, file=sys.stderr)
            return 1
        _strict_proof_warn_sha(record, "mainbrain: ")
    if getattr(args, "bracket_lint", False):
        if _bracket_lint_summary(args.summary, "mainbrain: "):
            return 1
    _append_jsonl(root / MAIN_REL, record)
    return 0


def _format_kimi_ack_block(ts: str, payload_ref: str, status: str, notes: str | None) -> str:
    lines = [
        "[KIMI_ACK]",
        f"timestamp: {ts}",
        f"payload_ref: {payload_ref}",
        f"status: {status}",
        f"notes: {notes or ''}",
    ]
    return "\n".join(lines)


def cmd_kimi_ack(args: argparse.Namespace, root: Path) -> int:
    ts = args.timestamp or _utc_now_iso()
    notes = args.notes or None
    block = _format_kimi_ack_block(ts, args.payload_ref, args.status, notes)
    ka = {
        "timestamp": ts,
        "payload_ref": args.payload_ref,
        "status": args.status,
        "notes": notes,
    }
    urls = args.evidence_url or None
    record = {
        "schema": "kc_main_brain_log_v1",
        "ts": _utc_now_iso(),
        "kind": "kimi_ack",
        "summary": block,
        "commands": None,
        "exit_code": args.exit_code,
        "git_sha": args.git_sha or _git_sha(root),
        "evidence_urls": urls,
        "payload_ref": args.payload_ref,
        "kimi_ack": ka,
    }
    pre = validate_mainbrain_record(record)
    if pre:
        for e in pre:
            print(e, file=sys.stderr)
        return 1
    if args.strict_proof:
        errs = _strict_proof_errors(record, label="kimi-ack: ")
        if errs:
            for e in errs:
                print(e, file=sys.stderr)
            return 1
        _strict_proof_warn_sha(record, "kimi-ack: ")
    _append_jsonl(root / MAIN_REL, record)
    return 0


def cmd_validate(args: argparse.Namespace, root: Path) -> int:
    raw = list(args.paths) if args.paths else []
    paths = [root / p if not p.is_absolute() else p for p in raw] if raw else [root / REVIEW_REL, root / MAIN_REL]
    failed = False
    for p in paths:
        errs = validate_jsonl_file(p)
        if errs:
            failed = True
            print(f"--- {p} ---", file=sys.stderr)
            for e in errs:
                print(e, file=sys.stderr)
        else:
            print(f"OK {p}")
    return 1 if failed else 0


def cmd_proof_check(args: argparse.Namespace, root: Path) -> int:
    review_path = root / REVIEW_REL
    main_path = root / MAIN_REL
    errs = validate_jsonl_file(review_path) + validate_jsonl_file(main_path)
    if errs:
        for e in errs:
            print(e, file=sys.stderr)
        return 1
    # Last student audit row must have exit_code and evidence_urls
    last_audit: dict | None = None
    if review_path.is_file():
        with review_path.open(encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict) and obj.get("role") == "student" and obj.get("phase") == "audit":
                    last_audit = obj
    if last_audit is None:
        print(
            "proof-check: no student/audit row found in KC Review Log "
            "(append one after smoke: kc_log_append.py review --strict-proof ...)",
            file=sys.stderr,
        )
        return 2
    if last_audit.get("exit_code") is None:
        print("proof-check: last student audit missing exit_code", file=sys.stderr)
        return 3
    urls = last_audit.get("evidence_urls")
    if not urls:
        print("proof-check: last student audit missing evidence_urls", file=sys.stderr)
        return 3
    print(f"proof-check OK (last student audit ts={last_audit.get('ts')})")

    last_main: dict | None = None
    if main_path.is_file():
        with main_path.open(encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict) and obj.get("kind") != "bootstrap":
                    last_main = obj
    if last_main is None:
        print(
            "proof-check: no non-bootstrap row in KC Main Brain Log "
            "(append obedience/swarm_ack/kimi_ack with exit_code + evidence_urls)",
            file=sys.stderr,
        )
        return 2
    if last_main.get("exit_code") is None:
        print("proof-check: last main-brain receipt missing exit_code", file=sys.stderr)
        return 3
    m_urls = last_main.get("evidence_urls")
    if not m_urls:
        print("proof-check: last main-brain receipt missing evidence_urls", file=sys.stderr)
        return 3
    print(f"proof-check OK (last main-brain kind={last_main.get('kind')} ts={last_main.get('ts')})")
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
        help="Command lines executed",
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
    pr.add_argument(
        "--strict-proof",
        action="store_true",
        help="Require exit_code and at least one evidence URL; warn if git_sha missing",
    )
    pr.add_argument(
        "--bracket-lint",
        action="store_true",
        help="Reject summary if bracket blasphemy register violated",
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
    pm.add_argument(
        "--strict-proof",
        action="store_true",
        help="Require exit_code and at least one evidence URL; warn if git_sha missing",
    )
    pm.add_argument(
        "--bracket-lint",
        action="store_true",
        help="Reject summary if bracket blasphemy register violated",
    )

    pk = sub.add_parser("kimi-ack", help="Append standardized Kimi acknowledgement (main brain log)")
    pk.set_defaults(func=cmd_kimi_ack)
    pk.add_argument("--payload-ref", required=True)
    pk.add_argument("--status", required=True, help="e.g. acknowledged, rejected, partial")
    pk.add_argument("--notes", default=None)
    pk.add_argument("--timestamp", default=None, help="ISO8601 UTC (default: now)")
    pk.add_argument("--exit-code", type=int, default=0)
    pk.add_argument("--git-sha", default=None)
    pk.add_argument("--evidence-url", action="append", default=None, metavar="URL")
    pk.add_argument(
        "--strict-proof",
        action="store_true",
        help="Require exit_code and at least one evidence URL (default exit_code=0 counts)",
    )

    pv = sub.add_parser("validate", help="Validate JSONL lines against kc_* schemas")
    pv.set_defaults(func=cmd_validate)
    pv.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="JSONL files (default: both KC logs under docs/swarm-ops/logs/)",
    )

    pp = sub.add_parser(
        "proof-check",
        help="Validate logs + require a recent student/audit row with exit_code and evidence_urls",
    )
    pp.set_defaults(func=cmd_proof_check)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    root = args.repo_root or _repo_root()
    return int(args.func(args, root))


if __name__ == "__main__":
    raise SystemExit(main())
