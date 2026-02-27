// Common application JavaScript utilities

// highlight the active sidebar link based on current URL
function highlightActiveLink() {
    const links = document.querySelectorAll('.sidebar a');
    links.forEach(link => {
        // compare without querystring or hash
        const linkHref = link.href.split(/[?#]/)[0];
        const locHref  = window.location.href.split(/[?#]/)[0];
        if (linkHref === locHref) {
            links.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        }
    });
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

// DOM-ready initialization
function initApp() {
    highlightActiveLink();

    // bind sidebar toggle button (if not using inline onclick)
    const sidebarBtn = document.querySelector('.topbar-btn.d-md-none');
    if (sidebarBtn) sidebarBtn.addEventListener('click', toggleSidebar);

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

document.addEventListener('DOMContentLoaded', initApp);
window.addEventListener('resize', applyAutoFit);

// also use ResizeObserver to update dynamically if layout changes
if (window.ResizeObserver) {
    const ro = new ResizeObserver(applyAutoFit);
    ro.observe(document.body);
}

