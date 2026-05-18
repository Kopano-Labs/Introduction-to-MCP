/**
 * Kopano Context API origin for Studio fetch/WebSocket calls.
 *
 * - Dev default: http://127.0.0.1:8000 (local FastAPI)
 * - Production / .exe bundle: set VITE_KC_API_BASE_URL at build time, e.g.
 *   https://context.kopanolabs.com
 */
export function getApiBase(): string {
  const raw = import.meta.env.VITE_KC_API_BASE_URL?.trim();
  if (raw) {
    return raw.replace(/\/+$/, '');
  }
  return 'http://127.0.0.1:8000';
}

/** ws: or wss: URL matching the API origin. */
export function getWsLiveUrl(apiBase: string): string {
  if (apiBase.startsWith('https://')) {
    return `wss://${apiBase.slice('https://'.length)}/ws/live`;
  }
  if (apiBase.startsWith('http://')) {
    return `ws://${apiBase.slice('http://'.length)}/ws/live`;
  }
  return `${apiBase.replace(/^http/i, 'ws')}/ws/live`;
}
