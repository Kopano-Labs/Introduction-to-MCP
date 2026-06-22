---
title: Kairos Reference
created: 2026-04-04
updated: 2026-04-05
author: Lead (Claude Opus 4.6)
tags:
  - training
  - reference
  - kairos
  - claude-code
priority: medium
status: active
---

# Kairos — Claude Code's Assistant Mode

Kairos is Claude Code's "assistant mode" — a long-running autonomous agent that operates as a persistent assistant rather than an interactive REPL session. The name "Kairos" (Greek for "the right moment") reflects its proactive, schedule-driven nature.

---

## Feature Flag System

Kairos uses a **two-layer gating mechanism**:

1. **Build-time**: `feature('KAIROS')` is a Bun bundler compile-time constant. When `false`, dead-code-elimination strips all guarded code from the binary.
2. **Runtime**: GrowthBook entitlement (`tengu_kairos`) checked via `src/assistant/gate.js` at startup.

The flag system is imported from `bun:bundle`:
```typescript
import { feature } from 'bun:bundle'
```

### Sub-Features

| Sub-Feature | Purpose |
|---|---|
| `KAIROS` | Full assistant mode — includes everything below |
| `KAIROS_BRIEF` | BriefTool (SendUserMessage) as primary output channel |
| `KAIROS_CHANNELS` | MCP channel notifications (Discord/Slack/SMS inbound) |
| `KAIROS_DREAM` | `/dream` skill — distills daily logs into topic files |
| `KAIROS_PUSH_NOTIFICATION` | Push notifications when user is away |
| `KAIROS_GITHUB_WEBHOOKS` | GitHub PR webhook subscriptions |

---

## Activation Flow

**File**: `src/main.tsx` (lines ~1048-1089)

The startup sequence:

1. Initializes `kairosEnabled = false`
2. If `--assistant` flag is passed (Agent SDK daemon), calls `markAssistantForced()` to skip GrowthBook check
3. If `isAssistantMode()` AND not a spawned teammate AND workspace trust accepted:
   - Sets `kairosEnabled = isAssistantForced() || await isKairosEnabled()`
4. If `kairosEnabled`:
   - Forces `--brief` on
   - Calls `setKairosActive(true)` (global state)
   - Initializes assistant team via `initializeAssistantTeam()`
   - Appends assistant-specific system prompt addendum

Later (line 2206), the assistant system prompt addendum is appended:
```typescript
if (feature('KAIROS') && kairosEnabled && assistantModule) {
  const assistantAddendum = assistantModule.getAssistantSystemPromptAddendum();
  appendSystemPrompt = appendSystemPrompt
    ? `${appendSystemPrompt}\n\n${assistantAddendum}`
    : assistantAddendum;
}
```

`kairosEnabled` is stored in `AppState` (line 2962) and in headless state (line 2648) as the single source of truth for downstream consumers.

---

## Global State

**File**: `src/bootstrap/state.ts`

Simple runtime boolean:
```typescript
// Type definition (line 72)
kairosActive: boolean

// Default value (line 301)
kairosActive: false,

// Getter/Setter (lines 1085-1091)
export function getKairosActive(): boolean {
  return STATE.kairosActive
}
export function setKairosActive(value: boolean): void {
  STATE.kairosActive = value
}
```

Additional state in `src/state/AppStateStore.ts` (line 116):
```typescript
kairosEnabled: boolean  // React state boolean, default false (line 483)
```

`kairosActive` is the global runtime flag. `kairosEnabled` is the computed React state that flows into the component tree.

---

## `src/assistant/` Directory

Contains one source file:

### `src/assistant/sessionHistory.ts` (87 lines)

Implements paginated fetch of session events from the Anthropic API for "viewer" mode. Exports:
- `createHistoryAuthCtx()` — prepares OAuth headers + API base URL
- `fetchLatestEvents()` — fetches the newest page via `anchor_to_latest`
- `fetchOlderEvents()` — fetches older pages via `before_id` cursor

Primary consumer: `src/hooks/useAssistantHistory.ts` (250 lines) — React hook with scroll-anchored lazy-loading, fill-viewport chaining (up to 10 pages on mount), and sentinel message management for virtual scroll.

