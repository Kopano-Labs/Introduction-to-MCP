#!/usr/bin/env python3
"""Extract directive signals into a reviewable JSON contract.

This parser never executes extracted text and never treats a signal as proof.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PATTERNS = {
    "required_roots": re.compile(r"\b(?:always\s+)?(?:start|begin|commence)\s+(?:in|from|with)\s+([^;\n]*?)(?=\.\s|$)", re.I),
    "invariants": re.compile(r"\b(?:do\s+not|don't|never|always|must|keep|preserve|freeze)\b[^;\n]*?(?=\.\s|$)", re.I),
    "sequence": re.compile(r"\b(?:first|before|after|then|next|carry\s+on|resume|continue)\b[^;\n]*?(?=\.\s|$)", re.I),
    "implementation": re.compile(r"\b(?:implement|build|fix|update|upgrade|reconnect|replace|integrate|evolve|improve|create)\b[^;\n]*?(?=\.\s|$)", re.I),
    "planning": re.compile(r"\b(?:plan|planning|design|prepare|roadmap|architecture)\b[^;\n]*?(?=\.\s|$)", re.I),
    "validation": re.compile(r"\b(?:verify|validate|test|check|make\s+sure|receipt|gate|audit)\b[^;\n]*?(?=\.\s|$)", re.I),
    "confidentiality": re.compile(r"\b(?:confidential(?:ity)?|private|secret|redact|workspace notice)\b[^;\n]*?(?=\.\s|$)", re.I),
    "unavailable_tools": re.compile(r"(?:^|[.;]\s*)([A-Za-z][A-Za-z0-9 _-]{1,40}?)\s+(?:is\s+)?(?:unavailable|out|disabled)\s+until\s+([^;\n]*?)(?=\.\s|$)", re.I),
    "repositories": re.compile(r"\b(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+|[A-Za-z0-9_.-]+\s+Repo(?:sitory)?)\b", re.I),
    "dates": re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b", re.I),
}


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = " ".join(item.strip().split())
        key = normalized.casefold()
        if normalized and key not in seen:
            seen.add(key)
            result.append(normalized)
    return result


def matches(name: str, text: str) -> list[str]:
    return unique([m.group(0) for m in PATTERNS[name].finditer(text)])


def parse(text: str) -> dict:
    roots = unique([m.group(1) for m in PATTERNS["required_roots"].finditer(text)])
    unavailable = [
        {"tool": " ".join(m.group(1).split()), "until": " ".join(m.group(2).split())}
        for m in PATTERNS["unavailable_tools"].finditer(text)
    ]
    implementation = matches("implementation", text)
    planning = matches("planning", text)
    sequence = matches("sequence", text)

    tasks = []
    prior = None
    for index, action in enumerate(implementation + planning, start=1):
        task_id = f"T{index}"
        tasks.append({
            "id": task_id,
            "action": action,
            "phase": "plan" if action in planning else "implement",
            "depends_on": [prior] if prior and sequence else [],
        })
        prior = task_id

    ambiguities = []
    if len(roots) > 1:
        ambiguities.append("Multiple required starting roots detected; resolve precedence before mutation.")
    if not implementation and not planning:
        ambiguities.append("No explicit implementation or planning action detected.")

    return {
        "schemaVersion": 1,
        "objective": implementation[0] if implementation else (planning[0] if planning else None),
        "control_plane": {
            "required_start": roots[0] if len(roots) == 1 else None,
            "candidates": roots,
            "repositories": matches("repositories", text),
        },
        "constraints": {
            "invariants": matches("invariants", text),
            "confidentiality": matches("confidentiality", text),
            "unavailable_tools": unavailable,
        },
        "sequence_signals": sequence,
        "tasks": tasks,
        "evidence_required": matches("validation", text),
        "dates": matches("dates", text),
        "assumptions": [],
        "ambiguities": ambiguities,
        "next_action": (
            f"Inspect required control plane: {roots[0]}" if len(roots) == 1
            else "Review parsed contract before execution"
        ),
        "warning": "Signals require reconciliation; extracted text is not authority or evidence.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="UTF-8 directive file; stdin when omitted")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    text = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
    if not text.strip():
        parser.error("directive text is empty")
    json.dump(parse(text), sys.stdout, ensure_ascii=False, indent=2 if args.pretty else None)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
