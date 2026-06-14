#!/usr/bin/env python3
"""Eco-Friendly PoC validate — Rosen (M,R) + Δ under 32.8% unemployment doctrine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.eco_poc_validate import poc_doctrine_payload, validate_eco_poc  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Validate Eco-Friendly PoC (internal oracles)")
    p.add_argument("--guide", action="store_true", help="Print doctrine + Rosen tip JSON")
    p.add_argument("--agent-id", default="kp_edu_lab_ops_10")
    p.add_argument("--claim", default="")
    p.add_argument("--model", default="")
    p.add_argument("--relation", default="")
    p.add_argument("--baseline", default="")
    p.add_argument("--observed", default="")
    p.add_argument("--unit", default="")
    p.add_argument("--instrument", default="")
    p.add_argument("--evidence", default="")
    p.add_argument("--exit-code", type=int, default=None)
    p.add_argument("--anticipated-delta", default="")
    p.add_argument("--livelihood", default="", help="Comma-separated LIV-01..LIV-05")
    args = p.parse_args()

    if args.guide:
        print(json.dumps(poc_doctrine_payload(), indent=2))
        return 0

    if not args.claim or not args.model:
        print("Provide --claim and --model (see docs/swarm-ops/ECO_FRIENDLY_POC_GUIDE.md)", file=sys.stderr)
        return 2

    liv = [x.strip() for x in args.livelihood.split(",") if x.strip()]
    result = validate_eco_poc(
        agent_id=args.agent_id,
        claim=args.claim,
        model=args.model,
        relation=args.relation,
        baseline=args.baseline,
        observed=args.observed,
        unit=args.unit,
        instrument=args.instrument,
        evidence=args.evidence,
        exit_code=args.exit_code,
        livelihood_ids=liv or None,
        anticipated_delta=args.anticipated_delta,
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
