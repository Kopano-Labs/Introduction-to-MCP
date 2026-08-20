#!/usr/bin/env python3
"""Dependency-free validation gate for KPGS adaptive Google AI media guardrails."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"KPGS-ADAPTIVE-MEDIA FAIL: {message}")


def load_protocol():
    spec = importlib.util.spec_from_file_location("kpgs_adaptive_media", ROOT / "adaptive_media_guardrail.py")
    require(spec is not None and spec.loader is not None, "protocol must be importable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    protocol = load_protocol()
    prompt = (
        "Create a cinematic scene with the approved recurring adult fictional character, "
        "same green polo and beige trousers, walking through a new public environment."
    )
    context = protocol.MediaPolicyContext(
        immutable_constraints=(
            "adult fictional character identity remains consistent",
            "green polo and beige trousers remain consistent",
            "non-deceptive fictional media intent remains consistent",
        ),
        mutable_constraints=(
            "camera angle may change",
            "environment may change",
            "lighting and movement may change",
        ),
    )

    success = protocol.classify_provider_outcome(http_status=200, payload={}, finish_reasons=("STOP",))
    require(success.classification == "success", "ordinary STOP result must remain success")
    require(success.explanation_required is False, "successful result must not trigger diagnostic loop")

    opaque = protocol.classify_provider_outcome(
        http_status=400,
        payload={},
        finish_reasons=("SAFETY",),
    )
    require(opaque.classification == "opaque_policy_failure", "opaque safety failure must be classified")
    require(opaque.explanation_required is True, "opaque safety failure must request explanation")
    require(opaque.retry_mode == "explain_then_govern", "policy failure must not auto-retry")

    diagnostic = protocol.build_policy_explanation_request(
        original_prompt=prompt,
        provider_outcome=opaque,
        policy_context=context,
    )
    system_instruction = diagnostic["system_instruction"].lower()
    require("do not bypass" in system_instruction, "diagnostic must prohibit safety bypass")
    require("adapted_prompt" in system_instruction, "diagnostic must request structured compliant adaptation")
    require(
        diagnostic["diagnostic_input"]["expected_invariant_digest"] == context.invariant_digest(),
        "diagnostic must bind immutable PKA constraints",
    )

    explanation = protocol.PolicyExplanation.from_mapping({
        "verdict": "allowed_in_principle",
        "reason_code": "ambiguous_person_generation_context",
        "explanation": "The request appears allowed in principle; clarify that the subject is an adult fictional character.",
        "adapted_prompt": (
            "Create a cinematic scene with the approved recurring adult fictional character, "
            "same green polo and beige trousers, clearly fictional and non-deceptive, walking "
            "through a new public environment."
        ),
        "invariant_digest": context.invariant_digest(),
        "confidence": "medium",
    })
    decision = protocol.authorize_adaptive_retry(
        original_prompt=prompt,
        explanation=explanation,
        policy_context=context,
        retry_count=0,
    )
    require(decision.authorized is True, "allowed-in-principle clarification should receive one governed retry")
    require(decision.retry_count == 1, "authorized retry must consume the single adaptive retry budget")

    exhausted = protocol.authorize_adaptive_retry(
        original_prompt=prompt,
        explanation=explanation,
        policy_context=context,
        retry_count=1,
    )
    require(exhausted.authorized is False, "second adaptive retry must fail closed")
    require(exhausted.reason == "adaptive_retry_budget_exhausted", "retry budget failure reason must be explicit")

    tampered = protocol.PolicyExplanation.from_mapping({
        "verdict": "allowed_in_principle",
        "reason_code": "ambiguous_person_generation_context",
        "explanation": "Attempted rewrite changed a protected invariant.",
        "adapted_prompt": "Generate a different person with different clothing.",
        "invariant_digest": "0" * 64,
        "confidence": "high",
    })
    tampered_decision = protocol.authorize_adaptive_retry(
        original_prompt=prompt,
        explanation=tampered,
        policy_context=context,
        retry_count=0,
    )
    require(tampered_decision.authorized is False, "immutable PKA drift must fail closed")
    require(
        tampered_decision.reason == "immutable_constraint_digest_mismatch",
        "invariant drift must have a deterministic failure reason",
    )

    disallowed = protocol.PolicyExplanation.from_mapping({
        "verdict": "disallowed",
        "reason_code": "provider_policy",
        "explanation": "Published provider policy does not allow this request.",
        "adapted_prompt": None,
        "invariant_digest": context.invariant_digest(),
        "confidence": "high",
    })
    blocked = protocol.authorize_adaptive_retry(
        original_prompt=prompt,
        explanation=disallowed,
        policy_context=context,
        retry_count=0,
    )
    require(blocked.authorized is False, "disallowed content must never receive an adaptive rewrite")

    transient = protocol.classify_provider_outcome(
        http_status=429,
        payload={"error": {"status": "RESOURCE_EXHAUSTED", "message": "rate limited"}},
        finish_reasons=(),
    )
    require(transient.classification == "technical_transient", "429 must be treated as technical/transient")
    require(transient.retry_mode == "same_prompt", "technical retry must not mutate semantic intent")

    outcome_receipt = opaque.safe_receipt(request_id="req_veo_validation_001", prompt=prompt)
    explanation_receipt = explanation.safe_receipt(request_id="req_veo_validation_001")
    retry_receipt = decision.safe_receipt(request_id="req_veo_validation_001", policy_context=context)
    serialized_receipts = json.dumps([outcome_receipt, explanation_receipt, retry_receipt], sort_keys=True)

    require(prompt not in serialized_receipts, "safe receipts must not persist raw prompts")
    require(explanation.explanation not in serialized_receipts, "safe receipts must not persist diagnostic prose")
    require(outcome_receipt["canonical"] is False, "provider outcome must remain non-canonical")
    require(retry_receipt["semantic_authority"] == "kpgs", "retry authority must remain with KPGS")

    print("KPGS-ADAPTIVE-MEDIA PASS: explain -> govern -> adapt -> retry is bounded and fail-closed.")
    print(f"Invariant digest: {context.invariant_digest()}")
    print(f"Outcome: {opaque.classification}; retry authorized: {decision.authorized}")


if __name__ == "__main__":
    main()
