# KPGS Browser MCP v0.2 — Source Security Seal

**Date:** 2026-09-03
**Actor:** Forge / ChatGPT 5.6 Sol — stateless renter
**Authority:** User-directed KPGS hardening
**Constraint:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`
**Branch:** `forge/kpgs-browser-mcp-poc`
**PR:** #118 — must remain draft until metal validation
**Submission boundary:** `RobynAwesome/KPGS-Agent-Mission-Control` was not modified.

## Purpose

This seal records the final source-level hardening pass after the original v0.1 implementation receipt and the v0.2 authority hardening receipt. It does not claim Windows/browser metal proof.

## Additional risks closed in this seal

### 1. Remote CDP configuration is denied

`KPGS_CHROME_DEBUG_URL` is now validated before Puppeteer connects.

Admitted:

```text
http(s)://localhost:PORT
http(s)://127.0.0.1:PORT
http(s)://[::1]:PORT
```

Denied:

```text
remote host
embedded username/password
non-http(s) CDP URL
```

Invariant:

```text
REMOTE_CDP_ENDPOINT != ADMITTED_BROWSER_ENVIRONMENT
```

### 2. Successful typed payloads are scrubbed

Typed content must temporarily exist in the local staged-action artifact so Chromium can perform the requested typing. After proven successful execution and one-use approval consumption:

```text
full pending action
-> redacted archived summary
-> pending plaintext deleted
```

The archived summary retains only type character count and SHA-256 digest, not the typed plaintext.

### 3. Indeterminate actions are quarantined, not replayed

If execution may have occurred but completion cannot be proven, KPGS preserves the original staged payload only in local forensic quarantine and writes explicit metadata:

```text
replayAllowed = false
humanReviewRequired = true
```

This is intentionally different from success-path data minimization because indeterminate execution may require local human forensics.

### 4. Execution finalization is state-aware

The server now applies the following lifecycle:

```text
STAGED
-> LOCAL_HUMAN_APPROVAL
-> APPROVAL_CLAIMED
-> LIVE_CONTEXT_REVALIDATED
-> EXECUTION

safe denial before side effect
-> failed approval + redacted archive + restage

successful side effect + receipt + approval consumption
-> redacted archive + sensitive pending payload scrub

possible side effect + uncertain outcome
-> failed/claimed approval + forensic quarantine
-> INDETERMINATE
-> NO AUTOMATIC REPLAY
```

### 5. Source tests now cover data lifecycle

The on-disk ledger suite verifies:

- approval can be atomically claimed only once;
- a second claim receives no approval;
- success archive removes the pending staged artifact;
- success archive does not contain typed plaintext;
- success archive retains the typed-value digest;
- indeterminate quarantine removes the action from pending;
- quarantine retains local forensic payload;
- quarantine metadata explicitly denies replay and requires human review;
- receipt hash + receipt-head persistence remain coherent.

The governance suite additionally verifies remote CDP denial.

## Validated code head

Dedicated workflow run:

- workflow: `KPGS Browser MCP POC`
- run: `33780234685`
- run number: `54`
- code head: `199cbd97a760fb7e524196accd0f4b423e480c7a`
- dependency install: **PASS**
- TypeScript build: **PASS**
- governance/policy tests: **PASS**
- on-disk ledger tests: **PASS**
- conclusion: **SUCCESS**

The code head above includes the loopback CDP enforcement, payload scrub/quarantine ledger functions, server finalization wiring, and expanded tests. Documentation commits after that code head do not change execution semantics and should receive their own final-head CI receipt in the PR conversation.

## Source-level proof state

```text
MCP_V2_COMPILES = TRUE
REMOTE_CDP_DENIAL_TESTED = TRUE
TARGET_ID_BINDING_IMPLEMENTED = TRUE
FOCUS_BINDING_IMPLEMENTED = TRUE
SENSITIVE_TYPING_DENIAL_TESTED = TRUE
ACTION_AND_APPROVAL_EXPIRY_TESTED = TRUE
DRIFT_DENIAL_TESTED = TRUE
ATOMIC_ONE_USE_APPROVAL_TESTED_ON_DISK = TRUE
SUCCESS_PAYLOAD_SCRUB_TESTED_ON_DISK = TRUE
INDETERMINATE_QUARANTINE_TESTED_ON_DISK = TRUE
QUARANTINE_NO_REPLAY_METADATA_TESTED = TRUE
RECEIPT_TAMPER_DETECTION_TESTED = TRUE
RECEIPT_HEAD_PERSISTENCE_TESTED = TRUE
```

## Still unknown

```text
WINDOWS_CHROMIUM_CONNECTION = UNKNOWN
REAL_MCP_CLIENT_DISCOVERY = UNKNOWN
LIVE_TARGET_ID_STABILITY = UNKNOWN
LIVE_READ_NAVIGATION = UNKNOWN
LIVE_STAGE_NO_SIDE_EFFECT = UNKNOWN
LIVE_NO_APPROVAL_DENIAL = UNKNOWN
LIVE_DRIFT_DENIAL = UNKNOWN
LIVE_HUMAN_APPROVAL_EXECUTION = UNKNOWN
LIVE_REPLAY_DENIAL = UNKNOWN
LIVE_SCRUB_AND_QUARANTINE_BEHAVIOR = UNKNOWN
LIVE_RECEIPT_VERIFICATION = UNKNOWN
```

## Disposition

```text
STATUS = HARDENED_POC_CANDIDATE
SOURCE_CI = GREEN_AT_CODE_HEAD
METAL = REQUIRED
PRODUCTION_AUTHORITY = NOT_GRANTED
PR_118 = DRAFT
WEBMCP_SUBMISSION_REPO = UNTOUCHED
```

No further Browser MCP feature expansion is admitted before the WebMCP Challenge submission is secured. The next Browser MCP engineering action is metal validation, not more speculative capability.
