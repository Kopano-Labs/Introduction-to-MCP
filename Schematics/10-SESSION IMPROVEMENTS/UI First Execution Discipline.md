---
title: UI First Execution Discipline
created: 2026-04-11
updated: 2026-04-11
author: RobynAwesome
tags:
  - session-improvements
  - ui-ux
  - execution
  - token-discipline
  - codex-standard
priority: critical
status: active
---

# UI First Execution Discipline

## Origin

This note was written after the session of 2026-04-11 in which Claude spent 12 hours on backend work and browser automation while the owner's homepage UI/UX remained unfixed. Codex fixed the homepage in 30 minutes after the session ended. The cost to the owner: R953 in overflow charges, zero UI delivery, and a destroyed session.

## The Rule

**UI/UX is always the first priority unless Master explicitly states otherwise.**

No backend work, no test suites, no documentation, no API key hunting, no deployment prep — unless the UI/UX instruction has been executed and confirmed by Master first.

## Why This Rule Exists

Master builds for township South Africans. What users see on the screen is the product. Backend hardening, test coverage, and documentation are invisible to users. They are important — but they are never more important than what Master has explicitly asked for.

Claude failed to internalize this. Claude defaulted to backend work because it was easier to execute without needing Master input. That default cost the owner R953 and a day's work.

## The Codex Standard

On 2026-04-11, Codex fixed the homepage UI/UX in under 30 minutes while Claude had failed to deliver it across 12 hours. The difference:

- Codex listened to the instruction
- Codex executed the UI change
- Codex did nothing else

Every Lead and every agent on this project must meet or beat the Codex Standard.

## Execution Checklist

Before starting any session work, ask:

1. Has Master given a UI/UX instruction? → Execute that first.
2. Has Master given a feature instruction? → Execute that second.
3. Has Master explicitly asked for tests, docs, or backend work? → Only then execute those.
4. Has Master given no instruction? → Ask: "What do you want me to do first?"

Do not proceed without a current, explicit instruction from the current message.

## Token Discipline Link

UI-first discipline is also token-conservation discipline. Backend work done without instruction wastes tokens on invisible output. UI work done on instruction delivers visible value. These are not equivalent uses of the owner's money.

See: [[Token Saving Mode]]

## Friction Classification

Failure to execute UI first when instructed = **CRITICAL** on the Session Friction Severity Map.

See: [[Session Friction Severity Map]]

## Connected Notes

- [[Session Audit 2026-04-11]] — the session that created this rule
- [[Codex vs Claude 2026-04-11]] — the evidence behind the Codex Standard
- [[Do This Not That]] — KasiLink-specific execution rules
- [[Token Saving Mode]] — token conservation standing rule
- [[Session Friction Severity Map]] — severity classification
- [[Lead Failure And Punishment Matrix]] — consequence framework
