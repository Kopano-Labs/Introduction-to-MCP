"""
LD operates as LPM — stress ideas under Bracket, BlackMask, BlackMass, TSAP, Guardian/Identi.

Cursor-metal / LD hemisphere: #? hypothesis → protocol stress → #! proof or HOLD.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO_ROOT / "docs" / "swarm-ops" / "LD_LPM_OPERATE.json"
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


def _blackmass_gate() -> dict[str, Any]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from kc_main_brain_roadmap import check_entry_gate

    ok, msg = check_entry_gate()
    return {"check": "blackmass_roadmap_gate", "verdict": "PASS" if ok else "FAIL", "detail": msg}


def stress_idea(
    *,
    idea_id: str,
    action: str,
    evidence: str,
    bracket_tag: str = "[LPM_PROTOCOL]",
    run_blackmask: bool = True,
    agent_id: str = "cassy",
) -> dict[str, Any]:
    """Stress one idea through bracket lint, LPM dialectic, LPH, BlackMask, BlackMass gate."""
    from .blackmask_bracket_stress import run_blackmask_bracket_stress
    from .lpm_lph_engine import attach_lpm_to_mao, lpm_dialectic, select_lph_personality
    from .phu_apprenticeship import blackmask_drill

    checks: list[dict[str, Any]] = []

    receipt_text = f"{bracket_tag} action: {action[:120]} | evidence: {evidence[:120]}"
    bracket_errs = _bracket_lint(receipt_text)
    checks.append(
        {
            "check": "bracket_lint_idea",
            "verdict": "PASS" if not bracket_errs else "FAIL",
            "violations": bracket_errs,
        }
    )

    lph = select_lph_personality(f"{action} {evidence}")
    dialectic = lpm_dialectic(
        imperfect_pattern=f"#? {idea_id}: {action[:80]}",
        perfect_pattern=f"#! measurable proof — {evidence[:80]}",
    )
    mao_attach = attach_lpm_to_mao(f"{action} {evidence}", intent=lph.get("mao_intent", "execute"))
    checks.append(
        {
            "check": "lpm_lph_attach",
            "verdict": "PASS",
            "personality": lph.get("personality_id"),
            "vector": mao_attach.get("kpefs", {}).get("active_vector"),
            "dialectic_closed": dialectic.get("dialectic_closed"),
        }
    )

    if run_blackmask:
        drill = blackmask_drill(agent_id)
        checks.append(
            {
                "check": "blackmask_drill",
                "verdict": "PASS" if drill.get("verdict") == "SHIP" else "FAIL",
                "agent_id": agent_id,
                "summary": drill.get("summary", "")[:120],
            }
        )

    bm_stress = run_blackmask_bracket_stress(write_report=True, operator="LD-LPM")
    checks.append(
        {
            "check": "blackmask_bracket_stress",
            "verdict": bm_stress.get("verdict", "FAIL"),
            "passed": bm_stress.get("passed"),
            "total": bm_stress.get("total"),
        }
    )

    bm_gate = _blackmass_gate()
    checks.append(bm_gate)

    failed = [c["check"] for c in checks if c.get("verdict") == "FAIL"]
    overall = "SHIP" if not failed else "HOLD"

    return {
        "idea_id": idea_id,
        "verdict": overall,
        "failed_checks": failed,
        "checks": checks,
        "lpm": dialectic,
        "lph": lph,
        "mao_attach": mao_attach,
        "bracket_receipt": receipt_text,
    }


def run_ld_lpm_tranche(
    *,
    idea_id: str,
    action: str,
    evidence: str,
    department_id: str = "kopano_labs_experimentation",
    operator: str = "LD-LPM",
    identi_agent: str = "identi_cursor",
    teacher_approve: bool = True,
    write_report: bool = True,
) -> dict[str, Any]:
    """
    Full LD tranche: stress idea → Identi (LPM/LPH) → Guardian (BlackMask + Cassey).
    """
    from .lpm_lph_engine import operate_guardian_flow, operate_identi_flow

    from .kpgs_governance import classify_submission

    telemetry = classify_submission(action=action, evidence=evidence)
    if telemetry.get("blocked"):
        report = {
            "schema": "ld_lpm_operate_v1",
            "ts": _utc_now(),
            "operator": operator,
            "idea_id": idea_id,
            "verdict": "HOLD",
            "reason": "telemetry_routing_gate",
            "telemetry_routing": telemetry,
        }
        if write_report:
            REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return report

    stress = stress_idea(idea_id=idea_id, action=action, evidence=evidence)
    if stress["verdict"] != "SHIP":
        report = {
            "schema": "ld_lpm_operate_v1",
            "ts": _utc_now(),
            "operator": operator,
            "idea_id": idea_id,
            "verdict": "HOLD",
            "reason": "idea_stress_failed",
            "stress": stress,
        }
        if write_report:
            REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return report

    identi = operate_identi_flow(
        department_id=department_id,
        action=action,
        evidence=evidence,
        imperfect_pattern=f"#? {idea_id} unproven",
        perfect_pattern=f"#! {idea_id} under BlackMask + bracket",
        identi_agent=identi_agent,
        submit_to_guardian=False,
    )
    if identi.get("verdict") == "BRACKET_REJECT":
        report = {
            "schema": "ld_lpm_operate_v1",
            "ts": _utc_now(),
            "operator": operator,
            "idea_id": idea_id,
            "verdict": "BRACKET_REJECT",
            "identi": identi,
            "stress": stress,
        }
        if write_report:
            REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return report

    guardian = operate_guardian_flow(
        department_id=department_id,
        action=f"[{operator}] {action}",
        evidence=evidence,
        student_agent="cassy",
        run_blackmask=True,
        teacher_approve=teacher_approve,
        teacher_note=f"LD-LPM tranche {idea_id} — Cassey maps to KC Save|Watch",
    )

    g_verdict = guardian.get("verdict", "HOLD")
    overall = "SHIP" if g_verdict in ("SHIP", "SUBMITTED") else g_verdict

    summary = (
        f"[LPM_PROTOCOL] ld_tranche | operator: {operator} | idea: {idea_id} | "
        f"verdict: {overall} | lph: {stress['lph'].get('personality_id')} | "
        f"[BLACK_MASK_DRILL] guardian: {g_verdict} | [TSAP_PROTOCOL] identi: {identi.get('verdict')}"
    )

    report = {
        "schema": "ld_lpm_operate_v1",
        "ts": _utc_now(),
        "operator": operator,
        "idea_id": idea_id,
        "department_id": department_id,
        "verdict": overall,
        "action": action,
        "evidence": evidence,
        "telemetry_routing": telemetry,
        "stress": stress,
        "identi": {"verdict": identi.get("verdict"), "lph": identi.get("lph", {}).get("personality_id")},
        "guardian": {"verdict": g_verdict},
        "summary": summary,
        "report_path": str(REPORT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "protocols": [
            "BRACKET_PROTOCOL",
            "BLACK_MASK",
            "BLACK_MASS",
            "LPM_PROTOCOL",
            "LPH_PROTOCOL",
            "TSAP_PROTOCOL",
            "GUARDIAN_AI_FLOW",
            "KPGS_TELEMETRY_ROUTE",
        ],
    }

    if write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    _append_jsonl(
        MAIN_BRAIN_LOG,
        {
            "schema": "kc_main_brain_log_v1",
            "ts": _utc_now(),
            "kind": "ld_lpm_operate",
            "operator": operator,
            "summary": summary,
            "exit_code": 0 if overall == "SHIP" else 1,
            "payload_ref": report["report_path"],
        },
    )

    return report
