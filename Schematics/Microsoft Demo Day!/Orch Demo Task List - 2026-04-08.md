---
title: Orch Demo Task List - 2026-04-08
created: 2026-04-08
updated: 2026-04-09
author: Codex
tags:
  - orch
  - demo
  - tasks
  - gui
priority: critical
status: active
---

# Orch Demo Task List - 2026-04-08

> Hub: [Microsoft Demo Day!](index.md)
> Owner decisions: [Owner Must Handle - Microsoft Demo Day](Owner%20Must%20Handle%20-%20Microsoft%20Demo%20Day.md)

## Current Objective

Turn Orch into a demo-grade public AI surface with a Claude plus Codex feel, a younger South African audience fit, a clean top navigation shell, a distinct admin layer, and working demo-level interactions that can be rehearsed live.

## April 8 Closeout

- functional April 8 blocker-removal work is complete on the Codex side
- the remaining April 8 gap is outside the GUI shell and sits in owner-supplied Clerk plus Atlas access for the wider KasiLink path
- the unchecked items below now belong to April 9 polish, copy, research, or owner decisions rather than core April 8 functional breakage

## Active Direction

- [x] keep the public and admin split introduced on 2026-04-08
- [x] confirm that public activity preview should move out of the public shell and remain admin-only
- [ ] finish current-market research on youth-facing AI UX signals and competition relevant to South Africa
- [x] convert the existing left-rail shell into a top-nav information architecture
- [x] replace dashboard-like filler cards with clearer primary actions and demo routes
- [x] upgrade the visual language to a fresher motion-led, mobile-first presentation
- [x] keep functional surfaces real enough for demo rather than shipping only cosmetic mockups

## Information Architecture

- [x] define the new top navigation for `LIVE COUNCIL`, `ORCH LABS`, `FORGE`, `CONSOLE`, and `ADMIN`
- [x] decide which public sections stay on one page versus move behind section switching
- [x] convert current Labs section buttons into a cleaner navigation or dropdown pattern
- [x] remove leftover sidebar dependency from the public shell
- [x] keep session vault access exclusively inside admin-authenticated views
- [x] move activity preview and operator history fully into the admin surface
- [x] make the public hero read like a product landing shell, not an internal control room

## Visual Redesign

- [x] introduce a slicker display font pairing that still renders reliably on Windows and the web
- [x] enlarge hero titles so they fill the available space without breaking mobile layout
- [x] add a fluid moving background that feels intentional rather than noisy
- [x] blend Claude-style calm spacing with Codex-style precision and operator cues
- [x] tune colors and contrast for a younger South African audience without looking juvenile
- [x] make cards, buttons, chips, and navigation feel consistent across council, labs, and admin
- [ ] ensure the public surface still looks good when the live feed is quiet

## Public Experience

- [x] rewrite public copy so it speaks to creators, learners, and operators rather than internal staff
- [x] give the public home state a clear primary call to action
- [x] make every major public feature pressable and visually obvious
- [x] keep Forge usable from the public layer if it is part of the demo story
- [x] keep Console usable from the public layer if it is part of the demo story
- [x] remove or soften internal planning language from public labels
- [ ] check that the page feels clean enough that users do not notice section changes as jarring context switches

## Admin Experience

- [x] make the admin portal visibly internal-only from the first screen
- [x] keep admin login in a distinct visual system from the public shell
- [x] preserve working access to session vault, logs, analytics, and execution boards
- [x] ensure activity preview appears only inside admin
- [x] verify admin views still expose the live feed, vault, and internal execution summaries clearly

## Working Functionality

- [x] verify live council updates still render after the shell redesign
- [x] verify Labs navigation still reaches interfaces, cloud, actions, tools, forge, and console
- [x] verify Forge create, edit, and lane-move actions still work after layout changes
- [x] verify MCP Console send and stream still work after layout changes
- [x] verify admin login still works after layout changes
- [x] verify session loading and audit mode still work after layout changes
- [x] verify live logs still show in the correct internal surfaces
- [x] verify the public shell does not expose admin-only data when not logged in

## Public Surface

