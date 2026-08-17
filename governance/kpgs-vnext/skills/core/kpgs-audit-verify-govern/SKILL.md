---
name: kpgs-audit-verify-govern
description: Audit a proposed KPGS change against its governing specification, verify the strongest available evidence, classify unproven claims, and produce a governance decision or safe next action. Use before promotion, release, capability escalation, or when a user asks whether a change actually works.
---

# KPGS Audit, Verify, Govern

## Trigger

Use this skill when KPGS must decide whether an implementation, workflow, domain migration, skill, renter or release is sufficiently proven to move forward.

## Required context

Before execution, resolve:

1. the governing specification;
2. acceptance criteria;
3. implementation/release reference;
4. available verifier outputs;
5. active capability lease if this skill will perform external reads/writes;
6. rollback/recovery reference for any production-impacting decision.

If the governing specification cannot be identified, stop with `SPEC_MISSING` rather than inventing criteria after the implementation exists.

## Workflow

### 1. Audit the claim

Translate the requested outcome into concrete claims that can be checked.

For each claim classify it as:

- `specified` — explicitly required by the governing spec;
- `out-of-scope` — not part of this task;
- `new-requirement` — useful but requires a spec amendment;
- `unsupported-claim` — asserted without evidence.

Do not allow implementation scope to silently expand the specification.

### 2. Resolve the strongest available evidence

Prefer, in order:

1. deterministic tests/schema/security gates;
2. integration or end-to-end execution of the real workflow;
3. runtime logs, screenshots, traces or generated artifacts;
4. static inspection;
5. clearly labelled inference.

Never report inference as execution evidence.

### 3. Check hard gates first

Evaluate security, tenant isolation, capability scope, destructive-action controls and other criteria marked `hard_gate=true`.

If any hard gate fails:

- decision cannot be `promote`;
- record the failing criterion and evidence;
- choose `hold`, `deny` or `rollback` according to the spec and current lifecycle state.

A high aggregate score cannot override a failed hard gate.

### 4. Check continuity and recovery

For Stateless Renter work, verify that destruction/recreation does not lose canonical truth or duplicate durable side effects.

For domain/release work, verify the rollback path before production promotion.

### 5. Produce the evidence bundle

Correlate:

`estate property -> release -> adapter -> renter -> skill -> task -> verifier -> governance decision`

Record only references to secrets/credentials, never raw secret material.

### 6. Decide

Allowed decisions:

- `allow` — bounded action may proceed;
- `deny` — policy or hard criterion forbids continuation;
- `promote` — verified artifact may advance lifecycle state;
- `hold` — more evidence or approval is required;
- `rollback` — the current release/state should revert according to the declared recovery path.

## Plain-language output

For everyday users, explain only:

- what was checked;
- what is proven;
- what is not proven;
- the decision;
- the next safe action.

Do not expose MCP, WebSocket, schema or renter terminology unless it helps the user complete the task.

## Guardrails

- Do not fabricate evidence.
- Do not mark CI as a code failure when the runner never started.
- Do not import fork-derived code whose license/provenance gate is still pending.
- Do not promote a release without a rollback path when the governing spec requires one.
- Do not treat runtime warmth/temperature configuration as model-weight fine-tuning.

## Failure codes

- `SPEC_MISSING`
- `EVIDENCE_INSUFFICIENT`
- `HARD_GATE_FAILED`
- `CAPABILITY_DENIED`
- `VERIFIER_UNAVAILABLE`
- `ROLLBACK_UNPROVEN`
- `PROVENANCE_BLOCKED`
