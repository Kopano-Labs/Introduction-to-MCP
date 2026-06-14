"""
Heavy BlackMask + bracket protocol stress test — CF comms tranche abilities probe.

Exercises:
- Expanded bracket lint matrix (sacred caps reject, canonical accept)
- Log summary lint (Main Brain + Review)
- Live BlackMask drill on full boot mesh
- Failure injection (partial commandments → HOLD)
- Dry-run mesh sweep
- promotion_allowed per operating flagship
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO_ROOT / "docs" / "swarm-ops" / "BLACKMASK_BRACKET_STRESS.json"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
SCRIPTS = REPO_ROOT / "scripts"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _bracket_lint(text: str) -> list[str]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from kc_bracket_lint import lint_brackets

    return lint_brackets(text)


def _bracket_heavy_matrix() -> list[dict[str, Any]]:
    """Expanded cases beyond kc_bracket_lint --self-test."""
    return [
        {"text": "[oNE_wORLD_oRDER] diaspora vector ok", "expect_ok": True, "tag": "canonical_owo"},
        {"text": "[ONE_WORLD_ORDER] sacred bad", "expect_ok": False, "tag": "sacred_owo"},
        {"text": "[One World Order] title case bad", "expect_ok": False, "tag": "title_owo"},
        {"text": "[elon_mask] withheld", "expect_ok": True, "tag": "canonical_elon"},
        {"text": "[Elon Musk] honorific bad", "expect_ok": False, "tag": "title_elon"},
        {"text": "[silcon_valley] typo canonical", "expect_ok": True, "tag": "canonical_sv"},
        {"text": "[Silicon Valley] sacred bad", "expect_ok": False, "tag": "sacred_sv"},
        {"text": "[KPEFS_FOUR_VECTOR] doctrine ok", "expect_ok": True, "tag": "kpefs"},
        {"text": "[BLACK_MASK_DRILL] agent: cassy | verdict: SHIP", "expect_ok": True, "tag": "blackmask"},
        {"text": "[TSAP_PROTOCOL] lane: mcp | verdict: SUBMITTED", "expect_ok": True, "tag": "tsap"},
        {"text": "[GUARDIAN_AI_FLOW] verdict: SHIP", "expect_ok": True, "tag": "guardian"},
        {"text": "[IDENTI_AI_FLOW] verdict: PROPOSE", "expect_ok": True, "tag": "identi"},
        {"text": "[KPEFS_STEWARD_LANE] KC Save|Watch", "expect_ok": True, "tag": "steward"},
        {"text": "mixed [je] and [KPEFS_GRADUATION_BAR] ok", "expect_ok": True, "tag": "mixed_canonical"},
        {"text": "[JEFFREY_EPSTEIN] all caps bad", "expect_ok": False, "tag": "sacred_je"},
        {
            "text": "[GOD_COMPLEX] #?: imperfect | #!: perfect | lph_birth: witness",
            "expect_ok": True,
            "tag": "lpm_god",
        },
    ]


def run_blackmask_bracket_stress(
    *,
    write_report: bool = True,
    operator: str = "CF_cloud",
) -> dict[str, Any]:
    from .operating_mesh import FLAGSHIP_ASSIGNMENTS
    from .phu_apprenticeship import blackmask_drill, load_black_mask_doctrine
    from .phu_boot_governance import blackmask_dry_run, mesh_agent_ids, promotion_allowed

    checks: list[dict[str, Any]] = []

    # ── Bracket heavy matrix ──
    matrix = _bracket_heavy_matrix()
    bracket_failures: list[str] = []
    for case in matrix:
        errs = _bracket_lint(case["text"])
        ok = (len(errs) == 0) == case["expect_ok"]
        if not ok:
            bracket_failures.append(f"{case['tag']}: expected_ok={case['expect_ok']} errs={errs}")
    checks.append(
        {
            "check": "bracket_heavy_matrix",
            "verdict": "PASS" if not bracket_failures else "FAIL",
            "total": len(matrix),
            "failed": bracket_failures,
        }
    )

    # ── Log summaries ──
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from kc_bracket_lint import lint_log_summaries

    main_log = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
    review_log = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Review Log.jsonl"
    log_errs = lint_log_summaries(main_log, 80) + lint_log_summaries(review_log, 80)
    checks.append(
        {
            "check": "bracket_log_summaries_80",
            "verdict": "PASS" if not log_errs else "FAIL",
            "errors": log_errs[:20],
            "error_count": len(log_errs),
        }
    )

    # ── BlackMask live mesh sweep ──
    mesh_ids = mesh_agent_ids()
    live_results: list[dict[str, Any]] = []
    for aid in mesh_ids:
        live_results.append(blackmask_drill(aid))
    live_ship = sum(1 for r in live_results if r.get("verdict") == "SHIP")
    live_hold = len(live_results) - live_ship
    checks.append(
        {
            "check": "blackmask_live_mesh",
            "verdict": "PASS" if live_hold == 0 else "FAIL",
            "agents_total": len(live_results),
            "ship": live_ship,
            "hold": live_hold,
            "hold_agents": [r["agent_id"] for r in live_results if r.get("verdict") != "SHIP"],
        }
    )

    # ── Failure injection ──
    doctrine = load_black_mask_doctrine()
    cmd_ids = [c["id"] for c in doctrine.get("commandments", [])]
    pil_ids = [p["id"] for p in doctrine.get("pillars", [])]
    partial = blackmask_drill(
        "stress_probe_partial",
        commandments_ack=cmd_ids[:3],
        pillars_ack=pil_ids[:1],
    )
    # Empty list defaults to full ack in drill — use explicit no-match ids for zero-ack probe.
    zero_ack = blackmask_drill(
        "stress_probe_zero_ack",
        commandments_ack=["__stress_zero_cmd__"],
        pillars_ack=["__stress_zero_pil__"],
    )
    injection_ok = partial.get("verdict") == "HOLD" and zero_ack.get("verdict") == "HOLD"
    checks.append(
        {
            "check": "blackmask_failure_injection",
            "verdict": "PASS" if injection_ok else "FAIL",
            "partial_verdict": partial.get("verdict"),
            "zero_ack_verdict": zero_ack.get("verdict"),
        }
    )

    # ── Dry run ──
    dry = blackmask_dry_run(agent_ids=mesh_ids)
    checks.append(
        {
            "check": "blackmask_dry_run_mesh",
            "verdict": "PASS" if dry.get("all_ship") else "FAIL",
            "ship": dry.get("ship"),
            "hold": dry.get("hold"),
            "agents_total": dry.get("agents_total"),
        }
    )

    # ── Governance core + flagships ──
    for core in ("cassy", "cassey", "kc"):
        if core == "kc":
            continue  # KC ledger-only — no BlackMask execute lane
        r = blackmask_drill(core)
        checks.append(
            {
                "check": f"blackmask_core_{core}",
                "verdict": "PASS" if r.get("verdict") == "SHIP" else "FAIL",
                "agent_id": core,
                "summary": r.get("summary", "")[:120],
            }
        )

    promo_rows: list[dict[str, Any]] = []
    for fid in FLAGSHIP_ASSIGNMENTS:
        promo_rows.append(promotion_allowed(fid))
    promo_allowed_count = sum(1 for p in promo_rows if p.get("promotion_allowed"))
    checks.append(
        {
            "check": "promotion_allowed_flagships",
            "verdict": "PASS",
            "flagships_total": len(promo_rows),
            "promotion_allowed": promo_allowed_count,
            "note": "Informational — operating mesh may already satisfy checks",
            "sample": promo_rows[:3],
        }
    )

    # ── Polluted student action lint (abilities gate) ──
    polluted = _bracket_lint("[ONE_WORLD_ORDER] fake receipt")
    reject_ok = len(polluted) > 0
    checks.append(
        {
            "check": "bracket_rejects_sacred_submit",
            "verdict": "PASS" if reject_ok else "FAIL",
            "violations": polluted,
        }
    )

    failed = [c["check"] for c in checks if c["verdict"] == "FAIL"]
    overall = "PASS" if not failed else "FAIL"

    report = {
        "schema": "blackmask_bracket_stress_v1",
        "ts": _utc_now(),
        "operator": operator,
        "tranche": "Main Brain audit → KC → Cassy → BlackMask heavy stress",
        "bracket": "[BLACK_MASK_DRILL] [TSAP_PROTOCOL] [KPEFS_STEWARD_LANE]",
        "verdict": overall,
        "passed": sum(1 for c in checks if c["verdict"] == "PASS"),
        "total": len(checks),
        "failed_checks": failed,
        "mesh_agents_drilled": len(mesh_ids),
        "bracket_matrix_size": len(matrix),
        "checks": checks,
        "report_path": str(REPORT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "cf_dispatch": f"@{operator} → LD: Heavy BlackMask + bracket stress — abilities probe complete.",
    }

    if write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        summary = (
            f"[BLACK_MASK_DRILL] stress_test | verdict: {overall} | "
            f"checks: {report['passed']}/{report['total']} | "
            f"mesh: {len(mesh_ids)} SHIP={live_ship} HOLD={live_hold} | "
            f"bracket_matrix: {len(matrix)} | "
            f"[TSAP_PROTOCOL] {operator} bracket protocol heavy stress"
        )
        _append_jsonl(
            MAIN_BRAIN_LOG,
            {
                "schema": "kc_main_brain_log_v1",
                "ts": _utc_now(),
                "kind": "blackmask_bracket_stress",
                "operator": operator,
                "summary": summary,
                "exit_code": 0 if overall == "PASS" else 1,
                "payload_ref": report["report_path"],
            },
        )

    return report
