#!/usr/bin/env python3
"""Generate Infinite Hood domain-sharded deployment manifest from domain grid + 300 spawn agents."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.infinite_hood_cloud import (  # noqa: E402
    build_deployment_manifest,
    load_domain_grid,
    write_deployment_manifest,
)

OUT = REPO / "docs" / "swarm-ops" / "INFINITE_HOOD_DEPLOYMENT.json"


def main() -> int:
    grid = load_domain_grid()
    manifest = build_deployment_manifest()
    path = write_deployment_manifest(manifest)
    print(
        f"Infinite Hood deployment: verdict={manifest.get('verdict')} | "
        f"plots={manifest.get('plots_total')} | agents={manifest.get('agents_assigned')} | "
        f"landlords={manifest.get('landlords_assigned')} -> {path}"
    )
    if manifest.get("verdict") != "READY":
        print(json.dumps({"by_role": manifest.get("by_role"), "unassigned": manifest.get("agents_unassigned")}, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
