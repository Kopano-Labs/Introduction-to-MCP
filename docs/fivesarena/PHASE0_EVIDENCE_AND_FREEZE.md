# FivesArena Phase 0 — Evidence and Freeze Ledger

Issue: #27  
Branch: `agent/fivesarena-phase0-evidence`  
Control plane: `RobynAwesome/Introduction-to-MCP`

## Confidentiality boundary

This ledger records public architecture and verification evidence only. Do not commit credentials, environment values, private booking/customer data, internal prompts, proprietary design-source files, or unpublished commercial material. Use redacted fixtures and checksums.

## Hard invariants

- The existing FivesArena logo is immutable. Its observed bytes are now hashed; owner confirmation is still required before declaring the file canonical.
- Discovery may hash assets but must not rewrite, optimize, recolour, resize, regenerate, or relocate them.
- Work begins and receipts land in Introduction-to-MCP.
- Production claims require agreement between source, lockfile, CI, deployment, and live runtime.
- Figma and Canva are design-source lanes; runtime assets require provenance and reviewed exports.
- Third-party websites may inspire interaction patterns, but their protected code and assets must not be copied.

## Known baseline

| Surface | Observed state | Gate |
|---|---|---|
| TypeScript | Bookit package declares `^5.4.5` | No TS7 claim |
| Three.js | Bookit declares `^0.184.0`; RobynAwesome/three.js dev reports 0.185.0 | Pin exact provenance before use |
| Next.js | `^15.5.18` | Align related tooling |
| eslint-config-next | `16.2.1` | Major mismatch must be resolved |
| PWA manifest | World Cup naming remains | Replace only after product/data decision |
| Tournament UI | `TournamentSection.jsx` hard-codes teams, dates, format and prize presentation | Treat as editorial campaign data, not live scores |
| Football feeds | `/api/football/*` normalizes provider data through `lib/sports/football.js` | Add freshness, provenance and fallback contracts |
| Service worker | Broad successful-GET runtime caching | Privacy correction required |
| APWA | Canonical definition exists | Target POC-2 / PROOF-01..03 |
| Copilot | unavailable through 2026-09-01 | No workflow may depend on it |

## Evidence collector

Run from the Introduction-to-MCP checkout:

```bash
FIVESARENA_REPO=/absolute/path/to/Bookit-5s-Arena \
  node scripts/fivesarena-phase0-audit.mjs > fivesarena-phase0-report.json
```

The collector is read-only. It:

1. hashes logo/brand/icon/model candidates;
2. locates stale World Cup strings;
3. reports TypeScript, Next.js, Three.js, and related versions;
4. summarizes strictness settings;
5. flags broad service-worker caching patterns;
6. emits no file contents or environment values.

The generated report is evidence, not automatically safe to publish. Review it before committing because filenames can still disclose unpublished product structure.

## Canonical asset registry

| Logical ID | Repository | Path | SHA-256 | Owner-confirmed | Runtime use |
|---|---|---|---|---|---|
| `fivesarena.logo.primary` | `Kopano-Labs/Bookit-5s-Arena` | `public/images/logo.svg` | `a113c8ac…a9118d` | no | existing; preserve exact bytes |
| `fivesarena.icon.app.192` | `Kopano-Labs/Bookit-5s-Arena` | `public/icons/icon-192x192.png` | `f019db47…02d59` | no | existing; pending confirmation |
| `fivesarena.icon.maskable` | `Kopano-Labs/Bookit-5s-Arena` | `public/icons/icon-maskable-512x512.png` | pending | no | blocked |
| `fivesarena.poster.static` | pending | pending | pending | no | planned fallback |
| `fivesarena.scene.football` | pending | pending | pending | no | planned, feature-flagged |

The primary-logo candidate is referenced by `components/Header.jsx`. That observation plus its hashes provides identity evidence, but the owner must still confirm it is the canonical source. No row becomes canonical merely because a filename contains “logo”.

## Data provenance registry

| Dataset | Current source | Freshness | Trust state | Offline policy | Owner |
|---|---|---|---|---|---|
| Venue/courts | pending inspection | pending | unverified | last-known-good only | pending |
| Bookings/availability | pending inspection | real-time required | verified-only | never imply availability offline | pending |
| Arena fixtures | pending inspection | pending | unverified | label cached timestamp | pending |
| External football fixtures | `/api/football/*` → `lib/sports/football.js` → provider adapter | provider-dependent | architecture observed; runtime unverified | stale badge + expiry | pending |
| World Cup campaign | `components/home/TournamentSection.jsx` hard-coded constants and copy | editorial/manual | stale-risk; not live data | static fallback only after review | pending |

### Stale-data replacement rule

Do not replace hard-coded campaign content with raw Three.js objects. Separate content from presentation first:

1. move tournament claims into a typed, freshness-aware campaign adapter;
2. display `asOf`, source and stale/archived status;
3. keep a static, accessible fallback;
4. let the Three.js scene consume the same approved view model behind a feature flag;
5. never use cached booking availability as if it were current.

## Three.js and design-source gate

The first scene is a progressive enhancement, not the data source. It must have:

- fixed-timestep movement and gravity;
- deterministic reset and reduced-motion behavior;
- lazy loading and a static fallback;
- WebGL/context-loss recovery;
- asset provenance, size budgets and reviewed Figma/Canva exports;
- no logo texture mutation or regeneration.

## Phase 0 acceptance checklist

- [ ] Run collector against both real checkouts.
- [x] Identify the logo candidate consumed by the production header and store its exact hashes.
- [ ] Obtain owner confirmation for canonical logo/icon files.
- [ ] Hash remaining manifest/icon candidates.
- [x] Separate hard-coded World Cup campaign content from provider-backed football feeds in the evidence model.
- [ ] Identify each data adapter and its source-of-truth owner.
- [ ] Capture clean-install, lint, typecheck, test, build, BDD, browser-console, and offline-sync baselines.
- [ ] Classify all service-worker routes by privacy and caching strategy.
- [ ] Record exact Three.js source commit and asset licenses.
- [ ] Confirm which World Cup content is obsolete, historical, or still operational.
- [ ] Do not begin visual implementation until the freeze gate passes.

## Next implementation order

1. Runtime/check reliability and dependency alignment.
2. Typed freshness-aware campaign and sports-data adapters.
3. Service-worker privacy and bounded caching.
4. APWA perception/orchestration shell.
5. Feature-flagged Three.js physics proof with static fallback.
6. Reviewed Figma/Canva asset ingestion.