- [x] split top-level navigation into `LIVE COUNCIL`, `ORCH LABS`, and `ADMIN PORTAL`
- [x] remove public session-vault exposure from the left rail
- [x] replace decorative Labs metrics with pressable function cards
- [x] define public section anchors for interfaces, cloud, actions, tools, forge, and console
- [x] remove public activity preview from the public shell and keep operator history inside admin
- [x] keep public live context inside the Console surface instead of a generic recent-activity panel
- [x] keep Orch Forge interactive on the public surface
- [x] verify the new public Labs layout reads cleanly on desktop
- [x] retire the old sidebar-based public shell in favor of the redesign

## Admin And Auth

- [x] add an `ADMIN PORTAL` route in the GUI state model
- [x] add admin login form state to the GUI
- [x] move internal execution boards behind the admin branch
- [x] move Orch Code controls behind the admin branch
- [x] move creator throughput and console analytics behind the admin branch
- [x] fix the current TypeScript error in the live-feed handler
- [x] seed a local demo admin account if it does not already exist
- [x] verify admin login against the live Orch auth endpoint

## Logs And Runtime

- [x] add a persistent in-memory feed log model to the GUI
- [x] attach websocket events to the feed log
- [x] attach polled `/updates` events to the feed log
- [x] add explicit system log entries for room boot and operator actions
- [x] render a visible live-feed log in the public console section
- [x] render a visible live-feed log in the council view
- [x] render a visible operator log in the admin view
- [x] verify `/broadcast` to `/updates` event flow still works after the redesign
- [x] verify that new live events actually appear in all three views during runtime

## Build And Verification

- [x] redesign the council view into a cleaner briefing-room layout
- [x] patch the Windows Orch CLI startup banner so local serve does not crash on emoji output
- [x] rebuild `orch/gui` cleanly after the public/admin split
- [x] restart Orch and refresh the served GUI bundle
- [x] verify no JSX or CSS regressions on first load
- [x] verify section-card scrolling works from every Labs function button
- [x] verify Forge create, edit, and lane-move actions still work
- [x] verify MCP Console send and stream still work
- [x] rebuild `orch/gui` cleanly after the full-shell redesign
- [x] restart Orch and confirm the served GUI reflects the redesign bundle
- [x] smoke-check root GUI, Labs overview, session vault endpoint, Forge room list, and admin login on the live server
- [x] run a browser-level visual pass on desktop and mobile-width layouts

## Demo Readiness

- [ ] verify the public page no longer exposes internal planning language
- [ ] verify the admin page clearly reads as internal-only
- [ ] verify the live council never looks broken when idle
- [ ] verify a quiet websocket still leaves meaningful visible logs
- [x] rehearse one public Labs walkthrough from top to bottom
- [x] rehearse one admin login plus vault access walkthrough
- [x] capture the next blocker after the first full GUI rehearsal
- [ ] decide whether any remaining surface needs fresh copy or tighter labeling
- [ ] decide whether any non-working section should be hidden for demo day rather than shown half-ready

## Routed Page Split And Motion Pass

- [x] split the top nav surfaces into their own routed pages instead of one long mixed shell
- [x] rebuild `LIVE COUNCIL` as its own presentation page with a deliberate idle state
- [x] rebuild `ORCH LABS` as its own overview page with proof-first cards and quick launches
- [x] rebuild `FORGE` as its own focused execution page
- [x] rebuild `CONSOLE` as its own split-pane interaction page
- [x] rebuild `ADMIN` as its own clearly internal-only page
- [x] add a persistent Framer Motion background and page-transition system
- [x] rerun build, live runtime, and browser QA after the routed split lands

## Schematics And Handoff

- [x] create a dedicated Orch demo task list in `Schematics`
- [x] update this task list as each redesign milestone lands
- [x] update `Demo Countdown - April 8-15, 2026` with the Orch GUI split checkpoint
- [x] update `dev-tracker.md` with the current GUI refactor status
- [x] update `comms-log.md` with the public/admin separation decision
- [x] note the admin demo account in docs once verified
- [x] record the build result after the current TypeScript fix
- [x] record the runtime verification result after the next GUI restart
- [x] commit the next clean Schematics checkpoint after verification

## Current Blocker

- full GUI interaction blockers are cleared as of `2026-04-09 07:23`
- locked Orch-only rehearsal paths now exist for public and admin as of `2026-04-09 08:15`
- new routed shell and motion layer are verified as of `2026-04-09 18:18`
- April 8 functional work is closed on the Codex side
- next blocker is product polish plus routed-shell click-path rehearsal: tighten copy, rerun the full public/admin demo through the new pages, and connect the Orch-only script back to the wider KasiLink demo story
