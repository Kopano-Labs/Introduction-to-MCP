#!/usr/bin/env python3
"""Structural and executable gate for KPGS Frontier Harness v0.1."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def load_json(name: str) -> Any:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"KPGS-FRONTIER FAIL: {message}")


def validate_schema(name: str, required: set[str]) -> dict[str, Any]:
    schema = load_json(name)
    require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", f"{name} must use draft 2020-12")
    require(schema.get("type") == "object", f"{name} root must be object")
    require(schema.get("additionalProperties") is False, f"{name} must reject undeclared root properties")
    declared = set(schema.get("required", []))
    require(required <= declared, f"{name} missing required fields: {sorted(required - declared)}")
    require(declared <= set(schema.get("properties", {})), f"{name} requires undeclared properties")
    return schema


def load_harness():
    spec = importlib.util.spec_from_file_location("kpgs_frontier_harness", ROOT / "frontier_harness.py")
    require(spec is not None and spec.loader is not None, "frontier_harness.py must be importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    request_schema = validate_schema(
        "capability-request.schema.json",
        {"schema_version", "request_id", "created_at", "source", "capability", "policy", "semantic_input"},
    )
    receipt_schema = validate_schema(
        "capability-receipt.schema.json",
        {"schema_version", "receipt_id", "request_id", "created_at", "router_decision", "provider_result", "evaluation", "analytics_copy", "public_anchor", "boundaries"},
    )
    modality_schema = validate_schema(
        "modality-contract.schema.json",
        {"schema_version", "contract_id", "request_id", "semantic_ref", "primary", "renderers", "fallbacks", "accessibility", "renderer_has_semantic_authority"},
    )
    anchor_schema = validate_schema(
        "anchor-intent.schema.json",
        {"schema_version", "intent_id", "request_id", "network", "commitment", "status", "contains_private_data", "payload"},
    )

    require(request_schema["properties"]["source"]["properties"]["trust"].get("const") == "untrusted-input", "intake must remain untrusted")
    require(receipt_schema["properties"]["provider_result"]["properties"]["canonical"].get("const") is False, "provider output cannot self-canonicalize")
    require(receipt_schema["properties"]["evaluation"]["properties"]["semantic_authority"].get("const") == "kpgs", "KPGS must retain semantic authority")
    require(receipt_schema["properties"]["public_anchor"]["properties"]["contains_private_data"].get("const") is False, "public anchor must structurally reject private data")
    require(modality_schema["properties"]["renderer_has_semantic_authority"].get("const") is False, "renderer must never receive semantic authority")
    require(anchor_schema["properties"]["network"].get("const") == "solana-devnet", "v0.1 anchor must remain devnet-only")
    require(anchor_schema["properties"]["contains_private_data"].get("const") is False, "anchor intent must reject private data")

    fixture = load_json("example.fillout-event.json")
    require(fixture.get("classification") == "synthetic", "committed frontier fixture must remain synthetic")

    harness = load_harness()
    request = harness.normalize_fillout_event(fixture)
    artifacts = harness.build_artifacts(request)
    receipt = artifacts["receipt"]
    anchor = artifacts["anchor_intent"]
    modality = artifacts["modality_contract"]

    require(request["policy"]["data_classification"] == "synthetic", "fixture classification must survive normalization")
    require(request["policy"]["allow_external_processing"] is True, "synthetic fixture should permit rented capability test")
    require(receipt["router_decision"]["adapter_mode"] == "mock", "v0.1 must not claim live model execution")
    require(receipt["provider_result"]["canonical"] is False, "mock provider output must remain non-canonical")
    require(receipt["evaluation"]["semantic_authority"] == "kpgs", "receipt must retain KPGS semantic authority")
    require(receipt["analytics_copy"]["status"] == "prepared", "Snowflake copy must remain prepared until live credentials/capability lease exist")
    require(anchor["status"] == "ready", "synthetic fixture should produce a ready anchor intent")
    require(anchor["contains_private_data"] is False, "anchor cannot contain private data")
    require(set(anchor["payload"]) == {"schema", "commitment"}, "public anchor payload must contain only schema and commitment")
    require(anchor["payload"]["commitment"] == anchor["commitment"], "anchor commitment mismatch")
    require(bool(HEX64.match(anchor["commitment"])), "anchor commitment must be SHA-256")
    require(modality["renderer_has_semantic_authority"] is False, "renderer authority boundary violated")
    require("native-text" in modality["fallbacks"], "every v0.1 modality must retain a text fallback")

    sql = (ROOT / "snowflake" / "bootstrap.sql").read_text(encoding="utf-8")
    require("KPGS_FRONTIER" in sql and "FRONTIER_TELEMETRY" in sql, "Snowflake bootstrap must create governed telemetry objects")
    require("SEMANTIC_INPUT" not in sql, "Snowflake analytics schema must not ingest semantic input in v0.1")

    build_spec = json.loads((ROOT.parent / "agent-governance" / "specs" / "frontier-harness-v0.1.json").read_text(encoding="utf-8"))
    require(build_spec.get("spec_id") == "kpgs-frontier-harness-v0.1", "governing spec identity mismatch")
    criterion_ids = [item["id"] for item in build_spec.get("acceptance_criteria", [])]
    require(len(criterion_ids) == len(set(criterion_ids)), "acceptance criterion IDs must be unique")
    planned = {item["criterion_id"] for item in build_spec.get("verification_plan", [])}
    require(set(criterion_ids) <= planned, "verification plan must cover every acceptance criterion")

    print("KPGS-FRONTIER PASS: provider-independent vertical slice is structurally coherent and executable.")
    print(f"Receipt: {receipt['receipt_id']} | commitment: {anchor['commitment']}")


if __name__ == "__main__":
    main()
