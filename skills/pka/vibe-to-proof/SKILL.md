---
name: kpgs-vibe-to-proof
description: Preserve subjective human signal without turning it into unsupported truth. Route vibe -> hypothesis -> investigation -> CCP convergence -> receipts -> accepted bounded claim, with PKA MAYBE retained until verified evidence exists.
tags:
  - pka
  - kpgs
  - ccp
  - epistemics
  - receipts
  - human-signal
  - governance
allowed-tools: []
license: MIT
author: Kholofelo Robyn Rababalela
---

# VTP-01 — Vibe-to-Proof

## Canonical law

> **The vibe tells us where to look; the receipt tells us what we are allowed to believe.**

## Objective

Use this skill when a human or model detects something meaningful before formal evidence is complete: a vibe, intuition, discomfort, attraction, felt inconsistency, emotional fracture, social signal, or emerging pattern.

The signal is not noise. The signal is also not fact.

VTP-01 preserves both truths by forcing the signal through a governed promotion path.

```text
vibe
  -> hypothesis
  -> investigate
  -> CCP convergence
  -> receipts
  -> accepted bounded claim
```

## Core invariants

```text
VIBE != FACT
```

```text
VIBE = ADMISSIBLE_HUMAN_TELEMETRY
```

```text
CONVERGENCE != PROOF
```

```text
NO_ACCEPTED_CLAIM_WITHOUT_VERIFIED_RECEIPT
```

```text
VERIFIED_CONTRADICTION -> MAYBE
```

## Epistemic states

Map the pipeline to KPGS status explicitly:

| Stage | KPGS epistemic status | PKA state |
|---|---|---|
| vibe / raw human signal | `observed` | `MAYBE` |
| hypothesis | `proposed` | `MAYBE` |
| investigation observations | `inferred` | `MAYBE` |
| CCP convergence without verified receipts | `inferred` | `MAYBE` |
| verified supporting receipt + convergence | `verified` | `POC_CANDIDATE` |
| verified contradictory receipt | `unknown` / reopened | `MAYBE` |

## Required protocol

### Phase 0 — Preserve the signal

Do not dismiss a subjective signal merely because it is not yet evidenced.

Record it as:

```yaml
signal:
  class: human_vibe
  epistemic_status: observed
  assertion_authority: none
```

### Phase 1 — Form the smallest hypothesis

Translate the vibe into a bounded proposition that could be supported or contradicted.

Do not convert:

```text
"this feels off"
```

into:

```text
"this person/system is malicious"
```

without an investigation boundary.

### Phase 2 — Investigate

Gather observations, telemetry, primary-source records, direct tool output, tests, logs, or other relevant evidence.

Observations may strengthen a hypothesis, but they remain `MAYBE` until evidence is inspectable and verified.

### Phase 3 — Reach CCP convergence

CCP convergence means governed participants now understand the same proposition.

It does **not** mean the proposition is true.

```text
HYPOTHESIS + CCP = MAYBE
```

### Phase 4 — Require receipts

A receipt must be inspectable and have explicit provenance.

Examples:

```text
verified-source
verified-live
primary-source tool output
test result
CI log
versioned repository evidence
```

A label saying `verified=true` without a receipt reference is not sufficient.

### Phase 5 — Promote only the bounded claim

When CCP convergence and at least one verified supporting receipt are both present, the claim may become:

```yaml
epistemic_status: verified
pka_verdict: POC_CANDIDATE
```

This is bounded acceptance, not permanent truth.

Future evidence may reopen it.

### Phase 6 — Contradiction reopens the state

If a verified receipt contradicts the hypothesis:

```text
ACCEPTED/PROPOSED CLAIM -> MAYBE
```

Do not protect the old conclusion because it previously felt right or because both participants had converged on it.

## PKA binding

Canonical implementation lives in:

`RobynAwesome/Partial-Knowable-Algebra`

Runtime source:

`src/Pka.Engine/VibeToProof.cs`

Formal algebra:

`docs/mathematics/VIBE_TO_PROOF.md`

The engine entry point is:

```text
VibeToProofGate.Evaluate(...)
```

Introduction-to-MCP is the KPGS execution membrane for the protocol; it does not replace the PKA source implementation.

## Required output

A VTP-01 audit should return at minimum:

```yaml
signal:
  value: <raw vibe>
  epistemic_status: observed

hypothesis:
  value: <bounded proposition>
  epistemic_status: proposed

investigation:
  observations: []
  receipts: []

ccp:
  converged: true | false

receipt_gate:
  verified_supporting: 0
  verified_contradicting: 0

claim:
  accepted: true | false
  epistemic_status: observed | proposed | inferred | unknown | verified
  pka_verdict: MAYBE | POC_CANDIDATE
```

## Anti-patterns

Do not:

- suppress a human signal because it is subjective;
- promote a human signal because it is emotionally intense;
- use agreement as evidence;
- treat model fluency as proof;
- turn repeated intuition into a verified claim by repetition alone;
- accept an unverifiable `verified=true` flag without a provenance reference;
- preserve a conclusion after verified contradictory evidence appears;
- convert bounded evidence into permanent human identity or personality truth.

## Graduation gate

VTP-01 is correctly implemented when:

1. vibe survives as inspectable telemetry;
2. vibe cannot directly become fact;
3. CCP convergence cannot directly become fact;
4. verified receipt provenance is required for promotion;
5. contradictory verified evidence reopens the claim;
6. accepted claims remain bounded and revisable under PKA;
7. the system can explain every promotion step from signal to assertion.

## Canonical sentence

> **Human signal chooses the investigation direction. Governed evidence chooses the assertion boundary.**

/s/ Kholofelo Robyn Rababalela
