// ══════════════════════════════════════════════════════════════════════════
// CHART CONFIGURATION — DARK THEME
// ══════════════════════════════════════════════════════════════════════════

// Debug: Check if data is available
console.log('Dashboard data available:', !!window.dashboardData, window.dashboardData);

// Prevent "already declared" errors by checking if colors already defined
if (typeof C === 'undefined') {
    var C = {
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
        text:    '#8b90a8',
        textPri: '#f0f2f8',
    };
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
        'monthlyChart','fundChart','budgetChart','expenseChart','supplierChart',
        'taxChart','chequeChart','districtChart','bankChart'
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
        // ── 1. Monthly Disbursement Trend — Line with Fill ───────────────────
        const monthlyData = window.dashboardData.monthlyData;
        const mLabels = Object.keys(monthlyData);
        const mValues = Object.values(monthlyData);

Plotly.newPlot('monthlyChart', [{
    x: mLabels,
    y: mValues,
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Monthly Disbursement',
    line: { color: C.teal, width: 2.5, shape: 'spline' },
    marker: { size: 5, color: C.teal, line: { color: '#07080f', width: 1.5 } },
    fill: 'tozeroy',
    fillcolor: 'rgba(59, 130, 246, 0.1)',
    hovertemplate: '<b>%{x}</b><br>₱%{y:,.0f}<extra></extra>',
}], {
    ...baseLayout,
    margin: { l: 60, r: 20, t: 16, b: 40 },
    xaxis: { ...axisStyle, showgrid: false },
    yaxis: { ...axisStyle },
}, config);

// ── 2. Disbursement by Fund Source — Donut ─────────────────────────────
const fundLabels = window.dashboardData.fundLabels;
const fundValues = window.dashboardData.fundValues;

Plotly.newPlot('fundChart', [{
    labels: fundLabels,
    values: fundValues,
    type: 'pie',
    hole: 0.48,
    marker: { colors: palette, line: { color: '#12141e', width: 2 } },
    textposition: 'inside',
    textinfo: 'percent',
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
    margin: { l: 10, r: 140, t: 16, b: 16 },
}, config);

// ── 3. Budget vs Disbursement — Grouped Bar ───────────────────────────
let budgetLabels = window.dashboardData.budgetLabels;
let budgetAmounts = window.dashboardData.budgetAmounts;
let disburseAmounts = window.dashboardData.disburseAmounts;

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

Plotly.newPlot('budgetChart', [
    {
        x: budgetLabels,
        y: budgetAmounts,
        type: 'bar',
        name: 'Budget',
        marker: { color: C.violet, opacity: 0.8 },
        hovertemplate: '<b>%{x}</b><br>Budget: ₱%{y:,.0f}<extra></extra>',
    },
    {
        x: budgetLabels,
        y: disburseAmounts,
        type: 'bar',
        name: 'Disbursed',
        marker: { color: C.sky, opacity: 0.8 },
        hovertemplate: '<b>%{x}</b><br>Disbursed: ₱%{y:,.0f}<extra></extra>',
    }
], {
    ...baseLayout,
    margin: { l: 60, r: 20, t: 16, b: 80 },
    xaxis: { ...axisStyle, showgrid: false, automargin: true },
    yaxis: { ...axisStyle },
    barmode: 'group',
    showlegend: true,
    legend: { orientation: 'h', x: 0, y: 1.1, bgcolor: 'rgba(0,0,0,0)' },
}, config);

// ── 4. Account Title / Expense Objects — Horizontal Bar ─────────────────
const expenseLabels = window.dashboardData.expenseLabels;
const expenseValues = window.dashboardData.expenseValues;

Plotly.newPlot('expenseChart', [{
    x: expenseValues,
    y: expenseLabels,
    type: 'bar',
    orientation: 'h',
    marker: { color: C.blue, opacity: 0.85 },
    hovertemplate: '<b>%{y}</b><br>₱%{x:,.0f}<extra></extra>',
}], {
    ...baseLayout,
    margin: { l: 200, r: 20, t: 16, b: 40 },
    xaxis: { ...axisStyle },
    yaxis: { ...axisStyle, automargin: true },
}, config);

// ── 5. Top Suppliers — Bar ──────────────────────────────────────────────
const supplierLabels = window.dashboardData.supplierLabels;
const supplierValues = window.dashboardData.supplierValues;

Plotly.newPlot('supplierChart', [{
    x: supplierLabels,
    y: supplierValues,
    type: 'bar',
    marker: { color: C.amber, opacity: 0.85 },
    hovertemplate: '<b>%{x}</b><br>₱%{y:,.0f}<extra></extra>',
}], {
    ...baseLayout,
    margin: { l: 50, r: 20, t: 16, b: 100 },
    xaxis: { ...axisStyle, showgrid: false, automargin: true },
    yaxis: { ...axisStyle },
}, config);

// ── 6. Tax Withholding Summary — Stacked Bar ────────────────────────────
const taxLabels = window.dashboardData.taxLabels;
const taxValues = window.dashboardData.taxValues;

Plotly.newPlot('taxChart', [{
    x: taxLabels,
    y: taxValues,
    type: 'bar',
    marker: { color: palette },
    hovertemplate: '<b>%{x}</b><br>₱%{y:,.0f}<extra></extra>',
}], {
    ...baseLayout,
    margin: { l: 50, r: 20, t: 16, b: 100 },
    xaxis: { ...axisStyle, showgrid: false, automargin: true },
    yaxis: { ...axisStyle },
}, config);

// ── 7. Cheque Monitoring — Donut ──────────────────────────────────────
const chequeLabels = window.dashboardData.chequeLabels;
const chequeCounts = window.dashboardData.chequeCounts;

Plotly.newPlot('chequeChart', [{
    labels: chequeLabels,
    values: chequeCounts,
    type: 'pie',
    hole: 0.48,
    marker: { colors: palette, line: { color: '#12141e', width: 2 } },
    textposition: 'inside',
    textinfo: 'percent',
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
    margin: { l: 10, r: 140, t: 16, b: 16 },
}, config);

// ── 8. District Spending — Stacked Column ───────────────────────────────
let districtLabels = window.dashboardData.districtLabels;
let districtValues = window.dashboardData.districtValues;

// Filter out "Unspecified" entries
const filteredDistricts = districtLabels
    .map((label, index) => ({ label, value: districtValues[index] }))
    .filter(item => item.label && item.label.toLowerCase() !== 'unspecified');

districtLabels = filteredDistricts.map(item => item.label);
districtValues = filteredDistricts.map(item => item.value);

Plotly.newPlot('districtChart', [{
    x: districtLabels,
    y: districtValues,
    type: 'bar',
    marker: { color: C.green, opacity: 0.85 },
    hovertemplate: '<b>%{x}</b><br>₱%{y:,.0f}<extra></extra>',
}], {
    ...baseLayout,
    margin: { l: 60, r: 20, t: 16, b: 80 },
    xaxis: { ...axisStyle, showgrid: false, automargin: true },
    yaxis: { ...axisStyle },
}, config);

// ── 9. Bank Balance Trend — Area ────────────────────────────────────────
const bankDates = window.dashboardData.bankDates;
const bankDebits = window.dashboardData.bankDebits;
const bankCredits = window.dashboardData.bankCredits;
const bankBalances = window.dashboardData.bankBalances;

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
    margin: { l: 60, r: 20, t: 16, b: 40 },
    xaxis: { ...axisStyle, showgrid: false },
    yaxis: { ...axisStyle },
    showlegend: true,
    legend: { orientation: 'h', x: 0, y: 1.1, bgcolor: 'rgba(0,0,0,0)' },
}, config);

    } catch (error) {
        console.error('Error initializing dashboard charts:', error);
    }
} // End of safeInitializeDashboardCharts() function

// ── Responsive resize (set up once) ─────────────────────────────────────
const chartIds = [
    'monthlyChart','fundChart','budgetChart','expenseChart','supplierChart',
    'taxChart','chequeChart','districtChart','bankChart'
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
});
