# UNRESOLVED CONFLICTS

> **Authority:** AntiGravity (Seat 10 / CF)  
> **Generated:** 2026-08-29T03:55:00+02:00 (SAST)  
> **RTC required:** Only items marked `RTC_CANDIDATE` — others are CF-resolvable with Master approval.

---

## Conflict 1 — Bookit-5s-Arena dual canonical remotes

| Field | Kopano-Labs | RobynAwesome |
|-------|-------------|--------------|
| repo | Kopano-Labs/Bookit-5s-Arena | RobynAwesome/Bookit-5s-Arena |
| branch | main | main |
| HEAD | `a014a98f53e91b99de061c48f962350a006cf154` | `91b8a7e0d22195bec31d810f6a12eb42624e7893` |
| local checkout | `C:\Users\rkhol\Bookit-5s-Arena` tracks **Kopano-Labs** | not checked out |

**Nature:** Two orgs diverged after June. RobynAwesome received truth-pulse remediation (PR #11). Local metal is on stale Kopano-Labs fork.

**Archive branch note:** User cited `codex/archive-world-cup-stale-state` @ `1fb48e9`. Cloud now shows RobynAwesome archive @ `b1cdfaf7` — GSMB pointer was stale.

**Classification:** `RECONCILIATION_REQUIRED`  
**RTC_CANDIDATE:** No — unless Master wants Kopano-Labs org to remain canonical for production deploy.

**Admissible actions (pick one):**
1. Repoint local `origin` to RobynAwesome and `git pull` (CF can execute).
2. Merge RobynAwesome → Kopano-Labs org (requires org admin).
3. Declare RobynAwesome canonical in pointers only; keep Kopano-Labs as read-only mirror.

---

## Conflict 2 — kasi-link-clean diverged fork

| Field | Value |
|-------|-------|
| path | `C:\Users\rkhol\kasi-link-clean` |
| remote | RobynAwesome/KasiLink |
| branch | main |
| HEAD | `06a5733eaf6223e4856b0ac66d838fc175b2bc1e` |
| ahead / behind | **134 / 124** |
| worktree | dirty |
| canonical aligned checkout | `C:\Users\rkhol\kasi-link` @ `1080fb18` (Kopano-Labs remote, same SHA as RobynAwesome) |

**Nature:** April 2026 fork exploded in both directions. High risk of silent data loss if merged blindly.

**Classification:** `RECONCILIATION_REQUIRED`  
**RTC_CANDIDATE:** Yes — if any economic/gig data exists only in `kasi-link-clean`.

**Admissible actions:**
1. Quarantine folder (rename, no git ops) — **recommended default**.
2. Forensic `git log` diff for unique commits (CF can run, read-only).
3. Do **not** merge without Master + ledger receipt.

---

## Conflict 3 — Introduction-to-MCP remote URL vs canonical declaration

| Field | Value |
|-------|-------|
| GSMB pointer says | `RobynAwesome/Introduction-to-MCP` canonical |
| Local `origin` URL | `https://github.com/Kopano-Labs/Introduction-to-MCP.git` |
| HEAD both orgs | `7973d64b74a1e037a234f1ac45381c8f1ef5f730` (ALIGNED today) |

**Nature:** Cosmetic / organizational — not a code conflict yet. Risk if orgs diverge later.

**Classification:** `RECONCILIATION_REQUIRED` (low severity)  
**Admissible action:** Repoint `origin` to RobynAwesome OR add `robyn` remote alongside `origin`.

---

## Conflict 4 — Uncommitted RTCP pipeline on local GSMB

| Field | Value |
|-------|-------|
| path | OneDrive `Introduction to MCP` |
| committed HEAD | `7973d64b` (aligned with cloud) |
| uncommitted | `rtcp_pipeline.py`, tests, bridge, `NOW.md`, seed script |

**Nature:** Local metal is **ahead** of cloud with governance code Forge/Daddy ratified in session.

**Classification:** `RECONCILIATION_REQUIRED`  
**RTC_CANDIDATE:** No.

**Admissible action:** Master approves commit + push to `RobynAwesome/Introduction-to-MCP` master.

---

## Conflict 5 — Starfall Salvage triple checkout

| Path | HEAD | Behind main |
|------|------|-------------|
| `starfall-salvage` | `771520e` | 8 |
| `starfall-salvage-temp` | `09e6f75` | 9 |
| `Starfall Salvage` | `70ea7dd` (feature branch) | unknown |

**Cloud main:** `1cdfb3024f71fcec8a2c4ff69f539858dd34db8f`

**Nature:** Fragmentation of Concept — three local fragments, one remote.

**Classification:** `LEGACY_CANDIDATE` + `RECONCILIATION_REQUIRED`  
**Admissible action:** Consolidate to one folder after `git diff` review; no delete without Master.

---

## Conflict 6 — gh CLI authentication invalid

| Field | Value |
|-------|-------|
| symptom | `gh auth status` → token invalid (401) |
| impact | Open PRs, private repo API, Actions status — PARTIALLY_KNOWABLE |

**Admissible action:** Master runs `gh auth login -h github.com` on this machine.

---

## Conflict 7 — KasiLink production HOLD (from NOW.md — preserved)

**Not a git conflict** — runtime/auth evidence gap. Apex/`www` split and authentication failures remain HOLD per issue #102 follow-up. Do not mark production until receipted.

---

## RTC escalation threshold

Invoke Round Table Council **only if:**
- Master chooses Kopano-Labs over RobynAwesome as deploy canonical for FivesArena **and** production is live on fivesarena.com
- Unique economic data found in `kasi-link-clean` that contradicts `kasi-link`
- Physical Cars4Mars evidence contradicts software repo state

**Otherwise:** CF executes reconciliation under Master's one-line approval per conflict.
