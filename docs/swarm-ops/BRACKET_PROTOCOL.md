# Bracket Protocol — The Breaking Point

The **Bracket Protocol** is the Kopano-Phu handshake that marks when the Main Brain (Schematics) and all vault sub-brains are wired back into the Cassy legacy runtime.

## Bracket receipt format

```
[BRACKET_PROTOCOL] timestamp: 2026-05-21T12:00:00Z | ecosystem: Kopano-Phu | status: breaking_point | main_brain_ratio: 0.92 | attached: 9
```

Written to `docs/swarm-ops/logs/KC Main Brain Log.jsonl` with `kind: bracket_protocol` via `kc_phu_populate_main_brain.py` or `POST /api/kc/phu/populate-main-brain`.

## Breaking Point (all true)

1. **Main Brain populated** — ≥85% of indexed Schematics paths exist (logs, registry, roadmap, protocols).
2. **Sub-brains attached** — no detached rows with vault folders present (after reattach).
3. **Bracket receipt** — latest Main Brain log row is `bracket_protocol`, `kimi_ack`, or contains `[BRACKET`.

## Relation to Kimi ACK

[KIMI_ACK_FORMAT.md](./KIMI_ACK_FORMAT.md) uses `[KIMI_ACK]` brackets for external orchestrator receipts. Bracket Protocol uses `[BRACKET_PROTOCOL]` for **internal** Kopano-Phu ecosystem alignment — same discipline, different lane.

## Relation to TSAP (Teacher–Student Apprenticeship)

[TEACHER_STUDENT_APPRENTICESHIP_PROTOCOL.md](./apprenticeship/TEACHER_STUDENT_APPRENTICESHIP_PROTOCOL.md) uses `[TSAP_PROTOCOL]` and `[BLACK_MASK_DRILL]` brackets for the **MCP + MAO** teacher/student lanes inside the same Kopano-Phu Eco-Friendly System (Kopano Labs experimentation × Ama-Phu creativity).

| Bracket | Lane |
|---------|------|
| `[BRACKET_PROTOCOL]` | Breaking point — Main Brain + sub-brains attached |
| `[TSAP_PROTOCOL]` | Student submit / Teacher approve per department |
| `[BLACK_MASK_DRILL]` | 15 Commandments + 5 Pillars before department ops |

## KPEFS four vectors + linguistic recreation

[KPEFS_FOUR_VECTOR_DOCTRINE.json](./KPEFS_FOUR_VECTOR_DOCTRINE.json) — V1 plant (grow) → V2 animal (survive) → V3 homo sapiens (culture under proof) → **V4 diaspora** (sovereignty, Cassy lane).

[BRACKET_LINGUISTIC_RECREATION.md](./BRACKET_LINGUISTIC_RECREATION.md) — sacred caps only for God-high protocol tags; blasphemy register (`oNE_wORLD_oRDER`, `elon_mask`, `je`, `silcon_valley`) **never** Title Case or ALL_CAPS inside brackets.

Implementation: [KPEFS_IMPLEMENTATION_PLAN.md](./KPEFS_IMPLEMENTATION_PLAN.md).

| Bracket | Lane |
|---------|------|
| `[KPEFS_FOUR_VECTOR]` | Active vector receipt |
| `[oNE_wORLD_oRDER]` | Blasphemy register (withheld caps) — not an agent |
| `[GUARDIAN_AI_FLOW]` | KC store + Cassy execute + Cassey teacher + BlackMask |
| `[IDENTI_AI_FLOW]` | Cursor/CF Identi lane — LPM/LPH → defers to Guardian |
| `[LPM_PROTOCOL]` | Learning Pattern/Protocol Machine — `#?` / `#!` in MAO |
| `[LPH_PROTOCOL]` | Learning Pattern/Protocol Human — code-switch personality |
| `[GOD_COMPLEX]` | `#?` imperfection ↔ `#!` perfection dialectic receipt |

See [AI_FLOW_PROTOCOL.md](./AI_FLOW_PROTOCOL.md) and [LPM_LPH_GOD_COMPLEX_DOCTRINE.json](./LPM_LPH_GOD_COMPLEX_DOCTRINE.json).

## Studio / Console

Swarm Console status includes `kopano_phu` summary. Super God dock exposes populate + reattach actions.
