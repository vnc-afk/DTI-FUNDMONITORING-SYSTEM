/* table.js — Table filtering, sorting, and pagination */

// Initialize table functionality
function initializeTableFunctionality() {
  /* ── Element References ── */
  const searchInput  = document.getElementById('searchInput');
  const statusFilter = document.getElementById('statusFilter');
  const vatFilter    = document.getElementById('vatFilter');
  const tbody        = document.getElementById('tableBody');
  const noResults    = document.getElementById('noResults');
  const visibleCount = document.getElementById('visibleCount');
  const entryCount   = document.getElementById('entryCount');

  if (!tbody) return;

  /* ── Filter (Search + Status/VAT) ── */
  function filterTable() {
    const q  = searchInput ? searchInput.value.toLowerCase() : '';
    const st = statusFilter ? statusFilter.value.toLowerCase() : '';
    const vat = vatFilter ? vatFilter.value : '';
    const rows = tbody.querySelectorAll('tr');
    let visible = 0;

    rows.forEach(row => {
      const text      = row.textContent.toLowerCase();
      const rowStatus = (row.dataset.status || '').toLowerCase();
      const rowVat    = (row.dataset.vat || '').toLowerCase();
      const matchQ    = !q  || text.includes(q);
      const matchS    = !st || rowStatus === st;
      const matchVat  = !vat || rowVat.includes(vat.toLowerCase());

      if (matchQ && matchS && matchVat) {
        row.classList.remove('hidden');
        visible++;
      } else {
        row.classList.add('hidden');
      }
    });

    if (noResults) noResults.style.display = visible === 0 ? 'block' : 'none';
    if (visibleCount) visibleCount.textContent = visible;
    if (entryCount) entryCount.textContent = visible + ' entr' + (visible === 1 ? 'y' : 'ies');
  }

  if (searchInput) searchInput.addEventListener('input', filterTable);
  if (statusFilter) statusFilter.addEventListener('change', filterTable);
  if (vatFilter) vatFilter.addEventListener('change', filterTable);

  /* ── Expandable Rows ── */
  const expandableRows = document.querySelectorAll('tr.expandable-row');
  
  expandableRows.forEach(expandRow => {
    expandRow.addEventListener('click', function(e) {
      // Don't expand if clicking action buttons
      if (e.target.closest('.actions') || e.target.closest('.act-btn')) {
        return;
      }

      const recordId = this.dataset.id;
      const detailRow = document.querySelector(`tr.detail-row[data-id="${recordId}"]`);
      
      if (!detailRow) return;

      const isOpen = detailRow.classList.contains('open');
      
      // Close all other detail rows
      document.querySelectorAll('tr.detail-row.open').forEach(row => {
        if (row.dataset.id !== recordId) {
          row.classList.remove('open');
          const correspondingExpandRow = document.querySelector(`tr.expandable-row[data-id="${row.dataset.id}"]`);
          if (correspondingExpandRow) {
            correspondingExpandRow.classList.remove('expanded');
          }
        }
      });
      
      // Toggle current detail row
      if (isOpen) {
        detailRow.classList.remove('open');
        this.classList.remove('expanded');
      } else {
        detailRow.classList.add('open');
        this.classList.add('expanded');
      }
    });
  });

  /* ── Column Sort ── */
  document.querySelectorAll('thead th[data-col]').forEach(th => {
    th.addEventListener('click', () => {
      const col   = parseInt(th.dataset.col);
      const isAsc = th.classList.contains('sorted-asc');

      // Reset all headers
      document.querySelectorAll('thead th').forEach(t =>
        t.classList.remove('sorted-asc', 'sorted-desc')
      );

      // Apply new direction
      th.classList.add(isAsc ? 'sorted-desc' : 'sorted-asc');

      // Sort rows
      const rows = Array.from(tbody.querySelectorAll('tr'));
      rows.sort((a, b) => {
        const aVal = a.querySelectorAll('td')[col]?.textContent.trim() || '';
        const bVal = b.querySelectorAll('td')[col]?.textContent.trim() || '';
        return isAsc
          ? bVal.localeCompare(aVal, undefined, { numeric: true })
          : aVal.localeCompare(bVal, undefined, { numeric: true });
      });

      rows.forEach(r => tbody.appendChild(r));
    });
  });

  /* ── Pagination ── */
  document.querySelectorAll('.page-btn:not([disabled])').forEach(btn => {
    btn.addEventListener('click', function () {
      // Only activate numbered buttons (not arrow buttons)
      if (!this.querySelector('svg') && !this.querySelector('i')) {
        document.querySelectorAll('.page-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
      }
    });
  });
}

// Initialize on page load and when AJAX loads new content
document.addEventListener('DOMContentLoaded', initializeTableFunctionality);