# Changelog

## 1.0.0-poc.1 — 2026-08-18

- Canonicalize Adaptive PU → Progressive Update → CRUD → SWFUS flow.
- Replace simulated ingestion/synchronization claims with receipt-bearing evidence states.
- Add revision conflicts, tombstones, quarantine ledger and offline `pending_sync` behavior.
- Add correlation-bound idempotency so reconnect retries cannot duplicate CRUD mutation.
- Reject reuse of a correlation ID for different payload content.
- Make READ a side-effect-free witness observation with `syncState=not_applicable`.
- Preserve legacy telemetry ingestion as a compatibility adapter.
- Add portable cross-runtime schema, fixture, mapping and downstream conformance gates.
