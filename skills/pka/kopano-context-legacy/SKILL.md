---
name: kpgs-kopano-context-legacy
description: Operationalize KC — Kopano Context Legacy — by converting local context into governed learning, validated capability, evidenced economic pathways and capability multiplication without allowing unemployment-impact claims to exceed proof.
tags:
  - kpgs
  - kc
  - legacy
  - pka
  - unemployment
  - capability
  - learning
  - livelihoods
  - poc
  - foc
  - provenance
  - receipts
allowed-tools: []
license: MIT
author: Kholofelo Robyn Rababalela
---

# KCL-01 — Kopano Context Legacy

## Canonical doctrine

Load and preserve:

```text
Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/MAIN-BRAIN/Legacy.md
```

Doctrine invariant:

```text
KC = KOPANO_CONTEXT_LEGACY
KPGS_LEGACY > RENTER_IDENTITY
```

`Kopano Context Core` remains an implementation/storage component. In new governance text use `Kopano Context Core` or `KCC` when needed to avoid ambiguity with KC.

## Use when

Use KCL-01 when a KPGS task proposes, evaluates or reports any of the following:

- learning or skills development;
- employability, employment or livelihood pathways;
- local capability-building programmes;
- partnerships intended to create economic opportunity;
- a repository, feature or product claiming contribution to the KPGS legacy;
- replication of a successful pattern into a different community, country or economic context;
- impact claims about unemployment or economic participation;
- succession, continuity or preservation of KPGS knowledge beyond one founder/model/tool.

## Stateless renter entry

Before applying KCL-01:

```text
I_AM_STATELESS_RENTER_NOT_LANDLORD
```

A renter serves the legacy. It does not own or redefine it.

Load current human instruction, current repository state, applicable KPGS doctrine and provenance-bearing receipts before using historical context.

## PKA split

For the current case classify:

```text
X = CHANGEABLE_LOCAL_CONTEXT
Y = KPGS_LEGACY_INVARIANTS
X + Y = MAYBE
```

Minimum `X` classes:

```yaml
local_context:
  geography: unknown
  cohort: unknown
  language: unknown
  constraints: []
  available_infrastructure: []
  labour_market_signals: []
  institutions: []
  economic_pathways: []
  current_capabilities: []
  evidence_sources: []
```

Minimum `Y` invariants:

```yaml
legacy_invariants:
  evidence_over_narrative: true
  provenance_required: true
  human_choice_preserved: true
  local_context_required: true
  poc_foc_gate_required: true
  hidden_model_memory_is_not_authority: true
  receipts_are_append_only: true
  capability_must_be_transferable: true
  global_claims_require_global_scale_evidence: true
```

Do not infer missing `X`. Preserve `unknown`.

## Capability conversion algorithm

Evaluate the proposed system against this chain:

```text
LOCAL_CONTEXT
-> CONSTRAINTS_AND_OPPORTUNITIES_CLASSIFIED
-> LEARNING_PATHWAY
-> PRACTICE
-> PROOF_ARTIFACT
-> VALIDATION
-> ECONOMIC_PATHWAY
-> ECONOMIC_PARTICIPATION
-> CONTRIBUTOR
-> CAPABILITY_MULTIPLIER
```

For every transition ask:

```text
WHAT_CHANGED?
WHAT_PROVES_IT?
WHO_VALIDATED_IT?
WHAT_REMAINS_UNKNOWN?
CAN_A_FRESH_RENTER_RECONSTRUCT_IT?
```

A missing transition does not automatically invalidate the whole system. It becomes an explicit `MAYBE`, `HOLD` or next proof requirement.

## Continuous learning loop

Where KCL-01 governs a learning system, preserve the loop:

```text
ENCOUNTER
-> UNDERSTAND
-> BUILD
-> VALIDATE
-> TEACH
-> PRESERVE
-> REVISIT
```

A learning activity is not complete merely because information was consumed.

Prefer evidence that the learner can produce, explain, operate, repair, adapt or teach the capability under relevant conditions.

## Economic pathway rule

Do not collapse economic participation into a single employment model.

