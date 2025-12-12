/**
 * StockVision Service Worker
 * Handles Push Notifications
 */

// Listen for push events
self.addEventListener('push', function (event) {
    console.log('[SW] Push Received:', event);

    let data = {
        title: 'StockVision Alert',
        body: 'You have a new notification',
        url: '/dashboard'
    };

    // Parse payload if available
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data.body = event.data.text();
        }
    }

    const options = {
        body: data.body,
        icon: '/static/images/icon-192.png',  // Add an icon if you have one
        badge: '/static/images/badge-72.png',
        vibrate: [100, 50, 100],
        data: {
            url: data.url || '/dashboard'
        },
        actions: [
            { action: 'view', title: 'View' },
            { action: 'dismiss', title: 'Dismiss' }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Handle notification click
self.addEventListener('notificationclick', function (event) {
    console.log('[SW] Notification clicked:', event.action);

    event.notification.close();

    if (event.action === 'dismiss') {
        return;
    }

    // Open the app or focus existing window
    const targetUrl = event.notification.data?.url || '/dashboard';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function (clientList) {
            // Check if there's already an open window
            for (let client of clientList) {
                if (client.url.includes(self.location.origin) && 'focus' in client) {
                    client.navigate(targetUrl);
                    return client.focus();
                }
            }
            // Otherwise open a new window
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});

// Handle service worker installation
self.addEventListener('install', function (event) {
    console.log('[SW] Installing Service Worker...');
    self.skipWaiting();
});

// Handle service worker activation
self.addEventListener('activate', function (event) {
    console.log('[SW] Service Worker activated');
    event.waitUntil(clients.claim());
});
