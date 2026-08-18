# KPGS Adaptive Progressive Updates

This directory is the canonical vNext contract surface for turning a live Adaptive PWA state change into a governed, evidence-bearing update.

```text
Adaptive PU
  -> Progressive Update
  -> CRUD intent
  -> SWFUS witness/sync/severance
  -> receipt
  -> user-visible feedback
```

## Canonical files

- `SWFUS_CRUD_CONTRACT.md` — human-readable governance contract.
- `swfus-update.schema.json` — cross-runtime wire shape for progressive updates and receipts.
- `../../../kopano-core/kopano/swfus_engine.py` — executable Python reference runtime.
- `../../../tests/test_swfus_engine.py` — executable invariants.

## Boundary

A domain may implement this wire contract in TypeScript, .NET, Python or another runtime. It must not invent a competing semantic meaning for `synced`, `pending_sync`, `severed`, revisions, tombstones or evidence receipts.

A domain implementation is an **adapter of the canonical contract**, not a new canonical SWFUS authority.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
