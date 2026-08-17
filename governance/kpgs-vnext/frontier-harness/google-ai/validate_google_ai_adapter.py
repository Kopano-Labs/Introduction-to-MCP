#!/usr/bin/env python3
"""Dependency-free gate for the KPGS Google AI v0.3 adapter."""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"KPGS-GOOGLE-AI FAIL: {message}")


def load_adapter():
    spec = importlib.util.spec_from_file_location("kpgs_google_ai_adapter", ROOT / "generate_content_adapter.py")
    require(spec is not None and spec.loader is not None, "adapter must be importable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps({
            "candidates": [{
                "content": {"parts": [{"text": "Provider result for KPGS evaluation."}]},
                "finishReason": "STOP"
            }],
            "usageMetadata": {
                "promptTokenCount": 22,
                "candidatesTokenCount": 8,
                "totalTokenCount": 30
            }
        }).encode("utf-8")


def main() -> None:
    adapter = load_adapter()
    now = datetime(2026, 8, 17, 15, 50, tzinfo=timezone.utc)
    target = adapter.GeminiTarget("gemini-3.6-flash")
    lease = {
        "lease_id": "lease_google_ai_test_001",
        "subject": {"id": "frontier-google-ai-adapter", "kind": "adapter"},
        "tenant_id": "kopano-labs",
        "domain_id": "Introduction-to-MCP",
        "task_id": "frontier-google-ai-v0.3-test",
        "capabilities": [{
            "name": "google-ai.generate-content",
            "resource_scope": "models/gemini-3.6-flash:generateContent",
            "constraints": ["public-or-synthetic-only", "non-canonical-output"]
        }],
        "issued_at": (now - timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
        "expires_at": (now + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        "policy_decision_ref": "policy://frontier-google-ai-v0.3/test",
        "governing_spec_ref": "kpgs-frontier-harness-google-ai-v0.3",
        "secret_provider_refs": ["env://KPGS_GOOGLE_AI_API_KEY"],
    }
    request = {
        "schema_version": "kpgs.capability_request.v1",
        "request_id": "req_google_ai_validation_001",
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "source": {"provider": "fillout", "event_id": "evt_test", "trust": "untrusted-input"},
        "capability": {
            "name": "reasoning",
            "purpose": "validate rented model boundary",
            "preferred_provider": "google-ai",
            "requested_modality": "text",
        },
        "policy": {
            "data_classification": "synthetic",
            "allow_external_processing": True,
            "allow_public_anchor": True,
            "governing_spec_ref": "kpgs-frontier-harness-v0.1",
            "capability_lease_ref": "lease_google_ai_test_001",
        },
        "semantic_input": "Explain why a rented model must not become the canonical authority.",
    }

    prepared = adapter.prepare_generation(request, lease, target, now=now)
    body_text = json.dumps(prepared.body, sort_keys=True).lower()
    safe = prepared.safe_receipt()

    require(prepared.endpoint.endswith("/v1beta/models/gemini-3.6-flash:generateContent"), "wrong Gemini endpoint")
    require("x-goog-api-key" not in body_text and "api_key" not in body_text, "credential leaked into body")
    require(safe["contains_input"] is False and safe["contains_secret"] is False, "safe request receipt leaked sensitive material")
    require(safe["canonical"] is False and safe["semantic_authority"] == "kpgs", "authority boundary violated")

    captured = {}

    def fake_opener(http_request, timeout):
        captured["headers"] = dict(http_request.header_items())
        captured["timeout"] = timeout
        return FakeResponse()

    execution = adapter.submit_prepared(
        prepared,
        secret_resolver=lambda _ref: "test-api-key-not-a-real-secret",
        opener=fake_opener,
    )
    headers = {k.lower(): v for k, v in captured["headers"].items()}
    require(headers.get("x-goog-api-key") == "test-api-key-not-a-real-secret", "API key must be sent in x-goog-api-key header")
    require(execution["http_status"] == 200, "fake execution should succeed")
    require(execution["contains_output"] is False and execution["contains_secret"] is False, "execution receipt leaked content/secret")
    require(execution["output_digest"] and len(execution["output_digest"]) == 64, "output must be digest-bound")
    require(execution["canonical"] is False and execution["semantic_authority"] == "kpgs", "provider result self-canonicalized")
    require(execution["usage"]["total_tokens"] == 30, "usage metadata was not captured")

    private_request = json.loads(json.dumps(request))
    private_request["policy"]["data_classification"] = "private"
    private_request["policy"]["allow_external_processing"] = False
    try:
        adapter.prepare_generation(private_request, lease, target, now=now)
    except adapter.GovernanceError:
        pass
    else:
        raise SystemExit("KPGS-GOOGLE-AI FAIL: private request was allowed to leave KPGS")

    expired = dict(lease)
    expired["issued_at"] = "2026-08-16T00:00:00Z"
    expired["expires_at"] = "2026-08-16T00:10:00Z"
    try:
        adapter.prepare_generation(request, expired, target, now=now)
    except adapter.GovernanceError:
        pass
    else:
        raise SystemExit("KPGS-GOOGLE-AI FAIL: expired capability lease was accepted")

    try:
        adapter.prepare_generation(request, lease, adapter.GeminiTarget("gemini-2.0-flash"), now=now)
    except adapter.GovernanceError:
        pass
    else:
        raise SystemExit("KPGS-GOOGLE-AI FAIL: deprecated/non-allow-listed model was accepted")

    print("KPGS-GOOGLE-AI PASS: live-capable renter adapter is leased, fail-closed and non-canonical.")
    print(f"Prepared: {prepared.request_id} -> {prepared.endpoint}")
    print(f"Receipt digest: {execution['output_digest']}")


if __name__ == "__main__":
    main()
