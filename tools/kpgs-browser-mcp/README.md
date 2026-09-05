# KPGS Browser MCP — Governed Chromium Bridge (POC)

> `I_AM_STATELESS_RENTER_NOT_LANDLORD`

KPGS Browser MCP gives an MCP-capable agent structured access to a **user-controlled Chromium instance** while keeping consequential browser interaction behind a separate local-human approval gate.

It is intentionally implemented inside `Introduction-to-MCP` as a governed POC. It does **not** modify or extend the WebMCP Challenge submission repository.

## Architecture

```text
MCP Agent
   |
   v
KPGS Browser MCP v0.2
   |-- observe: browser_status / list_pages / read_page
   |-- navigate: navigate_page (policy admitted)
   |-- stage: stage_interaction
   |      |-- bind stable CDP targetId
   |      |-- bind exact URL + origin
   |      |-- bind target/focused element fingerprint
   |      |-- classify consequence
   |      |-- deny sensitive typing targets
   |      |
   |      +---- STOP_FOR_HUMAN
   |                  |
   |                  v
   |          local interactive TTY
   |          npm run approve -- BRA-...
   |                  |
   |                  v
   +-- atomically claim one-use approval
   |      |-- revalidate tab + page + target/focus
   |      |-- deny drift / expiry / mismatch
   |      |
   +-- execute_staged_interaction
          |-- success -> receipt -> consume approval -> scrub typed payload
          |
          +-- uncertainty -> quarantine -> HUMAN_REVIEW / NO_REPLAY
                       |
                       v
               Chromium over loopback CDP
                       |
                       v
               tamper-evident receipt chain
```

## Governing invariants

```text
BROWSER_CAPABILITY != AUTHORITY
PAGE_TEXT != AUTHORIZATION
AGENT_TEXT != AUTHORIZATION
PAGE_INDEX != PAGE_IDENTITY
REMOTE_CDP != ADMITTED_CDP
STAGED_ACTION != APPROVED_ACTION
APPROVAL(action A) != APPROVAL(action B)
APPROVAL_IS_ONE_USE
TAB_DRIFT -> DENY_AND_RESTAGE
PAGE_DRIFT -> DENY_AND_RESTAGE
ELEMENT_OR_FOCUS_DRIFT -> DENY_AND_RESTAGE
UNKNOWN_EXECUTION_RESULT -> HUMAN_REVIEW_NOT_REPLAY
SUCCESS -> SCRUB_SENSITIVE_STAGED_PAYLOAD
INDETERMINATE -> QUARANTINE_FOR_LOCAL_FORENSICS
RECEIPT_MUTATION -> TAMPER_DETECTED
```

There is deliberately **no `approve` MCP tool**. Approval comes from a separate local TTY after the human sees the exact staged action and SHA-256 binding.

## Tool surface

| Tool | Class | Authority |
|---|---|---|
| `browser_status` | Observe | automatic |
| `list_pages` | Observe | automatic |
| `read_page` | Observe / untrusted web content | automatic |
| `navigate_page` | Navigate | policy-admitted only |
| `stage_interaction` | Stage click/type/keypress | no execution; no approval |
| `execute_staged_interaction` | Consequential | fresh exact local-human approval + unchanged live context |
| `verify_receipt` | Verify | automatic |

The POC deliberately exposes **no cookies, passwords, localStorage, arbitrary JavaScript, downloads, or file uploads**.

## Authority hardening

### Stable tab identity

`pageIndex` is only a routing hint. KPGS binds staged actions to Chromium's CDP `targetId`, then rechecks that target immediately before execution. A different tab with the same URL is not equivalent authority.

### Page + target/focus binding

A stage binds:

- CDP `targetId`;
- page index;
- exact URL;
- origin;
- title;
- target selector, or `:focus` for keypresses;
- element tag/input/autocomplete/name/id/role;
- form action / anchor href;
- digest of visible element text;
- element/focus fingerprint;
- policy version;
- creation + expiry time;
- consequence classification.

