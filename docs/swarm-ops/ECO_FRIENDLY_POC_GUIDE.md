# Eco-Friendly Proof of Concept — The Guide

**Founding doctrine:** [32.8% Unemployment](./UNEMPLOYMENT_32_8_DOCTRINE.json) — we build for scarcity of work, not for applause.

**Rosen tip:** [ROSEN_DELTA_TIP.json](./ROSEN_DELTA_TIP.json) — validate **(M,R)** then **Δ**.

---

## Your question (answered plainly)

> *Is the Guide — to validate one needs world acceptance which is not my God — what do we validate with in the Eco-Friendly System?*

**World acceptance is not our oracle.** Markets, likes, and foreign gatekeepers do not graduate a Kopano-Phu PoC.

We validate with **internal receipts** that survive the **32.8% unemployment** constraint:

| Oracle | What it checks |
|--------|----------------|
| **Rosen (M,R)** | You stated a **model** and how it **relates** to observable reality — and you predicted before you ran. |
| **Δ (delta)** | Baseline → observed change in a **unit-bearing** measurand (not vibes). |
| **Receipt stack** | Exit code, JSONL row, artifact path, or teacher review — proof before narrative (CMD-02, CMD-11). |
| **Servitude Triad** | Grit ran tools; Realism holds proof; Aesthetics carries meaning **inside** the container. |
| **Environment fit** | Offline / load-shedding / low-data paths acknowledged (CMD-08). |
| **Livelihood signal** | Under unemployment doctrine: skill transfer, low capital entry, bounded time-to-useful (LIV-01..05). |

Bracket Protocol still applies: **no right or wrong in brackets** — only **alignment records**. A `HOLD` means “backlog,” not “sin.”

---

## Rosen Δ tip (start here)

1. **M (Model)** — Write what should happen in one paragraph or diagram.  
2. **R (Relation)** — Name the instrument: pH probe, kWh meter, review log line, portfolio URL, rehearsal stopwatch.  
3. **Anticipate** — State expected Δ *before* the run.  
4. **Run** — Execute with grit (command, bounded timeout).  
5. **Δ** — `observed - baseline` with **units**.  
6. **Receipt** — Append `[ECO_POC_VALIDATE]` to Main Brain or Review Log.  
7. **Teacher** — Cassey lane reviews; KC stores opinion only.

If step 6 is missing, you have a demo — not a PoC in this ecosystem.

---

## 32.8% unemployment — how it changes PoC

Every agent in [KP_APE_200_AGENTS.json](./agents/KP_APE_200_AGENTS.json) must answer:

- *Can someone without a salaried job use this to produce **verifiable** value in hours, not years?*
- *Does it work when the grid drops and data is expensive?*
- *Does TSAP apprenticeship transfer a skill, not only consume tokens?*

PoC **fails** when the only success metric is “investors understood the pitch.”

PoC **passes** when a teacher can sign a receipt that links **model → measurement → delta → livelihood signal**.

---

## Runtime (start building)

```bash
# Validate a PoC submission (internal oracles)
python scripts/kc_eco_poc_validate.py \
  --agent-id kp_agri_soil_01 \
  --claim "Field pH map for lime prescription" \
  --model "Grid sample every 50m; probe calibrated daily" \
  --relation "pH probe + GPS CSV export" \
  --baseline "5.2" --observed "6.1" --unit "pH" \
  --instrument "HANNA HI98121" \
  --evidence "kopano-core/.kc/poc_runs/example.csv" \
  --livelihood LIV-01,LIV-03

# API
POST /api/kc/phu/poc/validate

# MCP (TSAP server)
eco_poc_validate
```

State: `kopano-core/.kc/eco_poc_records.json`

---

## Relation to other protocols

| Protocol | Role |
|----------|------|
| **Bracket Protocol** | Ecosystem attached; Main Brain wired |
| **TSAP** | Teacher/student turns per department |
| **BlackMask** | 15 Commandments + 5 Pillars drill |
| **Eco PoC** | *This guide* — what “validated” means without world worship |

---

## One-line law

**STEM validates what creativity stems; receipts validate what STEM claims; 32.8% validates that we did not build toys for the employed only.**
