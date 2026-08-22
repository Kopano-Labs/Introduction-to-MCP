export type DetailDensity = "compact" | "balanced" | "detailed";
export type Pace = "calm" | "normal" | "fast";
export type Initiative = "low" | "balanced" | "high";
export type ExplanationStyle = "plain" | "steps" | "why";

export type InteractionProfile = {
  warmth: number;
  detailDensity: DetailDensity;
  pace: Pace;
  initiative: Initiative;
  explanationStyle: ExplanationStyle;
  accountSyncConsent: boolean;
};

export type PilotStep = "understand" | "permission" | "confirm" | "complete";

export type PilotState = {
  step: PilotStep;
  permissionAcknowledged: boolean;
  completedAt: string | null;
};

export type ConnectionState = {
  online: boolean;
  reconnecting: boolean;
};

export const PROFILE_STORAGE_KEY = "kc.everyday.interaction-profile.v1";
export const PILOT_STORAGE_KEY = "kc.everyday.pilot-progress.v1";

export const DEFAULT_PROFILE: InteractionProfile = Object.freeze({
  warmth: 4,
  detailDensity: "balanced",
  pace: "normal",
  initiative: "balanced",
  explanationStyle: "plain",
  accountSyncConsent: false,
});

export const DEFAULT_PILOT: PilotState = Object.freeze({
  step: "understand",
  permissionAcknowledged: false,
  completedAt: null,
});

const DETAIL: DetailDensity[] = ["compact", "balanced", "detailed"];
const PACE: Pace[] = ["calm", "normal", "fast"];
const INITIATIVE: Initiative[] = ["low", "balanced", "high"];
const EXPLANATION: ExplanationStyle[] = ["plain", "steps", "why"];

function oneOf<T extends string>(value: unknown, allowed: readonly T[], fallback: T): T {
  return typeof value === "string" && allowed.includes(value as T) ? (value as T) : fallback;
}

function clampWarmth(value: unknown): number {
  const numeric = typeof value === "number" && Number.isFinite(value) ? value : DEFAULT_PROFILE.warmth;
  return Math.min(5, Math.max(1, Math.round(numeric)));
}

export function normalizeProfile(value: unknown): InteractionProfile {
  const source = value && typeof value === "object" ? (value as Partial<InteractionProfile>) : {};
  return {
    warmth: clampWarmth(source.warmth),
    detailDensity: oneOf(source.detailDensity, DETAIL, DEFAULT_PROFILE.detailDensity),
    pace: oneOf(source.pace, PACE, DEFAULT_PROFILE.pace),
    initiative: oneOf(source.initiative, INITIATIVE, DEFAULT_PROFILE.initiative),
    explanationStyle: oneOf(source.explanationStyle, EXPLANATION, DEFAULT_PROFILE.explanationStyle),
    accountSyncConsent: source.accountSyncConsent === true,
  };
}

export function serializeProfile(profile: InteractionProfile): string {
  return JSON.stringify({
    schema: "kc.everyday.interaction-profile.v1",
    profile: normalizeProfile(profile),
  });
}

export function parseProfile(raw: string | null | undefined): InteractionProfile {
  if (!raw) return { ...DEFAULT_PROFILE };
  try {
    const decoded = JSON.parse(raw) as { profile?: unknown };
    return normalizeProfile(decoded?.profile ?? decoded);
  } catch {
    return { ...DEFAULT_PROFILE };
  }
}

export function normalizePilot(value: unknown): PilotState {
  const source = value && typeof value === "object" ? (value as Partial<PilotState>) : {};
  const step: PilotStep = ["understand", "permission", "confirm", "complete"].includes(
    String(source.step),
  )
    ? (source.step as PilotStep)
    : "understand";
  return {
    step,
    permissionAcknowledged: source.permissionAcknowledged === true,
    completedAt:
      typeof source.completedAt === "string" && source.completedAt.trim() ? source.completedAt : null,
  };
}

export function serializePilot(pilot: PilotState): string {
  return JSON.stringify({
    schema: "kc.everyday.pilot-progress.v1",
    canonicalWorkflowState: false,
    pilot: normalizePilot(pilot),
  });
}

export function parsePilot(raw: string | null | undefined): PilotState {
  if (!raw) return { ...DEFAULT_PILOT };
  try {
    const decoded = JSON.parse(raw) as { pilot?: unknown };
    return normalizePilot(decoded?.pilot ?? decoded);
  } catch {
    return { ...DEFAULT_PILOT };
  }
}

export function nextPilotState(
  current: PilotState,
  event: "continue" | "acknowledge" | "complete" | "restart",
  nowIso = new Date().toISOString(),
): PilotState {
  const state = normalizePilot(current);
  if (event === "restart") return { ...DEFAULT_PILOT };
  if (event === "acknowledge" && state.step === "permission") {
    return { ...state, permissionAcknowledged: true };
  }
  if (event === "continue" && state.step === "understand") {
    return { step: "permission", permissionAcknowledged: false, completedAt: null };
  }
  if (event === "continue" && state.step === "permission" && state.permissionAcknowledged) {
    return { ...state, step: "confirm" };
  }
  if (event === "complete" && state.step === "confirm") {
    return { step: "complete", permissionAcknowledged: true, completedAt: nowIso };
  }
  return state;
}

export function runtimeAdaptation(profile: InteractionProfile) {
  const normalized = normalizeProfile(profile);
  const temperatureByPace: Record<Pace, number> = {
    calm: 0.35,
    normal: 0.5,
    fast: 0.45,
  };
  return {
    responseProfile: {
      warmth: normalized.warmth,
      detailDensity: normalized.detailDensity,
      pace: normalized.pace,
      initiative: normalized.initiative,
      explanationStyle: normalized.explanationStyle,
    },
    inferenceHints: {
      temperature: temperatureByPace[normalized.pace],
      concise: normalized.detailDensity === "compact",
      proactive: normalized.initiative === "high",
    },
    modelWeightTraining: false,
    accountSyncAllowed: normalized.accountSyncConsent,
  };
}

export function connectionMessage(state: ConnectionState): {
  title: string;
  detail: string;
  action: string | null;
} {
  if (!state.online) {
    return {
      title: "You’re offline",
      detail: "Your preferences and review progress stay on this device. Live status may be out of date.",
      action: "Reconnect to refresh live status",
    };
  }
  if (state.reconnecting) {
    return {
      title: "Checking the latest status",
      detail: "Your saved progress is safe while the live view catches up.",
      action: null,
    };
  }
  return {
    title: "Up to date",
    detail: "This view can refresh live status while keeping your local preferences separate.",
    action: null,
  };
}

export function permissionExplanation() {
  return {
    action: "Review what needs attention",
    reason: "You asked to see what still needs a decision or evidence before work can safely continue.",
    scope: "Read current status only",
    consequence: "This review cannot change websites, permissions, releases, or protected system state.",
    authorityEffect: "none" as const,
  };
}

export function friendlyGate(label: string): string {
  const normalized = label.toLowerCase();
  if (normalized.includes("provider receipts")) return "A live service receipt is still missing.";
  if (normalized.includes("source pin") || normalized.includes("ingestion")) {
    return "Some connected work still needs its source confirmed.";
  }
  if (normalized.includes("realtime") || normalized.includes("deployed/live")) {
    return "The live dashboard connection has not been proven yet.";
  }
  return "One item still needs evidence before it can move forward.";
}
