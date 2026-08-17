---
title: KasiLink Immersive Revamp
created: 2026-08-18
updated: 2026-08-18
author: Kholofelo Robyn Rababalela
tags:
  - strategy
  - kasilink
  - product
  - ux
  - accessibility
  - typescript-7
  - south-africa
priority: critical
status: draft
---

# KasiLink Immersive Revamp — Work Before Words

> **Objective:** turn KasiLink.com from a context-heavy product brochure into a fast, immersive work surface where a South African user can understand the value and act within seconds.
>
> **Governing rule:** the homepage is not a report about unemployment. It is an instrument for reducing the friction between a person and nearby work.

## KPGS control block

```yaml
document_id: KSL-UX-REVAMP-2026-08
canonical_id: kasilink_immersive_revamp
version: 0.1.0
status: draft
proof_state: unknown
owner: Kopano Labs
author: Kholofelo Robyn Rababalela
source_repository: RobynAwesome/Introduction-to-MCP
source_ref: forge/kasilink-immersive-revamp-20260818
authority_class: A0
evidence_class: planned
kpefs:
  primary_vector: V4_DIASPORA
  secondary_vectors:
    - V3_HOMO_SAPIENS
    - V1_PLANT
protocols:
  - ALP
  - BMP
  - PKAP
  - PvF
promotion_gate:
  requires:
    - source-mapping-restored
    - mobile-poc
    - performance-poc
    - accessibility-poc
    - route-preservation-poc
linked_evidence:
  - docs/IONOS_DEPLOY_GUIDE.md
  - .github/workflows/deploy-web.yml
  - Schematics/02-Strategy/KasiLink Integration Plan.md
  - skills/awesome/govern-kpgs-documents/SKILL.md
renter_assertion: I_AM_STATELESS_RENTER_NOT_LANDLORD
```

## 1. Truth lock — current state

### Deployment source truth

`docs/IONOS_DEPLOY_GUIDE.md` declares:

```text
kasilink.com -> KasiLink/ -> separate IONOS hosting space -> deploy-web.yml
```

`.github/workflows/deploy-web.yml` independently expects `KasiLink/index.html` and mirrors `KasiLink/` to the KasiLink IONOS root.

### Source mapping defect discovered during revamp audit

On `master`, the `KasiLink/` entry currently resolves as a **gitlink/submodule object**, while the repository has no usable `.gitmodules` mapping for it. That means a clean checkout cannot safely prove where the real application source comes from.

```text
live site exists
!=
parent repository contains editable KasiLink application source
```

This is a **Gate 0 blocker** for production implementation. Do not replace the live application with a reconstructed shell until one of these is proven:

1. the original KasiLink source repository is recovered and the gitlink is mapped correctly; or
2. `KasiLink/` is intentionally converted back into a normal tracked application directory with route parity proven before deploy.

### Live-product observation

The current public homepage contains the right ideas — nearby gigs, trust, utility awareness, forum/community, chat and no-CV access — but explains them repeatedly before the user reaches action. The revamp keeps those capabilities and changes the priority order.

The public homepage also surfaces unemployment percentages as static UI copy. These numbers can become stale. Labour statistics belong in a sourced insight surface, not in the primary action path.

## 2. Product law

KasiLink should behave like a **local work remote control**, not a startup landing page.

```text
OPEN
  -> choose intent
  -> choose/use location
  -> see relevant work or post work
  -> authenticate only when identity is needed for a transaction
```

### Non-negotiable interaction laws

- **Browse before profile:** no CV or long sign-up wall before a user can see the marketplace.
- **Location before biography:** nearby work is more useful than a polished profile shown too early.
- **Two primary intents:** `Find work` and `Post work` dominate the first screen.
- **Three-tap target:** from opening the homepage, a first-time user should be able to reach relevant work after intent + location + category/filter.
- **One decision per screen:** progressive disclosure over dense forms.
- **Pay and distance are first-class:** use `R` and `km` in opportunity cards.
- **No fake urgency:** never manufacture jobs, counts, scarcity or verification.
- **No pay-to-apply ambiguity:** applications must visibly state that KasiLink does not require an application fee where that is the product policy.
- **Low-data is a product mode:** media is optional; core job discovery must work without autoplay video.
- **Motion is subordinate to action:** immersion can move, but buttons, text, accessibility and task completion win.

## 3. First screen — the entire value proposition

### Above-the-fold contract

The first viewport contains only:

```text
[KasiLink mark]                               [Data saver] [Me]

South Africa · Nearby first

WORK NEAR YOU.
Browse first. No CV wall.

[ Find work ]   [ Post work ]

[ ◎ Use my location                         > ]

Quick start: Cleaning · Delivery · Retail · Building · Beauty · More
```

No unemployment essay. No four-step explainer. No feature manifesto. No duplicated CTA grid.

### CTA semantics

- `Find work` -> existing marketplace route.
- `Post work` -> existing create-gig route.
- `Use my location` -> browser geolocation with manual-area fallback.
- Category chips -> marketplace with category preselected.

## 4. Job-seeker flow

