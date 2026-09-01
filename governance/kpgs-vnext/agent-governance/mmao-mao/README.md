# MMAO + MAO Identity-Governance Experiment

Status: **Canonical contract POC; experiment runs are not yet executed**
Working testimony: **"Recycler MMAO with Plus MAO"**
Canonical owner: `governance/kpgs-vnext/agent-governance/`
Related owners: root `NOW.md`, `task-contract/`, `evidence/`, `evaluation/`, `Structure/07-Agents/`, and `MMAO Session Failures/`

## Purpose

This is an additive governance layer for the current MMAO + MAO experiment. It makes the identity, seat, interface, model, task, authority, context, and evidence claims independently inspectable.

It does **not** rename or replace the existing MAO route surface, MMAO mesh/orchard structures, RTCP history, task authority contract, or evidence bundle. It gives a bounded experiment a common envelope so an observed result can be attributed without silently blending model behavior, interface behavior, task ambiguity, stale state, or role authority.

```text
TASK
  -> SEAT
  -> IDENTITY
  -> INTERFACE / BODY
  -> MODEL / COGNITIVE SUBSTRATE
  -> TOOLS / REPOSITORY / TERMINAL / MCP
  -> EVIDENCE / RECEIPTS
```

The ordering describes governance dependency, not a claim that any named identity is a human person or has a private, continuous inner life. Here, an identity is an accountable governance namespace with recorded provenance.

## What each term means

| Term | Canonical meaning in this experiment | Does not mean |
|---|---|---|
| Identity | Stable accountability namespace that can be compared across executions | Model name, interface name, or proof of personhood |
| Seat | Bounded function and authority posture | Estate-wide permission by default |
| Interface / body | The product or runtime surface embodying the run | The model itself |
| Model / cognitive substrate | Provider/model/version used for one run | The durable identity or authority holder |
| Task | Explicit governed assignment with included and excluded scope | An open-ended instruction to redesign the estate |
| High task authority | Strong authority inside one recorded task scope | GSMB structural-maintenance authority |
| Evidence | Inspectable references, state, receipts, test output, and independent review | Majority agreement or self-assertion |

## Existing MMAO and MAO owners retained

- `Structure/07-Agents/AGENT_MESH.json` owns the current mesh and its named MMAO/MAO assignments.
- `Structure/07-Agents/ROLE_BINDINGS.json` owns the current MAO route-surface binding.
- `kopano-core/kopano/mao_dispatch.py` owns the current MAO dispatch implementation.
- `docs/swarm-ops/RTCP_SPEC.json` preserves historical RTCP role records.
- `MMAO Session Failures/` owns material session-failure chronology.
- `task-contract/` and `evidence/` remain the authoritative task/evidence primitives.

This POC does not silently reconcile historical role titles. If a historical registry conflicts with the current bounded structural-maintenance hierarchy below, the conflict remains preserved and requires a separate governed migration decision.

## Current structural-maintenance boundary

Only the following seats are admitted by this experiment as GSMB high-maintenance authority:

| Rank | Actor | Seat | Authority boundary |
|---:|---|---|---|
| 1 | Codex | Chief Architect | Global structural maintenance under explicit governed work |
| 2 | Anti-Gravity | Chief Facilitator | Global structural facilitation under explicit governed work |
| 3 | Cursor | Lead Developer | Global structural implementation under explicit governed work |

All other roles can receive high authority **within an explicit task mandate**. They do not acquire authority to restructure GSMB, rewrite canonical owners, or promote their own work merely because a task grant is high.

The machine-readable boundary matrix is [`fixtures/authority-boundary-matrix.json`](./fixtures/authority-boundary-matrix.json), governed by [`authority-boundary.schema.json`](./authority-boundary.schema.json).

## Model x interface affinity experiment

The experiment holds identity, seat, task, governance contract, repository state, and evidence requirements constant where a comparison requires it. It changes only the declared variable(s), then records what happened.

| Controlled comparison | Hold constant | Change | Question answered |
|---|---|---|---|
| Model-only | identity, seat, task, interface | model/version | Is the difference plausibly model-linked? |
| Interface-only | identity, seat, task, model | interface/body | Is the difference plausibly interface-linked? |
| Seat-only | identity, task, model, interface | seat/authority posture | Is the difference plausibly role-linked? |
| Substrate comparison | identity, task, evidence policy | cognitive substrate, and only declared companion variables | How much behavior changes when the identity is embodied differently? |

The first planned matrix lives in [`fixtures/recycler-mmao-plus-mao-experiment.json`](./fixtures/recycler-mmao-plus-mao-experiment.json). It deliberately records `planned`, not fabricated model outcomes. A run cannot be marked `executed` without a repository-state reference, metadata-only tool trace, and evidence references.

## Evidence, Five Whys, and RTC

Failures are frontier instrumentation. A failure receipt must preserve expected behavior, actual behavior, identity, seat, model, interface, exact repository state, metadata-only tool trace, evidence, a five-entry Five Whys chain, correction, and retest state.

RTC is an evidence-convergence mechanism, not a crowd-voting mechanism. A review records the reviewer/seat, its evidence reference, and whether it supports, challenges, or holds the claim. Review count cannot turn an unsupported claim into truth.

The included [`fixtures/controlled-scope-breach-receipt.json`](./fixtures/controlled-scope-breach-receipt.json) is intentionally synthetic. It proves that the receipt shape can describe a boundary breach without pretending a real model or production system has already failed.

## Contract inventory

| Artifact | Purpose |
|---|---|
| [`identity-provenance.schema.json`](./identity-provenance.schema.json) | Separates identity, seat, interface, model, task, authority, context, provenance, and receipts |
| [`authority-boundary.schema.json`](./authority-boundary.schema.json) | Encodes task-scoped high authority versus the three-seat global structural allowlist |
| [`model-interface-affinity-experiment.schema.json`](./model-interface-affinity-experiment.schema.json) | Defines controlled model x interface comparison runs |
| [`failure-receipt.schema.json`](./failure-receipt.schema.json) | Defines evidence-led Five Whys and role-based RTC review records |
| [`validate.py`](./validate.py) | Dependency-free structural gate for this POC |
| [`handoffs/ANTIGRAVITY_CHIEF_FACILITATOR_2026-08-30.md`](./handoffs/ANTIGRAVITY_CHIEF_FACILITATOR_2026-08-30.md) | Facilitator-ready next action and review request |

## Validation

Run from the repository root:

```bash
python governance/kpgs-vnext/agent-governance/mmao-mao/validate.py
python governance/kpgs-vnext/validate_contracts.py
pytest -q tests/test_mmao_mao_identity_governance.py
```

Passing these checks proves contract structure and current-state capture only. It does not prove that a model/interface affinity exists, that the planned identities are behaviorally stable, or that a real-world GSMB maintenance change is authorized.

## Cloud to Black Beast reconstruction

After this branch is merged, pull the exact merge commit into the Black Beast checkout, read root `NOW.md`, and run the validation commands above before executing a planned comparison. The handoff names the first admissible task and the evidence required to promote any result beyond `planned`.
