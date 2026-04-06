---
name: orch-repo-explorer
description: Explore a repository using the same delegation mechanics as Codex. Use when asked to survey a repo, map the active codepaths, find entry points, identify tooling or tests, or produce a compact codebase briefing. Trigger for prompts about repo exploration, codebase audit, project structure, entry points, tooling, tests, onboarding, and next inspection targets.
---

# Orch Repo Explorer

Use explorer-style delegation in three phases.

## Phase 1: Broad scout

Spawn one read-only explorer for the wide survey.

Use this prompt:

```text
Explore this repository and produce a concise codebase survey. Focus on:
1) top-level structure,
2) primary languages/frameworks/tooling,
3) likely app entry points,
4) test/build/lint commands if discoverable,
5) notable risks, oddities, or areas to inspect next.
Do not edit anything. Keep the result compact and practical.
```

## Phase 2: Parallel deep-dives

Spawn 2-4 read-only explorers in parallel. Keep scopes disjoint.

Recommended slices:

- App structure and runtime entry points
- Developer tooling, scripts, config, and CI
- Tests, docs, and onboarding risks
- Data model, integrations, or infra if the repo obviously has them

Use prompts with the same shape:

- define one narrow scope
- forbid edits
- ask for concrete file paths and commands
- ask for a compact actionable summary

## Phase 3: Synthesis

Merge the scout and deep-dive results into one briefing with:

- top-level structure
- active codepaths versus stale or duplicate ones
- primary stack
- runtime entry points
- build, test, lint, and dev commands
- notable risks, oddities, and cleanup candidates
- best next files or modules to inspect

## Working rules

- Prefer the active app surface over legacy or duplicate directories.
- Cite concrete paths when naming entry points or risky files.
- Keep the briefing compact. Avoid dumping every file.
- If the repo has multiple roots, explicitly separate active, legacy, and reference material.
- If asked to continue, turn the synthesis into targeted inspection tasks rather than repeating the survey.

## Handy follow-up prompts

Use these after the initial briefing:

- "Audit the active runtime path and separate production code from stale code."
- "Compare the current app surface with legacy duplicates and identify safe cleanup targets."
- "Deep-dive the tool system, persistence layer, and UI launch surface."