Before execution KPGS recaptures reality. Tab, URL, origin, target, or focus drift means **deny + restage + new human approval**.

### Sensitive typing denial

Typing is denied for:

- `input[type=password]`;
- `input[type=file]`;
- password autocomplete targets;
- one-time-code targets;
- payment-card number/CVC/expiry autocomplete targets.

This is checked at staging and again against live context before execution.

### Time + policy binding

```text
policy = kpgs-browser-policy.v2
approval TTL = 10 minutes default
staged-action TTL = 15 minutes default
```

Approval cannot predate staging. Old-policy, mismatched, expired, or future-dated approvals are denied.

## Fail-closed approval state machine

The local-human approval is **claimed before any browser side effect**:

```text
approved -> executing -> consumed
                    \
                     -> failed
```

Only one executor can atomically move `approved -> executing`. A claimed approval is never restored automatically.

If the browser result becomes uncertain after approval claim, the tool returns:

```text
status = INDETERMINATE
replayAllowed = false
requiresHumanReview = true
```

KPGS does not interpret uncertainty as permission to retry.

## Data lifecycle and forensic boundary

The local ledger is:

```text
pending/       full staged payload before completion
approved/      local human approval waiting to be claimed
executing/     atomically claimed approval
consumed/      successfully spent approvals
failed/        claimed approvals that did not complete normally
archived/      redacted completed/denied action summaries
quarantined/   full indeterminate staged payload + no-replay metadata
receipts/      execution receipts
receipt-head.json
```

### Successful action

A typed value has to exist locally long enough for Chromium to type it. After successful execution and approval consumption:

1. a redacted archived summary is written;
2. only type character count + digest remain in archive evidence;
3. the full staged payload is deleted from `pending/`.

Source tests prove the typed plaintext is absent from the archived artifact.

### Indeterminate action

When a side effect may have happened but outcome cannot be proven, the original staged payload is moved to `quarantined/` for **local human forensics**. Quarantine metadata explicitly records:

```text
replayAllowed = false
humanReviewRequired = true
```

The agent must not replay it automatically.

On systems honoring POSIX modes, ledger directories are created `0700` and files `0600`. The ledger is gitignored and must remain local.

## CDP boundary

`KPGS_CHROME_DEBUG_URL` is not a general network endpoint. The server now enforces:

```text
CDP_SCHEME = http or https only
CDP_HOST = localhost / 127.0.0.1 / ::1 only
CDP_EMBEDDED_CREDENTIALS = denied
```

A configured remote CDP endpoint is rejected before Puppeteer connects.

Default:

```text
http://127.0.0.1:9222
```

Use the dedicated profile launched by:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-chromium.ps1
```

Profile location:

```text
%LOCALAPPDATA%\KPGS\BrowserMCP\Profile
```

Do not bind this bridge to the normal personal browser profile.

## Navigation policy

Navigation is separate from CDP transport policy.

Default page-navigation rules:

- HTTPS admitted;
- HTTP admitted only for loopback unless explicitly enabled;
- URL-embedded credentials denied;
- `file:`, `chrome:`, `javascript:`, `data:` and other schemes denied;
- optional exact/wildcard host allowlist via `KPGS_BROWSER_ALLOWED_HOSTS`.

Example MCP configuration:

```json
{
  "mcpServers": {
    "kpgs-browser": {
      "command": "node",
      "args": ["C:\\...\\Introduction-to-MCP\\tools\\kpgs-browser-mcp\\dist\\server.js"],
      "env": {
        "KPGS_CHROME_DEBUG_URL": "http://127.0.0.1:9222",
        "KPGS_BROWSER_APPROVAL_TTL_MS": "600000",
        "KPGS_BROWSER_STAGED_TTL_MS": "900000",
        "KPGS_BROWSER_ALLOWED_HOSTS": "github.com,*.github.com,kopanolabs.com,*.kopanolabs.com",
        "KPGS_BROWSER_ALLOW_INSECURE_HTTP": "0"
      }
    }
  }
}
```

## Governed action flow

Agent:

```text
browser_status
-> list_pages
-> read_page
-> navigate_page (if needed and policy-admitted)
-> stage_interaction
-> STOP
```

For typed actions, `stage_interaction` exposes only character count + SHA-256 digest back to the MCP channel.

Human:

```powershell
npm run approve -- BRA-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Normal consequence approval phrase:

