---
title: Vault Hygiene and CRUD Discipline
created: 2026-04-09
updated: 2026-04-09
author: Codex
tags:
  - training
  - obsidian
  - organization
  - crud
priority: critical
status: active
---

# Vault Hygiene and CRUD Discipline

> Training rule for future Orch work: organization is not the same thing as moving files.
> A repo-backed Obsidian vault only stays useful when cleanup is done as full CRUD plus link maintenance.

## Failure Mode This Note Corrects

- superficial cleanup moves files without updating note homes
- root docs get relocated even though tests, README, or scripts still expect them
- Obsidian notes keep stale paths like `STRUCTURE/...` after the vault has already moved to `Schematics/...`
- assets move, but image links and dashboards do not
- the user asked for consolidation, while the agent only performed relocation

## Required CRUD Workflow

1. **Create**
   - add missing index notes, current-state notes, and home notes before moving files around
2. **Read**
   - inspect existing notes, backlinks, README links, tests, and scripts before changing file homes
3. **Update**
   - patch stale links, dashboards, status notes, image paths, and cross-note references
4. **Delete**
   - only remove or archive stale items once a replacement home and navigation path exists

## Obsidian-Safe Rules

- prefer stable note names over frequent renames
- when root docs are externally referenced, index them from Schematics instead of moving them
- use one canonical "open this first" note so the vault has a clear entry point
- when adding a new note cluster, also add an index note for that cluster
- fix stale path references immediately once the vault naming changes

## Verification Checklist

- does the note show up from the dashboard?
- does the current-state note point to it?
- do README or tests still resolve moved assets and docs?
- are there stale `STRUCTURE/...` or dead relative links left behind?
- can a human open one note and understand what is current?

## Codex-Specific Training Rule

Codex can solve the filesystem part of an organization request faster than the knowledge-architecture part.

That behavior is not good enough for this vault.

Future Codex passes must:

- assume "organize" means information architecture, not just directory hygiene
- preserve Obsidian usability first
- treat repo-root doc references as contracts
- produce a readable map, not only a cleaner tree
- treat repeated user prompts as a sign the earlier pass was too shallow or looked lazy from the user's side

## Commit Identity Memory Rule

- all repo commits must use `RobynAwesome <rkholofelo@gmail.com>`
- this is not optional metadata
- treat wrong author identity as a workflow failure that must be corrected before commit
