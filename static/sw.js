// Service Worker pour MonNkap PWA
// Version 1.0.0

const CACHE_NAME = 'monnkap-v1';
const OFFLINE_URL = '/offline/';

// Ressources essentielles à mettre en cache
const ESSENTIAL_RESOURCES = [
    '/',
    '/dashboard/home/',
    '/static/css/custom-design.css',
    '/static/manifest.json',
    '/static/favicon.svg',
    '/static/icons/icon-192.png',
    OFFLINE_URL
];

// Installation du Service Worker
self.addEventListener('install', (event) => {
    console.log('[SW] Installation...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Mise en cache des ressources essentielles');
                return cache.addAll(ESSENTIAL_RESOURCES);
            })
            .catch((error) => {
                console.error('[SW] Erreur lors de la mise en cache:', error);
            })
    );
    // Forcer l'activation immédiate
    self.skipWaiting();
});

// Activation du Service Worker
self.addEventListener('activate', (event) => {
    console.log('[SW] Activation...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[SW] Suppression ancien cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    // Prendre le contrôle immédiatement
    return self.clients.claim();
});

// Stratégie de fetch: Network First, fallback Cache
self.addEventListener('fetch', (event) => {
    // Ignorer les requêtes non-GET
    if (event.request.method !== 'GET') {
        return;
    }

    // Ignorer les requêtes admin et API externes
    if (event.request.url.includes('/admin/') || 
        event.request.url.includes('googleapis.com')) {
        return;
    }

    event.respondWith(
        // Essayer le réseau d'abord
        fetch(event.request)
            .then((response) => {
                // Mettre en cache TOUTES les réponses valides (pas seulement basic)
                if (response && response.status === 200) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    }).catch(err => console.log('[SW] Cache error:', err));
                }
                return response;
            })
            .catch(() => {
                console.log('[SW] Network failed, trying cache for:', event.request.url);
                // Si le réseau échoue, utiliser le cache
                return caches.match(event.request)
                    .then((cachedResponse) => {
                        if (cachedResponse) {
                            console.log('[SW] Serving from cache:', event.request.url);
                            return cachedResponse;
                        }
                        console.log('[SW] Not in cache, showing offline page');
                        // Si pas en cache, afficher la page offline pour les navigations
                        if (event.request.mode === 'navigate') {
                            return caches.match(OFFLINE_URL);
                        }
                    });
            })
    );
});

// Gestion des notifications push (pour le futur)
self.addEventListener('push', (event) => {
    const options = {
        body: event.data ? event.data.text() : 'Nouvelle notification',
        icon: '/static/icons/icon-192.png',
        badge: '/static/icons/badge-96.png',
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        }
    };
    
    event.waitUntil(
        self.registration.showNotification('MonNkap', options)
    );
});

// Gestion du clic sur les notifications
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/dashboard/home/')
    );
});

// Synchronisation en arrière-plan (pour le futur)
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-expenses') {
        event.waitUntil(syncExpenses());
    }
});

async function syncExpenses() {
    // TODO: Implémenter la synchronisation des dépenses offline
    console.log('[SW] Synchronisation des dépenses...');
}
