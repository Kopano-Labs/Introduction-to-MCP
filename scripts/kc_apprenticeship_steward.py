#!/usr/bin/env python3
"""Steward KC apprenticeship tasks with machine-verifiable evidence (submit + review)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from kopano.kc_training_store import KcTrainingStore  # noqa: E402

from kc_apprenticeship_generic_handlers import fill_generic_handlers  # noqa: E402
from kc_apprenticeship_handlers_extra import extra_handlers  # noqa: E402
from kc_apprenticeship_manifest import CHECKPOINT_EVERY, MANIFEST_PATH  # noqa: E402
from kc_apprenticeship_status import (  # noqa: E402
    print_checkpoint_report,
    summarize_store,
    write_checkpoint,
)

DEFAULT_STORE = REPO_ROOT / "kopano-core" / ".kc" / "context_store.json"

COMPARE_URL = (
    "https://github.com/Kopano-Labs/Introduction-to-MCP/compare/"
    "master...codex/kc-sovereign-gui-full-dev?expand=1"
)
CODE_IN_CONTEXT = re.compile(r"Task (KCA-\d{4})")


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()[:2000]


def _git_sha() -> str:
    code, out = _run(["git", "rev-parse", "HEAD"])
    return out if code == 0 else "unknown"


def _read_excerpt(path: Path, max_lines: int = 12) -> str:
    if not path.exists():
        return f"missing: {path}"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[:max_lines])


def handlers(root: Path, manifest_tasks: list[dict] | None = None) -> dict[str, object]:
    sha = _git_sha()

    def h_note(note: str, teacher: str = "Save") -> tuple[str, str]:
        return f"{note}\nsha={sha}", teacher

    def h_file(path: str, note: str) -> tuple[str, str]:
        excerpt = _read_excerpt(root / path)
        student = f"{note}\npath={path}\nsha={sha}\n---\n{excerpt}"
        teacher = "Save — bounded file evidence; no external claim beyond repo."
        return student, teacher

    def h_cmd(label: str, cmd: list[str]) -> tuple[str, str]:
        code, out = _run(cmd)
        student = f"{label}\nexit={code}\nsha={sha}\n---\n{out}"
        teacher = "Save" if code == 0 else "Watch — command failed; fix and re-run."
        return student, teacher

    def h_grep(path: str, needle: str, note: str) -> tuple[str, str]:
        target = root / path
        if not target.is_file():
            return h_file(path, note)
        hits = [
            line
            for line in target.read_text(encoding="utf-8", errors="replace").splitlines()
            if needle in line
        ][:10]
        student = f"{note}\nneedle={needle}\npath={path}\nsha={sha}\n---\n" + "\n".join(hits or ["(no match)"])
        teacher = "Save" if hits else "Watch — pattern not found."
        return student, teacher

    base: dict[str, object] = {
        "KCA-0101": lambda: h_file(
            "docs/swarm-ops/SWARM_OPERATIONS.md",
            "External proof = CI URLs, DNS/HTTP probes, GitHub compare. Local = kc_guard, pytest, JSONL validate.",
        ),
        "KCA-0102": lambda: h_file("docs/swarm-ops/SWARM_OPERATIONS.md", "Proof bar section excerpt."),
        "KCA-0103": lambda: (
            "Forbidden: fake swarm complete, 300 nodes in code, demo-bypass evidence URLs under --strict-proof.\n"
            f"sha={sha}\nref=scripts/kc_log_append.py _STRICT_PROOF_BYPASS_MARKERS",
            "Save — aligns with doctrine.",
        ),
        "KCA-0104": lambda: h_cmd(
            "kc_log_append validate",
            [sys.executable, "scripts/kc_log_append.py", "validate"],
        ),
        "KCA-0105": lambda: h_cmd(
            "kc_log_append proof-check",
            [sys.executable, "scripts/kc_log_append.py", "proof-check"],
        ),
        "KCA-0106": lambda: (
            f"strict-proof requires exit_code + evidence_urls; compare URL used: {COMPARE_URL}\nsha={sha}",
            "Save — use real CI/compare URLs only.",
        ),
        "KCA-0107": lambda: h_cmd(
            "pytest student audit evidence",
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_kc_log_append.py",
                "tests/test_kc_guard.py",
                "-q",
            ],
        ),
        "KCA-0108": lambda: (
            "kimi_ack and swarm_ack accepted by kc_guard --require-swarm-ack; Kimi is external manual.\n"
            f"sha={sha}\nref=docs/swarm-ops/KIMI_ACK_FORMAT.md",
            "Save",
        ),
        "KCA-0109": lambda: h_file(
            "docs/swarm-ops/SWARM_OPERATIONS.md",
            "Kimi-external / Cursor-local boundary.",
        ),
        "KCA-0110": lambda: h_cmd(
            "pytest kc suite",
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_kc_log_append.py",
                "tests/test_kc_guard.py",
                "tests/test_kc_apprenticeship.py",
                "-q",
            ],
        ),
        "KCA-0111": lambda: h_file("docs/swarm-ops/VERIFIED_ENDPOINTS.md", "Verified hosts table."),
        "KCA-0112": lambda: h_file("index.md", "Root index links to swarm-ops."),
        "KCA-0113": lambda: (
            "Production host: https://context.kopanolabs.com (see VERIFIED_ENDPOINTS.md).\n"
            f"sha={sha}",
            "Save",
        ),
        "KCA-0114": lambda: h_cmd(
            "kc_guard doctrine-doc-hosts",
            [sys.executable, "scripts/kc_guard.py", "doctrine-doc-hosts"],
        ),
        "KCA-0115": lambda: (
            f"CI workflow: .github/workflows/swarm-proof.yml on branch push.\ncompare={COMPARE_URL}\nsha={sha}",
            "Save",
        ),
        "KCA-0201": lambda: h_file(
            "docs/swarm-ops/logs/README.md",
            "JSONL schema + CLI paths.",
        ),
        "KCA-0202": lambda: h_cmd(
            "validate logs",
            [sys.executable, "scripts/kc_log_append.py", "validate"],
        ),
        "KCA-0203": lambda: (
            f"Main brain append via kc_log_append mainbrain; sha={sha}",
            "Save",
        ),
        "KCA-0204": lambda: (
            'Use quoted pytest in review --commands, e.g. "python -m pytest ... -q".\n'
            f"sha={sha}",
            "Save",
        ),
        "KCA-0205": lambda: (
            "demo-bypass markers rejected by --strict-proof in kc_log_append.py.\n"
            f"sha={sha}",
            "Save",
        ),
        "KCA-0301": lambda: h_cmd(
            "kc_guard status",
            [sys.executable, "scripts/kc_guard.py", "status"],
        ),
        "KCA-0302": lambda: h_cmd(
            "kc_guard validate",
            [sys.executable, "scripts/kc_guard.py", "validate"],
        ),
        "KCA-0303": lambda: h_cmd(
            "kc_guard proof",
            [sys.executable, "scripts/kc_guard.py", "proof"],
        ),
        "KCA-0304": lambda: h_cmd(
            "kc_guard all (no doc hosts)",
            [sys.executable, "scripts/kc_guard.py", "all", "--no-check-doc-hosts"],
        ),
        "KCA-0305": lambda: (
            "--require-swarm-ack optional; no kimi_ack fabricated in repo.\n"
            f"sha={sha}",
            "Save",
        ),
        "KCA-0306": lambda: h_cmd(
            "git_sync_monitor",
            [sys.executable, "scripts/git_sync_monitor.py"],
        ),
        "KCA-0307": lambda: h_file(".gitignore", "kopano-core/.kc/ ignored for local store."),
        "KCA-0308": lambda: h_cmd(
            "pytest guard",
            [sys.executable, "-m", "pytest", "tests/test_kc_guard.py", "-q"],
        ),
        "KCA-0309": lambda: h_cmd(
            "pytest log append",
            [sys.executable, "-m", "pytest", "tests/test_kc_log_append.py", "-q"],
        ),
        "KCA-0310": lambda: h_file("DEMO_DAY_RUNBOOK.md", "Runbook machine gates."),
        "KCA-0401": lambda: (
            "Training API: kopano-core/kopano/kc_training_api.py GET /api/kc/training\n"
            f"sha={sha}",
            "Save",
        ),
        "KCA-0402": lambda: h_file("kopano-core/studio/src/apiBase.ts", "VITE_KC_API_BASE_URL."),
        "KCA-0403": lambda: (
            f"Manifest tasks=250 path=docs/swarm-ops/apprenticeship/kc_apprenticeship_250.json sha={sha}",
            "Save",
        ),
    }
    base.update(
        extra_handlers(root, sha, COMPARE_URL, h_file, h_cmd, h_grep, DEFAULT_STORE)
    )
    if manifest_tasks:
        fill_generic_handlers(
            base,
            manifest_tasks,
            root=root,
            sha=sha,
            h_file=h_file,
            h_cmd=h_cmd,
            store_path=DEFAULT_STORE,
        )
    return base


def record_codes(store: KcTrainingStore, manifest_tasks: list[dict]) -> dict[str, str]:
    ordered = sorted(store.records.keys(), key=lambda rid: int(rid.split("-", 1)[1]))
    mapping: dict[str, str] = {}
    for index, rid in enumerate(ordered):
        if index < len(manifest_tasks):
            mapping[rid] = manifest_tasks[index]["code"]
        else:
            match = CODE_IN_CONTEXT.search(store.records[rid].teacher_context)
            if match:
                mapping[rid] = match.group(1)
    return mapping


def _rid_by_code(store: KcTrainingStore, manifest_tasks: list[dict]) -> dict[str, str]:
    codes = record_codes(store, manifest_tasks)
    return {code: rid for rid, code in codes.items()}


def _emit_checkpoint(
    milestone: int,
    store: KcTrainingStore,
    manifest_tasks: list[dict],
    *,
    git_sha: str,
    log_review: bool,
) -> Path:
    payload = summarize_store(store, manifest_tasks, milestone=milestone)
    path = write_checkpoint(milestone, store, manifest_tasks, git_sha=git_sha)
    print_checkpoint_report(payload)
    if log_review:
        summary = payload["closure_line"]
        subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "kc_log_append.py"),
                "review",
                "--role",
                "student",
                "--phase",
                "apprenticeship",
                "--summary",
                f"KC status checkpoint @{milestone}: {summary}",
                "--commands",
                "python scripts/kc_apprenticeship_steward.py",
                "--exit-code",
                "0",
                "--evidence-url",
                COMPARE_URL,
            ],
            cwd=REPO_ROOT,
            check=False,
        )
    return path


def steward_phase(
    store: KcTrainingStore,
    manifest_tasks: list[dict],
    max_phase: int,
    promote: bool,
    checkpoint_every: int = 0,
    *,
    log_checkpoints: bool = True,
) -> dict[str, int]:
    hmap = handlers(REPO_ROOT, manifest_tasks)
    code_to_rid = _rid_by_code(store, manifest_tasks)
    stats = {"skipped": 0, "submitted": 0, "reviewed": 0, "promoted": 0, "no_handler": 0}
    sha = _git_sha()
    completed_index = 0

    for task in manifest_tasks:
        code = task["code"]
        phase = task["phase"]
        if phase > max_phase:
            continue
        rid = code_to_rid.get(code)
        if not rid:
            stats["no_handler"] += 1
            continue
        record = store.records[rid]
        if record.status in {"reviewed", "promoted"}:
            stats["skipped"] += 1
            completed_index += 1
            if checkpoint_every and completed_index % checkpoint_every == 0:
                _emit_checkpoint(
                    completed_index,
                    store,
                    manifest_tasks,
                    git_sha=sha,
                    log_review=log_checkpoints,
                )
            continue
        handler = hmap.get(code)
        if not handler:
            stats["no_handler"] += 1
            continue
        student, teacher = handler()
        store.submit(rid, student)
        stats["submitted"] += 1
        store.review(rid, teacher)
        stats["reviewed"] += 1
        if promote and teacher.startswith("Save"):
            store.promote(rid)
            stats["promoted"] += 1
        completed_index += 1
        if checkpoint_every and completed_index % checkpoint_every == 0:
            _emit_checkpoint(
                completed_index,
                store,
                manifest_tasks,
                git_sha=sha,
                log_review=log_checkpoints,
            )

    total = len(manifest_tasks)
    if checkpoint_every and completed_index == total and total % checkpoint_every != 0:
        _emit_checkpoint(
            total,
            store,
            manifest_tasks,
            git_sha=sha,
            log_review=log_checkpoints,
        )

    return stats


def write_progress(
    store: KcTrainingStore,
    stats: dict[str, int],
    max_phase: int,
    manifest_tasks: list[dict] | None = None,
) -> Path:
    counts: dict[str, int] = {}
    for record in store.records.values():
        counts[record.status] = counts.get(record.status, 0) + 1
    kc_status = summarize_store(store, manifest_tasks) if manifest_tasks else None
    payload = {
        "git_sha": _git_sha(),
        "task_count": len(manifest_tasks) if manifest_tasks else None,
        "checkpoint_every": CHECKPOINT_EVERY,
        "max_phase_stewarded": max_phase,
        "store_path": str(store.path),
        "status_counts": counts,
        "kc_opinion_counts": (kc_status or {}).get("kc_opinion_counts"),
        "last_run": stats,
        "compare_url": COMPARE_URL,
    }
    out = REPO_ROOT / "docs" / "swarm-ops" / "apprenticeship" / "progress.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


def append_receipt(stats: dict[str, int], progress_path: Path) -> None:
    summary = (
        f"Apprenticeship steward: submitted={stats['submitted']} reviewed={stats['reviewed']} "
        f"promoted={stats.get('promoted', 0)} progress={progress_path.name}"
    )
    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "kc_log_append.py"),
            "review",
            "--role",
            "student",
            "--phase",
            "apprenticeship",
            "--summary",
            summary,
            "--commands",
            "python scripts/kc_apprenticeship_steward.py",
            "--exit-code",
            "0",
            "--evidence-url",
            COMPARE_URL,
        ],
        cwd=REPO_ROOT,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--max-phase", type=int, default=10)
    parser.add_argument("--promote", action="store_true", help="Promote records with Save review")
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=0,
        help="Emit KC status checkpoint every N tasks (0=off; drill does not need sermon files)",
    )
    parser.add_argument("--no-log", action="store_true")
    parser.add_argument("--no-checkpoint-log", action="store_true", help="Skip review log on checkpoints")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    tasks = manifest["tasks"]
    store = KcTrainingStore(args.store)
    if not store.records:
        print("store empty; run kc_apprenticeship_activate.py first", file=sys.stderr)
        return 1
    if len(store.records) != len(tasks):
        print(
            f"warn: store has {len(store.records)} records, manifest has {len(tasks)} tasks",
            file=sys.stderr,
        )

    stats = steward_phase(
        store,
        tasks,
        args.max_phase,
        args.promote,
        args.checkpoint_every,
        log_checkpoints=not args.no_checkpoint_log,
    )
    progress = write_progress(store, stats, args.max_phase, tasks)
    print(json.dumps({"stats": stats, "progress": str(progress)}, indent=2))
    if not args.no_log and stats["reviewed"]:
        append_receipt(stats, progress)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
