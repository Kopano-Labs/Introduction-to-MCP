# KPGS Evidence Bundle Contract

Issue: #45

## Purpose

Evidence is the bridge between execution and governance. A release, capability use, policy decision, evaluation or rollback is only inspectable when KPGS can correlate it to the exact domain, release, adapter, renter, skill, task and verifier involved.

## Canonical correlation chain

```text
estate property
  -> release
  -> adapter
  -> renter
  -> skill(s)
  -> task/session
  -> verifier(s)
  -> governance decision
```

## Evidence classes

- `specification`
- `policy-decision`
- `capability-lease`
- `execution`
- `verification`
- `security`
- `performance`
- `accessibility`
- `deployment`
- `rollback`
- `user-outcome`

## Hard-gate rule

Aggregate scores MUST NOT hide or average away a failed hard governance or security gate. Evidence bundles therefore carry both:

- individual verifier results with `hard_gate` and `passed` state; and
- optional aggregate scores for dimensions where aggregation is meaningful.

## Redaction

Evidence may reference secret-provider operations and sensitive events, but MUST NOT store raw credentials or unredacted secrets. Retention and redaction policy must be explicit at the owning tenant/domain level.

## Release requirement

A production release SHOULD carry an immutable evidence bundle reference. If a release cannot identify the evidence that justified its promotion, KPGS treats that release as outside canonical governance.