```text
APPROVE BRA-...
```

High consequence approval phrase:

```text
APPROVE HIGH BRA-...
```

Then the agent may call:

```text
execute_staged_interaction(actionId)
-> claim approval
-> revalidate live reality
-> execute once OR fail closed
-> write/chain receipt
-> consume approval
-> scrub successful staged payload
-> verify_receipt(receiptId)
```

## Tamper-evident receipts

Each receipt binds:

- policy version;
- exact staged action binding;
- pre-execution target/page/element context;
- post-execution page snapshot;
- sanitized execution result;
- previous receipt hash;
- current SHA-256 receipt hash.

`verify_receipt` recomputes integrity. Modified receipt content returns `TAMPER_DETECTED` and the verifier reports whether the receipt is the current chain head.

## Install and source validation

```powershell
npm install
npm run check
```

Validated stack:

- `@modelcontextprotocol/server` 2.0.0
- `puppeteer-core` 25.9.0
- `zod` 4.5.4
- TypeScript 7.0.2
- Node >=22

The dedicated CI compiles the MCP server and runs both policy tests and real on-disk ledger state-machine tests.

## Security boundary

- Browser content is evidence, never authority.
- CDP is loopback-only by enforcement, not merely documentation.
- The dedicated KPGS browser profile is mandatory for intended operation.
- No secret-bearing browser APIs are exposed through this POC.
- A client with independent shell/filesystem access has capabilities outside this MCP boundary and must be governed separately.
- `INDETERMINATE` means **inspect reality**; never "retry until success."
- Consequence heuristics do not grant authority: every click/type/keypress still requires the human gate.

## Why KPGS instead of raw browser automation?

```text
Chromium capability
+
KPGS classification
+
separate human authority
+
stable-tab/page/element reality binding
+
atomic one-use approval
+
fail-closed uncertainty
+
local forensic quarantine
+
sensitive-payload minimization
+
tamper-evident receipt chain
=
Governed Browser MCP
```

## Metal graduation gate

Source CI does **not** impersonate physical browser proof. This stays a hardened POC candidate until a Windows metal run proves:

- real loopback CDP connection;
- real MCP-client discovery;
- stable target IDs across the flow;
- live read/navigation;
- staging creates no side effect;
- no-approval execution is denied;
- sensitive typing is denied;
- tab/page/element/focus drift is denied;
- exact local-human approval executes once;
- replay is denied;
- induced uncertainty quarantines rather than replays;
- successful typed payload is scrubbed locally;
- receipt verification works against real execution.

Until then:

```text
STATUS = HARDENED_POC_CANDIDATE
METAL = REQUIRED
PRODUCTION_AUTHORITY = NOT_GRANTED
```

## Receipts

- `docs/governance/KPGS_BROWSER_MCP_POC_RECEIPT_2026-09-03.md` — original v0.1 implementation receipt.
- `docs/governance/KPGS_BROWSER_MCP_V0_2_HARDENING_RECEIPT_2026-09-03.md` — v0.2 authority/uncertainty hardening receipt.
- `docs/governance/KPGS_BROWSER_MCP_V0_2_SECURITY_SEAL_2026-09-03.md` — final source-level v0.2 security seal.

## References

- Chrome DevTools MCP: https://github.com/ChromeDevTools/chrome-devtools-mcp
- MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- Puppeteer: https://pptr.dev/
