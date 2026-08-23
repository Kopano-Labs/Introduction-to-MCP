# Sovereign Everyday Mode

Issue: #41

## Purpose

Everyday Mode is the non-technical interaction layer for KPGS-governed products. It hides infrastructure vocabulary by default while preserving visible consequences, permission reasons, recovery paths and evidence boundaries.

The reference implementation lives in `apps/kc-dashboard` and preserves the existing technical dashboard as **Operator Mode**.

## Experience law

```text
one clear next action
  -> explain consequence
  -> disclose why/permission when needed
  -> confirm
  -> execute only within the declared local/server authority
  -> explain what happened
  -> explain what happens next
```

Progressive disclosure hides jargon, not governance.

## Companion presentation layer

The additive public interaction contract lives in:

- [`COMPANION_INTERACTION_PROTOCOL.md`](./COMPANION_INTERACTION_PROTOCOL.md)
- [`companion-interaction-contract.json`](./companion-interaction-contract.json)

It extends Everyday Mode from a plain-language dashboard into a companion-first interaction law for RTCP/MMAO and public product surfaces:

```text
USER <-> COMPANION -> GUARD -> SYSTEM -> RECEIPT
```

The companion talks to the user; RTCP/council routing stays behind it. Operator/proof detail remains available on demand.

A safe public breach visual stops at the guard and explains the block without exposing secrets, credential structure, private infrastructure or exploit recipes.

## Reference pilot

The KC dashboard reference pilot is intentionally read-only:

```text
understand -> permission explanation -> acknowledge -> confirm -> complete
```

Completing the pilot stores only local review progress. It cannot mutate websites, permissions, releases, capability leases, deployment state or canonical workflow state.

This proves the everyday experience membrane without inventing a privileged backend action.

## Interaction profile

Portable schema: `interaction-profile.schema.json`.

Current bounded preferences:

- warmth (`1..5`);
- detail density (`compact | balanced | detailed`);
- pace (`calm | normal | fast`);
- initiative (`low | balanced | high`);
- explanation style (`plain | steps | why`);
- explicit consent flag for future account sync.

The reference PWA stores the profile locally by default under a versioned storage key. Pilot progress is stored under a **different** versioned key.

Therefore:

```text
RESET PREFERENCES != RESET WORKFLOW PROGRESS
PROFILE != CAPABILITY
PROFILE != AUTHORITY
```

Profiles are inspectable in the UI, resettable, and exportable as JSON.

## Account sync boundary

`accountSyncConsent=false` by default.

The reference experience can record explicit consent, but it does not claim that account sync is connected. A future account-sync implementation must still add authenticated transport, privacy/retention policy and evidence before synchronization can be represented as successful.

## Runtime adaptation vs training

Everyday preferences may produce runtime hints such as:

- response warmth;
- response density;
- pacing;
- initiative;
- explanation style;
- supported inference hints.

The reference runtime always declares:

```text
modelWeightTraining = false
```

Changing Everyday Mode settings is **not** fine-tuning and does not update model weights. Training/fine-tuning requires a separate governed dataset, provenance, privacy, evaluation and promotion pipeline.

## Offline and reconnect

When offline:

- local profile remains available;
- local reference-pilot progress remains available;
- live status is explicitly labelled as potentially stale;
- user gets a direct reconnect/retry path.

Realtime transport is never canonical state. A connected indicator means current status may be refreshed; it does not grant authority.

## Accessibility and mobile

The reference surface includes:

- semantic buttons/labels/details/summary controls;
- `aria-live` status for connection and completion feedback;
- visible focus treatment;
- reduced-motion behavior;
- mobile single-column layouts;
- touch targets at least 44px, with primary mobile actions at 48px;
- progressive disclosure rather than dense infrastructure panels.

## Operator Mode

The original technical KC topology remains accessible through **Operator view**.

This lets operators inspect canonical/reference/experimental membranes, provenance, frontier lanes and authority boundaries without forcing those concepts into the everyday task path.

```text
EVERYDAY MODE = SIMPLE CONSEQUENCES + RECOVERY
OPERATOR MODE = TECHNICAL INSPECTION
BOTH VIEWS != NEW AUTHORITY
```

## Verification

The reference proof has three layers:

1. `node --test` executes the pure profile/pilot state model after TypeScript compilation;
2. `tests/test_sovereign_everyday_mode.py` checks plain-language, persistence isolation, consent, accessibility and mobile invariants;
3. Vite/TypeScript typecheck + production build proves the reference UI compiles.

Promotion evidence must keep these separate from real production user-outcome telemetry. A reference UI test does not prove real-world task-completion rates.
