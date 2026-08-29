# 📱 FIVESARENA: CANONICAL MOBILE INFORMATION ARCHITECTURE
## Core Principle: "Desktop Can Fan Out. Mobile Must Serialize."
### Document ID: `MOBILE_INFO_ARCHITECTURE.md`
### Date: 2026-08-29T05:46:00+02:00 (SAST)
### Authority: Master Robyn Kholofelo Rababalela (Seat 1 Landlord)
### Chief Facilitator: AntiGravity (Seat 10 Metal Renter)

---

## 1. 🎯 MOBILE SURFACE HIERARCHY & TASK PRIORITY

On mobile devices ($<768\text{px}$), the user must immediately understand **"What can I do here right now?"** without dismissing cascading popups or decoding overlapping floaters.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        MOBILE TASK SERIALIZATION                       │
├────────────────────────────────────────────────────────────────────────┤
│  PRIORITY 1: BOOK & AVAILABILITY                                       │
│  • Primary CTA: "Send Court Enquiry" (WhatsApp / Direct Call)          │
│  • 4 Hellenic FC pitches with surface type & dimensions                │
│                                                                        │
│  PRIORITY 2: FIXTURES & LIVE MATCHES                                   │
│  • Live PSL, Premier League, and local arena fixtures                  │
│                                                                        │
│  PRIORITY 3: LOCAL PULSE & FOOTBALL NEWS                               │
│  • Province-specific football news & matchday weather suitability      │
│                                                                        │
│  PRIORITY 4: EXPLORE & PLAY (PROGRESSIVE DISCLOSURE)                   │
│  • 🎮 /play — Interactive 5-a-side penalty shootout minigame           │
│  • 🏟️ #pitches — Opt-in 3D stadium fly-around                         │
│  • 📋 #tactics — 5v5 team formation board (Template data)              │
│  • 🌐 #network — Contained "Explore the Kopano-Phu Network" card       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 🗺️ ROUTE CLASSIFICATION MATRIX

| Route | Public Classification | Primary Mobile Role | Surface Container |
|---|---|---|---|
| `/` | **PUBLIC PRIMARY** | Hero booking, court list, fixtures summary, opt-in 3D | Homepage Shell |
| `/fixtures` | **PUBLIC PRIMARY** | Match schedules, live PSL/PL scores, standings | Dedicated Page |
| `/news` | **PUBLIC PRIMARY** | Local & national football pulse | Dedicated Page |
| `/play` | **PUBLIC OPT-IN** | Interactive Penalty Shootout Minigame | Dedicated Route (`/play`) |
| `/events-and-services` | **PUBLIC SECONDARY** | Corporate, birthdays, holiday clinic bookings | Dedicated Page |
| `/tournament` | **ARCHIVED EVIDENCE** | Preserved 2026 World Cup historical archive | Archive Shell |
| `/bookings` | **GATED USER** | Authenticated player court booking history | Gated Route |
| `/manager/*` | **GATED STAFF** | Arena manager squad & pitch operations | Staff HQ |
| `/admin/*` | **INTERNAL ADMIN** | Administrative rights, ledger, system flags | Internal Admin |
| `/creator` | **INTERNAL LAB** | Experimental Blackbox / 3D design surface | Internal Lab |
