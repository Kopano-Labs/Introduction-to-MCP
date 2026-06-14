#!/usr/bin/env python3
"""KPEFS full gate — Phases 0-5 operator check (bracket, mesh, graduation, PoC)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

PY = sys.executable


def _run(script: str, *args: str) -> tuple[int, str]:
    proc = subprocess.run(
        [PY, str(REPO / "scripts" / script), *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode, out


def main() -> int:
    p = argparse.ArgumentParser(description="KPEFS Phases 0-5 full gate")
    p.add_argument("--json", action="store_true")
    p.add_argument("--append-main-brain", action="store_true", help="Log kpefs_full_gate receipt")
    args = p.parse_args()

    from kopano.external_swarm_lane import kpefs_closure_status
    from kopano.graduation_bar import graduation_bar_status, lock_kpefs_phases_3_5, record_steward_trust
    from kopano.operating_mesh import operating_mesh_status
    from kopano.agent_build_poc_validate import validate_agent_build_poc

    steps: list[dict] = []

    c1, o1 = _run("kc_bracket_lint.py", "--self-test")
    steps.append({"step": "bracket_lint_self_test", "exit_code": c1, "detail": o1[:200]})

    om = operating_mesh_status()
    steps.append(
        {
            "step": "operating_mesh",
            "exit_code": 0 if om.get("phase3_exit_met") else 1,
            "detail": f"{om.get('operating_count')}/{om.get('flagships_total')}",
            "phase3_exit_met": om.get("phase3_exit_met"),
        }
    )

    gb = graduation_bar_status()
    steps.append(
        {
            "step": "graduation_bar",
            "exit_code": 0 if gb.get("phase5_exit_met") else 1,
            "detail": f"verified={gb.get('verified_production')}/{gb.get('public_graduation_bar')}",
            "phase5_exit_met": gb.get("phase5_exit_met"),
        }
    )

    poc = validate_agent_build_poc(write_report=True)
    steps.append(
        {
            "step": "agent_build_poc",
            "exit_code": 0 if poc.get("verdict") == "PASS" else 1,
            "detail": f"{poc.get('passed')}/{poc.get('total')} {poc.get('verdict')}",
            "failed_checks": poc.get("failed_checks"),
        }
    )

    closure = kpefs_closure_status()
    steps.append(
        {
            "step": "external_swarm_cmd03",
            "exit_code": 0,
            "advisory": True,
            "detail": (
                "receipt_on_file"
                if closure.get("external_swarm_receipt")
                else "manual kimi_ack required (CMD-03)"
            ),
            "full_closure": closure.get("full_closure"),
        }
    )

    failed = [s["step"] for s in steps if s.get("exit_code") != 0]
    overall_ok = not failed

    payload = {
        "schema": "kpefs_full_gate_v1",
        "verdict": "PASS" if overall_ok else "FAIL",
        "failed_steps": failed,
        "steward_lane": gb.get("steward_lane"),
        "steps": steps,
        "poc_report": poc.get("report_path"),
        "closure": closure,
    }

    if overall_ok:
        try:
            from kopano.external_swarm_lane import write_closure_snapshot

            write_closure_snapshot(append_main_brain=args.append_main_brain)
        except ImportError:
            pass

    if args.append_main_brain and overall_ok:
        lock_kpefs_phases_3_5()
        record_steward_trust(note="kpefs_full_gate PASS — phases 0-5")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"KPEFS full gate: {payload['verdict']}")
        for s in steps:
            mark = "ok" if s.get("exit_code") == 0 else "FAIL"
            print(f"  [{mark}] {s['step']}: {s.get('detail')}")
        if failed:
            print(f"Failed: {', '.join(failed)}")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
