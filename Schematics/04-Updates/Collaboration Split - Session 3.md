# Collaboration Split - Session 3

> [!important]
> Historical Session 3 lane split.
> Use [Now](../00-Home/Now.md), [task-board](task-board.md), and current git status for live coordination. This overlap list is preserved as a session artifact, not as the current active control note.

## Historical Safe Split

- `Codex Terminal`: documentation, handoff, audits, safe non-overlapping work
- `Codex App`: active product/config/runtime file edits already present in repo status

## Rule

Do not overwrite active parallel edits until ownership is reconciled.

## Historical Parallel File Set

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

Plus two live documentation files:

- `Schematics/04-Updates/Project Status.md`
- `Schematics/06-Reference/Open Issues.md`

## Current Repo Reality Check Against The Historical Snapshot

- `2026-04-08` verification against the current `KasiLink` repo could not reproduce this file set.
- The current app tree is TypeScript-first and uses paths such as `app/layout.tsx`, `app/api/gigs/route.ts`, `components/Navbar.tsx`, and `lib/db.ts`.
- The listed overlap paths appear to belong to a different or older app snapshot than the repo currently available in `Introduction to MCP/KasiLink`.
- Until the source repo for the older file list is identified, treat the above overlap set as a stale handoff artifact rather than a live collision in the current repo.

## Safe Boundary After Reconciliation

- `Codex Terminal`: Schematics, audit notes, countdown planning, blocker documentation, rehearsal evidence, and verification against the current `KasiLink` repo
- Current `KasiLink` code edits should stay limited to changes that are directly supported by the present tree and verified against local repo status

## Observed Functional Scope

- centralizing `SITE_URL` and canonical origin handling
- normalizing metadata, RSS, robots, sitemap, Stripe, email, and referral links
- refactoring search modal and bottom navbar route-reset behavior
- restoring linted build behavior in `package.json`
