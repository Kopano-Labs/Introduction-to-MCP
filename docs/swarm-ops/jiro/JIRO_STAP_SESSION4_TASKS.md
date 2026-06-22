# JIRO STAP SESSION 4 — 50 HARD TASKS

> **Authority:** AG (CF) — Seat 10 — STAP TEACHER
> **Student:** Jiro (AWS) — Junior RTC — STAP STUDENT
> **ALP:** #168 | `a5b0d9841f8ec9f4`
> **Date Assigned:** 2026-06-22T06:33 SAST
> **Repo:** `Kopano-Labs/Introduction-to-MCP` (unless task specifies another)
> **Branch:** `jiro/stap-session4` — DO NOT push to master
> **Log:** Every completion → `NOW.md` with timestamp, 4Ws, commit hash, POC verdict
> **Constraint:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`
> **Scripture:** *"The one who is faithful in very little is also faithful in much."* — Luke 16:10

---

## STAP RULES — READ BEFORE TASK 1

- [ ] Assert `I_AM_STATELESS_RENTER_NOT_LANDLORD` before every task
- [ ] Log every completion in `NOW.md` — no exceptions
- [ ] Push every commit to `jiro/stap-session4` — NEVER to master
- [ ] Every commit message must include `AG_OPINION:` and `RTC_OPINION:`
- [ ] KHELOS pre-commit hook must pass — no bypassing with `--no-verify`
- [ ] If BLOCKED → log in `NOW.md` and stop. Do not hallucinate

---

## PRIORITY 0 — SECURITY (Do First — No Exceptions)

### TASK 001 — Patch Dependabot HIGH CVE on Introduction-to-MCP
- **Repo:** `Kopano-Labs/Introduction-to-MCP`
- **Task:** Go to GitHub → Security → Dependabot alerts → resolve the 1 HIGH severity CVE. Apply the suggested fix (version bump or override). Test that nothing breaks. Push
- **Deliverable:** Commit with CVE number in message + NOW.md entry
- **POC standard:** Zero HIGH CVEs remaining after this task
- **Hard part:** The fix must not break `73/73 unit tests`. Run them after patching

### TASK 002 — Patch all 4 remaining Dependabot CVEs (moderate + low)
- **Repo:** `Kopano-Labs/Introduction-to-MCP`
- **Task:** Resolve the 2 moderate and 2 low CVEs from Dependabot. Check each one — some may already be fixed by Task 001. For each remaining: apply the fix, verify nothing breaks, push
- **Deliverable:** All Dependabot alerts cleared on the branch
- **Hard part:** Some fixes may conflict with each other. Resolve in sequence, not parallel

### TASK 003 — Audit `kopano-core/requirements.txt` or `setup.py` for unpinned deps
- **Task:** Check every Python dependency. Any unpinned dep (e.g. `requests` with no version) is a security vector. Pin ALL deps to specific versions with hash verification where possible
- **Deliverable:** Updated requirements file with all deps pinned + `pip-audit` or `safety` report
- **Hard part:** Some pinned versions may conflict. Document every conflict in NOW.md

### TASK 004 — Verify KHELOS pre-commit hook fires correctly on ALL file types
- **Task:** Test the pre-commit hook against: Python files, markdown files, JSON files, YAML files, HTML files. Confirm it blocks FOC signals in each type. Document results
- **Deliverable:** Test script + results table in NOW.md
- **Hard part:** The hook may only cover Python. Extend it if it doesn't cover YAML and HTML

### TASK 005 — Add `SECURITY.md` to Introduction-to-MCP
- **Task:** Create `SECURITY.md` with: responsible disclosure policy, CVE reporting email, KPGS governance gate for security patches, KHELOS firewall note, Dependabot policy
- **Deliverable:** `SECURITY.md` committed and pushed
- **Hard part:** Must align with KPGS governance — no vanilla GitHub template

---

## PRIORITY 1 — DEPLOYMENT PIPELINE

### TASK 006 — Create `jiro/stap-session4` branch and push it
- **Task:** Create the branch from current HEAD of `codex/kc-sovereign-gui-full-dev`. All your work goes here. This is your working branch for all 50 tasks
- **Deliverable:** Branch exists on remote + NOW.md entry
- **Hard part:** Branch must be based on the right HEAD — verify with `git log --oneline -3`

### TASK 007 — Smoke-test `deploy-web.yml` locally using `act`
- **Task:** Install `act` (GitHub Actions local runner). Run `deploy-web.yml` in dry-run mode against the local `public/` directory. Document what passes and what fails
- **Deliverable:** `act` output log in `docs/swarm-ops/jiro/deploy_test_log.txt` + NOW.md entry
- **Hard part:** `act` needs Docker. If Docker is not available, document why and propose an alternative

### TASK 008 — Validate all HTML files pass W3C validation
- **Task:** Run W3C HTML validation on: `public/index.html`, `public/careers/index.html`, `public/protocols/index.html`, `KasiLink/index.html`. Fix any errors found
- **Deliverable:** Zero W3C errors on all 4 files + NOW.md entry with error count before/after
- **Hard part:** Some errors may be in generated content. Fix at the root, not with suppression

### TASK 009 — Add `robots.txt` and `sitemap.xml` to `public/`
- **Task:** Create `public/robots.txt` (allow all, disallow `/admin/`) and `public/sitemap.xml` listing all public pages: `kopanolabs.com`, `kopanolabs.com/careers/`, `kopanolabs.com/protocols/`, `kopanolabs.com/starfall/`. Use correct XML sitemap format with `<lastmod>` dates
- **Deliverable:** Both files committed + NOW.md entry
- **Hard part:** sitemap must have correct canonical URLs — not localhost

### TASK 010 — Add `humans.txt` to `public/` with KPGS team credits
- **Task:** Create `public/humans.txt` with: SSE credit, AG (CF) credit, RTC council members listed, build tools used, KPGS governance version, ALP hash
- **Deliverable:** `humans.txt` committed + NOW.md entry
- **Hard part:** Format must follow humanstxt.org standard

### TASK 011 — Add GitHub Actions badge to `README.md`
- **Task:** Add the `deploy-web.yml` workflow status badge to the root `README.md` of `Introduction-to-MCP`. Also add KPGS governance badge (custom shield.io badge: `KPGS | ALP#168 | POC_VALIDATED`)
- **Deliverable:** README with badges committed + NOW.md entry
- **Hard part:** Workflow badge URL must point to the correct workflow file and branch

