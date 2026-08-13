---
name: kpgs-watch-what-you-call
description: Separate change causality, invocation causality, and defect provenance so automation does not blame the change that merely surfaced a pre-existing failure. Use PKA non-closure when causality is not proven, and harden CI/CD call scope before execution.
tags:
  - pka
  - kpgs
  - orchestration
  - ci-cd
  - causality
  - provenance
  - github-actions
  - governance
  - incident-response
allowed-tools: []
license: MIT
author: Kholofelo Robyn Rababalela
---

# WYC-01 — Watch What You Call

## Canonical quote

> “My PKA files did not create those underlying defects. My call caused completely unrelated systems to execute and expose them. And that is still my orchestration mistake.”
>
> — **Kholofelo Robyn Rababalela**, 13 August 2026

## Objective

Use this skill whenever a code change triggers automation and one or more jobs fail. The skill prevents a common causal error:

```text
change happened
    ↓
workflow ran
    ↓
workflow failed
    ↓
therefore the change caused the defect
```

That conclusion is invalid unless dependency evidence establishes causality.

The hardened KPGS rule is:

> **An invocation may reveal a defect without causing it. The revealed defect remains attributable to the subsystem in which its causal condition exists; the unnecessary invocation remains attributable to the orchestration layer that crossed its authorized execution boundary. Never transfer defect ownership merely because a caller surfaced it, and never absolve the caller merely because the surfaced defect was pre-existing.**

## Core invariants

```text
FAILURE_SURFACED_BY_CALL != FAILURE_CAUSED_BY_CHANGE
```

```text
UNNECESSARY_EXECUTION = ORCHESTRATION_DEFECT
```

```text
TRIGGER_PROVENANCE != DEFECT_CAUSALITY
```

```text
CALLER_OWNS_CALL
DEFECT_OWNER_OWNS_DEFECT
```

A caller may therefore be responsible for **scope** while not being responsible for the **underlying defect**.

## Three-vector causal model

Every surfaced failure MUST be evaluated independently across three vectors.

### Vector 1 — Change causality

Question:

> Did the change modify, configure, import, generate, version, or transitively affect the failing subsystem?

Let:

- `C` = changed artifacts.
- `D(C)` = dependency closure of the change.
- `F` = failing subsystem.

Then direct or transitive causal eligibility requires:

```text
F ∈ D(C)
```

If `F ∉ D(C)`, do not attribute the defect to the change without new evidence.

### Vector 2 — Invocation causality

Question:

> Why was the failing subsystem executed at all?

Let:

- `I(C)` = execution graph triggered by the change.
- `A(C)` = execution graph authorized by change scope and governance.

If:

```text
I(C) ⊄ A(C)
```

then orchestration crossed its authorized boundary.

That is an orchestration defect even if every invoked job would have passed.

### Vector 3 — Defect provenance

Question:

> Where and when did the failing condition actually enter the system?

Trace the first supported causal condition through:

```text
commit / dependency / configuration / secret / environment / infrastructure / generated artifact
```

Do not use the triggering commit timestamp as the defect's origin unless evidence proves they are the same event.

## PKA binding

WYC-01 runs through Partial Knowable Algebra.

```text
X + Y = MAYBE
```

For a failure investigation:

- `X` = partial observations: failing job, changed files, dependency evidence, logs, historical runs, environment state.
- `Y` = knowable governance: workflow path rules, dependency declarations, ownership boundaries, deployment policy, required secrets, branch rules.
- `MAYBE` = causality remains unresolved until sufficient evidence exists.

### Non-closure rule

If dependency evidence is incomplete:

```text
CAUSED_BY_CHANGE = MAYBE
```

Do not convert `MAYBE` into blame because the failure occurred after the commit.

## Classification matrix

| Change caused defect | Invocation was authorized | Classification | Required response |
|---|---|---|---|
| yes | yes | `LEGITIMATE_REGRESSION` | fix/revert the causal change |
| yes | no | `REGRESSION_PLUS_ORCHESTRATION_DEFECT` | fix causal change and tighten call scope |
| no | yes | `PREEXISTING_DEFECT_LEGITIMATELY_DISCOVERED` | route defect to subsystem owner |
| no | no | `UNRELATED_DEFECT_EXPOSED_BY_ORCHESTRATION_MISTAKE` | fix call scope; separately track subsystem defect |
| maybe | any | `CAUSALITY_UNRESOLVED` | preserve MAYBE; collect dependency/log/history evidence |

## Required execution protocol

### Phase 0 — Freeze blame

Do not begin with "this commit broke CI."

Begin with:

```text
This commit triggered a run in which failure F was observed.
Causality is not yet established.
```

### Phase 1 — Build the change set

Collect:

```text
changed files
changed manifests
changed workflow files
changed generated artifacts
changed dependencies / lockfiles
changed environment declarations
```

Produce `C`.

### Phase 2 — Build dependency closure

