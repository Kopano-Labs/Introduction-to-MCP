# KC — Stateful Observer / Sub-Membrane Landlord

Status: **POC / read-only / snapshot-first**

KC is Seat 1 of KPGS. He observes, correlates and publishes governed state. He does **not** take APEX orchestration authority, KHELOS validation authority, or human choice authority.

## Evolution

```text
KC RTCP context publisher
        ↓
context + urgency landlord
        ↓
Sub-Membrane estate observer
        ↓
evidence-aware sovereignty map
        ↓
KC dashboard
```

The dashboard turns KC's existing RTCP signals (`CONTEXT_SOURCE_LOCK`, `CONTEXT_GAP`, `URGENCY_PING`, `EMOTIONAL_FUEL`, `STATE_UPDATED`) into a read-only estate view spanning governed repositories, capability renters, receipts, unresolved gates and provenance.

## Sub-Membrane law

Every repository is represented as a **Sub-Membrane**, not copied wholesale into the canonical repository.

A Sub-Membrane descriptor records source identity, default branch, pinned revision when witnessed, authority class, ingestion state, extracted logic facets and provenance notes. Discovery never grants canonical authority. Imported logic must be reviewed and admitted under KPGS contracts.

`Introduction-to-MCP` remains the only canonical governance membrane in this registry.

## Weekend ingestion

The user supplied `14 August 2026 to 17 August 2025`, which reverses chronology. Because this work concerns the just-completed weekend on 17 August 2026, the governed window is normalized to **14–17 August 2026** and the literal input is retained in `weekend-window.json`.

GitHub discovery query:

`user:RobynAwesome pushed:2026-08-14..2026-08-17`

13 repositories are seeded. 10 have pinned observed heads; 3 remain explicitly `discovered-pending-pin`. That is ingestion honesty: seeded does not mean semantically exhausted.

## Dashboard design source

The TypeScript 7 dashboard applies two explicit `RobynAwesome/Skills` references:

- `agent-skills/ui/design-first-ui-prompting/SKILL.md` — stable shell, hierarchy first, restrained accent, consistent spacing.
- `agent-skills/web-design/animation-systems/SKILL.md` — motion only for hierarchy/feedback/continuity, transform/opacity first, reduced-motion mandatory.

The runtime stack follows the current Kopano Labs website precedent: React 19.2.4, Vite 8.1.5 and TypeScript 7.0.2. The dashboard deliberately avoids WebGL: KC's topology is operational information, not decorative 3D.

## Dashboard surfaces

- **Context Lock:** source, freshness and current KC boundary.
- **Gate Rail:** unresolved P1/P2 gates with owner.
- **Sub-Membrane Topology:** all seeded repositories around KC, with canonicality and ingestion badges.
- **Selected Membrane Inspector:** source ref, revision, facets and ingestion state.
- **Frontier Lanes:** Snowflake, Google AI, ElevenLabs, Solana and offline replication state.
- **KC Authority Card:** what KC may observe/publish vs what he must hand to APEX/KHELOS/human authority.

The current application is a **snapshot POC**. It does not fake realtime connectivity.

## Run

```bash
cd apps/kc-dashboard
npm install
npm run typecheck
npm run build
```

Repository-native contract gate:

```bash
python governance/kpgs-vnext/kc/validate_kc.py
```

## Promotion boundary

Before the dashboard can be called operational, KPGS must prove live ingestion receipts, live source freshness, deployed dashboard evidence, and handoff receipts to APEX/KHELOS. KC remains landlord of observed context, never the executor.
