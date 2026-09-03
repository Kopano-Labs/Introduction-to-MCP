import assert from "node:assert/strict";
import { rm } from "node:fs/promises";
import test from "node:test";
import {
  POLICY_VERSION,
  buildReceipt,
  sha256Binding,
  stageBrowserAction,
  type BrowserPageContext,
  type HumanApproval
} from "./governance.js";
import {
  claimApproval,
  finalizeApprovalConsumption,
  ledgerRoot,
  readHumanApproval,
  readReceipt,
  readReceiptHead,
  writeHumanApproval,
  writeReceipt,
  writeStagedAction
} from "./ledger.js";

function context(): BrowserPageContext {
  const basis = {
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
    element: { ...basis, fingerprint: sha256Binding(basis) }
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