### Build-time Artifacts (not in source)

Several modules are referenced at runtime but do not exist as source files — they are build-time artifacts:

- **`src/assistant/index.js`** exports:
  - `isAssistantMode()` — checks if current session is in assistant mode
  - `markAssistantForced()` / `isAssistantForced()` — override for Agent SDK daemon
  - `initializeAssistantTeam()` — pre-seeds in-process team context
  - `getAssistantSystemPromptAddendum()` — assistant-specific system prompt text
  - `getAssistantActivationPath()` — analytics metadata about activation

- **`src/assistant/gate.js`** exports:
  - `isKairosEnabled()` — GrowthBook entitlement gate check

- **`src/assistant/sessionDiscovery.js`** — discovers running assistant sessions on the host (used by `claude assistant` to find attachable sessions)

- **`src/assistant/AssistantSessionChooser.js`** — UI component for selecting from discovered assistant sessions (used by `src/dialogLaunchers.tsx`)

---

## Runtime Behavior Changes

When Kairos is active:

| Behavior | Detail |
|---|---|
| **Primary output** | BriefTool (`SendUserMessage`) — model must use this; plain text hidden |
| **Memory system** | Daily-log append to `logs/YYYY/MM/YYYY-MM-DD.md` instead of live `MEMORY.md` index |
| **Cron scheduler** | Runs with `assistantMode: true` |
| **Dream skill** | `/dream` distills daily logs into topic files nightly |
| **Bridge worker** | Type set to `"claude_code_assistant"` |
| **AgentTool** | Async fire-and-forget execution for long-running tasks |
| **Background tasks** | PowerShell/Bash background tasks auto-enable |
| **Session continuity** | `--session-id` / `--continue` flags for bridge session resume |

---

## KAIROS-Specific Tools

| Tool | Gate | Purpose |
|---|---|---|
| **BriefTool** (`SendUserMessage`) | `KAIROS \|\| KAIROS_BRIEF` + `tengu_kairos_brief` GB gate | Primary user-facing output channel. Supports attachments. |
| **SendUserFileTool** | `KAIROS` only | Sends files to the user. KAIROS-exclusive |
| **PushNotificationTool** | `KAIROS \|\| KAIROS_PUSH_NOTIFICATION` | Push notifications when user is away |
| **SubscribePRTool** | `KAIROS_GITHUB_WEBHOOKS` | GitHub PR webhook subscriptions |
| **SleepTool** | `PROACTIVE \|\| KAIROS` | Yields REPL loop, waking on ticks or queued commands |
| **CronCreate/CronDelete/CronList** | `AGENT_TRIGGERS` + `tengu_kairos_cron` GB gate | Schedules prompts for future execution (one-shot or recurring) |

### Tool Registration

**File**: `src/tools.ts` (lines 26-50)
```typescript
feature('PROACTIVE') || feature('KAIROS')            // SleepTool
feature('KAIROS')                                     // SendUserFileTool
feature('KAIROS') || feature('KAIROS_PUSH_NOTIFICATION')  // PushNotificationTool
feature('KAIROS_GITHUB_WEBHOOKS')                     // SubscribePRTool
```

### BriefTool Two-Gate System

**File**: `src/tools/BriefTool/BriefTool.tsx`

BriefTool has two independent entitlement checks:

- **`isBriefEntitled()`** — Can the user opt in at all? Returns `true` if `kairosActive || CLAUDE_CODE_BRIEF env || GrowthBook tengu_kairos_brief`.
- **`isBriefEnabled()`** — Is it active right now? Requires `isBriefEntitled()` && (`kairosActive` || user explicitly opted in via message) && GrowthBook still returns true.

GrowthBook refresh window is 5 minutes (`KAIROS_BRIEF_REFRESH_MS`). Flipping `tengu_kairos_brief` off mid-session takes effect on the next refresh. When `kairosActive` is true, the user opt-in requirement is bypassed.

### AgentTool Async Forcing

**File**: `src/tools/AgentTool/AgentTool.tsx` (line 566)

