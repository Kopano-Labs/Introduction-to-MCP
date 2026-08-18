# KPGS Adaptive Progressive Updates → CRUD → SWFUS

Status: **vNext runtime contract / non-authoritative synchronization surface**

This contract joins runtime pieces that already existed in `Introduction-to-MCP` but were previously separated:

```text
Adaptive Progressive Updates (APU)
        ↓
Progressive Update
        ↓
#NB
        ↓
bounded CRUD
        ↓
SWFUS
State-Wide Framework Universal Synchronization
```

`#NB` is preserved as the explicit operator boundary marker supplied to this contract. This document deliberately does **not** invent an expansion for it.

## Why this canonicalization exists

Legacy KPGS code described multiple SWFUS mnemonics and a `swfus_engine.py` path that could write a local projection and invoke its simulated synchronization step **before** rejecting FOC/hallucinated telemetry. That ordering is incompatible with current KPGS vNext governance.

The vNext law is:

> **CRUD changes bounded state. SWFUS aligns governed system reality. Synchronization is not authority.**

This contract therefore inherits the already-proven offline-replication invariant:

> **Availability and synchronization are not authority.**

No realtime, peer, cloud, WebSocket, iroh, Automerge or other transport can widen the authority of an admitted update.

## Canonical stage order

Every progressive update is accounted for in this order:

```text
1. Telemetry
2. Classification
3. Routing
4. Protocol Selection
5. Invariant Audit
6. POC / FOC Check
7. State Update
8. Distribution
```

A rejected or held update still emits stage receipts for the full ordering; later stages are marked `NOT_REACHED` rather than silently disappearing.

### 1 — Telemetry

Establish update identity, CRUD operation and idempotency identity.

- missing update/node identity → reject;
- unknown CRUD operation → reject;
- missing idempotency key → reject;
- exact idempotent replay → return the original receipt with no repeated effect;
- same key with different content → reject collision.

### 2 — Classification

Bind the update to a lane, APU state and admitted state class.

Admitted state classes match the offline-replication membrane:

- `non_authoritative`
- `derived_projection`
- `pending_proposal`

`constitutional_truth` and other authoritative classes are rejected.

APU remains the early adaptive signal:

- `GREEN` — may continue to proof gates;
- `YELLOW` — held for review before mutation;
- `RED` — rejected before mutation/distribution;
- `UNSPECIFIED` — does not manufacture proof; later POC evidence is still required.

### 3 — Routing

Context routing is mandatory before any read or mutation.

A `READ` may proceed after routing because observation is not mutation authority. Remaining mutation stages are emitted as explicit skips and no distribution occurs.

### 4 — Protocol Selection

Mutating CRUD operations require an explicit governed protocol. Relevance or available context cannot substitute for protocol selection.

### 5 — Invariant Audit

The runtime checks that:

- `authority_effect == "none"`;
- the caller's invariant audit passed;
- the `#NB` boundary marker is present;
- numeric input is finite;
- optimistic version expectations are structurally valid.

### 6 — POC / FOC Check

This is the mutation membrane.

- APU `RED` or explicit FOC → reject;
- APU `YELLOW` → hold;
- mutation without `poc_validated=true` → hold;
- mutation without evidence references → hold.

**No mutating CRUD operation reaches state update before this gate passes.**

### 7 — State Update

CRUD is bounded to the non-authoritative projection owned by the runtime adapter:

- `CREATE` — after lane classification and full mutation gates; target must not exist;
- `READ` — after context routing; no mutation;
- `UPDATE` — after invariant and POC/FOC audit; target must exist;
- `DELETE` — only after FOC stripping/POC admission; target must exist.

Optimistic `expected_version` may hold stale writes rather than overwriting a newer projection.

### 8 — Distribution

Only an admitted, successfully applied mutation can emit a SWFUS distribution event.

The distribution event is evidence of framework alignment:

- `canonical=false`;
- `authority_effect=none`;
- `transport_grants_authority=false`;
- carries content hashes/evidence references instead of claiming canonical business truth.

If an injected distribution sink fails, the non-authoritative projection is rolled back so the local view cannot claim an update was synchronized when it was not.

## APU → Progressive Update

`kopano-core/kopano/apu_vector_matrix.py` remains the adaptive signal source. It does **not** directly mutate SWFUS state.

The intended bridge is:

```text
APU signal
  GREEN ───────┐
  YELLOW ─ HOLD│
  RED ─── REJECT
               ↓
kpgs.progressive-update.v1
               ↓
#NB + CRUD governance
               ↓
kpgs.swfus.receipt.v1
```

The machine contract is `progressive-update.schema.json`.

## Compatibility boundary

`SwfusPayload` and `SwfusHierarchy.execute(payload) -> bool` remain for legacy callers such as KESSA. The adapter now routes those calls through the canonical stage law. It no longer:

- syncs before FOC validation;
- claims Azure as the synchronization authority;
- mutates a projection before validation;
- equates a successful transport step with canonical truth.

New integrations should consume `execute_update()` and persist the resulting receipt/evidence through the canonical evidence surface.

## Relationship to vNext issues

This slice is a shared substrate, not a false closure of the larger epics:

- **#35 Sovereign Hub** — supplies a governed update/distribution primitive for control-plane state projections;
- **#38 Evaluation loop** — APU GREEN/YELLOW/RED becomes a bounded input to later proof decisions, not the decision itself;
- **#40 Realtime event plane** — SWFUS distribution events can ride WebSocket/SSE/iroh/etc., but transport remains non-authoritative;
- **#45 Evidence bundles** — SWFUS receipts expose stage order, state digest, evidence references and correlation identity for later bundle inclusion;
- **#46 vNext epic** — connects adaptive interaction state to the existing sovereign runtime laws without rewriting domain frontends.

## Non-goals

This contract does not claim:

- distributed consensus;
- canonical database ownership;
- automatic production promotion;
- transport-specific reliability;
- authority from WebSocket/Automerge/iroh/Azure connectivity;
- that APU scoring alone is POC evidence.

Those remain separate governed gates.