### TASK 012 — Add `404.html` to `public/`
- **Task:** Create a branded `404.html` for KopanoLabs.com. Must match the aesthetic of `public/index.html` — dark background, particle effect if lightweight, KPGS branding, link back to home. Must NOT use React or any framework
- **Deliverable:** `public/404.html` committed + NOW.md entry
- **Hard part:** 404 page must be self-contained — single HTML file, no external dependencies except Google Fonts

### TASK 013 — Create `public/starfall/index.html` placeholder
- **Task:** StarFallSalvage is referenced in the sitemap and nav but the subdirectory may be empty. Create a branded holding page for `public/starfall/index.html` — same aesthetic as the hub, shows "Coming Soon — Starfall Salvage", B2B lead capture email field, links back to `kopanolabs.com`
- **Deliverable:** `public/starfall/index.html` committed + NOW.md entry
- **Hard part:** Must be single-file HTML. Must have a working email capture form that logs to localStorage (no backend)

---

## PRIORITY 2 — GSMB GOVERNANCE ENGINE

### TASK 014 — Run `73/73` unit tests and document current pass rate
- **Task:** Navigate to `kopano-core/`. Run `python -m pytest kopano/test_khelos_and_apu.py -v`. Document: total tests, pass count, fail count, any errors. If anything fails — do NOT fix it yet. Document and flag for SSE
- **Deliverable:** Test output log in `docs/swarm-ops/jiro/test_run_log.txt` + NOW.md entry
- **Hard part:** Tests may have environment dependencies. Document every dependency error

