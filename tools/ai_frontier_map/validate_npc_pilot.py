#!/usr/bin/env python3
"""Validate NPC AI pilot manifest execution and reuse invariants."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RUN_STATES = {
    "ISOLATED_PILOT",
    "ENGINE_SANDBOX_ONLY",
    "NONCOMMERCIAL_SANDBOX_ONLY",
    "STUDY_ONLY",
    "BLOCKED",
}
REUSE_MODES = {"code_reuse", "architectural_reuse", "research_only"}
PERMISSIVE = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC"}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()

    for idx, item in enumerate(data.get("candidates", []), 1):
        prefix = f"candidate[{idx}] {item.get('id')!r}: "
        cid = item.get("id")
        if not cid:
            errors.append(prefix + "missing id")
            continue
        if cid in seen:
            errors.append(prefix + "duplicate id")
        seen.add(cid)

        for required in (
            "lane", "upstream_repo", "provenance", "license", "primitive",
            "reuse_mode", "run_state", "reason", "source_url",
        ):
            if not item.get(required):
                errors.append(prefix + f"missing {required}")

        state = item.get("run_state")
        if state not in RUN_STATES:
            errors.append(prefix + f"invalid run_state {state!r}")

        mode = item.get("reuse_mode")
        if mode not in REUSE_MODES:
            errors.append(prefix + f"invalid reuse_mode {mode!r}")

        licence = item.get("license")
        if mode == "code_reuse" and licence not in PERMISSIVE:
            errors.append(prefix + "code_reuse requires a reviewed permissive licence")

        if licence and "Noncommercial" in licence and mode != "research_only":
            errors.append(prefix + "non-commercial licence must remain research_only")
        if licence and "Noncommercial" in licence and state != "NONCOMMERCIAL_SANDBOX_ONLY":
            errors.append(prefix + "non-commercial licence requires NONCOMMERCIAL_SANDBOX_ONLY")

        if state == "ENGINE_SANDBOX_ONLY" and item.get("lane") != "world_actuation":
            errors.append(prefix + "ENGINE_SANDBOX_ONLY is reserved for world_actuation effectors")

        url = item.get("source_url", "")
        if not url.startswith("https://github.com/"):
            errors.append(prefix + "source_url must be an upstream GitHub provenance URL")

        if item.get("provenance") == "oya_native_fork":
            if not item.get("observed_repo", "").startswith("OyaAIProd/"):
                errors.append(prefix + "oya_native_fork requires observed OyaAIProd repo")
            if not item.get("observed_repo_id"):
                errors.append(prefix + "oya_native_fork requires stable observed_repo_id")

    if not data.get("candidates"):
        errors.append("manifest has no candidates")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "manifest",
        nargs="?",
        default="data/ai-frontier-map/npc-pilot-candidates.json",
    )
    args = ap.parse_args()

    path = Path(args.manifest)
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        print("\n".join(errors))
        print(f"FAILED: {len(errors)} NPC pilot invariant error(s)")
        return 1

    candidates = data["candidates"]
    runnable = sum(
        1 for item in candidates
        if item["run_state"] in {"ISOLATED_PILOT", "ENGINE_SANDBOX_ONLY", "NONCOMMERCIAL_SANDBOX_ONLY"}
    )
    print(f"PASS: {len(candidates)} NPC candidates; {runnable} gated sandbox candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
