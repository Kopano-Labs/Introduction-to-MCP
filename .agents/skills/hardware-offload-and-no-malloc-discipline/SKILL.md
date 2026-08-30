---
name: hardware-offload-and-no-malloc-discipline
description: Governed protocol and automated toolkit for reclaiming disk space, purging npm/temp caches, retrimming NVMe SSDs, and maintaining the 'No Malloc Margin' on local hardware until dedicated GSMB 2 device offloading is established.
---

# Hardware Offload & No Malloc Margin Discipline

> **Canonical Authority:** GSMB Distribution Trinity & Master Robyn Kholofelo Rababalela  
> **Purpose:** Prevent hardware memory/disk exhaustion (`ENOMEM`, `ENOSPC`, no-malloc crashes) during high-throughput local AI development, build cycles, and 3D simulation on the Black Beast (AMD Ryzen 7 5800H).

## When to Activate This Skill
Trigger this skill whenever:
1. Local disk space on drive `C:` drops below **15 GB** (The *No Malloc Margin* red-alert threshold).
2. Next.js, Webpack, Vite, or Turbopack builds stall with heap allocation or disk-exhaustion errors.
3. Repositories experience sluggish `git status` / `git diff` operations.
4. Preparing for heavy Three.js / APWA / AI fine-tuning sprints before offloading to dedicated GSMB 2 hardware.

---

## The 4-Tier Hardware Hygiene Pipeline

```text
[ TIER 1: CACHE PURGE ]  -->  [ TIER 2: SYSTEM DUMP CLEAN ]  -->  [ TIER 3: NVMe RETRIM ]  -->  [ TIER 4: GIT REPACK ]
      npm + pip + temp             WER + WinUpdate Download           Optimize-Volume -ReTrim          git gc --prune=now
```

### 1. Tier 1: Cache & Temp Purge
* **NPM Cache:** Deep-purges `AppData\Local\npm-cache` and runs `npm cache clean --force`.
* **User Temp:** Purges unlocked files in `AppData\Local\Temp`.
* **Puppeteer / Headless Browsers:** Cleans redundant Chromium binaries in `.cache\puppeteer`.
* **Session Media Blobs:** Safely purges orphan `.tempmediaStorage` folders from completed agent sessions while preserving active conversation directories.

### 2. Tier 2: System Dumps & Updates
* **Windows Update Cache:** Cleans out `C:\Windows\SoftwareDistribution\Download` installer leftovers.
* **Crash Dumps:** Cleans `%LOCALAPPDATA%\CrashDumps`.
* **DNS Resolver:** Flushes DNS cache via `ipconfig /flushdns`.

### 3. Tier 3: NVMe SSD ReTrim
* Re-trims freed flash memory blocks using `Optimize-Volume -DriveLetter C -ReTrim` to restore peak read/write IOPS and minimize write amplification.

### 4. Tier 4: Git Object Compaction
* Executes `git gc --prune=now` across core working repositories (`Bookit-5s-Arena`, `Introduction to MCP`, `kasi-link-clean`) to compress loose objects into consolidated packfiles.

---

## One-Line Execution

To run the automated hygiene routine, execute the bundled script:

```powershell
powershell -ExecutionPolicy Bypass -File .\.agents\skills\hardware-offload-and-no-malloc-discipline\scripts\offload_hardware.ps1
```

---

## Strategic Roadmap: Bridge to GSMB 2
This skill serves as the **bridge maintenance protocol** on the current machine (Black Beast) until **GSMB 2** is deployed on a dedicated separate hardware server. 

Refer to the full governance schematic:
[`Schematics/18-PROTOCOLS/Hardware-Maintenance-And-GSMB2-Offload-Protocol.md`](file:///c:/Users/rkhol/OneDrive/Documents/Anthropic/Introduction%20to%20MCP/Schematics/18-PROTOCOLS/Hardware-Maintenance-And-GSMB2-Offload-Protocol.md).
