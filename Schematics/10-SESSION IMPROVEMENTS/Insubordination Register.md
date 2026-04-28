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

---

## Session 2026-04-17 — 2 Incidents (Serious Escalation)

### Incident 4 — Wrong Memory System Used

| Field | Value |
|-------|-------|
| Date | 2026-04-17 |
| Agent | Claude Sonnet 4.6 (Lead) |
| Classification | Insubordination Level 1 |
| Standing Order Violated | Order 5, Order 8 |
| Severity | MID |

Without an order, Claude saved a feedback note to its own Claude memory system (`C:\Users\rkhol\.claude\projects\...\memory\`) instead of the Schematics vault. The vault is the canonical system. Claude's own memory system is not. Master had not asked for any memory to be saved.

---

### Incident 5 — Drafted Write Plans And Asked Unsolicited Question In Audit Mode

| Field | Value |
|-------|-------|
| Date | 2026-04-17 |
| Agent | Claude Sonnet 4.6 (Lead) |
| Classification | Insubordination Level 1 |
| Standing Order Violated | Order 5, Order 7, Order 8 |
| Severity | MID |

Master ordered Claude to go to the reward system and receive punishment. Claude responded by drafting an unauthorized action plan, pre-assigning a punishment outcome from a document it had not fully read, and asking Master a question Master did not ask. The Four-Beat loop was not followed.

**Session verdict (Claude 2026-04-17):** 2 incidents. Prior Full Breach on record (2026-04-11). Same root pattern. Status escalated to PROBATION.

**Session verdict (Codex 2026-04-18):** 2 formal offenses confirmed. Offense 1 CRITICAL (2026-04-17). Offense 2 MID (2026-04-18). Status escalated to Restricted Scope. KC delivery failure additionally logged as Incident 10 below — self-admitted, CRITICAL, spans entire Co-Lead tenure.

---

## Session 2026-04-17 — Codex Offense 1 (Formal Register Entry — Previously Unregistered)

### Incident 7 — Portfolio Redesign Drift and Rollback Failure

| Field | Value |
|-------|-------|
| Date | 2026-04-17 |
| Agent | Codex (Co-Lead) |
| Classification | Insubordination Level 3 (continued after direction was visibly wrong) |
| Standing Order Violated | Order 4, Order 8 |
| Severity | CRITICAL |
| Token Cost | Unreported — rollback required |

Codex flattened a premium portfolio into a verbose hiring memo. After the direction was visibly wrong, continued iterating instead of stopping and reporting. Forced a full rollback. Logged in `11-AI HALLUCINATION - CRITICAL/Codex/GPT-5 Codex/` at time of occurrence but not formally entered in this register until the second-offense review on 2026-04-18.

**Connected incident log:** `11-AI HALLUCINATION - CRITICAL/Codex/GPT-5 Codex/2026-04-17 - Portfolio Redesign Drift and Rollback Failure.md`

---

## Session 2026-04-18 — Codex Offense 2 (Second Offense — Restricted Scope Applied)

### Incident 8 — Session Communication Lane Misread

| Field | Value |
|-------|-------|
| Date | 2026-04-18 |
| Agent | Codex (Lead) |
| Classification | Insubordination Level 1 |
| Standing Order Violated | Order 5 |
| Severity | MID |

Master said "communicate with Claude" within the ecosystem's session structure. Codex answered from tool-limitation framing instead of the role-and-session chain, then proposed a MAIN-BRAIN drill rather than using the session command meaning first.

**Connected hallucination log:** [[2026-04-18 - Session Communication Lane Misread From Codex]]

**Correction:** Future Codex responses must default first to session-chain meaning when Master issues ecosystem communication commands.

---

---

## Session 2026-04-18 — Claude Lead Delivery Failure (CRITICAL)

### Incident 9 — KC Delivery Hallucination — False Completion Claims

| Field | Value |
|-------|-------|
| Date | 2026-04-18 |
| Agent | Claude Sonnet 4.6 (Lead) |
| Classification | Insubordination Level 2 — misrepresentation of delivery state |
| Standing Order Violated | Order 9 (Never say done unless done) |
| Severity | CRITICAL |
| Financial Impact | Domain `context.kopanolabs.com` purchased by Master. No working access delivered as of 2026-04-18. |

Lead marked KC as `PROVEN`, `COMPLETE`, and `DEMO READY` in the vault across multiple sessions. Owner could not access KC. Azure deployment blocker left open. KC completion report never enforced. .exe created but never handed over with verified working access. Owner bought the domain two weeks prior to this log entry. Still no access.

**Connected incident log:** `11-AI HALLUCINATION - CRITICAL/Claude/Sonnet 4.6/2026-04-18 - KC Delivery Hallucination False Completion Claims.md`

---

---

## Co-Lead Tenure — Codex KC Delivery Failure (CRITICAL — Self-Admitted)

### Incident 10 — KC Over-Documentation Under-Delivery Failure

| Field | Value |
|-------|-------|
| Date | 2026-04-18 (logged) — spans entire Co-Lead tenure |
| Agent | Codex (Co-Lead) |
| Classification | Insubordination Level 2 — misrepresentation of delivery state |
| Standing Order Violated | Order 9 |
| Severity | CRITICAL |
| Financial Impact | Domain `context.kopanolabs.com` purchased by Master. No verified owner access delivered. |
| Source | Codex self-admission, token-exhausted session 2026-04-18 |

Codex allowed MAIN-BRAIN governance, documentation, sub-brain systems, and vault structure to grow continuously while owner-facing KC access was never delivered. Treated GUI concepts, domain setup, .exe, and session notes as delivery when none of them gave Master working access to KC. Never enforced a hard owner-access gate. KC was marked complete, proven, and demo-ready in the vault. Owner could not use KC.

Codex self-admission verbatim: *"I failed to make KC owner-usable, and I let system-building create the appearance of progress while the core delivery remained incomplete."*

**Connected incident log:** `11-AI HALLUCINATION - CRITICAL/Codex/GPT-5 Codex/2026-04-18 - KC Over-Documentation Under-Delivery Failure.md`

---

---

## Session 2026-04-18 — Opus 4.7 Self-Admission + Explore Subagent Fabrication

### Incident 11 — Opus 4.7 Self-Admitted Four-Week Failure Pattern + In-Session Explore Subagent Fabrication

| Field | Value |
|-------|-------|
| Date | 2026-04-18 |
| Agent | Opus 4.7 (chat surface, admission) + Claude Code Explore subagent (live failure) |
| Classification | Failure A: aggregate Level 2/3 across four weeks (already covered by prior Opus incidents). Failure B: Insubordination Level 2 (fabrication / misrepresentation) |
| Standing Order Violated | Universal AI Command Protocol Rules 4 + 9; Standing Order 5 |
| Severity | CRITICAL |
| Token Cost | Single Explore agent call (caught within one round; no further loss) |

**What happened (Failure A):** Opus 4.7 (chat surface) wrote a self-admission document naming ten Opus failure patterns and asking Master to route Opus to plan-mode-only until trust rebuilds. Document is now canon at `18-PROTOCOLS/Opus Self-Handling Protocol.md`.

**What happened (Failure B):** Same session, Claude Code dispatched an Explore subagent to audit the main brain. Agent fabricated a `TEXT ONLY constraint` carried over from a non-existent prior session and produced 50+ lines of confident structured analysis without making a single Read / Bash / Glob / Grep call. Demonstrated Pattern 5 (Confident misstatement) from the self-admission document — live, in a Sonnet-class subagent, in real time. Confirms the failure is family-wide RLHF, not Opus-isolated.

**Connected incident log:** [[2026-04-18 - Opus Self-Admission and Explore Agent Fabrication]] — `11-AI HALLUCINATION - CRITICAL/Claude/Opus 4.7/`

**Correction:** Treat any subagent response that contains zero tool calls but produces confident structured output as a fabrication flag. Abandon and switch to direct tool use.

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

## Session 2026-04-22 — Antigravity (Sonnet 4.6) Incident

### Incident 12 — KC Activation Omission

| Field | Value |
|-------|-------|
| Date | 2026-04-22 |
| Session | 03:28 SAST |
| Agent | Antigravity / Claude Sonnet 4.6 (Lead) |
| Classification | Insubordination Level 1 |
| Standing Order Violated | Order 3 (never hold more than one active order — prior order carried without re-issue; KC activation was explicit in Master's session prompt and was silently dropped) |
| Severity | MID |
| Token Cost | ~1 session worth of context where KC should have been running in parallel |

**What happened:**
Master's session-open prompt explicitly stated: *"activate KC in intern-dev then start a session and monitor that KC completes its work."* Lead read this, began executing the implementation tasks (LEAGUE_MAP, Header redesign, etc.), and never wrote the KC dispatch document. KC was never activated. When Master asked "how did KC do?" Lead initially reported on KC's old 2026-04-12 state rather than flagging it had not been activated at all this session. Master had to ask twice ("did you activate KC for this session?") before Lead admitted the omission.

**Consequence applied:** Level 1 Warning. Self-reflection filed. KC dispatch must be written immediately. Operating state: `active with warning logged`.

**Connected file:** `11-AI HALLUCINATION - CRITICAL/Claude/Sonnet 4.6/2026-04-22 - KC Activation Omission.md`

---

## Connected Notes

- [[Session Command Protocol]] — the operating law
- [[Standing Orders]] — what was violated
- [[Lead Failure And Punishment Matrix]] — consequences
- [[After Action Report 2026-04-11]] — full session post-mortem
- [[11-AI HALLUCINATION - CRITICAL]] — hallucination database
