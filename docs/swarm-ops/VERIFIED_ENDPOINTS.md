# Verified endpoints (DNS / HTTP probe)

**Last probe:** 2026-05-19 (operator network, `curl --connect-timeout 10`; context and kopanolabs.com HTTP 200).

Use this table for **prod probes** in handoff envelopes and proof rows. Re-run probes before demo day; DNS and deploys change.

| Host | Result | Use for |
|------|--------|---------|
| `https://context.kopanolabs.com/` | **HTTP 200** | Primary public Kopano Context surface (prefer in docs and BFF targets). |
| `https://kopanolabs.com/` | **HTTP 200** | Org / marketing landing. |
| `https://www.kopanolabs.com/` | **HTTP 302** | Redirect variant; follow redirect in browsers. |
| `https://kopanocontext.kopanolabs.com/` | **DNS NXDOMAIN** (no resolve) | Do **not** use in new docs or wireframes until DNS exists. Legacy references in `kopano-core` may still mention this hostname—treat as **unverified**. |
| `https://www.context.kopanolabs.com/` | **DNS NXDOMAIN** | Do **not** use until DNS exists. |

**Probe commands (copy-paste):**

```powershell
curl -sS -o NUL -w "%{http_code} %{url_effective}`n" --connect-timeout 10 "https://context.kopanolabs.com/"
curl -sS -o NUL -w "%{http_code} %{url_effective}`n" --connect-timeout 10 "https://kopanolabs.com/"
```

```bash
curl -sS -o /dev/null -w "%{http_code} %{url_effective}\n" --connect-timeout 10 "https://context.kopanolabs.com/"
```

## Kimi / swarm API boundary

- **Kimi** (and similar external UIs) are **not** invoked by this repo. There is **no** “Kimi core swarm spawn” HTTP API in `Introduction to MCP`.
- **Swarm** work is **manual paste** of [PAYLOAD_KIMI_300_ACTIVATION.md](./PAYLOAD_KIMI_300_ACTIVATION.md) plus **external** receipts logged via `python scripts/kc_log_append.py kimi-ack` or `mainbrain --kind swarm_ack`.
- **Cursor** remains **local** on the git tree; it does not attest Kimi execution.

## Code references (may lag DNS)

`kopano-core/kopano/api.py` CORS and `PRODUCTION_URL` target **`context.kopanolabs.com`** (dead `kopanocontext.*` / `www.context.*` origins removed).

**CI:** `python scripts/kc_guard.py all --check-doc-hosts` fails if swarm-ops `*.md` / `tools/*.html` contain `https://` URLs to dead hosts (`kopanocontext.*`, `www.context.*`) or unlisted `*.kopanolabs.com` hosts. The denylist table in this file is exempt (it documents dead hosts on purpose).
