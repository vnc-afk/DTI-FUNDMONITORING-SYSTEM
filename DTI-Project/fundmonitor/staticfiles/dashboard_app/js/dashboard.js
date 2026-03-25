// ══════════════════════════════════════════════════════════════════════════
// CHART CONFIGURATION — RESPONSIVE TO DARK & LIGHT THEME
// ══════════════════════════════════════════════════════════════════════════

// Debug: Check if data is available
console.log('Dashboard data available:', !!window.dashboardData, window.dashboardData);

// Function to get CSS variable colors (adapts to current theme)
function getThemeColors() {
    const root = document.documentElement;
    const computedStyle = getComputedStyle(root);
    
    return {
        teal:    '#3b82f6',
        blue:    '#3b82f6',
        amber:   '#f59e0b',
        rose:    '#f43f5e',
        violet:  '#8b5cf6',
        sky:     '#38bdf8',
        lime:    '#a3e635',
        orange:  '#fb923c',
        green:   '#10b981',
        pink:    '#ec4899',
        bg:      'rgba(0,0,0,0)',
        plotBg:  'rgba(255,255,255,0.02)',
        grid:    'rgba(255,255,255,0.05)',
        text:    computedStyle.getPropertyValue('--text-secondary').trim(),
        textPri: computedStyle.getPropertyValue('--text-primary').trim(),
    };
}

// Prevent "already declared" errors by checking if colors already defined
if (typeof C === 'undefined') {
    var C = getThemeColors();
}

const palette = [C.teal, C.blue, C.amber, C.rose, C.violet, C.sky, C.lime, C.orange, C.green, C.pink];

const baseLayout = {
    paper_bgcolor: C.bg,
    plot_bgcolor:  C.plotBg,
    font: {
        family: '"DM Sans", -apple-system, sans-serif',
        size: 11,
        color: C.text,
    },
    hovermode: 'closest',
    margin: { l: 50, r: 20, t: 16, b: 40 },
    showlegend: false,
};

const axisStyle = {
    gridcolor:     C.grid,
    zerolinecolor: C.grid,
    tickfont:      { size: 10, color: C.text },
    showline:      false,
};

const config = { responsive: true, displayModeBar: false };

