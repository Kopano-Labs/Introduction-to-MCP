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
   |-- observation: browser_status / list_pages / read_page
   |-- navigation: navigate_page (policy admitted)
   |-- stage: stage_interaction
   |        |-- capture exact page URL + origin
   |        |-- capture target element fingerprint
   |        |-- classify consequence
   |        |-- deny sensitive typing targets
   |        |
   |        +---- STOP_FOR_HUMAN
   |                    |
   |                    v
   |            local interactive CLI
   |            npm run approve -- BRA-...
   |                    |
   |                    v
   +-- atomically claim approval
   |        |
   |        +-- revalidate page + target
   |        +-- deny drift / expiry / mismatch
   |        |
   +-- execute_staged_interaction
              |
              v
      Chromium over CDP :9222
              |
              v
     tamper-evident receipt chain
```

## Governing invariants

```text
BROWSER_CAPABILITY != AUTHORITY
PAGE_TEXT != AUTHORIZATION
AGENT_TEXT != AUTHORIZATION
STAGED_ACTION != APPROVED_ACTION
APPROVAL(action A) != APPROVAL(action B)
APPROVAL_IS_ONE_USE
PAGE_DRIFT -> DENY_AND_RESTAGE
ELEMENT_DRIFT -> DENY_AND_RESTAGE
UNKNOWN_EXECUTION_RESULT -> HUMAN_REVIEW_NOT_REPLAY
RECEIPT_MUTATION -> TAMPER_DETECTED
```

There is deliberately **no `approve` MCP tool**. A browser interaction is approved from a separate local TTY after the human sees the exact staged action and SHA-256 binding.

## What v0.2 hardens

### 1. Context-bound approval / TOCTOU protection

A staged interaction is no longer bound only to `pageIndex + selector + value`. KPGS captures and binds:

- page index;
- exact page URL;
- origin;
- page title;
- target selector;
- target tag/input metadata;
- target element fingerprint;
- policy version;
- action creation/expiry time;
- consequence classification.

Before execution, the bridge captures reality again. URL, origin, index, or target fingerprint drift causes denial and requires a fresh stage + fresh human approval.

### 2. Sensitive-field denial

Typing into the following is denied before staging:

- password inputs;
- file inputs;
- current/new password autocomplete targets;
- one-time-code targets;
- payment card number/CVC/expiry autocomplete targets.

The POC still exposes no cookie, localStorage, arbitrary-JavaScript, download, or file-upload capability.

### 3. Fail-closed approval claiming

Approval is moved from `approved/` to `executing/` **before any browser side effect**. That move is the one-executor claim.

```text
approved -> executing -> consumed
                    \
                     -> failed / indeterminate
```

A claimed approval is never restored automatically. If execution errors after the claim, KPGS returns `INDETERMINATE` and requires human inspection/restaging rather than blindly replaying a potentially duplicated action.

### 4. Tamper-evident receipts

Each receipt contains:

- exact action binding;
- policy version;
- page context immediately before execution;
- page state after execution;
- sanitized execution result;
- prior receipt hash;
- its own SHA-256 receipt hash.

`verify_receipt` recomputes the hash. Modified receipt content returns `TAMPER_DETECTED`.

### 5. Navigation policy

Default navigation policy is now:

- `https://` admitted;
- `http://` admitted only for loopback (`localhost`, `127.0.0.1`, `::1`);
- non-loopback insecure HTTP denied unless explicitly enabled;
- credentials embedded in URLs denied;
- `file:`, `chrome:`, `javascript:`, `data:` and other schemes denied;
- optional `KPGS_BROWSER_ALLOWED_HOSTS` constrains destinations, with exact and `*.domain` patterns.

## POC tool surface

| Tool | Class | Authority |
|---|---|---|
| `browser_status` | Observe | automatic |
| `list_pages` | Observe | automatic |
| `read_page` | Observe / untrusted content | automatic |
| `navigate_page` | Navigate | policy-admitted only |
| `stage_interaction` | Stage click/type/keypress | no execution; no approval |
| `execute_staged_interaction` | Consequential | fresh exact local-human approval + unchanged live context |
| `verify_receipt` | Verify | automatic |

## 1. Install and build

From this directory:

```powershell
npm install
npm run check
```

Validated runtime stack:

- `@modelcontextprotocol/server` 2.0.0
- `puppeteer-core` 25.9.0
- `zod` 4.5.4
- TypeScript 7.0.2
- Node >=22