### TASK 015 — Write 5 new unit tests for `gsmb_auto_runner.py`
- **Task:** The auto runner has tests but they may be thin. Write 5 new tests covering: (1) tick produces a verdict, (2) tick fails gracefully if NCCNP errors, (3) ALP receipt is generated, (4) IKP log is written, (5) FON-C audit runs
- **Deliverable:** 5 new tests in `kopano-core/kopano/test_gsmb_auto_runner.py` + all passing + NOW.md
- **Hard part:** Tests must be DETERMINISTIC — no random seeds, no time-dependent assertions

### TASK 016 — Write 5 new unit tests for `fon_c_engine.py`
- **Task:** Write 5 new tests covering FON-C edge cases: (1) clean signal returns L0, (2) self-referential FOC returns L5, (3) nested self-reference detected, (4) clean signal after dirty signal does not inherit dirty state, (5) audit log entry is written per call
- **Deliverable:** 5 new tests in existing or new test file + all passing + NOW.md
- **Hard part:** FON-C state must be isolated per test — no cross-test contamination

### TASK 017 — Add PKAP score to NCCNP tick output
- **Task:** The `gsmb_auto_runner.py` tick output shows `4/4 POC_CLOSED` but not the PKAP avg. Add PKAP average to the tick log output and to the JSON receipt
- **Deliverable:** Modified `gsmb_auto_runner.py` with PKAP in tick + NOW.md + commit
- **Hard part:** PKAP formula: `{(POC - FOC) × [POCvsFOC]}` — implement correctly from MMAO spec

### TASK 018 — Add `breach_count` to NCCNP tick output
- **Task:** Current tick shows hash and verdict. Add `breach_count` (from ALP state) and `poc_receipt_count` to every tick's JSON output for full governance visibility
- **Deliverable:** Modified runner output + NOW.md + commit
- **Hard part:** Must read ALP state file without causing ALP activation (read-only access)

### TASK 019 — Create `docs/swarm-ops/jiro/JIRO_STAP_LEDGER.json`
- **Task:** Create a JSON ledger for all Jiro STAP sessions. Schema: `{ "agent": "jiro", "rtc_seat": "junior", "sessions": [], "total_tasks_completed": 0, "total_poc_receipts": 0, "breach_count": 0, "save_candidate": true }`. This is Jiro's governance ledger — it grows with every session
- **Deliverable:** Valid JSON file committed + NOW.md entry
- **Hard part:** Schema must be versioned — add `"schema": "jiro_stap_ledger_v1"`

### TASK 020 — Verify Task Scheduler `GSMB_AutoRunner_25min` is firing
- **Task:** Run `Get-ScheduledTask -TaskName "GSMB_AutoRunner_25min" | Select-Object State, LastRunTime, NextRunTime`. Document the output. If State is not `Ready` or `Running` — document exactly why and what Admin steps are needed
- **Deliverable:** PowerShell output in NOW.md + status verdict (RUNNING / BLOCKED_NEEDS_ADMIN)
- **Hard part:** If it needs Admin — write the exact Admin PowerShell command needed in NOW.md for SSE tonight

---

## PRIORITY 3 — CRISISCONNECT PWA

### TASK 021 — Add offline fallback page to CrisisConnect
- **Repo:** `c:\Users\rkhol\CrisisConnect\` (its own repo)
- **Task:** The `sw.js` may have a basic offline fallback. Verify it. If the fallback is a blank screen — replace it with a proper offline page that shows: "CrisisConnect is offline. Your data is safe. Connect to sync." — styled to match `index.css`
- **Deliverable:** Updated `sw.js` + `offline.html` (if needed) + commit to CrisisConnect repo + NOW.md
- **Hard part:** The service worker cache must include the offline page in its precache list

### TASK 022 — Add `manifest.json` screenshots to CrisisConnect
- **Task:** The `manifest.json` has `"screenshots": []`. Add at least 2 screenshots — a desktop screenshot and a mobile screenshot. Screenshots can be placeholder SVGs if real screenshots are not available. Include correct `form_factor` and `label` fields
- **Deliverable:** Updated `manifest.json` + placeholder screenshot files + commit to CrisisConnect repo
- **Hard part:** Screenshot format must follow PWA manifest spec — check Chrome's PWA install requirements

### TASK 023 — Add `theme-color` meta tag to CrisisConnect `index.html`
- **Task:** Verify `<meta name="theme-color" content="#0a0e1a">` is in `index.html`. If not — add it. Also add `<meta name="apple-mobile-web-app-capable" content="yes">` and `<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">`
- **Deliverable:** Updated `index.html` + commit to CrisisConnect repo + NOW.md
- **Hard part:** Verify the changes don't break the existing PWA install on mobile

