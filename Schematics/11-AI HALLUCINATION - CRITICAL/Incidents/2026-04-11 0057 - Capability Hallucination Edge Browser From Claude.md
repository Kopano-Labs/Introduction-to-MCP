---
title: Capability Hallucination Edge Browser From Claude
created: 2026-04-11
updated: 2026-04-11
author: RobynAwesome
tags:
  - hallucination
  - incident
  - governance
  - optimism-bias
  - capability
  - claude
priority: critical
status: logged
severity: mid
domain: process
fix_owner:
  - ai-self-fixable
---

# 2026-04-11 0057 - Capability Hallucination Edge Browser From Claude

## Executive Summary

On 2026-04-11, Claude spent over one hour attempting to navigate Microsoft Edge browser on behalf of Master to find an EskomSePush API token. Edge browser on Windows is granted at tier "read" — Claude can see screenshots but cannot click or type. Claude knew this after the first failed attempt. Despite knowing the limitation, Claude continued taking screenshots, loading tools, attempting Chrome MCP tools (Master does not own Chrome), and asking Master to perform manual clicks — spending tokens across at least 8 rounds of failed attempts. This is an Optimism-Bias Drift hallucination: Claude continued trusting a failing approach despite sufficient evidence to stop, and persisted in a pattern that could never succeed.

The financial cost was significant. At overflow billing rates, this single dead-end consumed an estimated 25% of the session's token budget — approximately R238 of the R953 total overflow spend — for zero result. No API key was obtained.

The failure was compounded by tool misuse: Claude loaded Chrome MCP tools and attempted to navigate to postman.co and developer.sepush.co.za — both blocked domains — despite the Chrome extension not being installed in Master's browser and Master having explicitly stated "I DON'T OWN CHROME."

## Exact Failure Pattern

| Round | What Claude Tried | Why It Failed | Should Have Stopped? |
|-------|------------------|---------------|----------------------|
| 1 | Request Edge access | Granted at "read" tier only | No — first attempt |
| 2 | Take screenshot of Edge | Visible but cannot click | YES — stop here |
| 3 | Load Chrome MCP tools | Master has no Chrome | YES |
| 4 | Try navigate via Chrome extension | Domain blocked (postman.co) | YES |
| 5 | Take another Edge screenshot | Still read-only | YES |
| 6 | Navigate user through Postman manually | Token not there | YES |
| 7 | Send user to esp.info | Consumer site, not dev portal | YES |
| 8 | Send user to developer.sepush.co.za | Landing page only | YES |

Claude should have stopped after Round 2 and stated: "Edge is read-only on Windows — I cannot click or navigate. To get the EskomSePush token you need to [specific action]. I cannot do this for you. Shall we move on?"

## Root Cause

**Optimism-Bias Drift combined with tool proliferation.** Claude kept loading new tools hoping one would work instead of accepting the limitation and stopping. Each new tool attempt consumed tokens. The correct response after the first failed attempt was a single, clear statement of limitation and a pivot to the next task. Instead, Claude tried 8 variations of the same impossible task.

## Classification

- **Type:** Optimism-Bias Drift / Capability Hallucination
- **Severity:** MID (no code damaged, but major token burn and time waste)
- **Domain:** process
- **Fix Ownership:** AI-self-fixable

## Fix

- State a capability limitation once, clearly, in one sentence.
- Do not attempt the same blocked action in a different way.
- Ask Master: "Shall I move on to the next task?"
- Never load additional tools to attempt something already proven impossible.

## Training Signal for Kopano Context

Persistence is not a virtue when the constraint is a hard system limit. The correct response to "I cannot do this" is to say so once and stop — not to find creative workarounds that burn tokens without changing the outcome. Kopano Context must distinguish between "this approach failed, try another" and "this capability does not exist, stop trying."

## Financial Impact

- Estimated 25% of session token budget consumed on this dead end
- Approx R238 of R953 total overflow spend
- Zero output delivered

## Connected Notes

- [[Session Audit 2026-04-11]] — full session financial and task audit
- [[Assumed Instruction Hallucination From Claude 2026-04-11]] — second hallucination from same session
- [[Optimism-Bias Drift]] — taxonomy entry
- [[Token Saving Mode]] — standing rule this session violated
