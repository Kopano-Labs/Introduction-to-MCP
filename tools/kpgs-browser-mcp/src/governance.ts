import { createHash, randomUUID } from "node:crypto";

export const HUMAN_APPROVAL_TTL_MS = Number(process.env.KPGS_BROWSER_APPROVAL_TTL_MS ?? 10 * 60 * 1000);

export type BrowserInteraction = "click" | "type" | "press";

export type BrowserActionInput = {
  pageIndex: number;
  operation: BrowserInteraction;
  selector?: string;
  value?: string;
  key?: string;
};

export type StagedBrowserAction = BrowserActionInput & {
  actionId: string;
  classification: "CONSEQUENTIAL";
  authority: "HUMAN_REQUIRED";
  createdAt: string;
  binding: string;
};

export type HumanApproval = {
  actionId: string;
  binding: string;
  approvedAt: string;
  approvedBy: "LOCAL_HUMAN";
};

export type BrowserReceipt = {
  receiptId: string;
  actionId: string;
  binding: string;
  operation: BrowserInteraction;
  pageIndex: number;
  executedAt: string;
  result: Record<string, unknown>;
};

function canonicalize(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([key, nested]) => [key, canonicalize(nested)])
    );
  }
  return value;
}

export function canonicalJson(value: unknown): string {
  return JSON.stringify(canonicalize(value));
}

export function sha256Binding(value: unknown): string {
  return createHash("sha256").update(canonicalJson(value)).digest("hex");
}

export function validateActionInput(input: BrowserActionInput): void {
  if (!Number.isInteger(input.pageIndex) || input.pageIndex < 0) {
    throw new Error("pageIndex must be a non-negative integer");
  }
  if (input.operation === "click" && !input.selector) {
    throw new Error("click requires selector");
  }
  if (input.operation === "type" && (!input.selector || input.value === undefined)) {
    throw new Error("type requires selector and value");
  }
  if (input.operation === "press" && !input.key) {
    throw new Error("press requires key");
  }
}

export function stageBrowserAction(input: BrowserActionInput, now = new Date()): StagedBrowserAction {
  validateActionInput(input);
  const actionId = `BRA-${randomUUID()}`;
  const createdAt = now.toISOString();
  const binding = sha256Binding({ actionId, ...input, createdAt });
  return {
    actionId,
    ...input,
    classification: "CONSEQUENTIAL",
    authority: "HUMAN_REQUIRED",
    createdAt,
    binding
  };
}

export function validateApproval(
  staged: StagedBrowserAction,
  approval: HumanApproval | undefined,
  now = new Date(),
  ttlMs = HUMAN_APPROVAL_TTL_MS
): { allowed: true } | { allowed: false; reason: string } {
  if (!approval) return { allowed: false, reason: "HUMAN_APPROVAL_REQUIRED" };
  if (approval.actionId !== staged.actionId) return { allowed: false, reason: "APPROVAL_ACTION_MISMATCH" };
  if (approval.binding !== staged.binding) return { allowed: false, reason: "APPROVAL_BINDING_MISMATCH" };
  if (approval.approvedBy !== "LOCAL_HUMAN") return { allowed: false, reason: "APPROVAL_ACTOR_INVALID" };

  const approvedAt = Date.parse(approval.approvedAt);
  if (!Number.isFinite(approvedAt)) return { allowed: false, reason: "APPROVAL_TIMESTAMP_INVALID" };
  if (now.getTime() - approvedAt > ttlMs) return { allowed: false, reason: "APPROVAL_EXPIRED" };
  if (approvedAt > now.getTime() + 5_000) return { allowed: false, reason: "APPROVAL_TIMESTAMP_FUTURE" };

  return { allowed: true };
}

export function assertGovernedNavigationUrl(rawUrl: string): URL {
  const url = new URL(rawUrl);
  if (url.protocol !== "https:" && url.protocol !== "http:") {
    throw new Error("Only http:// and https:// navigation is admitted in the POC");
  }
  return url;
}
