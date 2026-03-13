// MOOE Report Dynamic Rendering

const MOOE_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MOOE_QUARTERS = [
  { label: "Q1", range: "January – March", months: [1, 2, 3] },
  { label: "Q2", range: "April – June", months: [4, 5, 6] },
  { label: "Q3", range: "July – September", months: [7, 8, 9] },
  { label: "Q4", range: "October – December", months: [10, 11, 12] },
];

function formatCurrency(value) {
  return value > 0
    ? `₱ ${parseFloat(value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    : '—';
}

function toggleAccordionItem(headerElement) {
  const item = headerElement.closest('.acc-item');
  if (item) {
    item.classList.toggle('open');
  }
}

function renderMooeAccordion(accordion, breakdown, codes) {
  accordion.innerHTML = '';
  
  MOOE_QUARTERS.forEach((quarter, qIdx) => {
    const item = document.createElement('div');
    item.className = 'acc-item open';
    
    const header = document.createElement('div');
    header.className = 'acc-header';
    header.onclick = function() { toggleAccordionItem(this); };
    
    let grandTotal = 0;
    let monthsHtml = '';
    
    quarter.months.forEach(monthNum => {
      const monthData = breakdown[monthNum - 1];
      const monthTotal = monthData.total;
      grandTotal += monthTotal;
      
      let codeCellsHtml = '';
      codes.forEach(code => {
        const value = monthData.data[code] || 0;
        codeCellsHtml += `
          <td class="fund-cell" data-fund="${code}" data-value="${value}">
            ${formatCurrency(value)}
          </td>
        `;
      });
      
      monthsHtml += `
        <tr class="month-row">
          <td class="month-cell">
            <span class="row-dot"></span>
            <span class="month-label">${MOOE_MONTHS[monthNum - 1]}</span>
          </td>
          ${codeCellsHtml}
          <td class="total-cell col-total">${formatCurrency(monthTotal)}</td>
        </tr>
      `;
    });
    
    const codeHeaders = codes.map(c => `<th style="text-align: right; font-size: 9px; color: var(--text-secondary);">${c}</th>`).join('');
    
    header.innerHTML = `
      <div class="acc-header-left">
        <i class="bi bi-chevron-down acc-chevron"></i>
        <span class="q-badge q${qIdx + 1}">${quarter.label}</span>
        <span class="q-range">${quarter.range}</span>
      </div>
      <div class="acc-header-right">
        <span class="q-grand-total" data-quarter="${qIdx + 1}">${formatCurrency(grandTotal)}</span>
      </div>
    `;
    
    const body = document.createElement('div');
    body.className = 'acc-body';
    body.innerHTML = `
      <div class="table-wrap" style="border-radius: 0; margin-bottom: 0;">
        <table class="quarterly-table">
          <thead>
            <tr>
              <th style="text-align: left; font-size: 9px; color: var(--text-secondary);">Month</th>
              ${codeHeaders}
              <th style="text-align: right; font-size: 9px; color: var(--text-secondary);">Total</th>
            </tr>
          </thead>
          <tbody>
            ${monthsHtml}
          </tbody>
        </table>
      </div>
    `;
    
    item.appendChild(header);
    item.appendChild(body);
    accordion.appendChild(item);
  });
}

function initMooeReport(reportData) {
  // Render disbursement accordion
  const disbAccordion = document.querySelector('[data-breakdown="disbursement"]');
  if (disbAccordion) {
    renderMooeAccordion(disbAccordion, reportData.disbursementBreakdown, reportData.categoryCodes);
  }
  
  // Render downloads accordion
  const dlAccordion = document.querySelector('[data-breakdown="downloads"]');
  if (dlAccordion) {
    renderMooeAccordion(dlAccordion, reportData.downloadsBreakdown, reportData.categoryCodes);
  }
  
  // Wire up buttons
  setupMooeReportButtons();
}

function setupMooeReportButtons() {
  const openAllBtn = document.getElementById('open-all-btn');
  if (openAllBtn) {
    openAllBtn.addEventListener('click', () => {
      document.querySelectorAll('.acc-item').forEach(item => {
        item.classList.add('open');
      });
    });
  }

  const closeAllBtn = document.getElementById('close-all-btn');
  if (closeAllBtn) {
    closeAllBtn.addEventListener('click', () => {
      document.querySelectorAll('.acc-item').forEach(item => {
        item.classList.remove('open');
      });
    });
  }

  // Tab switching
  document.querySelectorAll('.filter-btn[data-tab]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn[data-tab]').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');
      btn.classList.add('active');
      const tabId = 'tab-' + btn.dataset.tab;
      document.getElementById(tabId).style.display = 'block';
    });
  });
}

// Auto-initialize when DOM is ready or if already loaded
function initializeMooeReportIfReady() {
  if (typeof MOOE_REPORT_DATA !== 'undefined') {
    initMooeReport(MOOE_REPORT_DATA);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeMooeReportIfReady);
} else {
  initializeMooeReportIfReady();
}
