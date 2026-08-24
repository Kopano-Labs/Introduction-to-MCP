# Mzansi Language Contracts — Phase 7

Status: **PR1 contract slice** for `RobynAwesome/Introduction-to-MCP#103`.

This directory defines the first governed boundary for KPGS sociolinguistic inference. It does **not** claim a trained Sepedi model, production TTS quality, or native-speaker validation.

## Contracts

| Contract | Purpose |
| --- | --- |
| `evidence-class.schema.json` | Prevents AI-generated/transformed data from silently becoming human truth. |
| `linguistic-record.schema.json` | Stores meaning-aligned language evidence, code-switch segments, declared context, consent/licensing, and validation state. |
| `inference-request.schema.json` | Captures the requested language/register/code-switch/MXIT/speech transformation and locality/cost constraints. |
| `validation-receipt.schema.json` | Records what happened, measurable confidence, human validation, route/fallback, flags, and POC/FOC status. |

All schemas use JSON Schema Draft 2020-12 and follow the strict KPGS vNext pattern (`additionalProperties: false`, versioned `schema` constants).

## Invariants

1. **Meaning preservation is mandatory.** `meaning_preservation_required` is locked to `true`.
2. **Street language is not random slang injection.** Register, code-switching, MXIT compression, and speech are explicit dimensions.
3. **User context is explicit.** `user_contract.context_source` is locked to `explicit_user_input`; region/register preferences must not be guessed from stereotypes.
4. **Evidence provenance is mandatory.** Every linguistic record carries one canonical evidence class.
5. **Synthetic evidence never self-promotes.** `AI_GENERATED` and `AI_TRANSFORMED` remain distinguishable from `HUMAN_RECORDED` and `HUMAN_VALIDATED`.
6. **Consent/licensing are data-plane fields, not policy prose.** Speaker consent and licensing are required record properties.
7. **Cloud/local routing is visible.** The validation receipt records the inference location, providers, and whether fallback occurred.
8. **HOLD is valid.** A request may produce `hold` when evidence is insufficient rather than hallucinating cultural certainty.
9. **POC is receipted.** `POC_VALIDATED` is a receipt outcome, never a branding claim.

## First Sepedi vertical slice

```text
Formal Sepedi text
  -> meaning-preserving register transform
  -> conversational / street Sepedi
  -> optional controlled Sepedi-English code-switch
  -> optional MXIT compression
  -> speech synthesis
  -> validation receipt
```

The first runtime slice should remain limited to Sepedi (`nso`) until receipts support expansion.

## Example request

```json
{
  "schema": "kpgs.mzansi.inference-request.v1",
  "request_id": "req-000001",
  "input": {
    "text": "REPLACE_WITH_VALIDATED_SEPEDI_SOURCE_TEXT",
    "language_tag": "nso",
    "register": "formal"
  },
  "target": {
    "language_tag": "nso",
    "register": "street",
    "meaning_preservation_required": true,
    "code_switch_ratio": 0.25,
    "mxit_mode": "prefer",
    "speech": {
      "required": true,
      "voice_id": null,
      "high_fidelity": false
    }
  },
  "user_contract": {
    "context_source": "explicit_user_input",
    "preferred_language_tag": "nso",
    "street_formal_ratio": 0.75,
    "code_switch_tolerance": "medium",
    "region": null,
    "accessibility_notes": null
  },
  "execution": {
    "locality": "prefer_local",
    "max_cost_zar": 0,
    "allow_teacher_review": true,
    "allow_human_review": true
  },
  "created_at": "2026-08-24T02:10:00+02:00"
}
```

The placeholder source text is deliberate: this contracts PR must not invent Sepedi examples and then accidentally canonize unvalidated linguistic content.

## Promotion gate

Before PR2 (Data Engine) can claim POC:

- collect meaning-aligned examples with provenance;
- record speaker consent/licensing;
- identify which records are human vs synthetic;
- obtain native-speaker validation for candidate transformations;
- define acceptance thresholds for meaning preservation, naturalness, pronunciation, and code-switch appropriateness;
- preserve failures/disagreements instead of deleting them from the evidence trail.

Canonical truth lock: `RobynAwesome/Introduction-to-MCP#103`.