Permitted evidenced pathway classes include:

```text
EMPLOYMENT
PAID_WORK
CONTRACTING
ENTREPRENEURSHIP
PRODUCTIVE_OWNERSHIP
OTHER_VALIDATED_LIVELIHOOD
```

The pathway must be locally meaningful and supported by evidence. A pathway label without observed participation remains a proposal.

## Impact-claim gate

Before making an unemployment or livelihood impact claim, require:

```yaml
impact_claim:
  claim: <text>
  geography: <defined or unknown>
  cohort: <defined or unknown>
  denominator: <defined or unknown>
  time_window: <defined or unknown>
  baseline: <defined or unknown>
  observed_change: <defined or unknown>
  methodology: <defined or unknown>
  evidence_refs: []
  attribution_basis: <defined or unknown>
```

Routing:

```text
missing critical proof                   -> KC_HOLD
local proof + bounded local claim        -> KC_POC_CANDIDATE
validated capability + pathway evidence  -> KC_ALIGNED_POC
claim exceeds evidence                   -> KC_FOC_CANDIDATE
fabricated / unverifiable proof          -> KC_FOC_BLOCK
```

Never convert the mission "address unemployment globally" into a factual claim that global unemployment has been solved.

## Legacy succession gate

A system contributes to KC only if its useful state can outlive the current operator.

Check:

```yaml
succession:
  problem_reconstructable: false
  context_reconstructable: false
  governance_reconstructable: false
  implementation_reconstructable: false
  failures_preserved: false
  evidence_reconstructable: false
  unresolved_unknowns_preserved: false
  continuation_path_available: false
```

A project may still be a valid experiment while these values are false. It must not be promoted as durable legacy until the relevant succession surface is proven.

## Output contract

Emit a receipt-shaped result:

```yaml
kcl_receipt:
  doctrine: KCL-01
  renter_assertion: I_AM_STATELESS_RENTER_NOT_LANDLORD
  subject: <repo/project/programme/person/system>
  local_context:
    known: []
    unknown: []
  capability_chain:
    observed: []
    inferred: []
    validated: []
    missing: []
  economic_pathway:
    proposed: []
    observed: []
    validated: []
  impact_claim:
    requested: <claim or none>
    bounded_claim: <claim or none>
    proof_refs: []
  succession:
    proven: []
    missing: []
  disposition: KC_HOLD | KC_POC_CANDIDATE | KC_ALIGNED_POC | KC_FOC_CANDIDATE | KC_FOC_BLOCK
  next_proof_required: []
  unresolved_unknowns: []
  receipt_refs: []
```

## Decision discipline

```text
MISSION != METRIC
ACTIVITY != CAPABILITY
CAPABILITY != ECONOMIC_PARTICIPATION
LOCAL_SUCCESS != GLOBAL_AUTHORITY
MODEL_CONTINUITY != LEGACY
FOUNDER_PRESENCE != SYSTEM_CONTINUITY
```

KCL-01 is deliberately strict about these boundaries because KC is intended to survive changing people, models, markets, institutions and implementations.

## Relationship to SRCCP-01

`skills/pka/stateless-renter-consistency/SKILL.md` governs reconstruction, provenance, consistency and CCP → PKA admission across stateless renters.

KCL-01 consumes that discipline at a higher purpose layer:

```text
SRCCP-01: WHO/WHAT MAY RECONSTRUCT AND ACT?
KCL-01:   WHAT LEGACY IS THAT ACTION REQUIRED TO SERVE?
```

## Success condition

A fresh human or renter can determine, from receipts rather than hidden memory:

- what local problem was being addressed;
- what context was known and unknown;
- what capability pathway was attempted;
- what the learner/person actually proved;
- what economic pathway was observed;
- what claim is justified by evidence;
- what failed;
- what remains unresolved; and
- how the next person can continue and multiply the capability.

> **Preserve context. Prove capability. Connect capability to locally valid economic pathways. Multiply it through people. Leave receipts strong enough that the work survives us.**

/s/ Kholofelo Robyn Rababalela
