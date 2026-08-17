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
```

The gate is dependency-free and network-free. It proves lease enforcement, model allow-listing, private-input rejection, external secret isolation, request construction, response digesting, usage capture, and non-canonical provider output.

## Promotion boundary

A real Google AI call is authorized only when KPGS issues a current lease bound to `kpgs-frontier-harness-google-ai-v0.3`, the request is classified `public` or `synthetic`, `allow_external_processing=true`, and the external API key resolves at runtime.

A successful provider response still remains non-canonical until KPGS evaluates it and emits the governing capability receipt.
