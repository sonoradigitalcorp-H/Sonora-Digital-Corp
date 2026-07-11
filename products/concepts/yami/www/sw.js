// YAMI Service Worker v1.0
// Cache-first for static assets, network-first for pages + API

const CACHE = 'yami-v1';
const STATIC_CACHE = 'yami-static-v1';

const PRECACHE = [
  '/',
  '/index.html',
  '/miru.html',
  '/kiku.html',
  '/tomoni.html',
  '/icon.svg',
  '/icons/icon.svg',
  '/og-image.svg',
  '/manifest.json'
];

// Install: pre-cache app shell
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => {
      return cache.addAll(PRECACHE);
    }).then(() => self.skipWaiting())
  );
});

// Activate: clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(k => k !== CACHE && k !== STATIC_CACHE)
          .map(k => caches.delete(k))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch: network-first for pages + API, cache-first for static assets
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // API calls — network first, fallback to cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(event.request));
    return;
  }

  // Google Fonts — cache-first
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    event.respondWith(cacheFirst(event.request));
    return;
  }

  // HTML pages — network first
  if (url.pathname.endsWith('.html') || url.pathname === '/') {
    event.respondWith(networkFirst(event.request));
    return;
  }

  // Static assets (SVG, CSS, JS, fonts) — cache-first
  if (url.pathname.match(/\.(svg|css|js|json|woff2?|ttf|png|jpg)$/)) {
    event.respondWith(cacheFirst(event.request));
    return;
  }

  // Everything else — network first
  event.respondWith(networkFirst(event.request));
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (e) {
    return new Response('Offline', { status: 503 });
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (e) {
    const cached = await caches.match(request);
    if (cached) return cached;
    // For API calls, return a structured offline response
    if (request.url.includes('/api/')) {
      return new Response(
        JSON.stringify({ error: 'Sin conexión', offline: true }),
        { status: 503, headers: { 'Content-Type': 'application/json' } }
      );
    }
    return new Response('Sin conexión', { status: 503 });
  }
}
