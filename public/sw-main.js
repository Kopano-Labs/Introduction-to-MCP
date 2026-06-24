/* ═══════════════════════════════════════════════════════════════
   Kopano Labs — Service Worker (APWA Sovereign Shell)
   Offline-first. Load-shedding-tolerant. Township-built.
   Reality accommodates aesthetics — not the other way around.
   ═══════════════════════════════════════════════════════════════ */

const CACHE_VERSION = 'kopano-labs-v1';
const SHELL_CACHE = `${CACHE_VERSION}-shell`;
const FONT_CACHE = `${CACHE_VERSION}-fonts`;

const SHELL_ASSETS = [
  './',
  './index.html',
  './404.html',
  './humans.txt'
];

/* ── Install: cache app shell ──────────────────────────── */
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(SHELL_CACHE)
      .then(cache => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
  );
});

/* ── Activate: purge old caches ────────────────────────── */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => k !== SHELL_CACHE && k !== FONT_CACHE)
          .map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

/* ── Fetch: cache-first for shell, stale-while-revalidate for fonts ── */
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Google Fonts — cache with stale-while-revalidate
  if (url.hostname.includes('fonts.googleapis.com') || url.hostname.includes('fonts.gstatic.com')) {
    event.respondWith(
      caches.open(FONT_CACHE).then(cache =>
        cache.match(event.request).then(cached => {
          const fetched = fetch(event.request).then(response => {
            cache.put(event.request, response.clone());
            return response;
          }).catch(() => cached);
          return cached || fetched;
        })
      )
    );
    return;
  }

  // Sub-app pages — let them handle their own SW
  if (url.pathname.startsWith('/CrisisConnect/') ||
      url.pathname.startsWith('/fivesarena/') ||
      url.pathname.startsWith('/starfall/') ||
      url.pathname.startsWith('/othello/') ||
      url.pathname.startsWith('/freddys-farm/') ||
      url.pathname.startsWith('/careers/') ||
      url.pathname.startsWith('/sovereign-sim/') ||
      url.pathname.startsWith('/altar/') ||
      url.pathname.startsWith('/admin/') ||
      url.pathname.startsWith('/flows/') ||
      url.pathname.startsWith('/protocols/')) {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
    return;
  }

  // Shell assets — cache-first
  event.respondWith(
    caches.match(event.request)
      .then(cached => {
        if (cached) return cached;
        return fetch(event.request)
          .then(response => {
            // Cache successful same-origin responses
            if (response.ok && url.origin === self.location.origin) {
              const clone = response.clone();
              caches.open(SHELL_CACHE).then(cache => cache.put(event.request, clone));
            }
            return response;
          })
          .catch(() => {
            // Offline fallback for navigation
            if (event.request.mode === 'navigate') {
              return caches.match('./index.html');
            }
          });
      })
  );
});
