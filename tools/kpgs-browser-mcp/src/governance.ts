import { createHash, randomUUID } from "node:crypto";

export const POLICY_VERSION = "kpgs-browser-policy.v2";
export const HUMAN_APPROVAL_TTL_MS = Number(process.env.KPGS_BROWSER_APPROVAL_TTL_MS ?? 10 * 60 * 1000);
export const STAGED_ACTION_TTL_MS = Number(process.env.KPGS_BROWSER_STAGED_TTL_MS ?? 15 * 60 * 1000);

export type BrowserInteraction = "click" | "type" | "press";
export type BrowserRisk = "CONSEQUENTIAL" | "HIGH_CONSEQUENCE";

export type BrowserActionInput = {
  pageIndex: number;
  operation: BrowserInteraction;
  selector?: string;
  value?: string;
  key?: string;
};

export type BrowserElementContext = {
  selector: string;
  tagName: string;
  inputType: string | null;
  autocomplete: string | null;
  name: string | null;
  id: string | null;
  role: string | null;
  formAction: string | null;
  fingerprint: string;
};

export type BrowserPageContext = {
  pageIndex: number;
  url: string;
  origin: string;
  title: string;
  element: BrowserElementContext | null;
};

export type StagedBrowserAction = BrowserActionInput & {
  actionId: string;
  classification: BrowserRisk;
  authority: "HUMAN_REQUIRED";
  policyVersion: typeof POLICY_VERSION;
  createdAt: string;
  expiresAt: string;
  context: BrowserPageContext;
  binding: string;
};

export type HumanApproval = {
  actionId: string;
  binding: string;
  policyVersion: typeof POLICY_VERSION;
  approvedAt: string;
  approvedBy: "LOCAL_HUMAN";
};

