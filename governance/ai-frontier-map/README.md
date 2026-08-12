# AI Frontier Map

> **Status:** Phase 1 — provenance-first corpus construction  
> **Authority:** KPGS / Introduction-to-MCP

The AI Frontier Map converts public AI repositories into an evidence-backed engineering-intelligence graph. The unit of analysis is not a repository name; it is a provenance record linking the observed repository to its upstream developer, original source, technical primitive, capability/risk surface, licence and permitted reuse mode.

## Pipeline

```text
OyaAIProd corpus
  -> enumerate every repository
  -> classify provenance
  -> resolve upstream parent/source
  -> recover original developer + project metadata
  -> locate SafeSkill scan/PR evidence
  -> extract security surface
  -> identify technical primitive
  -> resolve licence
  -> score frontier value
  -> calculate KPGS convergence
  -> ADOPT / ADAPT / STUDY / MONITOR / REJECT
```

## Immutable rules

1. **No primitive without provenance.**
2. **No code without licence.**
3. **No convergence without validation.**
4. **Do not equate `fork:false` with original authorship.** Detached forks require commit/PR/history evidence.
5. **Do not rank by stars alone.** Frontier value measures engineering signal, not popularity.
6. **Collector facts and analyst inferences remain separate fields.**

## Reuse membrane

- **CODE REUSE** — licence explicitly permits reuse and all obligations are preserved.
- **ARCHITECTURAL REUSE** — understand the public pattern and independently implement it.
- **RESEARCH ONLY** — study the project but do not import implementation code.

Every reuse receipt records:

```text
UPSTREAM + AUTHOR + REPOSITORY + COMMIT SHA + LICENSE + DISCOVERY DATE
+ WHAT WE LEARNED + WHAT WE TOOK + HOW WE CHANGED IT
```

## Frontier score

| Dimension | Weight |
|---|---:|
| Novelty | 20% |
| Technical depth | 20% |
| Composability | 20% |
| Ecosystem relevance | 15% |
| KPGS relevance | 15% |
| Current activity | 10% |

Each dimension is scored 0–5 and normalized to 100. `confidence_score` is independent: value and evidentiary certainty are not the same thing.

## Product map × risk map

**Product:** problem, capability, architecture, protocol, integrations, composability, novel abstraction.

**Risk:** filesystem, network, secrets, database, browser, process execution, repository mutation, cloud access, authentication, prompt injection and taint flow.

## Convergence verdicts

- **ADOPT** — directly reusable and worth integrating.
- **ADAPT** — valuable primitive; independently implement/adapt for KPGS.
- **STUDY** — important intelligence; no implementation decision yet.
- **MONITOR** — immature/emerging and worth tracking.
- **REJECT** — redundant, incompatible, unsafe or irrelevant.

## Phase 1 deliverables

- `provenance-record.schema.json` — canonical record contract.
- `tools/ai_frontier_map/collect_oya_corpus.py` — deterministic GitHub metadata collector.
- `tools/ai_frontier_map/validate_corpus.py` — local/CI invariant gate.
- `data/ai-frontier-map/seed.records.jsonl` — verified seed evidence.
- `.github/workflows/ai-frontier-map-gate.yml` — provenance/reuse CI gate.

The collector intentionally does **not** invent technical-intelligence fields. Those are populated only after source inspection.
