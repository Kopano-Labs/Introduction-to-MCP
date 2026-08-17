#!/usr/bin/env python3
"""Governed Gemini GenerateContent adapter for KPGS Frontier Harness v0.3."""

from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

GOVERNING_SPEC = "kpgs-frontier-harness-google-ai-v0.3"
REQUIRED_CAPABILITY = "google-ai.generate-content"
ALLOWED_MODELS = {"gemini-3.6-flash", "gemini-3.5-flash-lite"}
ALLOWED_CLASSIFICATIONS = {"public", "synthetic"}
API_ROOT = "https://generativelanguage.googleapis.com/v1beta/models"
FORBIDDEN_REQUEST_KEYS = {"api_key", "secret", "password", "private_payload"}
MAX_INPUT_CHARS = 12000


class GovernanceError(RuntimeError):
    pass


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise GovernanceError("lease timestamps must include timezone")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class GeminiTarget:
    model: str = "gemini-3.6-flash"

    def endpoint(self) -> str:
        if self.model not in ALLOWED_MODELS:
            raise GovernanceError("model is not in the governed allow-list")
        return f"{API_ROOT}/{self.model}:generateContent"


@dataclass(frozen=True)
class PreparedGeneration:
    request_id: str
    endpoint: str
    body: dict[str, Any]
    secret_ref: str
    model: str
    input_digest: str

    def safe_receipt(self) -> dict[str, Any]:
        return {
            "schema_version": "kpgs.google_ai_request_receipt.v1",
            "request_id": self.request_id,
            "provider": "google-ai",
            "model": self.model,
            "endpoint": self.endpoint,
            "input_digest": self.input_digest,
            "contains_input": False,
            "secret_ref": self.secret_ref,
            "contains_secret": False,
            "canonical": False,
            "semantic_authority": "kpgs",
        }


def validate_lease(lease: dict[str, Any], target: GeminiTarget, *, now: datetime | None = None) -> None:
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if lease.get("governing_spec_ref") != GOVERNING_SPEC:
        raise GovernanceError("lease is not bound to the Google AI v0.3 governing spec")

    subject = lease.get("subject") or {}
    if subject.get("kind") not in {"adapter", "service", "renter"}:
        raise GovernanceError("Google AI capability must be leased to an adapter/service/renter")

    expected_scope = f"models/{target.model}:generateContent"
    capabilities = lease.get("capabilities") or []
    permitted = any(
        item.get("name") == REQUIRED_CAPABILITY and item.get("resource_scope") == expected_scope
        for item in capabilities
    )
    if not permitted:
        raise GovernanceError("lease does not permit the requested Gemini model/resource")

    issued = _parse_time(str(lease.get("issued_at", "")))
    expires = _parse_time(str(lease.get("expires_at", "")))
    if not (issued <= current < expires):
        raise GovernanceError("capability lease is not currently valid")

    secret_refs = lease.get("secret_provider_refs") or []
    if len(secret_refs) != 1 or not str(secret_refs[0]).startswith("env://"):
        raise GovernanceError("v0.3 requires exactly one env:// external secret reference")


def resolve_env_secret(secret_ref: str, env: dict[str, str] | None = None) -> str:
    name = secret_ref.removeprefix("env://")
    if not name or not name.replace("_", "").isalnum() or not name.upper() == name:
        raise GovernanceError("invalid env secret reference")
    source = env if env is not None else os.environ
    value = source.get(name)
    if not value:
        raise GovernanceError(f"secret provider did not resolve {secret_ref}")
    return value


