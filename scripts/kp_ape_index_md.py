#!/usr/bin/env python3
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
src = REPO / "docs/swarm-ops/agents/KP_APE_200_AGENTS.json"
out = REPO / "docs/swarm-ops/agents/KP_APE_200_AGENTS_INDEX.md"
d = json.loads(src.read_text(encoding="utf-8"))
lines = [
    "# KP + APE — 200 STEM Agents (Index)",
    "",
    "Full JSON: [KP_APE_200_AGENTS.json](./KP_APE_200_AGENTS.json)",
    "",
]
for code, label in (("KP", "Kopano Labs"), ("APE", "Ama-Phu Entertainment")):
    lines.append(f"## {code} — {label} (100 agents)")
    lines.append("")
    lines.append("| # | ID | Name | STEM domain | Functionality |")
    lines.append("|---|-----|------|-------------|---------------|")
    n = 0
    for a in d["agents"]:
        if a["department_code"] != code:
            continue
        n += 1
        fn = a["functionality"].replace("|", "/")
        lines.append(
            f"| {n} | `{a['id']}` | {a['display_name']} | {a['stem_domain']} | {fn} |"
        )
    lines.append("")
out.write_text("\n".join(lines), encoding="utf-8")
print(out)
