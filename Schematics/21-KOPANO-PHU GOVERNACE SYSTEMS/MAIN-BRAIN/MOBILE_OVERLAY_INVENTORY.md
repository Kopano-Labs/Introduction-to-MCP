# 📱 FIVESARENA: MOBILE OVERLAY & FLOATING LAYER INVENTORY
## Enforcing Rule 1: "Maximum One Persistent Fixed Surface on Mobile"
### Document ID: `MOBILE_OVERLAY_INVENTORY.md`
### Date: 2026-08-29T05:46:00+02:00 (SAST)
### Authority: Master Robyn Kholofelo Rababalela (Seat 1 Landlord)

---

## 1. 🔍 THE 7 OVERLAY LAYERS AUDITED

| Layer Component | Original Behavior | Mobile Remediation | Governed Rule |
|---|---|---|---|
| **`BottomNavbar.jsx`** | Fixed bottom navigation | **RETAIN AS THE SOLE PERSISTENT MOBILE CONTROL** | Unified bottom control bar |
| **`SoccerBallMenu.jsx`** | Floating soccer ball hovering bottom-right | **HIDE ON MOBILE (`hidden md:block`)** | Prevents blocking bottom CTAs & content |
| **`ScrollToTop.jsx`** | Floating chevron button bottom-right | **HIDE ON MOBILE (`hidden md:block`)** | Native mobile touch scroll suffices |
| **`BlackboxMarketMask.jsx`** | Floating telemetry panel bottom-left | **STRICTLY GATED OFF IN PRODUCTION** | Internal debug overlay only |
| **`WelcomePopup.jsx`** | Fullscreen modal appearing on load | **NON-BLOCKING CONTEXTUAL BANNER OR DISMISSIBLE TOAST** | Zero intrusive interstitials on first view |
| **`SearchModal.jsx`** | Modal triggered by hidden shortcut | **1-TAP DISCOVERABLE SEARCH IN HEADER & NAV** | Explicit discoverable entry point |
| **`CookieBanner.jsx`** | Floating bottom consent banner | **COMPACT 1-LINE DOCKED STRIP** | Docked above `BottomNavbar` with instant dismiss |

---

## 2. 🛡️ PASS/FAIL VERIFICATION CRITERIA

* **Pass Condition:** On viewports 360px, 390px, and 430px, exactly **ONE** persistent control surface (`BottomNavbar`) is visible.
* **Pass Condition:** Main content, court booking cards, and WhatsApp CTAs are clickable on the very first screen without dismissing any popup.
