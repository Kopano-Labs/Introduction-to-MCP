#!/usr/bin/env python3
"""Inspect and evaluate KC — Kopano Context Legacy runtime packets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.kpgs_legacy import (  # noqa: E402
    evaluate_legacy_impact,
    legacy_packet_template,
    legacy_status,
)


def _print(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show the current KC Legacy runtime contract.")
    sub.add_parser("template", help="Print a minimum impact packet template.")

    evaluate = sub.add_parser(
        "evaluate",
        help="Evaluate a JSON impact packet against the KC Legacy proof boundary.",
    )
    evaluate.add_argument("packet", type=Path, help="Path to a JSON impact packet.")

    args = parser.parse_args(argv)

    if args.command == "status":
        _print(legacy_status())
        return 0
    if args.command == "template":
        _print(legacy_packet_template())
        return 0

    try:
        packet = json.loads(args.packet.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"packet not found: {args.packet}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"invalid packet JSON: {exc}", file=sys.stderr)
        return 2

    result = evaluate_legacy_impact(packet)
    _print(result)
    return 1 if result["disposition"] == "KC_FOC_BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