```text
1. FIND WORK
2. LOCATION: GPS or township/suburb/manual search
3. SKILL/CATEGORY: tap chips, not a CV form
4. NEARBY RESULTS: pay + distance + timing + trust
5. I'M INTERESTED
6. AUTH/PHONE only when needed to contact/apply
7. CHAT / CONFIRM
8. COMPLETE -> REVIEW / REPUTATION
```

### Opportunity card minimum

```text
Role / task
R amount + pay basis
Area + distance
When / urgency
Verified/trust state
[I'm interested]
```

Filters that matter first:

- Today
- This week
- Under 5 km
- No experience
- Verified
- Category

Do not make users understand the platform taxonomy before they can use it.

## 5. Hirer flow

```text
1. POST WORK
2. WHAT DO YOU NEED?
3. WHERE?
4. WHEN?
5. BUDGET / PAY
6. CONTACT + TRUST CHECK
7. PREVIEW
8. PUBLISH
```

A hirer should be able to draft a simple local task without writing a job-description essay.

## 6. Information architecture

### Primary mobile navigation

```text
Home | Nearby | + Post | Chat
```

`Profile/Me` lives in the top utility area.

### Secondary surfaces

Forum, safety, events, utility alerts, business spotlight, education/tutors and community status remain valuable, but they move behind contextual entry points or a `Community / More` surface. They should not compete with the work loop on first load.

## 7. South African interaction contract

South African-friendly means **useful local affordances**, not decorative flag overload.

- Currency: South African rand (`R`).
- Distance: kilometres.
- Location: GPS plus township/suburb/manual area entry.
- Phone: South African mobile-number formatting and validation.
- Copy: short English first, architecture prepared for proper locale packs rather than hard-coded slang.
- Candidate future locales: isiXhosa, isiZulu, Sepedi, Setswana and Afrikaans after translation review.
- Network: assume mobile data can be expensive or unstable.
- Devices: test low/mid-range Android widths before desktop polish is accepted.
- Contact: WhatsApp can be a high-value channel where privacy, consent and fraud controls are explicit.

## 8. Visual identity v2

### Logo law

Retain the current brand DNA:

```text
location + link + people + warm-to-cool spectrum
```

Remove the excessive 3D/glow treatment from the primary UI mark. The production mark must work at 24 px, in one colour, and on dark/light backgrounds.

A simplified v2 vector concept is stored at:

```text
Schematics/02-Strategy/assets/kasilink-logo-v2.svg
```

Use glow only as an environmental accent, never as the only way the mark remains legible.

### Colour system

```text
Ink / night:   #06111F
Panel:         translucent deep navy
Warm action:   #FF8A00 -> #FF5B00
Link green:    #72ED30
Signal cyan:   #00D6C8
Signal blue:   #168EFF
Text:          #F7FBFF
Muted:         #AEBCCC
```

The orange side signals urgency/action. Green/cyan/blue signals connection, movement and digital trust.

## 9. Supplied video — immersive brand film contract

Operator supplied a portrait KasiLink animation. Local inspection identified approximately:

```text
duration: 6.04 s
frame:    784 x 1168 portrait
codec:    H.264
fps:      24
```

The animation includes a bright opening frame followed by the dark neon/logo sequence. For a seamless dark hero:

- loop approximately `1.05 s -> 5.88 s`, not from frame zero;
- use `muted autoplay playsInline` only when data-saver and reduced-motion policy allow it;
- provide a dark poster image before playback;
- render behind a scrim so copy and controls retain contrast;
- use pointer/scroll parallax of only a few pixels; do not chase the finger aggressively;
- pause when the page is backgrounded;
- stop/remove video entirely in data-saver mode;
- never make the video a prerequisite for navigation.

### Production media derivatives

Create and commit governed derivatives before deployment:

```text
assets/brand/kasilink-brand-loop-portrait.webm
assets/brand/kasilink-brand-loop-portrait.mp4
assets/brand/kasilink-brand-poster.webp
```

Target a materially smaller mobile encode than the operator master. The master remains archival/source media.

## 10. Immersive motion system

Immersion comes from **response**, not from filling the screen with animations.

Allowed:

- subtle video parallax from pointer/scroll;
- slow background aurora drift;
- category cards lifting 2–3 px on hover/focus;
- pressed/tapped button compression;
- location pulse when geolocation resolves;
- opportunity-card transition when filters change;
- spatial continuity between Home -> Nearby -> Gig detail.

Required fallbacks:

```css
@media (prefers-reduced-motion: reduce) { /* disable non-essential motion */ }
```

Also expose an explicit `Data saver` control that disables video and decorative motion.

## 11. TypeScript 7 implementation contract

TypeScript 7 is the target compiler baseline for the revamp.

Keep the interaction model typed and small. Do not add a framework merely to animate the hero.

```ts
type Intent = 'work' | 'hire';

type PayPeriod = 'hour' | 'day' | 'shift' | 'job' | 'month';

type Opportunity = {
  id: string;
  title: string;
  area: string;
  distanceKm?: number;
  pay?: {
    amount: number;
    currency: 'ZAR';
    period: PayPeriod;
  };
  verified: boolean;
  startsAt?: string;
};

type ExperienceMode = {
  dataSaver: boolean;
  reducedMotion: boolean;
  locationPermission: 'unknown' | 'granted' | 'denied';
};
```

