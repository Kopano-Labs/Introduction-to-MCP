import puppeteer, { type Browser, type KeyInput, type Page } from "puppeteer-core";
import {
  sha256Binding,
  type BrowserActionInput,
  type BrowserElementContext,
  type BrowserPageContext
} from "./governance.js";

const DEBUG_URL = process.env.KPGS_CHROME_DEBUG_URL ?? "http://127.0.0.1:9222";
let browserPromise: Promise<Browser> | undefined;

type ObservedElement = {
  tagName: string;
  inputType: string | null;
  autocomplete: string | null;
  name: string | null;
  id: string | null;
  role: string | null;
  formAction: string | null;
  href: string | null;
  text: string | null;
};

export async function getBrowser(): Promise<Browser> {
  if (!browserPromise) {
    browserPromise = puppeteer.connect({ browserURL: DEBUG_URL, defaultViewport: null }).catch((error) => {
      browserPromise = undefined;
      throw error;
    });
  }
  return browserPromise;
}

export function chromeDebugUrl(): string {
  return DEBUG_URL;
}

export async function getPages(): Promise<Page[]> {
  return (await getBrowser()).pages();
}

export async function getPage(pageIndex: number): Promise<Page> {
  const pages = await getPages();
  const page = pages[pageIndex];
  if (!page) throw new Error(`No Chromium page exists at index ${pageIndex}`);
  return page;
}

function originOf(rawUrl: string): string {
  try {
    return new URL(rawUrl).origin;
  } catch {
    return `OPAQUE:${rawUrl}`;
  }
}

async function targetIdOf(page: Page): Promise<string> {
  const session = await page.createCDPSession();
  try {
    const { targetInfo } = await session.send("Target.getTargetInfo");
    return targetInfo.targetId;
  } finally {
    await session.detach();
  }
}

function finalizeElementContext(selector: string, observed: ObservedElement): BrowserElementContext {
  const textDigest = observed.text === null ? null : sha256Binding(observed.text);
  const basis = {
    selector,
    tagName: observed.tagName,
    inputType: observed.inputType,
    autocomplete: observed.autocomplete,
    name: observed.name,
    id: observed.id,
    role: observed.role,
    formAction: observed.formAction,
    href: observed.href,
    textDigest
  };
  return { ...basis, fingerprint: sha256Binding(basis) };
}

function observeElementInPage(element: Element): ObservedElement {
  const html = element as HTMLElement;
  const input = element instanceof HTMLInputElement ? element : null;
  const formAction =
    element instanceof HTMLButtonElement || element instanceof HTMLInputElement
      ? element.formAction || element.getAttribute("formaction")
      : element.getAttribute("formaction");
  const href = element instanceof HTMLAnchorElement ? element.href : element.getAttribute("href");
  const text = (html.innerText || element.textContent || "").trim().slice(0, 512) || null;
  return {
    tagName: element.tagName.toLowerCase(),
    inputType: input?.type?.toLowerCase() ?? null,
    autocomplete: element.getAttribute("autocomplete"),
    name: element.getAttribute("name"),
    id: html.id || null,
    role: element.getAttribute("role"),
    formAction: formAction || null,
    href: href || null,
    text
  };
}

async function captureElementContext(page: Page, selector: string): Promise<BrowserElementContext> {
  await page.waitForSelector(selector, { visible: true, timeout: 10_000 });
  const observed = await page.$eval(selector, (element) => {
    const html = element as HTMLElement;
    const input = element instanceof HTMLInputElement ? element : null;
    const formAction =
      element instanceof HTMLButtonElement || element instanceof HTMLInputElement
        ? element.formAction || element.getAttribute("formaction")
        : element.getAttribute("formaction");
    const href = element instanceof HTMLAnchorElement ? element.href : element.getAttribute("href");
    const text = (html.innerText || element.textContent || "").trim().slice(0, 512) || null;
    return {
      tagName: element.tagName.toLowerCase(),
      inputType: input?.type?.toLowerCase() ?? null,
      autocomplete: element.getAttribute("autocomplete"),
      name: element.getAttribute("name"),
      id: html.id || null,
      role: element.getAttribute("role"),
      formAction: formAction || null,
      href: href || null,
      text
    };
  });
  return finalizeElementContext(selector, observed);
}

