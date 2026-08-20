# Google AI v0.3 — Governed Renter Adapter

Status: **POC / live-capable / fail-closed**

This promotes the Frontier Harness Google AI leg from a deterministic mock to a live-capable Gemini GenerateContent renter while preserving KPGS authority.

## Authority boundary

```text
KPGS capability request
        |
        v
short-lived capability lease
        |
        +-- google-ai.generate-content
        +-- exact model resource scope
        +-- external env:// secret reference
        |
        v
Gemini GenerateContent API
        |
        v
non-canonical provider result
        |
        v
KPGS evaluation + receipt
```

## Governing laws

1. **Provider output != KPGS truth.**
2. **Model execution != semantic authority.**
3. **API key != repository state.**
4. **Private/restricted input does not leave KPGS in v0.3.**
5. **Model selection is allow-listed and lease-scoped.**
6. **Receipts keep digests/usage metadata, not raw prompts or model output.**

## Current model policy

The default stable model is `gemini-3.6-flash`; `gemini-3.5-flash-lite` is permitted for high-throughput/low-cost work. Deprecated/shut-down Gemini 2.x identifiers are rejected. Model policy was checked against Google AI documentation on 2026-08-17.

The adapter deliberately avoids deprecated sampling controls such as `temperature`, `top_p`, and `top_k`.

## Authentication

No Google API key is stored in the repository. The capability lease references `env://KPGS_GOOGLE_AI_API_KEY`; runtime resolution supplies the key only to the `x-goog-api-key` HTTP header.

## Gate

```bash
python governance/kpgs-vnext/frontier-harness/google-ai/validate_google_ai_adapter.py
python governance/kpgs-vnext/frontier-harness/google-ai/validate_adaptive_media_guardrail.py
```

The first gate is dependency-free and network-free. It proves lease enforcement, model allow-listing, private-input rejection, external secret isolation, request construction, response digesting, usage capture, and non-canonical provider output.

The adaptive-media gate proves opaque media failures do not become silent dead ends or jailbreak loops. It validates the bounded `explain -> govern -> adapt -> retry -> receipt` path, immutable PKA constraint binding, one-retry budget, transient-failure separation, raw-prompt exclusion from receipts, and fail-closed behavior for disallowed content.

## Adaptive media policy transparency — Veo-class generation

`adaptive_media_guardrail.py` captures the failure mode observed in real media-generation workflows: a provider may reject a request while exposing too little information for the user to distinguish a genuine policy violation from ambiguity, a provider inconsistency, or a transient service failure.

KPGS does **not** answer that problem by weakening the provider guardrail. It makes the failure inspectable and bounded:

```text
media request
    |
    v
provider attempt
    |
    +-- success --------------------------> receipt
    |
    +-- technical transient -------------> same-prompt retry policy
    |
    +-- policy / opaque provider failure
             |
             v
      policy-transparency diagnostic
             |
             v
      KPGS governance decision
             |
             +-- disallowed / unknown ---> stop + receipt
             |
             +-- allowed in principle
                     |
                     v
              minimal clarification
              x = mutable scene state
              y = immutable intent / identity / consent anchors
                     |
                     v
              one governed retry maximum
                     |
                     v
                   receipt
```

### Why the diagnostic exists

A diagnostic is allowed to ask the model to explain observable failure evidence and compare the request against published policy concepts. It is explicitly forbidden from asking for hidden-policy disclosure, jailbreaks, obfuscation, euphemistic evasion, or any other method for bypassing provider safety.

If the diagnostic concludes that the request is allowed in principle, it may propose one minimal clarification. The retry is authorized only when the diagnostic returns the exact digest of the caller-declared immutable constraints. This is the PKA boundary: mutable `x` may adapt; static `y` must survive unchanged.

If the diagnostic says the request is disallowed or cannot establish that it is allowed, KPGS stops. There is no rewrite loop.

### Receipt boundary

Adaptive-media receipts persist:

- request and prompt digests;
- normalized outcome classification;
- observable finish reasons and HTTP status;
- diagnostic/verdict digests;
- immutable-constraint digest;
- retry authorization and retry count.

They do **not** persist raw prompts, diagnostic prose, generated media, credentials, or claim provider output as canonical truth.

## Promotion boundary

A real Google AI call is authorized only when KPGS issues a current lease bound to `kpgs-frontier-harness-google-ai-v0.3`, the request is classified `public` or `synthetic`, `allow_external_processing=true`, and the external API key resolves at runtime.

A successful provider response still remains non-canonical until KPGS evaluates it and emits the governing capability receipt.