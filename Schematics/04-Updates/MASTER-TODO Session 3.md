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
- [ ] reward system has no live implementation yet, so authenticated QA is blocked until product and code exist

## 2026-04-10 Operating Override | Lead And Dev Model

- Lead Developer: `Codex`
- DEV_1: `Germini (Google AI)`
- DEV_2: `Nother`
- DEV_3: `Meither`
- Standing rule: before starting any task, check current `git status`, active diffs, latest `comms-log.md` entry, and the other dev lanes' current progress.
- Logging rule: every major checkpoint must be written into [comms-log](comms-log.md) with exact date, time, action, verification, and next blocker truth.
- Reward rule: reward and referral findings must stay explicit in this board and in [Reward System Status - Session 3](Reward%20System%20Status%20-%20Session%203.md).

### DEV_1 | Germini | Reward System, Product Truth, And Demo Narrative

- [x] check current dev progress, diffs, and latest comms before touching reward work
- [x] map the live reward and referral code paths that actually exist
- [x] identify auth and data dependencies blocking end-to-end reward QA
- [x] verify reward page claims against backend fields and current UI truth
- [x] verify the referral API contract and expected request plus response behavior
- [x] verify the 5-level referral ladder against code, not assumptions
- [x] inspect birthday reward behavior and confirm whether product intent is documented
- [x] inspect placeholder achievements and classify each one as real, placeholder, or deferred
- [x] inspect perk redemption logic and record what is proven versus unproven
- [x] inspect manager and admin reward visibility requirements
- [x] inspect any rewards wording that still says `coming soon` and decide whether it is true
- [x] build the end-to-end reward QA checklist for live authenticated verification
- [x] define exact owner actions needed before real reward verification can happen
- [x] define fallback wording if the reward system is out of the demo script
- [x] sync reward-system truth into [Reward System Status - Session 3](Reward%20System%20Status%20-%20Session%203.md)
- [x] sync reward blockers into the live Schematics control notes after verification
- [x] add a dated reward update into [comms-log](comms-log.md)
- [x] separate proven reward behavior from product assumptions in one clean summary
- [x] produce a reward go or no-go recommendation for demo use
- [x] hand off exact next reward actions to Lead

### DEV_1 Reward Audit Result | 2026-04-10

- no live reward or referral code path exists in the current workspace
- auth and data blockers are real, but the larger blocker is that the reward implementation itself is absent
- reward page claims, referral API claims, ladder claims, and `coming soon` wording are documentation-only until code lands
- birthday rewards, placeholder achievements, perk redemption, and manager/admin reward visibility are not proven in runtime code
- reward/referral is a `NO-GO` for the live demo script until it has an actual implementation to verify

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

### DEV_3 Checkpoint - 2026-04-10

- [x] current progress, git diff, and latest comms were checked before doc edits
- [x] Microsoft Demo Day hub and folder index were aligned with the locked safe route and readiness story
- [x] the countdown baseline was kept honest about `Orch-only` versus owner-blocked `KasiLink`
- [x] the Orch Demo Script and owner checklist remained synced with the current UI route and blocker wording
- [x] `SA Startup Week Demo` stayed marked as the target story
- [x] `Azure Demo Day Playbook` was kept framed as a readiness story
- [x] a dated comms-log checkpoint was written with the contradiction that was fixed
- [x] historical notes were preserved while current-date overrides remained in place
- [ ] next-session start-here summary should be prepared if the date rolls over

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

- [ ] finish current overlapping edits already present in git status
- [ ] publish a short handoff note for changed files and intended next actions
- [x] confirm current lane is mainly site-url/env normalization and nav/search cleanup
- [x] confirm parallel lane did not touch untracked Session 3 docs or `lib/bookingSlots.js`
- [ ] confirm whether any deeper reward/referral changes are intended beyond share URL normalization

Known active file set:
- `Schematics/04-Updates/Project Status.md`
- `Schematics/06-Reference/Open Issues.md`
- `app/api/referral/route.js`
- `app/api/rss/route.js`
- `app/layout.jsx`
- `app/robots.js`
- `app/sitemap.js`
- `components/BottomNavbar.jsx`
- `components/SearchModal.jsx`
- `lib/config/env.js`
- `lib/constants.js`
- `lib/integrations/stripe.js`
- `lib/notificationSender.js`
- `lib/sendBookingConfirmation.js`
- `package.json`

