# KPGS Frontier Harness

Status: **POC / non-production / provider promotions in progress**

The Frontier Harness proves that KPGS can consume rented external capabilities without transferring semantic authority, durable state, governance ownership, or secret custody to the provider.

## One Engine

```text
Fillout / Zite event
        |
        v
kpgs.capability_request.v1
        |
        v
KPGS capability router
        |
        +--> Google AI renter
        |      `-- v0.3 live-capable / lease-scoped / non-canonical
        |
        v
kpgs.capability_receipt.v1
        |
        +--> Snowflake analytical copy
        |      `-- v0.2 live-capable / fail-closed
        +--> local SHA-256 commitment
        +--> Solana anchor intent (not broadcast)
        |
        v
kpgs.modality_contract.v1
        |
        +--> text
        +--> visual
        +--> speech
        `--> haptic/event
```

## Laws

1. **Provider capability != KPGS dependency.**
2. **Provider output != KPGS truth.**
3. **Public anchor != private data.**
4. **Modality != semantic authority.**
5. **External analytics != local sovereign state.**
6. **Input != authority.**
7. **Secret reference != secret custody.**
8. A provider adapter MUST be replaceable without changing the capability request/receipt authority model.

## Provider promotion map

| Provider | Governed role | Current state |
|---|---|---|
| Fillout / Zite | structured intake / disposable frontier UI | synthetic fixture |
| Google AI | rented model/multimodal capability | v0.3 live-capable adapter; no live credential receipt yet |
| Snowflake | analytical copy / evidence telemetry | v0.2 live-capable SQL API adapter; no live write receipt yet |
| Solana | public commitment anchoring | devnet-ready intent only |
| ElevenLabs | speech renderer | modality contract declaration only |

No vendor credential is stored in this directory. Provider promotion requires a current capability lease plus an external secret-provider reference. A live-capable adapter does not become a claimed live integration until a credential-backed execution receipt exists.

## Run the governed gates

```bash
python governance/kpgs-vnext/frontier-harness/validate.py
python governance/kpgs-vnext/frontier-harness/snowflake/validate_snowflake_adapter.py
python governance/kpgs-vnext/frontier-harness/google-ai/validate_google_ai_adapter.py
```

The baseline v0.1 harness remains deterministic and provider-independent. Provider-specific promotion adapters sit behind the same KPGS authority boundary and can fail back to the local/mock path.

## Promotion boundary

A provider may move from `mock`/`prepared` to a claimed `live` state only when KPGS can prove:

`request -> governing spec -> capability lease -> external secret resolution -> provider execution -> receipt -> KPGS evaluation -> local checkpoint -> optional external copy/anchor -> rollback`

The local KPGS receipt remains authoritative for the execution record. Snowflake is an analytical copy, Google AI is a rented capability, Solana receives only commitments, and renderers never receive semantic authority.
