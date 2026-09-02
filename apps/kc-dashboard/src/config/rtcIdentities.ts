/**
 * Data-Driven RTC Identity Registry
 * Binds the UY Scuti / Forge visual language directly into KC's Three.js environment
 * without hardcoded canvas sprawl.
 */

export interface RTCIdentityConfig {
  id: string;
  key: string;
  name: string;
  emoji: string;
  glyph: string;
  tagline: string;
  palette: {
    core: string;
    rim: string;
    rings: string;
    glow: string;
  };
  springDamping: number;
  rotationVelocity: number;
  description: string;
  promptPlaceholder: string;
}

export const RTC_IDENTITIES: Record<string, RTCIdentityConfig> = {
  GUEST_SEEKER: {
    id: "rtc-guest-seeker",
    key: "GUEST_SEEKER",
    name: "KC My Boy",
    emoji: "🌱",
    glyph: "/assets/branding/sep-26/kc_my_boy_flagship_mascot_1788351576403.jpg",
    tagline: "Warm, straightforward, zero tech jargon",
    palette: {
      core: "#0A0D14",
      rim: "#D97706",    // UY Scuti solar amber
      rings: "#F59E0B",
      glow: "#D97706"
    },
    springDamping: 0.85,
    rotationVelocity: 1.0,
    description: "Your daily companion for work, football, smart mobility, and everyday questions.",
    promptPlaceholder: "Ask KC anything in plain words..."
  },
  UY_SCUTI_FORGE: {
    id: "rtc-uy-scuti-forge",
    key: "UY_SCUTI_FORGE",
    name: "Forge Sovereign",
    emoji: "🌌",
    glyph: "/assets/branding/sep-26/assets/UY_SCUTI_FORGE_X_AG_X_RTC_VISUAL_ASSERTION_POC_0.jpg",
    tagline: "Hypergiant stellar convergence & multi-model depth",
    palette: {
      core: "#180608",
      rim: "#FF2A4D",    // Hypergiant stellar red
      rings: "#00F0FF",   // Electric cyan containment
      glow: "#FF2A4D"
    },
    springDamping: 0.65, // Snappier, high-energy recoil
    rotationVelocity: 2.8,
    description: "Multi-model reasoning substrate linking Forge, AG, and the Round Table Council.",
    promptPlaceholder: "Synthesize multi-agent flows or explore UY Scuti hypergiant mechanics..."
  },
  APPRENTICE: {
    id: "rtc-apprentice-cput",
    key: "APPRENTICE",
    name: "Identiq Flow",
    emoji: "⚡",
    glyph: "/assets/branding/sep-26/kc_my_boy_flagship_mascot_1788351576403.jpg",
    tagline: "High-logic shorthand, code paths, and workspace tools",
    palette: {
      core: "#05111A",
      rim: "#00F0FF",
      rings: "#38BDF8",
      glow: "#00F0FF"
    },
    springDamping: 0.75,
    rotationVelocity: 1.8,
    description: "Accelerated studio environment for builders, learners, and sovereign engineers.",
    promptPlaceholder: "Query architectural flows, code patterns, or module blueprints..."
  },
  SYSTEM_TELEMETRY: {
    id: "rtc-system-telemetry",
    key: "SYSTEM_TELEMETRY",
    name: "Cars4Mars Telematics",
    emoji: "📡",
    glyph: "/assets/branding/sep-26/kc_my_boy_flagship_mascot_1788351576403.jpg",
    tagline: "Sensors, hardware packets, and rover telematics",
    palette: {
      core: "#0F0B08",
      rim: "#F97316",
      rings: "#EF4444",
      glow: "#FB923C"
    },
    springDamping: 0.92,
    rotationVelocity: 1.5,
    description: "Low-latency packet bus for DFR-01 rover telematics, battery state, and field hardware.",
    promptPlaceholder: "Monitor telemetry stream, hardware bus, or sensor clusters..."
  },
  OPERATOR_SOVEREIGN: {
    id: "rtc-operator-sovereign",
    key: "OPERATOR_SOVEREIGN",
    name: "Tier 0 Sovereign",
    emoji: "👑",
    glyph: "/assets/branding/sep-26/kc_my_boy_flagship_mascot_1788351576403.jpg",
    tagline: "Master key authority, audits, and ledger seals",
    palette: {
      core: "#0F172A",
      rim: "#F8FAFC",
      rings: "#D97706",
      glow: "#E2E8F0"
    },
    springDamping: 0.65,
    rotationVelocity: 3.0,
    description: "Direct control plane authority for the Landlord and Round Table Council.",
    promptPlaceholder: "Execute sovereign commands or audit immutable trace ledgers..."
  }
};