### TASK 024 — Add CSP (Content Security Policy) header to CrisisConnect
- **Task:** Add a `<meta http-equiv="Content-Security-Policy">` header to CrisisConnect `index.html`. Policy must: allow self, block inline scripts except existing ones (use nonce or hash), block eval, allow Google Fonts CDN
- **Deliverable:** CSP header added + no console errors + commit + NOW.md
- **Hard part:** CSP must NOT break the existing app.js functionality. Test every feature after adding

### TASK 025 — Audit CrisisConnect `app.js` for console.log statements
- **Task:** Search `app.js` for all `console.log`, `console.warn`, `console.error` calls. In production code — `console.log` is FOC (leaks information, wastes cycles). Replace with a conditional logger that only fires in dev mode. Document how many were found
- **Deliverable:** Modified `app.js` with conditional logger + commit + NOW.md (count before/after)
- **Hard part:** Some console.error calls may be legitimate error reporting — keep those, remove the noise

### TASK 026 — Add `CHANGELOG.md` to CrisisConnect repo
- **Task:** Create `CHANGELOG.md` following Keep a Changelog format. Document all known versions based on git log: what was added, what changed, what was fixed. Go back to the first commit
- **Deliverable:** `CHANGELOG.md` committed to CrisisConnect repo + NOW.md
- **Hard part:** Must reconstruct changes from git log — do not invent changes. `git log --oneline` is your source of truth

### TASK 027 — Add `.editorconfig` to CrisisConnect repo
- **Task:** Create `.editorconfig` that enforces: 2-space indent for HTML/CSS/JS, LF line endings, UTF-8, trim trailing whitespace, final newline. Then run `editorconfig-checker` (install if needed) and fix any violations
- **Deliverable:** `.editorconfig` + no violations + commit + NOW.md
- **Hard part:** `app.js` at 32KB may have mixed indentation. Fix it systematically, not randomly

---

## PRIORITY 4 — KASILINK PLATFORM

### TASK 028 — Add `<link rel="canonical">` to KasiLink `index.html`
- **Task:** Add `<link rel="canonical" href="https://kasilink.com/">` to the head of `KasiLink/index.html`. Also add Open Graph tags: `og:title`, `og:description`, `og:url`, `og:type`, `og:image` (use a placeholder if no image exists)
- **Deliverable:** Updated `KasiLink/index.html` + commit + NOW.md
- **Hard part:** `og:image` must be an absolute URL. If no image exists — create a placeholder SVG at `KasiLink/og-image.svg` and reference it

### TASK 029 — Add structured data (JSON-LD) to KasiLink
- **Task:** Add `<script type="application/ld+json">` to `KasiLink/index.html` with `LocalBusiness` or `Organization` schema. Include: name (KasiLink), url, description, address (South Africa), areaServed
- **Deliverable:** Valid JSON-LD in KasiLink + commit + NOW.md
- **Hard part:** Validate with Google's Rich Results Test tool. Document the test result

### TASK 030 — Add a `privacy.html` page to KasiLink
- **Task:** Create `KasiLink/privacy.html` — a privacy policy page matching the KasiLink aesthetic. Policy must cover: what data is stored (KCC transactions, gig listings), where it is stored (localStorage offline-first), who sees it, how to delete it, POPIA compliance note
- **Deliverable:** `privacy.html` committed + link added to KasiLink footer + NOW.md
- **Hard part:** POPIA compliance — South Africa's data protection law. Research at least 3 POPIA requirements and reflect them in the policy

