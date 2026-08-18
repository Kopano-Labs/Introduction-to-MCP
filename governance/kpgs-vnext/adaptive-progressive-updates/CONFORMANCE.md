# Downstream SWFUS Conformance

A domain implementation conforms only when it proves all of the following:

1. It consumes or mirrors `kpgs.swfus.update.v1` without changing semantics.
2. CREATE produces the first active revision and cannot silently overwrite an active node.
3. READ observes the current witness without rewriting it or invoking mutation/synchronization side effects; its `syncState` is `not_applicable`.
4. UPDATE can reject a stale `expectedRevision`.
5. DELETE produces an evidence-preserving tombstone/revision.
6. A rejected update does not erase the last accepted witness.
7. Offline/transport failure preserves an accepted local witness as `pending_sync`.
8. `synced` is emitted only after observed external acceptance.
9. Every accepted/rejected transition exposes a receipt/evidence reference.
10. The same `correlationId` + same payload can be retried without a second CRUD mutation; correlation reuse with different payload content fails closed.
11. User-facing adaptive rendering profiles do not change the update's authority or truth semantics.
12. Private/transactional operations remain capability/policy gated and are never smuggled into a public offline cache lane.

A downstream PR should identify the exact Introduction-to-MCP commit/contract revision used and attach automated evidence for these invariants before promotion.
