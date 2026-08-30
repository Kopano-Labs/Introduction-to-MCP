# CURRENT CLOUD ESTATE

> **Authority:** AntiGravity (Seat 10 / CF)  
> **Generated:** 2026-08-29T03:55:00+02:00 (SAST)  
> **Source order:** Forge continuity (assumed) → GitHub public API → local verification  
> **Constraint:** `gh` CLI token **invalid** (401). Open PR lists are **PARTIALLY_KNOWABLE** until re-auth.

---

## Estate summary

| Metric | Value |
|--------|------:|
| RobynAwesome repos surveyed | 13 public + 4 private (404 without auth) |
| Kopano-Labs org repos (public) | 10 |
| Generation III active (Aug 2026) | 12+ nodes |
| Canonical GSMB cloud remote | `RobynAwesome/Introduction-to-MCP` **and** `Kopano-Labs/Introduction-to-MCP` (same HEAD) |

---

## Active project registry (cloud)

### Constitutional / governance

| Project | Repository | Owner | Default branch | HEAD | Last push (UTC) | Lane | Continuity note |
|---------|------------|-------|----------------|------|-----------------|------|-----------------|
| Introduction-to-MCP | Introduction-to-MCP | RobynAwesome | master | `7973d64b74a1e037a234f1ac45381c8f1ef5f730` | 2026-08-28 23:20 | `KPGS_GOVERNANCE` | MMAO failure ledger + Forge case 001; mirrors Kopano-Labs at same SHA |
| Introduction-to-MCP | Introduction-to-MCP | Kopano-Labs | master | `7973d64b74a1e037a234f1ac45381c8f1ef5f730` | — | `KPGS_GOVERNANCE` | Local OneDrive checkout tracks this remote URL |

**Recent commits (RobynAwesome/Introduction-to-MCP):**
- `7973d64b` — ledger: add MMAO session failures and Forge case 001
- `6f967590` — Merge PR #111 forge/kc-gui-truth
- `974f263d` — docs(gui): retire stale sovereign GUI branch pointer

**Open PRs:** UNKNOWN — `gh auth` failed. Re-run `gh pr list -R RobynAwesome/Introduction-to-MCP` after login.

---

### Generation III runtimes

| Project | Repository | Owner | Branch | HEAD | Last push | Lane | Purpose |
|---------|------------|-------|--------|------|-----------|------|---------|
| KMEC | kpgs-morning-engine-core--kmec- | RobynAwesome | main | **PRIVATE** local `ce7017060f1dd530992d413374e11c0742dbf6a7` | 2026-08-28 | `KPGS_RUNTIME` | Local-first morning engine, SQLite receipts, KPCB+ |
| PKA | Partial-Knowable-Algebra | RobynAwesome | main | **PRIVATE** local `0abc68810ee5799f4bb703f8bb99fb2bf11b3e86` | 2026-08-28 | `KPGS_GOVERNANCE` | D/F/G/R observational evidence executable |
| Ayakha AI | ayakha-ai | RobynAwesome | main | `a20e6d5c93b8b9ae464515059b37ce988752659b` | 2026-08-26 | `AYA_RINGFENCED` | Voice-first desktop CAD; **not hackathon** |
| AMAPHU App | amaphu-app | RobynAwesome | main | `e15963833fd3722deebd30829528521309934d7b` | 2026-08-22 | `AMAPHU_ENTERTAINMENT` | Entertainment shell + Jennifer integration |
| Project Jennifer | Project-Jennifer | RobynAwesome | main | `5d4dd2a6af04345e3a30a90f51de3d809c52cae1` | 2026-08-24 | `PERSONAL_RELATIONAL` | PERN relationship engine; UJ IKM playground |
| Kopano Sovereign Hub | kopano-sovereign-hub | RobynAwesome | main | `9a521a88a6203194b38d2d8fb55ccbe4da66fecc` | 2026-08-28 | `KOPANO_LABS_HUB` | Alpaca receipts, arbitrage kernel |
| Kopano Labs Website | Kopano-Labs-Website | RobynAwesome | main | `bc835af53e60474ea12c734335e1608bca64bfa6` | 2026-08-28 | `KOPANO_LABS_HUB` | Public site; SEA production launch receipt |
| Search Entity Architecture | Search-Entity-Architecture | RobynAwesome | main | **PRIVATE** local `f67b57184b97617ef5e711cfbb6c7e73dc2ea4c4` | 2026-08-28 | `KOPANO_LABS_HUB` | Entity/indexing; merged into website launch |
| Kopano-Labs-Interns | Kopano-Labs-Interns | RobynAwesome | main | `5773f7e3e2841c27fcd433ff23ceb78da91bf05a` | 2026-08-26 | `KPGS_GOVERNANCE` | Stateless-renter apprenticeship infra |

