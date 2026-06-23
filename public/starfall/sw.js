// ════════════════════════════════════════════════════════════
// STARFALL SALVAGE — AW3GL SERVICE WORKER
// Adaptive Web 3-Vector Graphics Layer
// PAU v3: Offline-first. No internet gatekeeping.
// 
// POC: This service worker is INVARIANT.
//   - It caches the game so 32.8% can play without data.
//   - 1 install = 1 game, on any device, forever.
//   - No app store. No platform fee. No permission slip.
//
// FOC: The old model was VARIANT.
//   - Needed internet to play. Needed an app store to install.
//   - Changed based on platform, carrier, and data balance.
//
// The service worker IS the proof that access is invariant.
// ════════════════════════════════════════════════════════════

const CACHE_NAME = 'starfall-aw3gl-v3';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap'
];

// INGRESS — Cache on install
self.addEventListener('install', event => {
  console.log('%c[AW3GL] INGRESS: Installing service worker. Caching game for offline play.', 'color:#ffd700;font-weight:bold;');
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS).then(() => {
        console.log('%c[AW3GL] INVARIANCE: Game cached. Offline access = POC.', 'color:#00d4aa;font-weight:bold;');
      });
    })
  );
  self.skipWaiting();
});

// INVARIANCE — Serve from cache, fall back to network
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        // Cache new requests dynamically (fonts, etc.)
        if (response.ok && event.request.method === 'GET') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => {
        // DECLINE — Network failed, no cache. Return offline page.
        if (event.request.destination === 'document') {
          return caches.match('./index.html');
        }
      });
    })
  );
});

// DECLINE — Clean up old caches on activate + GSMB Mandate 001 Vault Lock
self.addEventListener('activate', event => {
  console.log('%c[AW3GL] DECLINE: Clearing old caches. PAU chain preserved.', 'color:#e94560;font-weight:bold;');
  event.waitUntil(
    Promise.all([
      caches.keys().then(names => {
        return Promise.all(
          names.filter(n => n !== CACHE_NAME).map(n => caches.delete(n))
        );
      }),
      // GSMB MANDATE 001: Request persistent storage — game telemetry survives OS pressure
      navigator.storage && navigator.storage.persist
        ? navigator.storage.persist().then(granted => {
            console.log('%c[AW3GL] GSMB Mandate 001 — Vault Lock: ' + (granted ? 'GRANTED' : 'DENIED'), 'color:#ffd700;font-weight:bold;');
          })
        : Promise.resolve(),
    ])
  );
  self.clients.claim();
});
