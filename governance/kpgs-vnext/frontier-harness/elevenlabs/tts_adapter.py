#!/usr/bin/env python3
"""Governed ElevenLabs text-to-speech renderer for KPGS Frontier Harness v0.4."""

from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

GOVERNING_SPEC = "kpgs-frontier-harness-elevenlabs-v0.4"
REQUIRED_CAPABILITY = "elevenlabs.tts.generate"
ALLOWED_MODELS = {"eleven_flash_v2_5", "eleven_multilingual_v2", "eleven_v3"}
ALLOWED_CLASSIFICATIONS = {"public", "synthetic"}
API_ROOT = "https://api.elevenlabs.io/v1/text-to-speech"
VOICE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
MAX_TEXT_CHARS = 5000


class GovernanceError(RuntimeError):
    pass


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_text(value: str) -> str:
    return digest_bytes(value.encode("utf-8"))


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise GovernanceError("lease timestamps must include timezone")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class ElevenLabsTarget:
    voice_id: str
    model: str = "eleven_flash_v2_5"
    output_format: str = "mp3_44100_128"

    def endpoint(self) -> str:
        if not VOICE_ID_RE.fullmatch(self.voice_id):
            raise GovernanceError("invalid ElevenLabs voice id")
        if self.model not in ALLOWED_MODELS:
            raise GovernanceError("model is not in the governed allow-list")
        return f"{API_ROOT}/{self.voice_id}?output_format={urllib.parse.quote(self.output_format, safe='')}"


@dataclass(frozen=True)
class PreparedSpeech:
    request_id: str
    endpoint: str
    body: dict[str, Any]
    secret_ref: str
    voice_id: str
    model: str
    text_digest: str

    def safe_receipt(self) -> dict[str, Any]:
        return {
            "schema_version": "kpgs.elevenlabs_request_receipt.v1",
            "request_id": self.request_id,
            "provider": "elevenlabs",
            "voice_id": self.voice_id,
            "model": self.model,
            "text_digest": self.text_digest,
            "contains_text": False,
            "contains_secret": False,
            "renderer_has_semantic_authority": False,
            "semantic_authority": "kpgs",
        }


def validate_lease(lease: dict[str, Any], target: ElevenLabsTarget, *, now: datetime | None = None) -> None:
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if lease.get("governing_spec_ref") != GOVERNING_SPEC:
        raise GovernanceError("lease is not bound to the ElevenLabs v0.4 governing spec")
    subject = lease.get("subject") or {}
    if subject.get("kind") not in {"adapter", "service", "renter"}:
        raise GovernanceError("ElevenLabs capability must be leased to an adapter/service/renter")
    expected_scope = f"voice/{target.voice_id}/model/{target.model}"
    capabilities = lease.get("capabilities") or []
    permitted = any(
        item.get("name") == REQUIRED_CAPABILITY and item.get("resource_scope") == expected_scope
        for item in capabilities
    )
    if not permitted:
        raise GovernanceError("lease does not permit this voice/model renderer scope")
    issued = _parse_time(str(lease.get("issued_at", "")))
    expires = _parse_time(str(lease.get("expires_at", "")))
    if not (issued <= current < expires):
        raise GovernanceError("capability lease is not currently valid")
    refs = lease.get("secret_provider_refs") or []
    if len(refs) != 1 or not str(refs[0]).startswith("env://"):
        raise GovernanceError("v0.4 requires exactly one env:// external secret reference")


def resolve_env_secret(secret_ref: str, env: dict[str, str] | None = None) -> str:
    name = secret_ref.removeprefix("env://")
    if not name or not name.replace("_", "").isalnum() or name.upper() != name:
        raise GovernanceError("invalid env secret reference")
    source = env if env is not None else os.environ
    value = source.get(name)
    if not value:
        raise GovernanceError(f"secret provider did not resolve {secret_ref}")
    return value


