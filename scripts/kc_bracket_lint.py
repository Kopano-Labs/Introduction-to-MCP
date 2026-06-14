#!/usr/bin/env python3
"""Bracket linguistic recreation — blasphemy register must not use sacred caps."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REGISTER = REPO / "docs" / "swarm-ops" / "BRACKET_BLASPHEMY_REGISTER.json"
BRACKET_TAG = re.compile(r"\[([^\]]+)\]")


def load_register() -> dict:
    return json.loads(REGISTER.read_text(encoding="utf-8"))


def lint_brackets(text: str, reg: dict | None = None) -> list[str]:
    """Return list of violation messages (empty = ok)."""
    reg = reg or load_register()
    forbidden = reg.get("sacred_forbidden_patterns") or []
    canonical_set = {e["bracket"] for e in reg.get("canonical_bracket_forms", [])}
    errors: list[str] = []

    for match in BRACKET_TAG.finditer(text):
        inner = match.group(1)
        if inner in canonical_set:
            continue
        # Exact sacred forbidden string as whole bracket (e.g. ONE_WORLD_ORDER)
        if inner in forbidden or inner.upper() in {f.upper() for f in forbidden}:
            entry = next(
                (
                    e
                    for e in reg.get("canonical_bracket_forms", [])
                    if inner.upper()
                    in {a.upper() for a in e.get("aliases", [])} | {e["bracket"].upper()}
                ),
                None,
            )
            hint = entry["bracket"] if entry else "see BRACKET_BLASPHEMY_REGISTER.json"
            errors.append(f"Sacred caps blasphemy: [{inner}] — use [{hint}]")
            continue
        # Title Case / mixed honorific for blasphemy aliases (not canonical form)
        for entry in reg.get("canonical_bracket_forms", []):
            bracket = entry["bracket"]
            if inner == bracket:
                continue
            for alias in entry.get("aliases", []):
                if alias.lower() not in inner.lower():
                    continue
                # Reject if looks honored: Title Case words or ALL_CAPS alias
                if inner == inner.upper() and inner != bracket:
                    errors.append(f"ALL_CAPS blasphemy: [{inner}] — use [{bracket}]")
                elif re.search(r"\b[A-Z][a-z]+", inner):
                    errors.append(f"Title Case blasphemy: [{inner}] — use [{bracket}]")

    return errors


def lint_log_summaries(path: Path, limit: int = 50) -> list[str]:
    """Lint summary fields on last N JSONL rows."""
    if not path.is_file():
        return [f"missing log: {path}"]
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and isinstance(obj.get("summary"), str):
                rows.append(obj)
    errors: list[str] = []
    for obj in rows[-limit:]:
        summary = obj["summary"]
        for err in lint_brackets(summary):
            errors.append(f"{path.name} ts={obj.get('ts')}: {err}")
    return errors


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--text", default="", help="Lint inline text")
    p.add_argument("--self-test", action="store_true", help="Run built-in cases")
    p.add_argument(
        "--check-logs",
        action="store_true",
        help="Lint summary in last 50 rows of KC Main + Review logs",
    )
    p.add_argument("--limit", type=int, default=50, help="Rows per log for --check-logs")
    args = p.parse_args()

    if args.check_logs:
        main_log = REPO / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"
        review_log = REPO / "docs" / "swarm-ops" / "logs" / "KC Review Log.jsonl"
        errors = lint_log_summaries(main_log, args.limit) + lint_log_summaries(
            review_log, args.limit
        )
        if errors:
            for e in errors:
                print(e, file=sys.stderr)
            return 1
        print(f"bracket lint logs: pass (last {args.limit} summaries each)")
        return 0

    if args.self_test:
        cases = [
            ("[oNE_wORLD_oRDER] diaspora ok", True),
            ("[ONE_WORLD_ORDER] bad", False),
            ("[KPEFS_FOUR_VECTOR] sacred ok", True),
            ("[elon_mask] withheld ok", True),
            ("[Elon Musk] bad", False),
            ("[silcon_valley] ok", True),
        ]
        failed = 0
        for text, should_pass in cases:
            errs = lint_brackets(text)
            ok = len(errs) == 0
            if ok != should_pass:
                print(f"FAIL: {text!r} errors={errs}", file=sys.stderr)
                failed += 1
            else:
                print(f"ok: {text!r}")
        return 1 if failed else 0

    if not args.text:
        print("Provide --text or --self-test", file=sys.stderr)
        return 2
    errs = lint_brackets(args.text)
    if errs:
        for e in errs:
            print(e, file=sys.stderr)
        return 1
    print("bracket lint: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
