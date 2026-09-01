# KPGS vNext — Sovereign Hub Re-engineering

Status: **Architecture substrate complete; live estate operations continue under fresh receipts**
Epic: #46 (closed 2026-08-24)
Continuity lane: #101
Live estate operations: #102

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
17. Repository-root `NOW.md` is the volatile/current-state authority for work in this repository; model memory and nested/personal `Now.md` files do not supersede it.
18. CCP/CDP direction MUST NOT be encoded as a universal pipeline. Situational transitions admit `CCP | CDP | CONVERGE | DIVERGE | HOLD` from current state, knowable evidence and governance invariants.
19. `HOLD` is a valid governance outcome when evidence, authority or continuity is insufficiently knowable.
20. Socio-technical POC MUST NOT be inferred from software tests alone; external human/economic claims require field evidence.

## Control loops

### Engineering
`specify -> delegate -> execute -> verify -> steer -> ship`

### Evaluation
`prepare -> execute -> verify/profile -> score -> improve -> promote | rollback`

### Runtime
`discover -> lease -> hydrate -> execute -> emit -> checkpoint -> release`

### Product feedback
`ship -> observe -> learn -> reshape`

### Continuity / temporal state

```text
assert stateless renter
  -> load durable Legacy purpose
  -> read repository-root NOW.md
  -> classify evidence before interpretation
  -> recover admitted lane + blockers + receipts
  -> execute within authority
  -> receipt material work
  -> update NOW.md before material handoff
```

See `continuity/README.md`, `continuity/situational-transition.schema.json`, root `NOW.md`, root `AGENTS.md`, and the canonical Stateless Renter Entryway.

### Situational PKA transition law

```text
S_t = current state
K_t = currently knowable evidence
G   = governance invariants

T(S_t, K_t, G)
  -> CCP
  -> CDP
  -> CONVERGE
  -> DIVERGE
  -> HOLD
```

Every bounded transition is explainable as:

`trigger -> evidence -> invariant -> authority -> transition -> receipt`

The invariant is not a fixed CCP/CDP direction. The invariant is the law deciding whether the situational edge is admissible.

Canonical doctrine: **Do not prescribe the universe. Govern the transition.**

### Capability Factory

KPGS should graduate reusable web/system capabilities rather than rebuild identical infrastructure per DNS:

```text
Capability
  -> Contract
  -> Implementation
  -> Test
  -> Receipt
  -> POC
  -> Reusable Primitive
```

Candidate classes include components, auth, commerce, dashboards, CMS/content, deployment, telemetry, testing, SEO/indexing and APWA/offline/adaptive primitives. Reuse without proof metadata is not yet a KPGS-graduated primitive.

### KasiLink employment feedback

```text
Discover
  -> Access
  -> Understand
  -> Learn
  -> Validate capability
  -> Trust validation
  -> Transact
  -> Get paid
  -> Telemetry
  -> Improve
```

The proof surface must eventually include weak-device/low-data access, fraud resistance, trusted validation, completed transactions/payment, scale and reproducibility. Agent observation does not grant ambient production authority.

### Vanguard C reality validation

Kopano Labs Intern Vanguard C is the field-validation lane for claims that leave the software boundary: human trust, procurement, manufacturing, regulation, education, organizational adoption, capital formation, physical logistics, relationships and market demand.

Field observations return as evidence/receipts; they do not automatically promote universal claims.

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
- **Phase 1 — Governance substrate:** identity/capability leases, Sovereign Hub registry, evidence model. **Complete.**
- **Phase 2 — Runtime packages:** .NET domain adapter, skill runtime, realtime event plane. **Complete as architecture/runtime substrate.**
- **Phase 3 — Validation + human experience:** evaluation loop and Sovereign Everyday Mode. **Complete as architecture/reference proof.**
- **Phase 4 — Estate migration architecture:** reusable migration membrane/playbook. **Complete.**
- **Ongoing estate operations:** real provider/DNS admission, cutover, observation and rollback receipts continue per-property in fresh operational lanes such as #102.

## Canonical artifacts

### Phase 0 / shared substrate

- `stateless-renter/PROTOCOL.md`
- `stateless-renter/renter-envelope.schema.json`
- `agent-governance/SPECIFICATION.md`
- `agent-governance/build-spec.schema.json`
- `agent-governance/mmao-mao/README.md`
- `agent-governance/mmao-mao/identity-provenance.schema.json`
- `agent-governance/mmao-mao/authority-boundary.schema.json`
- `agent-governance/mmao-mao/model-interface-affinity-experiment.schema.json`
- `agent-governance/mmao-mao/failure-receipt.schema.json`
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

### Continuity / situational governance

- `continuity/README.md`
- `continuity/situational-transition.schema.json`
- repository-root `NOW.md`
- repository-root `AGENTS.md`
- `Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/MAIN-BRAIN/STATELESS_RENTER_ENTRYWAY.md`
- `Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/MAIN-BRAIN/STATELESS_RENTER_ENTRYWAY.json`

### MMAO + MAO identity-governance POC

The current controlled experiment lives at `agent-governance/mmao-mao/`. It records identity, seat, interface, model/version, task, task-scoped authority, context state, and evidence separately. It preserves a strict distinction between high task authority and GSMB structural-maintenance authority, and it keeps model x interface affinity as an unrun hypothesis until controlled receipts exist.

## Definition of done

A meaningful user workflow is only `released` when KPGS can prove:

`request -> governing spec -> capability lease -> renter/skill execution -> evidence -> governance decision -> live release -> rollback path`

That proof MUST survive destruction and recreation of the executing renter.

A socio-technical outcome is only POC-validated when the corresponding real-world consequence has its own admissible evidence; deployment success alone cannot substitute for human/economic validation.