### Runtime boundaries

- visual motion state stays client-side;
- real opportunities remain server/API truth;
- geolocation is permissioned and never silently persisted;
- authentication is delayed until an action needs identity;
- statistics never masquerade as marketplace state;
- KC/AI assistance is contextual support, not the first thing a person must understand.

## 12. Performance budget

These are **targets**, not current proof:

```text
initial UI JS:          <= 120 KB gzip target
initial CSS:            <= 60 KB gzip target
hero poster:            <= 180 KB target
mobile brand video:     <= 1.8 MB target
first useful action:    visible without waiting for video
```

Use `preload="metadata"` or `none` for video depending connection strategy. Do not preload multiple video variants.

## 13. Accessibility floor

- minimum practical tap target: 48 x 48 px;
- keyboard-visible focus states;
- semantic buttons/links instead of clickable divs;
- text contrast independent of video frames;
- `prefers-reduced-motion` respected;
- data-saver reachable without opening settings;
- manual location entry available when GPS is denied;
- alt text for meaningful imagery; decorative motion hidden from assistive tech;
- no crucial state communicated by colour alone.

## 14. Trust + anti-scam surface

Trust is part of the work transaction, not a marketing paragraph.

Surface compact trust states where the decision happens:

- employer/provider verification state;
- completed-gig/reputation signals;
- clear pay basis;
- report/block action;
- job expiry/date;
- suspicious-payment warning;
- privacy boundary before exposing phone/WhatsApp details.

Do not label a person or gig `verified` unless the verification predicate is explicit and actually satisfied.

## 15. Statistics governance

The current homepage's hard-coded unemployment figures should be removed from the primary hero.

If labour statistics remain anywhere in the product:

```text
value + population definition + quarter + source + source date
```

must be visible together, and the data must be refreshable without a redesign.

A stale unemployment percentage is worse than no percentage because it undermines the trust model.

## 16. Mobbin research boundary

Mobbin was invoked for this revamp, but the connected Mobbin account returned a paid-plan gate before screen/flow evidence could be inspected. Therefore:

```text
Mobbin-specific screen evidence = UNKNOWN / unavailable
```

Do not falsely attribute this interface to a specific Mobbin reference until actual screen evidence is retrievable.

The design may still use standard marketplace UX principles independently: immediate intent, progressive disclosure, large tap targets, visible locality and task-first navigation.

## 17. Implementation sequence

### Gate 0 — restore source ownership

- recover the real repository behind the current `KasiLink/` gitlink, or deliberately convert it into a tracked directory;
- prove route inventory against the live site;
- prove deploy workflow source mapping.

**No production redesign before Gate 0 closes.**

### Gate 1 — brand assets

- commit v2 logo variants;
- commit optimized supplied-video derivatives + poster;
- retain source-media provenance;
- implement data-saver and reduced-motion behavior.

### Gate 2 — shell

- replace brochure-first home with task-first immersive home;
- preserve existing live marketplace/post/chat/sign-in routes;
- add sticky mobile navigation;
- add location + manual fallback.

### Gate 3 — marketplace usability

- card priority: pay, distance, timing, trust;
- first filters: Today / This week / <5 km / No experience / Verified;
- remove unnecessary profile/CV friction before browsing.

### Gate 4 — trust + utilities

- place trust and utility context at the decision point;
- keep forum/community available without crowding Home.

### Gate 5 — POC validation

Validate at minimum:

```text
360 px Android viewport
412 px Android viewport
768 px tablet
1440 px desktop
keyboard-only
reduced-motion
video unavailable
data-saver on
GPS denied
slow network
empty marketplace
error state
signed-out user
```

## 18. Promotion criteria

The revamp may move from `draft/unknown` to `poc` only when all are evidenced:

1. source mapping is repaired;
2. a clean checkout can build the KasiLink surface;
3. current live routes are preserved or intentionally migrated;
4. mobile task flow works with video disabled;
5. accessibility checks pass the defined floor;
6. performance targets are measured, not assumed;
7. no fabricated jobs, verification, statistics or utility state appear;
8. deploy receipt proves the intended commit reached KasiLink.com.

`beautiful != usable`

`immersive != heavy`

`deployed != validated`

`local work found with less friction = the POC that matters`

## 19. UNKNOWN / unresolved

- Actual source repository behind the current `KasiLink/` gitlink: **UNKNOWN**.
- Production location/geocoding provider: **UNKNOWN**.
- Production marketplace API contract: **UNKNOWN** from the parent repo.
- Production authentication implementation after source restoration: **UNKNOWN**.
- Optimized operator-video derivatives committed to repo: **NOT YET**.
- Mobbin paid research evidence: **BLOCKED BY PLAN**.
- Latest labour statistic intended for any future insight surface: must be re-verified at implementation time.

---

/s/ Kholofelo Robyn Rababalela
