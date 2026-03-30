interface NcMonth {
  name: string;
  month_total: number | string;
  nc_data: Record<string, number | string>;
}

interface NcQuarter {
  label?: string;
  range?: string;
  total: number | string;
  months: NcMonth[];
}

interface NegosyoCenter {
  id: string;
  name: string;
}

interface NcDistrict {
  name: string;
  order?: number | string;
  district_total: number | string;
  negosyo_centers: NegosyoCenter[];
  quarters: NcQuarter[];
}

interface NcReportData {
  districts: NcDistrict[];
}

const NC_QUARTERS = [
  { label: "Q1", range: "January - March" },
  { label: "Q2", range: "April - June" },
  { label: "Q3", range: "July - September" },
  { label: "Q4", range: "October - December" },
] as const;

function ncAsNumber(value: number | string | undefined): number {
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : 0;
  }

  if (typeof value === "string") {
    const parsed = parseFloat(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  return 0;
}

function ncFormatCurrency(value: number | string | undefined): string {
  const amount = ncAsNumber(value);
  return amount > 0
    ? `₱ ${amount.toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    : "-";
}

function toggleDistrict(header: HTMLElement): void {
  const item = header.closest(".acc-item");
  if (!item) {
    return;
  }

  item.classList.toggle("open");

  const chevron = header.querySelector<HTMLElement>(".acc-chevron");
  if (chevron) {
    chevron.style.transform = item.classList.contains("open") ? "rotate(0deg)" : "rotate(-90deg)";
  }
}

function toggleNcQuarter(header: HTMLElement): void {
  const item = header.closest(".qtr-item");
  if (!item) {
    return;
  }

  item.classList.toggle("open");

  const chevron = header.querySelector<HTMLElement>(".qtr-chevron");
  if (chevron) {
    chevron.style.transform = item.classList.contains("open") ? "rotate(0deg)" : "rotate(-90deg)";
  }
}

function renderNcAccordion(accordion: HTMLElement, districts: NcDistrict[]): void {
  accordion.innerHTML = "";

  districts.forEach((district) => {
    const districtItem = document.createElement("div");
    districtItem.className = "acc-item open";

    const districtHeader = document.createElement("div");
    districtHeader.className = "acc-header";
    districtHeader.addEventListener("click", () => toggleDistrict(districtHeader));

    districtHeader.innerHTML = `
      <div class="acc-header-left">
        <i class="bi bi-chevron-down acc-chevron"></i>
        <div class="acc-q-label">${district.name}</div>
      </div>
      <div class="acc-header-right">
        <div class="dist-total-container">
          <div class="dist-total-label">Annual Disbursement</div>
          <span class="dist-total" data-district="${district.order ?? ""}">${ncFormatCurrency(district.district_total)}</span>
        </div>
      </div>
    `;

    const districtBody = document.createElement("div");
    districtBody.className = "acc-body";

    let quartersHtml = "";

    district.quarters.forEach((quarter, quarterIndex) => {
      let monthRowsHtml = "";
      const quarterNcTotals: Record<string, number> = {};

      district.negosyo_centers.forEach((center) => {
        quarterNcTotals[center.id] = 0;
      });

      quarter.months.forEach((month) => {
        let ncCellsHtml = "";

        district.negosyo_centers.forEach((center) => {
          const value = ncAsNumber(month.nc_data[center.id]);
          quarterNcTotals[center.id] = (quarterNcTotals[center.id] ?? 0) + value;
          ncCellsHtml += `
            <td style="text-align: right;">
              ${ncFormatCurrency(value)}
            </td>
          `;
        });

        monthRowsHtml += `
          <tr>
            <td><span class="row-dot"></span>${month.name}</td>
            ${ncCellsHtml}
            <td style="text-align: right; font-weight: bold;">${ncFormatCurrency(month.month_total)}</td>
          </tr>
        `;
      });

      const subtotalCellsHtml = district.negosyo_centers
        .map((center) => `<td style="text-align: right; font-weight: 700;">${ncFormatCurrency(quarterNcTotals[center.id])}</td>`)
        .join("");

      monthRowsHtml += `
        <tr class="quarter-subtotal-row q${quarterIndex + 1}">
          <td>Quarter Subtotal</td>
          ${subtotalCellsHtml}
          <td style="text-align: right; font-weight: 700;">${ncFormatCurrency(quarter.total)}</td>
        </tr>
      `;

      const ncHeaders = district.negosyo_centers
        .map((center) => `<th style="text-align: right; font-size: 9px;">${center.name}</th>`)
        .join("");

      const quarterMeta = NC_QUARTERS[quarterIndex];
      const quarterLabel = quarter.label ?? quarterMeta?.label ?? `Q${quarterIndex + 1}`;
      const quarterRange = quarter.range ?? quarterMeta?.range ?? "";

      quartersHtml += `
        <div class="qtr-item">
          <div class="qtr-hd" onclick="toggleNcQuarter(this)">
            <i class="bi bi-chevron-down qtr-chevron"></i>
            <span class="q-badge q${quarterIndex + 1}">${quarterLabel}</span>
            <span class="q-range">${quarterRange}</span>
            <span class="qtr-total q${quarterIndex + 1}">Qtr Total - ${ncFormatCurrency(quarter.total)}</span>
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

function setupNcReportButtons(): void {
  const exportButton = document.getElementById("btn-export");
  if (exportButton) {
    exportButton.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      if (typeof exportNcReportAll === "function") {
        exportNcReportAll();
      }
    });
  }

  const openAllButton = document.getElementById("open-all-btn");
  if (openAllButton) {
    openAllButton.addEventListener("click", () => {
      document.querySelectorAll<HTMLElement>(".acc-item, .qtr-item").forEach((item) => {
        item.classList.add("open");
      });

      document.querySelectorAll<HTMLElement>(".acc-chevron, .qtr-chevron").forEach((chevron) => {
        chevron.style.transform = "rotate(0deg)";
      });
    });
  }

  const closeAllButton = document.getElementById("close-all-btn");
  if (closeAllButton) {
    closeAllButton.addEventListener("click", () => {
      document.querySelectorAll<HTMLElement>(".acc-item, .qtr-item").forEach((item) => {
        item.classList.remove("open");
      });

      document.querySelectorAll<HTMLElement>(".acc-chevron, .qtr-chevron").forEach((chevron) => {
        chevron.style.transform = "rotate(-90deg)";
      });
    });
  }
}

function initNcReport(reportData: NcReportData): void {
  const accordion = document.getElementById("districts-accordion") as HTMLElement | null;
  if (accordion) {
    renderNcAccordion(accordion, reportData.districts);
  }

  setupNcReportButtons();
}

function initializeNcReportIfReady(): void {
  if (typeof NC_REPORT_DATA !== "undefined" && NC_REPORT_DATA) {
    initNcReport(NC_REPORT_DATA);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeNcReportIfReady);
} else {
  initializeNcReportIfReady();
}