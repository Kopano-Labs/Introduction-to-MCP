---
title: Orch Demo Task List - 2026-04-08
created: 2026-04-08
updated: 2026-04-08
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

## Current Objective

Make the Orch GUI demo-safe by separating public and admin surfaces, turning Labs into a pressable function router, restoring visible logs, and proving the core flows work locally.

## Public Surface

- [x] split top-level navigation into `LIVE COUNCIL`, `ORCH LABS`, and `ADMIN PORTAL`
- [x] remove public session-vault exposure from the left rail
- [x] replace decorative Labs metrics with pressable function cards
- [x] define public section anchors for interfaces, cloud, actions, tools, forge, and console
- [x] add a public activity preview to the sidebar
- [x] add a public recent-activity section to Labs
- [x] keep Orch Forge interactive on the public surface
- [ ] verify the new public Labs layout reads cleanly on desktop

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
- [ ] verify that new live events actually appear in all three views during runtime

## Build And Verification

- [x] redesign the council view into a cleaner briefing-room layout
- [x] patch the Windows Orch CLI startup banner so local serve does not crash on emoji output
- [x] rebuild `orch/gui` cleanly after the public/admin split
- [x] restart Orch and refresh the served GUI bundle
- [ ] verify no JSX or CSS regressions on first load
- [ ] verify section-card scrolling works from every Labs function button
- [ ] verify Forge create, edit, and lane-move actions still work
- [ ] verify MCP Console send and stream still work

## Demo Readiness

- [ ] verify the public page no longer exposes internal planning language
- [ ] verify the admin page clearly reads as internal-only
- [ ] verify the live council never looks broken when idle
- [ ] verify a quiet websocket still leaves meaningful visible logs
- [ ] rehearse one public Labs walkthrough from top to bottom
- [ ] rehearse one admin login plus vault access walkthrough
- [ ] capture the next blocker after the first full GUI rehearsal
- [ ] decide whether any remaining surface needs fresh copy or tighter labeling

## Schematics And Handoff

- [x] create a dedicated Orch demo task list in `Schematics`
- [ ] update `Demo Countdown - April 8-15, 2026` with the Orch GUI split checkpoint
- [ ] update `dev-tracker.md` with the current GUI refactor status
- [ ] update `comms-log.md` with the public/admin separation decision
- [x] note the admin demo account in docs once verified
- [x] record the build result after the current TypeScript fix
- [x] record the runtime verification result after the next GUI restart
- [ ] commit the next clean Schematics checkpoint after verification
