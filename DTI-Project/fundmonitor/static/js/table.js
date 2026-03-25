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

      // Check if table has expandable rows
      const hasExpandableRows = tbody.querySelectorAll('tr.expandable-row').length > 0;

      if (hasExpandableRows) {
        // Sort with expandable row pairs (detail rows stay with expandable rows)
        const expandableRows = Array.from(tbody.querySelectorAll('tr.expandable-row'));
        
        expandableRows.sort((a, b) => {
          const aVal = a.querySelectorAll('td')[col]?.textContent.trim() || '';
          const bVal = b.querySelectorAll('td')[col]?.textContent.trim() || '';
          return isAsc
            ? bVal.localeCompare(aVal, undefined, { numeric: true })
            : aVal.localeCompare(bVal, undefined, { numeric: true });
        });

        // Re-append rows with their paired detail rows
        expandableRows.forEach(expandRow => {
          const recordId = expandRow.dataset.id;
          const detailRow = document.querySelector(`tr.detail-row[data-id="${recordId}"]`);
          tbody.appendChild(expandRow);
          if (detailRow) {
            tbody.appendChild(detailRow);
          }
        });
      } else {
        // Regular sort for tables without expandable rows
        const rows = Array.from(tbody.querySelectorAll('tr'));
        rows.sort((a, b) => {
          const aVal = a.querySelectorAll('td')[col]?.textContent.trim() || '';
          const bVal = b.querySelectorAll('td')[col]?.textContent.trim() || '';
          return isAsc
            ? bVal.localeCompare(aVal, undefined, { numeric: true })
            : aVal.localeCompare(bVal, undefined, { numeric: true });
        });

        rows.forEach(r => tbody.appendChild(r));
      }
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

/* ══════════════════════════════════════════════════════════════════════════════
   TOOLBAR SEARCH, FILTER, AND EXPORT FUNCTIONALITY
   ══════════════════════════════════════════════════════════════════════════════ */

