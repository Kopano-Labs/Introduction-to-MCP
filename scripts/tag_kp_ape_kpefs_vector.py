#!/usr/bin/env python3
"""Add kpefs_vector to each agent in KP_APE_200_AGENTS.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AGENTS_PATH = REPO / "docs" / "swarm-ops" / "agents" / "KP_APE_200_AGENTS.json"
KROOT = REPO / "kopano-core"
sys.path.insert(0, str(KROOT))

from kopano.kpefs_router import vector_for_stem_domain  # noqa: E402


def main() -> int:
    doc = json.loads(AGENTS_PATH.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    for agent in doc.get("agents", []):
        dept = agent.get("department_code", "KP")
        vec = vector_for_stem_domain(agent.get("stem_domain", ""), dept)
        agent["kpefs_vector"] = vec
        counts[vec] = counts.get(vec, 0) + 1
    doc["kpefs_vector_tagged_at"] = "batch_tag_v1"
    AGENTS_PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Tagged {len(doc.get('agents', []))} agents:")
    for vid, n in sorted(counts.items()):
        print(f"  {vid}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
