# FivesArena Phase 0 — Evidence and Freeze Ledger

Issue: #27  
Branch: `agent/fivesarena-phase0-evidence`  
Control plane: `RobynAwesome/Introduction-to-MCP`

## Confidentiality boundary

This ledger records public architecture and verification evidence only. Do not commit credentials, environment values, private booking/customer data, internal prompts, proprietary design-source files, or unpublished commercial material. Use redacted fixtures and checksums.

## Hard invariants

- The existing FivesArena logo is immutable until the owner identifies the canonical source files.
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
| `fivesarena.logo.primary` | pending | pending | pending | no | blocked |
| `fivesarena.icon.maskable` | pending | pending | pending | no | blocked |
| `fivesarena.icon.app` | pending | pending | pending | no | blocked |
| `fivesarena.poster.static` | pending | pending | pending | no | planned |
| `fivesarena.scene.football` | pending | pending | pending | no | planned |

No row becomes canonical merely because a filename contains “logo”.

## Data provenance registry

| Dataset | Current source | Freshness | Trust state | Offline policy | Owner |
|---|---|---|---|---|---|
| Venue/courts | pending inspection | pending | unverified | last-known-good only | pending |
| Bookings/availability | pending inspection | real-time required | verified-only | never imply availability offline | pending |
| Arena fixtures | pending inspection | pending | unverified | label cached timestamp | pending |
| External football fixtures | `/api/football/*` observed | provider-dependent | unverified | stale badge + expiry | pending |
| World Cup tournament | hard-coded claims observed | stale risk | stale/unverified | do not present as live | pending |

## Phase 0 acceptance checklist

- [ ] Run collector against both real checkouts.
- [ ] Review candidate paths and identify canonical logo/icon files.
- [ ] Store owner-approved hashes in this ledger or a reviewed machine-readable registry.
- [ ] Identify each data adapter and its source-of-truth owner.
- [ ] Capture clean-install, lint, typecheck, test, build, BDD, browser-console, and offline-sync baselines.
- [ ] Classify all service-worker routes by privacy and caching strategy.
- [ ] Record exact Three.js source commit and asset licenses.
- [ ] Confirm which World Cup content is obsolete, historical, or still operational.
- [ ] Do not begin visual implementation until the freeze gate passes.

## Next implementation order

1. Runtime/check reliability and dependency alignment.
2. Typed freshness-aware data adapter.
3. Service-worker privacy and bounded caching.
4. APWA perception/orchestration shell.
5. Feature-flagged Three.js physics proof with static fallback.
6. Reviewed Figma/Canva asset ingestion.
