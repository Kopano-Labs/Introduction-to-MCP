#!/usr/bin/env python3
"""KPGS 300-Agent Spawn Swarm — generate, validate, SWFUS envelope, status."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_spawn_swarm import (  # noqa: E402
    compile_spawn_swarm,
    forensic_sociology_classify,
    jethro_triage,
    load_spawn_catalog,
    load_spawn_doctrine,
    spawn_swarm_status,
    swfus_envelope,
    validate_spawn_agent,
    validate_spawn_swarm,
    wwjd_firewall,
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Spawn swarm status")
    sub.add_parser("compile", help="Compile + validate all 300 spawn agents")
    sub.add_parser("generate", help="Regenerate KPGS_SPAWN_300_AGENTS.json from KP_APE + juniors")

    v = sub.add_parser("validate", help="Validate spawn agents")
    v.add_argument("--agent-id", default="", help="Single agent (default: full swarm)")
    v.add_argument("--sample", action="store_true", help="Structural + first 10 only")

    f = sub.add_parser("forensic", help="Forensic sociology classify a message")
    f.add_argument("message")
    f.add_argument("--agent-id", default="spawn_junior_205")

    j = sub.add_parser("jethro", help="Jethro triage for agent + task")
    j.add_argument("--agent-id", required=True)
    j.add_argument("task")

    w = sub.add_parser("wwjd", help="WWJD firewall on action")
    w.add_argument("action")
    w.add_argument("--evidence", default="")

    s = sub.add_parser("swfus", help="SWFUS envelope for agent + prompt")
    s.add_argument("--agent-id", required=True)
    s.add_argument("prompt")

    sub.add_parser("doctrine", help="Print spawn altar doctrine")
    sub.add_parser("catalog", help="Print spawn catalog counts")

    args = p.parse_args()

    if args.cmd == "generate":
        script = REPO / "scripts" / "generate_kpgs_spawn_300.py"
        subprocess.run([sys.executable, str(script)], check=True, cwd=REPO)
        return 0

    if args.cmd == "status":
        out = spawn_swarm_status()
    elif args.cmd == "compile":
        out = compile_spawn_swarm()
    elif args.cmd == "validate":
        if args.agent_id:
            out = validate_spawn_agent(args.agent_id)
        else:
            out = validate_spawn_swarm(write_report=True, sample_only=args.sample)
    elif args.cmd == "forensic":
        out = forensic_sociology_classify(message=args.message, agent_id=args.agent_id)
    elif args.cmd == "jethro":
        out = jethro_triage(agent_id=args.agent_id, task=args.task)
    elif args.cmd == "wwjd":
        out = wwjd_firewall(action=args.action, evidence=args.evidence)
    elif args.cmd == "swfus":
        out = swfus_envelope(agent_id=args.agent_id, prompt=args.prompt)
    elif args.cmd == "doctrine":
        out = load_spawn_doctrine()
    elif args.cmd == "catalog":
        out = load_spawn_catalog()
    else:
        return 1

    print(json.dumps(out, indent=2))
    if args.cmd == "compile" and out.get("verdict") != "COMPILED":
        return 1
    if args.cmd == "validate" and not args.agent_id and out.get("verdict") != "PASS":
        return 1
    if args.cmd == "validate" and args.agent_id and out.get("verdict") != "SHIP":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
