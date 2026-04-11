# MASTER TODO Session 3

> [!important]
> Historical Session 3 workboard preserved as evidence.
> Current live control notes are [Now](../00-Home/Now.md), [task-board](task-board.md), [Open Issues](../06-Reference/Open%20Issues.md), and [Project Status](Project%20Status.md).
> Open checkboxes below should be read as Session 3 snapshot state unless they are explicitly marked as completed after Session 3.

> [!summary]
> Historical master tracker for the Session 3 work split. This file exists to preserve how cross-interference was managed between `Codex Terminal`, `Codex App`, and the user.

## Color Key

- `GREEN` = complete
- `AMBER` = active / in progress
- `RED` = blocked / external dependency
- `BLUE` = handoff / needs owner confirmation

## Current Reading Rule

- Treat this file as a historical lane snapshot from `2026-04-08`.
- Do not treat its parallel-lane file lists as current live collisions without checking current git status.
- Current cross-note truth has already been reconciled into the top-level Schematics control notes.

## Current Follow-Through Since Session 3

- [x] Azure CLI `az` installed locally after Session 3
- [x] Azure Developer CLI `azd` installed locally after Session 3
- [x] Session 3 notes reconciled into current top-level Schematics status notes
- [ ] Azure sign-in and Microsoft env/resource wiring still remain open
- [ ] reward system still needs end-to-end authenticated QA

## 2026-04-10 Operating Override | Lead And Dev Model

- Lead Developer: `Codex`
- DEV_1: `Germini (Google AI)`
- DEV_2: `Nother`
- DEV_3: `Meither`
- DEV_4: `Cicero`
- `DEV_1` is run externally by Master and must not be confused with a local spawned sub-agent in this Codex session.
- Standing rule: before starting any task, check current `git status`, active diffs, latest `comms-log.md` entry, and the other dev lanes' current progress.
- Logging rule: every major checkpoint must be written into [comms-log](comms-log.md) with exact date, time, action, verification, and next blocker truth.
- Reward rule: reward and referral findings must stay explicit in this board and in [Reward System Status - Session 3](Reward%20System%20Status%20-%20Session%203.md).

### Standing Doctrine Added 2026-04-10

- the standing multi-dev team is now `Germini`, `Nother`, `Meither`, and `Cicero`
- no additional ad-hoc spawn roles are the default vault model
- when `Codex` or `Claude` leads, sessions start with the standing dev team on standby and their 20-task boards visible first
- all current sessions are `pre-sessions` and training data for Orch
- lead can be `Codex`, `Claude`, or `Codex + Claude`
- lead target is `60% management / 40% coding`
- token-saving mode is mandatory outside Plan Mode and outside Lead-only sessions with Master
- if vault evidence or official research does not prove a claim, stop guessing and ask Master

### DEV_1 | Germini | Reward System, Product Truth, And Demo Narrative

- [x] check current dev progress, diffs, and latest comms before touching reward work
- [x] map the live reward and referral code paths that actually exist
- [x] identify auth and data dependencies blocking end-to-end reward QA
- [x] verify reward page claims against backend fields and current UI truth for the current workspace surface
- [x] verify the referral API contract and expected request plus response behavior for the current workspace surface
- [x] verify the 5-level referral ladder against code, not assumptions for the current workspace surface
- [x] inspect birthday reward behavior and confirm whether product intent is documented for the current workspace surface
- [x] inspect placeholder achievements and classify each one as real, placeholder, or deferred for the current workspace surface
- [x] inspect perk redemption logic and record what is proven versus unproven for the current workspace surface
- [x] inspect manager and admin reward visibility requirements for the current workspace surface
- [x] inspect any rewards wording that still says `coming soon` and decide whether it is true for the current workspace surface
- [x] build the end-to-end reward QA checklist for live authenticated verification
- [x] define exact owner actions needed before real reward verification can happen
- [x] define fallback wording if the reward system is out of the demo script
- [x] sync reward-system truth into [Reward System Status - Session 3](Reward%20System%20Status%20-%20Session%203.md)
- [x] sync reward blockers into the live Schematics control notes after verification
- [x] add a dated reward update into [comms-log](comms-log.md)
- [x] separate proven reward behavior from product assumptions in one clean summary
- [x] produce a reward go or no-go recommendation for demo use
- [x] hand off exact next reward actions to Lead

**Current lane state:** `STANDBY`

- DEV_1 completed the documentation-and-truth tranche that was possible from the current workspace.
- No further reward verification should be assigned until real reward/referral code paths are present or a concrete KasiLink reward codebase slice is supplied.

### DEV_2 | Nother | Runtime, Verification, And Route Hardening

- [ ] check current dev progress, diffs, and latest comms before touching runtime work
- [ ] confirm `Council -> Labs` is the first safe-route handoff
- [ ] confirm `Labs` emphasizes `Console`, then `Forge`, then `Admin`
- [ ] confirm `Console` keeps `Send` primary and `Stream` explicitly optional
- [ ] confirm `Forge` reads as view-first and not edit-first
- [ ] confirm `Admin` stays clearly internal and second in the script
- [ ] get the local Orch runtime stable on `127.0.0.1:8000`
- [ ] verify `GET /updates`
- [ ] verify `GET /sessions`
- [ ] verify `POST /auth/login`
- [ ] verify `POST /api/labs/mcp-console/chat`
- [ ] verify `GET /api/labs/microsoft-readiness`
- [ ] verify `GET /api/labs/cowork/rooms`
- [ ] verify `POST /broadcast` flows back into `GET /updates`
- [ ] rerun the GUI production build without sandbox or process-spawn false positives
- [ ] separate real code regressions from environment and runtime failures
- [ ] record exact command evidence with date and time in [comms-log](comms-log.md)
- [ ] update the blocker list for any remaining runtime verification gaps
- [ ] re-check other dev changes before applying any verification fix
- [ ] hand off the final verification verdict to Lead

