# LOCAL VS CLOUD RECONCILIATION

> **Authority:** AntiGravity (Seat 10 / CF)  
> **Generated:** 2026-08-29T03:55:00+02:00 (SAST)  
> **Method:** `tools/_estate_git_audit.py` + GitHub public API cross-check

---

## Executive summary

| Classification | Count |
|----------------|------:|
| ALIGNED | 18 |
| RECONCILIATION_REQUIRED | 4 |
| LEGACY_CANDIDATE | 9 |
| CLOUD_ONLY / NOT_CLONED_LOCALLY | 1 |
| PARTIALLY_KNOWABLE | 3 (gh auth, deployments, open PRs) |

**Canonical GSMB checkout:** `C:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP`  
**Cloud HEAD (both orgs):** `7973d64b74a1e037a234f1ac45381c8f1ef5f730` on `master`  
**Local committed state:** ALIGNED with cloud  
**Local worktree:** **dirty** (12 paths — see below)

---

## GSMB local ↔ cloud (Introduction-to-MCP)

| Field | Local (OneDrive) | Cloud RobynAwesome | Cloud Kopano-Labs |
|-------|------------------|--------------------|-------------------|
| path | `...\Introduction to MCP` | — | — |
| remote URL | `Kopano-Labs/Introduction-to-MCP` | same repo mirror | tracked remote |
| branch | master | master | master |
| HEAD | `7973d64b74a1e037a234f1ac45381c8f1ef5f730` | `7973d64b...` | `7973d64b...` |
| ahead/behind origin | 0 / 0 | — | — |
| worktree | **dirty** | — | — |

### Uncommitted local-only work (not on cloud yet)

| Path | Type | Action |
|------|------|--------|
| `NOW.md` | modified | continuity update |
| `Schematics/.obsidian/workspace.json` | modified | ignore for governance |
| `Schematics/.smart-env/...` | modified | ignore (plugin cache) |
| `Schematics/04-Updates/comms-log.md` | modified | review before commit |
| `kopano-core/kopano/rtcp_pipeline.py` | untracked | **RTCP canon — needs commit** |
| `kopano-core/kopano/pka_kmec_jennifer_bridge.py` | untracked | bridge — needs commit |
| `tests/test_rtcp_pipeline.py` | untracked | 8 tests pass |
| `tests/test_pka_kmec_jennifer_bridge.py` | untracked | needs run |
| `scripts/seed_external_repos_to_gsmb.py` | untracked | seeding tooling |
| `tools/_estate_git_audit.py` | untracked | CF audit tooling |

**Verdict:** Committed GSMB **ALIGNED**. Local metal is **ahead** with RTCP + estate tooling — push decision rests with Master.

---

## Per-checkout reconciliation

### ALIGNED (local HEAD = remote default HEAD)

| Local path | Remote | Branch | HEAD | Worktree |
|------------|--------|--------|------|----------|
| `C:\Users\rkhol\amaphu-app` | RobynAwesome/amaphu-app | main | `e1596383...` | clean |
| `C:\Users\rkhol\ayakha-ai` | RobynAwesome/ayakha-ai | main | `a20e6d5c...` | clean |
| `C:\Users\rkhol\cars4mars-project` | RobynAwesome/cars4mars-project | main | `74fa057f...` | clean |
| `C:\Users\rkhol\cars4mars-landingpage` | RobynAwesome/cars4mars-landingpage | main | `4169630b...` | clean |
| `C:\Users\rkhol\crisis-connect` | RobynAwesome/crisis-connect | main | `97de0b60...` | clean |
| `C:\Users\rkhol\Kopano-Labs-Interns` | RobynAwesome/Kopano-Labs-Interns | main | `5773f7e3...` | clean |
| `C:\Users\rkhol\Kopano-Labs-Website` | RobynAwesome/Kopano-Labs-Website | main | `bc835af5...` | clean |
| `C:\Users\rkhol\kopano-sovereign-hub` | RobynAwesome/kopano-sovereign-hub | main | `9a521a88...` | clean |
| `C:\Users\rkhol\kpgs-morning-engine-core--kmec-` | RobynAwesome/kpgs-morning-engine-core--kmec- | main | `ce701706...` | clean |
| `C:\Users\rkhol\Partial-Knowable-Algebra` | RobynAwesome/Partial-Knowable-Algebra | main | `0abc6881...` | clean |
| `C:\Users\rkhol\paws-and-potjie` | RobynAwesome/paws-and-potjie | main | `e0d6944b...` | clean |
| `C:\Users\rkhol\Search-Entity-Architecture` | RobynAwesome/Search-Entity-Architecture | main | `f67b5718...` | clean |
| `C:\Users\rkhol\kasi-link` | Kopano-Labs/KasiLink | main | `1080fb18...` | clean |
| `C:\Users\rkhol\Project-Jennifer` | RobynAwesome/Project-Jennifer | main | `5d4dd2a6...` | dirty |

