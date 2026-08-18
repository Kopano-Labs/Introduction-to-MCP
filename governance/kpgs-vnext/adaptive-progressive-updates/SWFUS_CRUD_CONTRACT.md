# Adaptive Progressive Updates → SWFUS CRUD Contract

**Status:** POC / executable contract  
**Canonical repository:** `RobynAwesome/Introduction-to-MCP`  
**Runtime:** `kopano-core/kopano/swfus_engine.py`

## Purpose

Adaptive PWA experiences need to change while a user is using them without confusing visual adaptation, local/offline state, canonical business truth and external synchronization.

The governed progression is:

```text
ADAPTIVE PU
  -> PROGRESSIVE UPDATE
  -> CRUD INTENT
  -> SWFUS
       S  Sovereign Ingestion
       W  Witness Isolation
       F  Fluid Vectoring
       U  Unified Synchronization
       S  Severance / quarantine
  -> RECEIPT
  -> UI / evidence feedback
```

This is **CRUD evolved**, not CRUD replaced. `CREATE | READ | UPDATE | DELETE` remain the explicit data intents. SWFUS governs how those intents are admitted, witnessed, transformed, synchronized and rejected.

## Core invariants

1. **Local witness != external sync.** An offline-valid update may be accepted locally as `pending_sync`; it must not be called externally synchronized.
2. **Transport failure != governance failure.** Network/provider failure does not erase a valid local witness.
3. **Rejected update != erased history.** Severance quarantines the rejected attempt and preserves previously witnessed state.
4. **DELETE is evidence-preserving.** Canonical SWFUS uses a tombstone/revision rather than silently destroying the prior record.
5. **Revision conflict fails closed.** `UPDATE` and `DELETE` may present `expected_revision`; stale writers cannot overwrite a newer witness.
6. **Every accepted or rejected attempt emits evidence.** Receipts carry node, requested/resolved action, revision, synchronization state, correlation/capability references and evidence hash.
7. **No fake external state.** A configured string/URL/provider name is not synchronization evidence. `synced` requires an observed successful sync-adapter result.
8. **Capability reference is evidence, not ambient authority.** A `capability_lease_id` may be attached to a receipt; validating and issuing the lease remains the responsibility of the canonical Hub/security boundary.
9. **Adaptive rendering cannot weaken data governance.** A Lite/Mobile/Enhanced/Immersive UI may render the same update differently, but the CRUD/SWFUS contract remains identical.
10. **Stateless renters do not own durable truth.** The runtime may execute a transition; durable authority belongs to the governed witness/canonical storage boundary.

## SWFUS stages

### 1. Sovereign Ingestion

Validate the request before mutation:

- node ID is present;
- action is governed;
- telemetry is finite and within declared bounds;
- explicitly untrusted/hallucinated payloads are rejected;
- revision expectations are structurally valid.

No claim of cryptographic identity is made merely because a payload passed this stage.

### 2. Witness Isolation

The accepted local state is written to an offline-capable witness store with:

- monotonic revision;
- tombstone state;
- data snapshot;
- telemetry value;
- observed timestamp;
- deterministic evidence fingerprint.

This is the minimum state that lets an Adaptive PWA remain coherent through disconnect/reconnect.

### 3. Fluid Vectoring

CRUD becomes an explicit transition:

```text
CREATE  -> new active revision
READ    -> current active witness
UPDATE  -> merge into next revision
DELETE  -> next revision + tombstone
```

Legacy `TELEMETRY_INGESTION` is a compatibility lane only and resolves to `CREATE` or `UPDATE` based on witnessed state.

### 4. Unified Synchronization

An injected sync adapter may attempt propagation to the canonical external boundary.

```text
observed success -> synced
no adapter        -> pending_sync
transport failure -> pending_sync
```

The local witness remains intact in all three cases. External synchronization should be retried by the PWA/adapter/event-plane workflow under its own policy.

### 5. Severance

Governance/transition violations produce a `severed` receipt and quarantine entry.

Severance does **not** delete a previously accepted witness. This makes failures auditable and prevents a bad update from rewriting history.

## Progressive Update state exposed to a PWA

An everyday UI should map receipts to simple state:

```text
accepted + synced        -> Saved
accepted + pending_sync  -> Saved on this device · syncing
severed                  -> Could not apply · review/retry
revision conflict        -> Newer change exists · refresh
```

The user does not need to see the terms SWFUS, CRUD, capability lease or synchronization adapter unless they open a technical/governance view.

## Relationship to KPGS vNext

This contract composes with:

- #39 specification-first build supervision;
- #40 realtime event-plane delivery/reconnect;
- #41 adaptive everyday PWA UX;
- #42 identity/capability leases;
- #45 evidence bundles and scorecards.

The flow is therefore:

```text
specification
 -> capability/policy decision
 -> adaptive user intent
 -> CRUD/SWFUS transition
 -> local witness
 -> realtime/sync attempt
 -> receipt/evidence
 -> progressive UI feedback
 -> verify/promote/rollback
```

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