def validate_modality_contract(contract: dict[str, Any]) -> None:
    if contract.get("schema_version") != "kpgs.modality_contract.v1":
        raise GovernanceError("unexpected modality contract")
    if contract.get("primary") != "speech":
        raise GovernanceError("ElevenLabs renderer requires primary=speech")
    if "elevenlabs-speech" not in (contract.get("renderers") or []):
        raise GovernanceError("modality contract does not select ElevenLabs speech")
    if contract.get("renderer_has_semantic_authority") is not False:
        raise GovernanceError("renderer cannot receive semantic authority")
    if "native-text" not in (contract.get("fallbacks") or []):
        raise GovernanceError("speech modality must retain native-text fallback")
    accessibility = contract.get("accessibility") or {}
    if accessibility.get("text_equivalent_required") is not True:
        raise GovernanceError("speech modality requires a text equivalent")


def prepare_speech(
    semantic_text: str,
    request: dict[str, Any],
    modality_contract: dict[str, Any],
    lease: dict[str, Any],
    target: ElevenLabsTarget,
    *,
    now: datetime | None = None,
) -> PreparedSpeech:
    validate_lease(lease, target, now=now)
    validate_modality_contract(modality_contract)
    policy = request.get("policy") or {}
    if policy.get("data_classification") not in ALLOWED_CLASSIFICATIONS or policy.get("allow_external_processing") is not True:
        raise GovernanceError("request policy does not authorize external speech rendering")
    if not isinstance(semantic_text, str) or not semantic_text.strip():
        raise GovernanceError("semantic text must be non-empty")
    if len(semantic_text) > MAX_TEXT_CHARS:
        raise GovernanceError("semantic text exceeds governed v0.4 renderer limit")
    request_id = str(request.get("request_id") or "")
    if len(request_id) < 8 or modality_contract.get("request_id") != request_id:
        raise GovernanceError("request/modality correlation mismatch")
    body = {"text": semantic_text, "model_id": target.model}
    return PreparedSpeech(
        request_id=request_id,
        endpoint=target.endpoint(),
        body=body,
        secret_ref=str(lease["secret_provider_refs"][0]),
        voice_id=target.voice_id,
        model=target.model,
        text_digest=digest_text(semantic_text),
    )


def submit_prepared(
    prepared: PreparedSpeech,
    *,
    secret_resolver: Callable[[str], str] = resolve_env_secret,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any]:
    api_key = secret_resolver(prepared.secret_ref)
    payload = json.dumps(prepared.body, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        prepared.endpoint,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
            "xi-api-key": api_key,
            "User-Agent": "KPGS-Frontier-Harness/0.4",
        },
    )
    try:
        with opener(request, timeout=45) as response:
            audio = response.read()
            return {
                "schema_version": "kpgs.elevenlabs_execution_receipt.v1",
                "request_id": prepared.request_id,
                "provider": "elevenlabs",
                "voice_id": prepared.voice_id,
                "model": prepared.model,
                "http_status": getattr(response, "status", 200),
                "content_type": response.headers.get("Content-Type") if getattr(response, "headers", None) else None,
                "text_digest": prepared.text_digest,
                "audio_digest": digest_bytes(audio),
                "audio_bytes": len(audio),
                "contains_text": False,
                "contains_audio": False,
                "contains_secret": False,
                "renderer_has_semantic_authority": False,
                "semantic_authority": "kpgs",
            }
    except urllib.error.HTTPError as exc:
        return {
            "schema_version": "kpgs.elevenlabs_execution_receipt.v1",
            "request_id": prepared.request_id,
            "provider": "elevenlabs",
            "voice_id": prepared.voice_id,
            "model": prepared.model,
            "http_status": exc.code,
            "text_digest": prepared.text_digest,
            "audio_digest": None,
            "audio_bytes": 0,
            "contains_text": False,
            "contains_audio": False,
            "contains_secret": False,
            "renderer_has_semantic_authority": False,
            "semantic_authority": "kpgs",
        }
