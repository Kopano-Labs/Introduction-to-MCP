#!/usr/bin/env python3
"""Build an ephemeral operating-mesh proof state for CI.

Fresh GitHub runners do not inherit local `.kc` state.  A phase gate that reads
that mutable state without first producing it is FOC: it tests somebody else's
machine history, not the checked-out commit.  This script executes the existing
promotion chain on the ephemeral runner and requires all flagship proof chains
to reach `operating` before later validators inspect Phase 3.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.operating_mesh import FLAGSHIP_ASSIGNMENTS, promote_all_flagships


def main() -> int:
    result = promote_all_flagships(skip_if_operating=False)
    expected = len(FLAGSHIP_ASSIGNMENTS)
    operating = int(result.get("operating", 0))
    payload = {
        "schema": "ci_operating_mesh_bootstrap_v1",
        "expected": expected,
        "operating": operating,
        "incomplete": int(result.get("incomplete", expected)),
        "phase3_exit_met": bool(result.get("phase3_exit_met")),
        "verdict": "PASS" if operating == expected and result.get("phase3_exit_met") else "FAIL",
        "results": result.get("results", []),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
