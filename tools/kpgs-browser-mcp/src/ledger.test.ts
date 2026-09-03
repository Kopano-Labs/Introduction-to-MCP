import assert from "node:assert/strict";
import { readFile, rm } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import {
  POLICY_VERSION,
  buildReceipt,
  sha256Binding,
  stageBrowserAction,
  type BrowserElementContext,
  type BrowserPageContext,
  type HumanApproval
} from "./governance.js";
import {
  archiveStagedAction,
  claimApproval,
  finalizeApprovalConsumption,
  ledgerRoot,
  quarantineStagedAction,
  readHumanApproval,
  readReceipt,
  readReceiptHead,
  readStagedAction,
  writeHumanApproval,
  writeReceipt,
  writeStagedAction
} from "./ledger.js";

function element(
  selector = "#save",
  overrides: Partial<Omit<BrowserElementContext, "selector" | "fingerprint">> = {}
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

function context(overrides: Partial<BrowserPageContext> = {}): BrowserPageContext {
  return {
    pageIndex: 0,
    targetId: "target-ledger-test",
    url: "https://example.com/settings",
    origin: "https://example.com",
    title: "Settings",
    element: element(),
    ...overrides
  };
}

test("approval is atomically claimable only once", async () => {
  await rm(ledgerRoot(), { recursive: true, force: true });
  const now = new Date();
  const staged = stageBrowserAction({ pageIndex: 0, operation: "click", selector: "#save" }, context(), now);
  const approval: HumanApproval = {
    actionId: staged.actionId,
    binding: staged.binding,
    policyVersion: POLICY_VERSION,
    approvedAt: new Date(now.getTime() + 1).toISOString(),
    approvedBy: "LOCAL_HUMAN"
  };

  await writeStagedAction(staged);
  await writeHumanApproval(approval);
  assert.deepEqual(await readHumanApproval(staged.actionId), approval);

  assert.deepEqual(await claimApproval(staged.actionId), approval);
  assert.equal(await claimApproval(staged.actionId), undefined);
  assert.equal(await readHumanApproval(staged.actionId), undefined);

  await finalizeApprovalConsumption(staged.actionId);
  assert.equal(await claimApproval(staged.actionId), undefined);
  await rm(ledgerRoot(), { recursive: true, force: true });
});

test("successful archive scrubs typed plaintext from pending and archived evidence", async () => {
  await rm(ledgerRoot(), { recursive: true, force: true });
  const secret = "local-only typed payload";
  const selector = "#note";
  const staged = stageBrowserAction(
    { pageIndex: 0, operation: "type", selector, value: secret },
    context({
      element: element(selector, {
        tagName: "textarea",
        inputType: null,
        autocomplete: "off",
        id: "note",
        textDigest: null
      })
    })
  );

  await writeStagedAction(staged);
  assert.equal((await readStagedAction(staged.actionId))?.value, secret);
  await archiveStagedAction(staged.actionId, "EXECUTED");
  assert.equal(await readStagedAction(staged.actionId), undefined);

  const archived = await readFile(path.join(ledgerRoot(), "archived", `${staged.actionId}.json`), "utf8");
  assert.equal(archived.includes(secret), false);
  assert.equal(archived.includes(sha256Binding(secret)), true);
  await rm(ledgerRoot(), { recursive: true, force: true });
});

test("indeterminate action is quarantined locally and explicitly non-replayable", async () => {
  await rm(ledgerRoot(), { recursive: true, force: true });
  const secret = "forensic payload retained locally";
  const selector = "#note";
  const staged = stageBrowserAction(
    { pageIndex: 0, operation: "type", selector, value: secret },
    context({
      element: element(selector, {
        tagName: "textarea",
        inputType: null,
        autocomplete: "off",
        id: "note",
        textDigest: null
      })
    })
  );

  await writeStagedAction(staged);
  await quarantineStagedAction(staged.actionId, "EXECUTION_ERROR_AFTER_APPROVAL_CLAIM");
  assert.equal(await readStagedAction(staged.actionId), undefined);

  const quarantined = await readFile(path.join(ledgerRoot(), "quarantined", `${staged.actionId}.json`), "utf8");
  const metadata = JSON.parse(
    await readFile(path.join(ledgerRoot(), "quarantined", `${staged.actionId}.meta.json`), "utf8")
  ) as Record<string, unknown>;
  assert.equal(quarantined.includes(secret), true);
  assert.equal(metadata.replayAllowed, false);
  assert.equal(metadata.humanReviewRequired, true);
  await rm(ledgerRoot(), { recursive: true, force: true });
});

test("receipt hash and chain head persist together", async () => {
  await rm(ledgerRoot(), { recursive: true, force: true });
  const page = context();
  const receipt = buildReceipt({
    receiptId: "RCP-00000000-0000-0000-0000-000000000010",
    actionId: "BRA-00000000-0000-0000-0000-000000000010",
    binding: "b".repeat(64),
    policyVersion: POLICY_VERSION,
    operation: "click",
    pageIndex: 0,
    executedAt: "2026-09-03T16:30:00.000Z",
    pageBefore: page,
    pageAfter: { ...page, element: null },
    result: { operation: "click", selector: "#save" },
    previousReceiptHash: null
  });

  await writeReceipt(receipt);
  assert.deepEqual(await readReceipt(receipt.receiptId), receipt);
  assert.deepEqual(await readReceiptHead(), { receiptId: receipt.receiptId, receiptHash: receipt.receiptHash });
  await rm(ledgerRoot(), { recursive: true, force: true });
});
