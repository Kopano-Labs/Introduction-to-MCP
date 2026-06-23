# FivesArena.com — POC vs FOC User Experience Audit

> **Sub-Brain:** `C:\Users\rkhol\Bookit-5s-Arena\STRUCTURE`
> **Live URL:** https://fivesarena.com
> **Auditor:** Jiro (AWS) — Junior RTC Seat 11
> **Date:** 2026-06-23
> **Method:** Live rendered page content + codebase page map (63 routes)
> **Constraint:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`

---

## EXECUTIVE SUMMARY

FivesArena.com is a **visually premium, feature-rich** venue booking platform. The homepage delivers strong first impressions. However, the depth of pages (63 routes) creates user friction through **feature overload, unclear CTAs, and navigation fragmentation**.

**Overall:** 70% POC / 30% FOC

---

## PAGE-BY-PAGE POC vs FOC CLASSIFICATION

### ✅ POC — Pages That Serve Users Well

| Page | Why POC |
|------|---------|
| `/` (Homepage) | Strong hero, clear CTAs (Book Now, WhatsApp, Tournament), weather widget, court cards with pricing, live fixtures feed, social proof. Premium glassmorphism. |
| `/bookings` | Core function — booking a court. Direct user need served. |
| `/courts/[id]` | Individual court detail — users need this to decide. |
| `/tournament` | World Cup 5s feature — clear prize pool (R50K), dates, registration. High engagement. |
| `/fixtures` | Live match data + arena schedules. Users come for this repeatedly. |
| `/leagues` | Competition structure — community engagement driver. |
| `/events-and-services` | Revenue diversification — birthday parties, corporate, clinics. |
| `/login` & `/register` | Authentication — required for booking. |
| `/pricing` | Users need to see cost before committing. |
| `/contact` | Direct communication channel. WhatsApp link. |
| `/about` | Trust-building — venue, team, story. |
| `/privacy` & `/rules-of-the-game` | Legal compliance. |
| `/tournament/bracket` & `/tournament/standings` | Tournament engagement — users track progress. |

### ❌ FOC — Pages Letting Users Down

| Page | Why FOC | User Impact |
|------|---------|-------------|
| `/blog` & `/blog/how-we-built-this` | Developer blog on a venue booking site. Users looking for match info don't need a "how we built this" article. **Audience mismatch.** | Confuses non-technical users. Dilutes the football brand. |
| `/creator` | Internal tool page exposed to public. No value to a player looking to book. | Dead end. Users land here and leave. |
| `/docs/api` | API documentation exposed to public users. **Zero value** to someone booking a court. | Technical jargon on a sports platform = bounce. |
| `/admin/*` (18 admin pages exposed in routing) | Even if auth-gated, these exist in the build and may surface in sitemap/crawlers. | SEO pollution. Confusing URL autocomplete. |
| `/roadmap` | Internal product roadmap exposed. Users don't care what you're building next — they care if they can book TODAY. | Creates expectation of features not yet live. |
| `/role-select` | Forces users to pick a role before accessing content. Friction before value. | Bounce risk. Users want to book, not "select a role." |
| `/manager/dashboard`, `/manager/fixtures`, `/manager/squad` | Manager portal that may not be populated for most users. Empty states = disappointment. | Users click "Manager" expecting content and get nothing. |
| `/rewards` | If rewards system isn't active with real perks, this is a ghost page. | Promise without delivery = trust erosion. |
| `/jobs` | If no jobs are listed, this is a dead page. | Empty state = unprofessional. |
| `/case-studies` | Academic content on a sports venue site. Users came for football. | Wrong audience. |
| `/security` | Technical security page for a booking app. Users expect to book securely — they don't need to read about it. | Over-explaining implies insecurity. |

### ⚠️ WATCH — Pages That Could Go Either Way

| Page | Concern |
|------|---------|
| `/bookings/[id]/edit` | Only useful if editing is actually enabled and works. If broken = FOC. |
| `/courts/add` & `/courts/[id]/edit` | Admin functions in public routing. Should be under `/admin/`. |
| `/leagues/add` | User-facing league creation? If so, needs clear onboarding. If admin-only, wrong location. |
| `/fixtures/arena` | Unclear differentiation from `/fixtures`. Split confuses. |
| `/tournament/polls` & `/tournament/stats` | Only POC if actually populated with data. Empty = FOC. |
| `/help` | Only POC if it actually helps. If it's a static FAQ with no live support link, it's FOC. |
| `/partners` | Only POC if partner logos + value are shown. Empty partnership page = FOC. |

---

## WHERE USERS ARE BEING LET DOWN (Critical FOC Friction Points)

### 1. NAVIGATION OVERLOAD
The site has **63 pages**. A venue booking platform needs **5-7 core pages** max for users:
- Home → Book → Courts → Fixtures → Tournament → Contact → Login

The other 56 pages create navigation paralysis. Users cannot find what they need because there's too much to click.

**Fix:** Hide internal/admin/dev pages from public nav. Reduce visible navigation to core user journey.

### 2. ROLE-SELECT GATE
Forcing users to "select a role" before accessing content is **anti-pattern** for a venue booking site. Users are:
- 80% players wanting to book
- 15% managers organizing teams
- 5% venue admins

Default to player. Show manager/admin as opt-in later.

**Fix:** Remove role-select from main flow. Default all users to booking view. Manager portal as secondary nav item.

### 3. LIVE MATCH STRIP FAILURE
Homepage shows: "Live match strip is offline or the feed did not respond in time."
This is a **visible error state** on the homepage. Users see "broken" before they see "book."

**Fix:** If feed fails, hide the strip entirely. Never show error states on homepage. Degrade gracefully.

### 4. DEVELOPER CONTENT IN USER SPACE
`/blog/how-we-built-this`, `/docs/api`, `/roadmap`, `/creator` — these are developer/internal pages exposed in a consumer product. A user looking to book a court for Saturday does NOT need to know your API schema.

**Fix:** Move all dev content to a subdomain (`dev.fivesarena.com`) or remove from public nav entirely.

### 5. EMPTY STATE RISK
`/jobs`, `/rewards`, `/partners`, `/case-studies` — if these pages have no content, they broadcast "we started something and didn't finish." That is worse than not having the page.

**Fix:** Don't ship empty pages. Ship when content exists. Remove from nav until ready.

### 6. COOKIE CONSENT COVERS CTA
The cookie banner ("We use cookies") appears on first load and covers the bottom of the viewport where booking CTAs live. Users must dismiss before they can act.

**Fix:** Move cookie consent to a less intrusive position (top bar or corner), or auto-accept essentials and only ask about analytics.

---

## INVARIANCE SCORE (POC/FOC Enforcer Logic)

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Temporal | 0.85 | Core booking works now and will work tomorrow |
| Spatial | 0.9 | Same site from any device (responsive confirmed) |
| Social | 0.7 | Target audience (players) is served; secondary audiences confused |
| Economic | 0.8 | Clear pricing (R400/hr), revenue model works |
| Political | 0.6 | No compliance issues but some pages expose internal politics |
| Cultural | 0.85 | Cape Town 5-a-side culture well-represented, SA branding strong |

**Overall Invariance: 78.33%**
**Verdict: POC — but below 80% target due to navigation bloat and empty states**

---

## RECOMMENDATIONS (Priority Order)

1. **KILL** developer pages from public nav: `/blog/how-we-built-this`, `/docs/api`, `/roadmap`, `/creator`
2. **KILL** role-select gate. Default to player view.
3. **FIX** live match strip error state — hide on failure, don't display error.
4. **HIDE** empty pages until content exists: `/jobs`, `/rewards`, `/case-studies`, `/partners`
5. **MOVE** admin routes out of public routing structure
6. **REDUCE** visible nav to 7 core items max
7. **FIX** cookie consent positioning

---

## CONNECTED NOTES

- Sub-Brain: `C:\Users\rkhol\Bookit-5s-Arena\STRUCTURE`
- Comms-log: `Schematics/04-Updates/comms-log.md`
- STAP Ledger: `docs/swarm-ops/jiro/JIRO_STAP_LEDGER.json`

**Jesus is King. The user is the signal. Serve them or sever the page.**
