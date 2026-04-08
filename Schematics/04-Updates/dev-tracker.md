# Dev Tracker

## Orch GUI Demo Split | 2026-04-08 22:10

- Orch GUI now splits into `LIVE COUNCIL`, `ORCH LABS`, and `ADMIN PORTAL`
- public Labs now uses pressable function cards for interfaces, cloud, actions, tools, forge, and console
- public session-vault exposure was removed from the sidebar and replaced with an internal-access lock note
- public Labs now shows recent activity and public operator-feed visibility instead of internal execution boards
- internal execution boards, Orch Code controls, creator throughput, and console analytics now sit behind the admin portal branch
- visible feed-log panels now exist in the sidebar, public Labs console, admin portal, and council view
- the live-feed handler type issue was fixed and `orch/gui` now passes `npm run build`
- local demo admin account `admin@orch.local` was registered and granted the `admin` role
- Orch was restarted on `127.0.0.1:8000` after the rebuild and `/api/kasilink/health` returned `200`
- `/auth/login` now returns the local demo admin with role `admin`
- `/broadcast` followed by `/updates` now returns the injected live event again, which confirms runtime feed flow after restart
- next verification gap is browser-level visual QA of the new public/admin split and section-card scroll behavior

## Demo Hardening Snapshot | 2026-04-08

- `KasiLink` dependencies were restored locally with `npm install`
- `KasiLink` now passes `npm run lint`
- `KasiLink` now passes `npm run build`
- Orch API is confirmed live on `/api/kasilink/health` and `/api/kasilink/dashboard`
- `KasiLink/app/api/orch/[...path]/route.ts` now normalizes upstream requests to the mounted `/api/kasilink/*` router
- public `GET` requests for the home-page Orch dashboard and load-shedding widgets are no longer blocked by app-side sign-in checks
- `KasiLink/.env.example` now includes `ORCH_BASE_URL` and `NEXT_PUBLIC_ORCH_BASE_URL`
- WebSocket support was added to the root `.venv` with `pip install websockets`
- direct Orch metrics currently report `"whatsapp_bridge_configured": false`
- live rehearsal in the web app is still blocked first by valid Clerk keys, then by reachable Mongo/Atlas access
- Chocolatey install attempts for `azure-cli` and `azd` are blocked in the current non-elevated shell by `C:\\ProgramData\\chocolatey` permissions

## Recent Commits

- `b8c2235` `session-3-court-refresh-and-4-tier-audits`
- `d85da42` `record-session-3-build-checkpoint`
- `9249309` `clarify-session-3-parallel-ownership`
- `7be1c95` `refine-session-3-reward-handoff`
- `0f1d03f` `add-session-3-reward-qa-checklist`
- `29bd592` `wire-session-3-vault-index`
- `ed13710` `session-3-coordination-layer`
- `3bdc468` `homepage-csp-hero-polish`
- `1fdba7a` `followup-external-access-blockers`
- `7781658` `followup-newsletter-mongo-resilience`
- `2b0eb74` `phase-14-obsidian-structure-and-ui-audit`
- `245907a` `phase-13-whatsapp-osint-admin-review`
- `a50416d` `phase-12-env-integrations-weather-search`
- `8ef6b3d` `phase-11-botid-anti-bot-hardening`
- `d13807e` `phase-10-security-hardening`

## Verification Pattern Used

- targeted eslint on touched files
- `npm run build`
- clean dev restart when phase risk touched route/build state
- smoke checks on changed public routes

## Session 3 Verification

- current combined working tree completed `npm run build` successfully on `2026-04-08`
- `next build` is linting again because the parallel lane restored the normal build script
- build currently passes with a sizable warning backlog, not hard lint errors
- data access during build still surfaces the known Atlas allowlist blocker, but the site falls back instead of failing the build
- parallel Codex report confirms `npm run lint` passes with `73 warnings` and `0 errors`
- parallel Codex report confirms `npm run build` passes and did not touch untracked Session 3 docs or `lib/bookingSlots.js`
- latest safe-lane verification shows `npm run lint` now passes with `56 warnings` and `0 errors` on the combined tree
- booking/court lane targeted eslint now passes with `0` warnings and `0` errors
- targeted eslint for the safe warning-reduction files also passes with `0` warnings and `0` errors
- second safe-lane warning-reduction batch passes targeted eslint with `0` warnings and `0` errors
- court media files were regenerated at `2026-04-08 18:41` and service-worker cache version was bumped
- hourly booking selection is now enforced in UI and booking APIs for create, guest reserve, and edit flows
- `app/courts/[id]/page.jsx` now falls back to seeded local courts when Mongo is unavailable or the route uses a local fallback id
- `components/GiscusComments.jsx` readiness logic was corrected so env validation no longer trips the linted build path
- second safe-lane cleanup removed unused variables and dead parameters in tournament/admin/profile/analytics utility routes and form pages

## Local Dev Notes

- port `3002` is the normal dev port
- `.next` should be cleared if Next dev starts surfacing manifest or stale build artifacts
- `.next-dev-phase*.log` files were only temporary local debugging artifacts and should not remain in the repo root once the debugging pass is complete
- local Mongo auth is no longer blocked by SRV resolution, but it is still blocked if Atlas has not allowlisted the current machine IP
- Google Search74 and WhatsApp OSINT provider wiring is in place, but live verification currently fails with `403` until the RapidAPI account has access to those APIs

## Orch GUI Redesign Checkpoint | 2026-04-09 01:03

- public Orch GUI now uses a sticky top navigation instead of the old left-rail shell
- public hero states for `LIVE COUNCIL`, `ORCH LABS`, and `ADMIN PORTAL` now use larger editorial titles and motion-led background styling
- public activity preview was removed from the public shell and kept inside admin-only views
- public console now keeps results and analytics visible without exposing the internal operator feed
- admin now exposes activity preview plus session-vault access for forensic replay
- `orch/gui/src/App.tsx` and `orch/gui/src/App.css` were refactored for the redesign pass
- `orch/gui` passes `npm run build` after the redesign
- runtime refresh on `127.0.0.1:8000` is still the next verification step

## Orch Runtime Refresh | 2026-04-09 01:06

- `orch serve api --host 127.0.0.1 --port 8000` was relaunched locally
- root GUI request on `http://127.0.0.1:8000` returns `200`
- `http://127.0.0.1:8000/api/labs/overview` returns `200`
- server logs show the rebuilt JS/CSS assets being served after the redesign build
- next remaining checks are browser-level visual QA and live interaction QA

## Orch Live Smoke Pass | 2026-04-09 01:08

- `POST /auth/login` succeeds for `admin@orch.local` and returns role `admin`
- `GET /sessions` returns the archived session list
- `GET /api/labs/cowork/rooms` returns the persisted Forge rooms
- `POST /api/labs/mcp-console/chat` returns a valid Orch guidance payload
- live browser click-path QA is still pending even though the API smoke path is healthy