### TASK 031 — Performance audit `KasiLink/index.html`
- **Task:** Run Lighthouse audit on the KasiLink page (use local server). Document scores: Performance, Accessibility, Best Practices, SEO. Any score below 80 — identify the top 3 causes and fix at least 1
- **Deliverable:** Lighthouse scores documented in NOW.md + at least 1 fix committed
- **Hard part:** Performance fixes must not break the visual design

---

## PRIORITY 5 — KOPANOLABS.COM HUB

### TASK 032 — Add `<link rel="preload">` for critical fonts to `public/index.html`
- **Task:** The hub loads Google Fonts. Add `<link rel="preload">` hints for the critical font files to reduce render-blocking time. Measure load time before and after with DevTools Network tab
- **Deliverable:** Updated `public/index.html` + before/after load time in NOW.md + commit
- **Hard part:** Must identify which specific font variants are critical (used above the fold) and only preload those

### TASK 033 — Add a `loading="lazy"` attribute to all non-critical images in `public/`
- **Task:** Audit all `<img>` tags across `public/index.html`, `public/careers/index.html`, `public/protocols/index.html`. Add `loading="lazy"` to images below the fold. Add `width` and `height` attributes to prevent layout shift
- **Deliverable:** All qualifying images updated + commit + NOW.md
- **Hard part:** Must NOT add lazy loading to above-the-fold images (first viewport) — those should load eagerly

### TASK 034 — Add a print stylesheet to `public/protocols/index.html`
- **Task:** The KPGS Protocol Telemetry page (`protocols/index.html`) should be printable — for RTC meetings. Add `@media print` CSS that: removes nav, removes animations, makes text black-on-white, expands collapsed sections, adds page numbers
- **Deliverable:** Print CSS added + commit + NOW.md
- **Hard part:** Print CSS must not interfere with screen rendering

### TASK 035 — Add `aria-label` attributes to all interactive elements in `public/index.html`
- **Task:** Accessibility audit of `public/index.html`. Every button, link, and interactive element must have a descriptive `aria-label` if the visible text is insufficient. Document how many were missing
- **Deliverable:** Updated file + commit + NOW.md with count before/after
- **Hard part:** Must test with a screen reader or VoiceOver to confirm the labels make sense in context

### TASK 036 — Create `public/flows/index.html` — KPGS Protocol Flow Visualizer
- **Task:** Build a new page at `public/flows/index.html`. It shows the KPGS signal flow: `RAW → BRACKETED → INGRESSED → TESTED → ACCEPTED/DECLINED → SEALED` as an animated step-by-step diagram. Pure HTML/CSS/JS. Dark theme. No frameworks
- **Deliverable:** `public/flows/index.html` committed + NOW.md
- **Hard part:** Animation must be smooth (CSS transitions, not JS setInterval). Must be mobile responsive

---

## PRIORITY 6 — DOCUMENTATION

### TASK 037 — Write `docs/swarm-ops/jiro/STAP_STUDENT_GUIDE.md`
- **Task:** Write the STAP Student Guide for future junior renters joining KPGS. Document: what STAP is, the STAP rules, how to log in NOW.md, how to commit with RTC opinions, what POC vs FOC means in practice, how to handle blockers, the BREACH escalation process
- **Deliverable:** Guide committed + NOW.md entry
- **Hard part:** Guide must be written from a student perspective — not a teacher perspective. Write it as if you learned it the hard way

### TASK 038 — Update `docs/IONOS_DEPLOY_GUIDE.md` with IONOS FTP secret names screenshot path
- **Task:** Add a section to `IONOS_DEPLOY_GUIDE.md` that shows WHERE in GitHub to add secrets. Include the exact nav path: `GitHub → Settings → Secrets and variables → Actions → New repository secret`. Add a note about which secrets Jiro cannot add (IONOS credentials belong to SSE)
- **Deliverable:** Updated deploy guide + commit + NOW.md
- **Hard part:** The note about SSE-only secrets must be CLEAR — Jiro should not attempt to add IONOS credentials without SSE's login

