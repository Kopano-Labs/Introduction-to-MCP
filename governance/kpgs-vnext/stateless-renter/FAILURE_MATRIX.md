# Stateless Renter Failure and Recovery Matrix

Issue: #34

Failures never widen renter authority or move canonical state into the renter process.

| Failure code | Typical source | Recoverability | Required behavior |
|---|---|---|---|
| `input_invalid` | Payload or orchestration classification violates declared input contract | `user_action` / `operator_action` | Reject before durable side effects. |
| `policy_denied` | Tenant/task/operation/resource outside capability lease | `operator_action` | Do not invoke the workload handler. |
| `trust_not_earned` | Missing, expired, self-issued, identity-mismatched, cycle-mismatched, or evidence-empty KPGS trust grant | `operator_action` | Deny MAO/MMAO entry before capability or handler execution. |
| `role_not_fit` | Renter is trusted but the current decision domain, consequence class, or authority mode is outside the grant | `operator_action` | Preserve trust receipt, deny this role, and route to an appropriately fit validator/executor. |
| `capability_expired` | Short-lived lease expired | `rehydrate` | Reject execution and obtain a fresh governed lease. |
| `dependency_unavailable` | Required external service unavailable | `retry` | Preserve Hub-owned checkpoint and retry from canonical state. |
| `timeout` | Bounded operation exceeds deadline | `retry` | Reuse the same idempotency key where a side effect may have committed. |
| `execution_failed` | Unclassified handler exception | `retry` | Emit failure; never fabricate completion. |
| `verification_failed` | Output/evidence fails verifier | `operator_action` | Keep the result unpromoted and surface verifier evidence. |
| `cancelled` | Operator cancellation or graceful eviction | `rehydrate` | Stop new work and continue on a replacement renter from canonical state. |

## Recovery invariants

1. Retry never widens the KPGS trust grant or capability lease.
2. Replacement renters load checkpoints and idempotency records from the declared canonical store.
3. Reusing an idempotency key returns the prior canonical result instead of repeating a durable side effect.
4. Failure envelopes retain tenant, domain, session, task, renter, correlation, lease and governing-spec provenance.
5. MAO/MMAO failures preserve `authority_mode`; successful trust/fit admission also receipts `decision_domain`, `consequence_class`, and `trust_grant_id`.
6. `trust_not_earned` and `role_not_fit` are distinct: untrusted is not the same state as trusted-but-wrong-role.
7. Validation-only authority never silently promotes into execution authority after retry or rehydration.
8. Cache/session-local state is disposable and is never the sole source required for recovery.

## Executable evidence

- Runtime: `kopano-core/kopano/stateless_renter.py`
- Conformance/recovery suite: `tests/test_stateless_renter_conformance.py`
- Event contract: `renter-envelope.schema.json`
- Trust/role-fit contract: `trust-grant.schema.json`
