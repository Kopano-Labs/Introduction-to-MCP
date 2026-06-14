#!/usr/bin/env python3
"""One command when you return — full gate + closure snapshot + when-back summary."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

PY = sys.executable


def main() -> int:
    p = argparse.ArgumentParser(description="KPEFS run snapshot (when back from a run)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--append-main-brain", action="store_true")
    p.add_argument("--skip-gate", action="store_true", help="Only refresh closure snapshot")
    args = p.parse_args()

    gate_exit = 0
    gate_out = ""
    if not args.skip_gate:
        proc = subprocess.run(
            [PY, str(REPO / "scripts" / "kc_kpefs_full_gate.py"), "--json"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
        )
        gate_exit = proc.returncode
        gate_out = proc.stdout or proc.stderr

    from kopano.external_swarm_lane import write_closure_snapshot

    closure = write_closure_snapshot(append_main_brain=args.append_main_brain)

    payload = {
        "schema": "kpefs_run_snapshot_v1",
        "full_gate_exit_code": gate_exit,
        "full_gate_verdict": None,
        "closure": closure,
    }
    if gate_out.strip():
        try:
            gate_json = json.loads(gate_out)
            payload["full_gate_verdict"] = gate_json.get("verdict")
            payload["full_gate_failed_steps"] = gate_json.get("failed_steps")
        except json.JSONDecodeError:
            payload["full_gate_raw"] = gate_out[:400]

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("KPEFS when-back snapshot")
        print(f"  Full gate: {payload.get('full_gate_verdict') or gate_exit} (exit {gate_exit})")
        print(f"  Internal KPEFS: {closure.get('internal_kpefs_complete')}")
        print(f"  External receipt: {closure.get('external_swarm_receipt')}")
        print(f"  Snapshot: {closure.get('snapshot_path')}")
        if closure.get("next_human_step"):
            print(f"  Next: {closure['next_human_step']}")
        guide = (closure.get("external_swarm") or {}).get("guide") or {}
        if guide.get("cli_template"):
            print(f"  CMD-03: {guide['cli_template']}")

    return gate_exit if gate_exit else (0 if closure.get("internal_kpefs_complete") else 1)


if __name__ == "__main__":
    raise SystemExit(main())
