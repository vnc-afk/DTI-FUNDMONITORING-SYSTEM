// Fund Report Dynamic Rendering

const FUND_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const FUND_QUARTERS = [
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

function renderFundAccordion(accordion, breakdown, funds) {
  accordion.innerHTML = '';
  
  FUND_QUARTERS.forEach((quarter, qIdx) => {
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
      
      let fundCellsHtml = '';
      funds.forEach(fund => {
        const value = monthData.data[fund.id] || 0;
        fundCellsHtml += `
          <td class="fund-cell" data-fund="${fund.id}" data-value="${value}">
            ${formatCurrency(value)}
          </td>
        `;
      });
      
      monthsHtml += `
        <tr class="month-row">
          <td class="month-cell">
            <span class="row-dot"></span>
            <span class="month-label">${FUND_MONTHS[monthNum - 1]}</span>
          </td>
          ${fundCellsHtml}
          <td class="total-cell col-total">${formatCurrency(monthTotal)}</td>
        </tr>
      `;
    });
    
    const fundHeaders = funds.map(f => `<th style="text-align: right; font-size: 9px; color: var(--text-secondary);">${f.name}</th>`).join('');
    
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
              ${fundHeaders}
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

function initFundReport(reportData) {
  // Render summary cards
  const summaryCards = document.getElementById('summary-cards');
  if (summaryCards) {
    summaryCards.innerHTML = reportData.funds.map((fund, i) => {
      const budget = reportData.budgetData[fund.id];
      return `
        <div class="scard report-row-disburse" style="animation-delay: ${i * 0.025}s">
          <div class="scard-label">${fund.name}</div>
          <div class="scard-amount">${formatCurrency(budget.total_disbursed)}</div>
          <div class="scard-pct">${budget.bur_percent.toFixed(1)}% BUR</div>
        </div>
      `;
    }).join('');
  }
  
  // Render disbursement accordion
  const disbAccordion = document.querySelector('[data-breakdown="disbursement"]');
  if (disbAccordion) {
    renderFundAccordion(disbAccordion, reportData.disbursementBreakdown, reportData.funds);
  }
  
  // Render downloads accordion
  const dlAccordion = document.querySelector('[data-breakdown="downloads"]');
  if (dlAccordion) {
    renderFundAccordion(dlAccordion, reportData.downloadsBreakdown, reportData.funds);
  }
  
  // Wire up buttons
  setupFundReportButtons();
}

function setupFundReportButtons() {
  // Override export button to export all data (both downloads and disbursement)
  const exportBtn = document.getElementById('btn-export');
  if (exportBtn) {
    exportBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      exportFundReportAll();
    });
  }

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
function initializeFundReportIfReady() {
  if (typeof FUND_REPORT_DATA !== 'undefined') {
    initFundReport(FUND_REPORT_DATA);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeFundReportIfReady);
} else {
  initializeFundReportIfReady();
}
