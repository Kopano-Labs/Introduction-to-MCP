# KPGS Continuity + Situational Transition Governance

Issue: #101

Status: **specified / review required**

`I_AM_STATELESS_RENTER_NOT_LANDLORD`

## Purpose

This lane binds KPGS continuity, Partial Knowable Algebra (PKA) transition reasoning, reusable capability graduation, KasiLink's employment loop, and Kopano Labs field validation into one governed feedback architecture.

It does **not** prescribe one universal route through reality. It defines the invariants that make a situational route admissible, inspectable, and receipted.

Canonical doctrine:

> **Do not prescribe the universe. Govern the transition.**

## 1. Continuity contract — durable doctrine vs volatile NOW

KPGS separates durable purpose/invariants from volatile current state:

```text
Legacy.md / governance doctrine = durable purpose + invariants
AGENTS.md                        = agent/renter entry surface
NOW.md                           = volatile salience + temporal truth
receipts                         = evidence that a claimed transition occurred
```

Repository-root `NOW.md` is the current-state authority for this repository. It records active objective, current lane, blockers, known errors, recent receipts, pauses, and the next admissible action.

A stateless renter must:

```text
assert renter identity
-> load Legacy purpose
-> read repository-root NOW.md
-> classify evidence before interpretation
-> recover admitted lane + blockers + receipts
-> execute within authority
-> produce receipts
-> update NOW.md on material handoff
```

Model memory, conversation history, a personal vault `Now.md`, or a nested `Now.md` may provide evidence. None silently supersedes repository-root `NOW.md` as temporal truth.

If root `NOW.md` is missing, contradictory, or materially stale relative to stronger witnessed receipts, the renter must expose the conflict and resolve to **HOLD** until continuity is reconciled.

## 2. PKA situational transition doctrine — CCP / CDP

### Anti-pipeline invariant

Neither of these is a universal law:

```text
CCP -> CDP
CDP -> CCP
```

A governed situation may legitimately:

- originate in CCP;
- originate in CDP;
- move CCP -> CDP;
- move CDP -> CCP;
- converge multiple states;
- diverge one state into multiple governed paths;
- remain on HOLD because the evidence is only partially knowable.

The route is variable. The law that admits or denies a transition is invariant.

### Formal sketch

```text
S_t = current system state
K_t = currently knowable evidence
G   = static / admitted governance invariants

T(S_t, K_t, G)
  -> CCP
  -> CDP
  -> CONVERGE
  -> DIVERGE
  -> HOLD
```

PKA should therefore answer:

> Given the current state, currently knowable evidence, and governing invariants, what transition is admissible now?

It should **not** answer:

> Which state always comes first?

### HOLD is first-class

`HOLD` is not an error or weak fallback. It is the correct governance result when the system cannot yet establish enough about the current situation to admit another transition.

Examples:

```text
insufficient evidence -> HOLD
contradictory receipts -> HOLD
missing authority      -> HOLD
unknown origin order   -> HOLD unless order is irrelevant to the bounded action
```

### Transition receipt law

Every admitted or withheld transition must be explainable through:

```text
trigger
-> evidence
-> invariant
-> authority
-> transition
-> receipt
```

The machine-readable contract is `situational-transition.schema.json`.

A transition receipt describes a decision. It does not manufacture the underlying evidence or authority.

## 3. KPGS Capability Factory — the governed website-producing machine

KPGS should increasingly reuse proven capabilities rather than repeatedly rebuilding the same infrastructure per DNS/repository.

Candidate capability classes:

- component libraries;
- identity/authentication;
- commerce and payments integration boundaries;
- dashboards;
- CMS/content primitives;
- deployment infrastructure;
- telemetry/observability;
- tests/verification harnesses;
- SEO/indexing primitives;
- APWA/offline/adaptive behavior.

A capability is not canonical merely because code exists.

Graduation law:

```text
Capability
-> Contract
-> Implementation
-> Test
-> Receipt
-> POC
-> Reusable Primitive
```

A new domain should increasingly ask:

> Which already-graduated KPGS capabilities does this system require?

rather than:

> How do we rebuild the entire website stack again?

### Capability proof boundary

A reusable primitive must carry enough metadata/receipts to answer:

- what contract does it satisfy?;
- what implementation/version was tested?;
- which tests and evidence prove it?;
- what authority admitted it?;
- where is it safe to reuse?;
- what invalidates its proof state?;
- what rollback/replacement path exists?