async function captureFocusedElementContext(page: Page): Promise<BrowserElementContext | null> {
  const observed = await page.evaluate(() => {
    const element = document.activeElement;
    if (!element) return null;
    const html = element as HTMLElement;
    const input = element instanceof HTMLInputElement ? element : null;
    const formAction =
      element instanceof HTMLButtonElement || element instanceof HTMLInputElement
        ? element.formAction || element.getAttribute("formaction")
        : element.getAttribute("formaction");
    const href = element instanceof HTMLAnchorElement ? element.href : element.getAttribute("href");
    const text = (html.innerText || element.textContent || "").trim().slice(0, 512) || null;
    return {
      tagName: element.tagName.toLowerCase(),
      inputType: input?.type?.toLowerCase() ?? null,
      autocomplete: element.getAttribute("autocomplete"),
      name: element.getAttribute("name"),
      id: html.id || null,
      role: element.getAttribute("role"),
      formAction: formAction || null,
      href: href || null,
      text
    };
  });
  return observed ? finalizeElementContext(":focus", observed) : null;
}

export async function capturePageSnapshot(pageIndex: number): Promise<BrowserPageContext> {
  const page = await getPage(pageIndex);
  const url = page.url();
  return {
    pageIndex,
    targetId: await targetIdOf(page),
    url,
    origin: originOf(url),
    title: await page.title(),
    element: null
  };
}

export async function captureInteractionContext(input: BrowserActionInput): Promise<BrowserPageContext> {
  const page = await getPage(input.pageIndex);
  const url = page.url();
  const element = input.selector
    ? await captureElementContext(page, input.selector)
    : input.operation === "press"
      ? await captureFocusedElementContext(page)
      : null;
  return {
    pageIndex: input.pageIndex,
    targetId: await targetIdOf(page),
    url,
    origin: originOf(url),
    title: await page.title(),
    element
  };
}

export async function browserStatus(): Promise<Record<string, unknown>> {
  const browser = await getBrowser();
  const pages = await browser.pages();
  return {
    connected: browser.connected,
    debugUrl: DEBUG_URL,
    browserVersion: await browser.version(),
    pageCount: pages.length
  };
}

export async function listPages(): Promise<Array<Record<string, unknown>>> {
  const pages = await getPages();
  return Promise.all(
    pages.map(async (page, index) => ({
      index,
      targetId: await targetIdOf(page),
      url: page.url(),
      title: await page.title()
    }))
  );
}

export async function readPage(pageIndex: number, maxChars = 20_000): Promise<Record<string, unknown>> {
  const page = await getPage(pageIndex);
  const text = await page.evaluate((limit) => {
    const body = document.body?.innerText ?? "";
    return body.slice(0, limit);
  }, maxChars);
  return {
    pageIndex,
    targetId: await targetIdOf(page),
    url: page.url(),
    title: await page.title(),
    text,
    truncated: text.length >= maxChars
  };
}

export async function navigatePage(pageIndex: number, url: string): Promise<Record<string, unknown>> {
  const page = await getPage(pageIndex);
  const targetId = await targetIdOf(page);
  const response = await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30_000 });
  return {
    pageIndex,
    targetId,
    url: page.url(),
    title: await page.title(),
    httpStatus: response?.status() ?? null
  };
}

export async function executeInteraction(input: BrowserActionInput): Promise<Record<string, unknown>> {
  const page = await getPage(input.pageIndex);

  if (input.operation === "click") {
    const selector = input.selector!;
    await page.waitForSelector(selector, { visible: true, timeout: 10_000 });
    await page.click(selector);
    return { operation: "click", selector, pageUrl: page.url() };
  }

  if (input.operation === "type") {
    const selector = input.selector!;
    const value = input.value!;
    await page.waitForSelector(selector, { visible: true, timeout: 10_000 });
    await page.focus(selector);
    await page.$eval(selector, (element) => {
      if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
        element.value = "";
        element.dispatchEvent(new Event("input", { bubbles: true }));
      }
    });
    await page.type(selector, value);
    return { operation: "type", selector, typedCharacters: value.length, pageUrl: page.url() };
  }

  const key = input.key! as KeyInput;
  await page.keyboard.press(key);
  return { operation: "press", key, pageUrl: page.url() };
}
