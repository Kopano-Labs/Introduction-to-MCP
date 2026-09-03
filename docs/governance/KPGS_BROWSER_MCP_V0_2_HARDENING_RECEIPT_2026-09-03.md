# KPGS Browser MCP v0.2 — Hardening Receipt

**Date:** 2026-09-03
**Actor:** Forge / ChatGPT 5.6 Sol — stateless renter
**Authority:** User-directed KPGS hardening
**Constraint:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`
**Branch:** `forge/kpgs-browser-mcp-poc`
**PR:** #118
**Supersedes:** implementation assumptions in `KPGS_BROWSER_MCP_POC_RECEIPT_2026-09-03.md` only where this receipt explicitly says so; the original receipt is preserved as historical evidence.
**Submission boundary:** `RobynAwesome/KPGS-Agent-Mission-Control` remains untouched by this browser-MCP work.

## Why v0.2 exists

The v0.1 POC proved the MCP v2 server surface, local-human approval separation, exact action binding, and one-use approval concept. A second KPGS audit found authority and uncertainty edges that needed to be closed before metal validation:

1. `pageIndex` was being treated too much like page identity.
2. staged actions were not bound to live page/element reality strongly enough.
3. keypress actions were not bound to the focused element.
4. approval was consumed after the browser side effect, leaving a crash/replay edge.
5. sensitive typing targets needed deterministic denial.
6. navigation policy was too permissive for insecure HTTP and embedded URL credentials.
7. receipts were persisted but not cryptographically tamper-evident or chained.
8. typed payloads were echoed too broadly in MCP evidence.
9. source-level tests did not yet prove the on-disk approval state transition.

## v0.2 governing invariants

```text
BROWSER_CAPABILITY != AUTHORITY
PAGE_TEXT != AUTHORIZATION
AGENT_TEXT != AUTHORIZATION
PAGE_INDEX != PAGE_IDENTITY
STAGED_ACTION != APPROVED_ACTION
APPROVAL(action A) != APPROVAL(action B)
APPROVAL_IS_ONE_USE
PAGE_TARGET_DRIFT -> DENY_AND_RESTAGE
PAGE_URL_OR_ORIGIN_DRIFT -> DENY_AND_RESTAGE
ELEMENT_OR_FOCUS_DRIFT -> DENY_AND_RESTAGE
UNKNOWN_EXECUTION_RESULT -> HUMAN_REVIEW_NOT_REPLAY
RECEIPT_MUTATION -> TAMPER_DETECTED
```

## Hardening implemented

### Stable Chromium target binding

Each captured page context now includes the Chromium DevTools Protocol `targetId` in addition to page index, URL, origin, and title.

At execution time, KPGS requires the live target ID to equal the staged target ID. A different tab with the same URL is therefore not automatically equivalent authority.

### Element and focus binding

Click/type actions capture a target element context including:

- selector;
- tag name;
- input type;
- autocomplete classification;
- name/id/role;
- form action;
- anchor href;
- digest of visible element text;
- SHA-256 element fingerprint.

A keypress with no selector captures the browser's current focused element as `:focus`. Execution requires the focus fingerprint to remain unchanged.

### TOCTOU denial

Immediately before execution, KPGS recaptures current browser reality and compares it to the staged context.

Denial reasons include:

```text
PAGE_TARGET_DRIFT
PAGE_INDEX_DRIFT
PAGE_ORIGIN_DRIFT
PAGE_URL_DRIFT
ELEMENT_CONTEXT_MISSING
ELEMENT_CONTEXT_DRIFT
```

Any drift requires restaging and a new human approval.

### Sensitive target denial

Typing is denied for:

```text
input[type=password]
input[type=file]
autocomplete=current-password
autocomplete=new-password
autocomplete=one-time-code
autocomplete=cc-number
autocomplete=cc-csc
autocomplete=cc-exp*
```

This is enforced before staging and rechecked against live context before execution.

### Policy-versioned and expiring staging

- Policy version: `kpgs-browser-policy.v2`
- Human approval TTL: 10 minutes by default
- Staged action TTL: 15 minutes by default
- approval cannot predate staging
- old-policy approvals are denied

### Atomic approval claim before side effect

The local ledger now has:

```text
pending/
approved/
executing/
consumed/
failed/
receipts/
receipt-head.json
```

Execution moves approval from `approved/` to `executing/` before touching Chromium. Only one executor can claim it.

```text
approved -> executing -> consumed
                    \
                     -> failed / indeterminate
