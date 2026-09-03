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
  type BrowserElementContext,
  type BrowserPageContext,
  type HumanApproval
} from "./governance.js";

function elementContext(
  selector = "#save",
  overrides: Partial<Omit<BrowserElementContext, "fingerprint" | "selector">> = {}
): BrowserElementContext {
  const basis = {
    selector,
    tagName: "button",
    inputType: null,
    autocomplete: null,
    name: null,
    id: "save",
    role: null,
    formAction: null,
    href: null,
    textDigest: sha256Binding("Save"),
    ...overrides
  };
  return { ...basis, fingerprint: sha256Binding(basis) };
}

function pageContext(overrides: Partial<BrowserPageContext> = {}): BrowserPageContext {
  return {
    pageIndex: 0,
    targetId: "target-1",
    url: "https://example.com/settings",
    origin: "https://example.com",
    title: "Settings",
    element: elementContext(),
    ...overrides
  };
}

test("canonical JSON is stable across object key order", () => {
  assert.equal(canonicalJson({ b: 2, a: 1 }), canonicalJson({ a: 1, b: 2 }));
});

test("consequential interaction stages with a human-required context binding", () => {
  const selector = "button[type=submit]";
  const staged = stageBrowserAction(
    { pageIndex: 0, operation: "click", selector },
    pageContext({ element: elementContext(selector) }),
    new Date("2026-09-03T14:00:00Z")
  );
  assert.match(staged.actionId, /^BRA-/);
  assert.equal(staged.classification, "HIGH_CONSEQUENCE");
  assert.equal(staged.authority, "HUMAN_REQUIRED");
  assert.equal(staged.policyVersion, POLICY_VERSION);
  assert.equal(staged.context.targetId, "target-1");
  assert.equal(staged.binding.length, 64);
});

test("missing human approval is denied", () => {
  const now = new Date("2026-09-03T14:00:00Z");
  const staged = stageBrowserAction(
    { pageIndex: 0, operation: "press", key: "Enter" },
    pageContext({ element: elementContext(":focus", { tagName: "input", inputType: "text" }) }),
    now
  );
  assert.deepEqual(validateApproval(staged, undefined, now), {
    allowed: false,
    reason: "HUMAN_APPROVAL_REQUIRED"
  });
});

test("approval must match exact staged binding and current policy", () => {
  const now = new Date("2026-09-03T14:00:00Z");
  const context = pageContext({
    element: elementContext("#q", {
      tagName: "input",
      inputType: "text",
      autocomplete: "off",
      name: "q",
      id: "q",
      textDigest: null
    })
  });
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

test("target URL and element drift invalidate an approved action", () => {
  const staged = stageBrowserAction(
    { pageIndex: 0, operation: "click", selector: "#save" },
    pageContext(),
    new Date("2026-09-03T14:00:00Z")
  );
  assert.deepEqual(validateExecutionContext(staged, pageContext({ targetId: "target-2" })), {
    allowed: false,
    reason: "PAGE_TARGET_DRIFT"
  });
  assert.deepEqual(validateExecutionContext(staged, pageContext({ url: "https://example.com/other" })), {
    allowed: false,
    reason: "PAGE_URL_DRIFT"
  });
  assert.deepEqual(
    validateExecutionContext(staged, pageContext({ element: { ...elementContext(), fingerprint: "f".repeat(64) } })),
    { allowed: false, reason: "ELEMENT_CONTEXT_DRIFT" }
  );
});

test("keypress requires a focused-element context", () => {
  assert.throws(
    () =>
      stageBrowserAction(
        { pageIndex: 0, operation: "press", key: "Enter" },
        pageContext({ element: null }),
        new Date("2026-09-03T14:00:00Z")
      ),
    /FOCUSED_ELEMENT_CONTEXT_REQUIRED/
  );
});

test("sensitive password file payment and OTP typing targets are denied", () => {
  const input = { pageIndex: 0, operation: "type" as const, selector: "#secret", value: "secret" };
  const context = pageContext({
    element: elementContext("#secret", {
      tagName: "input",
      inputType: "password",
      autocomplete: "current-password",
      name: "secret",
      id: "secret",
      textDigest: null
    })
  });
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
  const after = pageContext({ element: null });
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
