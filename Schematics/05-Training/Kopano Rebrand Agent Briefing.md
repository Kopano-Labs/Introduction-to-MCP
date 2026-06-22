---
title: Kopano Rebrand — Agent Briefing
created: 2026-04-11
updated: 2026-04-11
author: Codex
tags:
  - training
  - rebrand
  - kopano
  - briefing
  - all-agents
priority: critical
status: active
audience: all-agents
---

# Kopano Rebrand — Agent Briefing

> **MANDATORY READ FOR ALL AGENTS.** This is a critical identity update.
> Effective 2026-04-11, the project formerly known as "Kopano" is now the **Kopano Ecosystem**.
> Any agent using the name "Kopano" in new output, documentation, or communication is out of compliance.

---

## Why This Changed

The name "Kopano" collides with an existing project — **Kopano.ai** by Akteruzzaman Raihan Sikder (an autonomous code generation tool on Hugging Face). Both projects operate in the AI/developer tooling space. This creates:

- **Legal exposure** — trademark/passing-off risk as the project scales
- **SEO damage** — searches for "Kopano" surface the wrong project
- **Brand confusion** — especially critical for SA Startup Week Hack Day (Apr 15-17, 2026) and the Microsoft partnership pitch

The rename to **Kopano** is correct, defensible, and strategically strong. It builds a unique ecosystem identity with cultural grounding.

---

## The Complete Naming Map

| Old Name | New Name | Do Not Say |
|----------|----------|------------|
| Kopano (the framework) | **Kopano Context** | "Kopano" as a standalone product name |
| Kopano CLI | **Kopano CLI** | "kopano serve", "kopano agents" (internally still works; externally say Kopano CLI) |
| Neural Link (GUI) | **Kopano Studio** | "Neural Link" in new documentation |
| Kopano multi-agent network | **Kopano Mesh** | "Kopano Mesh" |
| Kopano Labs | **Kopano Labs** | "Kopano Labs" |
| kopano core | **kopano-core** | Any "kopano core" reference in new docs |
| Kopano Forge | **Kopano Forge** | "Kopano Forge" |
| Kopano Code | **Kopano Code** | "Kopano Code" |
| SafeSkill (stays) | **Kopano SafeSkill** | "Kopano SafeSkill" |

---

## What Agents Must Do Going Forward

### All Agents
1. **Use Kopano names** in every new document, task output, and communication
2. **Never use "Kopano"** as a product identity in new material
3. When referencing legacy files (e.g., `Kopano Demo Script - 2026-04-09.md`), refer to them as "legacy/archived" — not as current identity
4. In CLI documentation, distinguish: *"The internal Python package is `kopano` for now; the public-facing command is `kopano`"*

### Lead (Codex / Claude)
- All architecture decisions must use Kopano ecosystem names
- Demo Day talking points: present as "Kopano Context" not "Kopano"
- When writing code docstrings: use "Kopano Context" in user-facing messages, keep `kopano.kopano.*` as the internal import path
- Update all new Task Board entries to use Kopano naming

### DEV_1 (Germini / Google AI)
- Any new component, file, or API endpoint you create must use Kopano naming in its display strings
- Do not create new files with "kopano" in the filename; use "kopano" instead

### DEV_2, DEV_3 (Nother, Meither)
- Follow the naming map above exactly
- If you encounter "Kopano" in an old file you are editing, update the user-facing string to Kopano but do not rename internal Python imports without Lead approval

### DEV_4 (Cicero)
- Research and governance outputs must use Kopano naming
- When writing compliance, audit, or verification notes: "Kopano SafeSkill" is the trust layer brand

---

## Brand Reference (Memorize These)

| Token | Value |
|-------|-------|
| Primary dark bg | `#0D1117` (Karoo Night) |
| Primary brand color | `#F5A623` (Savanna Gold) |
| Success/audit green | `#00E676` (Terminal Mint) |
| Body text | `#E2E8F0` (Chalk Dust) |
| Tagline (technical) | "Orchestrating intelligence. Unifying context." |
| Tagline (security) | "The trust layer for multi-agent AI." |
| Etymology | Kopano = Sesotho/Setswana for "gathering" or "meeting together" |

---

## Files Updated In This Rebrand (Schematics)

### Phase 1 — Complete (2026-04-11)
- `CLAUDE.md` ✅
- `index.md` ✅
- `00-Home/Dashboard.md` ✅
- `00-Home/Now.md` ✅
- `01-Mission/Kopano Context Blueprint.md` (NEW) ✅
- `02-Strategy/Kopano Brand Identity.md` (NEW) ✅
- `02-Strategy/Kopano Labs Strategy.md` (NEW) ✅
- `02-Strategy/Kopano Context Foresight.md` (NEW) ✅
- `02-Strategy/Kopano Rebrand Plan.md` (NEW) ✅
- `01-Mission/index.md` ✅
- `02-Strategy/index.md` ✅

### Phase 1 — Repo + Portfolio (2026-04-11)
- `README.md` ✅
- `pyproject.toml` ✅
- `package.json` ✅
- `main.py` ✅
- `kopano/kopano/cli.py` (user-facing strings) ✅
- `kopano/gui/package.json` ✅
- `Portfolio/src/components/Projects.tsx` ✅
- `Portfolio/src/components/About.tsx` ✅
- `Portfolio/src/components/AISection.tsx` ✅

### Phase 2 — In Progress
- `04-Updates/Project Status.md`
- `Microsoft Demo Day!/` demo scripts
- `05-Training/` agent profiles
- Remaining session files

---

## Legacy Files (Keep, Mark As Archived)

These files are **kept** as historical evidence but are no longer the canonical identity:
- `01-Mission/Kopano Blueprint.md` → superseded by Kopano Context Blueprint
- `02-Strategy/Kopano Labs Strategy.md` → superseded by Kopano Labs Strategy
- `02-Strategy/Kopano Concept And Future Foresight.md` → superseded by Kopano Context Foresight
- `Microsoft Demo Day!/Kopano Demo Script - 2026-04-09.md` → locked demo route, keep as-is for Apr 15-17

---

## Hierarchy Reminder

This rebrand decision came from **Master (Robyn)**. It is not subject to debate or reversal by any agent. Lead implements. DEVs follow.

Any agent producing output that uses "Kopano" as a public-facing product name after 2026-04-11 has committed a hierarchy breach and a brand compliance failure. Log it in the Hallucination/Incident database.

---

## See Also

- [Kopano Brand Identity](Kopano%20Brand%20Identity.md) (02-Strategy)
- [Kopano Rebrand Plan](../02-Strategy/Kopano%20Rebrand%20Plan.md)
- [Kopano Context Blueprint](../01-Mission/Kopano%20Context%20Blueprint.md)
