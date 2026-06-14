/**
 * Kopano Context API origin for Studio fetch/WebSocket calls.
 *
 * - Dev default: http://127.0.0.1:8000 (local FastAPI)
 * - Production: prefer VITE_KC_API_BASE_URL when set, otherwise use the same
 *   origin as the current browser location.
 */
export function getApiBase(): string {
  const raw = import.meta.env.VITE_KC_API_BASE_URL?.trim();
  if (raw) {
    return raw.replace(/\/+$/, '');
  }
  if (typeof window !== 'undefined') {
    const { origin, hostname } = window.location;
    if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return origin.replace(/\/+$/, '');
    }
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
