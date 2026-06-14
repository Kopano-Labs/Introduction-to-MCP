#!/usr/bin/env python3
"""KPGS Agent Initialization — Altar Integration validator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_agent_validate import (  # noqa: E402
    compile_kpgs_thesis,
    execute_altar_gate,
    synthesize_agent_manifest,
    validate_kpgs_agent,
    validate_kpgs_mesh,
)
from kopano.kpgs_telemetry_route import (  # noqa: E402
    classify_telemetry_signal,
    compile_black_beast_thesis,
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("mesh", help="PoC — validate full boot mesh against KPGS core")
    m.add_argument("--json", action="store_true")

    t = sub.add_parser("thesis", help="Compile-check KPGS thesis payload X8020")
    t.add_argument("--json", action="store_true")

    b = sub.add_parser("black-beast", help="Compile-check Black Beast thesis payload V1")
    b.add_argument("--json", action="store_true")

    c = sub.add_parser("classify", help="Classify raw signal before interpretation")
    c.add_argument("signal", help="Raw telemetry text to route")
    c.add_argument("--json", action="store_true")

    v = sub.add_parser("validate", help="Validate one agent manifest")
    v.add_argument("agent_id")
    v.add_argument("payload_path", nargs="?", help="Optional kpgs manifest JSON path")
    v.add_argument("--synthetic", action="store_true", help="Use synthesized mesh manifest")

    s = sub.add_parser("synthesize", help="Print default manifest for agent_id")
    s.add_argument("agent_id")

    args = p.parse_args()

    if args.cmd == "black-beast":
        out = compile_black_beast_thesis()
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(out["summary"])
            if out.get("errors"):
                for e in out["errors"]:
                    print(f"  ERROR: {e}")
        return 0 if out["verdict"] == "COMPILED" else 1

    if args.cmd == "classify":
        out = classify_telemetry_signal(args.signal)
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(out["summary"])
            print(f"  note: {out['note']}")
        return 0 if out["verdict"] != "RECLASSIFY" else 1

    if args.cmd == "thesis":
        out = compile_kpgs_thesis()
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(out["summary"])
            if out.get("errors"):
                for e in out["errors"]:
                    print(f"  ERROR: {e}")
        return 0 if out["verdict"] == "COMPILED" else 1

    if args.cmd == "mesh":
        report = validate_kpgs_mesh()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"KPGS mesh PoC: {report['verdict']}")
            print(f"  agents: {report['agents_total']} SHIP={report['ship']} HOLD={report['hold']} REJECT={report['reject']}")
            print(f"  report: {report['report_path']}")
        return 0 if report["verdict"] == "PASS" else 1

    if args.cmd == "synthesize":
        print(json.dumps(synthesize_agent_manifest(args.agent_id), indent=2))
        return 0

    if args.synthetic or not args.payload_path:
        out = validate_kpgs_agent(args.agent_id)
    else:
        status = execute_altar_gate(args.agent_id, args.payload_path)
        out = validate_kpgs_agent(args.agent_id, manifest_path=args.payload_path)
        print(f"STATUS: {status}")

    print(json.dumps(out, indent=2))
    return 0 if out.get("verdict") == "SHIP" else 1


if __name__ == "__main__":
    raise SystemExit(main())
