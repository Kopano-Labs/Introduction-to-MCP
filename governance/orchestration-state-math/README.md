# KPGS Orchestration State Math

Status: **POC / executable governance heuristic**

This package converts recurring equations from KPGS design conversations into a small, testable runtime surface. The equations are intentionally treated as **governance heuristics**, not scientific measurements of a person and not claims about inaccessible model internals.

## Why this belongs in Introduction-to-MCP

`Introduction-to-MCP` already contains the CCP, PKA, POC-vs-FOC, APU vector, stateless-renter consistency, and governance primitives. The orchestration equations govern how those components decide whether to infer, execute, clarify, confirm, or hold. Duplicating the math into every downstream repo would create governance drift.

Canonical implementation:

- `kopano-core/kopano/orchestration_state_math.py`
- `tests/test_orchestration_state_math.py`

Downstream repositories should consume or port from this source with a pinned receipt rather than silently inventing divergent weights or thresholds.

## Equations encoded

### 1. Response pressure

Conversation shorthand:

`response ∝ learned_patterns + context + instruction_hierarchy + alignment + prompt_salience`

Runtime implementation: `ResponsePressure.score()`.

All values are caller-provided proxies in `[0,1]`. The runtime does not inspect hidden transformer activations.

### 2. Orchestration is larger than prompting

`orchestration = identity + state + history + permissions + feedback + tools + uncertainty_control + initiative`

Runtime implementation: `OrchestrationState.capacity()`.

This is a state-vector heuristic for sustained behavior over time, not a single-prompt score.

### 3. Meaning is contextual

`meaning_received = f(words, tone, timing, status, audience, history, delivery)`

Runtime implementation: `MeaningSignal.received()`.

A tone-sensitive preset is provided because identical words can produce materially different interpersonal effects through tone and delivery. The preset is explicit and replaceable; callers must not treat its weights as universal psychological truth.

### 4. Knowing is not understanding

`K(x) = stored / available representation of x`

`U(x,c) = contextual interpretation of x under context c`

Runtime implementation: `KnowledgeUnderstanding`.

`understanding = interpretation_accuracy × context_fit`

`overlap = min(knowledge, understanding)`

This preserves the distinction between possessing information and interpreting it correctly in context.

### 5. Reported resolution is not verified resolution

`reported_resolution != verified_resolution`

Runtime implementation: `ResolutionState`.

Residual distress, anger, and uncertainty are combined into `residual_load`; `experienced_resolution = 1 - residual_load`. A large positive mismatch means the explicit declaration of closure is ahead of the residual-state estimate.

This should only be used when those residual signals are actually available. It must never be used to overrule a person by pretending the runtime knows their internal state better than they do.

### 6. Earned autonomy

`A(t+1) = clamp(A(t) + gain×validated_executions - penalty×failed_executions)`

Runtime implementation: `AutonomyState.update()`.

The purpose is to reduce repeated micromanagement after validated execution while making failures decrease autonomy instead of being ignored.

### 7. Governed state transitions

The runtime should autonomously execute when:

- the objective is sufficiently clear;
- evidence is sufficient;
- permission is present;
- ambiguity is below threshold;
- the action is not high-risk or hard to reverse without confirmation.

Runtime implementation: `GovernedTransition.decide()` returning one of:

- `EXECUTE`
- `CLARIFY`
- `CONFIRM`
- `HOLD`

This encodes the preferred operating pattern:

`Observe -> Recall -> Infer -> Execute -> Validate`

with clarification or confirmation as **governed exceptions**, not a default dependency on repeated user instruction.

### 7a. Every arrow has a membrane

A workflow arrow is not free movement between nodes.

```text
state A
  |
  v
[ state-transition membrane ]
  |
  v
state B
```

**Nodes hold state. Membranes govern state transition.**

Runtime implementations:

- `InformationMembrane`
- `StateTransitionMembrane`
- `MembraneVerdict`
- `TransitionVelocity`

The membrane evaluates what happens *between* states:

- **identity receptor** — is the transition still modifying the same governed object?
- **scope receptor** — is the proposed mutation part of the requested task?
- **evidence receptor** — is there enough evidence to justify crossing the boundary?
- **selective permeability** — is the requested state delta within the authorized change budget?
- **state-cost / energy check** — is the transition creating excessive extra state to accomplish the objective?
- **homeostasis check** — does the new state restore or preserve the active objective?
- **ambiguity gate** — does interpretation need to slow and clarify before mutation?
- **risk / reversibility gate** — does the transition require explicit confirmation?

The information membrane makes four laws executable:

```text
AUTHORITY != ABUNDANCE
RELEVANCE != PERMISSION
OBSERVATION != MUTATION
NEW IDEA != CURRENT TASK
```

A large volume of context can therefore increase interpretation pressure without increasing mutation authority. A relevant observation may enter working context while still being blocked from state mutation.

#### Velocity is terrain-dependent

The runtime does not have one execution speed:

- `HIGHWAY` — low-risk inspection/read work can move quickly;
- `URBAN` — ambiguity slows interpretation;
- `SCHOOL_ZONE` — mutation requires bounded change and inspection;
- `CHECKPOINT` — high-risk or hard-to-reverse effects require confirmation.

More tools or more available context do **not** imply permission to accelerate. A larger mutation surface should generally strengthen the membrane.

### 8. Conceptual convergence can include both parties

`converged_target = (user_target×user_weight + agent_target×agent_weight) / total_weight`

Runtime implementation: `converge_targets()`.

Both target vectors must expose identical dimensions; missing dimensions fail closed rather than being guessed. Optional invariant bounds constrain the result.

The function does **not** imply equal authority. Governance determines the weights and invariant bounds.

### 9. Deterministic receipts

`receipt()` hashes the canonical JSON payload with SHA-256 and attaches the constraint:

`HEURISTIC_NOT_HIDDEN_STATE_OR_PSYCHOLOGICAL_GROUND_TRUTH`

This makes each calculation reproducible and auditable.

## POC vs FOC boundary

POC requires:

1. deterministic calculations;
2. closed-domain validation;
3. tests for autonomy increase/decrease;
4. fail-closed behavior on invalid inputs;
5. explicit confirmation for high-risk / hard-to-reverse transitions;
6. deterministic receipts;
7. mutation authority that cannot be manufactured from context abundance or relevance;
8. bounded state deltas and state-cost limits before mutation;
9. objective-homeostasis checks at the transition boundary;
10. execution velocity that decreases as consequence and irreversibility increase.

FOC occurs if the runtime:

- claims to read hidden model states;
- claims to know a human internal state from these numbers;
- silently changes weights or thresholds;
- interprets a heuristic score as scientific truth;
- uses convergence to erase authority boundaries;
- treats autonomy as permission to bypass evidence or confirmation gates;
- treats an observed or relevant fact as permission to mutate state;
- creates replacement state instead of repairing the governed object without an explicit identity transition;
- expands a requested mutation beyond the membrane's permitted delta;
- accelerates mutation merely because more tools or context are available.

## Downstream integration rule

Do not copy this module blindly into `kopano-sovereign-hub`, RIVM, Cars4Mars, or other application repositories. First establish which runtime consumes the decision surface, then pin the canonical implementation or port it with a receipt and parity tests.
