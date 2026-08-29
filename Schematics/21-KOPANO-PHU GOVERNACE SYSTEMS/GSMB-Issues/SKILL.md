---
name: weekly-fork-audit
description: >
  Weekly audit of all forked repositories in RobynAwesome's GitHub estate.
  Checks upstream deltas, usability scoring, integration mapping, and
  seeds useful patterns back into GSMB Local. Follows the CRUD → SWFUS →
  BP → BMP → POCvsFOC → KPCB+ pipeline.
triggers:
  - "weekly fork audit"
  - "check forked repos"
  - "fork lore update"
  - "upstream delta check"
  - "forked repo usability"
---

# SKILL: Weekly Forked Repo Audit

## Purpose

Every week, audit all forked repositories in `RobynAwesome` to determine:
1. Are they still alive upstream?
2. Are they useful to KPGS lanes?
3. Should they be promoted from POC → FOC or demoted to STALE/ARCHIVE?

## Pre-Requisites

- Access to Microsoft Edge browser (user is logged into GitHub as RobynAwesome)
- Read `GSMB-Issues/index.md` for current fork classifications
- Read `GSMB-Issues/Forked-Repo-Lore/FORK_USABILITY_MATRIX.md` for current scores

## Execution Protocol

### Phase 1: CRUD (Create-Read-Update-Delete)

For each fork in the `Forked-Repo-Lore/` folder:

1. **Read** the fork's GitHub page: `https://github.com/RobynAwesome/<fork-name>`
2. **Read** the "X commits behind" indicator on the repo banner
3. **Read** the last commit date and message
4. **Update** `UPSTREAM_DELTA.md` in the fork's folder with:
   - Commits behind upstream
   - Last upstream release tag (if any)
   - Breaking changes in upstream changelog (if any)
5. **Delete** stale observations older than 4 weeks from `USABILITY_NOTES.md`

### Phase 2: SWFUS (Search-Watch-Filter-Understand-Synthesize)

1. **Search** upstream repos for issues/PRs mentioning features relevant to KPGS
2. **Watch** for new releases, major version bumps, deprecation notices
3. **Filter** changes that affect our integration points (e.g., API changes in `posthog`, shader API in `orb`)
4. **Understand** the delta: Does upstream's direction still align with our lane?
5. **Synthesize** a weekly summary into `WEEKLY_AUDIT_LOG.md`

### Phase 3: BP (Breaking Points)

For each fork with upstream changes:

1. Would pulling upstream HEAD break our current integration?
2. Are there dependency conflicts with our Next.js / Python / .NET stacks?
3. Does the fork's license still permit our use case?

### Phase 4: BMP (Breaking-Model Points)

After stress results:

1. What would full upstream adoption mean for our architecture?
2. Does it require refactoring any KPGS lane?
3. Cost/benefit: is the effort worth the capability gain?

### Phase 5: POCvsFOC (Proof of Concept vs Full Operational Capability)

Classify each fork using the scoring matrix:

| Score | Criteria |
|---|---|
| 🟢 **FOC** | Actively integrated, code referenced from our repos, upstream tracked within 10 commits |
| 🟡 **POC** | Shows promise, used in experiments/demos, not yet production-integrated |
| 🔴 **STALE** | >50 commits behind upstream, no active use case in any KPGS lane |
| ⚪ **ARCHIVE** | Kept for reference only, no planned integration |

Update `FORK_USABILITY_MATRIX.md` with new scores and justification.

### Phase 6: KPCB+ (Consistent Ingestion)

For any fork promoted or showing useful patterns:

1. Seed the relevant files/patterns into `Schematics/MAIN-BRAIN/External-Estate-Seeds/`
2. Update the GSMB sovereign pointer registry
3. Create a receipt in the fork's `INTEGRATION_MAP.md`

## Output Artifacts

After each weekly audit, produce:

1. **Updated `WEEKLY_AUDIT_LOG.md`** with dated entry
2. **Updated `FORK_USABILITY_MATRIX.md`** with current scores
3. **Updated per-fork `UPSTREAM_DELTA.md`** files
4. **Updated `NOW.md`** in repository root with audit receipt

## Canonical Forks to Audit

The following forks are canonical to KRR's evolution and MUST be checked every week:

| Fork | Upstream | KPGS Lane |
|---|---|---|
| `threeui` | mrdoob/three.js ecosystem | FivesArena 3D, Kopano Sovereign Hub |
| `orb` | WebGPU community | Visual identity, shader systems |
| `kage` | Lighting/atmosphere | Stadium ambiance, immersive UX |
| `towers` | Procedural generation | Generative architecture |
| `posthog` | PostHog/posthog | Product analytics across all surfaces |
| `speech-to-speech` | Voice AI | Aya/KC voice interfaces |
| `speechmatics-python-sdk` | Speechmatics | Speech API integration |
| `OmniRoute` | MIT AI gateway | Multi-model routing |
| `Graft` | Claude Code | Agent acceleration |
| `open-antigravity` | Community | Agent tooling |
| `Skills` | Community | Agent skill registry |
| `starfall-salvage` | WebGL games | 404 game / Arena Lab assets |
| `video_to_data` | Nvidia Isaac | Robotics pipeline (Cars4Mars) |
| `claude-code-templates` | Anthropic community | CLI configuration |

## Schedule

- **When**: Every Monday morning (SAST)
- **Duration**: 30–60 minutes
- **Triggered by**: Any stateless renter, or cron-scheduled via `/schedule`

## Connected Documents

- [`GSMB-Issues/index.md`](index.md) — Master issues index
- [`RTCP_PIPELINE_CRUD_SWFUS_BP_BMP_POCvsFOC_VNEXT.md`](../MAIN-BRAIN/RTCP_PIPELINE_CRUD_SWFUS_BP_BMP_POCvsFOC_VNEXT.md)
- [`KPCB_PLUS_LANGUAGE_STATUS.md`](../MAIN-BRAIN/KPCB_PLUS_LANGUAGE_STATUS.md)
