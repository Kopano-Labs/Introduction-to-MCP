# AI Frontier Map — Phase 1

**Date:** 2026-08-12  
**State:** IMPLEMENTATION READY  
**Target:** `RobynAwesome/Introduction-to-MCP`

## Objective

Turn the OyaAIProd public corpus into a provenance-preserving AI engineering intelligence map without treating Oya forks as Oya-authored inventions.

## Build order

1. Lock provenance record schema.
2. Collect all current OyaAIProd public repositories.
3. Resolve GitHub-native parent/source relationships.
4. Cross-reference SafeSkill badge PRs authored by OyaAIProd.
5. Keep detached forks as a separate forensic class.
6. Preserve licence metadata but default automated records to `research_only`.
7. Manually inspect upstream source before populating technical intelligence.
8. Score frontier value only after architecture review.
9. Record KPGS convergence verdict.
10. Cluster primitives after enough reviewed records exist.

## Phase 1 acceptance criteria

- Automated collector can enumerate the corpus with GitHub-observable facts.
- No collector inference can silently become `code_reuse`.
- Every record carries at least one evidence URL.
- Native forks resolve an upstream.
- SafeSkill forks require a scan/PR evidence receipt.
- Code reuse requires explicit licence + source commit + provenance URL.
- Frontier scores are either fully scored or fully unscored.
- CI rejects violations.

## First reviewed seed projects

- `RobynAwesome/Introduction-to-MCP` (repository ID `1188724145`; historically `Kopano-Labs/Introduction-to-MCP`) ↔ detached `OyaAIProd/Introduction-to-MCP`
- `cl0nazepamm/3dsmax-mcp`
- `shinpr/mcp-local-rag`
- `exa-labs/exa-mcp-server`

## Next phase

Run collector, produce corpus statistics, then select the first 25 upstream projects for manual primitive extraction based on architecture diversity rather than popularity.
