/**
 * Unified Report Export Handler
 * Handles exporting both downloads and disbursement data combined
 */

/**
 * Convert array data to CSV format
 * @param {Array<Array>} data - 2D array of data
 * @returns {string} CSV formatted string
 */
function arrayToCSV(data) {
  return data
    .map(row => 
      row.map(cell => {
        // Escape quotes and wrap in quotes if contains comma or newline
        const str = String(cell ?? '');
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
          return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
      }).join(',')
    )
    .join('\n');
}

/**
 * Download CSV file
 * @param {string} filename - Name of file to download
 * @param {string} csvContent - CSV content as string
 */
function downloadCSV(filename, csvContent) {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * Export Fund Report (all data - both disbursement and downloads)
 */
function exportFundReportAll() {
  if (typeof FUND_REPORT_DATA === 'undefined') {
    console.error('Fund report data not available');
    return;
  }

  const data = FUND_REPORT_DATA;
  const csvRows = [];

  // Header
  csvRows.push(['FUND REPORT - COMBINED DATA', '', '', '', '']);
  csvRows.push(['Fiscal Year 2025', '', '', '', '']);
  csvRows.push(['']);

  // ═════════════════════════════════════════════════════════════════
  // DISBURSEMENT SECTION
  // ═════════════════════════════════════════════════════════════════
  csvRows.push(['DISBURSEMENT BREAKDOWN', '', '', '', '']);
  
  // Build header row with fund names
  const fundNames = data.funds.map(f => f.name);
  csvRows.push(['Month', ...fundNames, 'Total']);

  // Add monthly disbursement data
  data.disbursementBreakdown.forEach(monthData => {
    const row = [monthData.month];
    data.funds.forEach(fund => {
      const value = monthData.data[fund.id] || 0;
      row.push(parseFloat(value).toFixed(2));
    });
    row.push(parseFloat(monthData.total).toFixed(2));
    csvRows.push(row);
  });

  csvRows.push(['']);

  // ═════════════════════════════════════════════════════════════════
  // DOWNLOADS SECTION
  // ═════════════════════════════════════════════════════════════════
  csvRows.push(['DOWNLOADS BREAKDOWN', '', '', '', '']);
  csvRows.push(['Month', ...fundNames, 'Total']);

  // Add monthly downloads data
  data.downloadsBreakdown.forEach(monthData => {
    const row = [monthData.month];
    data.funds.forEach(fund => {
      const value = monthData.data[fund.id] || 0;
      row.push(parseFloat(value).toFixed(2));
    });
    row.push(parseFloat(monthData.total).toFixed(2));
    csvRows.push(row);
  });

  csvRows.push(['']);

  // ═════════════════════════════════════════════════════════════════
  // SUMMARY STATISTICS
  // ═════════════════════════════════════════════════════════════════
  csvRows.push(['SUMMARY STATISTICS', '', '', '', '']);
  csvRows.push(['Fund', 'Annual Budget', 'Total Disbursed', 'Total Downloads', 'Balance', 'BUR %']);

  data.funds.forEach(fund => {
    const budget = data.budgetData[fund.id];
    if (budget) {
      csvRows.push([
        fund.name,
        parseFloat(budget.total_budget).toFixed(2),
        parseFloat(budget.total_disbursed).toFixed(2),
        parseFloat(budget.total_downloads).toFixed(2),
        parseFloat(budget.balance).toFixed(2),
        parseFloat(budget.bur_percent).toFixed(2)
      ]);
    }
  });

  const csvContent = arrayToCSV(csvRows);
  downloadCSV('fund_report_all.csv', csvContent);
}

/**
 * Export MOOE Report (all data - both disbursement and downloads)
 */
function exportMooeReportAll() {
  if (typeof MOOE_REPORT_DATA === 'undefined') {
    console.error('MOOE report data not available');
    return;
  }

  const data = MOOE_REPORT_DATA;
  const csvRows = [];

  // Header
  csvRows.push(['MOOE REPORT - COMBINED DATA', '', '', '', '']);
  csvRows.push(['Fiscal Year 2025', 'Maintenance and Other Operating Expenses', '', '', '']);
  csvRows.push(['']);

  // ═════════════════════════════════════════════════════════════════
  // DISBURSEMENT SECTION
  // ═════════════════════════════════════════════════════════════════
  csvRows.push(['DISBURSEMENT BREAKDOWN', '', '', '', '']);
  
  // Build header row with category codes
  csvRows.push(['Month', ...data.categoryCodes, 'Total']);

  // Add monthly disbursement data
  data.disbursementBreakdown.forEach(monthData => {
    const row = [monthData.month];
    data.categoryCodes.forEach(code => {
      const value = monthData.data[code] || 0;
      row.push(parseFloat(value).toFixed(2));
    });
    row.push(parseFloat(monthData.total).toFixed(2));
    csvRows.push(row);
  });

  csvRows.push(['']);

  // ═════════════════════════════════════════════════════════════════
  // DOWNLOADS SECTION
  // ═════════════════════════════════════════════════════════════════
  csvRows.push(['DOWNLOADS BREAKDOWN', '', '', '', '']);
  csvRows.push(['Month', ...data.categoryCodes, 'Total']);

  // Add monthly downloads data
  data.downloadsBreakdown.forEach(monthData => {
    const row = [monthData.month];
    data.categoryCodes.forEach(code => {
      const value = monthData.data[code] || 0;
      row.push(parseFloat(value).toFixed(2));
    });
    row.push(parseFloat(monthData.total).toFixed(2));
    csvRows.push(row);
  });

  csvRows.push(['']);

  // ═════════════════════════════════════════════════════════════════
  // BUDGET SUMMARY
  // ═════════════════════════════════════════════════════════════════
  csvRows.push(['BUDGET SUMMARY', '', '', '', '']);
  csvRows.push(['Category', 'Annual Budget', 'Total Disbursed', 'Total Downloads', 'Balance', 'BUR %']);

  data.budgetData.forEach(budget => {
    csvRows.push([
      budget.code,
      parseFloat(budget.total_budget).toFixed(2),
      parseFloat(budget.total_disbursed).toFixed(2),
      parseFloat(budget.total_downloads).toFixed(2),
      parseFloat(budget.balance).toFixed(2),
      parseFloat(budget.bur_percent).toFixed(2)
    ]);
  });

  const csvContent = arrayToCSV(csvRows);
  downloadCSV('mooe_report_all.csv', csvContent);
}

/**
 * Export Negosyo Center Report (all data)
 */
function exportNcReportAll() {
  if (typeof NC_REPORT_DATA === 'undefined') {
    console.error('Negosyo Center report data not available');
    return;
  }

  const data = NC_REPORT_DATA;
  const csvRows = [];

  // Header
  csvRows.push(['NEGOSYO CENTER REPORT - ALL DATA', '', '', '' ]);
  csvRows.push(['Fiscal Year 2025', '', '', '']);
  csvRows.push(['']);

  // ═════════════════════════════════════════════════════════════════
  // BY DISTRICT AND NEGOSYO CENTER
  // ═════════════════════════════════════════════════════════════════
  csvRows.push(['DISBURSEMENT BY DISTRICT & NEGOSYO CENTER', '', '', '']);

  data.districts.forEach(district => {
    csvRows.push(['']);
    csvRows.push([`DISTRICT: ${district.name}`, '', '', '']);
    
    // Get all negosyo centers for this district
    const ncNames = district.negosyo_centers.map(nc => nc.name);
    
    // Add header
    csvRows.push(['Month', ...ncNames, 'Total']);
    
    // Add all months from all quarters
    district.quarters.forEach(quarter => {
      quarter.months.forEach(month => {
        const row = [month.name];
        district.negosyo_centers.forEach(nc => {
          const value = month.nc_data[nc.id] || 0;
          row.push(parseFloat(value).toFixed(2));
        });
        row.push(parseFloat(month.month_total).toFixed(2));
        csvRows.push(row);
      });
    });
    
    // Add district annual total
    csvRows.push(['ANNUAL TOTAL', '', '', ...Array(district.negosyo_centers.length).fill(''), parseFloat(district.district_total).toFixed(2)]);
  });

  csvRows.push(['']);
  csvRows.push(['SUMMARY', '', '', '']);
  csvRows.push(['District', 'Annual Disbursement']);
  
  data.districts.forEach(district => {
    csvRows.push([district.name, parseFloat(district.district_total).toFixed(2)]);
  });
  
  let grandTotal = 0;
  data.districts.forEach(d => { grandTotal += parseFloat(d.district_total); });
  csvRows.push(['TOTAL', parseFloat(grandTotal).toFixed(2)]);

  const csvContent = arrayToCSV(csvRows);
  downloadCSV('negosyo_center_report_all.csv', csvContent);
}
