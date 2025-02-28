// service-worker.js
const CACHE_NAME = 'voxalyze-cache-v1.0';
const urlsToCache = [
  '/',
  '/static/icon-390x390.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});