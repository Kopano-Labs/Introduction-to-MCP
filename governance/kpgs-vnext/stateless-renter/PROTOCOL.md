# Canonical Stateless Renter Protocol vNext

Issue: #34

Runtime protocol version: `1.1`

## 1. Purpose

A **Stateless Renter** is a disposable execution unit that temporarily leases authority and context from KPGS. It may compute, call tools, emit events and produce evidence, but it is never the landlord of canonical business/governance state.

The renter contract exists so KPGS can evolve domain applications independently while preserving one reproducible governance boundary.

The admission law for agentic orchestration is:

```text
MODELS COMPETE FOR CAPABILITY.
AGENTS EARN TRUST.
SEATS CARRY AUTHORITY.
KPGS GOVERNS THE DIFFERENCE.
```

A model/provider/benchmark result is capability evidence only. It MUST NOT be treated as MAO/MMAO execution authority.

## 2. Normative lifecycle

```text
discover -> prove -> trust -> lease -> hydrate -> execute -> emit -> checkpoint -> release
```

### discover
The renter declares runtime identity, protocol version and supported capabilities. Discovery does not grant authority.

### prove
The renter produces receipts that KPGS can evaluate: bounded execution evidence, BlackMask/verification results, teacher/reviewer decisions, recovery behavior, and other domain-approved proof. A claim that the model is "frontier", "smart", "trusted", named, or highly ranked is not proof.

### trust
Before a stateless renter enters an `MAO` or `MMAO` cycle, KPGS MUST issue an evidence-backed trust grant. The trust grant is identity-bound, tenant/domain-bound, cycle-scoped, expiring, and receipt-bearing.

No trust grant means no orchestration entry.

### lease
Only after the trust gate passes for MAO/MMAO may the Sovereign Hub honor or issue a short-lived capability lease scoped to tenant, domain, task, resources and permitted operations.

### hydrate
The renter receives only the governed context required for the task. Hydration data carries version and provenance metadata.

### execute
The renter performs the bounded task. Every side effect MUST be idempotent or protected by an idempotency key.

### emit
Progress, decisions, tool outcomes and failures are emitted as typed events with tenant/task/correlation identifiers.

### checkpoint
A renter may emit a checkpoint reference into canonical storage. A checkpoint is evidence/state owned by the Hub or declared canonical domain store; it is not renter-local authority.

### release
The renter returns completion/failure evidence and releases/forgets its capability lease, trust material and task-local material.

## 3. KPGS trust admission gate

The canonical orchestration admission predicate is:

```text
ENTER(cycle, renter) =
  cycle in {MAO, MMAO}
  AND trust_state == trusted
  AND issuer == KPGS
  AND renter_id matches
  AND tenant/domain scope matches
  AND cycle is explicitly allowed
  AND trust grant is unexpired
  AND evidence_refs is non-empty
```

If any predicate is false:

```text
event_kind = policy.denied
failure.code = trust_not_earned
handler_execution = false
```

Trust MUST be earned from receipts. It MUST NOT be inferred from:

- model family or provider;
- benchmark rank;
- parameter count or context-window size;
- naming/persona continuity;
- prior conversation warmth;
- discovery success;
- local cached credentials;
- a previous renter process merely claiming it was trusted.

The governing promotion invariant remains:

```text
No promotion without proof. Drill is not graduation.
```

`Structure/07-Agents/PROMOTION_LAW.json` remains the canonical promotion-law anchor. A KPGS trust grant MAY reference promotion evidence, but trust admission and public graduation remain separate decisions.

### Trust is scoped authority, not permanent identity

A grant applies only to its declared renter, tenant/domain and allowed orchestration cycle(s). Expiry or scope mismatch MUST fail closed.

A replacement runtime may inherit a governed seat/context only when KPGS rehydrates valid trust evidence or issues a fresh grant. Model replacement alone MUST NOT transfer authority.

## 4. Canonical identifiers

Every governed execution MUST carry:

- `tenant_id`
- `domain_id`
- `task_id`
- `renter_id`
- `correlation_id`
- `lease_id`
- `protocol_version`
- `issued_at`

