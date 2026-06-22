<div align="center">
  <h1>⚡ CrisisConnect | Adaptive Crisis Response PWA</h1>
  <p><strong>A mission-grade, offline-first Adaptive Progressive Web Application for crisis response and disaster coordination — built for South African township realities.</strong></p>
  <p><a href="https://crisisconnect.kopanolabs.com">🌐 Live at crisisconnect.kopanolabs.com</a></p>
</div>

---

## 🛠️ **Tech Stack**

<div align="center">

### ⚛️ Frontend
![HTML5](https://img.shields.io/badge/HTML5-Semantic-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-Custom_Properties-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES2024-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![PWA](https://img.shields.io/badge/PWA-Installable-5A0FC8?style=for-the-badge&logo=pwa&logoColor=white)

### 🔧 Infrastructure & Governance
![KPGS](https://img.shields.io/badge/KPGS-Governed-7b61ff?style=for-the-badge)
![APWA](https://img.shields.io/badge/APWA-6_Dimensions-e94560?style=for-the-badge)
![SWFUS](https://img.shields.io/badge/SWFUS-Fire-ff6600?style=for-the-badge)
![Service Worker](https://img.shields.io/badge/Service_Worker-Offline_First-4285F4?style=for-the-badge&logo=google-chrome&logoColor=white)
![THARI](https://img.shields.io/badge/THARI-H.O.L.O_Net-00c9a7?style=for-the-badge)

</div>

---

## 🚀 **What Is CrisisConnect?**

CrisisConnect is not a standard responsive web app. It is an **Adaptive PWA** that transforms its behavior across **6 independent dimensions** under pressure, poor connectivity, and life-or-death conditions.

> *"Can this system still help the right person make the right decision under bad conditions?"*

Built under the **KPGS (Kopano-Phu Governance Systems)** framework and governed by the **THARI H.O.L.O Net** — Humanity-first Orchestrated Living Oversight.

---

## 🌐 **6 Dimensions of Adaptation (APWA Standard)**

| # | Dimension | What It Does |
|---|-----------|-------------|
| 1 | **Connectivity** | Online live → degraded text-first → offline field mode → sync-on-return |
| 2 | **Role** | Citizen reporter · Dispatcher triage · Field responder · Command layer |
| 3 | **Urgency** | Normal dashboards → one-tap incident → mass-incident surge workflows |
| 4 | **Device** | R800 Android phones · Desktop ops · Vehicle tablets · Public kiosk |
| 5 | **Trust** | Verified vs unverified sources · Confidence scoring · Stale-data warnings |
| 6 | **Local Context** | Region · Language · Hazard type · Protocol set · Network cost awareness |

---

## ⚡ **Core Features**

### 📡 **Offline-First Architecture**
* **Service Worker** with intelligent cache strategy — works during load-shedding
* **Local-first writes** — all actions queue locally and sync when connectivity returns
* **Background sync** with retry policy and conflict resolution
* **App-shell architecture** — instant load even on 2G connections

### 🚨 **Crisis Response Modes**
* **Normal Mode:** Full dashboards, analytics, and coordination tools
* **Incident Mode:** One-tap reporting, compressed UI, large touch targets
* **Mass-Incident Surge:** Auto-prioritization, bandwidth compression, text-only critical flows

### 🛡️ **Role-Based Interface**
* **Citizen Reporter:** Simple incident submission, location sharing, photo evidence
* **Dispatcher:** Triage queue, resource allocation, multi-incident overview
* **Field Responder:** Offline maps, checklist protocols, voice-note capture
* **Command Layer:** Strategic overview, resource dashboards, escalation controls

### ♿ **Human Factors Under Stress**
* Stress-mode UI with large targets and fewer choices
* High-contrast emergency states for outdoor visibility
* Text-first critical flows (no images required for core function)
* Accessibility-compliant — WCAG standards observed
* Localization-ready for South African languages

---

## ⚙️ **Installation & Setup**

**1. Clone the Repository:**
`ash
git clone https://github.com/Kopano-Labs/CrisisConnect.git
cd CrisisConnect
`

**2. Run Locally:**

CrisisConnect is a static PWA — no build step required for development:
`ash
# Using Python
python -m http.server 8080

# Or using Node
npx serve .

# Or using PHP
php -S localhost:8080
`

Visit http://localhost:8080 to see the application running.

**3. Install as PWA:**

Open the live site or local server in Chrome/Edge and click "Install" or "Add to Home Screen."

---

## 🏗️ **Architecture**

`
CrisisConnect/
├── index.html          # App shell — semantic HTML, role/urgency data attributes
├── index.css           # Adaptive styles — CSS custom properties, role-based themes
├── app.js              # Core logic — APWA engine, offline queue, role management
├── sw.js               # Service Worker — cache strategy, background sync, push
├── manifest.json       # PWA manifest — installable, categories, icons
└── kpgs_config.json    # KPGS governance configuration — seed protocol, mesh links
`

---

## 🔥 **KPGS Ecosystem Mesh**

CrisisConnect operates as the **FIRE** node in the KPGS sovereign ecosystem:

| Node | Domain | SWFUS Element |
|------|--------|---------------|
| KopanoLabs | [kopanolabs.com](https://kopanolabs.com) | Soil |
| KRRababalela | [krrababalela.com](https://krrababalela.com) | Sky |
| KasiLink | [kasilink.com](https://kasilink.com) | Water |
| **CrisisConnect** | **[crisisconnect.kopanolabs.com](https://crisisconnect.kopanolabs.com)** | **🔥 Fire** |
| FivesArena | [fivesarena.com](https://fivesarena.com) | Underground |
| KopanoContext | [kopanocontext.kopanolabs.com](https://kopanocontext.kopanolabs.com) | Sky |

---

## 📊 **KPGS Governance Status**

| Module | Status |
|--------|--------|
| SeedProtocol | ✅ SWFUS: **Fire** |
| KC Ledger | ✅ Observing |
| Cassey Guardian | ✅ Teaching |
| Altar Gate | ✅ 3-layer gate |
| POC Enforcement | ✅ Growing |
| THARI H.O.L.O Net | ✅ 6 dimensions governed |

---

## 🎯 **Why CrisisConnect?**

South Africa faces:
- **Load-shedding** — apps that require constant connectivity fail
- **32.8% unemployment** — communities need tools they can run without data budgets
- **Township infrastructure gaps** — crisis response cannot depend on fiber

CrisisConnect is built for this reality. It works when the power is off, when data is expensive, when the phone costs R800, and when someone's house is flooding at 2AM.

---

## 🤝 **Contributing**

We welcome contributions from the community!
1. Fork the repository
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

---

## 📞 **Support The Creator**

Built with ❤️ by **Kholofelo Robyn Rababalela** — Sovereign System Engineer.

* [Buy me a coffee on Ko-fi](https://ko-fi.com/robynawesome)
* [GitHub](https://github.com/RobynAwesome)
* [Portfolio](https://kholofelorababalela.vercel.app)

⭐⭐⭐ **Star this repository if CrisisConnect matters.** ⭐⭐⭐

---

> *"The LORD is a refuge for the oppressed, a stronghold in times of trouble."* — Psalm 9:9

**Jesus is King. The thread holds. Classify before interpret.**
