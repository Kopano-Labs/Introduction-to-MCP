# KPGS Frontier Harness v0.1

Status: **POC / non-production**

The Frontier Harness proves that KPGS can consume rented external capabilities without transferring semantic authority, durable state, or governance ownership to the provider.

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
        +--> Google AI adapter (mock in v0.1)
        |
        v
kpgs.capability_receipt.v1
        |
        +--> Snowflake analytics copy (prepared row)
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
7. A provider adapter MUST be replaceable without changing the capability request or receipt schemas.

## v0.1 provider roles

| Provider | Governed role | v0.1 state |
|---|---|---|
| Fillout / Zite | structured intake / disposable frontier UI | synthetic fixture |
| Google AI | rented model/multimodal capability | deterministic mock adapter |
| Snowflake | analytical copy / evidence telemetry | SQL bootstrap + staged row |
| Solana | public commitment anchoring | devnet-ready intent only |
| ElevenLabs | speech renderer | modality contract declaration only |

No vendor credential is stored in this directory. Live provider execution is deliberately out of scope until a capability lease and secret-provider reference are supplied.

## Run the vertical slice

```bash
python governance/kpgs-vnext/frontier-harness/frontier_harness.py
python governance/kpgs-vnext/frontier-harness/validate.py
```

`frontier_harness.py` uses only the Python standard library. It converts the synthetic Fillout-like event into a governed request, routes it through a deterministic Google-AI mock renter, emits a receipt, stages a Snowflake-compatible telemetry row, prepares a Solana devnet anchor intent, and emits a modality contract.

`validate.py` is the dependency-free structural gate for the v0.1 schemas and dry-run invariants.

## Promotion boundary

The harness is a POC. A provider may move from `mock`/`prepared` to `live` only when KPGS can prove:

`request -> governing spec -> capability lease -> provider execution -> receipt -> evaluation -> local checkpoint -> optional external copy/anchor -> rollback`

The local receipt remains authoritative for the execution record. Snowflake is an analytical copy, Solana receives only a commitment, and renderers never receive semantic authority.
