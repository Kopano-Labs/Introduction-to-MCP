# KPGS Specification-First Agent Governance

Issue: #39

## Purpose

KPGS treats the specification as the governing artifact for agentic implementation. Generation may be cheap and fast; production authority is not. A coding agent receives a bounded specification, capabilities and verification contract, then returns implementation evidence against that contract.

## Canonical loop

```text
specify -> delegate -> execute -> verify -> steer -> ship
```

## Required specification fields

Every governed build task MUST declare:

- `spec_id`
- `title`
- `outcome`
- `scope.included`
- `scope.excluded`
- `interfaces`
- `constraints`
- `acceptance_criteria`
- `verification_plan`
- `rollback_plan`
- `risk_class`
- `required_capabilities`
- `lifecycle_state`

The machine-readable contract is defined by `build-spec.schema.json`.

## MMAO + MAO identity-governance POC

`mmao-mao/` is the additive contract layer for controlled multi-agent identity and model-interface experiments. It separates the following claims so a run can be attributed without collapsing them into one agent label:

```text
identity -> seat -> interface/body -> model/version -> task/scope -> authority -> context state -> evidence
```

The POC preserves the current task-contract and evidence owners. It does not grant new ambient authority. In particular, **high task authority is local to an explicit task mandate**. Global GSMB structural maintenance is limited by the current experiment boundary to:

1. Codex - Chief Architect
2. Anti-Gravity - Chief Facilitator
3. Cursor - Lead Developer

The contract, planned matrix, Five Whys receipt shape, and Anti-Gravity handoff are under `mmao-mao/`. The associated build specification is `specs/mmao-mao-identity-governance-v0.1.json`. Its experiment remains `draft` until controlled runs produce exact state, trace, evidence, and independent review receipts.

## Lifecycle

A build artifact MUST be classifiable as exactly one of:

- `draft`
- `verified`
- `approved`
- `released`
- `rejected`
- `rolled-back`

A transition to `released` MUST NOT occur when a hard acceptance criterion, governance gate or security gate is failing.

## Delegation rules

1. The agent receives only the capabilities required by the active spec.
2. The agent MUST NOT silently broaden scope.
3. New requirements discovered during execution become a spec amendment or a follow-up spec.
4. Destructive/external side effects require the gate declared by the risk class.
5. Implementation and verification SHOULD be separable so that the same actor is not the only source of truth for its own correctness.

## Risk classes

### R0 — documentation / no runtime effect
May be auto-verified and auto-approved when repository policy permits.

### R1 — reversible local change
Requires automated verification and explicit rollback instructions.

### R2 — shared runtime / integration change
Requires integration verification, evidence bundle and an approval boundary before production promotion.

### R3 — destructive, security-sensitive, financial, identity or production-control change
Requires explicit human approval before the irreversible/external action and a tested recovery path.

## Acceptance criterion format

Acceptance criteria SHOULD be observable and binary where possible.

Good:
- `Destroy a renter mid-workflow; replacement renter completes without duplicate side effects.`
- `Unauthorized tenant scope returns a denied policy decision.`

Weak:
- `Make it robust.`
- `Improve UX.`

Qualitative criteria are allowed only when the verifier and evidence method are declared.

## Verification contract

Each criterion declares one or more verification methods:

- `unit`
- `integration`
- `e2e`
- `schema`
- `security`
- `performance`
- `accessibility`
- `human-review`
- `model-eval`

Model-based evaluation MUST be labelled as probabilistic and MUST NOT replace hard security/governance assertions.

## Steering

Steering occurs at meaningful decision boundaries:

- scope amendment;
- capability escalation;
- acceptance-criterion failure;
- destructive action;
- production promotion;
- rollback.

KPGS SHOULD avoid requiring humans to supervise every low-level agent action when the spec and capabilities already bound the task safely.

## Release proof

A released artifact MUST be traceable to:

`spec -> implementation revision -> verifier outputs -> evidence bundle -> approval/policy decision -> release`

If that chain cannot be reconstructed, the release is not canonically governed.
