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

# 4. Launch the stack
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
