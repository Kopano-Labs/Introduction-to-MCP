/**
 * FivesArena Service Worker — GSMB Mandate 001 (Vault Lock)
 * ==========================================================
 * Offline-first. Cache-first strategy. Load-shedding-tolerant.
 * navigator.storage.persist() called on activation.
 * 
 * Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
 */

const CACHE_NAME = 'fivesarena-v1';
const ASSETS = [
  '/fivesarena/',
  '/fivesarena/index.html',
  '/fivesarena/manifest.json',
];

// Install — cache core assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[FA-SW] Caching core assets');
      return cache.addAll(ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate — claim clients + request persistent storage (Mandate 001)
self.addEventListener('activate', (event) => {
  event.waitUntil(
    Promise.all([
      self.clients.claim(),
      // GSMB MANDATE 001: Request persistent storage
      navigator.storage && navigator.storage.persist
        ? navigator.storage.persist().then((granted) => {
            console.log('[FA-SW] Persistent storage:', granted ? 'GRANTED' : 'DENIED');
          })
        : Promise.resolve(),
      // Clean old caches
      caches.keys().then((names) =>
        Promise.all(
          names
            .filter((name) => name !== CACHE_NAME)
            .map((name) => caches.delete(name))
        )
      ),
    ])
  );
});

// Fetch — cache-first strategy (offline-first)
self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;

      return fetch(event.request)
        .then((response) => {
          // Cache successful responses
          if (response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, clone);
            });
          }
          return response;
        })
        .catch(() => {
          // Offline fallback for HTML pages
          if (event.request.headers.get('Accept')?.includes('text/html')) {
            return caches.match('/fivesarena/');
          }
        });
    })
  );
});

// Background sync support (future: pitch booking sync)
self.addEventListener('sync', (event) => {
  if (event.tag === 'pitch-booking-sync') {
    console.log('[FA-SW] Syncing pitch bookings...');
  }
});

console.log('[FA-SW] FivesArena Service Worker loaded — Mandate 001 active');