Determine which systems can actually be affected by `C`.

Include direct and transitive relationships only when supported by repository evidence.

Produce `D(C)`.

### Phase 3 — Build invocation graph

Record every workflow/job/system that executed because of the triggering event.

Produce `I(C)`.

Do not confuse this graph with dependency closure.

### Phase 4 — Evaluate authorized scope

Use repository governance to calculate `A(C)`.

Examples of scope controls:

```yaml
paths:
  - "skills/pka/**"
```

```yaml
paths-ignore:
  - "skills/**"
```

Other valid boundaries include explicit job conditions, environment approvals, workflow dispatch, reusable-workflow contracts, deployment gates, and branch protections.

### Phase 5 — Compare graphs

Evaluate independently:

```text
F ∈ D(C) ?
```

and:

```text
I(C) ⊆ A(C) ?
```

These are different questions.

### Phase 6 — Trace defect provenance

Inspect the failing subsystem's history until the causal condition is supported by evidence or remains `MAYBE`.

A prior failing run is evidence of pre-existence.
A prior passing run is not by itself proof that the triggering change caused the new failure.

### Phase 7 — Issue two ownership receipts

When applicable, create separate receipts:

```text
INVOCATION_RECEIPT
owner: orchestration layer
finding: unrelated subsystem was called
remediation: narrow execution scope
```

```text
DEFECT_RECEIPT
owner: failing subsystem / causal change
finding: actual defect condition
remediation: repair underlying defect
```

Never merge these receipts merely because they occurred during the same workflow run.

## High-consequence deployment rule

A content-only, documentation-only, or skill-only change MUST NOT implicitly trigger a production deployment unless an explicit dependency or policy requires deployment validation.

Before invoking deployment, require at least one of:

- production-affecting path match;
- explicit release intent;
- approved environment gate;
- reusable workflow contract proving deployment relevance.

If none exists:

```text
DEPLOYMENT_AUTHORIZATION = false
```

## CI/CD hardening algorithm

Use this ordering before changing workflow code:

```text
CHANGE SCOPE
    ↓
DEPENDENCY IMPACT
    ↓
AUTHORIZED CALL GRAPH
    ↓
EXECUTION
    ↓
FAILURE
    ↓
CAUSAL ATTRIBUTION
```

Never reverse it into:

```text
FAILURE
    ↓
LATEST CHANGE
    ↓
BLAME
```

## Required output

Every WYC-01 audit should return:

```yaml
trigger:
  ref: <commit/pr/event>
  changed_scope: []

failure:
  subsystem: <name>
  job: <name>

change_causality:
  verdict: yes | no | maybe
  dependency_evidence: []

invocation_causality:
  authorized: yes | no | maybe
  invocation_evidence: []

provenance:
  verdict: preexisting | introduced-by-change | independent | maybe
  evidence: []

classification: <WYC-01 class>

ownership:
  invocation_owner: <orchestration layer>
  defect_owner: <subsystem / change / maybe>

remediation:
  orchestration: []
  defect: []
```

## Case 001 — PKA skill publication / Introduction-to-MCP

Observed event:

```text
skills/pka/** changed
        ↓
full Kopano CI executed
CodeQL multi-language analysis executed
Azure production deployment executed
        ↓
pre-existing/unrelated failures surfaced
```

Correct attribution:

```text
PKA skill files
    != proven cause of unrelated subsystem defects
```

while simultaneously:

```text
skills-only change
    → unrelated CI/deploy execution
    = orchestration scope defect
```

Remediation pattern:

```text
skills/pka/**
    ↓
PKA Skills Validation only
```

with unrelated full-estate workflows ignoring `skills/**` unless a future dependency explicitly changes that contract.

This case is the canonical origin case for WYC-01.

## Anti-patterns

Do not:

- blame the most recent commit because it is temporally adjacent to the failure;
- treat workflow execution as proof of dependency;
- suppress a real underlying defect merely because the call was unnecessary;
- fix a subsystem defect and leave the orchestration over-call intact;
- narrow workflow scope so aggressively that legitimate dependency validation disappears;
- use `paths-ignore` as a substitute for understanding the dependency graph;
- claim causality from correlation when PKA requires `MAYBE`.

## Graduation gate

WYC-01 is correctly implemented when all of the following are true:

1. A change can trigger only its authorized validation surface by default.
2. A surfaced failure receives separate change-causality and invocation-causality verdicts.
3. `MAYBE` survives when evidence is insufficient.
4. Deployment cannot occur from unrelated changes without an explicit dependency or release gate.
5. Defect provenance is preserved independently of trigger provenance.
6. Orchestration mistakes cannot hide behind pre-existing defects.
7. Pre-existing defects cannot be falsely reassigned to the caller that merely exposed them.

## Canonical law

> **The caller owns the call. The defect owner owns the defect. A trigger establishes execution provenance, not defect causality.**

/s/ Kholofelo Robyn Rababalela
