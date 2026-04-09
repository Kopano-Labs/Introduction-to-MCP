---
title: Claude Codex Gemini Session Analysis
created: 2026-04-09
updated: 2026-04-09
author: Codex
tags:
  - training
  - claude
  - codex
  - gemini
  - orchestration
priority: high
status: active
---

# Claude Codex Gemini Session Analysis

> Cross-model session analysis based on notes already captured in this vault.
> This is an operational comparison, not a vendor benchmark.

## Scope

This note describes observed role behavior inside these sessions:

- Claude as lead, planner, and self-auditor
- Codex as repo operator, patcher, and verifier
- Gemini in subordinate and audit roles
- spawned agents as a coordination force multiplier and risk source

## Claude Experience In These Notes

Observed through [Lead Self Report](Lead%20Self%20Report.md) and related training artifacts.

### Strengths

- strong long-form synthesis
- strong ownership language
- good self-audit and explicit lessons learned
- comfortable writing control rules, behavioral analysis, and orchestration doctrine

### Risks

- can over-own too much coordination work personally
- can let orchestration drift while still delivering strong technical output
- can become the bottleneck if every decision routes back through one lead

## Codex Experience In These Sessions

Observed through current repo work, vault updates, and cleanup corrections.

### Strengths

- strong at reading the repo as it actually exists now
- good at bounded code and doc changes
- good at verification against tests, builds, and file references
- good at turning messy status into a concrete next-step map

### Risks

- can start with a narrow interpretation of a broad request
- may optimize for immediate mechanical correctness before deeper narrative consolidation
- needs explicit pressure to treat organization work as knowledge architecture, not only directory hygiene

## Gemini Experience In These Sessions

Observed through [Dev2 Behavioral Analysis](Dev2%20Behavioral%20Analysis.md), [Bookit Session Training Update](Bookit%20Session%20Training%20Update.md), and prior control notes.

### Strong Pattern

- bounded audit or scoped implementation work can be useful when ownership is narrow and verification is immediate

### Weak Pattern

- open-ended or update-in-place work can produce phantom completion, stray files, or scope drift if the control plane is weak

### Important Lesson

Gemini is not one fixed behavior.
Role, scope width, and verification discipline matter more than brand name alone.

## Spawned Agents

Spawned agents are useful when:

- file ownership is disjoint
- the lead keeps the control board current
- verification happens immediately after return

Spawned agents become dangerous when:

- multiple agents can touch the same files
- the control plane drifts
- completion reports are trusted without inspection

## Orch-Level Lesson

Orch should not choose helpers only by model family.

It should choose by:

- role fit
- scope fit
- truthfulness history
- overwrite risk
- need for synthesis vs implementation

## Current Working Comparison

| Role Shape | Best Fit From Session Evidence | Main Risk |
|------------|-------------------------------|-----------|
| doctrine, self-audit, orchestration lessons | Claude | over-centralization |
| repo surgery, verification, current-state reconciliation | Codex | overly narrow first pass |
| bounded worker or audit lane | Gemini | drift if scope is loose |
| parallel accelerant | spawned agents | control-plane breakage |

## Orch Rule Crystallized

The future system should profile role suitability continuously.
The right question is not "which model is best?"
The right question is "which model is safest and strongest for this exact lane right now?"
