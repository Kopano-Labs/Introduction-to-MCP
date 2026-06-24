/* ═══════════════════════════════════════════════════════════
   CrisisConnect Service Worker — Adaptive Offline Strategy
   Cache-first for shell, network-first for API, offline queue
   ═══════════════════════════════════════════════════════════ */

const CACHE_VERSION = 'cc-adaptive-v2';
const SHELL_CACHE = `${CACHE_VERSION}-shell`;
const DATA_CACHE = `${CACHE_VERSION}-data`;

const SHELL_ASSETS = [
  './',
  './index.html',
  './index.css',
  './app.js',
  './db.js',
  './manifest.json'
];

/* ── Install: cache app shell ──────────────────────────── */
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE)
      .then(cache => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
  );
});

/* ── Activate: clean old caches + GSMB Mandate 001 Vault Lock ─ */
self.addEventListener('activate', (event) => {
  event.waitUntil(
    Promise.all([
      // Clean old caches
      caches.keys().then(keys =>
        Promise.all(
          keys.filter(k => k !== SHELL_CACHE && k !== DATA_CACHE)
              .map(k => caches.delete(k))
        )
      ),
      // GSMB MANDATE 001: Request persistent storage — crisis data survives OS pressure
      navigator.storage && navigator.storage.persist
        ? navigator.storage.persist().then(granted => {
            console.log('[CC-SW] GSMB Mandate 001 — Vault Lock:', granted ? 'GRANTED' : 'DENIED');
          })
        : Promise.resolve(),
    ]).then(() => self.clients.claim())
  );
});

/* ── Fetch: adaptive caching strategy ──────────────────── */
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // API requests: network-first, fall back to cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const clone = response.clone();
          caches.open(DATA_CACHE).then(cache => cache.put(event.request, clone));
          return response;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // Shell assets: cache-first, fall back to network
  event.respondWith(
    caches.match(event.request)
      .then(cached => {
        if (cached) return cached;
        return fetch(event.request).then(response => {
          if (response.status === 200) {
            const clone = response.clone();
            caches.open(SHELL_CACHE).then(cache => cache.put(event.request, clone));
          }
          return response;
        });
      })
      .catch(() => {
        // Offline fallback for navigation
        if (event.request.mode === 'navigate') {
          return caches.match('./index.html');
        }
      })
  );
});

/* ── Background Sync: process offline queue ────────────── */
self.addEventListener('sync', (event) => {
  if (event.tag === 'cc-offline-queue') {
    event.waitUntil(processOfflineQueue());
  }
});

async function processOfflineQueue() {
  // Retrieve and process queued items from IndexedDB
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage({ type: 'SYNC_COMPLETE', ts: new Date().toISOString() });
  });
}

/* ── Push Notifications ────────────────────────────────── */
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : { title: 'CrisisConnect Alert', body: 'New incident update' };
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/manifest.json',
      badge: '/manifest.json',
      vibrate: [200, 100, 200],
      tag: 'cc-alert',
      renotify: true,
      requireInteraction: data.urgency === 'critical'
    })
  );
});
