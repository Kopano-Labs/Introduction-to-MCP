#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")

EXPECTED_REPOS = {
    "RobynAwesome/RobynAwesome", "RobynAwesome/Introduction-to-MCP", "RobynAwesome/Project-Jennifer",
    "RobynAwesome/Bookit-5s-Arena", "RobynAwesome/Partial-Knowable-Algebra", "RobynAwesome/claude-code-templates",
    "RobynAwesome/paws-and-potjie", "RobynAwesome/kpgs-morning-engine-core--kmec-", "RobynAwesome/Skills",
    "RobynAwesome/kopano-sovereign-hub", "RobynAwesome/Kopano-Labs-Website", "RobynAwesome/cars4mars-project",
    "RobynAwesome/OmniRoute",
}

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"KPGS-KC FAIL: {message}")

def main() -> None:
    registry = load(ROOT / "sub-membrane-registry.json")
    state = load(ROOT / "dashboard-state.json")
    window = load(ROOT / "weekend-window.json")
    package = load(REPO / "apps/kc-dashboard/package.json")
    app = (REPO / "apps/kc-dashboard/src/App.tsx").read_text(encoding="utf-8")
    css = (REPO / "apps/kc-dashboard/src/styles.css").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    membranes = registry["sub_membranes"]
    repos = [item["repository"] for item in membranes]
    ids = [item["id"] for item in membranes]
    require(len(membranes) == 13, "weekend seed must contain exactly 13 discovered repositories")
    require(set(repos) == EXPECTED_REPOS, "weekend Sub-Membrane set drifted from discovery receipt")
    require(len(repos) == len(set(repos)) and len(ids) == len(set(ids)), "Sub-Membrane ids/repos must be unique")
    require(registry["discovery"]["seeded_count"] == 13, "seeded_count mismatch")

    canonical = [item for item in membranes if item["authority"] == "canonical"]
    require(len(canonical) == 1 and canonical[0]["repository"] == "RobynAwesome/Introduction-to-MCP", "only Introduction-to-MCP may be canonical")
    for item in membranes:
        rev = item["revision"]
        if rev is None:
            require(item["ingestion_state"] == "discovered-pending-pin", f"{item['repository']} missing pin must stay pending")
        else:
            require(bool(HEX40.fullmatch(rev)), f"{item['repository']} revision must be a 40-char commit SHA")
            require(item["ingestion_state"] == "pinned-observed", f"{item['repository']} pinned state mismatch")

    require(window["normalized"]["from"].startswith("2026-08-14"), "window start normalization mismatch")
    require(window["normalized"]["to"].startswith("2026-08-17"), "window end normalization mismatch")

    kc = state["kc"]
    require(kc["role"] == "observer-landlord" and kc["stateful"] is True, "KC role/state mismatch")
    require(kc["can_execute"] is False and kc["can_orchestrate"] is False and kc["can_validate"] is False, "KC authority expanded beyond observer-landlord")
    require(state["mode"] == "snapshot", "dashboard must not fake realtime state")
    require(all(lane["live_receipt"] is False for lane in state["frontier_lanes"]), "live provider state cannot be claimed without receipts")

    require(package["devDependencies"]["typescript"] == "7.0.2", "KC dashboard must pin TypeScript 7.0.2")
    require(package["dependencies"]["react"] == "^19.2.4", "React precedent drift")
    require(package["dependencies"]["vite"] == "^8.1.5", "Vite precedent drift")
    require("SNAPSHOT" in app and "Observer / Landlord" in app, "dashboard must expose freshness and KC role")
    require("prefers-reduced-motion" in css, "reduced-motion fallback is mandatory")
    require("design-first-ui-prompting/SKILL.md" in readme, "design-first skill provenance missing")
    require("web-design/animation-systems/SKILL.md" in readme, "animation skill provenance missing")
    require("three" not in package["dependencies"], "KC dashboard must not add decorative WebGL dependency")

    print("KPGS-KC PASS: 13 Sub-Membranes seeded; KC remains observer-landlord; TS7 dashboard contracts are coherent.")
    print(f"Pinned membranes: {sum(1 for item in membranes if item['revision'])}/13 | mode={state['mode']}")

if __name__ == "__main__":
    main()
