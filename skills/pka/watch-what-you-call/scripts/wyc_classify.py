#!/usr/bin/env python3
"""WYC-01 reference classifier.

This utility classifies an already-evidenced failure receipt. It does not infer
causality from temporal order and it intentionally preserves MAYBE.
"""

from __future__ import annotations

import argparse
import json
from enum import StrEnum
from pathlib import Path
from typing import Any


class TriState(StrEnum):
    YES = "yes"
    NO = "no"
    MAYBE = "maybe"


class Classification(StrEnum):
    LEGITIMATE_REGRESSION = "LEGITIMATE_REGRESSION"
    REGRESSION_PLUS_ORCHESTRATION_DEFECT = "REGRESSION_PLUS_ORCHESTRATION_DEFECT"
    PREEXISTING_DEFECT_LEGITIMATELY_DISCOVERED = (
        "PREEXISTING_DEFECT_LEGITIMATELY_DISCOVERED"
    )
    UNRELATED_DEFECT_EXPOSED_BY_ORCHESTRATION_MISTAKE = (
        "UNRELATED_DEFECT_EXPOSED_BY_ORCHESTRATION_MISTAKE"
    )
    CAUSALITY_UNRESOLVED = "CAUSALITY_UNRESOLVED"


def classify(change_caused_defect: TriState, invocation_authorized: TriState) -> Classification:
    """Classify one failure without collapsing unresolved evidence into blame."""

    if TriState.MAYBE in {change_caused_defect, invocation_authorized}:
        return Classification.CAUSALITY_UNRESOLVED

    if change_caused_defect is TriState.YES and invocation_authorized is TriState.YES:
        return Classification.LEGITIMATE_REGRESSION

    if change_caused_defect is TriState.YES and invocation_authorized is TriState.NO:
        return Classification.REGRESSION_PLUS_ORCHESTRATION_DEFECT

    if change_caused_defect is TriState.NO and invocation_authorized is TriState.YES:
        return Classification.PREEXISTING_DEFECT_LEGITIMATELY_DISCOVERED

    if change_caused_defect is TriState.NO and invocation_authorized is TriState.NO:
        return Classification.UNRELATED_DEFECT_EXPOSED_BY_ORCHESTRATION_MISTAKE

    raise AssertionError("unreachable tri-state combination")


def load_receipt(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("receipt root must be a JSON object")
    return data


def classify_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    try:
        change_verdict = TriState(receipt["change_causality"]["verdict"])
        invocation_verdict = TriState(receipt["invocation_causality"]["authorized"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "receipt must contain change_causality.verdict and "
            "invocation_causality.authorized with yes|no|maybe values"
        ) from exc

    result = classify(change_verdict, invocation_verdict)
    enriched = dict(receipt)
    enriched["classification"] = result.value
    return enriched


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify a WYC-01 causal receipt")
    parser.add_argument("receipt", type=Path, help="Path to a WYC-01 JSON receipt")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the classification back to the receipt file",
    )
    args = parser.parse_args()

    enriched = classify_receipt(load_receipt(args.receipt))
    rendered = json.dumps(enriched, indent=2, sort_keys=True) + "\n"

    if args.write:
        args.receipt.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
