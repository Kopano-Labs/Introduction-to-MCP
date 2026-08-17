# Live Automerge + iroh Sync POC v0.1

Status: **Phase 0 / authenticated transport POC / non-production**

This crate replaces the simulated byte transport in the merged offline-replication contract with a real local QUIC connection while preserving the KPGS authority membrane.

## Version pins

- `automerge = 0.10.0`
- `iroh = 1.0.3`
- Rust `1.91` minimum (required by iroh 1.0.3)

## Architecture

```text
KPGS non-authoritative state
        │
        ▼
   Automerge document
        │
   sync::Message frames
        │ reliable / ordered
        ▼
     iroh QUIC stream
        │ authenticated endpoint ID
        ▼
 endpoint→principal binding
        │
        X  no authority elevation
        │
        ▼
 governing task/policy/receipt gate
```

Automerge's sync protocol requires a reliable in-order stream and maintains per-peer sync state. iroh QUIC bidirectional streams provide ordered delivery and authenticate the remote endpoint ID. This POC binds that endpoint ID to an expected KPGS principal, but the binding is still not a capability grant.

## Loopback-only validation

The tests deliberately use `endpoint::presets::Minimal`, disable address lookup and relay transports, clear the default IP transports, and bind only to `127.0.0.1:0`. No Number0 relay or DNS service is required for the test lane.

The protocol uses one long-lived bidirectional QUIC stream with:

- a dedicated ALPN: `kpgs/automerge-iroh/0.1`;
- 4-byte big-endian length-prefixed Automerge messages;
- zero-length frames as an explicit "nothing to send this turn" marker;
- a 4 MiB maximum frame;
- 128 maximum sync rounds;
- a 10 second synchronization timeout.

## Persistence

A replica persists both:

1. the Automerge document bytes; and
2. `sync::State::encode()` for the bound peer.

Restore validates that the saved sync state is being reused for the same endpoint/principal binding before decoding it. This prevents accidental peer-state reuse after identity changes.

## Authority boundary

This crate exposes only:

- `NonAuthoritative`;
- `DerivedProjection`;
- `PendingProposal`.

There is no authoritative state-class constructor.

`request_authority_promotion()` returns only a `PromotionProposal` and requires a governing KPGS task-receipt reference. QUIC/TLS authentication, successful CRDT convergence, endpoint identity, and network reachability never imply authorization.

## Tests

The live integration lane proves:

1. two independently modified documents converge through a real iroh QUIC connection;
2. both peers finish with matching Automerge heads;
3. document bytes and per-peer Automerge sync state survive replica recreation and continue syncing on a later connection;
4. an authenticated iroh connection is still rejected when its endpoint ID does not match the expected KPGS endpoint→principal binding;
5. all synchronized state remains `authority_effect = none`, with promotion proposal-only.

## Deliberate exclusions

This POC does not yet implement:

- relay-assisted internet traversal;
- multi-hop gossip;
- device key rotation/revocation;
- KPGS capability-lease exchange over the stream;
- encrypted application payloads beyond transport TLS;
- persistence to SQLite/PostgreSQL;
- automatic authority promotion;
- production Automerge document compaction/retention policy.

The next gate after this passes is to bind the iroh endpoint/principal mapping to the merged `KPGSTaskReceipt v0.1` capability contract and add explicit key-rotation/revocation tests.
