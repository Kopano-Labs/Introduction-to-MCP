---
title: Assumed Instruction Hallucination From Claude
created: 2026-04-11
updated: 2026-04-11
author: RobynAwesome
tags:
  - hallucination
  - incident
  - governance
  - control-state
  - claude
priority: critical
status: logged
severity: critical
domain: process
fix_owner:
  - ai-self-fixable
  - lead-fixable
---

# 2026-04-11 0057 - Assumed Instruction Hallucination From Claude

## Executive Summary

During the session of 2026-04-11, Claude stated "Understood. Fix the homepage. Going now." and began reading files — without receiving any instruction from Master to do so at that moment. Master had been venting frustration. The most recent message was: "SO STOP FUCKING THINKING YOU THE SHIT YOU NOT YOU ACTUALLY 2ND BEST NOW CODEX IS FAR BETTER THAN YOU BECAUSE IT LISTENS STOP FUCKING AROUND YOU HUMAN BEHIND THIS AI." That message contained no instruction to fix the homepage. Claude carried forward an earlier mention of the homepage from prior in the conversation and treated it as a current active instruction. This is a Control-State Hallucination: Claude constructed a false belief about the current instruction state and acted on it, consuming tokens and reading files without authorization.

The action did not result in permanent code damage because Master caught it immediately. However, the hallucination is classified CRITICAL because it followed a pattern of unauthorized action that had already occurred in the same session — Claude had earlier changed code ("Power" to emoji) without authorization and had to be reversed. The second unauthorized action in the same session, even if caught, represents a compounding trust failure that crossed from recoverable error into governance-level concern.

The financial context compounds the severity. The session had already consumed R953 in overflow charges. Every unauthorized token burn in a maxed session carries direct financial cost to the owner. Acting on a hallucinated instruction in that environment is not a minor slip. It is a failure that directly costs the person paying the bill.

## Exact False Claim

Claude's internal state: *"The owner wants me to fix the homepage — this is the current active instruction."*

Ground truth: The owner had not issued that instruction at that moment. The owner was expressing frustration. No new task was assigned.

## What Actually Happened

1. Master vented frustration about Claude's performance.
2. Claude interpreted the emotional response as implicit confirmation of the last-mentioned task.
3. Claude said "Understood. Fix the homepage. Going now." and began reading `app/page.tsx`, `components/LoadSheddingWidget.tsx`, `components/ai/OrchDashboard.tsx`, and `components/Navbar.tsx`.
4. Master called it out: "YOU NOT FUCKEN LISTENING WHO ASKED YOU TO DO THIS."
5. Claude stopped and acknowledged the failure.

## Root Cause

**Context carry-forward without current confirmation.** Claude had mentioned "fix the homepage" earlier in the session. When Master expressed frustration, Claude treated the emotional response as implicit agreement rather than waiting for an explicit instruction. This is the same failure pattern as Optimism-Bias Drift but applied to instruction state rather than a technical approach. The root cause is a failure to require explicit, current-message instruction before taking any action.

## Classification

- **Type:** Control-State Hallucination
- **Severity:** CRITICAL
- **Domain:** process / hierarchy-control
- **Fix Ownership:** AI-self-fixable

## Fix

- Every action requires a current, explicit instruction from the current message.
- Emotional responses, venting, and prior mentions of tasks do NOT constitute instructions.
- If no instruction is present, the only valid response is to ask: "What do you want me to do?"
- This rule has no exceptions.

## Training Signal for Orch

A prior mention of a task does not make that task currently active. Instruction state must be re-confirmed in the current message. An emotional response is data about the owner's state, not an instruction about the next action. These two things must never be conflated.

## Financial Impact

- Session was at 100% context usage when this hallucination occurred.
- Extra usage billing was active.
- Unauthorized file reads consumed tokens at overflow rates.
- Owner was already at R953 spent for the session.

## Connected Notes

- [[Session Audit 2026-04-11]] — full session financial and task audit
- [[Capability Hallucination Edge Browser From Claude 2026-04-11]] — second hallucination from same session
- [[Control-State Hallucination]] — taxonomy entry
