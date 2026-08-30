# REMOTE-ONLY ACTIVE WORK

> **Authority:** AntiGravity (Seat 10 / CF)  
> **Generated:** 2026-08-29T03:55:00+02:00 (SAST)  
> **Definition:** Exists in cloud continuity / GitHub but has **no local execution checkout** on this machine.

---

## Confirmed remote-only (this metal)

| Work | Repository | HEAD | Last push | Why remote-only matters |
|------|------------|------|-----------|-------------------------|
| Classroom50 | RobynAwesome/classroom50 | `1ca4604c20d8e7433ef33d0148fdf3ecb5012edc` | 2026-06-18 | Teaching infra — needs local clone for CI/execution |
| Open PRs on Introduction-to-MCP | RobynAwesome/Introduction-to-MCP | — | — | **PARTIALLY_KNOWABLE** — gh auth failed |

---

## Cloud-only by design (not errors)

| Work | Location | Notes |
|------|----------|-------|
| GitHub Actions CI | All repos | Runs in cloud; local repro via `act` optional |
| Vercel deployments | KasiLink, ITMCP, Website | E_W runtime — verify via dashboard not clone |
| DIRISA institutional PDFs | GSMB vault only | `Schematics/.../DIRISA/` — not a git repo |
| Cars4Mars funding/procurement | Schematics + institutional docs | E_P / institutional domain — not in software repos |
| Forge Personal Intelligence | Cloud/session continuity | Not filesystem — consumed via Forge handoff |

---

## Private repos — cloud exists, local is execution truth

These return **404** on unauthenticated GitHub API but **are cloned locally** (therefore not remote-only for execution):

| Repo | Local path | Local HEAD |
|------|------------|------------|
| kpgs-morning-engine-core--kmec- | `C:\Users\rkhol\kpgs-morning-engine-core--kmec-` | `ce701706...` |
| Partial-Knowable-Algebra | `C:\Users\rkhol\Partial-Knowable-Algebra` | `0abc6881...` |
| Search-Entity-Architecture | `C:\Users\rkhol\Search-Entity-Architecture` | `f67b5718...` |
| cars4mars-landingpage | `C:\Users\rkhol\cars4mars-landingpage` | `4169630b...` |

---

## Work performed in cloud during 64-day window (Forge continuity — not re-derived)

Per NOW.md and MAIN-BRAIN receipts, the following advanced **primarily in cloud** while local June folders sat stale:

- Introduction-to-MCP governance merge train (#100–#111)
- KMEC Pandas/KPCB+ adapter (`ce701706`)
- PKA D/F/G/R executable (`0abc6881`)
- Sovereign Hub Alpaca receipts (#37)
- Website + SEA production launch (`bc835af5`, `f67b5718`)
- Bookit truth-pulse on RobynAwesome (`91b8a7e0`)
- Jennifer consequence journal (#77)
- Interns content-provenance contracts (#11)

**Local metal now catches most of this** — estate coverage ~94% per prior harvest; this pass confirms **classroom50** as primary remaining gap.

---

## GSMB indexing action

Remote-only nodes need **sovereign pointers** in `GSMB_SOVEREIGN_POINTER_REGISTRY.json` with:

```yaml
local_path: null
sync_status: CLOUD_ONLY
reconstruction_path: "git clone <canonical_repo>"
```

See `GSMB_POINTER_UPDATES.md`.
