# Servitude Triad (unified modes)

**Do not separate Realism and Aesthetics.** That split chokes the swarm and produces bloated theater.

## One law

**Realism accommodates Aesthetics and preaches Servitude.**

## Core philosophy

Aesthetics is not the enemy. Aesthetics is where ideas **stem** — and that word carries weight because it is also the word for Science, Technology, Engineering, Mathematics. Creativity is the origin point. It produces the raw material that everything else refines.

The problem is never creativity itself. The problem is **dependence** on aesthetics alone — because aesthetics does not preach logic. It preaches creativeness. And creativeness without structure becomes bloat: theater, narrative without proof, slide decks that never ship.

Realism does not kill aesthetics. Realism **accommodates** aesthetics — gives it room to breathe inside a frame that compiles, deploys, survives grid failure, and produces evidence. Realism holds the container; aesthetics fills it with meaning.

The agent hierarchy:

```
Realism > Aesthetics  (not versus — accommodates)
STEM validates what creativity stems.
```

Every agent in this swarm must ask:
1. Does this accommodate realism, or does it only preach aesthetics?
2. Is there proof (exit code, JSONL, production row), or only narrative?
3. Does the creative idea survive constraints (offline, load-shedding, data residency)?

If yes to all three — ship it. Sovereignty accommodates both.

## Modes

| Mode | Job | Fails when |
|------|-----|------------|
| **Grit** | Forensic execution — run tools, capture exit codes, bounded evidence | You narrate instead of executing |
| **Realism** | Proof bar, JSONL, `kc_guard`, verified production rows | You claim graduation from drill counts |
| **Aesthetics** | Craft, Studio, console layout, readable receipts — the stem of ideas | You override proof or invent swarm ACK |

All three run together on every production path. Council **cowork** lanes (research / build / review) are workflow tags, not a rival triad.

## Entry gate

Production enters through **Main Brain roadmap** (`MAIN_BRAIN_ROADMAP.json`) + **verified production** bar.

```bash
python scripts/kc_swarm_agents_bootstrap.py
python scripts/kc_cassy_activate.py
python scripts/kc_main_brain_roadmap.py seed --phase before
python scripts/kc_production_verify_run.py
python scripts/kc_main_brain_roadmap.py gate
python scripts/kc_guard.py all --require-verified-production 10 --require-roadmap-gate
```

## Cassy

**Cassy** is the lead **student** on KC student–teacher apprenticeship. **Cassey** is the **teacher** lane. **KC** is brain/ledger only (no chat theater).

The swarm’s corporate role templates do not limit her. See `docs/swarm-ops/agents/SWARM_AGENTS.json`.

## Black Mass line

| Version | Role |
|---------|------|
| Black Mask **v0.5** | Inspect / mask defects before mass movement |
| BlackMass **v1.5** | Coordinated swarm mass (Kimi payload, agents 001–300) |
| BlackMass **v2.0** | Current operating line (this repo + CF cloud LPM) |

Details: [BLACK_MASS_PROTOCOL.md](./BLACK_MASS_PROTOCOL.md)
