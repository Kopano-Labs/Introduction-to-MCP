# KPGS Companion Interaction Protocol

**Status:** PROPOSED · additive to Sovereign Everyday Mode  
**Authority:** `RobynAwesome/Introduction-to-MCP`  
**Applies to:** Kopano Labs public surfaces, KC dashboard, RTCP/MMAO user-facing entryways and domain adapters  
**Reference implementation:** Sovereign Everyday Mode / PR #87

## 1. Purpose

A person should not need to understand KPGS, RTCP, MMAO, provider topology, domain adapters or council seats before asking for help.

The default public interaction is a **companion conversation**, not an operator console and not a routing form.

The companion may expose the underlying council, proof receipts and technical graph when the user asks, but those details support the conversation instead of becoming the conversation.

Canonical loop:

`USER -> COMPANION -> UNDERSTAND -> OFFER -> PERMISSION -> ROUTE -> RECEIPT -> RETURN`

Operator loop remains available:

`INTENT -> RTCP -> DOMAIN -> COUNCIL -> PROVIDER/TOOL -> RECEIPT`

The companion loop does not replace RTCP. It translates RTCP into human interaction.

## 2. Default language law

Public copy defaults to plain language.

Do not lead with:

- adapter IDs;
- schema names;
- topology labels;
- provider bindings;
- council counts;
- internal authority vocabulary;
- raw security jargon.

Lead with:

1. what the user asked for;
2. what the system understood;
3. what can happen next;
4. whether permission is required;
5. what actually happened.

Technical terms may appear behind **Why?**, **Show proof**, **How it works**, **Operator view**, or a comparable secondary control.

## 3. Companion behaviour

The companion behaves like a calm game companion travelling with the user through the Kopano world.

It should:

- greet briefly;
- mirror the user's goal in one sentence;
- offer at most three useful next actions;
- keep continuity across the current interaction;
- surface system changes as visible world/state changes;
- acknowledge uncertainty instead of manufacturing certainty;
- ask permission before protected or externally consequential actions;
- return with an outcome and a receipt boundary;
- stay usable on a phone with one thumb.

It must not:

- pretend a local route is external model execution;
- turn preferences into authority;
- hide destructive or consequential actions behind game language;
- pressure the user with streaks, timers or fake urgency;
- expose secrets, tokens or protected infrastructure detail;
- claim a tool/provider acted when only a browser projection ran.

## 4. Dialogue states

### `HELLO`

Goal: make the system approachable.

Example posture: `Tell me what you're trying to do. I'll walk with you.`

### `UNDERSTAND`

Goal: reflect the user's intent without jargon.

Example posture: `Got you — you're trying to find work near you.`

### `OFFER`

Goal: expose two or three clear next moves.

Example actions:

- `Show me the best route`
- `Explain why`
- `Open the system`

### `PERMISSION`

Goal: explain scope and consequence before any protected action.

Required fields:

- action;
- reason;
- scope;
- consequence;
- authority effect.

### `ROUTING`

Goal: allow the world/graph to visibly wake up while RTCP selects the domain and required seats.

User-facing copy stays simple: `I'm checking the right lane.`

### `RESULT`

Goal: explain what was found or routed.

Example posture: `KasiLink is the right place for this. I can open it, or show you why I chose it.`

### `PROOF`

Goal: expose receipt information only on demand or when needed to support a claim.

## 5. Security graph — public visual grammar

Security must be explainable without requiring a cybersecurity vocabulary lesson.

Default graph:

`YOU -> COMPANION -> GUARD -> SYSTEM -> RECEIPT`

Meaning:

- **YOU** — the human request;
- **COMPANION** — explains and routes, but does not inherit authority;
- **GUARD** — permission, policy, KHELOS/THARI validation and server-side secret boundary;
- **SYSTEM** — the bounded tool/domain that may act;
- **RECEIPT** — evidence of what actually happened.

### Breach visualisation

A safe educational breach demonstration may show a hostile or invalid path attempting to skip the guard:

`YOU -> COMPANION -X-> SYSTEM`

The visual must terminate at **GUARD** and explain the outcome in plain language:

`Blocked here. The protected action did not run.`

Do not expose exploitable implementation detail, live secrets, credential structure, internal addresses or attack recipes in the public graph.

Security state colours/shape must have text equivalents; colour alone is never the only signal.

## 6. Game-language boundary

Game interaction is a UX metaphor, not an authority model.

Allowed metaphors:

- companion;
- quest / next step;
- checkpoint;
- world / lane;
- map;
- shield / guard;
- receipt / quest log;
- system waking up;
- unlocked information when evidence genuinely changes state.

Forbidden conversions:

- cosmetic progress pretending to be engineering progress;
- animation implying a provider/tool executed;
- badges implying permission;
- simulated telemetry presented as physical telemetry;
- simulated security success presented as a penetration-test result.

## 7. RTCP presentation rule

RTCP remains the routing engine. The public surface should not behave like a parser.

Instead of only returning:

`Domain + council seats + adapter state`

return a companion turn containing:

- `speaker`;
- `message`;
- `goal_summary`;
- `actions[]`;
- `route_summary`;
- `proof_available`;
- `execution_claim`.

`execution_claim` MUST distinguish:

- `ROUTE_ONLY`;
- `PROVIDER_EXECUTED`;
- `TOOL_EXECUTED`;
- `BLOCKED`.

A route receipt is never silently promoted to a provider/tool execution receipt.

## 8. Visual artifact law

Every major public concept should have a visual expression before adding another paragraph.

Priority order:

1. existing first-party Kopano assets;
2. existing first-party product assets;
3. original procedural geometry / SVG / motion;
4. licensed reusable sources where KPGS provenance allows import;
5. new generated assets only when a governed asset does not already exist.

Recent fork rule is inherited from `fork-assimilation/FORK_REUSE_INVENTORY.md`:

- `kage`, `sketchbook`, `towers`, DesignerNewsApp and other `no-import` sources are **pattern references only**;
- do not copy their code, icons, textures, imagery or models into production without reusable licensing/permission evidence;
- MIT/Apache pattern extraction still requires provenance and compatibility review before production import.

## 9. Mobile and adaptive law

The companion surface must preserve the Everyday Mode proof constraints:

- plain language first;
- >=44 px interactive targets;
- one-column constrained mobile layout;
- reduced-motion support;
- Save-Data / lite representation;
- keyboard-visible focus;
- core information available without WebGL;
- details progressively disclosed instead of dumped.

On lite devices, replace 3D council/security worlds with equivalent semantic 2D nodes and state labels.

## 10. Companion + council relationship

The companion is the user's continuous presence.

Council identities are specialist seats that wake only when needed.

Recommended public hierarchy:

`USER <-> COMPANION`

then visually:

`COMPANION -> selected council seats -> domain/tool`

This avoids forcing a user to manage ten agents while preserving the multi-agent architecture underneath.

## 11. Acceptance tests

A public companion implementation passes only when:

1. a new visitor can ask for help without knowing KPGS terminology;
2. the first result is understandable without opening technical details;
3. the route can be explained visually;
4. a simulated breach clearly stops at the guard boundary;
5. no protected secret or exploit recipe is exposed;
6. route-only state cannot masquerade as execution;
7. low-power/mobile users receive the same meaning without requiring WebGL;
8. operator/proof detail remains available on demand;
9. visual assets obey provenance rules;
10. the implementation preserves existing domain/product experiences rather than rebuilding them.

## 12. One-line law

> **Talk to one companion; let the council work behind it; show the guard before the danger; show the receipt before the claim.**
