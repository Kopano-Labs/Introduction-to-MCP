import assert from "node:assert/strict";
import test from "node:test";
import {
  POLICY_VERSION,
  assertGovernedNavigationUrl,
  assertInteractionContextAdmissible,
  buildReceipt,
  canonicalJson,
  sha256Binding,
  stageBrowserAction,
  validateApproval,
  validateExecutionContext,
  validateStagedFreshness,
  verifyReceiptIntegrity,
  type BrowserPageContext,
  type HumanApproval
} from "./governance.js";

function pageContext(overrides: Partial<BrowserPageContext> = {}): BrowserPageContext {
  const base = {
    selector: "#save",
    tagName: "button",
    inputType: null,
    autocomplete: null,
    name: null,
    id: "save",
    role: null,
    formAction: null
  };
  return {
    pageIndex: 0,
    url: "https://example.com/settings",
    origin: "https://example.com",
    title: "Settings",
    element: { ...base, fingerprint: sha256Binding(base) },
    ...overrides
  };
}

test("canonical JSON is stable across object key order", () => {
  assert.equal(canonicalJson({ b: 2, a: 1 }), canonicalJson({ a: 1, b: 2 }));
});

test("consequential interaction stages with a human-required context binding", () => {
  const staged = stageBrowserAction(
    { pageIndex: 0, operation: "click", selector: "button[type=submit]" },
    pageContext(),
    new Date("2026-09-03T14:00:00Z")
  );
  assert.match(staged.actionId, /^BRA-/);
  assert.equal(staged.classification, "HIGH_CONSEQUENCE");
  assert.equal(staged.authority, "HUMAN_REQUIRED");
  assert.equal(staged.policyVersion, POLICY_VERSION);
  assert.equal(staged.binding.length, 64);
});

test("missing human approval is denied", () => {
  const now = new Date("2026-09-03T14:00:00Z");
  const context = pageContext({ element: null });
  const staged = stageBrowserAction({ pageIndex: 0, operation: "press", key: "Enter" }, context, now);
  assert.deepEqual(validateApproval(staged, undefined, now), {
    allowed: false,
    reason: "HUMAN_APPROVAL_REQUIRED"
  });
});

test("approval must match exact staged binding and current policy", () => {
  const now = new Date("2026-09-03T14:00:00Z");
  const typeBasis = {
    selector: "#q",
    tagName: "input",
    inputType: "text",
    autocomplete: "off",
    name: "q",
    id: "q",
    role: null,
    formAction: null
  };
  const context = pageContext({ element: { ...typeBasis, fingerprint: sha256Binding(typeBasis) } });
  const staged = stageBrowserAction({ pageIndex: 0, operation: "type", selector: "#q", value: "hello" }, context, now);
  const approval: HumanApproval = {
    actionId: staged.actionId,
    binding: "0".repeat(64),
    policyVersion: POLICY_VERSION,
    approvedAt: now.toISOString(),
    approvedBy: "LOCAL_HUMAN"
  };
  assert.equal(validateApproval(staged, approval, now).allowed, false);
});

test("fresh exact approval is admitted and expired approval is denied", () => {
  const stagedAt = new Date("2026-09-03T14:00:00Z");
  const staged = stageBrowserAction({ pageIndex: 0, operation: "click", selector: "#save" }, pageContext(), stagedAt);
  const approval: HumanApproval = {
    actionId: staged.actionId,
    binding: staged.binding,
    policyVersion: POLICY_VERSION,
    approvedAt: new Date("2026-09-03T14:01:00Z").toISOString(),
    approvedBy: "LOCAL_HUMAN"
  };

  assert.deepEqual(validateApproval(staged, approval, new Date("2026-09-03T14:02:00Z"), 5 * 60_000), { allowed: true });
  assert.deepEqual(validateApproval(staged, approval, new Date("2026-09-03T14:10:00Z"), 5 * 60_000), {
    allowed: false,
    reason: "APPROVAL_EXPIRED"
  });
});

test("staged actions expire independently of approval freshness", () => {
  const staged = stageBrowserAction(
    { pageIndex: 0, operation: "click", selector: "#save" },
    pageContext(),
    new Date("2026-09-03T14:00:00Z"),
    60_000
  );
  assert.deepEqual(validateStagedFreshness(staged, new Date("2026-09-03T14:02:00Z")), {
    allowed: false,
    reason: "STAGED_ACTION_EXPIRED"
  });
});

test("page URL and target element drift invalidate an approved action", () => {
  const staged = stageBrowserAction(
    { pageIndex: 0, operation: "click", selector: "#save" },
    pageContext(),
    new Date("2026-09-03T14:00:00Z")
  );
  assert.deepEqual(validateExecutionContext(staged, pageContext({ url: "https://example.com/other" })), {
    allowed: false,
    reason: "PAGE_URL_DRIFT"
  });
  assert.deepEqual(
    validateExecutionContext(
      staged,
      pageContext({ element: staged.context.element ? { ...staged.context.element, fingerprint: "f".repeat(64) } : null })
    ),
    { allowed: false, reason: "ELEMENT_CONTEXT_DRIFT" }
  );
});

test("sensitive password file payment and OTP typing targets are denied", () => {
  const input = { pageIndex: 0, operation: "type" as const, selector: "#secret", value: "secret" };
  const passwordBasis = {
    selector: "#secret",
    tagName: "input",
    inputType: "password",
    autocomplete: "current-password",
    name: "secret",
    id: "secret",
    role: null,
    formAction: null
  };
  const context = pageContext({ element: { ...passwordBasis, fingerprint: sha256Binding(passwordBasis) } });
  assert.throws(() => assertInteractionContextAdmissible(input, context), /SENSITIVE_INPUT_DENIED/);
});

test("navigation is HTTPS by default, loopback HTTP only, and can be host constrained", () => {
  assert.equal(assertGovernedNavigationUrl("https://example.com/").protocol, "https:");
  assert.equal(assertGovernedNavigationUrl("http://127.0.0.1:3000/").protocol, "http:");
  assert.throws(() => assertGovernedNavigationUrl("http://example.com/"), /INSECURE_HTTP_DENIED/);
  assert.throws(() => assertGovernedNavigationUrl("https://user:pass@example.com/"), /URL_EMBEDDED_CREDENTIALS_DENIED/);
  assert.throws(() => assertGovernedNavigationUrl("file:///etc/passwd"));
  assert.throws(() => assertGovernedNavigationUrl("javascript:alert(1)"));
  assert.equal(
    assertGovernedNavigationUrl("https://sub.example.com/", { allowedHosts: ["*.example.com"] }).hostname,
    "sub.example.com"
  );
  assert.throws(
    () => assertGovernedNavigationUrl("https://evil.example.net/", { allowedHosts: ["*.example.com"] }),
    /HOST_NOT_ADMITTED_BY_POLICY/
  );
});

test("receipts are tamper evident", () => {
  const before = pageContext();
  const after = { ...pageContext({ element: null }) };
  const receipt = buildReceipt({
    receiptId: "RCP-00000000-0000-0000-0000-000000000001",
    actionId: "BRA-00000000-0000-0000-0000-000000000001",
    binding: "a".repeat(64),
    policyVersion: POLICY_VERSION,
    operation: "click",
    pageIndex: 0,
    executedAt: "2026-09-03T14:03:00.000Z",
    pageBefore: before,
    pageAfter: after,
    result: { operation: "click", selector: "#save" },
    previousReceiptHash: null
  });
  assert.equal(verifyReceiptIntegrity(receipt), true);
  assert.equal(verifyReceiptIntegrity({ ...receipt, result: { operation: "click", selector: "#other" } }), false);
});