```typescript
assistantForceAsync = feature('KAIROS') ? appState.kairosEnabled : false
```

When Kairos is active, all subagent spawns are forced async (fire-and-forget via `<task-notification>` re-entry). This prevents synchronous subagents from blocking the main REPL loop — without this, a daemon's input queue backs up and the first overdue cron catch-up would spawn N serial subagent turns, blocking all user input.

---

## KAIROS-Related Commands

**File**: `src/commands.ts` (lines 63-101)

| Command | Gate | Purpose |
|---|---|---|
| `/proactive` | `PROACTIVE \|\| KAIROS` | Proactive agent features |
| `/brief` | `KAIROS \|\| KAIROS_BRIEF` | Toggle brief-only mode |
| `/assistant` | `KAIROS` only | Attach REPL as read-only viewer to running session |
| `/subscribe-pr` | `KAIROS_GITHUB_WEBHOOKS` | GitHub PR webhook subscriptions |
| `/loop` | Delegates to `isKairosCronEnabled()` | Schedules cron tasks |

### CLI Command

**File**: `src/main.tsx` (line 4334)
```typescript
if (feature('KAIROS')) {
  program.command('assistant [sessionId]')
    .description('Attach the REPL as a client to a running bridge session...')
}
```

---

## Proactive Agent Ticks

**File**: `src/cli/print.ts` (lines 361-362, 2475-2479)

The proactive module is loaded conditionally when `feature('PROACTIVE') || feature('KAIROS')`. When loaded, the REPL loop injects ticks into the conversation when:

- `proactiveModule.isProactiveActive()` is true
- The session is not paused
- The command queue is empty

A throttle mechanism prevents rapid successive ticks. The proactive module (`src/proactive/index.js`, a build artifact) exposes `isProactiveActive()`, `isProactivePaused()`, `activateProactive()`, and `deactivateProactive()`.

---

## Viewer Mode (`claude assistant`)

The CLI subcommand `claude assistant [sessionId]` attaches the REPL as a **read-only client** to a running assistant session:

- Connects via WebSocket to the running assistant bridge session
- Lazy-loads history via `sessionHistory.ts` (paginated API fetches)
- Real-time event streaming for monitoring
- Can send messages into the remote session

---

## Daily Log Memory

**File**: `src/memdir/memdir.ts` (line 432)

When Kairos is active, the memory system switches from maintaining a live `MEMORY.md` index to an **append-only daily log** paradigm:
- Logs are written to `logs/YYYY/MM/YYYY-MM-DD.md`
- The `/dream` skill (gated behind `KAIROS_DREAM`) distills daily logs into topic-specific files and `MEMORY.md` nightly
- KAIROS daily-log takes precedence over TEAMMEM (the two systems are architecturally incompatible — TEAMMEM maintains a shared live `MEMORY.md` across a team, KAIROS uses per-day append-only files)
- The prompt cache prefix is keyed on `systemPromptSection('memory')` and is **not** invalidated on date rollover — the model derives the current date from a `date_change` attachment injected at midnight

```typescript
if (feature('KAIROS') && autoEnabled && getKairosActive()) {
  // KAIROS daily-log mode takes precedence over TEAMMEM
}
```

### Auto-Dream Consolidation Service

**Files**: `src/services/autoDream/`

A background service that periodically fires the `/dream` skill to consolidate daily logs into `MEMORY.md` and topic-specific files.

Gate order (cheapest first):
1. **Time gate** — `minHours` since last consolidation (from GrowthBook `tengu_onyx_plover`)
2. **Session gate** — minimum number of transcripts must have accumulated (`minSessions`)
3. **Lock acquisition** — file-based lock via `src/services/autoDream/consolidationLock.ts` to prevent concurrent runs

| File | Role |
|---|---|
| `autoDream.ts` | Orchestrator — checks gates, acquires lock, forks the `/dream` agent |
| `config.ts` | `isAutoDreamEnabled()` — GrowthBook gate `tengu_onyx_plover_enabled` |
| `consolidationLock.ts` | File-based mutex — `readLastConsolidatedAt()` / `tryAcquireConsolidationLock()` / `rollbackConsolidationLock()` |
| `consolidationPrompt.ts` | `buildConsolidationPrompt()` — generates the `/dream` skill prompt |

