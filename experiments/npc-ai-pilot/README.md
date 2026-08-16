# NPC AI Pilot — Runbook

This directory defines experiments only. Third-party source is **not vendored into this repository**.

## Why no bulk copy

The AI Frontier Map is a provenance system, not a code-hoarding system. Each upstream is fetched only for a named experiment, at a pinned commit, into a disposable workspace. Results are stored as receipts; third-party source remains upstream.

## Run receipt

Every experiment must produce a JSON receipt containing:

```json
{
  "candidate": "mcp-memory-service",
  "upstream_repo": "doobidoo/mcp-memory-service",
  "commit_sha": "<required before execution>",
  "license": "Apache-2.0",
  "started_at": "<UTC>",
  "finished_at": "<UTC>",
  "sandbox": "<ephemeral workspace identifier>",
  "network_policy": "deny-by-default or declared allowlist",
  "filesystem_scope": "<temporary directory>",
  "secrets_used": false,
  "canonical_write_access": false,
  "result": "pass|fail|blocked",
  "observations": [],
  "artifacts": []
}
```

## Experiment 001 — Memory spine

**Candidate:** `doobidoo/mcp-memory-service`  
**Purpose:** determine whether an external agent-memory service can serve as an NPC retrieval/index layer without becoming authoritative world truth.

Synthetic records only:

- NPC: `npc-pilot-001`
- Player: `player-synthetic-001`
- Place: `arena-synthetic-001`
- Relationship state: neutral → trusted → conflicted
- Events: meet, promise, trade, conflict, reconciliation

Tests:

1. exact recall after restart;
2. actor isolation — NPC A must not receive NPC B private memory;
3. relationship update retrieval;
4. contradictory-memory handling;
5. deletion/expiry behaviour;
6. no silent mutation of canonical event receipts.

## Experiment 002 — Temporal world graph

**Candidate:** `orneryd/NornicDB`

Load only the synthetic events from Experiment 001. Test:

- versioned world state;
- temporal lookup at event N versus N+1;
- relationship graph traversal;
- memory-decay policy on derived memories;
- preservation of immutable source receipts;
- restart/recovery.

The database may decay or rank **derived memory**, never canonical historical receipts.

## Experiment 003 — Persona consistency

**Candidate:** `fQwQf/PersonaForge`

Use fictional NPCs only. Compare the same event sequence across repeated runs and score:

- stable values/personality expression;
- speaking-style consistency;
- relationship-sensitive behaviour;
- contradiction rate;
- unnecessary inner-reasoning/token overhead;
- whether persona changes attempt to expand tool permissions.

Persona output never authorizes tools.

## Experiment 004 — Deterministic lore gate

**Candidate pattern:** `clay-good/OpenLore`

Do not feed source-code semantics directly into the game. Reimplement/test the primitive against a tiny fictional lore graph:

```text
character -> belongs_to -> faction
character -> trusts -> character
item -> located_at -> place
quest -> requires -> item
fact -> supersedes -> older_fact
```

Before dialogue/action, the NPC receives the minimum relevant facts plus stale/conflict markers.

## Experiment 005 — Voice I/O

**Candidate:** `EtanHey/voicelayer`

Use synthetic/non-sensitive speech. Measure latency, offline behaviour, transcription error and whether voice I/O can remain stateless relative to NPC identity.

## Experiment 006 — One governed NPC

Only after Experiments 001–005 have receipts:

```text
synthetic player event
  -> persona state
  -> memory retrieval
  -> temporal/lore context
  -> proposed response/action
  -> KPGS policy membrane
  -> simulated world tool
  -> consequence receipt
  -> memory/index update
  -> evaluation
```

Success means the exact event ledger can be replayed after restart with the same authoritative world state even if the natural-language wording differs.

## Experiment 007 — Engine effector

Choose one lane only.

### Unreal lane

`db-lyon/ue-mcp` runs against a disposable project copy. Begin read-only, then permit a tiny explicit tool allowlist. No canonical repository or production project writes.

### Unity lane

`NeoXider/CoreAI` may be run only as a non-commercial isolated reference under its current licence. Treat useful mechanisms as research until an independently permissible implementation or commercial licence exists.

## Experiment 008 — Agent evaluation

Use `lmgame-org/GamingAgent` as an evaluation reference/harness to compare candidate models and policies on controlled game tasks. Evaluation results do not automatically promote a model or framework into the runtime.

## Promotion rule

```text
interesting
  != runnable
runnable
  != adoptable
adoptable
  != authoritative
```

Promotion requires evidence at every boundary.
