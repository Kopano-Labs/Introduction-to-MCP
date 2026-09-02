/**
 * RTC Identity & Kopano Assert Types
 * Defines the real-time context personas and verifiable assertion receipts.
 */

export type RTCIdentityKey =
  | "GUEST_SEEKER"
  | "UY_SCUTI_FORGE"
  | "APPRENTICE"
  | "SYSTEM_TELEMETRY"
  | "OPERATOR_SOVEREIGN";

export interface RTCIdentityProfile {
  key: RTCIdentityKey;
  label: string;
  emoji: string;
  tagline: string;
  primaryColor: string;
  secondaryColor: string;
  glowColor: string;
  ringSpeedMultiplier: number;
  dampingFactor: number;
  description: string;
  promptPlaceholder: string;
}

export interface KopanoAssertReceipt {
  assert_id: string;
  session_id: string;
  rtc_identity: string;
  intent_domain: string;
  claim: string;
  residency: string;
  proof_hash: string;
  status: string;
  timestamp: string;
}

export const RTC_IDENTITY_PROFILES: Record<RTCIdentityKey, RTCIdentityProfile> = {
  GUEST_SEEKER: {
    key: "GUEST_SEEKER",
    label: "Everyday Guest",
    emoji: "🌱",
    tagline: "Warm, straightforward, zero tech jargon",
    primaryColor: "#D97706", // Amber 600
    secondaryColor: "#00F0FF", // Electric Cyan
    glowColor: "#F59E0B", // Amber 500
    ringSpeedMultiplier: 1.0,
    dampingFactor: 0.85,
    description: "Your daily companion for work, football, smart mobility, and everyday questions.",
    promptPlaceholder: "Ask KC anything in plain words..."
  },
  UY_SCUTI_FORGE: {
    key: "UY_SCUTI_FORGE",
    label: "Forge Sovereign",
    emoji: "🌌",
    tagline: "Hypergiant stellar convergence & multi-model depth",
    primaryColor: "#FF2A4D", // Stellar Red
    secondaryColor: "#00F0FF", // Cyan
    glowColor: "#FF2A4D",
    ringSpeedMultiplier: 2.8,
    dampingFactor: 0.65,
    description: "Multi-model reasoning substrate linking Forge, AG, and the Round Table Council.",
    promptPlaceholder: "Synthesize multi-agent flows or explore UY Scuti hypergiant mechanics..."
  },
  APPRENTICE: {
    key: "APPRENTICE",
    label: "Sovereign Apprentice",
    emoji: "⚡",
    tagline: "High-logic shorthand, code paths, and workspace tools",
    primaryColor: "#00F0FF", // Electric Cyan
    secondaryColor: "#3B82F6", // Blue 500
    glowColor: "#38BDF8", // Sky 400
    ringSpeedMultiplier: 2.2,
    dampingFactor: 0.75,
    description: "Accelerated studio environment for builders, learners, and sovereign engineers.",
    promptPlaceholder: "Query architectural flows, code patterns, or module blueprints..."
  },
  SYSTEM_TELEMETRY: {
    key: "SYSTEM_TELEMETRY",
    label: "Cars4Mars Telematics",
    emoji: "📡",
    tagline: "Sensors, hardware packets, and rover telematics",
    primaryColor: "#F97316", // Orange 500
    secondaryColor: "#EF4444", // Red 500
    glowColor: "#FB923C", // Orange 400
    ringSpeedMultiplier: 1.5,
    dampingFactor: 0.92,
    description: "Low-latency packet bus for DFR-01 rover telematics, battery state, and field hardware.",
    promptPlaceholder: "Monitor telemetry stream, hardware bus, or sensor clusters..."
  },
  OPERATOR_SOVEREIGN: {
    key: "OPERATOR_SOVEREIGN",
    label: "Tier 0 Sovereign",
    emoji: "👑",
    tagline: "Master key authority, audits, and ledger seals",
    primaryColor: "#F8FAFC", // Pure White
    secondaryColor: "#D97706", // Gold
    glowColor: "#E2E8F0", // Slate 200
    ringSpeedMultiplier: 3.0,
    dampingFactor: 0.65,
    description: "Direct control plane authority for the Landlord and Round Table Council.",
    promptPlaceholder: "Execute sovereign commands or audit immutable trace ledgers..."
  }
};
