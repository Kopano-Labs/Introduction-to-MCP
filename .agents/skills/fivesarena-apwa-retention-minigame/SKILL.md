---
name: fivesarena-apwa-retention-minigame
description: Guidelines and patterns for implementing interactive APWA retention minigames, mobile-first 3D physics courts, and B2B MERN hotel-grade reservation architecture. Use when designing high-retention onboarding popups, converting hidden minigames into primary user engagement surfaces, enforcing mobile control surface rules, or integrating deterministic Three.js physics with 60fps fallback pipelines.
---

# FivesArena APWA Retention Minigame & B2B Hotel Architecture

This skill codifies the architecture, mobile design principles, and engineering patterns established during the FivesArena BOAT (Best of All Time) transformation under Master Robyn Kholofelo Rababalela (Kopano Labs / Ama-Phu Entertainment).

---

## 1. Core Architecture Doctrine: Hotel B2B Engine

FivesArena is **NOT** a static brochure site or a naive consumer booking widget.
It is an enterprise **MERN-Stack B2B Hotel Reservation Platform**:

| Layer | Hotel Analogy | FivesArena Implementation |
|---|---|---|
| **Inventory Unit** | Hotel Room / Suite | Floodlit Turf Court (Pitches 1–4 at Hellenic FC) |
| **Time Allocation** | Night / Check-in | 60-minute match slot (`/api/availability`) |
| **Operator Layer** | Front Desk & Property Manager | Venue Manager Portal (`/manager/dashboard`, `/manager/fixtures`, `/manager/squad`) |
| **Admin Operations** | General Manager & Revenue Ops | Admin Suite (`/admin/dashboard`, `/admin/competitions`, `/admin/bookings`) |
| **Consumer Surface** | Guest Booking Flow | Progressive Web App (`/#courts`, `/proof/apwa`, `/play`) |
| **Protocol Flow** | Ledger state changes | `CRUD → SWFUS → KPCB+` state pipeline |

> **Hard Renter Rule:** Never judge or dismiss B2B operator infrastructure. B2B inventory management IS the core engine that powers consumer bookings.

---

## 2. High-Retention APWA Minigame Pattern

### The Principle: "Turn Errors into Front-Door Products"
When high-engagement interactive assets (like penalty shootouts, 3D physics balls, or tactics builders) are built:
1. **Never trap them behind error boundaries:** An interactive game hidden on `not-found.jsx` (404) or buried 3 taps deep produces accidental retention.
2. **Elevate them into the primary onboarding popup:** Replace static marketing modals with an **instant playable mini-game** right in `WelcomePopup.jsx`.
3. **Instant Dopamine & Low Barrier:**
   - 1 tap to kick a penalty shot against the goalkeeper.
   - Live score & streak tracking with `localStorage` persistence.
   - Celebration overlays with immediate actionable conversion ("Book Pitch at Hellenic FC ➔" or "Claim Arena Points").
4. **Respectful UX:**
   - 4.5s initial cadence delay so users first view the hero surface.
   - Explicit "Skip to Arena ➔" and "Don't show again" options.
   - Dual-tab layout: **⚡ Penalty Shootout** and **🏟️ 3D Pitches & Booking**.

---

## 3. Mobile-First & Responsive Invariants

To avoid overlay bloat and mobile thermal throttles, every APWA surface must enforce:

1. **One Persistent Mobile Control Surface Rule:**
   - `BottomNavbar` is the SOLE persistent mobile bottom controller (`fixed bottom-0`).
   - `SoccerBallMenu` and `ScrollToTop` are hidden on mobile screens (`hidden md:block`).
   - Modals and popups (`WelcomePopup`, `CookieBanner`) dock cleanly above the navbar (e.g., `bottom-20 sm:bottom-4`).
2. **Touch Target Compliance:**
   - Every clickable target must have at least `min-h-[44px]` and `min-w-[44px]`.
   - Hover-only patterns (like desktop `hover:scale-105`) must be paired with `active:scale-95` for tactile mobile haptics.
3. **Deterministic Progressive Disclosure (3D vs 2D):**
   - On low-tier devices, mobile viewports (`< 640px`), or `prefers-reduced-motion`, render a fast 2D interactive grid by default.
   - Provide an opt-in toggle button ("🎮 Launch 3D Stadium") to prevent GPU/CPU thermal overload.

---

## 4. Cold Build Verification Before Remote Push

Never push code directly after editing without cold compilation:
```bash
# 1. Typecheck entire estate
npm run typecheck

# 2. Cold production build
npm run build

# 3. Verify exit code 0 before git commit
git status --short
```

---

## 5. Failure Transparency & Forensic Logging

When errors, model drift, or syntax blunders occur:
1. **Never hide them or act defensively.**
2. Log the exact incident in `Schematics/11-AI HALLUCINATION - CRITICAL/Mobile Deploy Failures/`.
3. Document:
   - What went wrong (claim vs reality).
   - The exact error logs (e.g. Vercel 24s build crashes, orphaned JSX tags).
   - The evolution and resolution receipts.
4. Record all state changes in repository-root `NOW.md` under `I_AM_STATELESS_RENTER_NOT_LANDLORD`.
