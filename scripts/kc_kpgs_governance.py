#!/usr/bin/env python3
"""KPGS governance — Schematics MAIN BRAIN compile, status, propagate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_governance import (  # noqa: E402
    compile_kpgs_governance,
    governance_status,
    propagate_governance_marker,
)
from kopano.kpgs_renter_entry import (  # noqa: E402
    assert_and_log_entry,
    block_holder_brief,
    hood_entry_assertion,
    load_altar_block_holders,
    load_renter_entryway,
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("compile", help="Compile full KPGS governance stack")
    sub.add_parser("status", help="Governance status (boot API shape)")
    sub.add_parser("propagate", help="Compile + log + Schematics comms marker")

    e = sub.add_parser("entry", help="Stateless renter hood entry — who you are fucking with")
    e.add_argument("--renter-id", default="anonymous_stateless_renter")
    e.add_argument("--renter-class", default="linguistic_actor")
    e.add_argument("--assert", dest="hood_assert", action="store_true", help="Require hood_ack and log entry")

    bh = sub.add_parser("block-holders", help="List KPGS altar block holders and mesh brief duty")
    bh.add_argument("--agent-id", default="", help="Single agent brief (default: all mesh + altar proxies)")

    args = p.parse_args()
    if args.cmd == "compile":
        out = compile_kpgs_governance()
    elif args.cmd == "status":
        out = governance_status()
    elif args.cmd == "entry":
        if args.hood_assert:
            from kopano.kpgs_renter_entry import HOOD_ACK_LITERAL  # noqa: E402

            out = assert_and_log_entry(
                renter_id=args.renter_id,
                renter_class=args.renter_class,
                hood_ack=HOOD_ACK_LITERAL,
            )
        else:
            out = hood_entry_assertion(renter_id=args.renter_id, renter_class=args.renter_class)
        print(json.dumps(out, indent=2))
        return 0
    elif args.cmd == "block-holders":
        from kopano.phu_boot_governance import mesh_agent_ids  # noqa: E402

        registry = load_altar_block_holders()
        if args.agent_id:
            aids = [args.agent_id]
        else:
            aids = sorted(set(mesh_agent_ids()) | {"mirror_warden", "operational_general"})
        briefs = [block_holder_brief(agent_id=aid) for aid in aids]
        out = {
            "schema": "kpgs_block_holders_report_v1",
            "registry": registry.get("_source"),
            "altar_layers": registry.get("altar_layers", []),
            "agents": briefs,
        }
        print(json.dumps(out, indent=2))
        return 0
    else:
        out = propagate_governance_marker()

    print(json.dumps(out, indent=2))
    verdict = out.get("verdict") or out.get("compile_verdict")
    if verdict == "INCOMPLETE":
        return 1
    if args.cmd == "compile" and out.get("verdict") != "COMPILED":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
