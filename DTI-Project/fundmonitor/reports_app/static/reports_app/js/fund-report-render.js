"use strict";
const FUND_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const FUND_QUARTERS = [
    { label: "Q1", range: "January - March", months: [1, 2, 3] },
    { label: "Q2", range: "April - June", months: [4, 5, 6] },
    { label: "Q3", range: "July - September", months: [7, 8, 9] },
    { label: "Q4", range: "October - December", months: [10, 11, 12] },
];
function fundAsNumber(value) {
    if (typeof value === "number") {
        return Number.isFinite(value) ? value : 0;
    }
    if (typeof value === "string") {
        const parsed = parseFloat(value);
        return Number.isFinite(parsed) ? parsed : 0;
    }
    return 0;
}
function formatCurrency(value) {
    const amount = fundAsNumber(value);
    return amount > 0
        ? `₱ ${amount.toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
        : "-";
}
function toggleAccordionItem(headerElement) {
    const item = headerElement.closest(".acc-item");
    if (item) {
        item.classList.toggle("open");
    }
}
function renderFundAccordion(accordion, breakdown, funds) {
    accordion.innerHTML = "";
    FUND_QUARTERS.forEach((quarter, quarterIndex) => {
        const item = document.createElement("div");
        item.className = "acc-item open";
        const header = document.createElement("div");
        header.className = "acc-header";
        header.addEventListener("click", () => toggleAccordionItem(header));
        let quarterGrandTotal = 0;
        let monthsHtml = "";
        const quarterFundTotals = {};
        funds.forEach((fund) => {
            quarterFundTotals[fund.id] = 0;
        });
        quarter.months.forEach((monthNumber) => {
            var _a;
            const monthData = breakdown[monthNumber - 1];
            const monthTotal = fundAsNumber(monthData === null || monthData === void 0 ? void 0 : monthData.total);
            quarterGrandTotal += monthTotal;
            let fundCellsHtml = "";
            funds.forEach((fund) => {
                var _a, _b;
                const value = fundAsNumber((_a = monthData === null || monthData === void 0 ? void 0 : monthData.data) === null || _a === void 0 ? void 0 : _a[fund.id]);
                quarterFundTotals[fund.id] = ((_b = quarterFundTotals[fund.id]) !== null && _b !== void 0 ? _b : 0) + value;
                fundCellsHtml += `
          <td class="fund-cell" data-fund="${fund.id}" data-value="${value}">
            ${formatCurrency(value)}
          </td>
        `;
            });
            const monthLabel = (_a = FUND_MONTHS[monthNumber - 1]) !== null && _a !== void 0 ? _a : "";
            monthsHtml += `
        <tr class="month-row">
          <td class="month-cell">
            <span class="row-dot"></span>
            <span class="month-label">${monthLabel}</span>
          </td>
          ${fundCellsHtml}
          <td class="total-cell col-total">${formatCurrency(monthTotal)}</td>
        </tr>
      `;
        });
        const subtotalCellsHtml = funds
            .map((fund) => `<td class="fund-cell" style="font-weight:700;">${formatCurrency(quarterFundTotals[fund.id])}</td>`)
            .join("");
        monthsHtml += `
      <tr class="quarter-subtotal-row q${quarterIndex + 1}">
        <td class="month-cell">Quarter Subtotal</td>
        ${subtotalCellsHtml}
        <td class="total-cell col-total" style="font-weight:700;">${formatCurrency(quarterGrandTotal)}</td>
      </tr>
    `;
        const fundHeaders = funds
            .map((fund) => `<th style="text-align: right; font-size: 9px; color: var(--text-secondary);">${fund.name}</th>`)
            .join("");
        header.innerHTML = `
      <div class="acc-header-left">
        <i class="bi bi-chevron-down acc-chevron"></i>
        <span class="q-badge q${quarterIndex + 1}">${quarter.label}</span>
        <span class="q-range">${quarter.range}</span>
      </div>
      <div class="acc-header-right">
        <span class="q-grand-total" data-quarter="${quarterIndex + 1}">${formatCurrency(quarterGrandTotal)}</span>
      </div>
    `;
        const body = document.createElement("div");
        body.className = "acc-body";
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
function setupFundReportButtons() {
    const exportButton = document.getElementById("btn-export");
    if (exportButton) {
        exportButton.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            if (typeof exportFundReportAll === "function") {
                exportFundReportAll();
            }
        });
    }
    const openAllButton = document.getElementById("open-all-btn");
    if (openAllButton) {
        openAllButton.addEventListener("click", () => {
            document.querySelectorAll(".acc-item").forEach((item) => {
                item.classList.add("open");
            });
        });
    }
    const closeAllButton = document.getElementById("close-all-btn");
    if (closeAllButton) {
        closeAllButton.addEventListener("click", () => {
            document.querySelectorAll(".acc-item").forEach((item) => {
                item.classList.remove("open");
            });
        });
    }
    document.querySelectorAll(".filter-btn[data-tab]").forEach((button) => {
        button.addEventListener("click", () => {
            document.querySelectorAll(".filter-btn[data-tab]").forEach((btn) => btn.classList.remove("active"));
            document.querySelectorAll(".tab-panel").forEach((panel) => {
                panel.style.display = "none";
            });
            button.classList.add("active");
            const tabName = button.dataset.tab;
            if (!tabName)
                return;
            const panel = document.getElementById(`tab-${tabName}`);
            if (panel) {
                panel.style.display = "block";
            }
        });
    });
}
function initFundReport(reportData) {
    const disbursementAccordion = document.querySelector("[data-breakdown=\"disbursement\"]");
    if (disbursementAccordion) {
        renderFundAccordion(disbursementAccordion, reportData.disbursementBreakdown, reportData.funds);
    }
    const downloadsAccordion = document.querySelector("[data-breakdown=\"downloads\"]");
    if (downloadsAccordion) {
        renderFundAccordion(downloadsAccordion, reportData.downloadsBreakdown, reportData.funds);
    }
    setupFundReportButtons();
}
function initializeFundReportIfReady() {
    if (typeof FUND_REPORT_DATA !== "undefined" && FUND_REPORT_DATA) {
        initFundReport(FUND_REPORT_DATA);
    }
}
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeFundReportIfReady);
}
else {
    initializeFundReportIfReady();
}
//# sourceMappingURL=fund-report-render.js.map