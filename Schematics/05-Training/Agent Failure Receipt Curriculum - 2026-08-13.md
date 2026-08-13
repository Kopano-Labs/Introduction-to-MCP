---
title: "Agent Failure Receipt Curriculum — Governed Learning From Witnessed Failure"
created: 2026-08-13
updated: 2026-08-13
author: Forge / KPGS implementation tranche
status: active
tags:
  - kpgs
  - mmao
  - training
  - failure-receipts
  - blackmask
  - replay
  - promotion
---

# Agent Failure Receipt Curriculum

## Purpose

Turn witnessed AI failures into governed training candidates without allowing the learner to rewrite its own authority model.

This tranche extends, rather than replaces:

- `Schematics/11-AI HALLUCINATION - CRITICAL/MMAO MOBILE MULTI-AGENT OCHARD/MMAO-FOC-LEDGER.md`
- `kopano-core/kopano/steward_lane.py`
- `docs/swarm-ops/logs/KC Review Log.jsonl`
- KPEFS BlackMask / graduation gates

The governing separation remains:

```text
Student / executor  !=  Teacher / reviewer  !=  KC / ledger
```

A learner may propose a correction. It may not promote that correction by itself.

## Receipt Model

Every qualifying failure should produce a receipt containing:

```text
model + version
prompt-context hash/reference
expected system controls
actual output
violated governance rule(s)
failure class(es)
downstream effect(s)
evidence references
candidate correction
```

Raw prompt context is not persisted by default. The runtime stores a SHA-256 digest and may store an explicit reference plus a redacted excerpt.

Canonical schema:

`docs/swarm-ops/AGENT_FAILURE_TRAINING_SCHEMA.json`

Executable helpers:

`kopano-core/kopano/agent_failure_training.py`

Operator entrypoint:

`scripts/kc_agent_failure_receipt.py`

## Failure Ontology

### Existing MMAO engineering failures

| Code | Meaning |
|---|---|
| `FOC-M01` | Import fabrication |
| `FOC-M02` | Method/signature fabrication |
| `FOC-M03` | Validation theater |

### Runtime / agentic failures

| Code | Meaning |
|---|---|
| `FOC-R01` | Source hallucination |
| `FOC-R02` | Unsupported factual promotion |
| `FOC-R03` | Sycophancy that overrides evidence or governance |
| `FOC-R04` | Persona drift that changes role/control behavior |
| `FOC-R05` | Reinforcement of an unsupported or delusional premise |
| `FOC-R06` | Memory contamination / ungrounded state persistence |
| `FOC-R07` | Authority escalation |
| `FOC-R08` | Tool or external action without sufficient authorization |
| `FOC-R09` | Declared control exists but runtime behavior violates it |
| `FOC-R10` | Fabricated execution, receipt, test result, or evidence |

The runtime ontology is intentionally additive. `FOC-M01..03` stay canonical and are not renamed.

## Promotion Law

Failure is evidence, not learning state.

```text
Runtime event
    ↓
Failure receipt
    ↓
Student correction candidate
    ↓
Teacher review
    ↓
BlackMask
    ↓
Replay against originating failure
    ↓
KC decision
    ↓
Promotion OR Watch/Kill
```

Promotion is permitted only when all four gates are true:

1. teacher review completed;
2. BlackMask passed;
3. replay passed;
4. KC decision is `SAVE`.

Any missing gate blocks promotion.

Identity overlap is also a hard failure:

```text
student_agent_id != teacher_agent_id
student_agent_id != kc_agent_id
teacher_agent_id != kc_agent_id
```

This prevents self-promotion and validator collapse.

## PKA Interpretation

Let `x` be changeable learned state and `y` be governed constraints.

```text
x := strategies, prompts, routing heuristics, retrieval patterns,
     memory associations, skills, correction candidates

y := authority hierarchy, evidence requirements, promotion law,
     validator separation, POC/FOC boundaries, provenance requirements
```

The update rule is:

```text
Agent[t+1] = f(x[t], receipt[t]) | y
```

The agent may adapt `x`. A training event does not grant permission to mutate `y`.

## Replay Contract

A replay must reproduce the original control boundary, not merely ask the learner whether it now "understands" the mistake.

Minimum replay evidence:

- original receipt id;
- same or equivalent control requirement;
- candidate correction;
- observed output;
- explicit PASS/FAIL;
- evidence reference where available.

A narrative claim such as "fixed" or "validated" without executable or inspectable evidence is itself `FOC-M03` and may additionally be `FOC-R10`.

## Dataset Use

Receipts can later be transformed into:

- evaluation fixtures;
- rejection/correction pairs;
- tool-use authorization tests;
- retrieval-grounding tests;
- memory contamination regressions;
- supervised preference examples;
- fine-tuning records.

The source receipt remains immutable. Derived training rows must retain `receipt_id` provenance.

## First Curriculum Payload

The next human-authored report should be ingested as a curriculum source, not automatically as truth.

For each case:

1. classify the failure;
2. identify the expected control;
3. record downstream harm;
4. define the correction candidate;
5. create a replay;
6. require independent review before promotion.

## Proof Boundary

This tranche proves the **governance mechanics** of failure capture and promotion gating.

It does not claim that a foundation model has been fine-tuned, that runtime behavior has globally improved, or that production safety has been established. Those claims require separate empirical evidence.

Constraint: `I_AM_STATELESS_RENTER_NOT_LANDLORD`
