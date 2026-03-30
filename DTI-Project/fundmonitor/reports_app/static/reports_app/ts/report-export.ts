type CellValue = string | number;
type SheetData = CellValue[][];

interface ExportSheet {
  name: string;
  data: SheetData;
}

interface XlsxUtils {
  book_new: () => unknown;
  aoa_to_sheet: (data: SheetData) => Record<string, any>;
  encode_cell: (cell: { r: number; c: number }) => string;
  book_append_sheet: (workbook: unknown, worksheet: unknown, name: string) => void;
}

interface XlsxGlobal {
  utils: XlsxUtils;
  writeFile: (workbook: unknown, filename: string) => void;
}

interface FundDefinition {
  id: string;
  name: string;
}

interface MonthBreakdown {
  month: string;
  data: Record<string, number | string>;
  total: number | string;
}

interface FundBudget {
  total_budget: number | string;
  total_disbursed: number | string;
  total_downloads: number | string;
  balance: number | string;
  bur_percent: number | string;
}

interface FundReportData {
  funds: FundDefinition[];
  disbursementBreakdown: MonthBreakdown[];
  downloadsBreakdown: MonthBreakdown[];
  budgetData: Record<string, FundBudget>;
}

interface MooeMonthBreakdown {
  month: string;
  data: Record<string, number | string>;
  total: number | string;
}

interface MooeBudget {
  code: string;
  total_budget: number | string;
  total_disbursed: number | string;
  total_downloads: number | string;
  balance: number | string;
  bur_percent: number | string;
}

interface MooeReportData {
  categoryCodes: string[];
  disbursementBreakdown: MooeMonthBreakdown[];
  downloadsBreakdown: MooeMonthBreakdown[];
  budgetData: MooeBudget[];
}

interface NcMonth {
  name: string;
  nc_data: Record<string, number | string>;
  month_total: number | string;
}

interface NcQuarter {
  months: NcMonth[];
}

interface NegosyoCenter {
  id: string;
  name: string;
}

interface NcDistrict {
  name: string;
  negosyo_centers: NegosyoCenter[];
  quarters: NcQuarter[];
  district_total: number | string;
}

interface NcReportData {
  districts: NcDistrict[];
}

interface ExpenseEntry {
  name: string;
  color: string;
  q1: number[];
  q2: number[];
  q3: number[];
  q4: number[];
}

function asNumber(value: number | string | undefined): number {
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : 0;
  }
  if (typeof value === "string") {
    const parsed = parseFloat(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }
  return 0;
}

function fixed2(value: number | string | undefined): string {
  return asNumber(value).toFixed(2);
}

function safeSheetName(name: string, fallbackIndex: number): string {
  const cleaned = name.replace(/[\\/:*?\[\]]/g, "").slice(0, 31);
  return cleaned || `Sheet${fallbackIndex}`;
}

function createExcelReport(filename: string, sheets: ExportSheet[]): void {
  if (typeof XLSX === "undefined" || !XLSX?.utils) {
    alert("Excel library is not loaded.");
    return;
  }

  if (!sheets || sheets.length === 0) {
    alert("No data to export");
    return;
  }

  try {
    const workbook = XLSX.utils.book_new();

    const buildColWidths = (data: SheetData): Array<{ wch: number }> => {
      const colCount = Math.max(...data.map((row) => (row ? row.length : 0)), 1);
      return Array.from({ length: colCount }, (_, colIndex) => {
        const maxLen = Math.max(
          ...data.map((row) => String(row?.[colIndex] ?? "").length),
          8
        );
        return { wch: Math.min(maxLen + 2, 60) };
      });
    };

    sheets.forEach((sheet, index) => {
      const data = sheet?.data || [];
      if (!data.length) return;

      const worksheet = XLSX.utils.aoa_to_sheet(data);
      worksheet["!cols"] = buildColWidths(data);

      const headerLength = data[0]?.length || 0;
      for (let col = 0; col < headerLength; col += 1) {
        const cellAddr = XLSX.utils.encode_cell({ r: 0, c: col });
        if (worksheet[cellAddr]) {
          worksheet[cellAddr].s = {
            font: { bold: true, color: { rgb: "FFFFFF" } },
            fill: { fgColor: { rgb: "4472C4" } },
            alignment: { horizontal: "center", vertical: "center" },
          };
        }
      }

      XLSX.utils.book_append_sheet(workbook, worksheet, safeSheetName(sheet.name || `Sheet${index + 1}`, index + 1));
    });

    const workbookLike = workbook as { SheetNames?: string[] };
    if (!workbookLike.SheetNames || workbookLike.SheetNames.length === 0) {
      alert("No rows to export");
      return;
    }

    XLSX.writeFile(workbook, `${filename}.xlsx`);
  } catch (error) {
    console.error("Export error:", error);
    alert("Export failed. Please try again.");
  }
}

