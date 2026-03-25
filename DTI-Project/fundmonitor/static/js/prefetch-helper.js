/**
 * Prefetch Helper - Intelligently prefetch pages and API data
 * Speeds up navigation by caching pages before they're clicked
 */

class PrefetchHelper {
    constructor() {
        this.pageLoader = pageLoader;
        this.cache = cache;
        this.hoveredUrl = null;
        this.prefetchDelay = 300; // ms delay before prefetch
        this.prefetchTimeout = null;
        this.isPrefetching = false;
        this.maxConcurrentPrefetches = 2;
        this.activePrefetches = 0;
        
        this.init();
    }

    /**
     * Initialize prefetch helpers
     */
    init() {
        // Bind hover events on sidebar links
        document.addEventListener('mouseover', (e) => this.onLinkHover(e), true);
        document.addEventListener('mouseout', (e) => this.onLinkOut(e), true);
        
        console.log('✨ Prefetch helper initialized');
    }

    /**
     * Handle link hover - start prefetch after delay
     */
    onLinkHover(e) {
        const link = e.target.closest('a.sidebar a, .navbar a[href]');
        if (!link) return;

        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;

        // Clear previous timeout
        if (this.prefetchTimeout) {
            clearTimeout(this.prefetchTimeout);
        }

        // Schedule prefetch after delay
        this.hoveredUrl = href;
        this.prefetchTimeout = setTimeout(() => {
            this.prefetch(href);
        }, this.prefetchDelay);
    }

    /**
     * Handle link out - cancel scheduled prefetch
     */
    onLinkOut(e) {
        if (this.prefetchTimeout) {
            clearTimeout(this.prefetchTimeout);
            this.prefetchTimeout = null;
        }
    }

    /**
     * Prefetch a URL if it's not already cached
     */
    async prefetch(url) {
        if (!url || this.isPrefetching) return;

        // Limit concurrent prefetches
        if (this.activePrefetches >= this.maxConcurrentPrefetches) {
            console.log('⏳ Prefetch queue at max capacity');
            return;
        }

        this.activePrefetches++;
        try {
            await this.pageLoader.prefetch(url);
        } catch (e) {
            console.warn('Prefetch failed:', e.message);
        } finally {
            this.activePrefetches--;
        }
    }

    /**
     * Prefetch multiple URLs (e.g., likely next pages)
     */
    async prefetchMany(urls) {
        for (const url of urls) {
            if (this.activePrefetches < this.maxConcurrentPrefetches) {
                this.prefetch(url);
            } else {
                // Wait for a slot to open
                await new Promise(resolve => setTimeout(resolve, 100));
                this.prefetch(url);
            }
        }
    }

    /**
     * Prefetch related API data
     */
    async prefetchApiData(endpoints) {
        for (const endpoint of endpoints) {
            const { url, params } = endpoint;
            try {
                await this.pageLoader.loadApiData(url, params || {});
                console.log('📦 Prefetched API:', url);
            } catch (e) {
                console.warn('API prefetch failed:', url);
            }
        }
    }
}

// Create global instance
const prefetchHelper = new PrefetchHelper();

/**
 * Utility: Get all sidebar links
 */
function getSidebarLinks() {
    return Array.from(document.querySelectorAll('.sidebar a[href]'));
}

/**
 * Utility: Prefetch all sidebar links (use sparingly)
 */
function prefetchAllSidebarLinks() {
    const links = getSidebarLinks().slice(0, 5); // Limit to first 5
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (href && !href.startsWith('#')) {
            prefetchHelper.prefetch(href);
        }
    });
}

/**
 * Utility: Get cache statistics and display them
 */
async function showcachestats() {
    const stats = await cache.getStats();
    console.log('📊 Cache Statistics:');
    console.log('  - Local Storage Size:', formatBytes(stats.localStorageSize));
    console.log('  - Local Storage Max:', formatBytes(stats.localStorageMaxSize));
    console.log('  - IndexedDB Available:', stats.dbAvailable);
    console.log('  - Cache Initialized:', stats.initialized);
}

/**
 * Utility: Format bytes for display
 */
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Utility: Clear all caches and reload page
 */
async function clearCachesAndReload() {
    console.log('🧹 Clearing caches...');
    await cache.clearAll();
    console.log('✨ Caches cleared! Reloading page...');
    location.reload();
}
