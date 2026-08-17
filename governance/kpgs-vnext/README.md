# KPGS vNext — Sovereign Hub Re-engineering

Status: **Phase 0 — Truth and Contracts**
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

## Control loops

### Engineering
`specify -> delegate -> execute -> verify -> steer -> ship`

### Evaluation
`prepare -> execute -> verify/profile -> score -> improve -> promote | rollback`

### Runtime
`discover -> lease -> hydrate -> execute -> emit -> checkpoint -> release`

### Product feedback
`ship -> observe -> learn -> reshape`

## Phase map

- **Phase 0 — Truth and contracts:** fork assimilation, renter protocol, specification-first governance.
- **Phase 1 — Governance substrate:** identity/capability leases, Sovereign Hub registry, evidence model.
- **Phase 2 — Runtime packages:** .NET domain adapter, skill runtime, realtime event plane.
- **Phase 3 — Validation + human experience:** evaluation loop and Sovereign Everyday Mode.
- **Phase 4 — Estate proof:** migrate one bounded low-risk workflow, prove rollback, then expand.

## Phase 0 artifacts

- `stateless-renter/PROTOCOL.md`
- `stateless-renter/renter-envelope.schema.json`
- `agent-governance/SPECIFICATION.md`
- `agent-governance/build-spec.schema.json`
- `fork-assimilation/evolution-matrix.json`
- `task-contract/README.md`
- `task-contract/principal-envelope.schema.json`
- `task-contract/task-receipt.schema.json`
- `task-contract/adapter.py`

## Definition of done

A meaningful user workflow is only `released` when KPGS can prove:

`request -> governing spec -> capability lease -> renter/skill execution -> evidence -> governance decision -> live release -> rollback path`

That proof MUST survive destruction and recreation of the executing renter.
