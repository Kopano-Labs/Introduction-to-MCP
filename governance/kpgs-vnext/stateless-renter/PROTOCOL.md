# Canonical Stateless Renter Protocol vNext

Issue: #34

## 1. Purpose

A **Stateless Renter** is a disposable execution unit that temporarily leases authority and context from KPGS. It may compute, call tools, emit events and produce evidence, but it is never the landlord of canonical business/governance state.

The renter contract exists so KPGS can evolve domain applications independently while preserving one reproducible governance boundary.

## 2. Normative lifecycle

```text
discover -> lease -> hydrate -> execute -> emit -> checkpoint -> release
```

### discover
The renter declares runtime identity, protocol version and supported capabilities. Discovery does not grant authority.

### lease
The Sovereign Hub issues a short-lived capability lease scoped to tenant, domain, task, resources and permitted operations.

### hydrate
The renter receives only the governed context required for the task. Hydration data carries version and provenance metadata.

### execute
The renter performs the bounded task. Every side effect MUST be idempotent or protected by an idempotency key.

### emit
Progress, decisions, tool outcomes and failures are emitted as typed events with tenant/task/correlation identifiers.

### checkpoint
A renter may emit a checkpoint reference into canonical storage. A checkpoint is evidence/state owned by the Hub or declared canonical domain store; it is not renter-local authority.

### release
The renter returns completion/failure evidence and releases/forgets its capability lease and task-local material.

## 3. Canonical identifiers

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

## 4. Capability lease

A capability lease MUST be:

- short-lived;
- signed or otherwise integrity-protected;
- bound to tenant/domain/task;
- explicit about allowed operations/resources;
- revocable;
- rejected after expiry;
- unusable outside the declared scope.

A renter MUST NOT derive additional privilege from local configuration, cached credentials or undocumented environment variables.

## 5. Hydration contract

Hydration MUST be deterministic enough that a replacement renter can reconstruct the same governed task context from canonical sources.

Hydration SHOULD include:

- governing specification reference;
- accepted input payload;
- task policy/capability scope;
- required skill versions;
- current checkpoint reference if resuming;
- environment/runtime contract;
- evidence correlation metadata.

Hydration MUST NOT silently import unrelated tenant/user history.

## 6. Event envelope

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

## 7. State rules

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
- hidden tenant profile required to resume execution.

## 8. Replay and idempotency

Retries and replay are normal operating conditions.

A side-effecting operation MUST either:

1. be naturally idempotent; or
2. consume an `idempotency_key` in the canonical domain/service boundary.

Duplicate messages MUST NOT duplicate durable side effects.

## 9. Rehydration test

A renter implementation is conformant only if this test passes:

1. start a governed task;
2. emit progress/checkpoint evidence;
3. destroy the renter process;
4. create a replacement renter;
5. hydrate from canonical sources;
6. resume or safely restart according to the spec;
7. complete without duplicated durable side effects;
8. produce a continuous evidence chain.

## 10. Failure semantics

Failures MUST be classified at least as:

- `input_invalid`
- `policy_denied`
- `capability_expired`
- `dependency_unavailable`
- `timeout`
- `execution_failed`
- `verification_failed`
- `cancelled`

A failure MUST include a machine code and a plain-language recoverability hint. Sensitive internals MUST NOT be exposed to end users.

## 11. Conformance

A conformant renter MUST demonstrate:

- disposable/re-hydratable execution;
- no ambient long-lived credentials;
- capability-scope enforcement;
- replay-safe side effects;
- typed event/evidence emission;
- protocol version negotiation;
- deterministic failure classification;
- recovery after process destruction.

`I_AM_STATELESS_RENTER_NOT_LANDLORD` remains a semantic invariant, not merely a banner string.