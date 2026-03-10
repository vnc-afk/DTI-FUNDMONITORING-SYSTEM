// Negosyo Center Report Dynamic Rendering

const NC_MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const NC_QUARTERS = [
  { label: 'Q1', range: 'January – March', months: [1, 2, 3] },
  { label: 'Q2', range: 'April – June', months: [4, 5, 6] },
  { label: 'Q3', range: 'July – September', months: [7, 8, 9] },
  { label: 'Q4', range: 'October – December', months: [10, 11, 12] },
];

function formatCurrency(value) {
  return value > 0
    ? `₱ ${parseFloat(value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    : '—';
}

function toggleDistrict(header) {
  const item = header.closest('.acc-item');
  item.classList.toggle('open');
  
  // Rotate main chevron
  const chevron = header.querySelector('.acc-chevron');
  if (chevron) {
    item.classList.contains('open') 
      ? chevron.style.transform = 'rotate(0deg)'
      : chevron.style.transform = 'rotate(-90deg)';
  }
}

function toggleQuarter(header) {
  const item = header.closest('.qtr-item');
  item.classList.toggle('open');
  
  // Rotate quarter chevron
  const chevron = header.querySelector('.qtr-chevron');
  if (chevron) {
    item.classList.contains('open')
      ? chevron.style.transform = 'rotate(0deg)'
      : chevron.style.transform = 'rotate(-90deg)';
  }
}

function renderNcAccordion(accordion, districts) {
  accordion.innerHTML = '';
  
  districts.forEach(district => {
    const districtItem = document.createElement('div');
    districtItem.className = 'acc-item open';
    
    const districtHeader = document.createElement('div');
    districtHeader.className = 'acc-header';
    districtHeader.onclick = function() { toggleDistrict(this); };
    
    districtHeader.innerHTML = `
      <div class="acc-header-left">
        <i class="bi bi-chevron-down acc-chevron"></i>
        <div class="acc-q-label">${district.name}</div>
      </div>
      <div class="acc-header-right">
        <div class="dist-total-container">
          <div class="dist-total-label">Annual Disbursement</div>
          <span class="dist-total" data-district="${district.order}">${formatCurrency(district.district_total)}</span>
        </div>
      </div>
    `;
    
    const districtBody = document.createElement('div');
    districtBody.className = 'acc-body';
    
    // Build quarters for this district
    let quartersHtml = '';
    
    district.quarters.forEach((quarter, qIdx) => {
      // Build month rows HTML
      let monthRowsHtml = '';
      
      quarter.months.forEach(month => {
        let ncCellsHtml = '';
        
        district.negosyo_centers.forEach(nc => {
          const value = month.nc_data[nc.id] || 0;
          ncCellsHtml += `
            <td style="text-align: right;">
              ${formatCurrency(value)}
            </td>
          `;
        });
        
        monthRowsHtml += `
          <tr>
            <td><span class="row-dot"></span>${month.name}</td>
            ${ncCellsHtml}
            <td style="text-align: right; font-weight: bold;">${formatCurrency(month.month_total)}</td>
          </tr>
        `;
      });
      
      const ncHeaders = district.negosyo_centers
        .map(nc => `<th style="text-align: right; font-size: 9px;">${nc.name}</th>`)
        .join('');
      
      quartersHtml += `
        <div class="qtr-item open">
          <div class="qtr-hd" onclick="toggleQuarter(this)">
            <i class="bi bi-chevron-down qtr-chevron"></i>
            <span class="q-badge q${qIdx + 1}">${quarter.label}</span>
            <span class="q-range">${quarter.range}</span>
            <span class="qtr-total">Qtr Total · ${formatCurrency(quarter.total)}</span>
          </div>
          <div class="qtr-body">
            <table class="quarterly-table">
              <thead>
                <tr>
                  <th style="text-align: left; font-size: 9px;">Month</th>
                  ${ncHeaders}
                  <th style="text-align: right; font-size: 9px;">Total</th>
                </tr>
              </thead>
              <tbody>
                ${monthRowsHtml}
              </tbody>
            </table>
          </div>
        </div>
      `;
    });
    
    districtBody.innerHTML = quartersHtml;
    
    districtItem.appendChild(districtHeader);
    districtItem.appendChild(districtBody);
    accordion.appendChild(districtItem);
  });
}

function initNcReport(reportData) {
  // Render districts accordion
  const accordion = document.getElementById('districts-accordion');
  if (accordion) {
    renderNcAccordion(accordion, reportData.districts);
  }
  
  // Wire up buttons
  setupNcReportButtons();
}

function setupNcReportButtons() {
  const openAllBtn = document.getElementById('open-all-btn');
  if (openAllBtn) {
    openAllBtn.addEventListener('click', () => {
      document.querySelectorAll('.acc-item, .qtr-item').forEach(item => {
        item.classList.add('open');
      });
      
      // Reset all chevrons
      document.querySelectorAll('.acc-chevron, .qtr-chevron').forEach(chevron => {
        chevron.style.transform = 'rotate(0deg)';
      });
    });
  }

  const closeAllBtn = document.getElementById('close-all-btn');
  if (closeAllBtn) {
    closeAllBtn.addEventListener('click', () => {
      document.querySelectorAll('.acc-item, .qtr-item').forEach(item => {
        item.classList.remove('open');
      });
      
      // Reset all chevrons
      document.querySelectorAll('.acc-chevron, .qtr-chevron').forEach(chevron => {
        chevron.style.transform = 'rotate(-90deg)';
      });
    });
  }
}

// Auto-initialize when DOM is ready or if already loaded
function initializeNcReportIfReady() {
  if (typeof NC_REPORT_DATA !== 'undefined') {
    initNcReport(NC_REPORT_DATA);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeNcReportIfReady);
} else {
  initializeNcReportIfReady();
}
