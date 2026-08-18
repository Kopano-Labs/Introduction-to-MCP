# KPGS Evidence Bundle Contract

Issue: #45

## Purpose

Evidence is the bridge between execution and governance. A release, capability use, policy decision, evaluation or rollback is only inspectable when KPGS can correlate it to the exact domain, release, adapter, renter, skill, task and verifier involved.

The executable reference is `evidence.py`. Both technical and plain-language scorecards are derived from the same finalized evidence bundle.

## Canonical correlation chain

```text
estate property
  -> exact release + commit
  -> adapter
  -> renter
  -> skill(s)
  -> task/session
  -> verifier(s)
  -> governance decision
```

For user-facing task evidence, trace hops additionally prove the request path across:

```text
PWA -> adapter -> Sovereign Hub -> renter -> skill -> verifier
```

Deployment promotion evidence also carries a deployment trace hop.

A canonical bundle cannot substitute an aggregate score for a missing correlation link.

## Evidence classes

Artifacts:

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

Metrics:

- latency
- realtime health
- cost/usage where measurable
- reliability/error/recovery rate
- user task completion/abandonment
- accessibility
- mobile validation

Every artifact and metric is a reference to inspectable evidence; raw credentials are never embedded.

## Production promotion requirement

A governance decision of `promote` requires:

- exact release reference;
- exact 40-character Git commit SHA;
- adapter implementation/version;
- renter identity/protocol version;
- at least one named/versioned skill;
- task + session + correlation identity;
- capability lease reference;
- complete user-task trace plus deployment trace;
- verifier results;
- core promotion artifact classes;
- core latency/realtime/reliability/error/task/accessibility/mobile metrics;
- explicit retention and redaction policy references.

If a release cannot identify the evidence that justified its promotion, KPGS treats that release as outside canonical governance.

## Hard-gate rule

Aggregate scores MUST NOT hide or average away a failed hard governance or security gate.

The runtime therefore evaluates hard gates independently:

- failed hard gate + `promote` → reject bundle finalization;
- failed hard gate + `allow` → reject bundle finalization;
- failed hard gate + `hold | deny | rollback` → bundle may finalize so the failure remains inspectable and actionable;
- engineering scorecard always exposes raw hard-gate failures independently of aggregate scores;
- everyday scorecard renders hard-gate failure as `blocked` / high risk.

A score of `0.9999` cannot cancel one failed hard security criterion.

## Scorecards

### Engineering scorecard

Derived directly from the canonical bundle and includes:

- exact release/commit/correlation IDs;
- raw verifier outputs;
- hard-gate failures;
- metrics;
- aggregate scores;
- trace hops;
- artifacts;
- governance decision;
- retention/redaction references.

### Everyday governance scorecard

Derived from that same bundle and answers:

- what property changed?
- what release/commit is involved?
- is it ready, active, attention-needed or blocked?
- what risk state applies?
- what decision was made?
- why was it allowed/blocked?
- which hard gates failed?
- what should happen next?

No separate “friendly” database or second scoring model exists.

## Redaction rules

Evidence MUST NOT store raw:

- authorization headers;
- passwords;
- access/session/API tokens;
- cookies;
- provider credentials;
- private keys;
- known secret-token patterns.

Trace metadata is recursively checked for secret-bearing key names and common credential patterns. Capability lease fields carry references such as `lease://...`, never compact signed tokens. Secret-provider evidence may be referenced through governed references (for example `vault://...`) but raw secret values are forbidden.

Every finalized bundle MUST name a `redaction_policy_ref` so the owning tenant/domain can resolve the exact policy used.

## Retention rules

Every finalized bundle MUST name a `retention_policy_ref`.

The referenced retention policy is responsible for defining, at minimum:

- evidence owner / tenant / domain;
- retention class;
- expiry or retention duration;
- legal/governance hold behavior where applicable;
- deletion/archive procedure;
- whether derived scorecards survive deletion of lower-level raw telemetry.

KPGS deliberately does not invent one universal retention duration in this protocol. The bundle proves **which governed policy applies**, while the owning policy defines the duration.

## Rollback support

`rollback_recommendation(bundle, thresholds)` derives a machine-readable signal from canonical evidence.

A failed hard gate always triggers a rollback recommendation. Optional caller-supplied numeric metric thresholds may also trigger it. The function **never executes rollback itself**.

Execution still requires:

- the recorded estate rollback target/procedure;
- a valid `estate.release.rollback` capability lease;
- a Sovereign Hub governance action.

This keeps evidence observable and automatable without allowing telemetry to become ambient authority.

## Machine contracts

- `evidence-bundle.schema.json`
- `evidence.py`
- `validate_evidence.py`
- `tests/test_evidence_bundles.py`
