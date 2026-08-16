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
6. deterministic receipts.

FOC occurs if the runtime:

- claims to read hidden model states;
- claims to know a human internal state from these numbers;
- silently changes weights or thresholds;
- interprets a heuristic score as scientific truth;
- uses convergence to erase authority boundaries;
- treats autonomy as permission to bypass evidence or confirmation gates.

## Downstream integration rule

Do not copy this module blindly into `kopano-sovereign-hub`, RIVM, Cars4Mars, or other application repositories. First establish which runtime consumes the decision surface, then pin the canonical implementation or port it with a receipt and parity tests.