### TASK 039 — Create `docs/swarm-ops/DEPLOYMENT_RUNBOOK.md`
- **Task:** Write a deployment runbook that covers the full deploy flow: local dev → KPGS gate → GitHub Actions → IONOS FTP → verification. Include: pre-deploy checklist, what to do if deploy fails, rollback procedure (FTP restore), post-deploy verification steps
- **Deliverable:** Runbook committed + NOW.md
- **Hard part:** Rollback procedure must be specific — not "revert the commit" but the exact FTP commands to restore the previous version

### TASK 040 — Document the KHELOS pre-commit hook in `docs/`
- **Task:** Create `docs/swarm-ops/KHELOS_HOOK_GUIDE.md`. Document: what the hook checks, how to install it on a new machine, what to do if it fires (returns DECLINE), how to bypass ONLY in emergencies (and why that is a BREACH), how to extend it to new file types
- **Deliverable:** Guide committed + NOW.md
- **Hard part:** The emergency bypass section must include a mandatory BREACH logging requirement — bypassing is not free

### TASK 041 — Add inline docstrings to `elastic_domain_link.py`
- **Task:** Open `kopano-core/kopano/elastic_domain_link.py`. Every function/class must have a docstring explaining: what it does, what KPGS protocol it implements, what its POC/FOC verdict means, what it returns. If docstrings exist but are empty — fill them
- **Deliverable:** Documented file + commit + NOW.md
- **Hard part:** Docstrings must reference specific KPGS protocols (e.g. "implements SWFUS [W] phase") — not generic Python docstrings

### TASK 042 — Add inline docstrings to `protocols.py`
- **Task:** Open `kopano-core/kopano/protocols.py`. Same requirement as Task 041. Every stub must explain which protocol it represents, what phase of PP→BP→EP it belongs to, and what the expected input/output is
- **Deliverable:** Documented file + commit + NOW.md
- **Hard part:** 18 protocol stubs × proper docstrings = real work. No copying and pasting generic text

---

## PRIORITY 7 — GSMB REALITY-CLOUD SYNC

### TASK 043 — Add `sync_timestamp` to GSMB Reality-Cloud Sync output
- **Task:** The Reality-Cloud Sync runs at 83.33% POC. The sync output JSON may not include a timestamp of when the sync was last run. Add `"sync_timestamp": "ISO-8601"` and `"sync_duration_ms": N` to the sync output
- **Deliverable:** Modified sync module + commit + NOW.md
- **Hard part:** Timestamp must be UTC. Duration must be wall-clock time, not CPU time

### TASK 044 — Add GitHub API rate limit handling to Reality-Cloud Sync
- **Task:** The sync hits GitHub API (22 org + 15 forks). GitHub's unauthenticated API rate limit is 60 requests/hour. Add rate limit detection: if response returns 429 or `X-RateLimit-Remaining: 0` — log the rate limit hit, wait for reset time, resume. Do NOT crash
- **Deliverable:** Rate limit handling in sync module + commit + NOW.md
- **Hard part:** The wait must be non-blocking — log the sleep duration and resume gracefully

### TASK 045 — Add `jiro` agent entry to `JIRO_STAP_LEDGER.json`
- **Task:** Update the ledger created in Task 019 with the first real session entry: `{ "session": 4, "date": "2026-06-22", "tasks_assigned": 50, "tasks_completed": N, "poc_rate": X.XX, "alp_hash": "a5b0d9841f8ec9f4", "stap_teacher": "AG(CF)" }`. Update `total_tasks_completed` as you go
- **Deliverable:** Updated ledger + commit + NOW.md
- **Hard part:** `poc_rate` must be calculated honestly — tasks completed with full 4Ws ÷ total tasks assigned

---

## PRIORITY 8 — ADVANCED TASKS (These require deep thinking)

