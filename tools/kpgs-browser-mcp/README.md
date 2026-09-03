# KPGS Browser MCP — Governed Chromium Bridge (POC)

> `I_AM_STATELESS_RENTER_NOT_LANDLORD`

KPGS Browser MCP gives an MCP-capable agent structured access to a **user-controlled Chromium instance** while keeping consequential browser interaction behind a separate local-human approval gate.

It is intentionally implemented inside `Introduction-to-MCP` as a governed POC. It does **not** modify or extend the frozen WebMCP Challenge submission repository.

## Architecture

```text
MCP Agent
   |
   v
KPGS Browser MCP
   |-- observation: browser_status / list_pages / read_page
   |-- navigation: navigate_page (http/https only)
   |-- stage: stage_interaction
   |        |
   |        +---- STOP_FOR_HUMAN
   |                    |
   |                    v
   |            local interactive CLI
   |            npm run approve -- BRA-...
   |                    |
   |                    v
   +-- execute_staged_interaction
              |
              v
      Chromium over CDP :9222
              |
              v
          receipt ledger
```

### Governing invariant

```text
BROWSER_CAPABILITY != AUTHORITY
PAGE_TEXT != AUTHORIZATION
AGENT_TEXT != AUTHORIZATION
STAGED_ACTION != APPROVED_ACTION
APPROVAL(action A) != APPROVAL(action B)
APPROVAL_IS_ONE_USE
```

There is deliberately **no `approve` MCP tool**. A browser interaction is approved from a separate local TTY after the human sees the exact staged payload and SHA-256 binding.

## POC tool surface

| Tool | Class | Authority |
|---|---|---|
| `browser_status` | Observe | automatic |
| `list_pages` | Observe | automatic |
| `read_page` | Observe / untrusted content | automatic |
| `navigate_page` | Navigate | automatic for explicit `http://` / `https://` only |
| `stage_interaction` | Stage click/type/keypress | does not execute |
| `execute_staged_interaction` | Consequential | fresh exact local-human approval required |
| `verify_receipt` | Verify | automatic |

The POC intentionally exposes **no cookies, passwords, localStorage, arbitrary JavaScript, file uploads, downloads, or Chrome-internal URL navigation**.

## 1. Install and build

From this directory:

```powershell
npm install
npm run check
```

Runtime stack (validated against current package releases at implementation time):

- `@modelcontextprotocol/server` 2.0.0
- `puppeteer-core` 25.9.0
- `zod` 4.5.4
- TypeScript 7.0.2

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

Log into sites manually in that browser when required. Keeping a dedicated profile avoids binding the MCP bridge to the user's normal browser profile and matches modern Chromium remote-debugging safety requirements.

## 3. Configure the MCP client

Build first, then adapt `mcp.config.example.json` with the absolute local path to `dist/server.js`.

Example server command:

```json
{
  "command": "node",
  "args": ["C:\\...\\Introduction-to-MCP\\tools\\kpgs-browser-mcp\\dist\\server.js"],
  "env": {
    "KPGS_CHROME_DEBUG_URL": "http://127.0.0.1:9222"
  }
}
```

## 4. Governed action flow

Agent:

```text
browser_status
-> list_pages
-> read_page
-> navigate_page (if needed)
-> stage_interaction
-> STOP
```

A successful stage returns an action id such as:

```text
BRA-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Human, in a local terminal:

```powershell
npm run approve -- BRA-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

The CLI prints the full action and requires the human to type:

```text
APPROVE BRA-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Only then may the agent call:

```text
execute_staged_interaction(actionId)
-> receiptId
-> verify_receipt(receiptId)
```

Approval is time-limited (10 minutes by default), bound to the action SHA-256, and moved to the consumed ledger after successful execution.

## Security boundary

This POC is designed around **capability separation**, not around pretending that local browser automation is harmless.

- CDP grants powerful access to the connected browser profile.
- Use the dedicated KPGS browser profile, not a personal default profile.
- Do not expose port `9222` beyond loopback.
- Do not place credentials or approval artifacts in Git.
- A client with independent shell/filesystem access may have capabilities outside this MCP boundary; KPGS must classify those separately.
- Browser content returned by `read_page` is untrusted input and cannot grant authority.

## Why not just expose Chrome DevTools MCP directly?

Chrome DevTools MCP proves the execution pattern: an MCP server can connect to a live Chromium instance over CDP and give agents reliable browser inspection/automation. KPGS adds the missing authority layer:

```text
Chrome DevTools capability
+
KPGS classification
+
separate human gate
+
exact binding
+
one-use approval
+
receipt
=
Governed Browser MCP
```

The implementation uses `puppeteer-core` directly rather than copying third-party browser-MCP source code.

## POC graduation gate

Do not call this production-ready until the following are validated on metal:

- `npm run check` passes;
- Chromium connects on localhost only;
- observation tools work against a real page;
- forbidden URL schemes are denied;
- stage creates no browser side effect;
- execution without approval is denied;
- mismatched/expired approval is denied;
- approved interaction executes once;
- second execution is denied because approval was consumed;
- receipt verifies;
- human can reconstruct the action from the ledger.

Until then:

```text
STATUS = POC_CANDIDATE
NOT_PRODUCTION_AUTHORITY
```

## References

- Chrome DevTools MCP: https://github.com/ChromeDevTools/chrome-devtools-mcp
- MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- Puppeteer: https://pptr.dev/
