// globals.d.ts
declare const XLSX: XlsxGlobal | undefined;
declare const FUND_REPORT_DATA: FundReportData | undefined;
declare const MOOE_REPORT_DATA: MooeReportData | undefined;
declare const NC_REPORT_DATA: NcReportData | undefined;
declare const EXPENSES_DATA: ExpenseEntry[] | undefined;    
declare const EXPENSES_YEAR: number | undefined;
declare const EXPENSES_GROUP_LABEL: string | undefined;
declare function exportFundReportAll(): void;
declare function exportMooeReportAll(): void;
declare function exportNcReportAll(): void;
declare function exportExpensesReportAll(): void;