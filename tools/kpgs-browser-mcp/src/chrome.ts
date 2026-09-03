import puppeteer, { type Browser, type KeyInput, type Page } from "puppeteer-core";
import type { BrowserActionInput } from "./governance.js";

const DEBUG_URL = process.env.KPGS_CHROME_DEBUG_URL ?? "http://127.0.0.1:9222";
let browserPromise: Promise<Browser> | undefined;

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
    url: page.url(),
    title: await page.title(),
    text,
    truncated: text.length >= maxChars
  };
}

export async function navigatePage(pageIndex: number, url: string): Promise<Record<string, unknown>> {
  const page = await getPage(pageIndex);
  const response = await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30_000 });
  return {
    pageIndex,
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
