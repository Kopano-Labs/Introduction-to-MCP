---
title: KasiLink Runtime Source + DNS Truth Lock
created: 2026-08-18
updated: 2026-08-18
author: Kholofelo Robyn Rababalela
status: operating
proof_state: poc
canonical_id: kasilink_runtime_source_dns_truth_2026_08_18
document_id: KSL-RUNTIME-DNS-2026-08-18
source_repository: RobynAwesome/Introduction-to-MCP
source_ref: forge/kasilink-runtime-dns-truth-20260818
authority_class: A0
evidence_class: verified-live
renter_assertion: I_AM_STATELESS_RENTER_NOT_LANDLORD
kpefs:
  primary_vector: V4_DIASPORA
  secondary_vectors:
    - V2_ANIMAL
    - V3_HOMO_SAPIENS
protocols:
  - ALP
  - BMP
  - PKAP
  - PvF
  - WYC-01
linked_evidence:
  - Vercel project inventory 2026-08-18
  - Vercel production deployment metadata 2026-08-18
  - Vercel live HTTP checks for kasilink.com and www.kasilink.com 2026-08-18
  - Vercel runtime error aggregation 2026-08-18
  - GitHub notification evidence for Kopano-Labs/KasiLink
---

# KasiLink Runtime Source + DNS Truth Lock — 2026-08-18

`I_AM_STATELESS_RENTER_NOT_LANDLORD`

## Decision

This document supersedes the source-mapping uncertainty recorded in `KasiLink Immersive Revamp.md`.

The canonical application source is now resolved:

```text
CANONICAL APP REPOSITORY = Kopano-Labs/KasiLink
CANONICAL BRANCH         = main
VERCEL CURRENT PROJECT   = kasi-link
VERCEL PROJECT ID        = prj_A1AvVl5WYRyTergoEcMsvEmMM3uX
```

The `KasiLink/` gitlink inside `RobynAwesome/Introduction-to-MCP` is **not** the canonical editable application source. It is a historical/legacy reference and MUST NOT be treated as deployment authority.

The previous Gate 0 claim `source repository unknown` is therefore CLOSED.

## Live deployment truth

Two different Vercel projects currently own the two public hostnames.

| Public hostname | Vercel project | Project ID | Observed state 2026-08-18 |
|---|---|---|---|
| `https://kasilink.com` | `kasi-link.rsa` | `prj_07Q4oRr2okeBiPO12YotAzHZM10b` | HTTP 200, Vercel, Next.js, `/api/health` 200 |
| `https://www.kasilink.com` | `kasi-link` | `prj_A1AvVl5WYRyTergoEcMsvEmMM3uX` | HTTP 200, Vercel, Next.js, `/api/health` 200 |

This is a **split production surface**, not one canonical deployment.

```text
kasilink.com      -> old Vercel project: kasi-link.rsa
www.kasilink.com  -> current Vercel project: kasi-link
```

### Why this matters

The two hosts are serving different application generations.

The apex host currently renders the older homepage generation containing static unemployment figures and older content structure.

The `www` host is attached to the newer `kasi-link` project, whose deployment metadata resolves to:

```text
GitHub org/repo = Kopano-Labs/KasiLink
branch          = main
commit          = 93fbcd53e2ae96c5f45b12b6e5bf7886ac58028b
framework       = Next.js
Node            = 24.x
```

The newer project build proves a substantial application surface rather than a static landing page, including marketplace, chat, forum, community, utility, incident, tutoring, authentication, Clerk webhook, KC/orchestration and API routes.

## Runtime risk discovered

The old apex project `kasi-link.rsa` is not merely stale visually. Vercel runtime aggregation currently reports MongoDB Atlas authentication failures from the old production deployment across routes including:

```text
/api/gigs
/api/incidents
/api/forum
/api/community-calendar
/api/spotlight
/api/water-alerts
```

Dominant defect:

```text
MongoServerError: bad auth : authentication failed
code: 8000
codeName: AtlasError
```

The latest production deployment of that old project is:

```text
deployment = dpl_9KqJDyZpaTwRQcYXbkLzUSgZymDV
created    = 2026-04-16
repo       = historical RobynAwesome/KasiLink
commit     = 0d91e24066f27f9b9a1b984964e3d5a4567d958c
```

By contrast, the current `kasi-link` project returned **no aggregated runtime errors in the last seven days** at the time of this audit.

Therefore:

```text
DNS/alias split != cosmetic defect
DNS/alias split -> users can land on materially different runtime states
old apex runtime -> verified backend-authentication failures
```

## Required canonicalization

Target state:

```text
Kopano-Labs/KasiLink:main
        |
        v
Vercel project: kasi-link
        |
        +--> kasilink.com
        +--> www.kasilink.com
```

