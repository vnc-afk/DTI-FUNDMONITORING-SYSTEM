/**
 * CacheManager - Intelligent client-side caching system
 * Uses localStorage for small data, IndexedDB for large data
 * Automatically manages cache expiration and size limits
 */

class CacheManager {
    constructor() {
        this.dbName = 'fundmonitor-cache';
        this.storeName = 'pages';
        this.apiStoreName = 'api-responses';
        this.metaStoreName = 'cache-meta';
        this.db = null;
        this.localStoragePrefix = 'fm-cache-';
        this.localStorageMaxSize = 5 * 1024 * 1024; // 5MB limit for localStorage
        this.cacheExpiry = 30 * 60 * 1000; // 30 minutes default
        this.initialized = false;
        
        this.init();
    }

    /**
     * Initialize IndexedDB
     */
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, 1);

            request.onerror = () => {
                console.warn('IndexedDB unavailable, falling back to localStorage only');
                this.db = null;
                this.initialized = true;
                resolve();
            };

            request.onsuccess = () => {
                this.db = request.result;
                this.initialized = true;
                resolve();
            };

            request.onupgradeneeded = (e) => {
                const db = e.target.result;
                if (!db.objectStoreNames.contains(this.storeName)) {
                    const store = db.createObjectStore(this.storeName);
                    store.createIndex('timestamp', 'timestamp', { unique: false });
                }
                if (!db.objectStoreNames.contains(this.apiStoreName)) {
                    const store = db.createObjectStore(this.apiStoreName);
                    store.createIndex('timestamp', 'timestamp', { unique: false });
                }
                if (!db.objectStoreNames.contains(this.metaStoreName)) {
                    db.createObjectStore(this.metaStoreName);
                }
            };
        });
    }

    /**
     * Get current cache size in bytes
     */
    getLocalStorageSize() {
        let size = 0;
        for (let key in localStorage) {
            if (key.startsWith(this.localStoragePrefix)) {
                size += localStorage[key].length + key.length;
            }
        }
        return size;
    }

    /**
     * Clear old cache entries to maintain size limits
     */
    async clearOldEntries(storeName) {
        if (!this.db) return;

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const index = store.index('timestamp');
            const now = Date.now();

            // Get all entries older than cache expiry
            const range = IDBKeyRange.upperBound(now - this.cacheExpiry);
            const request = index.getAll(range);

            request.onsuccess = () => {
                const entries = request.result;
                entries.forEach(entry => {
                    store.delete(entry.url || entry.key);
                });
                resolve();
            };

            request.onerror = reject;
        });
    }

    /**
     * Cache API response with automatic expiry
     */
    async cacheApiResponse(url, data, expiryMs = null) {
        const expiry = expiryMs || this.cacheExpiry;
        const cacheEntry = {
            key: url,
            url: url,
            data: data,
            timestamp: Date.now(),
            expiry: expiry
        };

        // Try IndexedDB first (better for large data)
        if (this.db) {
            try {
                await this.clearOldEntries(this.apiStoreName);
                return new Promise((resolve, reject) => {
                    const transaction = this.db.transaction([this.apiStoreName], 'readwrite');
                    const store = transaction.objectStore(this.apiStoreName);
                    const request = store.put(cacheEntry);

                    request.onsuccess = () => resolve(true);
                    request.onerror = reject;
                });
            } catch (e) {
                console.warn('IndexedDB write failed, trying localStorage');
            }
        }

        // Fallback to localStorage with size check
        const size = this.getLocalStorageSize();
        if (size < this.localStorageMaxSize) {
            try {
                localStorage.setItem(
                    this.localStoragePrefix + btoa(url),
                    JSON.stringify(cacheEntry)
                );
                return true;
            } catch (e) {
                console.warn('localStorage full, clearing old entries');
                this.clearOldLocalStorageEntries();
                return false;
            }
        }
        return false;
    }

    /**
     * Get cached API response if valid
     */
    async getApiResponse(url) {
        const now = Date.now();

        // Try IndexedDB first
        if (this.db) {
            try {
                const entry = await this.getFromIndexedDB(this.apiStoreName, url);
                if (entry && entry.timestamp + entry.expiry > now) {
                    return entry.data;
                }
                // Delete expired entry
                if (entry) await this.deleteFromIndexedDB(this.apiStoreName, url);
            } catch (e) {
                console.warn('IndexedDB read failed');
            }
        }

        // Try localStorage
        try {
            const stored = localStorage.getItem(this.localStoragePrefix + btoa(url));
            if (stored) {
                const entry = JSON.parse(stored);
                if (entry.timestamp + entry.expiry > now) {
                    return entry.data;
                }
                localStorage.removeItem(this.localStoragePrefix + btoa(url));
            }
        } catch (e) {
            console.warn('localStorage read failed');
        }

        return null;
    }

    /**
     * Cache HTML page content
     */
    async cachePageContent(url, html, expiryMs = null) {
        const expiry = expiryMs || this.cacheExpiry;
        const cacheEntry = {
            key: url,
            url: url,
            html: html,
            timestamp: Date.now(),
            expiry: expiry,
            size: html.length
        };

        if (this.db) {
            try {
                await this.clearOldEntries(this.storeName);
                return new Promise((resolve, reject) => {
                    const transaction = this.db.transaction([this.storeName], 'readwrite');
                    const store = transaction.objectStore(this.storeName);
                    const request = store.put(cacheEntry);

                    request.onsuccess = () => resolve(true);
                    request.onerror = reject;
                });
            } catch (e) {
                console.warn('Failed to cache page in IndexedDB');
            }
        }
        return false;
    }

    /**
     * Get cached page content if valid
     */
    async getPageContent(url) {
        const now = Date.now();

        if (!this.db) return null;

        try {
            const entry = await this.getFromIndexedDB(this.storeName, url);
            if (entry && entry.timestamp + entry.expiry > now) {
                return entry.html;
            }
            // Delete expired entry
            if (entry) await this.deleteFromIndexedDB(this.storeName, url);
        } catch (e) {
            console.warn('Failed to read page cache');
        }

        return null;
    }

    /**
     * Helper: Get from IndexedDB
     */
    getFromIndexedDB(storeName, key) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.get(key);

            request.onsuccess = () => resolve(request.result || null);
            request.onerror = reject;
        });
    }

    /**
     * Helper: Delete from IndexedDB
     */
    deleteFromIndexedDB(storeName, key) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.delete(key);

            request.onsuccess = resolve;
            request.onerror = reject;
        });
    }

    /**
     * Clear old localStorage entries
     */
    clearOldLocalStorageEntries() {
        const now = Date.now();
        const keysToDelete = [];

        for (let key in localStorage) {
            if (key.startsWith(this.localStoragePrefix)) {
                try {
                    const entry = JSON.parse(localStorage[key]);
                    if (entry.timestamp + entry.expiry < now) {
                        keysToDelete.push(key);
                    }
                } catch (e) {
                    keysToDelete.push(key);
                }
            }
        }

        keysToDelete.forEach(key => localStorage.removeItem(key));
    }

    /**
     * Clear all caches
     */
    async clearAll() {
        if (this.db) {
            for (let storeName of [this.storeName, this.apiStoreName]) {
                await new Promise((resolve, reject) => {
                    const transaction = this.db.transaction([storeName], 'readwrite');
                    const store = transaction.objectStore(storeName);
                    const request = store.clear();

                    request.onsuccess = resolve;
                    request.onerror = reject;
                });
            }
        }

        for (let key in localStorage) {
            if (key.startsWith(this.localStoragePrefix)) {
                localStorage.removeItem(key);
            }
        }
    }

    /**
     * Get cache statistics
     */
    async getStats() {
        return {
            localStorageSize: this.getLocalStorageSize(),
            localStorageMaxSize: this.localStorageMaxSize,
            dbAvailable: this.db !== null,
            initialized: this.initialized
        };
    }
}

// Create global instance
const cache = new CacheManager();
