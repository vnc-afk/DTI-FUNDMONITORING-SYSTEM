/**
 * PageLoader - Intelligent page loading with caching
 * Automatically caches pages and API responses to eliminate reloads
 */

class PageLoader {
    constructor() {
        this.cache = cache; // Use global CacheManager instance
        this.isLoading = false;
        this.currentUrl = window.location.href;
        this.loadingTimeout = 10000; // 10 second timeout for network requests
        this.useCache = true; // Can be disabled for bypass
    }

    /**
     * Load a page with intelligent caching
     * First tries cache, then network, then falls back to full reload
     */
    async loadPage(url, options = {}) {
        const {
            useCache = this.useCache,
            showSpinner = true,
            timeout = this.loadingTimeout,
            onProgress = null,
        } = options;

        // Normalize URL (remove hash)
        const normalizedUrl = url.split('#')[0];

        // Don't reload if already on this page
        if (normalizedUrl === this.currentUrl.split('#')[0]) {
            return null;
        }

        this.isLoading = true;
        const pageContent = document.querySelector('.page-content');
        
        if (showSpinner) {
            pageContent.style.opacity = '0.6';
            pageContent.style.pointerEvents = 'none';
        }

        try {
            onProgress && onProgress('checking_cache');

            // Step 1: Check cache first
            if (useCache) {
                const cachedHtml = await this.cache.getPageContent(normalizedUrl);
                if (cachedHtml) {
                    onProgress && onProgress('loaded_from_cache');
                    console.log('📦 Loaded from cache:', normalizedUrl);
                    this.renderPageContent(cachedHtml, normalizedUrl);
                    return { source: 'cache', url: normalizedUrl };
                }
            }

            onProgress && onProgress('fetching_network');

            // Step 2: Fetch from network with timeout
            const fetchPromise = fetch(normalizedUrl, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-Load-Type': 'ajax',
                }
            });

            const timeoutPromise = new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Network timeout')), timeout)
            );

            const response = await Promise.race([fetchPromise, timeoutPromise]);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const html = await response.text();

            onProgress && onProgress('caching');

            // Step 3: Cache the fetched content for future visits
            if (useCache) {
                await this.cache.cachePageContent(normalizedUrl, html);
                console.log('💾 Cached page:', normalizedUrl);
            }

            onProgress && onProgress('rendering');
            this.renderPageContent(html, normalizedUrl);

            return { source: 'network', url: normalizedUrl };
        } catch (error) {
            console.error('Page load error:', error);
            onProgress && onProgress('error');
            
            // If cache exists, use it as fallback even if expired
            if (useCache) {
                const cachedHtml = await this.cache.getPageContent(normalizedUrl);
                if (cachedHtml) {
                    console.warn('⚠️ Using expired cache as fallback');
                    this.renderPageContent(cachedHtml, normalizedUrl);
                    return { source: 'cache_expired', url: normalizedUrl };
                }
            }

            // Ultimate fallback: full page reload
            window.location.href = normalizedUrl;
            return null;
        } finally {
            this.isLoading = false;
            if (showSpinner) {
                pageContent.style.opacity = '1';
                pageContent.style.pointerEvents = 'auto';
            }
        }
    }

    /**
     * Render page content into the DOM
     */
    renderPageContent(html, url) {
        const parser = new DOMParser();
        const newDoc = parser.parseFromString(html, 'text/html');

        // Extract page content
        const newContent = newDoc.querySelector('.page-content');
        if (!newContent) {
            window.location.href = url;
            return;
        }

        const pageContent = document.querySelector('.page-content');
        
        // Get title
        const newTitle = newDoc.querySelector('title');
        if (newTitle) {
            document.title = newTitle.textContent;
        }

        // Store reference to newly loaded scripts that need to be executed
        const newScripts = Array.from(newDoc.querySelectorAll('script'));

        // Replace content
        pageContent.innerHTML = newContent.innerHTML;

        // Load external stylesheets
        const newLinks = newDoc.querySelectorAll('link[rel="stylesheet"]');
        newLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (!document.querySelector(`link[href="${href}"]`)) {
                const newLink = document.createElement('link');
                newLink.rel = 'stylesheet';
                newLink.href = href;
                document.head.appendChild(newLink);
            }
        });

        // Load inline styles
        const newStyles = newDoc.querySelectorAll('style');
        newStyles.forEach(style => {
            const newStyle = document.createElement('style');
            newStyle.textContent = style.textContent;
            document.head.appendChild(newStyle);
        });

        // Execute scripts in order
        this.executeScripts(newScripts);

        // Update browser history
        window.history.pushState({ url: url }, '', url);
        this.currentUrl = url;

        // Update UI
        highlightActiveLink(url);
        this.closeSidebar();

        // Re-initialize page-specific scripts
        if (typeof reinitializePageScripts === 'function') {
            reinitializePageScripts();
        }

        // Apply auto-fit text
        if (typeof applyAutoFit === 'function') {
            applyAutoFit();
        }

        // Scroll to top
        window.scrollTo(0, 0);
    }

    /**
     * Execute scripts from loaded page
     */
    async executeScripts(scripts) {
        for (const script of scripts) {
            if (script.src) {
                try {
                    await this.loadExternalScript(script.getAttribute('src'));
                } catch (e) {
                    console.warn('Failed to load script:', script.src);
                }
                continue;
            }

            if (script.textContent) {
                try {
                    const newScript = document.createElement('script');
                    newScript.textContent = script.textContent;
                    document.head.appendChild(newScript);
                } catch (e) {
                    console.error('Script execution error:', e);
                }
            }
        }
    }

    /**
     * Load external script if not already loaded
     */
    loadExternalScript(src) {
        if (document.querySelector(`script[src="${src}"]`)) {
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.async = false;
            script.onload = resolve;
            script.onerror = () => reject(new Error(`Failed to load: ${src}`));
            document.head.appendChild(script);
        });
    }

    /**
     * Close responsive sidebar after navigation
     */
    closeSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar && sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
        }
    }

    /**
     * Load API data with caching
     */
    async loadApiData(endpoint, params = {}, cacheTTL = null) {
        const url = new URL(endpoint, window.location.origin);
        Object.keys(params).forEach(key => {
            url.searchParams.append(key, params[key]);
        });

        const urlString = url.toString();

        // Check cache first
        const cached = await this.cache.getApiResponse(urlString);
        if (cached) {
            console.log('📦 API data from cache:', endpoint);
            return cached;
        }

        try {
            // Fetch from network
            const response = await fetch(urlString, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();

            // Cache the response
            await this.cache.cacheApiResponse(urlString, data, cacheTTL);
            console.log('💾 Cached API response:', endpoint);

            return data;
        } catch (error) {
            console.error('API load error:', error);
            throw error;
        }
    }

    /**
     * Prefetch and cache a URL in the background
     */
    async prefetch(url) {
        if (this.isLoading) return;

        try {
            const cached = await this.cache.getPageContent(url);
            if (cached) return; // Already cached

            const response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (response.ok) {
                const html = await response.text();
                await this.cache.cachePageContent(url, html);
                console.log('🔄 Prefetched:', url);
            }
        } catch (e) {
            // Silently fail on prefetch errors
        }
    }

    /**
     * Get cache statistics
     */
    async getCacheStats() {
        return await this.cache.getStats();
    }

    /**
     * Clear all caches
     */
    async clearAllCaches() {
        await this.cache.clearAll();
        console.log('✨ Caches cleared');
    }
}

// Create global instance
const pageLoader = new PageLoader();