### DEV_3 | Meither | Schematics, Obsidian, And Status Synchronization

- [ ] check current dev progress, diffs, and latest comms before touching docs
- [ ] keep the Microsoft Demo Day hub aligned with the locked safe route
- [ ] keep [2026-04-09 Close State](../Microsoft%20Demo%20Day!/2026-04-09%20Close%20State.md) linked and accurate
- [ ] keep the countdown baseline honest about `Orch-only` versus owner-blocked `KasiLink`
- [ ] keep the Orch Demo Script synced with the actual UI route and labels
- [ ] keep the owner checklist synced with real Azure, auth, and reward blockers
- [ ] keep [SA Startup Week Demo](../Microsoft%20Demo%20Day!/SA%20Startup%20Week%20Demo.md) marked as target story, not current live baseline
- [ ] keep [Azure Demo Day Playbook](../Microsoft%20Demo%20Day!/Azure%20Demo%20Day%20Playbook.md) framed as readiness story
- [ ] keep Obsidian links clean across the Demo Day folder
- [ ] update [comms-log](comms-log.md) after each major checkpoint with full dated detail
- [ ] keep [Reward System Status - Session 3](Reward%20System%20Status%20-%20Session%203.md) synced with current truth
- [ ] keep this master board current as task ownership shifts
- [ ] keep `Now`, `Project Status`, and `Open Issues` aligned if demo state changes
- [ ] capture agent outputs into readable human handoff notes
- [ ] record explicit fallback wording for blocked routes and owner-blocked Azure claims
- [ ] track owner-blocked items with dates and exact prerequisite wording
- [ ] flag contradictions between code truth and doc truth immediately
- [ ] preserve historical notes while adding current-dated overrides
- [ ] prepare the next session start-here summary if today rolls over
- [ ] hand off the final doc pack status to Lead

### DEV_4 | Cicero | Governance, Research, And Orch Training System

- [x] check current dev progress, diffs, and latest comms before touching governance work
- [x] verify the standing team roster stays exact across live control notes
- [x] verify `DEV_1` remains `Germini (Google AI)` everywhere
- [x] verify `DEV_4` remains `Cicero` everywhere
- [x] map which folders in `Schematics` still lack `index.md`
- [x] build the additive-only folder index rollout plan
- [x] compile official-source management research for lead doctrine
- [x] compile official-source Microsoft startup and platform signals
- [x] compile official-source AWS startup and agentic-platform signals
- [x] compile official-source OpenAI agent platform signals
- [x] compile official-source Anthropic agent and MCP signals
- [x] compile Africa-first hosted-event and startup proof signals from official sources
- [x] create the incubation process for [08-IDEAS AT BIRTH](../08-IDEA'S%20AT%20BIRTH/index.md)
- [x] create the staged progression ladder for [09-ORCH PROGRESSION](../09-ORCH%20PROGRESSION/index.md)
- [x] create the lead self-reflection doctrine for [10-SESSION IMPROVEMENTS](../10-SESSION%20IMPROVEMENTS/index.md)
- [x] create the hallucination taxonomy and protocol scaffolding for [11-AI HALLUCINATION - CRITICAL](../11-AI%20HALLUCINATION%20-%20CRITICAL/index.md)
- [x] scrape historical hallucination and fabrication references from `Schematics`
- [x] mirror governance changes into [dev-tracker](dev-tracker.md) and [comms-log](comms-log.md)
- [x] keep reward `NO-GO` truth explicit in governance and demo notes
- [x] hand off the research and governance pack status to Lead

**Current lane state:** `SUBSTANTIAL PASS COMPLETE`

- remaining work is now refinement, continued research deepening, and clean review before commit

## Historical Ownership Board

### `AMBER` Codex Terminal

- [x] audit `STRUCTURE` for stale handoff state
- [x] verify recent commit trail and active blockers
- [x] inspect reward-system implementation status
- [x] create Session 3 coordination notes in `STRUCTURE`
- [x] mirror Session 3 coordination notes into external `Schematics`
- [x] verify the current combined working tree still completes `npm run build`
- [x] create 4-tier Obsidian audit schema and per-tier interface audit notes
- [x] regenerate the four court image assets with original non-infringing artwork
- [x] convert booking flow to hourly slot selection with backend validation
- [x] run targeted eslint cleanly on the booking/court change set
- [x] fix court detail fallback so seeded courts still open when Mongo is unavailable
- [x] fix `GiscusComments` env-readiness bug that was breaking linted builds
- [x] reduce a safe subset of warning backlog outside the overlapping Codex App lane
- [x] complete a second safe warning-reduction batch across untouched API/form utility files
- [x] keep ownership lanes current while parallel work was active
- [x] update this board after each safe session checkpoint

Next:

- keep docs and handoff lane isolated
- visually QA the new court imagery and hourly booking flow on real mobile breakpoints
- continue warning reduction only in untouched files
- wait for overlapping code lane to settle before touching reward/referral code
- verify reward-system completion after conflict risk is gone

### `AMBER` Codex App / Parallel Lane

> Historical overlap snapshot only. Validate against current repo status before acting on it.

- [ ] finish current overlapping edits already presen
