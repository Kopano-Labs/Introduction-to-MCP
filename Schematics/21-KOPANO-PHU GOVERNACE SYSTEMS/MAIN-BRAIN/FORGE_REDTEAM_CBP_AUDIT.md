# Forge Red-Team Audit — CBP Gap Analysis

> **Agent:** Forge (ChatGPT-5.5 MED) — 2nd Wife
> **Date:** 2026-06-15
> **Target:** Context Bleed Protocol (CBP) Phase 3.2
> **Verdict:** "Phase 3.2 narrative architecture — not yet Phase 3.2 hardened runtime"

---

## 10 Hard Gaps Identified

| # | Gap | Risk | Required Fix |
|---|-----|------|-------------|
| 1 | **No idempotency** | Duplicate writes, replay on reconnect | `eventId` as global immutable key, server-side dedupe, ack receipt |
| 2 | **Unsafe buffer clearing** | Silent partial failure destroys unsynced records | Per-record sync status, append-only log, compact only confirmed |
| 3 | **No conflict model** | Concurrent offline edits across nodes | Event sourcing or CRDT/LWW policy, conflict class definitions |
| 4 | **localStorage wrong substrate** | Small quota, blocking API, poor reliability | IndexedDB, durable queue abstraction, encrypted-at-rest shard |
| 5 | **No auth/security model** | `X-Partner-ID` is not security | Device identity, signed payloads, token rotation, replay protection |
| 6 | **No backoff/retry policy** | Catch and exit on error | Exponential backoff with jitter, retry classes, dead-letter queue |
| 7 | **No observability contract** | Console logs not operations-grade | Sync metrics, queue depth, latency, rejection rate, per-node health |
| 8 | **Policy gate underspecified** | `AltarGate.verify()` conceptual only | Deterministic policy schema, rule versioning, audit trace |
| 9 | **No schema governance** | No event versioning | Payload schema version, migration contract, compatibility matrix |
| 10 | **Math block not executable** | Growth coefficient is branding | Define inputs, units, thresholds, enforcement consequences, tests |

## Required LocalEvent Type

```typescript
type LocalEvent = {
  eventId: string;
  deviceId: string;
  shardId: string;
  schemaVersion: string;
  createdAt: string;
  type: string;
  payload: unknown;
  policyRef?: string;
  status: "pending" | "inflight" | "acked" | "rejected" | "deadletter";
  retryCount: number;
  lastError?: string;
};
```

## Required SyncAck Type

```typescript
type SyncAck = {
  eventId: string;
  status: "accepted" | "duplicate" | "rejected";
  serverTime: string;
  receiptId: string;
  reason?: string;
};
```

## Required Execution Loop

1. Read oldest pending batch
2. Mark inflight with lease
3. Evaluate policy
4. Sign request
5. POST batch with idempotency keys
6. Persist ack per event
7. Only compact acked records
8. Park rejected in audit stream
9. Retry transient failures
10. Emit metrics

---

## Antigravity Response

All 10 gaps addressed in governance.js CBP rewrite. See commit history.

## Links

- [[VANGUARD_APEX_GSMB_THESIS|Vanguard-Apex Thesis]]
- [[KPGS_THESIS_MMAO|MMAO Thesis]]