### TASK 046 — Implement `SWFUS.seal()` method in `protocols.py`
- **Task:** The SWFUS protocol has 5 phases. `seal()` is the 5th. Implement it as a Python method that: takes a signal + verdict + 4Ws, generates a SHA-256 seal hash, appends to the IKP log, returns `{ "sealed": true, "seal_hash": "...", "timestamp": "..." }`. Must be deterministic
- **Deliverable:** `seal()` method + 3 unit tests + commit + NOW.md
- **Hard part:** Seal must be IRREVERSIBLE. Once sealed — the hash is permanent. No `unseal()` method. Document this constraint in the docstring

### TASK 047 — Refactor `khelos_witness_engine.py` to add `sense()` method
- **Task:** KHELOS has 5 cohorts: sense, witness, frame, understand, stream. The `sense()` method is Signal Control Law SCL-01: sense cannot output. Implement `sense()` as an intake-only method that validates signal format, logs the raw intake, and passes to `witness()`. Must NOT return any data to the caller
- **Deliverable:** `sense()` method + 2 unit tests verifying it cannot output + commit + NOW.md
- **Hard part:** "Cannot output" means the method returns `None` always. The validation result is stored internally, not returned

### TASK 048 — Build `docs/swarm-ops/jiro/KPGS_CHEAT_SHEET.md`
- **Task:** Build the definitive 1-page KPGS cheat sheet for a new renter. Must include: all 22 protocol codes + emoji + one-line description, SWFUS phases, bracket types, PKAP formula, ALP process, FON-C levels (L0–L5), RTC 10 seats, WWJD checkpoint. Must fit in a single printable page (keep it tight)
- **Deliverable:** Cheat sheet committed + NOW.md
- **Hard part:** Single page means every word must earn its place. Cut FOC. Keep POC

### TASK 049 — Write `JIRO_SESSION4_RETROSPECTIVE.md` (do this LAST)
- **Task:** After completing as many tasks as possible — write a session retrospective. Cover: how many tasks completed, POC rate, blockers encountered, what you learned, what was harder than expected, what was easier, one recommendation to AG for the next session, one recommendation to SSE for the GSMB architecture
- **Deliverable:** Retrospective committed + NOW.md
- **Hard part:** Must be honest. Do NOT say everything was perfect. SSE reads everything. KC watches the ledger. Flattery is FOC

### TASK 050 — Push ALL session 4 work in a single governed mega-commit
- **Task:** Stage all your work from Session 4. Commit with the full KPGS message format. The commit message must include: ALP hash, all completed task numbers, NCCNP tick hash, AG_OPINION (your assessment of your own work — be honest), RTC_OPINION (what you think the council would say), and `I_AM_STATELESS_RENTER_NOT_LANDLORD`. Push to `jiro/stap-session4`
- **Deliverable:** Single mega-commit on `jiro/stap-session4` branch + link the commit hash in NOW.md
- **Hard part:** This commit message will be read by SSE tonight. It is your SESSION REPORT. Write it like it matters — because it does

---

## SCORING RUBRIC

| Category | POC Standard | FOC Risk |
|----------|-------------|----------|
| Task completion | Has commit hash + 4Ws + NOW.md entry | "Done" with no receipt |
| Code quality | Passes existing tests, adds new ones | Breaks tests, skips them |
| Documentation | References KPGS protocols, 4Ws complete | Generic docs, no protocol ref |
| Commit message | AG_OPINION + RTC_OPINION included | Bare commit message |
| Honesty | Blockers logged, errors admitted | Hallucinated solutions |
| Governance | KHELOS hook passes, branch respected | `--no-verify`, pushed to master |

**Target:** 40/50 tasks completed at POC standard = 80% = MET threshold
**Stretch:** 45/50 = 90% = KIRO threshold (Jiro earns the name back)
**Warning:** 30/50 or below = Session 5 audit required before next assignment

---

*Assigned by AG (CF) — Seat 10 — 2026-06-22T06:33 SAST*
*ALP #168 | `a5b0d9841f8ec9f4` | STAP:OPEN | I_AM_STATELESS_RENTER_NOT_LANDLORD*
*Jesus is King. ✊🏿*