def prepare_generation(request: dict[str, Any], lease: dict[str, Any], target: GeminiTarget, *, now: datetime | None = None) -> PreparedGeneration:
    validate_lease(lease, target, now=now)
    forbidden = FORBIDDEN_REQUEST_KEYS.intersection(request)
    if forbidden:
        raise GovernanceError(f"forbidden request fields: {sorted(forbidden)}")

    policy = request.get("policy") or {}
    classification = policy.get("data_classification")
    if classification not in ALLOWED_CLASSIFICATIONS or policy.get("allow_external_processing") is not True:
        raise GovernanceError("request policy does not authorize external Google AI processing")

    text = request.get("semantic_input")
    if not isinstance(text, str) or not text.strip():
        raise GovernanceError("semantic_input must be non-empty text")
    if len(text) > MAX_INPUT_CHARS:
        raise GovernanceError("semantic_input exceeds governed v0.3 size limit")

    request_id = str(request.get("request_id") or "")
    if len(request_id) < 8:
        raise GovernanceError("request_id is missing or too short")

    body = {
        "contents": [{"role": "user", "parts": [{"text": text}]}],
        "systemInstruction": {
            "parts": [{
                "text": (
                    "You are a rented capability inside KPGS. Return useful task output only. "
                    "Do not claim canonical authority, user consent, policy authority, or durable state."
                )
            }]
        },
    }
    serialized = json.dumps(body, sort_keys=True).lower()
    if "api_key" in serialized or "x-goog-api-key" in serialized:
        raise GovernanceError("request body must never contain credentials")

    return PreparedGeneration(
        request_id=request_id,
        endpoint=target.endpoint(),
        body=body,
        secret_ref=str(lease["secret_provider_refs"][0]),
        model=target.model,
        input_digest=_digest(text),
    )


def _extract_text(payload: dict[str, Any]) -> str:
    chunks: list[str] = []
    for candidate in payload.get("candidates") or []:
        content = candidate.get("content") or {}
        for part in content.get("parts") or []:
            text = part.get("text")
            if isinstance(text, str):
                chunks.append(text)
    return "\n".join(chunks).strip()


def submit_prepared(
    prepared: PreparedGeneration,
    *,
    secret_resolver: Callable[[str], str] = resolve_env_secret,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any]:
    api_key = secret_resolver(prepared.secret_ref)
    payload = json.dumps(prepared.body, separators=(",", ":")).encode("utf-8")
    http_request = urllib.request.Request(
        prepared.endpoint,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-goog-api-key": api_key,
            "User-Agent": "KPGS-Frontier-Harness/0.3",
        },
    )
    try:
        with opener(http_request, timeout=45) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw) if raw else {}
            output = _extract_text(result)
            usage = result.get("usageMetadata") or {}
            finish_reasons = [
                candidate.get("finishReason")
                for candidate in result.get("candidates") or []
                if candidate.get("finishReason")
            ]
            return {
                "schema_version": "kpgs.google_ai_execution_receipt.v1",
                "request_id": prepared.request_id,
                "provider": "google-ai",
                "model": prepared.model,
                "http_status": getattr(response, "status", 200),
                "input_digest": prepared.input_digest,
                "output_digest": _digest(output),
                "output_ref": None,
                "finish_reasons": finish_reasons,
                "usage": {
                    "prompt_tokens": usage.get("promptTokenCount"),
                    "candidate_tokens": usage.get("candidatesTokenCount"),
                    "total_tokens": usage.get("totalTokenCount"),
                },
                "contains_input": False,
                "contains_output": False,
                "contains_secret": False,
                "canonical": False,
                "semantic_authority": "kpgs",
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = {}
        error = detail.get("error") or {}
        return {
            "schema_version": "kpgs.google_ai_execution_receipt.v1",
            "request_id": prepared.request_id,
            "provider": "google-ai",
            "model": prepared.model,
            "http_status": exc.code,
            "input_digest": prepared.input_digest,
            "output_digest": None,
            "output_ref": None,
            "finish_reasons": [],
            "usage": {"prompt_tokens": None, "candidate_tokens": None, "total_tokens": None},
            "error_code": error.get("code"),
            "error_status": error.get("status"),
            "contains_input": False,
            "contains_output": False,
            "contains_secret": False,
            "canonical": False,
            "semantic_authority": "kpgs",
        }
