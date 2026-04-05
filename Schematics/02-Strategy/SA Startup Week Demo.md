---
title: SA Startup Week Demo
created: 2026-04-05
updated: 2026-04-05
author: Robyn
tags:
  - strategy
  - hackday
  - demo
  - startup-week
priority: critical
status: planned
---

# SA Startup Week Hack Day Demo

> April 15-17, 2026
> See also: [[KasiLink Integration Plan]], [[Microsoft Contract Strategy]]

## Pitch

**"KasiLink — The AI-Powered Booking OS for Township Entrepreneurs"**

## Demo Flow (3 Minutes)

1. Customer in Soweto needs a car wash -> posts gig on KasiLink
2. AI agents (via Orch) deliberate on best provider match — show reasoning live
3. Loadshedding check: "This gig needs water pressure — no loadshedding in Diepkloof until 6pm, safe to book"
4. Provider gets WhatsApp notification: "New car wash gig, R150, Diepkloof, 2pm. Reply YES"
5. Show AI Dashboard: transparent reasoning, sentiment scores, demand forecast

## 3 Features to Demo

1. **AI-Powered Gig Matching** with visible reasoning (Orch simulation engine)
2. **Loadshedding-Aware Scheduling** (new loadshedding tool)
3. **WhatsApp Gig Notifications** (existing bridge, extended)

## Preparation Timeline

| Day | Focus |
|-----|-------|
| April 5-8 | Orch KasiLink API gateway + new tools |
| April 9-11 | KasiLink frontend integration |
| April 12-14 | Deploy to Railway, end-to-end testing |
| April 15-17 | Hack Day: demo, pitch, network |

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Orch API too slow | Pre-seed responses, use fast models |
| Railway free tier limits | Azure free tier as backup |
| LLM API costs spike | Set max_tokens=1024, cache responses |
| WhatsApp unreliable | Screenshot fallback |
| Loadshedding data unavailable | Hardcode Soweto schedule |

## Talking Points

- R1 trillion township economy with zero digital infrastructure
- 60% youth unemployment — KasiLink creates instant gig access
- AI transparency — users see WHY they were matched
- Works offline, on WhatsApp, during loadshedding
- Built by a South African developer, for South Africans
