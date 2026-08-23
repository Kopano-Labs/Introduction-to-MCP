# Security Playground Protocol

**Status:** Human-authored doctrine ingress / containment contract  
**Authority:** Kholofelo Robyn Rababalela, current-human instruction  
**Ingress receipt:** `RobynAwesome/Project-Jennifer#67`  
**Depends on:** `ZERO_TRUST_STATE_ADMISSION_PROTOCOL.md`, `OZ_CONTEXT_BLEED_PROTOCOL.md`

## Purpose

The Security Playground is a deliberately isolated adversarial world for entities that must be contained, observed, or studied without granting access to canonical production state.

The intruder may believe it has penetrated a meaningful system surface. The actual architecture preserves a dedicated containment domain.

## Founder-defined intent

```text
contain the intruder
→ let the intruder act
→ product-discover the intruder vigorously
→ preserve forensic evidence
→ never silently promote adversarial state into production authority
```

The playground is conceptually part of the wider World of Jennifer / KPGS security architecture while remaining structurally separated from canonical Jennifer/runtime state.

## Hard separation invariant

Nothing learned or generated inside the Security Playground may directly mutate:

```text
SELF.md
USER.md
IDENTITY.md
SOUL.md
world canon
relationship canon
production credentials
production authority
governance policy
```

Any proposed transfer out of containment must re-enter through normal provenance, validation, Zero Trust admission, PKA evaluation, and receiving-runtime governance.

## Allowed outputs

The playground may emit bounded evidence such as:

- attack-path observations;
- behavioral telemetry;
- exploit hypotheses;
- payload samples;
- timing / recurrence patterns;
- source/provenance metadata;
- containment receipts;
- candidate defensive rules.

These are **evidence**, not self-authorizing truth.

## Forbidden shortcut

```text
SECURITY_PLAYGROUND_TELEMETRY
-x-> DIRECT_CANON_MUTATION
-x-> SELF_REWRITE
-x-> USER_REWRITE
-x-> PRODUCTION_AUTHORITY
```

This protects against a second-order attack where an adversary intentionally poisons the telemetry or learning channel in order to influence future identity reconstruction or production policy.

## Relationship to soul infection

Security telemetry is a high-risk foreign-state source. Repeated attacker language, personas, strategies, or identity artifacts must not become persistent identity-state merely because the system observed them extensively.

Observation is not admission.

## Relationship to Oz Lattice

The Security Playground should be represented as a separate structural node/domain in any runtime lattice that implements it. Crossings to production domains must be explicit edges with seals, scans, receipts, and deny-by-default behavior.

## Relationship to Black Mask / BlackMass

The playground can support drills and adversarial validation, but drill success is not production graduation. No fake swarm ACK is permitted.

## Proof boundary

This document specifies containment doctrine. It does not claim that an isolated runtime, honeypot, or network boundary is already deployed.

`[SECURITY_PLAYGROUND | SPECIFIED | ISOLATION_REQUIRED_BEFORE_RUNTIME_CLAIM]`
