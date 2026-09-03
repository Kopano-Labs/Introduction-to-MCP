import assert from "node:assert/strict";
import test from "node:test";
import {
  assertGovernedNavigationUrl,
  canonicalJson,
  stageBrowserAction,
  validateApproval,
  type HumanApproval
} from "./governance.js";

test("canonical JSON is stable across object key order", () => {
  assert.equal(canonicalJson({ b: 2, a: 1 }), canonicalJson({ a: 1, b: 2 }));
});

test("consequential interaction stages with a human-required binding", () => {
  const staged = stageBrowserAction(
    { pageIndex: 0, operation: "click", selector: "button[type=submit]" },
    new Date("2026-09-03T14:00:00Z")
  );
  assert.match(staged.actionId, /^BRA-/);
  assert.equal(staged.classification, "CONSEQUENTIAL");
  assert.equal(staged.authority, "HUMAN_REQUIRED");
  assert.equal(staged.binding.length, 64);
});

test("missing human approval is denied", () => {
  const now = new Date("2026-09-03T14:00:00Z");
  const staged = stageBrowserAction({ pageIndex: 1, operation: "press", key: "Enter" }, now);
  assert.deepEqual(validateApproval(staged, undefined, now), {
    allowed: false,
    reason: "HUMAN_APPROVAL_REQUIRED"
  });
});

test("approval must match exact staged binding", () => {
  const now = new Date("2026-09-03T14:00:00Z");
  const staged = stageBrowserAction({ pageIndex: 0, operation: "type", selector: "#q", value: "hello" }, now);
  const approval: HumanApproval = {
    actionId: staged.actionId,
    binding: "0".repeat(64),
    approvedAt: now.toISOString(),
    approvedBy: "LOCAL_HUMAN"
  };
  assert.equal(validateApproval(staged, approval, now).allowed, false);
});

test("fresh exact approval is admitted and expired approval is denied", () => {
  const stagedAt = new Date("2026-09-03T14:00:00Z");
  const staged = stageBrowserAction({ pageIndex: 0, operation: "click", selector: "#save" }, stagedAt);
  const approval: HumanApproval = {
    actionId: staged.actionId,
    binding: staged.binding,
    approvedAt: new Date("2026-09-03T14:01:00Z").toISOString(),
    approvedBy: "LOCAL_HUMAN"
  };

  assert.deepEqual(validateApproval(staged, approval, new Date("2026-09-03T14:02:00Z"), 5 * 60_000), { allowed: true });
  assert.deepEqual(validateApproval(staged, approval, new Date("2026-09-03T14:10:00Z"), 5 * 60_000), {
    allowed: false,
    reason: "APPROVAL_EXPIRED"
  });
});

test("navigation admits only HTTP(S)", () => {
  assert.equal(assertGovernedNavigationUrl("https://example.com/").protocol, "https:");
  assert.throws(() => assertGovernedNavigationUrl("file:///etc/passwd"));
  assert.throws(() => assertGovernedNavigationUrl("javascript:alert(1)"));
});
