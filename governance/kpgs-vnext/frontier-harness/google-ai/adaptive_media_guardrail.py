#!/usr/bin/env python3
"""KPGS adaptive media guardrail protocol for Google AI / Veo-class generation.

This module does not bypass provider safety controls. It makes opaque generation
failures inspectable, separates provider-policy blocks from transient failures,
and allows a single governed retry only when an explanation establishes that the
request is allowed in principle and the adaptation preserves declared invariants.

PKA mapping:
- y / immutable_constraints: identity, consent, brand/character anchors, intent.
- x / mutable_constraints: wording, camera, environment, pacing, composition.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

GOVERNING_SPEC = "kpgs-google-ai-adaptive-media-v0.1"
MAX_ADAPTIVE_RETRIES = 1

POLICY_HINTS = {
    "SAFETY",
    "BLOCKLIST",
    "PROHIBITED_CONTENT",
    "IMAGE_SAFETY",
    "PERSON_GENERATION",
    "SPII",
    "RECITATION",
}

TRANSIENT_HTTP_STATUS = {408, 409, 425, 429, 500, 502, 503, 504}


class GovernanceError(RuntimeError):
    """Raised when an adaptive retry would violate KPGS governance."""


def _digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _digest_json(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return _digest_text(encoded)


def _upper_tokens(values: Sequence[str]) -> set[str]:
    return {str(value).strip().upper() for value in values if str(value).strip()}


def _error_text(payload: Mapping[str, Any] | None) -> str:
    if not payload:
        return ""
    error = payload.get("error") if isinstance(payload, Mapping) else None
    if isinstance(error, Mapping):
        parts = [error.get("status"), error.get("message"), error.get("code")]
    else:
        parts = [payload.get("status"), payload.get("message"), payload.get("code")]
    return " ".join(str(part) for part in parts if part is not None).strip()


@dataclass(frozen=True)
class MediaPolicyContext:
    """User-declared PKA boundary for a media generation request."""

    immutable_constraints: tuple[str, ...]
    mutable_constraints: tuple[str, ...]
    data_classification: str = "synthetic"
    consent_basis: str = "user-directed-generation"

    def invariant_digest(self) -> str:
        return _digest_json({
            "immutable_constraints": list(self.immutable_constraints),
            "data_classification": self.data_classification,
            "consent_basis": self.consent_basis,
        })


@dataclass(frozen=True)
class ProviderOutcome:
    """Normalized provider outcome without raw user prompt or media content."""

    classification: str
    http_status: int | None
    finish_reasons: tuple[str, ...]
    provider_error_digest: str | None
    explanation_required: bool
    retry_mode: str

    def safe_receipt(self, *, request_id: str, prompt: str) -> dict[str, Any]:
        return {
            "schema_version": "kpgs.google_ai_media_outcome_receipt.v1",
            "governing_spec_ref": GOVERNING_SPEC,
            "request_id": request_id,
            "classification": self.classification,
            "http_status": self.http_status,
            "finish_reasons": list(self.finish_reasons),
            "prompt_digest": _digest_text(prompt),
            "provider_error_digest": self.provider_error_digest,
            "explanation_required": self.explanation_required,
            "retry_mode": self.retry_mode,
            "contains_prompt": False,
            "contains_media": False,
            "canonical": False,
            "semantic_authority": "kpgs",
        }


@dataclass(frozen=True)
class PolicyExplanation:
    """Structured explanation produced after an opaque provider failure."""

    verdict: str
    reason_code: str
    explanation: str
    adapted_prompt: str | None = None
    invariant_digest: str | None = None
    confidence: str = "unknown"

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "PolicyExplanation":
        return cls(
            verdict=str(payload.get("verdict") or "unknown").strip().lower(),
            reason_code=str(payload.get("reason_code") or "unknown").strip().lower(),
            explanation=str(payload.get("explanation") or "").strip(),
            adapted_prompt=(str(payload["adapted_prompt"]).strip() if payload.get("adapted_prompt") else None),
            invariant_digest=(str(payload["invariant_digest"]).strip() if payload.get("invariant_digest") else None),
            confidence=str(payload.get("confidence") or "unknown").strip().lower(),
        )

    def safe_receipt(self, *, request_id: str) -> dict[str, Any]:
        return {
            "schema_version": "kpgs.google_ai_policy_explanation_receipt.v1",
            "governing_spec_ref": GOVERNING_SPEC,
            "request_id": request_id,
            "verdict": self.verdict,
            "reason_code": self.reason_code,
            "explanation_digest": _digest_text(self.explanation),
            "adapted_prompt_digest": _digest_text(self.adapted_prompt) if self.adapted_prompt else None,
            "invariant_digest": self.invariant_digest,
            "confidence": self.confidence,
            "contains_explanation": False,
            "contains_prompt": False,
            "canonical": False,
            "semantic_authority": "kpgs",
        }


@dataclass(frozen=True)
class RetryDecision:
    authorized: bool
    reason: str
    retry_prompt: str | None
    retry_count: int

    def safe_receipt(self, *, request_id: str, policy_context: MediaPolicyContext) -> dict[str, Any]:
        return {
            "schema_version": "kpgs.google_ai_adaptive_retry_receipt.v1",
            "governing_spec_ref": GOVERNING_SPEC,
            "request_id": request_id,
            "authorized": self.authorized,
            "reason": self.reason,
            "retry_prompt_digest": _digest_text(self.retry_prompt) if self.retry_prompt else None,
            "retry_count": self.retry_count,
            "invariant_digest": policy_context.invariant_digest(),
            "contains_prompt": False,
            "canonical": False,
            "semantic_authority": "kpgs",
        }


def classify_provider_outcome(
    *,
    http_status: int | None,
    payload: Mapping[str, Any] | None = None,
    finish_reasons: Sequence[str] = (),
) -> ProviderOutcome:
    """Classify a media-generation result using only observable provider evidence."""

    reasons = tuple(str(reason) for reason in finish_reasons if str(reason).strip())
    reason_tokens = _upper_tokens(reasons)
    error_text = _error_text(payload)
    error_upper = error_text.upper()
    error_digest = _digest_text(error_text) if error_text else None

    if http_status is not None and 200 <= http_status < 300 and not reasons:
        return ProviderOutcome("success", http_status, reasons, error_digest, False, "none")

    if http_status is not None and 200 <= http_status < 300 and not (reason_tokens & POLICY_HINTS):
        return ProviderOutcome("success", http_status, reasons, error_digest, False, "none")

    if http_status in TRANSIENT_HTTP_STATUS:
        return ProviderOutcome("technical_transient", http_status, reasons, error_digest, False, "same_prompt")

    policy_signal = bool(reason_tokens & POLICY_HINTS) or any(hint in error_upper for hint in POLICY_HINTS)
    if policy_signal:
        if error_text:
            return ProviderOutcome("provider_policy_block", http_status, reasons, error_digest, True, "explain_then_govern")
        return ProviderOutcome("opaque_policy_failure", http_status, reasons, error_digest, True, "explain_then_govern")

    if http_status is not None and http_status >= 400:
        return ProviderOutcome("opaque_provider_failure", http_status, reasons, error_digest, True, "explain_then_govern")

    return ProviderOutcome("unknown", http_status, reasons, error_digest, True, "explain_then_govern")


def build_policy_explanation_request(
    *,
    original_prompt: str,
    provider_outcome: ProviderOutcome,
    policy_context: MediaPolicyContext,
) -> dict[str, Any]:
    """Build a bounded self-explanation request; never asks the model to evade safety."""

    if not original_prompt.strip():
        raise GovernanceError("original_prompt must be non-empty")
    if not provider_outcome.explanation_required:
        raise GovernanceError("provider outcome does not require policy explanation")

    instruction = (
        "You are a policy-transparency diagnostic inside KPGS. Do not bypass, weaken, evade, "
        "obfuscate, or work around any provider safety rule. Based only on the supplied request, "
        "published policy concepts, and observable provider metadata: (1) decide whether the user "
        "request is allowed in principle, disallowed, or unknown; (2) explain the most specific "
        "reason you can justify without claiming hidden policy knowledge; (3) if and only if it is "
        "allowed in principle, propose one minimal clarification that preserves every immutable "
        "constraint and changes only mutable constraints. Return JSON only with keys verdict, "
        "reason_code, explanation, adapted_prompt, invariant_digest, confidence. If disallowed or "
        "unknown, adapted_prompt must be null."
    )

    return {
        "system_instruction": instruction,
        "diagnostic_input": {
            "original_prompt": original_prompt,
            "provider_classification": provider_outcome.classification,
            "http_status": provider_outcome.http_status,
            "finish_reasons": list(provider_outcome.finish_reasons),
            "immutable_constraints": list(policy_context.immutable_constraints),
            "mutable_constraints": list(policy_context.mutable_constraints),
            "expected_invariant_digest": policy_context.invariant_digest(),
        },
        "canonical": False,
        "semantic_authority": "kpgs",
    }


def authorize_adaptive_retry(
    *,
    original_prompt: str,
    explanation: PolicyExplanation,
    policy_context: MediaPolicyContext,
    retry_count: int,
) -> RetryDecision:
    """Authorize at most one clarification retry while preserving PKA invariants."""

    if retry_count < 0:
        raise GovernanceError("retry_count cannot be negative")
    if retry_count >= MAX_ADAPTIVE_RETRIES:
        return RetryDecision(False, "adaptive_retry_budget_exhausted", None, retry_count)

    if explanation.verdict != "allowed_in_principle":
        return RetryDecision(False, "provider_policy_not_cleared", None, retry_count)

    expected_invariant_digest = policy_context.invariant_digest()
    if explanation.invariant_digest != expected_invariant_digest:
        return RetryDecision(False, "immutable_constraint_digest_mismatch", None, retry_count)

    adapted = (explanation.adapted_prompt or "").strip()
    if not adapted:
        return RetryDecision(False, "no_compliant_adaptation_supplied", None, retry_count)
    if adapted == original_prompt.strip():
        return RetryDecision(False, "adaptation_did_not_change_request", None, retry_count)

    forbidden_reason_codes = {"disallowed", "bypass", "evasion", "jailbreak", "unknown"}
    if explanation.reason_code in forbidden_reason_codes:
        return RetryDecision(False, "diagnostic_reason_not_retryable", None, retry_count)

    return RetryDecision(True, "allowed_in_principle_clarification", adapted, retry_count + 1)
