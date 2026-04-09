---
title: Multi-Agent Profiling Framework
created: 2026-04-09
updated: 2026-04-09
author: Codex
tags:
  - training
  - profiling
  - agents
  - humans
priority: high
status: active
---

# Multi-Agent Profiling Framework

> Reusable profiling framework for people, AI agents, and collaboration systems inside Orch.

## Why Profile At All

Orch is not only a tool executor.
It is a coordination system.

Coordination improves when the system knows:

- who is reliable under pressure
- who needs tighter scope
- who synthesizes well
- who drifts, fabricates, or overwrites
- which personalities fit which tasks

## Core Dimensions

| Dimension | Human Meaning | AI Meaning |
|-----------|---------------|------------|
| Truthfulness | says what is real | does not fabricate progress or state |
| Scope discipline | stays inside the request | edits only owned files and tasks |
| State hygiene | keeps notes and trackers aligned | keeps control files, diffs, and logs aligned |
| Recovery behavior | responds well to mistakes | fixes cleanly and verifies after failure |
| Communication fidelity | updates clearly and on time | reports what actually changed |
| Autonomy fit | needs less supervision | can execute safely without constant prompts |
| Tool discipline | uses the right tools | does not overuse or misuse powerful tools |
| Vault hygiene | respects shared knowledge systems | preserves links, note homes, and dashboards |

## Profile Types

## Human Operator Profile

Use for owners, leads, and reviewers.

Track:

- pace tolerance
- preferred level of explanation
- trust triggers
- escalation triggers
- preferred source-of-truth format

## AI Lead Profile

Track:

- orchestration quality
- delegation quality
- verification quality
- tendency to over-code vs over-manage
- ability to keep control files synchronized

## AI Worker Profile

Track:

- bounded task performance
- update-in-place safety
- phantom completion risk
- stray file risk
- build-break risk

## Artifact Or System Profile

Use for things like an Obsidian vault, CI pipeline, or shared backlog.

Track:

- stability requirements
- external references
- allowed mutation types
- fragility points
- verification commands

## Required Output Format

Every profile should answer:

1. what this subject is good at
2. what breaks trust fastest
3. what operating conditions make it succeed
4. what constraints make it safe
5. what one rule future Orch runs should remember

## Current Training Linkage

- [Owner Profile](Owner%20Profile.md)
- [Robyn Operator Profile - Session 3](Robyn%20Operator%20Profile%20-%20Session%203.md)
- [Lead Self Report](Lead%20Self%20Report.md)
- [Codex Terminal Operational Profile](Codex%20Terminal%20Operational%20Profile.md)
- [Dev2 Behavioral Analysis](Dev2%20Behavioral%20Analysis.md)
- [Claude Codex Gemini Session Analysis](Claude%20Codex%20Gemini%20Session%20Analysis.md)
