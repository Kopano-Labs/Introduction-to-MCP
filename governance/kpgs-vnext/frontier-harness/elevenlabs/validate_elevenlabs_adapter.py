#!/usr/bin/env python3
"""Dependency-free gate for KPGS ElevenLabs modality v0.4."""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"KPGS-ELEVENLABS FAIL: {message}")


def load_adapter():
    spec = importlib.util.spec_from_file_location("kpgs_elevenlabs_adapter", ROOT / "tts_adapter.py")
    require(spec is not None and spec.loader is not None, "adapter must be importable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeHeaders:
    def get(self, name, default=None):
        return "audio/mpeg" if name.lower() == "content-type" else default


class FakeResponse:
    status = 200
    headers = FakeHeaders()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return b"ID3FAKE-MP3-KPGS-AUDIO"


def main() -> None:
    adapter = load_adapter()
    now = datetime(2026, 8, 17, 16, 0, tzinfo=timezone.utc)
    voice_id = "JBFqnCBsd6RMkjVDRZzb"
    target = adapter.ElevenLabsTarget(voice_id, "eleven_flash_v2_5")
    lease = {
        "lease_id": "lease_elevenlabs_test_001",
        "subject": {"id": "frontier-elevenlabs-renderer", "kind": "adapter"},
        "tenant_id": "kopano-labs",
        "domain_id": "Introduction-to-MCP",
        "task_id": "frontier-elevenlabs-v0.4-test",
        "capabilities": [{
            "name": "elevenlabs.tts.generate",
            "resource_scope": f"voice/{voice_id}/model/eleven_flash_v2_5",
            "constraints": ["renderer-only", "text-equivalent-required"]
        }],
        "issued_at": (now - timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
        "expires_at": (now + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        "policy_decision_ref": "policy://frontier-elevenlabs-v0.4/test",
        "governing_spec_ref": "kpgs-frontier-harness-elevenlabs-v0.4",
        "secret_provider_refs": ["env://KPGS_ELEVENLABS_API_KEY"],
    }
    request = {
        "schema_version": "kpgs.capability_request.v1",
        "request_id": "req_elevenlabs_validation_001",
        "policy": {"data_classification": "synthetic", "allow_external_processing": True},
    }
    modality = {
        "schema_version": "kpgs.modality_contract.v1",
        "contract_id": "modality_test_001",
        "request_id": request["request_id"],
        "semantic_ref": "a" * 64,
        "primary": "speech",
        "renderers": ["elevenlabs-speech"],
        "fallbacks": ["native-text"],
        "accessibility": {"text_equivalent_required": True, "reduced_motion_safe": True},
        "renderer_has_semantic_authority": False,
    }
    text = "KPGS governs modality; the renderer does not own meaning."
    prepared = adapter.prepare_speech(text, request, modality, lease, target, now=now)
    safe = prepared.safe_receipt()
    body = json.dumps(prepared.body, sort_keys=True).lower()
    require("api_key" not in body and "xi-api-key" not in body, "credential leaked into body")
    require(safe["contains_text"] is False and safe["contains_secret"] is False, "safe receipt leaked text/secret")
    require(safe["renderer_has_semantic_authority"] is False and safe["semantic_authority"] == "kpgs", "modality authority boundary violated")

    captured = {}

    def fake_opener(http_request, timeout):
        captured["headers"] = dict(http_request.header_items())
        captured["timeout"] = timeout
        return FakeResponse()

    receipt = adapter.submit_prepared(
        prepared,
        secret_resolver=lambda _ref: "test-eleven-key-not-real",
        opener=fake_opener,
    )
    headers = {k.lower(): v for k, v in captured["headers"].items()}
    require(headers.get("xi-api-key") == "test-eleven-key-not-real", "API key must be sent only in xi-api-key header")
    require(receipt["http_status"] == 200 and receipt["audio_bytes"] > 0, "fake TTS execution failed")
    require(receipt["audio_digest"] and len(receipt["audio_digest"]) == 64, "audio must be digest-bound")
    require(receipt["contains_audio"] is False and receipt["contains_text"] is False, "receipt must not embed content")
    require(receipt["renderer_has_semantic_authority"] is False, "renderer gained semantic authority")

    bad_modality = json.loads(json.dumps(modality))
    bad_modality["fallbacks"] = []
    try:
        adapter.prepare_speech(text, request, bad_modality, lease, target, now=now)
    except adapter.GovernanceError:
        pass
    else:
        raise SystemExit("KPGS-ELEVENLABS FAIL: speech without text fallback was accepted")

    private_request = json.loads(json.dumps(request))
    private_request["policy"]["data_classification"] = "private"
    private_request["policy"]["allow_external_processing"] = False
    try:
        adapter.prepare_speech(text, private_request, modality, lease, target, now=now)
    except adapter.GovernanceError:
        pass
    else:
        raise SystemExit("KPGS-ELEVENLABS FAIL: private semantic text was allowed externally")

    expired = dict(lease)
    expired["issued_at"] = "2026-08-16T00:00:00Z"
    expired["expires_at"] = "2026-08-16T00:10:00Z"
    try:
        adapter.prepare_speech(text, request, modality, expired, target, now=now)
    except adapter.GovernanceError:
        pass
    else:
        raise SystemExit("KPGS-ELEVENLABS FAIL: expired lease was accepted")

    print("KPGS-ELEVENLABS PASS: speech is governed as a renderer, not semantic authority.")
    print(f"Prepared: {prepared.request_id} -> {prepared.endpoint}")
    print(f"Audio digest: {receipt['audio_digest']}")


if __name__ == "__main__":
    main()