// ══════════════════════════════════════════════════════════════════════════
// Initialize Dashboard Charts — Wrapped in function for AJAX reloads
// ══════════════════════════════════════════════════════════════════════════
function safeInitializeDashboardCharts() {
    // Check if Plotly is available
    if (typeof Plotly === 'undefined') {
        console.error('Plotly library is not loaded');
        return;
    }
    
    // Check if data exists before rendering charts
    if (!window.dashboardData) {
        console.error('Dashboard data not found. Make sure the data is passed from Django context.');
        const chartsSection = document.querySelector('.charts-section');
        if (chartsSection) {
            chartsSection.innerHTML = '<p style="color: red; padding: 20px;">Error: Dashboard data not loaded. Please refresh the page or contact administrator.</p>';
        }
        return;
    }
    
    // Check if chart containers exist
    const chartIds = [
        'monthlyChart','monthlyDownloadsChart','fundChart','budgetChart','expenseChart','supplierChart',
        'mooeChart','chequeChart','districtChart','bankChart'
    ];
    let missingCharts = [];
    chartIds.forEach(id => {
        if (!document.getElementById(id)) {
            missingCharts.push(id);
        }
    });
    
    if (missingCharts.length > 0) {
        console.warn(`Chart containers missing from the page: ${missingCharts.join(', ')}`);
        return;
    }
    
    console.log('✓ Initializing dashboard charts... Data available:', !!window.dashboardData, 'Containers found:', chartIds.length);
    
    // Log all incoming data
    if (window.dashboardData) {
        console.log('=== DASHBOARD DATA DEBUG ===');
        console.log('monthlyData:', window.dashboardData.monthlyData);
        console.log('fundLabels:', window.dashboardData.fundLabels);
        console.log('fundValues:', window.dashboardData.fundValues);
        console.log('budgetLabels:', window.dashboardData.budgetLabels);
        console.log('expenseLabels:', window.dashboardData.expenseLabels);
        console.log('supplierLabels:', window.dashboardData.supplierLabels);
        console.log('========================');
    }
    
    // Purge any existing Plotly plots to avoid reusing old instances after AJAX navigation
    chartIds.forEach(id => {
        try {
            Plotly.purge(id);
            console.log(`Purged chart: ${id}`);
        } catch(e) {
            // Ignore if chart doesn't exist yet
        }
    });
    
    try {
        // Helper function to show empty state message
        const showEmptyState = (chartId, message = 'No data available for the selected period') => {
            const chartDiv = document.getElementById(chartId);
            if (chartDiv) {
                chartDiv.innerHTML = `<div style="padding: 40px; text-align: center; color: #8b90a8; font-size: 14px;">${message}</div>`;
            }
        };
        
        // ── 1. Monthly Disbursement Trend — Line with Fill ───────────────────
        let monthlyData = window.dashboardData.monthlyData;
        
        // Parse if it's a JSON string
        if (typeof monthlyData === 'string') {
            monthlyData = JSON.parse(monthlyData);
        }
        
        const mLabels = Object.keys(monthlyData);
        const mValues = Object.values(monthlyData);
        
        console.log('Monthly Data:', { monthlyData, mLabels, mValues, length: mLabels.length });

        if (mLabels.length > 0) {
            try {
                Plotly.newPlot('monthlyChart', [{
                    x: mLabels,
                    y: mValues,
                    type: 'scatter',
                    mode: 'lines+markers+text',
                    name: 'Monthly Disbursement',
                    line: { color: C.teal, width: 2.5, shape: 'spline' },
                    marker: { size: 5, color: C.teal, line: { color: '#07080f', width: 1.5 } },
                    text: mValues.map(v => '₱' + v.toLocaleString(undefined, {maximumFractionDigits: 0})),
                    textposition: 'middle right',
                    textfont: { size: 9, color: C.textPri },
                    fill: 'tozeroy',
                    fillcolor: 'rgba(59, 130, 246, 0.1)',
                    hovertemplate: '<b>%{x}</b><br>₱%{y:,.0f}<extra></extra>',
                }], {
                    ...baseLayout,
                    margin: { l: 30, r: 0, t: 0, b: 30 },
                    xaxis: { ...axisStyle, showgrid: false },
                    yaxis: { ...axisStyle },
                }, config);
                console.log('✓ Monthly chart rendered');
            } catch (e) {
                console.error('Error rendering monthly chart:', e);
                showEmptyState('monthlyChart', 'Error rendering chart');
            }
        } else {
            console.warn('No monthly data - mLabels empty');
            showEmptyState('monthlyChart', 'No monthly disbursement data available');
        }

        // ── 1b. Monthly Downloads Trend — Line with Fill ──────────────────────
        let monthlyDownloads = window.dashboardData.monthlyDownloads;
        
        // Parse if it's a JSON string
        if (typeof monthlyDownloads === 'string') {
            monthlyDownloads = JSON.parse(monthlyDownloads);
        }
        
        const dlLabels = Object.keys(monthlyDownloads);
        const dlValues = Object.values(monthlyDownloads);
        
        console.log('Monthly Downloads Data:', { monthlyDownloads, dlLabels, dlValues, length: dlLabels.length });

        if (dlLabels.length > 0) {
            try {
                Plotly.newPlot('monthlyDownloadsChart', [{
                    x: dlLabels,
                    y: dlValues,
                    type: 'scatter',
                    mode: 'lines+markers+text',
                    name: 'Monthly Downloads',
                    line: { color: C.green, width: 2.5, shape: 'spline' },
                    marker: { size: 5, color: C.green, line: { color: '#07080f', width: 1.5 } },
                    text: dlValues.map(v => '₱' + v.toLocaleString(undefined, {maximumFractionDigits: 0})),
                    textposition: 'middle right',
                    textfont: { size: 9, color: C.textPri },
                    fill: 'tozeroy',
                    fillcolor: 'rgba(16, 185, 129, 0.1)',
                    hovertemplate: '<b>%{x}</b><br>₱%{y:,.0f}<extra></extra>',
                }], {
                    ...baseLayout,
                    margin: { l: 30, r: 0, t: 0, b: 30 },
                    xaxis: { ...axisStyle, showgrid: false },
                    yaxis: { ...axisStyle },
                }, config);
                console.log('✓ Monthly downloads chart rendered');
            } catch (e) {
                console.error('Error rendering monthly downloads chart:', e);
                showEmptyState('monthlyDownloadsChart', 'Error rendering chart');
            }
        } else {
            console.warn('No monthly downloads data - dlLabels empty');
            showEmptyState('monthlyDownloadsChart', 'No monthly downloads data available');
        }

        // ── 2. Disbursement by Fund Source — Donut ─────────────────────────────
        let fundLabels = window.dashboardData.fundLabels;
        let fundValues = window.dashboardData.fundValues;        
        // Parse JSON strings if needed
        if (typeof fundLabels === 'string') fundLabels = JSON.parse(fundLabels);
        if (typeof fundValues === 'string') fundValues = JSON.parse(fundValues);
        
        console.log('Fund Data:', { fundLabels, fundValues, length: fundLabels ? fundLabels.length : 0 });
        if (fundLabels && fundLabels.length > 0) {
            Plotly.newPlot('fundChart', [{
                labels: fundLabels,
                values: fundValues,
                type: 'pie',
                hole: 0.48,
                marker: { colors: palette, line: { color: '#12141e', width: 2 } },
                textposition: 'auto',
                texttemplate: '<b>₱%{value:,.0f}</b><br>%{percent}',
                textfont: { size: 10, color: C.textPri },
                hovertemplate: '<b>%{label}</b><br>₱%{value:,.0f}<br>%{percent}<extra></extra>',
            }], {
                ...baseLayout,
                showlegend: true,
                legend: {
                    orientation: 'v',
                    x: 1.02, y: 0.5,
                    bgcolor: 'rgba(0,0,0,0)',
                    font: { size: 9, color: C.text },
                },
                margin: { l: 0, r: 0, t: 0, b: 0 },
            }, config);
        } else {
            showEmptyState('fundChart', 'No fund source data available');
        }

        // ── 3. Budget vs Disbursement — Grouped Bar ───────────────────────────
        let budgetLabels = window.dashboardData.budgetLabels;
        let budgetAmounts = window.dashboardData.budgetAmounts;
        let disburseAmounts = window.dashboardData.disburseAmounts;
        
        // Parse JSON strings if needed
        if (typeof budgetLabels === 'string') budgetLabels = JSON.parse(budgetLabels);
        if (typeof budgetAmounts === 'string') budgetAmounts = JSON.parse(budgetAmounts);
        if (typeof disburseAmounts === 'string') disburseAmounts = JSON.parse(disburseAmounts);

        // Filter out inactive funds (funds with zero budget)
        const activeBudgets = budgetLabels
            .map((label, index) => ({ 
                label, 
                budget: budgetAmounts[index], 
                disburse: disburseAmounts[index] 
            }))
            .filter(item => item.budget > 0); // Only include funds with budget > 0

        budgetLabels = activeBudgets.map(item => item.label);
        budgetAmounts = activeBudgets.map(item => item.budget);
        disburseAmounts = activeBudgets.map(item => item.disburse);

        if (budgetLabels.length > 0) {
            Plotly.newPlot('budgetChart', [
                {
                    x: budgetLabels,
                    y: budgetAmounts,
                    type: 'bar',
                    name: 'Budget',
                    marker: { color: C.violet, opacity: 0.8 },
                    textposition: 'outside',
                    texttemplate: '₱%{y:,.0f}',
                    textfont: { size: 10, color: C.textPri },
                    hovertemplate: '<b>%{x}</b><br>Budget: ₱%{y:,.0f}<extra></extra>',
                },
                {
                    x: budgetLabels,
                    y: disburseAmounts,
                    type: 'bar',
                    name: 'Disbursed',
                    marker: { color: C.sky, opacity: 0.8 },
                    textposition: 'outside',
                    texttemplate: '₱%{y:,.0f}',
                    textfont: { size: 10, color: C.textPri },
                    hovertemplate: '<b>%{x}</b><br>Disbursed: ₱%{y:,.0f}<extra></extra>',
                }
            ], {
                ...baseLayout,
                margin: { l: 30, r: 0, t: 0, b: 0 },
                xaxis: { ...axisStyle, showgrid: false, automargin: true },
                yaxis: { ...axisStyle },
                barmode: 'group',
                showlegend: true,
                legend: { orientation: 'h', x: 0, y: 1.15, bgcolor: 'rgba(0,0,0,0)', font: { size: 10 } },
            }, config);
        } else {
            showEmptyState('budgetChart', 'No budget data available');
        }

        // ── 4. Account Title / Expense Objects — Horizontal Bar ─────────────────
        let expenseLabels = window.dashboardData.expenseLabels;
        let expenseValues = window.dashboardData.expenseValues;
        
        // Parse JSON strings if needed
        if (typeof expenseLabels === 'string') expenseLabels = JSON.parse(expenseLabels);
        if (typeof expenseValues === 'string') expenseValues = JSON.parse(expenseValues);

        if (expenseLabels && expenseLabels.length > 0) {
            Plotly.newPlot('expenseChart', [{
                x: expenseValues,
                y: expenseLabels,
                type: 'bar',
                orientation: 'h',
                marker: { color: C.blue, opacity: 0.85 },
                textposition: 'outside',
                texttemplate: '₱%{x:,.0f}',
                textfont: { size: 10, color: C.textPri },
                hovertemplate: '<b>%{y}</b><br>₱%{x:,.0f}<extra></extra>',
            }], {
                ...baseLayout,
                margin: { l: 30, r: 0, t: 0, b: 0 },
                xaxis: { ...axisStyle },
                yaxis: { ...axisStyle, automargin: true },
            }, config);
        } else {
            showEmptyState('expenseChart', 'No expense data available');
        }

        // ── 5. Top Suppliers — Bar ──────────────────────────────────────────────
        let supplierLabels = window.dashboardData.supplierLabels;
        let supplierValues = window.dashboardData.supplierValues;
        
        // Parse JSON strings if needed
        if (typeof supplierLabels === 'string') supplierLabels = JSON.parse(supplierLabels);
        if (typeof supplierValues === 'string') supplierValues = JSON.parse(supplierValues);

        if (supplierLabels && supplierLabels.length > 0) {
            Plotly.newPlot('supplierChart', [{
                x: supplierLabels,
                y: supplierValues,
                type: 'bar',
                marker: { color: C.amber, opacity: 0.85 },
                textposition: 'outside',
                texttemplate: '₱%{y:,.0f}',
                textfont: { size: 10, color: C.textPri },
                hovertemplate: '<b>%{x}</b><br>₱%{y:,.0f}<extra></extra>',
            }], {
                ...baseLayout,
                margin: { l: 30, r: 0, t: 0, b: 0 },
                xaxis: { ...axisStyle, showgrid: false, automargin: true },
                yaxis: { ...axisStyle },
            }, config);
        } else {
            showEmptyState('supplierChart', 'No supplier data available');
        }

        // ── 6. MOOE Breakdown Remaining Balance — Donut ──────────────────────
        let mooeLabels = window.dashboardData.mooeLabels;
        let mooeValues = window.dashboardData.mooeValues;
        
        // Parse JSON strings if needed
        if (typeof mooeLabels === 'string') mooeLabels = JSON.parse(mooeLabels);
        if (typeof mooeValues === 'string') mooeValues = JSON.parse(mooeValues);

        if (mooeLabels && mooeLabels.length > 0) {
            Plotly.newPlot('mooeChart', [{
                labels: mooeLabels,
                values: mooeValues,
                type: 'pie',
                hole: 0.48,
                marker: { colors: palette, line: { color: '#12141e', width: 2 } },
                textposition: 'auto',
                texttemplate: '<b>₱%{value:,.0f}</b><br>%{percent}',
                textfont: { size: 10, color: C.textPri },
                hovertemplate: '<b>%{label}</b><br>₱%{value:,.0f}<br>%{percent}<extra></extra>',
            }], {
                ...baseLayout,
                showlegend: true,
                legend: {
                    orientation: 'v',
                    x: 1.02, y: 0.5,
                    bgcolor: 'rgba(0,0,0,0)',
                    font: { size: 9, color: C.text },
                },
                margin: { l: 0, r: 0, t: 0, b: 0 },
            }, config);
        } else {
            showEmptyState('mooeChart', 'No MOOE budget data available');
        }

        // ── 7. Cheque Monitoring — Donut ──────────────────────────────────────
        let chequeLabels = window.dashboardData.chequeLabels;
        let chequeCounts = window.dashboardData.chequeCounts;
        
        // Parse JSON strings if needed
        if (typeof chequeLabels === 'string') chequeLabels = JSON.parse(chequeLabels);
        if (typeof chequeCounts === 'string') chequeCounts = JSON.parse(chequeCounts);

        if (chequeLabels && chequeLabels.length > 0) {
            Plotly.newPlot('chequeChart', [{
                labels: chequeLabels,
                values: chequeCounts,
                type: 'pie',
                hole: 0.48,
                marker: { colors: palette, line: { color: '#12141e', width: 2 } },
                textposition: 'auto',
                texttemplate: '<b>%{value}</b><br>%{percent}',
                textfont: { size: 10, color: C.textPri },
                hovertemplate: '<b>%{label}</b><br>%{value} transactions<br>%{percent}<extra></extra>',
            }], {
                ...baseLayout,
                showlegend: true,
                legend: {
                    orientation: 'v',
                    x: 1.02, y: 0.5,
                    bgcolor: 'rgba(0,0,0,0)',
                    font: { size: 9, color: C.text },
                },
                margin: { l: 0, r: 0, t: 0, b: 0 },
            }, config);
        } else {
            showEmptyState('chequeChart', 'No cheque data available');
        }

        // ── 8. District Spending — Stacked Column ───────────────────────────────
        let districtLabels = window.dashboardData.districtLabels;
        let districtValues = window.dashboardData.districtValues;
        
        // Parse JSON strings if needed
        if (typeof districtLabels === 'string') districtLabels = JSON.parse(districtLabels);
        if (typeof districtValues === 'string') districtValues = JSON.parse(districtValues);

        if (districtLabels.length > 0) {
            Plotly.newPlot('districtChart', [{
                x: districtLabels,
                y: districtValues,
                type: 'bar',
                marker: { color: C.green, opacity: 0.85 },
                textposition: 'outside',
                texttemplate: '₱%{y:,.0f}',
                textfont: { size: 10, color: C.textPri },
                hovertemplate: '<b>%{x}</b><br>₱%{y:,.0f}<extra></extra>',
            }], {
                ...baseLayout,
                margin: { l: 30, r: 0, t: 0, b: 0 },
                xaxis: { ...axisStyle, showgrid: false, automargin: true },
                yaxis: { ...axisStyle },
            }, config);
        } else {
            showEmptyState('districtChart', 'No district data available');
        }

        // ── 9. Bank Balance Trend — Area ────────────────────────────────────────
        let bankDates = window.dashboardData.bankDates || [];
        let bankDebits = window.dashboardData.bankDebits || [];
        let bankCredits = window.dashboardData.bankCredits || [];
        let bankBalances = window.dashboardData.bankBalances || [];
        
        // Parse JSON strings if needed
        if (typeof bankDates === 'string') bankDates = JSON.parse(bankDates);
        if (typeof bankDebits === 'string') bankDebits = JSON.parse(bankDebits);
        if (typeof bankCredits === 'string') bankCredits = JSON.parse(bankCredits);
        if (typeof bankBalances === 'string') bankBalances = JSON.parse(bankBalances);

        console.log('Bank Trend Data:', {
            dates: bankDates,
            debits: bankDebits,
            credits: bankCredits,
            balances: bankBalances,
            hasData: bankDates.length > 0
        });

        if (bankDates.length > 0) {
            Plotly.newPlot('bankChart', [
                {
                    x: bankDates,
                    y: bankCredits,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Credit',
                    line: { color: C.green, width: 1 },
                    fill: 'tozeroy',
                    fillcolor: 'rgba(16, 185, 129, 0.1)',
                    hovertemplate: '<b>Credit</b><br>₱%{y:,.0f}<extra></extra>',
                },
                {
                    x: bankDates,
                    y: bankDebits,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Debit',
                    line: { color: C.rose, width: 1 },
                    fill: 'tozeroy',
                    fillcolor: 'rgba(244, 63, 94, 0.1)',
                    hovertemplate: '<b>Debit</b><br>₱%{y:,.0f}<extra></extra>',
                },
                {
                    x: bankDates,
                    y: bankBalances,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Balance',
                    line: { color: C.teal, width: 2.5 },
                    hovertemplate: '<b>Balance</b><br>₱%{y:,.0f}<extra></extra>',
                }
            ], {
                ...baseLayout,
                margin: { l: 30, r: 0, t: 0, b: 30 },
                xaxis: { ...axisStyle, showgrid: false },
                yaxis: { ...axisStyle },
                showlegend: true,
                legend: { orientation: 'h', x: 0, y: 1.1, bgcolor: 'rgba(0,0,0,0)' },
            }, config);
        } else {
            showEmptyState('bankChart', 'No bank statement data available for the selected period');
            console.warn('[WARNING] No bank statement data to display');
        }

    } catch (error) {
        console.error('Error initializing dashboard charts:', error);
    }
} // End of safeInitializeDashboardCharts() function

