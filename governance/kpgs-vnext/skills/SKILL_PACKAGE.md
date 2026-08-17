# KPGS Canonical Skill Package Contract

Issue: #37

## Purpose

A KPGS skill is a portable operating procedure that a human, coding agent or Stateless Renter can discover and execute under an explicit capability lease. The skill describes **how to perform a bounded job**; it does not grant authority by itself.

The upstream agent-skill pattern observed in `RobynAwesome/Skills` / `MengTo/Skills` is useful because it keeps procedures narrow, portable and versionable. KPGS adds machine-readable governance, capability boundaries, provenance and evaluation evidence around that pattern.

## Package layout

```text
skills/<category>/<skill-name>/
  SKILL.md                 # human/agent operating procedure
  skill.json               # KPGS machine-readable manifest
  REFERENCES.md            # optional links and provenance notes
  ARTICLE.md               # optional long explanation
  scripts/                 # optional helpers
  assets/                  # optional reusable assets
  examples/                # optional fixtures
  tests/                   # optional conformance/eval fixtures
```

## Canonical registry and discovery

`governance/kpgs-vnext/skills/registry.json` is the canonical discovery index. Registration means KPGS may discover and inspect a package; **registration does not grant execution authority**.

Registry entries declare:

- package identity and version;
- category and repository-relative package path;
- authority class (`canonical-core` or `publication-adapter`);
- plain-language discovery summary and tags.

Validate the registry and every registered package with:

```bash
python scripts/ci/validate_skill_registry.py
```

Search registered skills without loading them:

```bash
python scripts/ci/validate_skill_registry.py --discover governance
python scripts/ci/validate_skill_registry.py --discover "" --platform stateless-renter
```

The validator rejects duplicate identities, missing package files, manifest/registry identity drift, missing provenance/license state, missing capability declarations and missing validation contracts. CI runs the same conformance logic through `tests/test_skill_registry.py`.

A registered package is production-selectable only when its manifest state is `validated` or `approved`. The caller must still separately obtain a capability lease equal to or narrower than the package requirements. `draft`, `blocked` and `deprecated` packages remain non-production-loadable even when discoverable.

Publication adapters may be indexed so external package surfaces can be found and validated, but their `authority_class` must remain `publication-adapter`; registry presence must never be interpreted as a second canonical runtime.

## Required `SKILL.md` frontmatter

```yaml
---
name: kpgs-example-skill
description: What the skill does and when it should be used.
---
```

`SKILL.md` SHOULD remain procedural: triggers, preconditions, steps, guardrails, verification and recovery. Long theory belongs elsewhere.

## Required machine contract

`skill.json` MUST declare:

- skill identity and semantic version;
- description/category;
- runtime compatibility;
- input/output contracts;
- required capabilities;
- dependencies;
- provenance/license status;
- validation/evaluation contract;
- failure/recovery semantics.

The schema is `skill-manifest.schema.json`.

## Runtime lifecycle

```text
discover
  -> resolve policy
  -> verify package/provenance
  -> lease capabilities
  -> load
  -> execute
  -> validate output
  -> emit evidence
  -> release capabilities
```

## Governance rules

1. A skill never grants itself permission.
2. The active capability lease MUST be equal to or narrower than the skill's declared capability requirements.
3. A renter MUST reject a skill whose runtime/protocol compatibility is not satisfied.
4. Imported or fork-derived skill material MUST carry provenance and license metadata.
5. `pending`, `unknown` or incompatible license status blocks canonical vendoring/import.
6. Skills MUST NOT contain raw secrets, private client data or machine-specific absolute paths as required runtime assumptions.
7. Skill promotion requires declared validation evidence.
8. Breaking behavior changes require a major-version compatibility decision or migration note.

## Skill states

- `draft`
- `validated`
- `approved`
- `deprecated`
- `blocked`

Only `validated` or `approved` skills may be selected for governed production execution, subject to domain policy.

## Validation dimensions

A skill MAY use several verification methods, but each package MUST declare at least one:

- schema/contract validation
- deterministic test fixture
- integration test
- end-to-end workflow test
- security review
- accessibility review
- human review
- probabilistic/model evaluation

Probabilistic evaluation cannot override a failing hard security or governance check.

## User-facing requirement

When a skill fails, KPGS SHOULD translate the failure into:

- what was attempted;
- why it could not continue;
- whether the user can recover;
- the next safe action.

Everyday users should not need to understand skill manifests, MCP, renters or transport internals to complete their task.
