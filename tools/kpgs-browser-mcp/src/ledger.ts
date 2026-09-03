import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import path from "node:path";
import { verifyReceiptIntegrity, type BrowserReceipt, type HumanApproval, type StagedBrowserAction } from "./governance.js";

const ROOT = path.resolve(process.env.KPGS_BROWSER_LEDGER_DIR ?? ".kpgs-browser-ledger");
const PENDING = path.join(ROOT, "pending");
const APPROVED = path.join(ROOT, "approved");
const EXECUTING = path.join(ROOT, "executing");
const RECEIPTS = path.join(ROOT, "receipts");
const CONSUMED = path.join(ROOT, "consumed");
const FAILED = path.join(ROOT, "failed");
const RECEIPT_HEAD = path.join(ROOT, "receipt-head.json");

function assertActionId(actionId: string): void {
  if (!/^BRA-[0-9a-f-]+$/i.test(actionId)) throw new Error("Invalid browser action id");
}

function assertReceiptId(receiptId: string): void {
  if (!/^RCP-[0-9a-f-]+$/i.test(receiptId)) throw new Error("Invalid browser receipt id");
}

async function ensureLedger(): Promise<void> {
  await mkdir(ROOT, { recursive: true, mode: 0o700 });
  await Promise.all(
    [PENDING, APPROVED, EXECUTING, RECEIPTS, CONSUMED, FAILED].map((dir) =>
      mkdir(dir, { recursive: true, mode: 0o700 })
    )
  );
}

async function readJson<T>(filePath: string): Promise<T | undefined> {
  try {
    return JSON.parse(await readFile(filePath, "utf8")) as T;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return undefined;
    throw error;
  }
}

async function writeNewJson(filePath: string, value: unknown): Promise<void> {
  await writeFile(filePath, JSON.stringify(value, null, 2), { flag: "wx", mode: 0o600 });
}

export function ledgerRoot(): string {
  return ROOT;
}

export async function writeStagedAction(action: StagedBrowserAction): Promise<void> {
  await ensureLedger();
  assertActionId(action.actionId);
  await writeNewJson(path.join(PENDING, `${action.actionId}.json`), action);
}

export async function readStagedAction(actionId: string): Promise<StagedBrowserAction | undefined> {
  await ensureLedger();
  assertActionId(actionId);
  return readJson<StagedBrowserAction>(path.join(PENDING, `${actionId}.json`));
}

export async function writeHumanApproval(approval: HumanApproval): Promise<void> {
  await ensureLedger();
  assertActionId(approval.actionId);
  await writeNewJson(path.join(APPROVED, `${approval.actionId}.json`), approval);
}

export async function readHumanApproval(actionId: string): Promise<HumanApproval | undefined> {
  await ensureLedger();
  assertActionId(actionId);
  return readJson<HumanApproval>(path.join(APPROVED, `${actionId}.json`));
}

export async function claimApproval(actionId: string): Promise<HumanApproval | undefined> {
  await ensureLedger();
  assertActionId(actionId);
  const from = path.join(APPROVED, `${actionId}.json`);
  const to = path.join(EXECUTING, `${actionId}.json`);
  try {
    await rename(from, to);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return undefined;
    throw error;
  }
  return readJson<HumanApproval>(to);
}

export async function finalizeApprovalConsumption(actionId: string): Promise<void> {
  await ensureLedger();
  assertActionId(actionId);
  await rename(path.join(EXECUTING, `${actionId}.json`), path.join(CONSUMED, `${actionId}.json`));
}

export async function failClaimedApproval(actionId: string): Promise<void> {
  await ensureLedger();
  assertActionId(actionId);
  try {
    await rename(path.join(EXECUTING, `${actionId}.json`), path.join(FAILED, `${actionId}.json`));
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
  }
}

export async function readReceiptHead(): Promise<{ receiptId: string; receiptHash: string } | undefined> {
  await ensureLedger();
  return readJson<{ receiptId: string; receiptHash: string }>(RECEIPT_HEAD);
}

export async function writeReceipt(receipt: BrowserReceipt): Promise<void> {
  await ensureLedger();
  assertReceiptId(receipt.receiptId);
  if (!verifyReceiptIntegrity(receipt)) throw new Error("RECEIPT_INTEGRITY_INVALID_BEFORE_WRITE");
  await writeNewJson(path.join(RECEIPTS, `${receipt.receiptId}.json`), receipt);
  await writeFile(
    RECEIPT_HEAD,
    JSON.stringify({ receiptId: receipt.receiptId, receiptHash: receipt.receiptHash }, null, 2),
    { mode: 0o600 }
  );
}

export async function readReceipt(receiptId: string): Promise<BrowserReceipt | undefined> {
  await ensureLedger();
  assertReceiptId(receiptId);
  return readJson<BrowserReceipt>(path.join(RECEIPTS, `${receiptId}.json`));
}
