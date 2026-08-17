# KPGS Offline Replication Contract v0.1

Status: **Phase 0 / convergence-safety POC / non-production**

This slice proves one sovereign-runtime law in executable form:

> **Availability and synchronization are not authority.**

A device may continue producing benign local state while disconnected. Peer replicas may later exchange, deduplicate, and converge that state. None of those operations grant permission to mutate KPGS constitutional truth.

## Why this slice exists

KPGS already requires realtime transports to remain subordinate to canonical workflow state. The same rule must hold when the transport becomes peer-to-peer and the state layer becomes CRDT-like.

```text
LOCAL DEVICE STATE
      │
      ├── works offline
      ├── persists locally
      └── emits non-authoritative operations
                  │
                  ▼
           peer synchronization
                  │
          duplicate/reorder safe
                  │
                  ▼
         deterministic convergence
                  │
                  X
           NO AUTHORITY JUMP
                  │
                  ▼
       governed promotion proposal
                  │
                  ▼
        KPGS task/policy/receipt gate
```

## Executable POC

`replication_contract.py` implements a small transport-neutral Last-Write-Wins map CRDT:

- operations are immutable and content-hashed;
- operation IDs are replica/counter scoped;
- merge is set union;
- visible values are projected by a deterministic Lamport-counter + replica-ID ordering;
- duplicate and reordered delivery is idempotent;
- peer identity is bound to an expected principal before imported operations enter the projection;
- local state can be serialized, destroyed, restored, and synchronized again;
- replicated records are locked to `authority_effect = "none"`;
- direct mutation of the canonical authority store is refused;
- promotion produces only a proposal and requires an explicit governing task-receipt reference;
- provenance is hash-first so private source content does not enter replication metadata by default.

The POC intentionally accepts only operations originated by the sending peer. Forwarded/gossip operations remain a later protocol gate so transitive trust cannot appear accidentally.

## State classes

The v0.1 replicated surface admits only:

- `non_authoritative` — local user/runtime state with no governance effect;
- `derived_projection` — a cache/view derived from authoritative sources;
- `pending_proposal` — candidate state awaiting a separate governance decision.

`constitutional_truth` and any other authoritative state class are rejected.

## Transport boundary

The core contract deals in deterministic bytes:

```text
LocalReplica
   ↓ export_batch()
ReplicaBatch bytes
   ↓
transport adapter
   ↓
peer
   ↓ import_batch()
LocalReplica
```

The transport may later be:

- iroh;
- LAN/local IPC;
- WebSocket;
- Bluetooth-adjacent bridge;
- store-and-forward;
- another byte-oriented peer channel.

The transport cannot widen authority.

## Automerge / iroh placement

This POC deliberately locks the governance semantics **before** introducing networking dependencies.

The intended live experiment is:

```text
KPGS non-authoritative state contract
            │
            ▼
      Automerge document
            │
       sync messages
            │
            ▼
      iroh byte channel
            │
            ▼
       trusted peer
```

Automerge/iroh may replace the POC merge/transport machinery after their adapter passes the same conformance tests. They may not replace the KPGS authority membrane.

## Conformance gates

`tests/test_kpgs_offline_replication.py` proves:

1. two disconnected peers can perform concurrent benign writes and later converge;
2. equal-clock conflicts resolve deterministically independent of delivery order;
3. duplicate delivery creates no duplicate state effect;
4. untrusted peers are rejected before projection;
5. trusted peer IDs are bound to expected principals;
6. batch tampering is detected;
7. local persistence survives replica recreation and can resynchronize;
8. converged state cannot directly mutate canonical authority;
9. authority promotion requires a governing task receipt and yields a proposal only;
10. authoritative state classes/authority effects are refused;
11. provenance enters the replicated surface as a hash, not source payload.

## Relationship to Sovereign Everyday Mode

A PWA can safely show `offline` or `reconnecting` while continuing to mutate permitted local state. On reconnect, authoritative task/workflow state still refreshes from the canonical KPGS surface before client-only state is trusted.

This means:

```text
offline continuity     YES
local preferences      YES
non-authoritative UX   YES
cached projections     YES

silent privilege       NO
canonical task rewrite NO
policy bypass          NO
receipt fabrication    NO
```

## Scope boundary

This branch does **not** claim:

- production CRDT storage;
- Automerge integration;
- live iroh networking;
- multi-hop gossip;
- cryptographic peer signatures;
- key rotation/revocation;
- production encryption at rest;
- authoritative distributed consensus;
- automatic promotion of replicated state.

Those remain separate gates.

The next transport experiment should implement the current Automerge synchronization model over a current iroh byte channel and run this contract's partition, replay, tamper, restoration, and authority-separation tests against the live adapter.