---

### Products / missions

| Project | Repository | Owner | Branch | HEAD | Lane | Deployment (known) |
|---------|------------|-------|--------|------|------|-------------------|
| Cars4Mars (software) | cars4mars-project | RobynAwesome | main | `74fa057fed4a5a68ab9a0b9370b5f01b2be954a8` | `CARS4MARS_ROVER` | Repo only; hardware SANSA 2026-09-19 |
| Cars4Mars (landing) | cars4mars-landingpage | RobynAwesome | main | **PRIVATE** local `4169630b6862246e40474441d9aaf5f1e716bc94` | `CARS4MARS_ROVER` | UNKNOWN |
| FivesArena / Bookit | Bookit-5s-Arena | RobynAwesome | main | `91b8a7e0d22195bec31d810f6a12eb42624e7893` | `FIVES_ARENA_SPORTS` | fivesarena.com (verify live) |
| FivesArena archive branch | Bookit-5s-Arena | RobynAwesome | codex/archive-world-cup-stale-state | `b1cdfaf7c6181456e9fbb5d6c6bd8f11dc9d4f78` | `FIVES_ARENA_SPORTS` | Remediation; do not merge without revalidation |
| KasiLink | KasiLink | RobynAwesome | main | `1080fb18096cb2b5c9f8a9ea0d12b442b80329f4` | `KOPANO_LABS_HUB` | Vercel (auth issues HOLD per NOW) |
| CrisisConnect (Gen III) | crisis-connect | RobynAwesome | main | `97de0b60273be8a8440193623499e0054d06c0af` | `CRISIS_CONNECT_PWA` | KPGS vNext APU path |
| Paws and Potjie | paws-and-potjie | RobynAwesome | main | `e0d6944b22c909af1f24b77c8f22648860ffdc30` | `KOPANO_LABS_HUB` | PWA / 3D |
| Starfall Salvage | starfall-salvage | Kopano-Labs | main | `1cdfb3024f71fcec8a2c4ff69f539858dd34db8f` | `AMAPHU_ENTERTAINMENT` | Witnessed not production (NOW) |
| Classroom50 | classroom50 | RobynAwesome | main | `1ca4604c20d8e7433ef33d0148fdf3ecb5012edc` | `KPGS_GOVERNANCE` | Fork; stale since 2026-06-18 |

---

## Kopano-Labs org (public, secondary remotes)

| Repository | Branch | HEAD / note |
|------------|--------|-------------|
| Bookit-5s-Arena | main | `a014a98f53e91b99de061c48f962350a006cf154` — **DIVERGED** from RobynAwesome/main |
| classroom50 | main | Same SHA as RobynAwesome fork |
| azure-skills | main | 2026-08-25 activity |
| flow-inc-ink-demo | main | 2026-08-05 |
| teacher-toolbox | main | 2026-06-17 |

---

## Repos not found (public API)

| Expected name | Status |
|---------------|--------|
| kpgs-morning-engine-core--kmec- | **PRIVATE** — local clone verified |
| Partial-Knowable-Algebra | **PRIVATE** — local clone verified |
| Search-Entity-Architecture | **PRIVATE** — local clone verified |
| cars4mars-landingpage | **PRIVATE** — local clone verified |

---

## Forge / Daddy continuity assumptions (not re-derived)

Forge owns cloud continuity from Personal Intelligence. This document **verifies** cloud HEADs; it does not re-litigate Forge session history.

**August 2026 active lanes confirmed in cloud:**
- RTCP pipeline + DIRISA cornerstone in Introduction-to-MCP / Schematics
- KMEC + PKA private repos with Aug 28 commits
- Sovereign Hub + Website + SEA launch wave (Aug 28)
- Bookit truth-pulse remediation on RobynAwesome (ahead of Kopano-Labs fork)
- Jennifer consequence journal POC merged (#77)

---

## Evidence limits

| Claim type | Domain | Limit |
|------------|--------|-------|
| Git HEAD | GitHub REST (unauthenticated) | Public repos only; rate-limited |
| Private repo HEAD | Local `git rev-parse` | Requires local clone |
| Open PRs / CI | GitHub API | **BLOCKED** — renew `gh auth login` |
| Live deployment | E_W runtime | Not probed this pass — mark UNKNOWN |