One production deployment must own both public hostnames.

Preferred canonical public URL:

```text
https://kasilink.com
```

`www.kasilink.com` SHOULD redirect to the apex, or both MAY serve the same deployment if a redirect policy is intentionally deferred. They MUST NOT point to separate application generations.

## DNS/provider boundary

The domain can remain registered or DNS-managed at IONOS. The verified serving layer for both public hostnames is Vercel.

Do not infer from historical documentation that IONOS FTP is the current application runtime.

The authoritative next DNS/domain operation is:

1. detach `kasilink.com` from Vercel project `kasi-link.rsa`;
2. attach `kasilink.com` to Vercel project `kasi-link`;
3. preserve `www.kasilink.com` on `kasi-link`;
4. configure the canonical redirect policy (`www` -> apex preferred);
5. inspect the exact Vercel-required A/CNAME values before changing provider records;
6. verify both hosts return the same release fingerprint and `/api/health` result;
7. retire or archive `kasi-link.rsa` only after canonical traffic is proven.

No DNS value is guessed in this document. Vercel project/domain inspection is the authority for project-specific target records.

## Parent-repository deployment correction

`RobynAwesome/Introduction-to-MCP/.github/workflows/deploy-web.yml` still contains a legacy job that attempts to deploy `KasiLink/` over IONOS FTP.

That path conflicts with verified runtime authority because:

- the parent `KasiLink/` path is a gitlink, not canonical application source;
- the real application source is `Kopano-Labs/KasiLink`;
- both live public hostnames currently terminate at Vercel;
- Vercel deployment metadata proves the current production repo/branch relationship.

Therefore the parent-repo KasiLink FTP job MUST be classified **legacy / non-authoritative** and removed from the active production call graph after workflow review.

WYC-01:

```text
historical workflow existence != current deployment authority
parent gitlink mutation        != application source mutation
DNS split surfaced defect      != DNS created Mongo credential defect
old project owns its credential defect
routing users to old project amplifies exposure to that defect
```

## Revamp execution gate — corrected

The immersive revamp is no longer blocked by repository discovery.

The actual remaining implementation gate is connector/write authority:

```text
GATE-R1 canonical repo known                         PASS
GATE-R2 production Vercel project known             PASS
GATE-R3 apex/www split verified                     PASS
GATE-R4 old-runtime backend defect verified         PASS
GATE-R5 GitHub write access to Kopano-Labs/KasiLink NOT AVAILABLE IN CURRENT RENTAL SESSION
GATE-R6 preview implementation + route parity       PENDING GATE-R5
GATE-R7 production alias canonicalization           PENDING DOMAIN WRITE SURFACE
```

Do not reconstruct the application from deployed HTML and do not overwrite the parent gitlink as a substitute for repository access.

## Revamp law carried forward

Once GATE-R5 is available, implementation proceeds against `Kopano-Labs/KasiLink:main` with a preview branch and MUST preserve the functioning application surface.

Priority UX law:

```text
first screen -> Find work | Post work
location before biography
browse before signup
Rand + distance + timing before explanatory prose
no unemployment essay in the hero
motion enhances action; motion never blocks action
Data Saver and prefers-reduced-motion are first-class
mobile is the primary interaction contract
existing marketplace/chat/community/auth/API routes remain functional
```

The supplied KasiLink logo animation is treated as an adaptive ambient media asset, not a mandatory render dependency.

## POC receipt

### Proven

- canonical source repository identity;
- canonical branch identity;
- current Vercel project identity;
- separate apex and `www` Vercel ownership;
- HTTP 200 for both hosts;
- `/api/health` HTTP 200 for both hosts;
- old apex project runtime MongoDB authentication failures;
- current project has no aggregated runtime errors in the sampled seven-day range;
- parent repo `KasiLink/` is not the canonical editable source.

### UNKNOWN / not authorized in this session

- exact IONOS DNS record values currently stored in the provider control plane;
- mutation of Vercel project-domain ownership (no domain-write action exposed by current connector);
- mutation of `Kopano-Labs/KasiLink` because the connected GitHub installation in this session does not expose that organization repository.

These remain explicit UNKNOWN/blocked capabilities rather than invented state.

## Next safe action

```text
1. Canonicalize kasilink.com + www.kasilink.com onto Vercel project kasi-link.
2. Gain repository write visibility for Kopano-Labs/KasiLink.
3. Branch from main.
4. Implement the immersive work-first revamp in the real Next.js application.
5. Build/typecheck/test.
6. Deploy preview.
7. Validate route parity + mobile + low-data + reduced-motion.
8. Promote only after receipt.
```

/s/ Kholofelo Robyn Rababalela