function exportFundReportAll(): void {
  if (typeof FUND_REPORT_DATA === "undefined" || !FUND_REPORT_DATA) {
    console.error("Fund report data not available");
    return;
  }

  const data = FUND_REPORT_DATA;
  const csvRows: SheetData = [];

  csvRows.push(["FUND REPORT - COMBINED DATA", "", "", "", ""]);
  csvRows.push(["Fiscal Year 2025", "", "", "", ""]);
  csvRows.push([""]);
  csvRows.push(["DISBURSEMENT BREAKDOWN", "", "", "", ""]);

  const fundNames = data.funds.map((fund) => fund.name);
  csvRows.push(["Month", ...fundNames, "Total"]);

  data.disbursementBreakdown.forEach((monthData) => {
    const row: CellValue[] = [monthData.month];
    data.funds.forEach((fund) => {
      row.push(fixed2(monthData.data[fund.id]));
    });
    row.push(fixed2(monthData.total));
    csvRows.push(row);
  });

  csvRows.push([""]);
  csvRows.push(["DOWNLOADS BREAKDOWN", "", "", "", ""]);
  csvRows.push(["Month", ...fundNames, "Total"]);

  data.downloadsBreakdown.forEach((monthData) => {
    const row: CellValue[] = [monthData.month];
    data.funds.forEach((fund) => {
      row.push(fixed2(monthData.data[fund.id]));
    });
    row.push(fixed2(monthData.total));
    csvRows.push(row);
  });

  csvRows.push([""]);
  csvRows.push(["SUMMARY STATISTICS", "", "", "", ""]);
  csvRows.push(["Fund", "Annual Budget", "Total Disbursed", "Total Downloads", "Balance", "BUR %"]);

  data.funds.forEach((fund) => {
    const budget = data.budgetData[fund.id];
    if (!budget) return;
    csvRows.push([
      fund.name,
      fixed2(budget.total_budget),
      fixed2(budget.total_disbursed),
      fixed2(budget.total_downloads),
      fixed2(budget.balance),
      fixed2(budget.bur_percent),
    ]);
  });

  createExcelReport(`Fund_Report_${new Date().toISOString().split("T")[0]}`, [{ name: "Fund Report", data: csvRows }]);
}

function exportMooeReportAll(): void {
  if (typeof MOOE_REPORT_DATA === "undefined" || !MOOE_REPORT_DATA) {
    console.error("MOOE report data not available");
    return;
  }

  const data = MOOE_REPORT_DATA;
  const csvRows: SheetData = [];

  csvRows.push(["MOOE REPORT - COMBINED DATA", "", "", "", ""]);
  csvRows.push(["Fiscal Year 2025", "Maintenance and Other Operating Expenses", "", "", ""]);
  csvRows.push([""]);
  csvRows.push(["DISBURSEMENT BREAKDOWN", "", "", "", ""]);
  csvRows.push(["Month", ...data.categoryCodes, "Total"]);

  data.disbursementBreakdown.forEach((monthData) => {
    const row: CellValue[] = [monthData.month];
    data.categoryCodes.forEach((code) => {
      row.push(fixed2(monthData.data[code]));
    });
    row.push(fixed2(monthData.total));
    csvRows.push(row);
  });

  csvRows.push([""]);
  csvRows.push(["DOWNLOADS BREAKDOWN", "", "", "", ""]);
  csvRows.push(["Month", ...data.categoryCodes, "Total"]);

  data.downloadsBreakdown.forEach((monthData) => {
    const row: CellValue[] = [monthData.month];
    data.categoryCodes.forEach((code) => {
      row.push(fixed2(monthData.data[code]));
    });
    row.push(fixed2(monthData.total));
    csvRows.push(row);
  });

  csvRows.push([""]);
  csvRows.push(["BUDGET SUMMARY", "", "", "", ""]);
  csvRows.push(["Category", "Annual Budget", "Total Disbursed", "Total Downloads", "Balance", "BUR %"]);

  data.budgetData.forEach((budget) => {
    csvRows.push([
      budget.code,
      fixed2(budget.total_budget),
      fixed2(budget.total_disbursed),
      fixed2(budget.total_downloads),
      fixed2(budget.balance),
      fixed2(budget.bur_percent),
    ]);
  });

  createExcelReport(`MOOE_Report_${new Date().toISOString().split("T")[0]}`, [{ name: "MOOE Report", data: csvRows }]);
}

