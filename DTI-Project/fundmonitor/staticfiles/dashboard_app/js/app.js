// Common application JavaScript utilities

// Flag to enable/disable AJAX navigation
const ENABLE_AJAX_NAV = true;

// highlight the active sidebar link based on current URL or URL passed in
function highlightActiveLink(targetUrl = null) {
    const links = document.querySelectorAll('.sidebar a');
    const currentUrl = targetUrl || window.location.href;
    
    links.forEach(link => {
        // compare without querystring or hash
        const linkHref = link.href.split(/[?#]/)[0];
        const locHref  = currentUrl.split(/[?#]/)[0];
        if (linkHref === locHref) {
            links.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        }
    });
}

// AJAX-based page navigation (loads content without full page refresh)
function navigateToPage(url, event) {
    if (event) {
        event.preventDefault();
    }
    
    // Don't navigate if it's the current page
    const currentUrl = window.location.href.split(/[?#]/)[0];
    const targetUrl = url.split(/[?#]/)[0];
    if (currentUrl === targetUrl) {
        return false;
    }
    
    // Show loading state
    const pageContent = document.querySelector('.page-content');
    pageContent.style.opacity = '0.6';
    pageContent.style.pointerEvents = 'none';
    
    // Fetch the page content via AJAX
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
    })
    .then(html => {
        // Parse the response HTML
        const parser = new DOMParser();
        const newDoc = parser.parseFromString(html, 'text/html');
        
        // Extract the new page content (everything inside .page-content)
        const newContent = newDoc.querySelector('.page-content');
        if (!newContent) {
            // Fallback to full page load if content not found
            window.location.href = url;
            return;
        }
        
        // Replace the page content
        const pageContent = document.querySelector('.page-content');
        pageContent.innerHTML = newContent.innerHTML;
        
        // Extract and apply stylesheets from the loaded page
        const links = newDoc.querySelectorAll('link[rel="stylesheet"]');
        links.forEach(link => {
            // Only add if not already loaded
            const href = link.getAttribute('href');
            if (!document.querySelector(`link[href="${href}"]`)) {
                const newLink = document.createElement('link');
                newLink.rel = 'stylesheet';
                newLink.href = href;
                document.head.appendChild(newLink);
            }
        });
        
        // Extract and apply inline styles from the loaded page
        const styles = newDoc.querySelectorAll('style');
        styles.forEach(style => {
            const newStyle = document.createElement('style');
            newStyle.textContent = style.textContent;
            document.head.appendChild(newStyle);
        });
        
        // Execute inline scripts from the loaded page (needed for data like EXPENSES_DATA)
        // Look for <script> tags in the page-content and in any data attributes
        const scripts = newDoc.querySelectorAll('script');
        scripts.forEach(script => {
            // Only execute inline scripts (not external src files that are already loaded)
            if (!script.src && script.textContent) {
                const newScript = document.createElement('script');
                newScript.textContent = script.textContent;
                document.head.appendChild(newScript);
            }
        });
        
        // Update the browser history
        window.history.pushState({url: url}, '', url);
        
        // Update active sidebar link
        highlightActiveLink(url);
        
        // Close responsive sidebar if open
        const sidebar = document.getElementById('sidebar');
        if (sidebar && sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
        }
        
        // Re-initialize page-specific scripts
        reinitializePageScripts();
        
        // Re-apply auto-fit text
        applyAutoFit();
        
        // Restore normal state
        pageContent.style.opacity = '1';
        pageContent.style.pointerEvents = 'auto';
        
        // Scroll to top
        window.scrollTo(0, 0);
    })
    .catch(error => {
        console.error('Navigation error:', error);
        // Fallback to full page load
        window.location.href = url;
    });
    
    return false;
}

// toggle the responsive sidebar (used by the mobile button)
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('show');
}

// tab switching logic for reports (disbursement / downloads etc.)
function switchTab(name, btn) {
    document.querySelectorAll('.report-tab-panel').forEach(p => p.classList.remove('active'));
    const panel = document.getElementById('panel-' + name);
    if (panel) panel.classList.add('active');

    document.querySelectorAll('.report-tab').forEach(t => t.classList.remove('active'));
    if (btn) btn.classList.add('active');
}

// print current page
function printPage() {
    window.print();
}

// placeholder for export logic; page-specific handlers may override
function exportAll() {
    // if a download link exists inside the active report panel, follow it
    const link = document.querySelector('.report-tab-panel.active .btn-download');
    if (link) {
        link.click();
        return;
    }
    console.warn('exportAll() could not find a download link');
}

// resize text to fit within container by shrinking when overflow occurs
// does not enlarge text above its computed size
function fitText(el, minPx = 8) {
    const computed = window.getComputedStyle(el);
    let maxPx = parseFloat(computed.fontSize);
    if (isNaN(maxPx) || maxPx <= 0) {
        maxPx = 16; // fallback base size
    }
    let size = maxPx;
    el.style.fontSize = size + 'px';
    // only reduce size until it fits or reaches minimum
    while (size > minPx && el.scrollWidth > el.clientWidth) {
        size -= 1;
        el.style.fontSize = size + 'px';
    }
}

function applyAutoFit() {
    // standard elements that may need text scaling
    const selectors = ['.auto-fit', '.report-kpi-value', '.cell-amount'];
    document.querySelectorAll(selectors.join(',')).forEach(el => fitText(el));
}

// Bind sidebar navigation links (only done once on page load)
function bindSidebarNavigation() {
    if (!ENABLE_AJAX_NAV) return;
    
    const links = document.querySelectorAll('.sidebar a');
    links.forEach(link => {
        // Only bind if not already bound
        if (link.dataset.navBound === 'true') return;
        
        link.addEventListener('click', function(e) {
            navigateToPage(this.href, e);
        });
        
        link.dataset.navBound = 'true';
    });
}

// DOM-ready initialization
function initApp() {
    highlightActiveLink();

    // bind sidebar toggle button (if not using inline onclick)
    const sidebarBtn = document.querySelector('.topbar-btn.d-md-none');
    if (sidebarBtn) sidebarBtn.addEventListener('click', toggleSidebar);

    // bind sidebar navigation links (AJAX) - ONLY ONCE
    bindSidebarNavigation();

    // bind print/export buttons by id
    const printBtn = document.getElementById('btn-print');
    if (printBtn) printBtn.addEventListener('click', printPage);
    const exportBtn = document.getElementById('btn-export');
    if (exportBtn) exportBtn.addEventListener('click', exportAll);

    // delegate report tab clicks (data-tab attribute required)
    document.querySelectorAll('.report-tab').forEach(btn => {
        btn.addEventListener('click', () => {
            const name = btn.dataset.tab;
            if (name) switchTab(name, btn);
        });
    });

    // initial application of auto-fit text
    applyAutoFit();
}

// Re-initialize page-specific scripts (WITHOUT re-binding sidebar)
function reinitializePageScripts() {
    // IMPORTANT: Do NOT rebind sidebar links - they persist across AJAX loads
    // Only re-initialize page-specific functionality
    
    if (typeof initializeTableFunctionality === 'function') {
        initializeTableFunctionality();
    }
    if (typeof initializeCalculations === 'function') {
        initializeCalculations();
    }
    if (typeof initializeExpensesIfReady === 'function') {
        initializeExpensesIfReady();
    }
}

document.addEventListener('DOMContentLoaded', initApp);
window.addEventListener('resize', applyAutoFit);

// Handle browser back/forward buttons
window.addEventListener('popstate', function(event) {
    if (ENABLE_AJAX_NAV && event.state && event.state.url) {
        navigateToPage(event.state.url);
    }
});

// also use ResizeObserver to update dynamically if layout changes
if (window.ResizeObserver) {
    const ro = new ResizeObserver(applyAutoFit);
    ro.observe(document.body);
}

