import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import path from "node:path";
import type { BrowserReceipt, HumanApproval, StagedBrowserAction } from "./governance.js";

const ROOT = path.resolve(process.env.KPGS_BROWSER_LEDGER_DIR ?? ".kpgs-browser-ledger");
const PENDING = path.join(ROOT, "pending");
const APPROVED = path.join(ROOT, "approved");
const RECEIPTS = path.join(ROOT, "receipts");
const CONSUMED = path.join(ROOT, "consumed");

function assertActionId(actionId: string): void {
  if (!/^BRA-[0-9a-f-]+$/i.test(actionId)) throw new Error("Invalid browser action id");
}

function assertReceiptId(receiptId: string): void {
  if (!/^RCP-[0-9a-f-]+$/i.test(receiptId)) throw new Error("Invalid browser receipt id");
}

async function ensureLedger(): Promise<void> {
  await Promise.all([PENDING, APPROVED, RECEIPTS, CONSUMED].map((dir) => mkdir(dir, { recursive: true })));
}

async function readJson<T>(filePath: string): Promise<T | undefined> {
  try {
    return JSON.parse(await readFile(filePath, "utf8")) as T;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return undefined;
    throw error;
  }
}

export function ledgerRoot(): string {
  return ROOT;
}

export async function writeStagedAction(action: StagedBrowserAction): Promise<void> {
  await ensureLedger();
  assertActionId(action.actionId);
  await writeFile(path.join(PENDING, `${action.actionId}.json`), JSON.stringify(action, null, 2), { flag: "wx" });
}

export async function readStagedAction(actionId: string): Promise<StagedBrowserAction | undefined> {
  await ensureLedger();
  assertActionId(actionId);
  return readJson<StagedBrowserAction>(path.join(PENDING, `${actionId}.json`));
}

export async function writeHumanApproval(approval: HumanApproval): Promise<void> {
  await ensureLedger();
  assertActionId(approval.actionId);
  await writeFile(path.join(APPROVED, `${approval.actionId}.json`), JSON.stringify(approval, null, 2), { flag: "wx" });
}

export async function readHumanApproval(actionId: string): Promise<HumanApproval | undefined> {
  await ensureLedger();
  assertActionId(actionId);
  return readJson<HumanApproval>(path.join(APPROVED, `${actionId}.json`));
}

export async function consumeApproval(actionId: string): Promise<void> {
  await ensureLedger();
  assertActionId(actionId);
  try {
    await rename(path.join(APPROVED, `${actionId}.json`), path.join(CONSUMED, `${actionId}.json`));
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
  }
}

export async function writeReceipt(receipt: BrowserReceipt): Promise<void> {
  await ensureLedger();
  assertReceiptId(receipt.receiptId);
  await writeFile(path.join(RECEIPTS, `${receipt.receiptId}.json`), JSON.stringify(receipt, null, 2), { flag: "wx" });
}

export async function readReceipt(receiptId: string): Promise<BrowserReceipt | undefined> {
  await ensureLedger();
  assertReceiptId(receiptId);
  return readJson<BrowserReceipt>(path.join(RECEIPTS, `${receiptId}.json`));
}
