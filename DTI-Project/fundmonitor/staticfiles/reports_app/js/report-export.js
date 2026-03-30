"use strict";
function fromWindow(key) {
    return window[key];
}
function asNumber(value) {
    if (typeof value === "number") {
        return Number.isFinite(value) ? value : 0;
    }
    if (typeof value === "string") {
        const parsed = parseFloat(value);
        return Number.isFinite(parsed) ? parsed : 0;
    }
    return 0;
}
function fixed2(value) {
    return asNumber(value).toFixed(2);
}
function safeSheetName(name, fallbackIndex) {
    const cleaned = name.replace(/[\\/:*?\[\]]/g, "").slice(0, 31);
    return cleaned || `Sheet${fallbackIndex}`;
}
function createExcelReport(filename, sheets) {
    const xlsx = fromWindow("XLSX");
    if (!sheets || sheets.length === 0) {
        alert("No data to export");
        return;
    }
    try {
        if (!xlsx || !xlsx.utils) {
            alert("Excel library is not loaded.");
            return;
        }
        const workbook = xlsx.utils.book_new();
        const buildColWidths = (data) => {
            const colCount = Math.max(...data.map((row) => (row ? row.length : 0)), 1);
            return Array.from({ length: colCount }, (_, colIndex) => {
                const maxLen = Math.max(...data.map((row) => { var _a; return String((_a = row === null || row === void 0 ? void 0 : row[colIndex]) !== null && _a !== void 0 ? _a : "").length; }), 8);
                return { wch: Math.min(maxLen + 2, 60) };
            });
        };
        sheets.forEach((sheet, index) => {
            var _a;
            const data = (sheet === null || sheet === void 0 ? void 0 : sheet.data) || [];
            if (!data.length) {
                return;
            }
            const worksheet = xlsx.utils.aoa_to_sheet(data);
            worksheet["!cols"] = buildColWidths(data);
            const headerLength = ((_a = data[0]) === null || _a === void 0 ? void 0 : _a.length) || 0;
            for (let col = 0; col < headerLength; col += 1) {
                const cellAddr = xlsx.utils.encode_cell({ r: 0, c: col });
                if (worksheet[cellAddr]) {
                    worksheet[cellAddr].s = {
                        font: { bold: true, color: { rgb: "FFFFFF" } },
                        fill: { fgColor: { rgb: "4472C4" } },
                        alignment: { horizontal: "center", vertical: "center" },
                    };
                }
            }
            xlsx.utils.book_append_sheet(workbook, worksheet, safeSheetName(sheet.name || `Sheet${index + 1}`, index + 1));
        });
        const workbookLike = workbook;
        if (!workbookLike.SheetNames || workbookLike.SheetNames.length === 0) {
            alert("No rows to export");
            return;
        }
        xlsx.writeFile(workbook, `${filename}.xlsx`);
    }
    catch (error) {
        console.error("Export error:", error);
        alert("Export failed. Please try again.");
    }
}
function exportFundReportAll() {
    const data = fromWindow("FUND_REPORT_DATA");
    if (!data) {
        console.error("Fund report data not available");
        return;
    }
    const csvRows = [];
    csvRows.push(["FUND REPORT - COMBINED DATA", "", "", "", ""]);
    csvRows.push(["Fiscal Year 2025", "", "", "", ""]);
    csvRows.push([""]);
    csvRows.push(["DISBURSEMENT BREAKDOWN", "", "", "", ""]);
    const fundNames = data.funds.map((fund) => fund.name);
    csvRows.push(["Month", ...fundNames, "Total"]);
    data.disbursementBreakdown.forEach((monthData) => {
        const row = [monthData.month];
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
        const row = [monthData.month];
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
        if (!budget) {
            return;
        }
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
function exportMooeReportAll() {
    const data = fromWindow("MOOE_REPORT_DATA");
    if (!data) {
        console.error("MOOE report data not available");
        return;
    }
    const csvRows = [];
    csvRows.push(["MOOE REPORT - COMBINED DATA", "", "", "", ""]);
    csvRows.push(["Fiscal Year 2025", "Maintenance and Other Operating Expenses", "", "", ""]);
    csvRows.push([""]);
    csvRows.push(["DISBURSEMENT BREAKDOWN", "", "", "", ""]);
    csvRows.push(["Month", ...data.categoryCodes, "Total"]);
    data.disbursementBreakdown.forEach((monthData) => {
        const row = [monthData.month];
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
        const row = [monthData.month];
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
function exportNcReportAll() {
    const data = fromWindow("NC_REPORT_DATA");
    if (!data) {
        console.error("Negosyo Center report data not available");
        return;
    }
    const csvRows = [];
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
                const row = [month.name];
                district.negosyo_centers.forEach((center) => {
                    row.push(fixed2(month.nc_data[center.id]));
                });
                row.push(fixed2(month.month_total));
                csvRows.push(row);
            });
        });
        csvRows.push([
            "ANNUAL TOTAL",
            "",
            "",
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
function exportExpensesReportAll() {
    var _a, _b;
    const expensesData = fromWindow("EXPENSES_DATA");
    if (!expensesData) {
        console.error("Expenses data not available");
        return;
    }
    const reportYear = (_a = fromWindow("EXPENSES_YEAR")) !== null && _a !== void 0 ? _a : new Date().getFullYear();
    const groupLabel = (_b = fromWindow("EXPENSES_GROUP_LABEL")) !== null && _b !== void 0 ? _b : "Expense Category";
    const csvRows = [];
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
window.createExcelReport = createExcelReport;
window.exportFundReportAll = exportFundReportAll;
window.exportMooeReportAll = exportMooeReportAll;
window.exportNcReportAll = exportNcReportAll;
window.exportExpensesReportAll = exportExpensesReportAll;
//# sourceMappingURL=report-export.js.map