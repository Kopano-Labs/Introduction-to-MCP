# Stateless Renter Failure and Recovery Matrix

Issue: #34

This matrix binds the protocol failure codes to deterministic recovery behavior in the reference renter. Failure classification is evidence; it must not silently escalate renter authority or move canonical state into the renter process.

| Failure code | Typical source | Recoverability | Required behavior |
|---|---|---|---|
| `input_invalid` | Payload fails declared input contract | `user_action` | Reject before durable side effects; return the invalid-input boundary without mutating canonical progress. |
| `policy_denied` | Operation/resource/tenant/task outside lease | `operator_action` | Do not invoke workload handler; emit `policy.denied` with correlation and lease metadata. |
| `capability_expired` | Lease expiry reached | `rehydrate` | Do not invoke workload handler; acquire a fresh governed lease before retry. |
| `dependency_unavailable` | Required external service unavailable | `retry` | Preserve the last Hub-owned checkpoint and retry from canonical state. |
| `timeout` | Bounded operation exceeds deadline | `retry` | Do not infer success; retry using the same idempotency key where a side effect may already have committed. |
| `execution_failed` | Unclassified handler exception | `retry` | Emit `task.failed`; preserve checkpoint and idempotency evidence; do not fabricate completion. |
| `verification_failed` | Output/evidence fails declared verifier | `operator_action` | Keep result unpromoted and surface the verifier failure. |
| `cancelled` | Operator cancellation or graceful renter eviction | `rehydrate` | Stop new work on the draining renter and continue only through a replacement renter hydrated from canonical state. |

## Recovery invariants

1. A retry never widens the capability lease.
2. A replacement renter reads checkpoint/idempotency state from the canonical store, never from the destroyed renter.
3. Reusing an idempotency key returns the prior canonical result rather than repeating a durable side effect.
4. Every failure envelope retains tenant, domain, task, renter, correlation, lease, protocol and governing-spec metadata.
5. `retry` means the action may be attempted again under the same governing contract; it does not mean the previous side effect is known not to have happened.
6. `rehydrate` means replace or refresh transient renter state/authority from canonical sources before continuing.

## Executable evidence

The conformance and recovery behavior is exercised by:

- `tests/test_stateless_renter_conformance.py`
- `tests/test_stateless_renter_failure_recovery.py`
- reference runtime: `kopano-core/kopano/stateless_renter.py`

The same destroy/recreate harness is parameterized across two domain workloads, and the replay fixture proves a repeated idempotency key does not invoke the durable side-effect handler twice.