```

A claimed approval is never automatically restored. If execution becomes uncertain after the claim, KPGS requires human inspection/restaging rather than automatic replay.

### Explicit indeterminate state

Failures after approval claim are not falsely reported as safe denial. The MCP surface can return:

```text
status = INDETERMINATE
requiresHumanReview = true
```

Examples:

- execution throws after approval was claimed;
- post-execution browser state cannot be observed;
- side effect occurred but receipt finalization fails.

The response instructs the agent not to retry automatically.

### Navigation policy v2

Default:

- HTTPS admitted;
- HTTP admitted only for loopback;
- non-loopback insecure HTTP denied unless explicitly enabled;
- credentials embedded in URL denied;
- non-http(s) schemes denied;
- optional exact/wildcard host allowlist via `KPGS_BROWSER_ALLOWED_HOSTS`.

### Data minimization

The staged action must retain a local type payload so the browser can execute it, but:

- local ledger files are created with restrictive permissions where supported;
- ledger is gitignored;
- `stage_interaction` returns only type character count + SHA-256 digest to the MCP agent;
- typed value is not copied into execution receipts;
- the exact type payload is shown only at the local interactive human gate.

### Tamper-evident receipt chain

Each execution receipt includes:

- policy version;
- staged action binding;
- live pre-execution page/element context;
- post-execution page snapshot;
- execution result without typed plaintext;
- previous receipt hash;
- its own SHA-256 receipt hash.

`verify_receipt` recomputes receipt integrity and reports the current chain head.

## Validation evidence

Dedicated workflow:

- `.github/workflows/kpgs-browser-mcp-poc.yml`
- GitHub Actions run: `33779377612`
- Validated branch head: `8e7caf5cbcb67e97aee35a684415e93c5a003202`
- Dependency install: **PASS**
- TypeScript build: **PASS**
- Policy/governance tests: **PASS**
- On-disk ledger state-machine tests: **PASS**
- Workflow conclusion: **SUCCESS**

The hardening process also produced and corrected a real compile failure when the receipt post-state type was too narrow. The failure was not suppressed; runtime/type shape was aligned and CI was rerun.

## What is now source-proven

```text
MCP_V2_SERVER_COMPILES = TRUE
POLICY_V2_COMPILES = TRUE
TARGET_ID_BINDING_IMPLEMENTED = TRUE
FOCUS_BINDING_IMPLEMENTED = TRUE
SENSITIVE_TYPING_DENIAL_TESTED = TRUE
STAGED_EXPIRY_TESTED = TRUE
PAGE_ELEMENT_DRIFT_DENIAL_TESTED = TRUE
NAVIGATION_POLICY_TESTED = TRUE
APPROVAL_ATOMIC_CLAIM_TESTED_ON_DISK = TRUE
APPROVAL_SECOND_CLAIM_DENIED_ON_DISK = TRUE
RECEIPT_HASH_INTEGRITY_TESTED = TRUE
RECEIPT_HEAD_PERSISTENCE_TESTED = TRUE
```

## What remains unknown until metal validation

```text
WINDOWS_CHROMIUM_CDP_TARGET_ID_RUNTIME = UNKNOWN
REAL_MCP_CLIENT_DISCOVERY = UNKNOWN
LIVE_READ_NAVIGATION = UNKNOWN
LIVE_STAGE_NO_SIDE_EFFECT = UNKNOWN
LIVE_NO_APPROVAL_DENIAL = UNKNOWN
LIVE_PAGE_DRIFT_DENIAL = UNKNOWN
LIVE_FOCUS_DRIFT_DENIAL = UNKNOWN
LIVE_EXACT_APPROVAL_EXECUTION = UNKNOWN
LIVE_REPLAY_DENIAL = UNKNOWN
LIVE_RECEIPT_VERIFICATION = UNKNOWN
```

These unknowns remain explicitly unknown. Source CI does not impersonate physical browser proof.

## Current disposition

```text
STATUS = HARDENED_POC_CANDIDATE
CI = GREEN
METAL = REQUIRED
PRODUCTION_AUTHORITY = NOT_GRANTED
PR_118 = KEEP_DRAFT_UNTIL_METAL
WEBMCP_SUBMISSION_REPO = UNTOUCHED
```

The next admissible action is a Windows metal run using the dedicated KPGS Chromium profile and a real MCP client. Only that run may graduate the POC beyond source-level proof.