A component copied across repositories without those answers is reuse, but it is **not yet a KPGS-graduated primitive**.

## 4. KasiLink Employment Engine — socio-technical feedback loop

`KasiLink.com` is a proof surface for an employment system, not merely a frontend.

Canonical economic loop:

```text
Discover
-> Access
-> Understand
-> Learn
-> Validate capability
-> Trust validation
-> Transact
-> Get paid
-> Telemetry
-> Improve
-> repeat
```

The engine must eventually prove in reality:

- can a person discover an opportunity?;
- can they access it on weak hardware / low bandwidth?;
- can they understand it?;
- can they acquire the required capability?;
- can that capability be validated?;
- can another party trust the validation?;
- can the parties transact?;
- does money actually reach the worker?;
- can the process survive fraud?;
- can it survive poor connectivity?;
- can it scale?;
- can another person reproduce the outcome?

### Governed feedback path

```text
KasiLink runtime
-> telemetry
-> classification
-> routing
-> protocol selection
-> invariant audit
-> POC / FOC check
-> KMEC / PKA state update
-> governed distribution
```

The Agent Swarm and RTC leader may observe and route transitions, but no independent agent gains ambient authority to mutate production merely because it observed telemetry.

CCP/CDP direction remains situational under the transition doctrine above.

## 5. Kopano Labs — Intern Vanguard C reality-validation lane

AI and software can compress iteration time, but they do not eliminate external clocks such as:

- human trust;
- procurement;
- manufacturing;
- regulation;
- education;
- organizational adoption;
- capital formation;
- physical logistics;
- relationships;
- market demand.

**Intern Vanguard C** is the field-validation lane for claims that leave the software boundary.

The role is **field-validation operator**, not "cheap junior developer."

Example hypothesis:

> A young person can complete a learning pathway under weak-device / low-data constraints, have the acquired capability validated, and convert that proof into a trusted economic opportunity.

Vanguard C evidence should be able to record:

- who attempted/completed the pathway under the applicable consent/privacy rules;
- device class and connectivity/data constraints;
- where drop-off occurred;
- why drop-off occurred;
- whether capability was actually demonstrated;
- whether the market/employer trusted the validation;
- whether an opportunity resulted;
- whether payment actually completed;
- time-to-outcome;
- what failed outside the software system.

These observations are **receipts/evidence**, not automatic proof of a universal social claim.

## 6. Complete governed organism

```text
KPGS Capability Factory
-> KasiLink Employment Engine
-> human / economic reality
-> Kopano Labs Vanguard C field validation
-> evidence / telemetry
-> KMEC + PKA
-> KPGS correct | promote | rollback | HOLD
-> repeat
```

The objective is not merely:

> AI builds software faster.

The stronger hypothesis to validate is:

> AI can increase the rate at which a human being acquires, tests, validates, and economically deploys capability.

Engineering target:

```text
reduce time from idea -> validated economic consequence
without allowing speed to remove governance
```

Useful learning/iteration vector:

```text
Context x Persistence x Consistency x Feedback Density
```

Persistence without feedback can preserve the wrong direction efficiently. Feedback density makes iteration economically and epistemically useful.

## 7. Proof-state boundaries

This document **specifies** the architecture. It does not claim that:

- every reusable capability is already graduated;
- KasiLink has already proven every employment outcome;
- Vanguard C field evidence already exists;
- PKA/KMEC runtime code already enforces every situational transition described here;
- CCP/CDP has one canonical origin order;
- a software test is equivalent to socio-economic POC.

Runtime/field claims require implementation + evidence + authority + receipts in their owning lanes.

## 8. Review checklist

- [ ] root `NOW.md` remains the only repository current-state authority;
- [ ] stateless renter entry surfaces route through root `NOW.md`;
- [ ] `HOLD` is a first-class transition outcome;
- [ ] no fixed CCP/CDP direction is encoded;
- [ ] every transition carries trigger/evidence/invariant/authority/receipt semantics;
- [ ] reusable capability graduation is proof-driven;
- [ ] KasiLink employment loop includes access, learning, validation, trust, transaction, payment and telemetry;
- [ ] weak hardware/connectivity, fraud, scale and reproducibility are explicit;
- [ ] Vanguard C handles real-world validation outside the software boundary;
- [ ] reality feedback can route through KMEC/PKA without becoming ambient authority;
- [ ] no POC is promoted without receipts.
