# KPGS State-Transition Membrane Derivation Receipt

Status: **POC candidate — requires repository CI**

## Source observation

A workflow graph that models only nodes and arrows hides the governed transport that must occur between states. The transition boundary therefore needs an explicit selectively permeable membrane rather than treating `A -> B` as free movement.

## Canonical law

> Nodes hold state. Membranes govern state transition.

A transition membrane evaluates identity, scope, evidence, permeability, state cost, objective homeostasis, ambiguity, risk, reversibility, and confirmation before mutation.

## Information laws

```text
AUTHORITY != ABUNDANCE
RELEVANCE != PERMISSION
OBSERVATION != MUTATION
NEW IDEA != CURRENT TASK
```

## Velocity law

```text
READ / INSPECTION       -> HIGHWAY
AMBIGUOUS INTERPRETATION -> URBAN
STATE MUTATION           -> SCHOOL_ZONE
HIGH-RISK / IRREVERSIBLE -> CHECKPOINT
```

Tool availability or context volume is not authority to accelerate.

## Implementation receipt target

- `kopano-core/kopano/orchestration_state_math.py`
- `tests/test_orchestration_state_math.py`
- `governance/orchestration-state-math/README.md`

This receipt does not claim CI validation until repository workflows pass.