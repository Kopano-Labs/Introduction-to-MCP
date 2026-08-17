#!/usr/bin/env python3
"""Dependency-free KPGS Frontier Harness v0.1 vertical slice."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
BOUNDARIES = [
    "PROVIDER OUTPUT != KPGS TRUTH",
    "PUBLIC ANCHOR != PRIVATE DATA",
    "MODALITY != SEMANTIC AUTHORITY",
    "EXTERNAL ANALYTICS != LOCAL SOVEREIGN STATE",
    "INPUT != AUTHORITY",
]


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    raw = value if isinstance(value, str) else canonical(value)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}_{digest(value)[:20]}"


def normalize_fillout_event(event: dict[str, Any]) -> dict[str, Any]:
    answers = event["answers"]
    classification = event["classification"]
    externally_shareable = classification in {"public", "synthetic"}
    return {
        "schema_version": "kpgs.capability_request.v1",
        "request_id": stable_id("req", event),
        "created_at": event["submitted_at"],
        "source": {
            "provider": "fillout",
            "event_id": event["event_id"],
            "trust": "untrusted-input",
        },
        "capability": {
            "name": answers["capability"],
            "purpose": answers["purpose"],
            "preferred_provider": "google-ai",
            "requested_modality": answers["modality"],
        },
        "policy": {
            "data_classification": classification,
            "allow_external_processing": externally_shareable,
            "allow_public_anchor": externally_shareable,
            "governing_spec_ref": "kpgs-frontier-harness-v0.1",
            "capability_lease_ref": None,
        },
        "semantic_input": answers["content"],
    }


def route(request: dict[str, Any]) -> dict[str, str]:
    allowed = request["policy"]["allow_external_processing"]
    preferred = request["capability"]["preferred_provider"]
    if allowed and preferred == "google-ai":
        return {
            "selected_provider": "google-ai",
            "adapter_mode": "mock",
            "reason": "Synthetic/public input permits rented capability testing; v0.1 stays mock until a capability lease and secret-provider reference exist.",
        }
    return {
        "selected_provider": "local",
        "adapter_mode": "mock",
        "reason": "External processing is not permitted by the request policy.",
    }


def mock_google_ai(request: dict[str, Any]) -> dict[str, Any]:
    output = (
        "Provider capability can accelerate execution, but KPGS retains routing, "
        "evaluation, receipts, durable state, and semantic authority."
    )
    return {
        "provider": "google-ai",
        "output": output,
        "output_digest": digest(output),
        "canonical": False,
    }


def snowflake_row(request: dict[str, Any], provider: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_schema": "kpgs.frontier_telemetry.v1",
        "request_id": request["request_id"],
        "source_provider": request["source"]["provider"],
        "capability": request["capability"]["name"],
        "selected_provider": provider["provider"],
        "output_digest": provider["output_digest"],
        "data_classification": request["policy"]["data_classification"],
        "external_processing_allowed": request["policy"]["allow_external_processing"],
    }


def renderer_for(modality: str) -> str:
    return {
        "text": "native-text",
        "visual": "native-visual",
        "speech": "elevenlabs-speech",
        "haptic-event": "native-event",
    }[modality]


def build_artifacts(request: dict[str, Any]) -> dict[str, Any]:
    decision = route(request)
    if decision["selected_provider"] == "google-ai":
        provider = mock_google_ai(request)
    else:
        provider = {
            "provider": "local",
            "output": request["semantic_input"],
            "output_digest": digest(request["semantic_input"]),
            "canonical": False,
        }

    telemetry = snowflake_row(request, provider)
    telemetry_digest = digest(telemetry)
    commitment_material = {
        "request_id": request["request_id"],
        "provider_output_digest": provider["output_digest"],
        "telemetry_digest": telemetry_digest,
        "governing_spec_ref": request["policy"]["governing_spec_ref"],
    }
    commitment = digest(commitment_material)
    anchor_status = "ready" if request["policy"]["allow_public_anchor"] else "not-authorized"

    anchor = {
        "schema_version": "kpgs.anchor_intent.v1",
        "intent_id": stable_id("anchor", commitment_material),
        "request_id": request["request_id"],
        "network": "solana-devnet",
        "commitment": commitment,
        "status": anchor_status,
        "contains_private_data": False,
        "payload": {"schema": "kpgs.anchor_commitment.v1", "commitment": commitment},
    }

    receipt = {
        "schema_version": "kpgs.capability_receipt.v1",
        "receipt_id": stable_id("receipt", commitment_material),
        "request_id": request["request_id"],
        "created_at": request["created_at"],
        "router_decision": decision,
        "provider_result": {
            "provider": provider["provider"],
            "output_digest": provider["output_digest"],
            "output_ref": None,
            "canonical": False,
        },
        "evaluation": {"evaluator": "kpgs", "decision": "accepted", "semantic_authority": "kpgs"},
        "analytics_copy": {"provider": "snowflake", "status": "prepared", "row_digest": telemetry_digest},
        "public_anchor": {
            "provider": "solana",
            "status": anchor_status,
            "commitment": commitment,
            "contains_private_data": False,
        },
        "boundaries": BOUNDARIES,
    }

    requested_modality = request["capability"]["requested_modality"]
    modality = {
        "schema_version": "kpgs.modality_contract.v1",
        "contract_id": stable_id("modality", {"request": request["request_id"], "output": provider["output_digest"]}),
        "request_id": request["request_id"],
        "semantic_ref": provider["output_digest"],
        "primary": requested_modality,
        "renderers": [renderer_for(requested_modality)],
        "fallbacks": ["native-text"],
        "accessibility": {"text_equivalent_required": True, "reduced_motion_safe": True},
        "renderer_has_semantic_authority": False,
    }

    return {
        "request": request,
        "provider_output": provider["output"],
        "receipt": receipt,
        "snowflake_row": telemetry,
        "anchor_intent": anchor,
        "modality_contract": modality,
    }


def run() -> dict[str, Any]:
    event = json.loads((ROOT / "example.fillout-event.json").read_text(encoding="utf-8"))
    request = normalize_fillout_event(event)
    artifacts = build_artifacts(request)
    print(json.dumps(artifacts, indent=2, ensure_ascii=False))
    return artifacts


if __name__ == "__main__":
    run()
