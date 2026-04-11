---
title: Kopano Rebrand Plan
created: 2026-04-11
updated: 2026-04-11
author: Codex
tags:
  - strategy
  - brand
  - kopano
  - rebrand
priority: critical
status: active
---

# Kopano Rebrand Plan

> Orch is being retired as the public-facing brand identity.
> The new ecosystem name is **Kopano** — derived from the Sesotho/Setswana word for "gathering" or "meeting together."
> This document is the canonical plan for migrating all Schematics references from "Orch" to the Kopano ecosystem naming.

---

## 1. Ecosystem Naming Map

| Old Name | New Name | Role |
|----------|----------|------|
| Orch (core framework) | **Kopano Context** | Core orchestration framework and repository |
| Orch CLI | **Kopano CLI** | Terminal command-line interface |
| Neural Link (GUI) | **Kopano Studio** | Next.js React GUI and agent visualization dashboard |
| Orch mesh / multi-agent network | **Kopano Mesh** | Multi-agent network (Gemini, Grok, others in parallel) |
| Orch Labs | **Kopano Labs** | Product studio — experiment gallery and SA impact tools |
| Orch Core (engine) | **kopano-core** | Internal orchestration engine (lowercase, repo-style) |
| Orch Forge | **Kopano Forge** | Collaborative execution + canvas workflow tool |
| Orch Code | **Kopano Code** | Coding acceleration and craft learning tool |

---

## 2. Brand Identity

### Color Palette
| Name | Hex | Usage |
|------|-----|-------|
| Karoo Night | `#0D1117` | Primary dark background |
| Savanna Gold | `#F5A623` | Primary brand color — buttons, CLI highlights, accents |
| Terminal Mint | `#00E676` | Success accent — audit pass, SafeSkill verified, test pass |
| Chalk Dust | `#E2E8F0` | Body text and documentation base |

### Typography
- **Headings & Brand Mark:** Space Grotesk or Fira Code
- **Body & Docs:** Inter or Geist

### Taglines
- **Technical:** "Orchestrating intelligence. Unifying context."
- **Security/Audit:** "The trust layer for multi-agent AI."
- **Action (short):** "Connect the context. Let the agents build."

### Logo Concepts (for Figma)
- **Concept A — Indaba Nodes:** Three glowing dots (LLMs) connected by clean lines to a central circle (Moderator AI). Aerial indaba circle.
- **Concept B — Secure Weave:** Two overlapping `{ }` brackets woven like a basket. Highlights data context and cultural root.
- **Concept C — Terminal Shield:** A stylized `>_` terminal prompt inside a shield outline. Audit-first, trust-layer focus.

### Brand Voice
- Tone: Highly technical, direct, unpretentious. No Silicon Valley hype.
- Philosophy: "Audit twice." Transparent about what is happening under the hood.

---

## 3. Domain Strategy

| Domain | Priority | Use |
|--------|----------|-----|
| `kopano.dev` | Gold standard | Core developer tooling and open-source framework |
| `kopanocontext.ai` | Strong runner-up | Highlights AI/LLM nature of the framework |
| `kopanolabs.co.za` | Studio umbrella | Docs at `context.kopanolabs.co.za` |

---

## 4. Files to Update in Schematics

### Phase 1 — Critical (this session)
| File | Action |
|------|--------|
| `CLAUDE.md` | Update vault purpose, folder map, key file references |
| `index.md` | Update root description and all "Orch" references |
| `00-Home/Dashboard.md` | Update all "Orch" → Kopano ecosystem names |
| `00-Home/Now.md` | Update current state snapshot naming |
| `01-Mission/Orch Blueprint.md` | Rewrite as Kopano Context Blueprint |
| `02-Strategy/Orch Labs Strategy.md` | Rewrite as Kopano Labs Strategy |
| `02-Strategy/Orch Concept And Future Foresight.md` | Update naming throughout |
| `02-Strategy/Kopano Brand Identity.md` | **NEW** — canonical brand identity document |

### Phase 2 — High Priority (follow-up session)
| File | Action |
|------|--------|
| `04-Updates/Project Status.md` | Update naming in status tables |
| `Microsoft Demo Day!/` files | Update demo scripts for new brand |
| `05-Training/` profile files | Update Orch references in agent profiles |
| `09-ORCH PROGRESSION/` index | Update folder references |

### Phase 3 — Backlog (systematic sweep)
- All remaining files in 04-Updates, 07-Sessions By Day, 10-SESSION IMPROVEMENTS
- Folder renames: `09-ORCH PROGRESSION` → `09-KOPANO PROGRESSION`
- README in `/06-Reference/orch-code-implemtation`

---

## 5. What Does NOT Change

- **Operating model:** Lead (Codex), DEV roster, hierarchy, session protocol, hallucination system — all unchanged
- **KasiLink integration:** Kopano Context remains the AI microservice layer inside KasiLink
- **SafeSkill:** Trust layer terminology stays — now branded as Kopano SafeSkill
- **Microsoft Demo Day target:** April 15-17, 2026 — unchanged
- **GitHub identity:** `RobynAwesome` — unchanged
- **Commit identity:** `RobynAwesome <rkholofelo@gmail.com>` — unchanged

---

## 6. Execution Sequence (This Session)

1. [x] Audit Schematics — complete
2. [x] Draw up this plan and save to `02-Strategy/`
3. [x] Create `02-Strategy/Kopano Brand Identity.md` (full brand pack)
4. [x] Update `CLAUDE.md`
5. [x] Update `index.md`
6. [x] Create `01-Mission/Kopano Context Blueprint.md` (new canonical; legacy kept as archive)
7. [x] Create `02-Strategy/Kopano Labs Strategy.md` (new canonical; legacy kept as archive)
8. [x] Create `02-Strategy/Kopano Context Foresight.md` (replaces Orch Concept And Future Foresight)
9. [x] Update `00-Home/Dashboard.md`
10. [x] Update `00-Home/Now.md`
11. [x] Update `02-Strategy/index.md`
12. [x] Update `01-Mission/index.md`
