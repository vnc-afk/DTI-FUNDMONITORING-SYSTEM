interface MooeMonthBreakdown {
  total: number | string;
  data: Record<string, number | string>;
}

interface MooeReportData {
  categoryCodes: string[];
  disbursementBreakdown: MooeMonthBreakdown[];
  downloadsBreakdown: MooeMonthBreakdown[];
}

interface MooeQuarter {
  label: string;
  range: string;
  months: number[];
}

const MOOE_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"] as const;

const MOOE_QUARTERS: MooeQuarter[] = [
  { label: "Q1", range: "January - March", months: [1, 2, 3] },
  { label: "Q2", range: "April - June", months: [4, 5, 6] },
  { label: "Q3", range: "July - September", months: [7, 8, 9] },
  { label: "Q4", range: "October - December", months: [10, 11, 12] },
];

function mooeAsNumber(value: number | string | undefined): number {
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : 0;
  }
  if (typeof value === "string") {
    const parsed = parseFloat(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }
  return 0;
}

function mooeFormatCurrency(value: number | string | undefined): string {
  const amount = mooeAsNumber(value);
  return amount > 0
    ? `₱ ${amount.toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    : "-";
}

function toggleMooeAccordionItem(headerElement: HTMLElement): void {
  const item = headerElement.closest(".acc-item");
  if (item) {
    item.classList.toggle("open");
  }
}

function renderMooeAccordion(accordion: HTMLElement, breakdown: MooeMonthBreakdown[], codes: string[]): void {
  accordion.innerHTML = "";

  MOOE_QUARTERS.forEach((quarter, quarterIndex) => {
    const item = document.createElement("div");
    item.className = "acc-item open";

    const header = document.createElement("div");
    header.className = "acc-header";
    header.addEventListener("click", () => toggleMooeAccordionItem(header));

    let quarterGrandTotal = 0;
    let monthsHtml = "";
    const quarterCodeTotals: Record<string, number> = {};

    codes.forEach((code) => {
      quarterCodeTotals[code] = 0;
    });

    quarter.months.forEach((monthNumber) => {
      const monthData = breakdown[monthNumber - 1];
      const monthTotal = mooeAsNumber(monthData?.total);
      quarterGrandTotal += monthTotal;

      let codeCellsHtml = "";
      codes.forEach((code) => {
        const value = mooeAsNumber(monthData?.data?.[code]);
        quarterCodeTotals[code] = (quarterCodeTotals[code] ?? 0) + value;
        codeCellsHtml += `
          <td class="fund-cell" data-fund="${code}" data-value="${value}">
            ${mooeFormatCurrency(value)}
          </td>
        `;
      });

      const monthLabel = MOOE_MONTHS[monthNumber - 1] ?? "";
      monthsHtml += `
        <tr class="month-row">
          <td class="month-cell">
            <span class="row-dot"></span>
            <span class="month-label">${monthLabel}</span>
          </td>
          ${codeCellsHtml}
          <td class="total-cell col-total">${mooeFormatCurrency(monthTotal)}</td>
        </tr>
      `;
    });

    const subtotalCellsHtml = codes
      .map((code) => `<td class="fund-cell" style="font-weight:700;">${mooeFormatCurrency(quarterCodeTotals[code])}</td>`)
      .join("");

    monthsHtml += `
      <tr class="quarter-subtotal-row q${quarterIndex + 1}">
        <td class="month-cell">Quarter Subtotal</td>
        ${subtotalCellsHtml}
        <td class="total-cell col-total" style="font-weight:700;">${mooeFormatCurrency(quarterGrandTotal)}</td>
      </tr>
    `;

    const codeHeaders = codes
      .map((code) => `<th style="text-align: right; font-size: 9px; color: var(--text-secondary);">${code}</th>`)
      .join("");

    header.innerHTML = `
      <div class="acc-header-left">
        <i class="bi bi-chevron-down acc-chevron"></i>
        <span class="q-badge q${quarterIndex + 1}">${quarter.label}</span>
        <span class="q-range">${quarter.range}</span>
      </div>
      <div class="acc-header-right">
        <span class="q-grand-total" data-quarter="${quarterIndex + 1}">${mooeFormatCurrency(quarterGrandTotal)}</span>
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

function setupMooeReportButtons(): void {
  const exportButton = document.getElementById("btn-export");
  if (exportButton) {
    exportButton.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      if (typeof exportMooeReportAll === "function") {
        exportMooeReportAll();
      }
    });
  }

  const openAllButton = document.getElementById("open-all-btn");
  if (openAllButton) {
    openAllButton.addEventListener("click", () => {
      document.querySelectorAll<HTMLElement>(".acc-item").forEach((item) => {
        item.classList.add("open");
      });
    });
  }

  const closeAllButton = document.getElementById("close-all-btn");
  if (closeAllButton) {
    closeAllButton.addEventListener("click", () => {
      document.querySelectorAll<HTMLElement>(".acc-item").forEach((item) => {
        item.classList.remove("open");
      });
    });
  }

  document.querySelectorAll<HTMLElement>(".filter-btn[data-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll<HTMLElement>(".filter-btn[data-tab]").forEach((btn) => btn.classList.remove("active"));
      document.querySelectorAll<HTMLElement>(".tab-panel").forEach((panel) => {
        panel.style.display = "none";
      });

      button.classList.add("active");
      const tabName = button.dataset.tab;
      if (!tabName) return;

      const panel = document.getElementById(`tab-${tabName}`);
      if (panel) {
        panel.style.display = "block";
      }
    });
  });
}

function initMooeReport(reportData: MooeReportData): void {
  const disbursementAccordion = document.querySelector<HTMLElement>("[data-breakdown=\"disbursement\"]");
  if (disbursementAccordion) {
    renderMooeAccordion(disbursementAccordion, reportData.disbursementBreakdown, reportData.categoryCodes);
  }

  const downloadsAccordion = document.querySelector<HTMLElement>("[data-breakdown=\"downloads\"]");
  if (downloadsAccordion) {
    renderMooeAccordion(downloadsAccordion, reportData.downloadsBreakdown, reportData.categoryCodes);
  }

  setupMooeReportButtons();
}

function initializeMooeReportIfReady(): void {
  if (typeof MOOE_REPORT_DATA !== "undefined" && MOOE_REPORT_DATA) {
    initMooeReport(MOOE_REPORT_DATA);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeMooeReportIfReady);
} else {
  initializeMooeReportIfReady();
}