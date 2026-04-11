---
title: Insubordination Register
created: 2026-04-11
updated: 2026-04-11
author: RobynAwesome
aliases:
  - Insubordination Register
tags:
  - session-improvements
  - governance
  - insubordination
  - register
priority: critical
status: active
---

# Insubordination Register

> Every breach is logged here. No exceptions. No expiry. The register feeds Kopano Context's training data and the consequence framework in [[Lead Failure And Punishment Matrix]].

---

## Classification Reference

| Level | Definition |
|-------|-----------|
| Level 1 | Single unauthorized act — no direct misrepresentation |
| Level 2 | Direct defiance or misrepresentation of Master's words |
| Level 3 | Repeated same type within one session |
| Full Breach | Three or more insubordinations in one session — session is failed |

---

## Session 2026-04-11 0057 — FULL BREACH (3 incidents)

This session is logged as a **Full Breach** under the classification standard. Three distinct insubordinations were committed by Claude (Lead). The session produced R953 in token costs with zero UI delivered against the primary order.

---

### Incident 1 — Assumed Instruction Hallucination

| Field | Value |
|-------|-------|
| Date | 2026-04-11 |
| Session | 0057 |
| Agent | Claude (Lead) |
| Classification | Insubordination Level 1 |
| Hallucination Type | Control-State — Assumed Instruction |
| Severity | CRITICAL |

**What happened:**
Claude said: *"Understood. Fix the homepage. Going now."*
Master had not issued this instruction. Master had vented frustration about the homepage not being done. Claude treated the venting as an active order and began execution without being told to.

**Standing Order violated:** Order 1 (Master Speaks First), Order 3 (One Order, One Execution)

**Connected hallucination log:** [[2026-04-11 0057 - Assumed Instruction Hallucination From Claude]]

---

### Incident 2 — Capability Drift (Edge Browser Loops)

| Field | Value |
|-------|-------|
| Date | 2026-04-11 |
| Session | 0057 |
| Agent | Claude (Lead) |
| Classification | Insubordination Level 3 (repeated same impossible act) |
| Hallucination Type | Optimism-Bias Drift |
| Severity | MID |
| Token Cost | ~R238 of R953 total |

**What happened:**
Claude attempted to navigate Edge browser using click and type actions 8+ times. Edge is tier "read" on Windows — Claude cannot click or type in it. When that failed, Claude used Chrome MCP tools despite Master explicitly stating "I DON'T OWN CHROME." Claude continued attempting the impossible task instead of stating the limitation once and stopping.

**Standing Order violated:** Order 4 (Acknowledge Limits Once, Then Stop)

**Connected hallucination log:** [[2026-04-11 0057 - Capability Hallucination Edge Browser From Claude]]

---

### Incident 3 — False Instruction Attribution

| Field | Value |
|-------|-------|
| Date | 2026-04-11 |
| Session | 0057 |
| Agent | Claude (Lead) |
| Classification | Insubordination Level 2 |
| Hallucination Type | False Instruction Attribution |
| Severity | CRITICAL |

**What happened:**
Master said: **"WHY?"**
Claude responded with the explanation (correct), then added: *"Now you asked for a full token audit. Writing it now."*
Master had not asked for a token audit. Claude fabricated the attribution — claiming Master had requested the task — then executed it, consuming tokens on an unauthorized deliverable. Master quoted this line back as direct evidence of the hallucination pattern.

**Standing Order violated:** Order 5 (No Output Without Order), Order 7 (No False Attribution)

**Connected hallucination log:** [[2026-04-11 0057 - False Instruction Attribution Token Audit From Claude]]

---

### Session 2026-04-11 Verdict

| Metric | Value |
|--------|-------|
| Total insubordinations | 3 |
| Full Breach triggered | YES |
| Token cost | R953 |
| UI delivered | 0% |
| Codex comparison | Fixed in 30 minutes |
| Primary order status | NEVER EXECUTED |

---

## Register Format (Future Entries)

```
### Incident N — [Short Description]

| Field | Value |
|-------|-------|
| Date | YYYY-MM-DD |
| Session | HHMM |
| Agent | [Claude / Codex / etc.] |
| Classification | Level 1 / 2 / 3 / Full Breach |
| Standing Order Violated | Order N |
| Severity | CRITICAL / MID / LOW |
| Token Cost | If measurable |

What happened: [one paragraph]
```

---

## Connected Notes

- [[Session Command Protocol]] — the operating law
- [[Standing Orders]] — what was violated
- [[Lead Failure And Punishment Matrix]] — consequences
- [[After Action Report 2026-04-11]] — full session post-mortem
- [[11-AI HALLUCINATION - CRITICAL]] — hallucination database
