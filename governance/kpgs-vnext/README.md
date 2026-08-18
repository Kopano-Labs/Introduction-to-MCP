# KPGS vNext — Sovereign Hub Re-engineering

Status: **Phase 1 — Governance Substrate / Evidence Completion**
Epic: #46

KPGS vNext makes `Introduction-to-MCP` the canonical specification and governance layer for the Kopano DNS estate. Existing frontends may remain React/Next/Vite/PWA or other appropriate stacks; the canonical integration boundary is a governed domain adapter, Sovereign Hub, Stateless Renter protocol, skill runtime, realtime event plane and evidence system.

## Canonical operating model

```text
Everyday User
    |
    v
Adaptive PWA / Existing Domain UI
    |
    v
Canonical Domain Adapter (.NET reference boundary)
    |
    v
Kopano Sovereign Hub
    |-- DNS Estate Registry
    |-- Identity + Capability Leases
    |-- Skill Registry / Router
    |-- Governance / Policy
    |-- Realtime Event Plane
    `-- Evidence + Evaluation
    |
    v
Canonical Stateless Renter(s)
    |
    v
Tools / APIs / Domain Systems
```

## Invariants

1. Durable authority and canonical business state MUST NOT live inside a Stateless Renter.
2. A renter MUST be disposable and re-hydratable from governed context.
3. Privileged actions MUST resolve explicit capability scope; ambient authority is forbidden.
4. Governed implementation begins from an explicit specification and acceptance criteria.
5. Verification evidence precedes production promotion.
6. Realtime transports improve interaction but MUST NOT become canonical storage.
7. Existing frontends MUST NOT be rewritten solely to satisfy control-plane standardisation.
8. Adaptive warmth/tone/detail is runtime interaction configuration; it MUST NOT be represented as model-weight fine-tuning.
9. Imported/fork-derived code and assets require provenance, license, security and compatibility review.
10. Newly discovered DNS properties remain `unwitnessed` until ownership and governance admission are validated.
11. Availability, replication and synchronization MUST NOT be interpreted as authority.
12. Mutating CRUD MUST NOT occur before invariant and POC/FOC governance has passed.
13. Authentication establishes identity; privileged execution additionally requires a live, exact-scoped capability lease.
14. Lease signing material and durable provider credentials MUST NOT be owned by a Stateless Renter or frontend.
15. Aggregate scores MUST NOT hide a failed hard governance or security gate.
16. Production promotion MUST identify the exact release/commit and the canonical evidence bundle that justified it.

## Control loops

### Engineering
`specify -> delegate -> execute -> verify -> steer -> ship`

### Evaluation
`prepare -> execute -> verify/profile -> score -> improve -> promote | rollback`

### Runtime
`discover -> lease -> hydrate -> execute -> emit -> checkpoint -> release`

### Product feedback
`ship -> observe -> learn -> reshape`

### Adaptive progressive state

```text
APU (Adaptive Progressive Updates)
  -> Progressive Update
  -> #NB
  -> bounded CRUD
  -> SWFUS (State-Wide Framework Universal Synchronization)
```

The canonical SWFUS stage law is:

`telemetry -> classification -> routing -> protocol selection -> invariant audit -> POC/FOC check -> state update -> distribution`

CRUD mutates only admitted bounded state. SWFUS distributes/aligns the resulting framework projection only after governance; it is not canonical authority and it does not replace the Sovereign Hub, evidence system, capability leases, realtime event plane or durable domain stores. `#NB` is preserved as an explicit boundary marker without inventing an expansion.

See `progressive-updates/README.md` and `progressive-updates/progressive-update.schema.json`.

### Capability authority

```text
authenticated identity
  -> policy + governing specification
  -> short-lived capability lease
  -> exact tenant/domain/task/capability/resource check
  -> sensitive operation nonce
  -> execution
  -> audit/evidence
```

The reference capability runtime is intentionally server-side. OIDC/JWT/session identity may exist upstream, but no identity token alone becomes ambient execution authority. Key rotation is resolved by the issuing authority through signed lease `kid` metadata; an Adaptive PWA does not need redeployment to rotate Sovereign Hub signing keys.

See `security/CAPABILITY_LEASE.md`, `security/capability-lease.schema.json`, and `security/capability_lease.py`.

### Sovereign estate authority

```text
discover
  -> unwitnessed queue
  -> witness
  -> classify
  -> register
  -> staging
  -> production
  -> observe
  -> rollback | suspend | decommission
```

The estate registry is canonical control-plane state. Unknown properties never self-promote from connector visibility, public search or transport discovery. Production transitions require release evidence and rollback receipts, while realtime/SWFUS distribution remains non-authoritative projection alignment.

See `estate-registry/README.md`, `estate-registry/registry.py`, `estate-registry/estate-registry.schema.json`, and `estate-registry/discovery-candidate.schema.json`.

### Evidence and scorecards

```text
estate property
  -> exact release + commit
  -> adapter
  -> renter
  -> skill
  -> task/session
  -> verifier
  -> governance decision
  -> engineering scorecard
  `-> everyday governance scorecard
```

One canonical evidence bundle feeds both scorecards. Hard gates remain independent from aggregate scores. Secret-bearing material is rejected from bundle metadata, retention/redaction policy references are mandatory, and rollback assessment can recommend—but never directly execute—a rollback without the separately governed rollback capability.

See `evidence/EVIDENCE.md`, `evidence/evidence-bundle.schema.json`, and `evidence/evidence.py`.

## Phase map

- **Phase 0 — Truth and contracts:** fork assimilation, renter protocol, specification-first governance. **Complete.**
- **Phase 1 — Governance substrate:** identity/capability leases, Sovereign Hub registry, evidence model. **Implementation complete on this branch; final evidence CI/promotion pending.**
- **Phase 2 — Runtime packages:** .NET domain adapter, skill runtime, realtime event plane.
- **Phase 3 — Validation + human experience:** evaluation loop and Sovereign Everyday Mode.
- **Phase 4 — Estate proof:** migrate one bounded low-risk workflow, prove rollback, then expand.

## Canonical artifacts

### Phase 0 / shared substrate

- `stateless-renter/PROTOCOL.md`
- `stateless-renter/renter-envelope.schema.json`
- `agent-governance/SPECIFICATION.md`
- `agent-governance/build-spec.schema.json`
- `fork-assimilation/evolution-matrix.json`
- `task-contract/README.md`
- `task-contract/principal-envelope.schema.json`
- `task-contract/task-receipt.schema.json`
- `task-contract/adapter.py`
- `progressive-updates/README.md`
- `progressive-updates/progressive-update.schema.json`

### Phase 1 / governance substrate

- `security/CAPABILITY_LEASE.md`
- `security/capability-lease.schema.json`
- `security/capability_lease.py`
- `estate-registry/README.md`
- `estate-registry/estate-registry.schema.json`
- `estate-registry/discovery-candidate.schema.json`
- `estate-registry/estate.json`
- `estate-registry/registry.py`
- `evidence/EVIDENCE.md`
- `evidence/evidence-bundle.schema.json`
- `evidence/evidence.py`

## Definition of done

A meaningful user workflow is only `released` when KPGS can prove:

`request -> governing spec -> capability lease -> renter/skill execution -> evidence -> governance decision -> live release -> rollback path`

That proof MUST survive destruction and recreation of the executing renter.
