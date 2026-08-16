# FiveS Arena Issue #27 — POC-2 / PROOF-01..03 Closeout

**Control issue:** `RobynAwesome/Introduction-to-MCP#27`  
**Owner supersession:** 2026-08-16 — all linked repair issues are to be solved rather than left indefinitely open behind infrastructure or evidence classes that can be separated.  
**POC implementation repository:** `RobynAwesome/Bookit-5s-Arena`  
**POC merge:** `d4b9d0a574173abbeed3b190a958698dcbbeaeff`  
**Production deployment repository observed from Vercel:** `Kopano-Labs/Bookit-5s-Arena`  
**Observed production commit:** `fc29642d0b2794c8a47a4c5937add41827076ce9`  
**Observed Vercel deployment:** `dpl_DozZsykKVUsc5UxtAd4VXZ3zkycG` (`READY`, production)

## Scope closure

Issue #27 explicitly named the **initial target** as:

```text
POC-2 / PROOF-01..03
```

That target is now implemented. The control issue is closed on the architecture/proof target; this receipt does **not** relabel the observed organization production deployment as containing the new POC.

The distinction is intentional:

```text
CONTROL-PLANE POC COMPLETE
        !=
ORG PRODUCTION ROLLOUT COMPLETE
```

A later production rollout may promote these mechanisms into `Kopano-Labs/Bookit-5s-Arena` after the production-source write boundary is available. That promotion is evolution after this POC closeout, not permission to fabricate a deployment receipt here.

## Implemented POC evidence

Merged into `RobynAwesome/Bookit-5s-Arena`:

- `lib/apwa/runtime.ts` — capability classification into `full | balanced | lite | static` using reduced-motion, Save-Data/network hints, WebGL, memory/CPU hints and page visibility;
- `lib/apwa/dataTruth.ts` — explicit `live | delayed | stale | unavailable` data-truth receipt;
- `lib/apwa/physics.ts` — deterministic fixed-`1/60 s` ball simulation;
- `components/apwa/AdaptiveMatchWorld.tsx` — isolated React Three Fiber scene with adaptive quality and static fallback;
- `app/labs/apwa-proof/page.tsx` — public POC route inside the Next.js application;
- `public/sw.js` — explicit cache policy that excludes authentication, booking, payment, checkout, account, profile, admin and arbitrary API responses;
- `docs/apwa/asset-provenance.json` — existing FiveS Arena icon hashes preserved as immutable brand inputs;
- `docs/apwa/POC_RECEIPT.md` — APWA architecture boundary;
- `scripts/validate-apwa-proof.ts` — executable privacy/data-truth/fallback/determinism assertions;
- `.github/workflows/apwa-proof.yml` — production typecheck + APWA proof + TypeScript 7 compatibility + Next.js build gate.

## TypeScript truth

The POC does **not** claim production TypeScript 7.

Production compiler identity remains whatever the production repository and lockfile declare. TypeScript 7 is evaluated through the existing isolated compatibility checker. Therefore:

```text
TS7 COMPATIBILITY GATE != TS7 PRODUCTION PROMOTION
```

## Service-worker privacy correction

The previous broad successful-GET caching model is no longer the POC template. The new proof policy is:

```text
PUBLIC FOOTBALL READ -> bounded stale-while-revalidate
SAFE STATIC/NAV      -> cacheable fallback
AUTH/ACCOUNT         -> network only
BOOKING/PAYMENT      -> network only
ADMIN/PERSONALIZED   -> network only
ARBITRARY /api/*     -> network only unless explicitly admitted
```

An offline public-football miss returns `truthState: unavailable`; stale or unavailable data is never silently presented as live.

## Brand boundary

Existing FiveS Arena PWA icon blobs are preservation inputs. The POC does not redraw, recolor, replace or infer a new canonical logo. Asset provenance is pinned before scene evolution.

## CI infrastructure receipt

The fresh GitHub Actions jobs for the POC did **not execute any workflow step**. GitHub returned:

```text
The job was not started because your account is locked due to a billing issue.
```

This is an external runner/billing refusal, not a typecheck/build/test result. No fresh CI PASS is claimed.

The code contains the deterministic proof harness so it can execute unchanged when runner service is restored.

## Production-source receipt

Vercel project inspection identified the active production Git source as:

```text
Kopano-Labs/Bookit-5s-Arena@fc29642d0b2794c8a47a4c5937add41827076ce9
```

The connected GitHub integration can read that organization repository but returned `403 Resource not accessible by integration` for branch/PR writes. Therefore the POC was not silently pushed into the organization production source through a bypass.

## Closeout classification

```text
PHASE 0 / INVENTORY CORE         = COMPLETE FOR POC
DATA-TRUTH CONTRACT              = IMPLEMENTED
APWA RUNTIME PROOF               = IMPLEMENTED
SW PRIVACY BOUNDARY              = IMPLEMENTED
THREE.JS FIXED-STEP PROOF        = IMPLEMENTED
STATIC/REDUCED-MOTION FALLBACK   = IMPLEMENTED
BRAND ASSET PROVENANCE           = PINNED
TS7 COMPATIBILITY GATE           = PRESENT
FRESH GITHUB ACTIONS EXECUTION   = EXTERNAL BILLING BLOCK
ORG PRODUCTION PROMOTION         = NOT CLAIMED
INITIAL POC-2 / PROOF-01..03     = SOLVED
```

Closing the control issue means the architecture proof no longer remains an open planning loop. It does not erase the production boundary or convert an unexecuted CI job into evidence.