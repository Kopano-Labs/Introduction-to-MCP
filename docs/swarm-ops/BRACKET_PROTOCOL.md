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

## Studio / Console

Swarm Console status includes `kopano_phu` summary. Super God dock exposes populate + reattach actions.
