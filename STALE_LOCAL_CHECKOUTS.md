# STALE LOCAL CHECKOUTS

> **Authority:** AntiGravity (Seat 10 / CF)  
> **Generated:** 2026-08-29T03:55:00+02:00 (SAST)  
> **Rule:** Classification only — **no archive, delete, merge, or reset performed.**

---

## Definition

**STALE** = last meaningful activity before July 2026 **or** behind remote default by ≥1 commit **or** superseded by a Generation III replacement **or** diverged fork with no unique receipted work.

---

## Stale / legacy table

| Path | Remote | Branch | Local HEAD | Behind | Last commit | Classification | Still active? | Newer remote canon? |
|------|--------|--------|------------|--------|-------------|----------------|---------------|---------------------|
| `C:\Users\rkhol\5s-Arena-Blog` | Kopano-Labs/5s-Arena-Blog | main | `3b20a1fcd2670b8d8c72d59e653adba344aa9e6c` | 40 | 2026-06-25 | LEGACY_CANDIDATE | Maybe (blog) | Bookit-5s-Arena RobynAwesome |
| `C:\Users\rkhol\cape-campass` | Kopano-Labs/cape-campass | master | `a0b9090210810466ac1672fe85da32c25285b376` | 0 | 2026-06-25 | LEGACY_CANDIDATE | Unknown | No Aug activity |
| `C:\Users\rkhol\CrisisConnect` | Kopano-Labs/CrisisConnect | master | `1fa18d4f337b629a4b9d99e582ed09b84753e375` | 1 | 2026-06-22 | **SUPERSEDED** | No | `crisis-connect` RobynAwesome |
| `C:\Users\rkhol\KopanoContext` | Kopano-Labs/kopano-context | master | `983af126c978a1339df6cb28757a08d149550b4d` | 0 | 2026-06-15 | LEGACY_CANDIDATE | No | Introduction-to-MCP |
| `C:\Users\rkhol\Portfolio` | Kopano-Labs/Portfolio | main | `927525d65e012b88ff57fd156de7077cca3d12d3` | 0 | 2026-06-25 | LEGACY_CANDIDATE | Maybe | Kopano-Labs-Website |
| `C:\Users\rkhol\Portfolio-client-MBR` | Kopano-Labs/Portfolio-MBR | main | `ca48a95cd97b2007de18746d2868c88ce907e0b4` | 0 | 2026-06-25 | LEGACY_CANDIDATE | Maybe | Kopano-Labs-Website |
| `C:\Users\rkhol\starfall-salvage` | Kopano-Labs/starfall-salvage | main | `771520e20ca434d3d95af5776359a7b4dc9b6f1b` | 8 | 2026-06-22 | STALE | Witnessed only | Remote `1cdfb302` |
| `C:\Users\rkhol\starfall-salvage-temp` | Kopano-Labs/starfall-salvage | main | `09e6f7598e05711e6c1e63fad22fe68104c301ed` | 9 | 2026-05-21 | **DUPLICATE** | No | Delete candidate after Master review |
| `C:\Users\rkhol\Starfall Salvage` | Kopano-Labs/starfall-salvage | codex/starfall-mobile-weapon-ecosystem | `70ea7dd7cb9532100809c9c15180e39f0173eb47` | 0 | 2026-06-15 | STALE branch | No | main |
| `C:\Users\rkhol\freddy-nw-alfalfa` | RobynAwesome/freddy-nw-alfalfa | master | `3616a5119770d34bd6f0c000061e1c5af9133baf` | no upstream | 2026-06-25 | LEGACY_CANDIDATE | Sub-brain in GSMB | Verify remote exists |
| `C:\Users\rkhol\Top-AI-repos` | RobynAwesome/Top-AI-repos | feature/fix-readme-metadata-may2026 | `bbb8901dccb8323d979edb676fde660ac1f415d0` | 0 | 2026-06-05 | LEGACY_CANDIDATE | Reference only | N/A |
| `C:\Users\rkhol\kasi-link-clean` | RobynAwesome/KasiLink | main | `06a5733eaf6223e4856b0ac66d838fc175b2bc1e` | 124 behind / 134 ahead | 2026-04-06 | **DIVERGED FORK** | **No** | `kasi-link` @ `1080fb18` |

---

## Dirty worktrees (not necessarily stale — inspect before action)

| Path | Dirty | Notes |
|------|-------|-------|
| `CrisisConnect` | yes | superseded — check for unique files before archive |
| `freddy-nw-alfalfa` | yes | farm sub-brain — may have local-only ops notes |
| `kasi-link-clean` | yes | **dangerous** — do not merge |
| `KopanoContext` | yes | June altar gate experiments |
| `Project-Jennifer` | yes | active project — pull/review |
| `Starfall Salvage` | yes | stale branch |
| `starfall-salvage` | yes | behind remote |
| OneDrive `Introduction to MCP` | yes | RTCP uncommitted — **active work** |

---

## Recommended disposition (Master approval required)

1. **Keep as-is (active):** All Aug 2026 ALIGNED checkouts in `C:\Users\rkhol\` root list.
2. **Repoint, don't delete:** `Bookit-5s-Arena` → RobynAwesome remote.
3. **Quarantine:** `kasi-link-clean` — rename folder to `_ARCHIVE_kasi-link-clean_DO_NOT_USE` after Master confirms no unique commits needed.
4. **Consolidate Starfall:** single checkout at `starfall-salvage`, pull to `1cdfb302`, remove `-temp` and spaced folder after diff review.
5. **Mark superseded:** `CrisisConnect` → pointer to `crisis-connect` in GSMB only.