// ── Responsive resize (set up once) ─────────────────────────────────────
const chartIds = [
    'monthlyChart','monthlyDownloadsChart','fundChart','budgetChart','expenseChart','supplierChart',
    'mooeChart','chequeChart','districtChart','bankChart'
];
window.addEventListener('resize', () => {
    chartIds.forEach(id => { try { Plotly.Plots.resize(id); } catch(e) {} });
});

// Initialize charts on page load
document.addEventListener('DOMContentLoaded', () => {
    safeInitializeDashboardCharts();
    
    // Apply filters on form submission
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            this.submit();
        });
    }
    
    // Watch for theme changes using MutationObserver
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            // Check if class attribute changed (theme toggle usually changes html/body class)
            if (mutation.type === 'attributes' && 
                (mutation.attributeName === 'class' || mutation.attributeName === 'data-theme')) {
                console.log('[THEME] Theme changed - updating charts...');
                C = getThemeColors();
                safeInitializeDashboardCharts();
            }
        });
    });
    
    // Observe html element for class/theme attribute changes
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class', 'data-theme'],
        subtree: false
    });
});

// Listen for custom theme-changed events and re-render charts
document.addEventListener('theme-changed', () => {
    console.log('[THEME] Theme changed event - updating charts...');
    C = getThemeColors();
    safeInitializeDashboardCharts();
});

// Watch for localStorage changes (theme toggle from other tabs)
window.addEventListener('storage', (e) => {
    if (e.key === 'theme' || e.key === 'isDarkMode') {
        console.log('[THEME] Theme preference changed - updating charts...');
        C = getThemeColors();
        safeInitializeDashboardCharts();
    }
});
