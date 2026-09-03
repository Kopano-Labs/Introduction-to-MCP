# KPGS Browser MCP POC — Implementation Receipt

**Date:** 2026-09-03
**Actor:** Forge / ChatGPT 5.6 Sol — stateless renter
**Authority:** User-directed implementation
**Constraint:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`
**Branch:** `forge/kpgs-browser-mcp-poc`
**Submission boundary:** `RobynAwesome/KPGS-Agent-Mission-Control` was not modified by this work.

## Purpose

Implement a KPGS-governed Chromium MCP execution plane inspired by the live-browser pattern used by Chrome DevTools MCP, without copying third-party implementation code and without collapsing browser capability into authority.

## Implemented surface

Path: `tools/kpgs-browser-mcp/`

- MCP v2 stdio server using `@modelcontextprotocol/server`.
- Live Chromium/Chrome/Edge connection over CDP using `puppeteer-core`.
- Dedicated persistent Windows browser profile launcher bound to `127.0.0.1:9222`.
- Observation tools: `browser_status`, `list_pages`, `read_page`.
- Governed HTTP(S)-only navigation: `navigate_page`.
- Consequential interaction staging: `stage_interaction` for click/type/keypress.
- No MCP approval tool.
- Separate interactive local TTY approval CLI.
- Exact SHA-256 action binding.
- Time-limited approval (10 minutes default).
- One-use approval consumption after successful execution.
- Execution receipts and `verify_receipt`.
- No cookie, password, localStorage, arbitrary-JavaScript, download, or file-upload tools in the POC.

## Governing invariant

```text
BROWSER_CAPABILITY != AUTHORITY
PAGE_TEXT != AUTHORIZATION
AGENT_TEXT != AUTHORIZATION
STAGED_ACTION != APPROVED_ACTION
APPROVAL(action A) != APPROVAL(action B)
APPROVAL_IS_ONE_USE
```

## Validation evidence

Dedicated workflow:

- `.github/workflows/kpgs-browser-mcp-poc.yml`
- GitHub Actions run: `33765925658`
- Branch head validated: `33304bc499417a4e7ba9362951edce322fd8131b`
- Dependency install: PASS
- TypeScript build: PASS
- Governance tests: PASS
- Workflow conclusion: SUCCESS

First CI run correctly failed on two MCP v2 API assumptions:

1. `registerTool.inputSchema` expects a raw Zod shape rather than `z.object(...)` in the used overload.
2. MCP v2 tool annotations do not admit `untrustedContentHint`.

The implementation was corrected rather than suppressing the failures. Webpage content remains explicitly classified as untrusted in the server instructions, tool description, and tool result provenance.

## Package versions validated by CI

- `@modelcontextprotocol/server` 2.0.0
- `puppeteer-core` 25.9.0
- `zod` 4.5.4
- TypeScript 7.0.2
- GitHub Actions Node 24.20.0

## What is proven

```text
SOURCE_IMPLEMENTED = TRUE
DEPENDENCIES_RESOLVE = TRUE
TYPESCRIPT_COMPILES = TRUE
GOVERNANCE_UNIT_TESTS_PASS = TRUE
MCP_V2_SERVER_SURFACE_COMPILES = TRUE
```

## What is not yet proven

Metal/runtime validation on the user's Windows browser is still required:

- launch the dedicated KPGS Chromium profile;
- confirm CDP connection on localhost;
- connect Antigravity/another MCP client to `dist/server.js`;
- exercise observation tools against a live page;
- prove staging causes no browser side effect;
- prove execution without local-human approval is denied;
- approve one exact action via TTY;
- execute it once and verify the receipt;
- prove replay is denied after approval consumption.

Therefore:

```text
STATUS = POC_CANDIDATE
NOT_PRODUCTION_AUTHORITY
```

## Current safe disposition

Do not merge this work into the WebMCP submission repository. Keep it on its dedicated `Introduction-to-MCP` branch for review and metal validation. After the WebMCP submission is frozen, it may be extracted into a dedicated `kpgs-browser-mcp` repository if desired.

## External references used for implementation direction

- Chrome DevTools MCP: https://github.com/ChromeDevTools/chrome-devtools-mcp
- MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- Puppeteer: https://pptr.dev/