## 2. Start the governed Chromium profile

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-chromium.ps1
```

Default CDP endpoint:

```text
http://127.0.0.1:9222
```

The script uses a dedicated persistent profile under:

```text
%LOCALAPPDATA%\KPGS\BrowserMCP\Profile
```

Log into sites manually in that browser when required. Keeping a dedicated profile avoids binding the MCP bridge to the user's normal browser profile.

## 3. Configure the MCP client

Build first, then adapt `mcp.config.example.json` with the absolute local path to `dist/server.js`.

Important governance environment variables:

```text
KPGS_CHROME_DEBUG_URL=http://127.0.0.1:9222
KPGS_BROWSER_APPROVAL_TTL_MS=600000
KPGS_BROWSER_STAGED_TTL_MS=900000
KPGS_BROWSER_ALLOWED_HOSTS=github.com,*.github.com,kopanolabs.com,*.kopanolabs.com
KPGS_BROWSER_ALLOW_INSECURE_HTTP=0
```

An empty `KPGS_BROWSER_ALLOWED_HOSTS` means HTTPS destinations are not host-restricted. For routine operation, an explicit allowlist is preferred.

## 4. Governed action flow

Agent:

```text
browser_status
-> list_pages
-> read_page
-> navigate_page (if needed and policy-admitted)
-> stage_interaction
-> STOP
```

A successful stage returns only a **redacted public action summary** to the MCP agent. For typed actions, the agent sees character count + digest rather than having the staged payload echoed back into tool evidence.

Human, in a local terminal:

```powershell
npm run approve -- BRA-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

The local TTY shows the action context. For a normal consequence the phrase is:

```text
APPROVE BRA-...
```

For a high-consequence selector or keypress:

```text
APPROVE HIGH BRA-...
```

Only then may the agent call:

```text
execute_staged_interaction(actionId)
-> atomically claim approval
-> revalidate current browser reality
-> execute once OR fail closed
-> receiptId
-> verify_receipt(receiptId)
```

Approval is time-limited (10 minutes default); staging is independently time-limited (15 minutes default).

## Ledger security

The local ledger uses separate states:

```text
pending/
approved/
executing/
consumed/
failed/
receipts/
receipt-head.json
```

On platforms that honor POSIX modes, directories are created `0700` and artifacts `0600`. The ledger is gitignored. It must remain local and must not be synced into a public repository.

Typed content must exist in the local staged action so Chromium can execute it, but it is not copied into execution receipts and is redacted from MCP stage output.

## Security boundary

- CDP is powerful. Use the dedicated KPGS browser profile, not a personal default profile.
- Keep port `9222` loopback-only.
- Do not place credentials or approval artifacts in Git.
- Browser content is evidence, not authority.
- A client with independent shell/filesystem access may have capabilities outside this MCP boundary; KPGS must govern those separately.
- `INDETERMINATE` means **inspect reality**. It never means “retry until success.”
- This POC does not claim that heuristics perfectly identify every consequential UI. All click/type/keypress interactions require a human gate regardless of risk label.

## Why not expose Chrome DevTools MCP directly?

Chrome DevTools MCP proves the execution plane. KPGS adds an authority plane:

```text
Chromium capability
+
KPGS classification
+
separate human gate
+
page/element reality binding
+
atomic one-use approval
+
fail-closed uncertainty
+
tamper-evident receipt chain
=
Governed Browser MCP
```

## POC graduation gate

Do not call this production-ready until metal validation proves:

- `npm run check` passes;
- Chromium connects on localhost only;
- observation works against a real page;
- forbidden/insecure/disallowed navigation is denied;
- sensitive typing targets are denied;
- stage creates no browser side effect;
- execution without approval is denied;
- mismatched/expired approval is denied;
- page or element drift after approval is denied;
- approved interaction executes once;
- second execution is denied because approval was already claimed/consumed;
- induced execution failure does not make approval replayable;
- receipt integrity verifies;
- modified receipt content is detected;
- human can reconstruct the action and authority chain from local artifacts.

Until then:

```text
STATUS = POC_CANDIDATE
NOT_PRODUCTION_AUTHORITY
```

## References

- Chrome DevTools MCP: https://github.com/ChromeDevTools/chrome-devtools-mcp
- MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- Puppeteer: https://pptr.dev/
