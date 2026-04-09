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
