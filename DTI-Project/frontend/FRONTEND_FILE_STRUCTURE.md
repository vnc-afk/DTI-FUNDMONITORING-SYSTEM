# Frontend File Structure

Generated on: 2026-04-16 11:09:40

Excluded directories: node_modules, dist, .git, .vite

```text
DTI-Project/frontend
|-- .vscode
|   `-- extensions.json
|-- public
|-- src
|   |-- assets
|   |   |-- css
|   |   |   |-- components
|   |   |   |   `-- components.css
|   |   |   |-- foundations
|   |   |   |   `-- base.css
|   |   |   |-- patterns
|   |   |   |   |-- archive.css
|   |   |   |   |-- archive-list.css
|   |   |   |   |-- auth.css
|   |   |   |   |-- executive-dashboard.css
|   |   |   |   |-- form-pages.css
|   |   |   |   |-- layouts.css
|   |   |   |   |-- list-pages.css
|   |   |   |   |-- password-change.css
|   |   |   |   |-- reports.css
|   |   |   |   |-- settings.css
|   |   |   |   `-- sidebar.css
|   |   |   |-- tokens
|   |   |   |   |-- colors.css
|   |   |   |   |-- spacing.css
|   |   |   |   `-- typography.css
|   |   |   |-- utils
|   |   |   |   `-- utils.css
|   |   |   `-- index.css
|   |   `-- images
|   |       `-- DTI_Logo_2019.png
|   |-- components
|   |   |-- patterns
|   |   |   |-- BaseFormSection.vue
|   |   |   |-- DashboardPageLayout.vue
|   |   |   |-- DataTablePage.vue
|   |   |   |-- FormPage.vue
|   |   |   `-- ReportPageLayout.vue
|   |   `-- ui
|   |       |-- ActionButton.vue
|   |       |-- DeleteConfirmModal.vue
|   |       |-- EmptyState.vue
|   |       |-- FilterChips.vue
|   |       |-- LoadingState.vue
|   |       |-- SearchInput.vue
|   |       |-- UiAccordion.vue
|   |       |-- UiBadge.vue
|   |       |-- UiButton.vue
|   |       |-- UiCard.vue
|   |       |-- UiCheckbox.vue
|   |       |-- UiCurrencyInput.vue
|   |       |-- UiDrawer.vue
|   |       |-- UiIcon.vue
|   |       |-- UiInput.vue
|   |       |-- UiModal.vue
|   |       |-- UiNoResults.vue
|   |       |-- UiPageHeader.vue
|   |       |-- UiSelect.vue
|   |       |-- UiSidebar.vue
|   |       |-- UiSummaryCards.vue
|   |       |-- UiTable.vue
|   |       |-- UiTableFooter.vue
|   |       |-- UiTextarea.vue
|   |       |-- UiToast.vue
|   |       |-- UiToolbar.vue
|   |       `-- UiTopbar.vue
|   |-- layouts
|   |   `-- Layout.vue
|   |-- pages
|   |   |-- ActivityLogsPage.vue
|   |   |-- ActivitySummaryPage.vue
|   |   |-- ArchiveDashboardPage.vue
|   |   |-- ArchivedStatementsPage.vue
|   |   |-- ArchivedTransactionsPage.vue
|   |   |-- BankStatementFormPage.vue
|   |   |-- BankStatementPage.vue
|   |   |-- ChangePasswordPage.vue
|   |   |-- DashboardPage.vue
|   |   |-- ExecutiveDashboardPage.vue
|   |   |-- ExpenseCategoryFormPage.vue
|   |   |-- ExpenseCategoryListPage.vue
|   |   |-- ExpenseObjectFormPage.vue
|   |   |-- ExpenseObjectListPage.vue
|   |   |-- ExpensesReportPage.vue
|   |   |-- FundReportPage.vue
|   |   |-- FundSourceBreakdownFormPage.vue
|   |   |-- FundSourceDetailPage.vue
|   |   |-- FundSourceFormPage.vue
|   |   |-- FundSourcesPage.vue
|   |   |-- ImportFormPage.vue
|   |   |-- ImportResultPage.vue
|   |   |-- LoginPage.vue
|   |   |-- MasterFundMonitoringFormPage.vue
|   |   |-- MasterFundMonitoringPage.vue
|   |   |-- ModelActivityLogsPage.vue
|   |   |-- MooeReportPage.vue
|   |   |-- NegosyoCenterReportPage.vue
|   |   |-- SettingsPage.vue
|   |   |-- StaffFormPage.vue
|   |   |-- StaffListPage.vue
|   |   |-- SupplierFormPage.vue
|   |   |-- SupplierListPage.vue
|   |   |-- TaxFormPage.vue
|   |   |-- TaxTablePage.vue
|   |   |-- UserAccountDetailPage.vue
|   |   |-- UserAccountFormPage.vue
|   |   |-- UserAccountsListPage.vue
|   |   `-- UserActivityLogsPage.vue
|   |-- router
|   |   `-- index.js
|   |-- services
|   |   |-- activityLogsService.js
|   |   |-- apiFeedbackService.js
|   |   |-- archiveService.js
|   |   |-- authAxiosBootstrap.js
|   |   |-- authService.js
|   |   |-- bankStatementFormService.js
|   |   |-- bankStatementService.js
|   |   |-- dashboardService.js
|   |   |-- executiveDashboardService.js
|   |   |-- expenseCategoryService.js
|   |   |-- expenseObjectService.js
|   |   |-- expensesReportService.js
|   |   |-- fundReportService.js
|   |   |-- fundSourceService.js
|   |   |-- importService.js
|   |   |-- masterFundMonitoringFormService.js
|   |   |-- masterFundMonitoringService.js
|   |   |-- mooeReportService.js
|   |   |-- negosyoCenterReportService.js
|   |   |-- realtimeService.js
|   |   |-- settingsService.js
|   |   |-- sidebarService.js
|   |   |-- staffService.js
|   |   |-- supplierFormService.js
|   |   |-- supplierService.js
|   |   |-- taxTableService.js
|   |   |-- topbarService.js
|   |   `-- userAccountsService.js
|   |-- stores
|   |   |-- authStore.js
|   |   |-- index.js
|   |   |-- notificationsStore.js
|   |   `-- sharedStore.js
|   |-- utils
|   |   |-- archiveRefresh.js
|   |   `-- excelExport.js
|   |-- App.vue
|   `-- main.js
|-- .gitignore
|-- FRONTEND_FILE_STRUCTURE.md
|-- index.html
|-- package.json
|-- package-lock.json
`-- vite.config.js
```
