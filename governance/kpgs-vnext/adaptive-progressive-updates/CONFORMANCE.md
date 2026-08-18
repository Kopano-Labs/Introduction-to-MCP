# Downstream SWFUS Conformance

A domain implementation conforms only when it proves all of the following:

1. It consumes or mirrors `kpgs.swfus.update.v1` without changing semantics.
2. CREATE produces the first active revision and cannot silently overwrite an active node.
3. UPDATE can reject a stale `expectedRevision`.
4. DELETE produces an evidence-preserving tombstone/revision.
5. A rejected update does not erase the last accepted witness.
6. Offline/transport failure preserves an accepted local witness as `pending_sync`.
7. `synced` is emitted only after observed external acceptance.
8. Every accepted/rejected transition exposes a receipt/evidence reference.
9. The same `correlationId` + same payload can be retried without a second CRUD mutation; correlation reuse with different payload content fails closed.
10. User-facing adaptive rendering profiles do not change the update's authority or truth semantics.
11. Private/transactional operations remain capability/policy gated and are never smuggled into a public offline cache lane.

A downstream PR should identify the exact Introduction-to-MCP commit/contract revision used and attach automated evidence for these invariants before promotion.
