#!/usr/bin/env python3
"""Record governed KPGS/MMAO agent failure receipts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.agent_failure_training import (  # noqa: E402
    build_failure_receipt,
)

DEFAULT_LEDGER = REPO / "docs" / "swarm-ops" / "logs" / "Agent Failure Receipts.jsonl"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object")
    return payload


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create immutable KPGS agent-failure receipts from JSON input"
    )
    parser.add_argument("input", type=Path, help="JSON input containing the failure event")
    parser.add_argument(
        "--ledger",
        type=Path,
        default=DEFAULT_LEDGER,
        help="JSONL receipt ledger path",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the normalized receipt without appending to the ledger",
    )
    args = parser.parse_args()

    raw = _load_json(args.input)
    receipt = build_failure_receipt(**raw)
    payload = receipt.to_dict()

    if not args.dry_run:
        _append_jsonl(args.ledger, payload)

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