Where a message can cause a durable side effect, it MUST also carry `idempotency_key`.

Where execution occurs inside MAO/MMAO, the event SHOULD also carry:

- `orchestration_cycle`
- `trust_grant_id`

## 5. Capability lease

A capability lease MUST be:

- short-lived;
- signed or otherwise integrity-protected;
- bound to tenant/domain/task;
- explicit about allowed operations/resources;
- revocable;
- rejected after expiry;
- unusable outside the declared scope.

A capability lease does not substitute for a KPGS trust grant. For MAO/MMAO, both gates apply:

```text
KPGS_TRUST_PASS
AND
CAPABILITY_LEASE_PASS
-> MAY_EXECUTE
```

A renter MUST NOT derive additional privilege from local configuration, cached credentials or undocumented environment variables.

## 6. Hydration contract

Hydration MUST be deterministic enough that a replacement renter can reconstruct the same governed task context from canonical sources.

Hydration SHOULD include:

- governing specification reference;
- accepted input payload;
- task policy/capability scope;
- required skill versions;
- current checkpoint reference if resuming;
- environment/runtime contract;
- evidence correlation metadata;
- orchestration cycle when applicable;
- current KPGS trust-grant reference when applicable.

Hydration MUST NOT silently import unrelated tenant/user history.

## 7. Event envelope

Renter events use the machine-readable envelope in `renter-envelope.schema.json`.

Canonical event kinds:

- `task.accepted`
- `task.started`
- `task.progress`
- `task.awaiting_approval`
- `task.checkpointed`
- `task.completed`
- `task.failed`
- `policy.denied`
- `capability.expired`
- `evidence.emitted`

Canonical trust admission failure:

- `trust_not_earned`

The grant format is defined by `trust-grant.schema.json`.

## 8. State rules

Allowed renter-local state:

- request-scoped working memory;
- caches that can be safely discarded;
- transient transport/session state;
- temporary files whose loss cannot invalidate canonical truth.

Forbidden renter-local canonical state:

- production source of truth;
- long-lived credentials;
- sole audit history;
- sole workflow progress record;
- hidden tenant profile required to resume execution;
- self-issued or locally persisted trust authority.

## 9. Replay and idempotency

Retries and replay are normal operating conditions.

A side-effecting operation MUST either:

1. be naturally idempotent; or
2. consume an `idempotency_key` in the canonical domain/service boundary.

Duplicate messages MUST NOT duplicate durable side effects.

Trust replay is also bounded: a previously observed trust grant may be reused only while its identity, tenant/domain, cycle and expiry predicates remain valid.

## 10. Rehydration test

A renter implementation is conformant only if this test passes:

1. start a governed task;
2. if MAO/MMAO, prove KPGS trust admission before execution;
3. emit progress/checkpoint evidence;
4. destroy the renter process;
5. create a replacement renter;
6. hydrate from canonical sources;
7. revalidate trust and capability scope;
8. resume or safely restart according to the spec;
9. complete without duplicated durable side effects;
10. produce a continuous evidence chain.

## 11. Failure semantics

Failures MUST be classified at least as:

- `input_invalid`
- `policy_denied`
- `trust_not_earned`
- `capability_expired`
- `dependency_unavailable`
- `timeout`
- `execution_failed`
- `verification_failed`
- `cancelled`

A failure MUST include a machine code and a plain-language recoverability hint. Sensitive internals MUST NOT be exposed to end users.

## 12. Conformance

A conformant renter MUST demonstrate:

- disposable/re-hydratable execution;
- no ambient long-lived credentials;
- KPGS trust-gate enforcement before MAO/MMAO execution;
- evidence-backed, identity/scope/expiry-bound trust;
- capability-scope enforcement;
- replay-safe side effects;
- typed event/evidence emission;
- protocol version negotiation;
- deterministic failure classification;
- recovery after process destruction.

`I_AM_STATELESS_RENTER_NOT_LANDLORD` remains a semantic invariant, not merely a banner string.
