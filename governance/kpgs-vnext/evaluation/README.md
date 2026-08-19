# KPGS Evaluation & Reward Loop

Issue: #38

```text
prepare/synthesize
→ execute
→ verify/profile
→ score
→ improve
→ promote | hold
→ observe
→ rollback recommendation when thresholds regress
```

## Canonical inputs

- `reference-suite.json` — versioned regression/evaluation cases;
- `promotion-policy.json` — thresholds declared **before** execution;
- `evaluation.py` — deterministic scoring, promotion admission and post-release observation;
- canonical `evidence/evidence.py` — machine-readable evidence bundle, verifier attribution and hard-gate law.

The reference regression suite covers one renter boundary, one skill-runtime boundary and one bounded SWFUS/domain-adapter boundary. The KPGS contract workflow executes those concrete test surfaces before the evaluation-loop test.

## Deterministic versus probabilistic

Every case declares one of:

- `deterministic` — contract/unit/integration result expected to be reproducible;
- `probabilistic` — bounded statistical result with a declared sample floor;
- `model-eval` — nondeterministic/model evaluation, also requiring a sample floor.

They remain separate in `kpgs.evaluation-score.v1`. A probabilistic score cannot hide a failed deterministic hard gate.

## Evidence correlation

Production promotion consumes the existing canonical KPGS evidence bundle. The bundle already binds exact repository commit, adapter version, renter protocol version, skill versions, capability-lease references, verifier identity, artifacts, metrics and deployment trace. Environment identity belongs in the `deployment` trace/artifact metadata; it is not inferred from a hostname or CI branch name.

A promotion decision stores the evidence `bundle_id` and exact commit SHA. It is therefore auditable back to the same machine-readable evidence surface used by engineering/everyday scorecards.

## Promotion gates

`promotion-policy.json` declares before evaluation:

- minimum aggregate score;
- risk classes requiring human approval;
- observation-window duration;
- rollback-target requirement;
- post-release rollback thresholds.

Hard evaluation/security/governance failures force `hold` even if aggregate score is high.

High/critical risk promotion requires a human approval reference. The runtime records the approval reference; it does not fabricate or self-approve it.

## Observation and rollback

Promotion starts a declared observation window. `observe_release()` evaluates measured post-release metrics against the predeclared rollback thresholds.

A trigger produces a recommendation only:

```text
rollback_recommended = true
automatic_execution = false
required_capability = estate.release.rollback
```

Rollback execution remains a separate governed action with its own capability lease and recorded target.

## Hard laws

```text
HIGH SCORE != HARD-GATE PASS
MODEL EVAL != DETERMINISTIC TEST
PROMOTION != SELF-APPROVAL
PROMOTION DECISION != EVIDENCE BUNDLE
OBSERVATION != AUTOMATIC ROLLBACK
ROLLBACK RECOMMENDATION != ROLLBACK AUTHORITY
CI BRANCH NAME != DEPLOYMENT ENVIRONMENT
```