(function() {
  let searchTimeout;
  const searchInput = document.getElementById('searchInput');
  const clearBtn = document.getElementById('clearSearchBtn');
  const exportBtn = document.getElementById('exportBtn');
  const filterSelect = document.getElementById('statusFilter') || document.getElementById('filterSelect');
  const toolbarForm = document.querySelector('.toolbar-search');

  function toggleClearButton(value) {
    if (!clearBtn) {
      return;
    }
    clearBtn.style.display = value && value.trim() ? 'inline-flex' : 'none';
  }
  
  // Helper function to update table display based on results
  function updateTableDisplay(html) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const newTableBody = doc.querySelector('tbody');
    const currentTableBody = document.querySelector('table tbody');

    if (newTableBody && currentTableBody) {
      // Replace table body with new filtered content
      currentTableBody.innerHTML = newTableBody.innerHTML;

      // Check if there are actual data rows.
      const bodyRows = Array.from(currentTableBody.querySelectorAll('tr'));
      const hasDataRows = bodyRows.some((row) => {
        if (row.hasAttribute('data-id')) {
          return true;
        }
        return row.querySelector('td[colspan]') === null;
      });
      const hasNoResults = !hasDataRows;

      // Hide/show the no_results component and hide the table
      const table = currentTableBody.closest('table');
      const tableWrap = currentTableBody.closest('.table-wrap');
      const noResultsElement = tableWrap?.querySelector('.no-results');

      if (noResultsElement && table) {
        if (hasNoResults) {
          table.style.display = 'none';
          noResultsElement.style.display = 'flex';
        } else {
          table.style.display = '';
          noResultsElement.style.display = 'none';
        }
      }

      // Update footer
      const newFooter = doc.querySelector('.table-footer');
      const currentFooter = document.querySelector('.table-footer');
      if (newFooter && currentFooter) {
        currentFooter.innerHTML = newFooter.innerHTML;
      }

      // Update toolbar count
      const entryCount = doc.querySelector('#entryCount');
      const currentCount = document.querySelector('#entryCount');
      if (entryCount && currentCount) {
        currentCount.textContent = entryCount.textContent;
      }
    }
  }
  
  // Helper function to perform AJAX filtering
  function applyFilterAJAX() {
    const url = new URL(window.location);
    const formData = new FormData(toolbarForm);
    
    const params = new URLSearchParams(formData);
    for (const [key, value] of params) {
      if (value) {
        url.searchParams.set(key, value);
      } else {
        url.searchParams.delete(key);
      }
    }
    url.searchParams.set('page', '1');
    
    window.history.pushState({}, '', url.toString());
    
    fetch(url.toString(), {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => response.text())
    .then(html => {
      updateTableDisplay(html);
      
      if (filterSelect) {
        const statusParam = url.searchParams.get('status');
        filterSelect.value = statusParam || '';
      }
      if (searchInput) {
        const qParam = url.searchParams.get('q');
        searchInput.value = qParam || '';
        toggleClearButton(searchInput.value);
      }
    })
    .catch(err => {
      console.error('Filter error:', err);
      window.location.href = url.toString();
    });
  }
  
  // Search input handler
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      toggleClearButton(searchInput.value);
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(function() {
        applyFilterAJAX();
      }, 500);
    });

    toggleClearButton(searchInput.value || new URL(window.location).searchParams.get('q') || '');
  }
  
  // Filter select handler
  if (filterSelect) {
    filterSelect.addEventListener('change', function(e) {
      if (searchInput) {
        searchInput.value = '';
        toggleClearButton('');
      }
      
      const url = new URL(window.location);
      const value = filterSelect.value;
      
      if (value) {
        url.searchParams.delete('q');
        url.searchParams.set('status', value);
      } else {
        url.searchParams.delete('status');
        url.searchParams.delete('q');
      }
      url.searchParams.set('page', '1');
      
      window.history.pushState({}, '', url.toString());
      
      fetch(url.toString(), {
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.text())
      .then(html => {
        updateTableDisplay(html);
        
        if (filterSelect) {
          const statusParam = url.searchParams.get('status');
          filterSelect.value = statusParam || '';
        }
        toggleClearButton('');
      })
      .catch(err => {
        console.error('Filter error:', err);
        window.location.href = url.toString();
      });
    });
  }
  
  // Clear search button handler
  if (clearBtn) {
    clearBtn.addEventListener('click', function(e) {
      e.preventDefault();
      const url = new URL(window.location);
      url.searchParams.delete('q');
      url.searchParams.delete('page');
      
      if (searchInput) {
        searchInput.value = '';
        toggleClearButton('');
      }
      
      window.history.replaceState(null, '', url.toString());
      
      fetch(url.toString(), {
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.text())
      .then(html => {
        updateTableDisplay(html);
        
        if (filterSelect) {
          filterSelect.value = '';
        }
      })
      .catch(err => {
        console.error('Clear filter error:', err);
        window.location.href = url.toString();
      });
    });
  }

  // Export handler
  if (exportBtn) {
    exportBtn.addEventListener('click', async function() {
      const normalizeText = (value) => (value || '').replace(/\s+/g, ' ').trim();
      const xmlEscape = (value) => normalizeText(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;');

      const parseBodyRows = (doc, columnCount) => {
        const rows = Array.from(doc.querySelectorAll('tbody tr')).filter((row) => {
          const cells = row.querySelectorAll('td');
          if (!cells.length) {
            return false;
          }
          return !(cells.length === 1 && cells[0].hasAttribute('colspan'));
        });

        return rows.map((row) => {
          const cells = Array.from(row.querySelectorAll('td'));
          return Array.from({ length: columnCount }, (_, index) => normalizeText(cells[index]?.textContent || ''));
        });
      };

      const exportUrl = new URL(window.location.href);
      if (toolbarForm) {
        const formData = new FormData(toolbarForm);
        const params = new URLSearchParams(formData);
        for (const [key, value] of params.entries()) {
          if (value) {
            exportUrl.searchParams.set(key, value);
          } else {
            exportUrl.searchParams.delete(key);
          }
        }
      }
      exportUrl.searchParams.delete('export');
      exportUrl.searchParams.delete('scope');
      exportUrl.searchParams.set('page', '1');

      const originalLabel = exportBtn.textContent;
      exportBtn.disabled = true;
      exportBtn.textContent = 'Exporting...';

      try {
        let headers = [];
        let dataRows = [];
        let nextUrl = exportUrl;
        let guard = 0;

        while (nextUrl && guard < 500) {
          const response = await fetch(nextUrl.toString(), {
            headers: {
              'X-Requested-With': 'XMLHttpRequest'
            }
          });

          const html = await response.text();
          const doc = new DOMParser().parseFromString(html, 'text/html');

          if (!headers.length) {
            const headerCells = Array.from(doc.querySelectorAll('thead th'));
            headers = headerCells.map((th) => normalizeText(th.textContent || ''));
          }

          const columnCount = Math.max(headers.length, 1);
          dataRows = dataRows.concat(parseBodyRows(doc, columnCount));

          const nextLink = doc.querySelector('.pagination a[title="Next page"]');
          nextUrl = nextLink ? new URL(nextLink.getAttribute('href'), nextUrl.toString()) : null;
          guard += 1;
        }

        if (!dataRows.length) {
          return;
        }

        const columnCount = Math.max(headers.length, ...dataRows.map((row) => row.length));
        const headerRow = Array.from({ length: columnCount }, (_, index) => headers[index] || `Column ${index + 1}`);

        const colWidths = Array.from({ length: columnCount }, (_, colIndex) => {
          const lengths = [normalizeText(headerRow[colIndex]).length, ...dataRows.map((row) => row[colIndex].length)];
          const maxLen = Math.max(...lengths, 8);
          const width = Math.min(Math.max(maxLen * 7 + 16, 64), 420);
          return width;
        });

        const columnXml = colWidths.map((width) => `<Column ss:AutoFitWidth="0" ss:Width="${width}"/>`).join('');
        const headerXml = `<Row>${headerRow.map((value) => `<Cell ss:StyleID="Header"><Data ss:Type="String">${xmlEscape(value)}</Data></Cell>`).join('')}</Row>`;
        const dataXml = dataRows.map((row) => `<Row>${row.map((value) => `<Cell><Data ss:Type="String">${xmlEscape(value)}</Data></Cell>`).join('')}</Row>`).join('');

        const sheetName = (document.querySelector('.toolbar-title')?.textContent || 'Export').replace(/[\\/:*?\[\]]/g, '').trim() || 'Export';
        const xmlContent = `<?xml version="1.0"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:x="urn:schemas-microsoft-com:office:excel"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
  <Styles>
    <Style ss:ID="Default" ss:Name="Normal">
      <Alignment ss:Vertical="Center"/>
      <Font ss:FontName="Calibri" ss:Size="11"/>
    </Style>
    <Style ss:ID="Header">
      <Font ss:Bold="1"/>
      <Interior ss:Color="#E8EEF7" ss:Pattern="Solid"/>
    </Style>
  </Styles>
  <Worksheet ss:Name="${xmlEscape(sheetName).slice(0, 31)}">
    <Table>
      ${columnXml}
      ${headerXml}
      ${dataXml}
    </Table>
  </Worksheet>
</Workbook>`;

        const blob = new Blob(['\uFEFF' + xmlContent], { type: 'application/vnd.ms-excel;charset=utf-8;' });
        const url = URL.createObjectURL(blob);

        const title = (document.querySelector('.toolbar-title')?.textContent || 'export')
          .replace(/\s+/g, '_')
          .replace(/[^a-zA-Z0-9_-]/g, '')
          .toLowerCase();
        const datePart = new Date().toISOString().slice(0, 10);
        const fileName = `${title || 'export'}_${datePart}.xls`;

        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } catch (err) {
        console.error('Export failed:', err);
      } finally {
        exportBtn.disabled = false;
        exportBtn.textContent = originalLabel;
      }
    });
  }
})();