Next:
- complete feature/code lane safely
- verify centralized `SITE_URL` behavior across metadata, RSS, robots, sitemap, Stripe, email, and referral links
- verify search modal and bottom navbar route-change behavior after refactor
- avoid editing Session 3 coordination notes unless reconciling with this board

### `BLUE` User / Client

- [ ] decide when overlapping code lane is stable enough for merge/review
- [ ] provide or activate any blocked external access still needed
- [ ] approve reward-system completion scope if it expands beyond current UX/API

## Priority Work Still Open

### `RED` External / Access Blockers

- [ ] valid Clerk publishable key and secret key for live rehearsal
- [ ] Atlas allowlist access for the current dev machine
- [ ] RapidAPI access/subscription for `whatsapp-osint`
- [ ] RapidAPI access/subscription for `google-search74`
- [x] install Azure CLI `az` after Session 3
- [x] install Azure Developer CLI `azd` after Session 3
- [ ] complete `az login` and `azd auth login`
- [ ] add Azure OpenAI, App Insights, and hosting env/resource values

### `AMBER` Reward System

- [x] reward page exists
- [x] rewards API exists
- [x] referral data model exists on `User`
- [x] referral API exists with `GET` and `POST` handlers
- [x] 5-level referral point ladder is implemented in code
- [ ] verify `/api/referral` end-to-end with real authenticated users after parallel lane stabilizes
- [ ] replace placeholder achievements with real tracked signals
- [ ] verify perk redemption logic and manager/admin visibility
- [ ] verify rewards copy, progression rules, and data truth against bookings/history
- [ ] review birthday reward interaction with `referralPoints` and confirm product intent
- [ ] review manager dashboard messaging where rewards/profile still says "coming soon"
- [ ] add reward-system QA checklist to admin/handoff docs once code lane is stable

### `AMBER` QA / Product Safety

- [x] confirm current working tree is buildable with active parallel lane
- [x] confirm lint currently passes with warnings only and no hard errors in the parallel report
- [x] confirm the live Orch API mount path is `/api/kasilink/*`
- [x] align `KasiLink` Orch proxy routing with the mounted upstream path
- [x] allow public `GET` bridge access for the home-page Orch dashboard and load-shedding widgets
- [x] confirm the booking/court change set passes targeted eslint with no warnings
- [x] confirm court detail routes can fall back to seeded local court data during Mongo outages
- [x] confirm the latest safe-lane warning-reduction files pass targeted eslint cleanly
- [x] confirm the second safe-lane warning batch reduced the combined lint report to `56` warnings
- [ ] reduce existing lint warning backlog now that `next build` is linting again
- [ ] run a real in-app demo rehearsal once valid Clerk keys are present
- [ ] confirm Mongo-backed writes once Clerk and Atlas access are live
- [ ] decide whether WhatsApp delivery is required in the demo script now that Orch reports `whatsapp_bridge_configured: false`
- [ ] full authenticated manager mutation sweep
- [ ] full authenticated admin mutation sweep
- [ ] confirm popup preference toggle fix end-to-end
- [ ] confirm mobile dimensions and macOS menu fixes on real breakpoints
- [ ] confirm local fixtures redesign parity against live fixtures standard
- [ ] visually approve the regenerated court imagery on live court pages
- [ ] verify service worker cache rollover serves the new court assets on real devices

### `BLUE` Documentation / Handoff

- [x] create Session 3 start-here note
- [x] create collaboration split note
- [x] create reward-system status note
- [x] mirror Session 3 notes to external `Schematics`
- [x] reconcile Session 3 notes back into existing top-level status files after parallel lane ends

## Session 3 Checkpoints

- [x] Session 3 bootstrap started
- [x] `STRUCTURE` reviewed for current state
- [x] reward-system state audited at code level
- [x] master board created
- [x] current working tree build verified
- [x] 4-tier audit pack added
- [x] court media refresh and hourly booking pass implemented
- [x] fallback court detail route support added for local/offline data mode
- [x] safe-lane warning cleanup checkpoint added
- [x] second safe-lane warning cleanup checkpoint added
- [x] Orch bridge mount path verified and app proxy aligned
- [ ] ownership board reconciled with Codex App output
- [ ] reward lane resumed safely
- [ ] merge/review checkpoint logged
