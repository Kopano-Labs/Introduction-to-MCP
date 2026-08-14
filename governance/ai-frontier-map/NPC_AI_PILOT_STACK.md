# NPC AI Pilot Stack

> **State:** EXPERIMENTAL / GOVERNED  
> **Parent:** AI Frontier Map  
> **Rule:** Study the upstream, preserve provenance, run only through the execution membrane.

## Goal

Use the AI Frontier Map to identify open-source primitives that can strengthen the NPC roadmap without importing an uncontrolled second orchestration system into KPGS.

The target is not one giant NPC framework. The target is a composable NPC stack:

```text
PLAYER / WORLD EVENT
        |
        v
VOICE / INPUT ------------------------------ EtanHey/voicelayer
        |
        v
PERSONA / MIND ----------------------------- fQwQf/PersonaForge
        |
        v
MEMORY ------------------------------------- doobidoo/mcp-memory-service
        |
        +--> TEMPORAL WORLD GRAPH ---------- orneryd/NornicDB
        |
        +--> LORE / TRUTH GATE ------------- clay-good/OpenLore pattern
        |
        v
KPGS GOVERNANCE + CANONICAL RECEIPT
        |
        v
WORLD ACTUATION ---------------------------- db-lyon/ue-mcp (Unreal lane)
        |
        v
GAME CONSEQUENCE / TELEMETRY
        |
        v
EVALUATION --------------------------------- lmgame-org/GamingAgent pattern
        |
        +--> replay into memory + governance
```

`NeoXider/CoreAI` is a separate **Unity executable reference lane**: useful for seeing a complete NPC runtime operating end-to-end, but its current PolyForm Noncommercial licence means it stays `RESEARCH ONLY` unless a commercial licence/permission is obtained.

## Candidate decisions

| Candidate | NPC lane | Licence | First decision | Why |
|---|---|---|---|---|
| `db-lyon/ue-mcp` | Unreal/world actuation | MIT | **ADAPT** | Deep engine/gameplay actuation through MCP; high mutation authority requires disposable engine sandbox. |
| `doobidoo/mcp-memory-service` | Persistent memory | Apache-2.0 | **ADAPT** | Strong cross-session and graph-memory primitive. External memory must not replace canonical KPGS receipts. |
| `orneryd/NornicDB` | Temporal world memory | MIT | **STUDY → PILOT** | Temporal MVCC + graph/vector + memory decay maps well to world timelines and relationship evolution. |
| `clay-good/OpenLore` | Lore truth gate | MIT | **ADAPT** | Deterministic local-first knowledge/guardrail pattern; upstream is code-oriented, so adapt the primitive rather than the domain. |
| `EtanHey/voicelayer` | Voice I/O | Apache-2.0 | **PILOT** | Small bounded local STT/TTS surface. |
| `fQwQf/PersonaForge` | Persona/mind | Apache-2.0 | **STUDY → PILOT** | Direct research fit for personality-consistent role-playing agents. |
| `NeoXider/CoreAI` | Unity NPC runtime | PolyForm Noncommercial 1.0 | **RESEARCH ONLY** | Direct runnable NPC reference with tools/memory/local models, but not eligible for commercial code reuse under current licence. |
| `lmgame-org/GamingAgent` | Evaluation | MIT | **ADAPT** | Game-agent evaluation primitive for regression/model comparison, not authoritative runtime. |

## Authority boundaries

### External memory is not canonical truth

An NPC memory engine may retrieve, associate, consolidate or decay memories. It may **not** silently rewrite authoritative world history. Canonical world changes require a KPGS receipt/event with stable identity, timestamp, actor, action, result and provenance.

### Persona is not permission

Character personality can influence expression, priorities and relationship behaviour. It cannot expand tool permissions. Capability authority is assigned outside the LLM/persona prompt.

### Speech is I/O, not identity

TTS/STT output is an interface layer. Character identity and relationship state stay in the governed NPC record.

### Engine tools are effectors

Unreal/Unity/editor tools are treated as privileged effectors. The NPC proposes intent; a bounded tool contract performs the effect after policy checks.

## Run membrane

A candidate may move to `RUNNABLE` only when all gates pass:

```text
PROVENANCE RESOLVED
        +
LICENCE RESOLVED
        +
PINNED COMMIT
        +
DEPENDENCY / SECRET REVIEW
        +
CAPABILITY SURFACE DECLARED
        +
DISPOSABLE SANDBOX
        +
NETWORK / FILESYSTEM BOUNDS
        +
TELEMETRY + RECEIPTS ENABLED
        +
NO CANONICAL PROJECT WRITE ACCESS
        +
HUMAN APPROVAL FOR PRIVILEGED EFFECTS
        =
RUNNABLE NPC EXPERIMENT
```

## Pilot order

### P0 — static evidence

Pin upstream SHAs, inspect manifests/dependencies, record exact licence, enumerate filesystem/network/process/tool authority.

### P1 — headless primitives

Run components that do not require Unity/Unreal first:

1. memory-service in an isolated temporary store;
2. NornicDB with synthetic NPC/world records;
3. OpenLore-inspired deterministic lore graph experiment;
4. PersonaForge against synthetic fictional NPC personas;
5. voicelayer with non-sensitive test audio.

No production credentials. No canonical database. No Project Jennifer mutation.

### P2 — one NPC loop

Create a fictional `npc-pilot-001` with:

```text
persona
  -> receive event
  -> retrieve memories
  -> retrieve world/lore facts
  -> propose action
  -> governance check
  -> simulated tool action
  -> consequence
  -> memory receipt
  -> evaluation score
```

The first loop uses a simulated world adapter, not an engine.

### P3 — engine sandbox

Choose exactly one engine lane:

- **Unreal:** `ue-mcp` against a disposable project; or
- **Unity:** evaluate `CoreAI` non-commercial sandbox/reference behaviour and independently integrate permitted primitives.

Do not attach both engine stacks to the same NPC pilot initially.

### P4 — combat and multi-NPC

Only after deterministic single-NPC replay succeeds:

- perception and targeting;
- combat decisions;
- relationship updates from consequences;
- NPC-to-NPC communication;
- multi-agent contention;
- deterministic replay/regression tests.

## Acceptance metrics

A useful NPC is not measured only by natural dialogue. Record at least:

- identity consistency;
- memory precision / false-memory rate;
- lore contradiction rate;
- unauthorized-tool attempt rate;
- action success rate;
- consequence acknowledgement;
- relationship-state consistency;
- replay determinism;
- latency and token/context cost;
- offline/local survivability;
- recovery after restart.

## Immediate experiment

The first executable target is **not** an engine integration. It is a headless `npc-pilot-001` loop combining:

```text
PersonaForge pattern
+ mcp-memory-service
+ NornicDB temporal graph experiment
+ deterministic lore gate
+ simulated world tools
+ KPGS receipts
```

Once that passes, plug the same governed NPC contract into an engine effector. This keeps the NPC mind portable instead of welding identity/memory to Unity or Unreal.
