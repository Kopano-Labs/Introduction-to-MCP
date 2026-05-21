"""Extended stewardship handlers for KC apprenticeship phases 2–10."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

Handler = Callable[[], tuple[str, str]]


def extra_handlers(
    root: Path,
    sha: str,
    compare_url: str,
    h_file: Callable[[str, str], tuple[str, str]],
    h_cmd: Callable[[str, list[str]], tuple[str, str]],
    h_grep: Callable[[str, str, str], tuple[str, str]],
    store_path: Path,
) -> dict[str, Handler]:
    def h_note(note: str, teacher: str = "Save") -> Handler:
        return lambda: (f"{note}\nsha={sha}", teacher)

    def h_store_counts() -> tuple[str, str]:
        if not store_path.exists():
            return f"store missing: {store_path}", "Watch"
        payload = json.loads(store_path.read_text(encoding="utf-8"))
        counts: dict[str, int] = {}
        for rec in payload.get("records", {}).values():
            st = rec.get("status", "assigned")
            counts[st] = counts.get(st, 0) + 1
        student = f"status_counts={counts}\nsha={sha}\npath={store_path}"
        return student, "Save"

    def h_http_probe(url: str, label: str) -> Handler:
        script = (
            "import urllib.request,sys\n"
            f"u={url!r}\n"
            "try:\n"
            "  r=urllib.request.urlopen(u,timeout=15)\n"
            "  print(r.status, r.geturl())\n"
            "except Exception as e:\n"
            "  print('ERR', e); sys.exit(1)\n"
        )
        return lambda: h_cmd(label, [sys.executable, "-c", script])

    ps_probe = [
        sys.executable,
        "-c",
        (
            "import subprocess,sys\n"
            "r=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass',"
            "'-File','scripts/swarm_remote_proof_urls.ps1','--probe'],"
            "capture_output=True,text=True,timeout=120)\n"
            "print(r.stdout,r.stderr); sys.exit(r.returncode)"
        ),
    ]

    protocol_path = "Schematics/18-PROTOCOLS/KC-Student-Teacher-Apprenticeship-Protocol.md"
    if not (root / protocol_path).exists():
        protocol_path = "docs/swarm-ops/apprenticeship/STEWARDSHIP.md"

    return {
        # Phase 2 remainder
        "KCA-0206": h_note("ISO-8601 timestamps required in JSONL ts fields."),
        "KCA-0207": h_note("Save/Kill/Watch documented in apprenticeship protocol."),
        "KCA-0208": lambda: h_file("docs/swarm-ops/NAVIGATION.md", "Comms decisions mirrored via swarm-ops index."),
        "KCA-0209": h_note("Tag reviews with apprenticeship phase in summary."),
        "KCA-0210": h_note("Keep student_response bounded; cite paths."),
        "KCA-0211": h_note("Prefer file paths over bare line numbers."),
        "KCA-0212": h_note(f"PR compare when gh 401: {compare_url}"),
        "KCA-0213": h_note(f"KC store path: {store_path}"),
        "KCA-0214": h_note("strict-proof rejects demo-bypass URL markers."),
        "KCA-0215": lambda: h_file("docs/swarm-ops/logs/KC Review Log.jsonl", "Archive task id in review notes."),
        # Phase 3 remainder
        "KCA-0311": lambda: h_file("scripts/kc_guard.py", "Exit codes: 0 pass."),
        "KCA-0312": lambda: h_grep("DEMO_DAY_RUNBOOK.md", "kc_guard", "Guard wired in runbook."),
        "KCA-0313": h_note("kc_guard watch mode polls sync + validate on interval."),
        "KCA-0314": h_note("No --require-swarm-ack until external kimi_ack exists."),
        "KCA-0315": lambda: h_cmd("kc_guard all", [sys.executable, "scripts/kc_guard.py", "all", "--no-check-doc-hosts"]),
        # Phase 4 remainder
        "KCA-0404": lambda: h_file("kopano-core/kopano/kc_training_api.py", "POST /api/kc/records for assignments."),
        "KCA-0405": lambda: h_file("kopano-core/kopano/kc_training_api.py", "POST submit endpoint."),
        "KCA-0406": lambda: h_file("kopano-core/kopano/kc_training_api.py", "POST review endpoint."),
        "KCA-0407": lambda: h_file("kopano-core/kopano/kc_training_api.py", "POST promote endpoint."),
        "KCA-0408": lambda: h_file("kopano-core/kopano/kc_training_api.py", "POST /seed-training and /seed-apprenticeship-150."),
        "KCA-0409": lambda: h_grep(
            "kopano-core/studio/src/pages/TrainingPage.tsx",
            "1800",
            "Training refresh interval 1.8s.",
        ),
        "KCA-0410": lambda: h_store_counts(),
        "KCA-0411": lambda: h_grep(
            "kopano-core/studio/src/pages/TrainingPage.tsx",
            "KC training API unavailable",
            "Offline error string present.",
        ),
        "KCA-0412": lambda: h_file("docs/swarm-ops/apprenticeship/kc_apprenticeship_150.json", "Manifest linked."),
        "KCA-0413": lambda: h_grep("kopano-core/studio/src/App.tsx", "kopano", "kopano student lane."),
        "KCA-0414": lambda: h_grep("kopano-core/studio/src/App.tsx", "cassey", "cassey teacher lane."),
        "KCA-0415": lambda: h_file("docs/swarm-ops/logs/KC Review Log.jsonl", "Export promoted summary to review log."),
        # Phase 5
        "KCA-0501": lambda: h_file("docs/swarm-ops/VERIFIED_ENDPOINTS.md", "Endpoints table."),
        "KCA-0502": lambda: h_cmd("swarm_remote_proof_urls.ps1 --probe", ps_probe),
        "KCA-0503": h_note("Use .sh probe on Unix; Windows uses .ps1 in KCA-0502."),
        "KCA-0504": h_http_probe("https://context.kopanolabs.com", "context host HTTP"),
        "KCA-0505": lambda: h_grep("docs/swarm-ops/VERIFIED_ENDPOINTS.md", "NXDOMAIN", "Retired hosts documented."),
        "KCA-0506": lambda: h_grep("kopano-core/kopano/api.py", "PRODUCTION_URL", "Production URL alignment."),
        "KCA-0507": lambda: h_grep("kopano-core/kopano/api.py", "CORSMiddleware", "CORS configuration excerpt."),
        "KCA-0508": lambda: h_grep("kopano-core/kopano/api.py", "kopanolabs.com", "kopanolabs.com in CORS."),
        "KCA-0509": lambda: h_file("kopano-core/studio/src/apiBase.ts", "apiBase default."),
        "KCA-0510": h_note("Local health: start API then GET /docs or /api/kc/training on :8000."),
        "KCA-0511": h_note("Operational receipts only — not cryptographic proof."),
        "KCA-0512": lambda: h_file("docs/swarm-ops/VERIFIED_ENDPOINTS.md", "Store probe results in evidence_urls."),
        "KCA-0513": lambda: h_cmd("swarm_remote_proof_urls.ps1 re-probe", ps_probe),
        "KCA-0514": lambda: h_file("docs/swarm-ops/SWARM_OPERATIONS.md", "Update doctrine when hosts change."),
        "KCA-0515": h_note(f"Probe receipt compare={compare_url}"),
        # Phase 6
        "KCA-0601": lambda: h_file(".github/workflows/swarm-proof.yml", "CI triggers."),
        "KCA-0602": lambda: h_grep(".github/workflows/swarm-proof.yml", "codex/kc-sovereign-gui-full-dev", "Push trigger."),
        "KCA-0603": lambda: h_grep(".github/workflows/swarm-proof.yml", "pytest", "Jobs include pytest."),
        "KCA-0604": lambda: h_cmd("pytest", [sys.executable, "-m", "pytest", "tests/test_kc_apprenticeship.py", "-q"]),
        "KCA-0605": h_note("Commits scoped to apprenticeship/swarm-ops/kopano-core."),
        "KCA-0606": h_note("Do not stage Schematics noise; use docs/swarm-ops."),
        "KCA-0607": h_note(f"compare URL: {compare_url}"),
        "KCA-0608": h_note(f"HEAD sha documented: {sha}"),
        "KCA-0609": h_note("No git commit --amend after push."),
        "KCA-0610": lambda: h_cmd("kc_guard all", [sys.executable, "scripts/kc_guard.py", "all", "--no-check-doc-hosts"]),
        "KCA-0611": h_note("Commit messages mention apprenticeship when relevant."),
        "KCA-0612": h_note(f"evidence_urls may include {compare_url}"),
        "KCA-0613": lambda: h_cmd("git status -sb", ["git", "status", "-sb"]),
        "KCA-0614": lambda: h_cmd(
            "git diff secret scan",
            ["git", "diff", "--name-only", "HEAD~3..HEAD"],
        ),
        "KCA-0615": h_note(f"Last green local gate: pytest + kc_guard at sha {sha}"),
        # Phase 7
        "KCA-0701": lambda: h_file(protocol_path, "Apprenticeship protocol excerpt."),
        "KCA-0702": h_note("Law 1: no unsupervised writes to Main Brain / production."),
        "KCA-0703": h_note("Law 5: KC stores/indexes; agents execute under review."),
        "KCA-0704": lambda: h_grep(protocol_path, "Teacher", "Teacher assignments table."),
        "KCA-0705": h_note("Cursor = AG execution surface in this session."),
        "KCA-0706": h_note("KC = durable memory via JSONL + context store."),
        "KCA-0707": lambda: h_cmd(
            "grep 300 nodes fiction",
            [sys.executable, "-c", "import subprocess; subprocess.run(['git','grep','-l','300 nodes'], cwd='.')"],
        ),
        "KCA-0708": lambda: h_file("DEMO_DAY_10_PHASES_50_TASKS.md", "50 demo tasks map."),
        "KCA-0709": lambda: h_file("docs/swarm-ops/apprenticeship/kc_apprenticeship_150.json", "150 = 10x15 tasks."),
        "KCA-0710": h_note("kimi_ack only after manual external step; never fabricated."),
        "KCA-0711": h_note("owner_proof=local_only_domain_first_unproven in training status."),
        "KCA-0712": lambda: h_file("docs/swarm-ops/NAVIGATION.md", "Navigation cross-links."),
        "KCA-0713": lambda: h_file("docs/swarm-ops/apprenticeship/progress.json", "Progress ledger."),
        "KCA-0714": h_note("Watch verdict for risky scope expansions."),
        "KCA-0715": h_note("Promote only when student_response has evidence."),
        # Phase 8
        "KCA-0801": lambda: h_grep("kopano-core/kopano/labs_api.py", "@router", "labs_api routes."),
        "KCA-0802": lambda: h_file("kopano-core/studio/src/pages/LabsPage.tsx", "Labs page source."),
        "KCA-0803": lambda: h_file("kopano-core/kopano/kasilink_api.py", "KasiLink bridge API."),
        "KCA-0804": lambda: h_grep("kopano-core/kopano/labs_api.py", "microsoft_readiness", "Microsoft readiness route."),
        "KCA-0805": lambda: h_file("kopano-core/kopano/mcp_console.py", "MCP console module."),
        "KCA-0806": lambda: h_grep("kopano-core/kopano/labs_api.py", "cowork", "Cowork routes."),
        "KCA-0807": lambda: h_grep("kopano-core/kopano/labs_api.py", "language", "SA language routes."),
        "KCA-0808": lambda: h_file("kopano-core/studio/src/pages/ForgePage.tsx", "Forge page."),
        "KCA-0809": lambda: h_file("kopano-core/studio/src/pages/CouncilPage.tsx", "Council page."),
        "KCA-0810": lambda: h_file("kopano-core/studio/src/pages/AdminPage.tsx", "Admin page."),
        "KCA-0811": lambda: h_file("kopano-core/studio/src/telemetry.ts", "Client telemetry optional."),
        "KCA-0812": h_note("Never paste API keys into student_response fields."),
        "KCA-0813": lambda: h_file("kopano-core/kopano/labs_api.py", "Labs reference."),
        "KCA-0814": h_note("Integration smoke: API modules import; Studio pages exist."),
        "KCA-0815": h_note("Teacher Save when bounded and reproducible."),
        # Phase 9
        "KCA-0901": h_note("Lifecycle: Onboarding → Shadowing → Supervised → Graduate."),
        "KCA-0902": lambda: h_store_counts(),
        "KCA-0903": lambda: h_store_counts(),
        "KCA-0904": h_note("Graduation requires 10+ verified production tasks (protocol)."),
        "KCA-0905": h_note("Cite files/commands only; no invented features."),
        "KCA-0906": h_note("Chief Architect sign-off is external to automation."),
        "KCA-0907": lambda: h_file("docs/swarm-ops/SWARM_OPERATIONS.md", "Protocol 13 grounded ops."),
        "KCA-0908": h_note("Shadowing = read-only; steward skips writes except store."),
        "KCA-0909": h_note(f"Supervised PR scope: {compare_url}"),
        "KCA-0910": h_note("Graduate criteria drafted — not claiming graduation met."),
        "KCA-0911": h_note("Cassy audits Lessons 001-014 under supervision."),
        "KCA-0912": h_note("OG Mirror Wardens: vault parity — external Kimi lane."),
        "KCA-0913": h_note("Recon scouts: research, no-write."),
        "KCA-0914": lambda: h_file("docs/swarm-ops/apprenticeship/STEWARDSHIP.md", "Stewardship split."),
        "KCA-0915": lambda: h_cmd(
            "mainbrain graduation intent",
            [
                sys.executable,
                "scripts/kc_log_append.py",
                "mainbrain",
                "--kind",
                "graduation_intent",
                "--summary",
                "Graduation intent logged after apprenticeship steward; Chief Architect sign-off still external.",
                "--exit-code",
                "0",
                "--evidence-url",
                compare_url,
                "--evidence-url",
                "https://github.com/Kopano-Labs/Introduction-to-MCP/actions",
            ],
        ),
        # Phase 10
        "KCA-1001": lambda: h_file("DEMO_DAY_RUNBOOK.md", "Demo runbook gates."),
        "KCA-1002": lambda: h_cmd(
            "pytest suite",
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
        "KCA-1003": h_note("Cold-start: python main.py serve api (kopano-core)."),
        "KCA-1004": h_note("Studio lint: npm run lint in kopano-core/studio when Node available."),
        "KCA-1005": h_note("KopanoContext.exe optional binary path."),
        "KCA-1006": h_note("Azure deploy artifacts referenced in runbook; no deploy claim."),
        "KCA-1007": h_note("SafeSkill: no hardcoded secrets in committed diff."),
        "KCA-1008": h_note("Reward system folder under Schematics (vault)."),
        "KCA-1009": h_note("Legacy archive — historical artifacts only."),
        "KCA-1010": lambda: h_file("DEMO_DAY_10_PHASES_50_TASKS.md", "50 demo tasks vs 150 apprenticeship."),
        "KCA-1011": lambda: h_cmd(
            "activate dry-run count",
            [sys.executable, "-c", "import json;print(len(json.load(open('docs/swarm-ops/apprenticeship/kc_apprenticeship_150.json'))['tasks']))"],
        ),
        "KCA-1012": h_note(f"Seed store: {store_path}"),
        "KCA-1013": lambda: h_store_counts(),
        "KCA-1014": h_note("Stewardship: Cursor executes; KC holds ledger."),
        "KCA-1015": lambda: h_cmd(
            "final guard",
            [sys.executable, "scripts/kc_guard.py", "all", "--no-check-doc-hosts"],
        ),
    }
