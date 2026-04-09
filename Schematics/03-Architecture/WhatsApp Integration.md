---
title: WhatsApp Integration Guide
created: 2026-04-03
updated: 2026-04-05
author: Robyn
tags:
  - architecture
  - whatsapp
  - phase-3
  - integration
priority: high
status: active
---

# WhatsApp Integration Guide (Phase 3)

> Connect orch AI agents to your phone using the **Evolution API** bridge.
> See also: [Orch Blueprint](../01-Mission/Orch%20Blueprint.md), [CLI Specification](CLI%20Specification.md), [Project Status](../04-Updates/Project%20Status.md)

## 1. Start the Messaging Bridge

Run a local bridge using Docker:

```bash
docker run -d --name evolution-api -p 8080:8080 atendaware/evolution-api
```

## 2. Pairing Your Phone

1. Open your browser to: `http://localhost:8080` (or your Instance URL)
2. Generate a new Instance (e.g., name it `main`).
3. **Scan the QR Code** with your personal WhatsApp (Settings > Linked Devices).

## 3. Configure orch

Update your `.env` file with your bridge credentials:

```env
WHATSAPP_API_KEY=your_evolution_api_key_here
WHATSAPP_INSTANCE_URL=http://localhost:8080
WHATSAPP_INSTANCE_NAME=main
WHATSAPP_RECIPIENT=1234567890@s.whatsapp.net
```

## 4. Launch the Gateway

Run a simulation and add the `-w` flag:

```bash
python -m orch.cli serve launch --topic "Artificial General Intelligence" --agents "grok" --max-rounds 2 --whatsapp
```

> [!TIP]
> **Groups**: You can also send to a WhatsApp Group by finding its **Group JID** (e.g., `1234567890@g.us`) and putting it in the `WHATSAPP_RECIPIENT` field!

## KasiLink Integration

With the [KasiLink Integration Plan](../02-Strategy/KasiLink%20Integration%20Plan.md), the WhatsApp bridge extends to support:
- Gig notifications to providers
- Booking confirmations to seekers
- Loadshedding alerts for scheduled gigs
