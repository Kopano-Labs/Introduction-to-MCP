"""Build the KC Student Apprenticeship 150-task manifest (10 phases × 15 tasks)."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "docs" / "swarm-ops" / "apprenticeship" / "kc_apprenticeship_150.json"

PHASES: list[tuple[str, list[str]]] = [
    (
        "Proof bar and receipts",
        [
            "Define what counts as external proof vs local-only work",
            "Read SWARM_OPERATIONS.md proof bar section",
            "List forbidden claims (fake swarm, demo-bypass URLs)",
            "Run kc_log_append.py validate on Review Log",
            "Run kc_log_append.py proof-check without strict mode",
            "Run proof-check with --strict-proof on a clean row",
            "Append a student_audit row with real pytest evidence only",
            "Explain difference between kimi_ack and swarm_ack",
            "Document why Kimi is out-of-repo manual",
            "Link VERIFIED_ENDPOINTS.md from index.md",
            "Verify context.kopanolabs.com probe in runbook",
            "Reject NXDOMAIN hosts in doc drift check",
            "Capture CI workflow URL after push",
            "Write one-line receipt for guard pass",
            "Summarize graduation Law 4 from apprenticeship protocol",
        ],
    ),
    (
        "JSONL stewardship logs",
        [
            "Locate KC Review Log and Main Brain Log paths",
            "Validate JSONL schema for review entries",
            "Append a mainbrain note with bounded scope",
            "Use review --commands with quoted pytest strings",
            "Avoid demo-bypass markers in evidence_urls",
            "Cross-check log entry timestamps are ISO-8601",
            "Explain Save/Kill/Watch in teacher review text",
            "Mirror one comms-log decision into Review Log",
            "Tag entry with apprenticeship phase id",
            "Keep student_response under 500 words",
            "Reference file paths not line numbers only",
            "Link PR compare URL when gh auth unavailable",
            "Record store_path for KC context store",
            "Note strict-proof failure modes",
            "Archive a completed task id in review notes",
        ],
    ),
    (
        "kc_guard and local gates",
        [
            "Run kc_guard.py status",
            "Run kc_guard.py validate",
            "Run kc_guard.py proof",
            "Run kc_guard.py all with doc-host check",
            "Run kc_guard.py all --no-check-doc-hosts",
            "Understand --require-swarm-ack optional gate",
            "Run git_sync_monitor.py once",
            "Fix gitignore guard if Schematics noise appears",
            "Run pytest for kc_guard tests",
            "Run pytest for kc_log_append tests",
            "Document exit codes in runbook",
            "Wire guard into DEMO_DAY_RUNBOOK.md",
            "Explain watch mode for long sessions",
            "Do not enable swarm ack without external receipt",
            "Post guard summary to Training student_response",
        ],
    ),
    (
        "Studio Training surface",
        [
            "Open Training page in Kopano Studio",
            "Confirm VITE_KC_API_BASE_URL override",
            "GET /api/kc/training returns status + records",
            "Create teacher assignment via UI",
            "Submit student response for one task",
            "Add teacher review with Save verdict",
            "Promote one record to graduated state",
            "Seed starter when store empty",
            "Refresh queue every 1.8s without errors",
            "Show active vs reviewed counts",
            "Handle API offline message gracefully",
            "Link Training page to apprenticeship manifest",
            "Use kopano lane as student identity",
            "Use cassey lane as teacher identity in copy",
            "Export one promoted record summary to JSONL",
        ],
    ),
    (
        "Verified endpoints and DNS",
        [
            "Read VERIFIED_ENDPOINTS.md table",
            "Run swarm_remote_proof_urls.ps1 --probe",
            "Run swarm_remote_proof_urls.sh --probe",
            "Record HTTP status for context host",
            "Document NXDOMAIN for retired hosts",
            "Align PRODUCTION_URL in api.py",
            "Trim dead CORS origins",
            "Add kopanolabs.com to CORS allowlist",
            "Update studio apiBase default",
            "Probe local 127.0.0.1:8000 health",
            "Never claim cryptographic proof",
            "Store probe output path in evidence",
            "Re-run probes after DNS change",
            "Update doctrine when host changes",
            "Submit probe receipt as student work",
        ],
    ),
    (
        "CI and branch hygiene",
        [
            "Read swarm-proof.yml triggers",
            "Confirm push to feature branch runs CI",
            "List jobs: validate, proof, guard, pytest",
            "Fix failing pytest before push",
            "Keep commits scoped to apprenticeship",
            "Avoid committing Schematics noise",
            "Use compare URL when gh 401",
            "Document HEAD sha in review log",
            "Do not amend pushed commits",
            "Run full guard before push",
            "Tag commit message with apprenticeship",
            "Link workflow run in evidence_urls",
            "Note branch tracks origin",
            "Verify no secrets in diff",
            "Student: summarize last green CI run",
        ],
    ),
    (
        "Doctrine and honesty",
        [
            "Read KC-Student-Teacher-Apprenticeship-Protocol",
            "State Law 1: no unsupervised writes",
            "State Law 5: KC is brain not worker",
            "List teacher assignments table",
            "Identify Cursor as AG student surface",
            "Identify KC as memory not executor",
            "Reject 300-node fiction in code claims",
            "Map 50 demo tasks to apprenticeship phases",
            "Explain 150 = 10×15 stewardship expansion",
            "No kimi-ack without manual external step",
            "Honesty about local-only owner_proof",
            "Cross-link NAVIGATION.md",
            "Update apprenticeship status in manifest",
            "Teacher review: Watch on risky scope",
            "Promote only after evidence attached",
        ],
    ),
    (
        "Labs and integration touchpoints",
        [
            "List labs_api routes at high level",
            "Open Labs page without console errors",
            "Describe KasiLink bridge purpose",
            "Note Microsoft readiness surface",
            "MCP console: ask one grounded question",
            "Cowork room: create read-only inspection",
            "SA language route: name target language",
            "Forge page: state mission in one sentence",
            "Council page: one agent message test",
            "Admin page: list what is configurable",
            "Telemetry: confirm client events optional",
            "Do not store API keys in student_response",
            "Reference labs from teacher_context",
            "Submit integration smoke notes",
            "Teacher: Save if bounded and reproducible",
        ],
    ),
    (
        "Graduation and lifecycle",
        [
            "Name four lifecycle stages from protocol",
            "Count promoted records in store",
            "Count reviewed vs assigned ratio",
            "Define 10+ verified tasks threshold",
            "Zero hallucination: cite files only",
            "Chief Architect sign-off is external",
            "Protocol 13 compliance checklist",
            "Shadowing: document watch-only session",
            "Supervised write: one reviewed PR scope",
            "Graduate: draft criteria not claim met",
            "Cassy supervised audits Lessons 001-014",
            "OG Mirror Wardens: vault parity note",
            "Recon scouts: research no-write example",
            "Stewardship split Cursor vs KC roles",
            "Append graduation intent to Main Brain Log",
        ],
    ),
    (
        "Demo hardening and ops",
        [
            "Read DEMO_DAY_RUNBOOK machine gates",
            "Run pytest suite documented in runbook",
            "Cold-start api path sanity check",
            "Studio npm run lint if node present",
            "Binary path: note KopanoContext.exe optional",
            "Azure deploy: cite bicep folder only",
            "SafeSkill: no hardcoded secrets scan",
            "Reward system folder purpose one line",
            "Legacy archive: what not to ship",
            "10 phases 50 tasks map to 150 ledger",
            "Activate script: dry-run count",
            "Activate script: seed store path",
            "Training UI shows 150 assigned queue",
            "Stewardship: autonomous Cursor execution",
            "Final: kc_guard all + manifest hash note",
        ],
    ),
]


def build_tasks() -> list[dict[str, str]]:
    tasks: list[dict[str, str]] = []
    for phase_index, (phase_title, items) in enumerate(PHASES, start=1):
        for task_index, item in enumerate(items, start=1):
            code = f"KCA-{phase_index:02d}{task_index:02d}"
            title = f"KC — P{phase_index} T{task_index:02d}: {item}"
            teacher_context = (
                f"Phase {phase_index} ({phase_title}). Task {code}. "
                f"Student (kopano/Cassy): {item}. "
                "Deliverable: short student_response with file paths, command output, or URL. "
                "No fake swarm, no demo-bypass evidence. Teacher (Cursor/KC) reviews Save/Kill/Watch."
            )
            tasks.append(
                {
                    "code": code,
                    "phase": phase_index,
                    "phase_title": phase_title,
                    "title": title,
                    "teacher_context": teacher_context,
                }
            )
    if len(tasks) != 150:
        raise RuntimeError(f"expected 150 tasks, got {len(tasks)}")
    return tasks


def write_manifest(path: Path | None = None) -> Path:
    target = path or MANIFEST_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "kc_apprenticeship_v1",
        "task_count": 150,
        "phases": 10,
        "tasks_per_phase": 15,
        "stewards": ["KC", "Cursor"],
        "protocol": "Schematics/18-PROTOCOLS/KC-Student-Teacher-Apprenticeship-Protocol.md",
        "tasks": build_tasks(),
    }
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target


if __name__ == "__main__":
    out = write_manifest()
    print(out)
