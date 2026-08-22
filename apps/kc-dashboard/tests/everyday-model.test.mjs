import test from "node:test";
import assert from "node:assert/strict";

import {
  DEFAULT_PILOT,
  DEFAULT_PROFILE,
  PILOT_STORAGE_KEY,
  PROFILE_STORAGE_KEY,
  connectionMessage,
  friendlyGate,
  nextPilotState,
  normalizeProfile,
  parseProfile,
  permissionExplanation,
  runtimeAdaptation,
  serializeProfile,
} from "../.proof/everyday-model.js";

test("profile normalization is bounded and exportable", () => {
  const normalized = normalizeProfile({
    warmth: 99,
    detailDensity: "unknown",
    pace: "fast",
    initiative: "high",
    explanationStyle: "why",
    accountSyncConsent: true,
  });
  assert.equal(normalized.warmth, 5);
  assert.equal(normalized.detailDensity, DEFAULT_PROFILE.detailDensity);
  assert.equal(normalized.pace, "fast");
  assert.equal(normalized.initiative, "high");
  assert.equal(normalized.accountSyncConsent, true);

  const roundTrip = parseProfile(serializeProfile(normalized));
  assert.deepEqual(roundTrip, normalized);
});

test("profile and pilot persistence use separate state domains", () => {
  assert.notEqual(PROFILE_STORAGE_KEY, PILOT_STORAGE_KEY);
  assert.match(PROFILE_STORAGE_KEY, /interaction-profile/);
  assert.match(PILOT_STORAGE_KEY, /pilot-progress/);
});

test("pilot cannot skip permission acknowledgement", () => {
  const permission = nextPilotState(DEFAULT_PILOT, "continue", "2026-08-20T00:00:00Z");
  assert.equal(permission.step, "permission");

  const skipped = nextPilotState(permission, "continue", "2026-08-20T00:00:00Z");
  assert.equal(skipped.step, "permission");

  const acknowledged = nextPilotState(permission, "acknowledge", "2026-08-20T00:00:00Z");
  assert.equal(acknowledged.permissionAcknowledged, true);
  const confirm = nextPilotState(acknowledged, "continue", "2026-08-20T00:00:00Z");
  assert.equal(confirm.step, "confirm");
  const complete = nextPilotState(confirm, "complete", "2026-08-20T00:00:00Z");
  assert.equal(complete.step, "complete");
  assert.equal(complete.completedAt, "2026-08-20T00:00:00Z");
});

test("runtime adaptation cannot become weight training authority", () => {
  const profile = { ...DEFAULT_PROFILE, accountSyncConsent: true, initiative: "high" };
  const adaptation = runtimeAdaptation(profile);
  assert.equal(adaptation.modelWeightTraining, false);
  assert.equal(adaptation.accountSyncAllowed, true);
  assert.equal(adaptation.inferenceHints.proactive, true);
});

test("offline state is explicit and recoverable", () => {
  const offline = connectionMessage({ online: false, reconnecting: false });
  assert.equal(offline.title, "You’re offline");
  assert.match(offline.detail, /stay on this device/i);
  assert.match(offline.action ?? "", /reconnect/i);
});

test("permission explanation is read-only and grants no authority", () => {
  const permission = permissionExplanation();
  assert.equal(permission.authorityEffect, "none");
  assert.match(permission.scope, /read/i);
  assert.match(permission.consequence, /cannot change/i);
});

test("everyday blocker copy removes infrastructure jargon", () => {
  const samples = [
    friendlyGate("Live provider receipts absent"),
    friendlyGate("3 weekend Sub-Membranes still need source pin + deep ingestion"),
    friendlyGate("Dashboard is repository-source POC; no deployed/live realtime feed receipt yet"),
  ].join(" ");
  for (const forbidden of ["KPGS", "MCP", ".NET", "WebSocket", "Sub-Membrane", "ingestion"]) {
    assert.equal(samples.includes(forbidden), false, `found forbidden everyday term: ${forbidden}`);
  }
});
