#!/usr/bin/env python3
"""Infinite Hood — cloud territory compile, domain grid, outer API status."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.infinite_hood_cloud import (  # noqa: E402
    build_deployment_manifest,
    compile_infinite_hood,
    hood_dispatch_for_plot,
    infinite_hood_status,
    load_deployment_manifest,
    load_domain_grid,
    outer_api_surface,
    write_deployment_manifest,
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Infinite Hood + domain grid status")
    sub.add_parser("compile", help="Compile spawn + write deployment manifest")
    sub.add_parser("generate", help="Regenerate INFINITE_HOOD_DEPLOYMENT.json")
    sub.add_parser("outer-api", help="Outer API client ingress map")
    sub.add_parser("grid", help="Print domain grid inventory")

    d = sub.add_parser("dispatch", help="Hood dispatch through plot landlord")
    d.add_argument("--plot-id", required=True)
    d.add_argument("message")

    args = p.parse_args()

    if args.cmd == "generate":
        script = REPO / "scripts" / "generate_infinite_hood_grid.py"
        subprocess.run([sys.executable, str(script)], check=True, cwd=REPO)
        return 0

    if args.cmd == "status":
        out = infinite_hood_status()
    elif args.cmd == "compile":
        out = compile_infinite_hood()
    elif args.cmd == "outer-api":
        out = outer_api_surface()
    elif args.cmd == "grid":
        out = load_domain_grid()
    elif args.cmd == "dispatch":
        out = hood_dispatch_for_plot(plot_id=args.plot_id, message=args.message)
    else:
        out = {"error": "unknown_cmd"}

    payload = json.dumps(out, indent=2, ensure_ascii=False)
    sys.stdout.buffer.write(payload.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")
    verdict = out.get("verdict")
    return 0 if verdict in ("COMPILED", "READY", None) else 1


if __name__ == "__main__":
    raise SystemExit(main())