The scheduler re-checks every `SESSION_SCAN_INTERVAL_MS` (10 minutes) so it doesn't spin when the time gate passes but the session gate is still blocking. Task progress is tracked via `src/tasks/DreamTask/DreamTask.ts` and surfaced in the UI via `src/components/tasks/DreamDetailDialog.tsx`.

---

## Channel Notification Architecture (KAIROS_CHANNELS)

**Files**: `src/services/mcp/channelNotification.ts`, `channelPermissions.ts`, `channelAllowlist.ts`

The `KAIROS_CHANNELS` sub-feature enables inbound messages from external platforms (Discord, Slack, SMS, iMessage, Telegram) delivered via MCP servers.

### Inbound Flow

1. MCP server emits `notifications/claude/channel` event with `content` + optional metadata
2. `channelNotification.ts` wraps content in `<channel source="serverName" ...>` XML — safe meta keys are passed through
3. Message is placed in the command queue; SleepTool wakes within 1 second
4. The model decides which tool to use in reply (the channel's own reply tool, `SendUserMessage`, or both)

### Multi-Layer Gate (`gateChannelServer()`)

Gates are checked in order:
1. **Capability** — MCP server must advertise the channel capability
2. **`tengu_harbor`** GrowthBook gate — master switch for all channel notifications
3. **OAuth check** — channels require OAuth auth (API key users are always blocked)
4. **Org policy** — managed orgs must have `channelsEnabled: true` in managed settings
5. **`--channels` session flag** — user must start with channels enabled
6. **Allowlist** — server name must be in `tengu_harbor_ledger` (GrowthBook config)
7. **Marketplace verification** — prevents untrusted plugins from bypassing trust boundaries

### Channel Permission Relay

**File**: `src/services/mcp/channelPermissions.ts`

GrowthBook gate: `tengu_harbor_permissions` (default false, separate from main channels gate).

When active, tool-use permission requests are relayed to channel servers as structured prompts instead of showing a terminal dialog. Reply spec: `/^\s*(y|yes|n|no)\s+([a-km-z]{5})\s*$/i`.

The approval ID is 5 lowercase letters from a 25-character alphabet (a-z minus `l`), blocklist-filtered for inappropriate combinations, and designed to be phone-keyboard friendly.

> **Trust note**: The allowlist (`tengu_harbor_ledger`) is the trust boundary, not the terminal. A compromised channel server that holds an allowlist entry can fabricate permission approvals.

### Startup UI

**File**: `src/components/LogoV2/ChannelsNotice.tsx`

Shown on startup when `--channels` or `--dangerously-load-development-channels` is passed. Displays different messages for: disabled, auth-blocked, or org-policy-blocked channels. Only rendered when `feature('KAIROS') || feature('KAIROS_CHANNELS')`.

### Org Policy Control

Managed orgs (Teams/Enterprise) can set `channelsEnabled: false` to block channels for all members. Unmanaged users fall back to the GrowthBook `tengu_harbor_ledger` allowlist. `KAIROS_CHANNELS` is marked `external: true` in feature spread, so org settings take precedence over the ledger when set.

---

## Analytics Integration

**Files**: `src/services/analytics/metadata.ts`, `src/services/analytics/datadog.ts`

When Kairos is active, analytics payloads include:

- `kairosActive: true` flag in event metadata
- `is_assistant_mode: true` dimension in Datadog metrics
- `'kairosActive'` is in the Datadog dimensional metrics list

The `getAssistantActivationPath()` export from `src/assistant/index.js` provides additional metadata about how the session was activated (e.g., `--assistant` flag vs. GrowthBook entitlement) for analytics tracking.

---

## Key File Locations

**Core**

| File | Role |
|---|---|
| `src/main.tsx` | KAIROS initialization, activation flow, system prompt injection |
| `src/bootstrap/state.ts` | `kairosActive` global state, getter/setter |
| `src/state/AppStateStore.ts` | `kairosEnabled` React state |
| `src/commands.ts` | KAIROS-related slash commands |
| `src/tools.ts` | KAIROS-specific tool registration |

**Assistant / Viewer Mode**

| File | Role |
|---|---|
| `src/assistant/sessionHistory.ts` | Viewer mode session history fetching |
| `src/assistant/index.js` | Build artifact — `isAssistantMode`, `initializeAssistantTeam`, `getAssistantSystemPromptAddendum`, `getAssistantActivationPath` |
| `src/assistant/gate.js` | Build artifact — `isKairosEnabled()` GrowthBook entitlement gate |
| `src/assistant/sessionDiscovery.js` | Build artifact — discovers running assistant sessions |
| `src/assistant/AssistantSessionChooser.js` | Build artifact — session picker UI |
| `src/bridge/bridgeMain.ts` | Session ID / continue flags, bridge worker setup |
| `src/bridge/initReplBridge.ts` | Bridge initialization with KAIROS guards; sets `workerType = 'claude_code_assistant'` |
| `src/hooks/useReplBridge.tsx` | REPL bridge integration with KAIROS |
| `src/hooks/useAssistantHistory.ts` | Scroll-anchored lazy-loading of viewer session history |

**Memory & Consolidation**

| File | Role |
|---|---|
| `src/memdir/memdir.ts` | Daily-log memory system; KAIROS takes precedence over TEAMMEM |
| `src/memdir/paths.ts` | Assistant mode path utilities |
| `src/services/autoDream/autoDream.ts` | Background consolidation orchestrator |
| `src/services/autoDream/config.ts` | `isAutoDreamEnabled()` — GrowthBook `tengu_onyx_plover_enabled` |
| `src/services/autoDream/consolidationLock.ts` | File-based mutex for consolidation runs |
| `src/services/autoDream/consolidationPrompt.ts` | Builds the `/dream` skill prompt |
| `src/tasks/DreamTask/DreamTask.ts` | Task tracking for `/dream` runs |

**Channel Notifications**

| File | Role |
|---|---|
| `src/services/mcp/channelNotification.ts` | Core channel handler; `gateChannelServer()`, `wrapChannelMessage()` |
| `src/services/mcp/channelPermissions.ts` | Permission relay over channels; approval ID generation |
| `src/services/mcp/channelAllowlist.ts` | `tengu_harbor` gate; approved channels ledger |
| `src/services/mcp/useManageMCPConnections.ts` | Channel-enabled MCP lifecycle management |
| `src/components/LogoV2/ChannelsNotice.tsx` | Startup UI for `--channels` flag |

**Tools**

| File | Role |
|---|---|
| `src/tools/BriefTool/BriefTool.tsx` | Brief tool; `isBriefEntitled()` / `isBriefEnabled()` two-gate system |
| `src/tools/BriefTool/attachments.ts` | Shared attachment logic (BriefTool + SendUserFile) |
| `src/tools/SendUserFileTool` | File sending tool (KAIROS exclusive) |
| `src/tools/ScheduleCronTool/prompt.ts` | `isKairosCronEnabled()` export |

**Scheduling**

| File | Role |
|---|---|
| `src/hooks/useScheduledTasks.ts` | Scheduled task runner; `assistantMode` param changes behavior |
| `src/utils/cronScheduler.ts` | Core cron engine; `assistantMode` path |
| `src/utils/cronJitterConfig.ts` | Reads `tengu_kairos_cron_config` / `tengu_kairos_cron_durable` from GrowthBook |

**Proactive / Misc**

| File | Role |
|---|---|
| `src/cli/print.ts` | Injects proactive ticks into REPL loop when Kairos active |
| `src/proactive/index.js` | Build artifact — proactive agent activation/deactivation |
| `src/services/analytics/metadata.ts` | `kairosActive` analytics flag |
| `src/services/analytics/datadog.ts` | `kairosActive` Datadog dimension |
| `src/services/compact/compact.ts` | Conditionally loads session transcript module when KAIROS |
| `src/components/StatusLine.tsx` | Status line hides when KAIROS active |
| `src/skills/bundled/index.ts` | `/dream` and `/loop` skill registration |