function exportNcReportAll(): void {
  if (typeof NC_REPORT_DATA === "undefined" || !NC_REPORT_DATA) {
    console.error("Negosyo Center report data not available");
    return;
  }

  const data = NC_REPORT_DATA;
  const csvRows: SheetData = [];

  csvRows.push(["NEGOSYO CENTER REPORT - ALL DATA", "", "", ""]);
  csvRows.push(["Fiscal Year 2025", "", "", ""]);
  csvRows.push([""]);
  csvRows.push(["DISBURSEMENT BY DISTRICT & NEGOSYO CENTER", "", "", ""]);

  data.districts.forEach((district) => {
    csvRows.push([""]);
    csvRows.push([`DISTRICT: ${district.name}`, "", "", ""]);

    const ncNames = district.negosyo_centers.map((center) => center.name);
    csvRows.push(["Month", ...ncNames, "Total"]);

    district.quarters.forEach((quarter) => {
      quarter.months.forEach((month) => {
        const row: CellValue[] = [month.name];
        district.negosyo_centers.forEach((center) => {
          row.push(fixed2(month.nc_data[center.id]));
        });
        row.push(fixed2(month.month_total));
        csvRows.push(row);
      });
    });

    csvRows.push([
      "ANNUAL TOTAL",
      ...Array(district.negosyo_centers.length).fill(""),
      fixed2(district.district_total),
    ]);
  });

  csvRows.push([""]);
  csvRows.push(["SUMMARY", "", "", ""]);
  csvRows.push(["District", "Annual Disbursement"]);

  data.districts.forEach((district) => {
    csvRows.push([district.name, fixed2(district.district_total)]);
  });

  const grandTotal = data.districts.reduce((total, district) => total + asNumber(district.district_total), 0);
  csvRows.push(["TOTAL", fixed2(grandTotal)]);

  createExcelReport(`Negosyo_Center_Report_${new Date().toISOString().split("T")[0]}`, [
    { name: "Negosyo Center Report", data: csvRows },
  ]);
}

function exportExpensesReportAll(): void {
  if (typeof EXPENSES_DATA === "undefined" || !EXPENSES_DATA) {
    console.error("Expenses data not available");
    return;
  }

  const expensesData = EXPENSES_DATA;
  const reportYear = typeof EXPENSES_YEAR !== "undefined" ? EXPENSES_YEAR : new Date().getFullYear();
  const groupLabel = typeof EXPENSES_GROUP_LABEL !== "undefined" ? EXPENSES_GROUP_LABEL : "Expense Category";

  const csvRows: SheetData = [];
  const data = expensesData.map((entry) => {
    const q1t = entry.q1.reduce((acc, value) => acc + value, 0);
    const q2t = entry.q2.reduce((acc, value) => acc + value, 0);
    const q3t = entry.q3.reduce((acc, value) => acc + value, 0);
    const q4t = entry.q4.reduce((acc, value) => acc + value, 0);
    return { ...entry, q1t, q2t, q3t, q4t, total: q1t + q2t + q3t + q4t };
  });

  const grandTotal = data.reduce((total, entry) => total + entry.total, 0);

  csvRows.push(["EXPENSES REPORT", "", "", "", "", "", "", ""]);
  csvRows.push([`Fiscal Year ${reportYear}`, "", "", "", "", "", "", ""]);
  csvRows.push([""]);
  csvRows.push([groupLabel, `${reportYear} Total`, "% of Total", "Q1", "Q2", "Q3", "Q4"]);

  data.forEach((entry) => {
    csvRows.push([
      entry.name,
      entry.total.toFixed(2),
      grandTotal > 0 ? ((entry.total / grandTotal) * 100).toFixed(1) : "0",
      entry.q1t.toFixed(2),
      entry.q2t.toFixed(2),
      entry.q3t.toFixed(2),
      entry.q4t.toFixed(2),
    ]);
  });

  csvRows.push([""]);
  csvRows.push(["TOTAL", grandTotal.toFixed(2), "100.0"]);

  createExcelReport(`Expenses_By_Category_Report_${new Date().toISOString().split("T")[0]}`, [
    { name: "Expenses Report", data: csvRows },
  ]);
}