export type BrowserReceipt = {
  receiptId: string;
  actionId: string;
  binding: string;
  policyVersion: typeof POLICY_VERSION;
  operation: BrowserInteraction;
  pageIndex: number;
  executedAt: string;
  pageBefore: BrowserPageContext;
  pageAfter: Omit<BrowserPageContext, "element"> & { element?: null };
  result: Record<string, unknown>;
  previousReceiptHash: string | null;
  receiptHash: string;
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

export function classifyInteractionRisk(input: BrowserActionInput): BrowserRisk {
  if (input.operation === "press") return "HIGH_CONSEQUENCE";
  const selector = (input.selector ?? "").toLowerCase();
  const highRiskTokens = [
    "submit",
    "delete",
    "remove",
    "purchase",
    "checkout",
    "pay",
    "send",
    "merge",
    "approve",
    "confirm",
    "publish",
    "deploy"
  ];
  return highRiskTokens.some((token) => selector.includes(token)) ? "HIGH_CONSEQUENCE" : "CONSEQUENTIAL";
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
  if (input.value && input.value.length > 20_000) {
    throw new Error("typed value exceeds governed 20,000-character limit");
  }
}

const DENIED_INPUT_TYPES = new Set(["password", "file"]);
const DENIED_AUTOCOMPLETE_TOKENS = new Set([
  "current-password",
  "new-password",
  "one-time-code",
  "cc-number",
  "cc-csc",
  "cc-exp",
  "cc-exp-month",
  "cc-exp-year"
]);

export function assertInteractionContextAdmissible(input: BrowserActionInput, context: BrowserPageContext): void {
  if (context.pageIndex !== input.pageIndex) throw new Error("PAGE_CONTEXT_INDEX_MISMATCH");
  if (!context.url || !context.origin) throw new Error("PAGE_CONTEXT_INVALID");

  if (input.operation === "type") {
    const element = context.element;
    if (!element) throw new Error("TYPE_ELEMENT_CONTEXT_REQUIRED");
    const inputType = (element.inputType ?? "").toLowerCase();
    const autocompleteTokens = (element.autocomplete ?? "")
      .toLowerCase()
      .split(/\s+/)
      .filter(Boolean);

    if (DENIED_INPUT_TYPES.has(inputType)) throw new Error(`SENSITIVE_INPUT_DENIED:${inputType}`);
    if (autocompleteTokens.some((token) => DENIED_AUTOCOMPLETE_TOKENS.has(token))) {
      throw new Error("SENSITIVE_AUTOCOMPLETE_DENIED");
    }
  }
}

export function stageBrowserAction(
  input: BrowserActionInput,
  context: BrowserPageContext,
  now = new Date(),
  ttlMs = STAGED_ACTION_TTL_MS
): StagedBrowserAction {
  validateActionInput(input);
  assertInteractionContextAdmissible(input, context);
  const actionId = `BRA-${randomUUID()}`;
  const createdAt = now.toISOString();
  const expiresAt = new Date(now.getTime() + ttlMs).toISOString();
  const classification = classifyInteractionRisk(input);
  const binding = sha256Binding({
    actionId,
    input,
    context,
    classification,
    policyVersion: POLICY_VERSION,
    createdAt,
    expiresAt
  });
  return {
    actionId,
    ...input,
    classification,
    authority: "HUMAN_REQUIRED",
    policyVersion: POLICY_VERSION,
    createdAt,
    expiresAt,
    context,
    binding
  };
}

export function validateStagedFreshness(
  staged: StagedBrowserAction,
  now = new Date()
): { allowed: true } | { allowed: false; reason: string } {
  if (staged.policyVersion !== POLICY_VERSION) return { allowed: false, reason: "POLICY_VERSION_MISMATCH" };
  const createdAt = Date.parse(staged.createdAt);
  const expiresAt = Date.parse(staged.expiresAt);
  if (!Number.isFinite(createdAt) || !Number.isFinite(expiresAt)) {
    return { allowed: false, reason: "STAGED_TIMESTAMP_INVALID" };
  }
  if (createdAt > now.getTime() + 5_000) return { allowed: false, reason: "STAGED_TIMESTAMP_FUTURE" };
  if (now.getTime() > expiresAt) return { allowed: false, reason: "STAGED_ACTION_EXPIRED" };
  return { allowed: true };
}

export function validateApproval(
  staged: StagedBrowserAction,
  approval: HumanApproval | undefined,
  now = new Date(),
  ttlMs = HUMAN_APPROVAL_TTL_MS
): { allowed: true } | { allowed: false; reason: string } {
  const freshness = validateStagedFreshness(staged, now);
  if (!freshness.allowed) return freshness;
  if (!approval) return { allowed: false, reason: "HUMAN_APPROVAL_REQUIRED" };
  if (approval.actionId !== staged.actionId) return { allowed: false, reason: "APPROVAL_ACTION_MISMATCH" };
  if (approval.binding !== staged.binding) return { allowed: false, reason: "APPROVAL_BINDING_MISMATCH" };
  if (approval.policyVersion !== POLICY_VERSION) return { allowed: false, reason: "APPROVAL_POLICY_MISMATCH" };
  if (approval.approvedBy !== "LOCAL_HUMAN") return { allowed: false, reason: "APPROVAL_ACTOR_INVALID" };

  const approvedAt = Date.parse(approval.approvedAt);
  if (!Number.isFinite(approvedAt)) return { allowed: false, reason: "APPROVAL_TIMESTAMP_INVALID" };
  if (approvedAt < Date.parse(staged.createdAt)) return { allowed: false, reason: "APPROVAL_PRECEDES_STAGING" };
  if (now.getTime() - approvedAt > ttlMs) return { allowed: false, reason: "APPROVAL_EXPIRED" };
  if (approvedAt > now.getTime() + 5_000) return { allowed: false, reason: "APPROVAL_TIMESTAMP_FUTURE" };

  return { allowed: true };
}

export function validateExecutionContext(
  staged: StagedBrowserAction,
  live: BrowserPageContext
): { allowed: true } | { allowed: false; reason: string } {
  if (live.pageIndex !== staged.context.pageIndex) return { allowed: false, reason: "PAGE_INDEX_DRIFT" };
  if (live.origin !== staged.context.origin) return { allowed: false, reason: "PAGE_ORIGIN_DRIFT" };
  if (live.url !== staged.context.url) return { allowed: false, reason: "PAGE_URL_DRIFT" };

  if (staged.selector) {
    if (!live.element || !staged.context.element) return { allowed: false, reason: "ELEMENT_CONTEXT_MISSING" };
    if (live.element.fingerprint !== staged.context.element.fingerprint) {
      return { allowed: false, reason: "ELEMENT_CONTEXT_DRIFT" };
    }
  }
  return { allowed: true };
}

export function publicActionSummary(staged: StagedBrowserAction): Record<string, unknown> {
  return {
    actionId: staged.actionId,
    operation: staged.operation,
    selector: staged.selector ?? null,
    key: staged.key ?? null,
    valueCharacters: staged.value?.length ?? null,
    valueDigest: staged.value === undefined ? null : sha256Binding(staged.value),
    classification: staged.classification,
    authority: staged.authority,
    policyVersion: staged.policyVersion,
    createdAt: staged.createdAt,
    expiresAt: staged.expiresAt,
    page: {
      index: staged.context.pageIndex,
      url: staged.context.url,
      origin: staged.context.origin,
      title: staged.context.title,
      element: staged.context.element
    },
    binding: staged.binding
  };
}

export function buildReceipt(
  input: Omit<BrowserReceipt, "receiptHash"> & { receiptHash?: never }
): BrowserReceipt {
  const receiptHash = sha256Binding(input);
  return { ...input, receiptHash };
}

export function verifyReceiptIntegrity(receipt: BrowserReceipt): boolean {
  const { receiptHash, ...unsigned } = receipt;
  return sha256Binding(unsigned) === receiptHash;
}

function isLoopbackHost(hostname: string): boolean {
  const normalized = hostname.toLowerCase();
  return normalized === "localhost" || normalized === "127.0.0.1" || normalized === "[::1]" || normalized === "::1";
}

function hostMatchesPattern(hostname: string, pattern: string): boolean {
  const host = hostname.toLowerCase();
  const normalized = pattern.trim().toLowerCase();
  if (!normalized) return false;
  if (normalized.startsWith("*.")) {
    const suffix = normalized.slice(1);
    return host.endsWith(suffix) && host !== suffix.slice(1);
  }
  return host === normalized;
}

export function assertGovernedNavigationUrl(
  rawUrl: string,
  options: { allowedHosts?: string[]; allowInsecureHttp?: boolean } = {}
): URL {
  const url = new URL(rawUrl);
  if (url.username || url.password) throw new Error("URL_EMBEDDED_CREDENTIALS_DENIED");
  if (url.protocol !== "https:" && url.protocol !== "http:") {
    throw new Error("Only http:// and https:// navigation is admitted");
  }
  if (url.protocol === "http:" && !isLoopbackHost(url.hostname) && !options.allowInsecureHttp) {
    throw new Error("INSECURE_HTTP_DENIED");
  }

  const configured = options.allowedHosts ?? (process.env.KPGS_BROWSER_ALLOWED_HOSTS ?? "").split(",").filter(Boolean);
  if (configured.length > 0 && !configured.some((pattern) => hostMatchesPattern(url.hostname, pattern))) {
    throw new Error("HOST_NOT_ADMITTED_BY_POLICY");
  }
  return url;
}