---

### RECONCILIATION_REQUIRED

| Local path | Issue | Cloud truth | Recommendation |
|------------|-------|-------------|----------------|
| `C:\Users\rkhol\Bookit-5s-Arena` | Remote Kopano-Labs `a014a98` ≠ RobynAwesome `91b8a7e0` | RobynAwesome/main is ahead (truth-pulse PR #11) | Repoint origin to RobynAwesome OR pull RobynAwesome into Kopano-Labs — **Master decision** |
| `C:\Users\rkhol\kasi-link-clean` | ahead **134** / behind **124** | RobynAwesome/KasiLink `1080fb18` | **Do not merge.** Archive candidate; use `kasi-link` |
| OneDrive ITMCP remote URL | tracks Kopano-Labs not RobynAwesome | Same SHA today | Cosmetic; pointer registry says RobynAwesome canonical |
| GSMB pointer registry | stale SHAs (e.g. ITMCP `f512a38b`, FivesArena `1fb48e9`) | See `GSMB_POINTER_UPDATES.md` | Update pointers, not code |

---

### LEGACY_CANDIDATE

| Local path | Remote | Last activity | Notes |
|------------|--------|---------------|-------|
| `C:\Users\rkhol\5s-Arena-Blog` | Kopano-Labs/5s-Arena-Blog | 2026-06-25 | behind 40 |
| `C:\Users\rkhol\cape-campass` | Kopano-Labs/cape-campass | 2026-06-25 | aligned but stale |
| `C:\Users\rkhol\CrisisConnect` | Kopano-Labs/CrisisConnect | 2026-06-22 | **superseded** by `crisis-connect` |
| `C:\Users\rkhol\KopanoContext` | Kopano-Labs/kopano-context | 2026-06-15 | dirty; pre-GSMB |
| `C:\Users\rkhol\Portfolio` | Kopano-Labs/Portfolio | 2026-06-25 | stale |
| `C:\Users\rkhol\Portfolio-client-MBR` | Kopano-Labs/Portfolio-MBR | 2026-06-25 | stale |
| `C:\Users\rkhol\starfall-salvage` | Kopano-Labs/starfall-salvage | 2026-06-22 | behind 8, dirty |
| `C:\Users\rkhol\starfall-salvage-temp` | Kopano-Labs/starfall-salvage | 2026-05-21 | behind 9 |
| `C:\Users\rkhol\Starfall Salvage` | Kopano-Labs/starfall-salvage | 2026-06-15 | feature branch, dirty |
| `C:\Users\rkhol\freddy-nw-alfalfa` | RobynAwesome/freddy-nw-alfalfa | 2026-06-25 | no upstream, dirty |
| `C:\Users\rkhol\Top-AI-repos` | RobynAwesome/Top-AI-repos | 2026-06-05 | feature branch, dirty |

---

### CLOUD_ONLY (not cloned locally)

| Repository | Cloud HEAD | Lane |
|------------|------------|------|
| RobynAwesome/classroom50 | `1ca4604c20d8e7433ef33d0148fdf3ecb5012edc` | Classroom / teaching |

---

## August 2026 lane reconciliation status

| Lane | Cloud | Local | Status |
|------|-------|-------|--------|
| Introduction-to-MCP / GSMB | `7973d64b` | OneDrive aligned + dirty RTCP | ALIGNED + local ahead |
| KMEC | private | `C:\Users\rkhol\kpgs-morning-engine-core--kmec-` | ALIGNED |
| Aya | `a20e6d5c` | `C:\Users\rkhol\ayakha-ai` | ALIGNED |
| AMAPHU | `e1596383` | `C:\Users\rkhol\amaphu-app` | ALIGNED |
| Jennifer | `5d4dd2a6` | `C:\Users\rkhol\Project-Jennifer` | ALIGNED (dirty) |
| Sovereign Hub | `9a521a88` | `C:\Users\rkhol\kopano-sovereign-hub` | ALIGNED |
| Website / SEA | `bc835af5` / `f67b5718` | both cloned | ALIGNED |
| Interns | `5773f7e3` | `C:\Users\rkhol\Kopano-Labs-Interns` | ALIGNED |
| Cars4Mars | `74fa057f` + landing | both cloned | ALIGNED (institutional docs in Schematics) |
| FivesArena | RobynAwesome `91b8a7e0` | Kopano-Labs `a014a98` | **RECONCILIATION_REQUIRED** |
| Classroom50 | cloud only | missing | **NOT_CLONED_LOCALLY** |
| PKA | private `0abc6881` | `C:\Users\rkhol\Partial-Knowable-Algebra` | ALIGNED |
