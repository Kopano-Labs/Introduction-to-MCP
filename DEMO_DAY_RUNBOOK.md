# Kopano Context — Demo Day Runbook
**Demo Day: April 15-17, 2026 | SA Startup Week Hack Day**
**Status: FULL STACK DEMO READY**

---

## Pre-Demo Checklist (Run the morning of)

```bash
# 1. Run Atlas connectivity check
python scripts/check_atlas.py

# 2. Run preflight
powershell -ExecutionPolicy Bypass -File .\scripts\demo_day_preflight.ps1

# 3. Run smoke test
python scripts/demo_day_smoke.py --strict

# 4. Swarm logs — validate + proof gate (must pass before "demo ready")
python scripts/kc_log_append.py validate
python scripts/kc_log_append.py proof-check

# 5. Append KC student audit (strict proof — real CI/job URL required)
python scripts/kc_log_append.py review --strict-proof --role student --phase audit \
  --summary "Demo preflight + smoke complete" \
  --commands python scripts/demo_day_smoke.py --strict \
  --exit-code 0 \
  --evidence-url "<PASTE_CI_OR_ARTIFACT_URL>"

# 6. Launch the stack
python main.py serve api
```

Access Studio at: `http://localhost:8000`
Production: [www.context.kopanolabs.com](https://www.context.kopanolabs.com)

---

## Demo Route (LOCKED)

```
Council  →  Labs  →  Console  →  Forge  →  Admin Audit
```

### Step 1 — Council
- Open the Kopano Context multi-agent discussion panel
- Show: Moderator AI routing messages between Anthropic (Claude), Google (Gemini), xAI (Grok)
- Talking point: "Every voice in the room is a different AI provider — Kopano Context orchestrates them"

### Step 2 — Kopano Labs
- Navigate to the Labs gallery
- Show: Gig Matcher, Loadshedding Planner, SA Language Engine
- Talking point: "These are South African-first impact tools — built for township economies"

### Step 3 — Console
- Show the live agent console and discussion logs
- Show: SQLite data lake persistence (every discussion is saved for audit and training)
- Talking point: "Kopano Context is an audit-first platform — nothing is hidden"

### Step 4 — Kopano Forge
- Show the collaborative execution canvas
- Talking point: "Forge is where ideas become structured AI workflows"

### Step 5 — Admin Audit
- Show the Microsoft readiness dashboard
- Show: Azure OpenAI integration, Application Insights telemetry (South Africa North region)
- Show: SafeSkill 100/100 score
- Talking point: "6/6 Microsoft readiness checks — zero hardcoded secrets, full observability"

---

## Owner-Blocked (Do Not Demo)

- WhatsApp live phone route — device registration pending
- Full KasiLink marketplace walkthrough — Clerk + Atlas auth — owner must confirm
- Reward/referral live flow — documentation only

---

## Swarm proof & verification gate (doctrine)

Client-facing demos are **audit-before-presentation** (**Protocol 13**). Narrative-only “green” is not evidence. **Honest handoff:** seed Main Brain receipts before claiming demo-ready.

**Canonical SOP:** [Swarm Ops & Proof Doctrine](./docs/swarm-ops/SWARM_OPERATIONS.md) — proof bar (commands, exit/HTTP, logs/CI URLs, SHA, prod probes; chat-only proofs excluded), Kimi-external vs Cursor-local boundary, handoff envelope.

**Machine-checkable demo stack (this repo):** Run every step in **Pre-Demo Checklist** above; then from repo root: `python scripts/kc_guard.py all` (must exit 0) and `python -m pytest tests/test_kc_log_append.py tests/test_kc_guard.py -q`. Capture **stdout**, **CI job URLs** ([Actions](https://github.com/Kopano-Labs/Introduction-to-MCP/actions)), and prod probe output per [VERIFIED_ENDPOINTS.md](./docs/swarm-ops/VERIFIED_ENDPOINTS.md). Claims of “demo ready” without those attachments fail the gate until receipts are filed.

**KC apprenticeship logs (mandatory for swarm doctrine demos):** After steps 1–4, append a **strict-proof** student audit (real `--evidence-url`). Until `validate` + `proof-check` pass and a new audit row is appended, treat demo readiness as **unverified**. Canonical navigation: [docs/swarm-ops/NAVIGATION.md](./docs/swarm-ops/NAVIGATION.md).

---

## Emergency Recovery

If the API crashes during demo:
```bash
# Restart from the exe (no Python needed)
dist\KopanoContext.exe
```

If Studio won't load:
```bash
cd kopano-core/studio
npm run dev
```

---

## Key Contacts

- Creator / Owner: RobynAwesome — [rkholofelo@context.kopanolabs.com](mailto:rkholofelo@context.kopanolabs.com)
- Lead Coder: Claude (Anthropic)
- Lead Developer: Codex
- DEV_1: Germini (Google AI)
