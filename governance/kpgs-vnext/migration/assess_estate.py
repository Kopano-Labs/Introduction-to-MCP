#!/usr/bin/env python3
"""Assess the canonical estate for migration readiness without mutating it."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
MIGRATION_PATH = ROOT / "governance/kpgs-vnext/migration/migration.py"
ESTATE_PATH = ROOT / "governance/kpgs-vnext/estate-registry/estate.json"


def load_migration_module():
    spec = importlib.util.spec_from_file_location("kpgs_estate_migration", MIGRATION_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load migration runtime")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--estate", type=Path, default=ESTATE_PATH)
    parser.add_argument("--workflow-id", default="bounded-pilot")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    migration = load_migration_module()
    estate = json.loads(args.estate.read_text(encoding="utf-8"))
    assessments = migration.assess_estate(estate, workflow_id=args.workflow_id)
    payload = {
        "schema": "kpgs.estate-migration-estate-assessment.v1",
        "estate_id": estate["estate_id"],
        "workflow_id": args.workflow_id,
        "assessments": assessments,
        "canonical_registry_changed": False,
        "authority_effect": "none",
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

    # Current canonical estate is allowed to be all HOLD. This CLI is an assessor,
    # not a deployment gate that fabricates witness data.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
