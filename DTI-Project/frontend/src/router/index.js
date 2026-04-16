import { createRouter, createWebHistory } from 'vue-router'

import Layout from '@/layouts/Layout.vue'
import { hasAuthenticatedSession } from '@/services/authService'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { title: 'Login' },
  },
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: '',
        redirect: '/dashboard',
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/pages/DashboardPage.vue'),
        meta: { title: 'Dashboard' },
      },
      {
        path: 'executive-dashboard',
        name: 'executive-dashboard',
        component: () => import('@/pages/ExecutiveDashboardPage.vue'),
        meta: { title: 'Executive Dashboard' },
      },
      {
        path: 'bank-statements',
        name: 'bank-statements',
        component: () => import('@/pages/BankStatementPage.vue'),
        meta: { title: 'Bank Statements' },
      },
      {
        path: 'bank-statements/new',
        name: 'bank-statements-new',
        component: () => import('@/pages/BankStatementFormPage.vue'),
        meta: { title: 'New Bank Statement' },
      },
      {
        path: 'master-fund-monitoring',
        name: 'master-fund-monitoring',
        component: () => import('@/pages/MasterFundMonitoringPage.vue'),
        meta: { title: 'Master Fund Monitoring' },
      },
      {
        path: 'master-fund-monitoring/new',
        name: 'master-fund-monitoring-new',
        component: () => import('@/pages/MasterFundMonitoringFormPage.vue'),
        meta: { title: 'New Master Fund Monitoring Record' },
      },
      {
        path: 'master-fund-monitoring/:id/edit',
        name: 'master-fund-monitoring-edit',
        component: () => import('@/pages/MasterFundMonitoringFormPage.vue'),
        meta: { title: 'Edit Master Fund Monitoring Record' },
      },
      {
        path: 'suppliers',
        name: 'suppliers',
        component: () => import('@/pages/SupplierListPage.vue'),
        meta: { title: 'Supplier List' },
      },
      {
        path: 'staff',
        name: 'staff',
        component: () => import('@/pages/StaffListPage.vue'),
        meta: { title: 'Staff List' },
      },
      {
        path: 'expense-categories',
        name: 'expense-categories',
        component: () => import('@/pages/ExpenseCategoryListPage.vue'),
        meta: { title: 'Expense Category List' },
      },
      {
        path: 'expense-objects',
        name: 'expense-objects',
        component: () => import('@/pages/ExpenseObjectListPage.vue'),
        meta: { title: 'Expense Object List' },
      },
      {
        path: 'expense-objects/new',
        name: 'expense-objects-new',
        component: () => import('@/pages/ExpenseObjectFormPage.vue'),
        meta: { title: 'Add Expense Object' },
      },
      {
        path: 'expense-objects/:id/edit',
        name: 'expense-objects-edit',
        component: () => import('@/pages/ExpenseObjectFormPage.vue'),
        meta: { title: 'Edit Expense Object' },
      },
      {
        path: 'user-accounts',
        name: 'user-accounts',
        component: () => import('@/pages/UserAccountsListPage.vue'),
        meta: { title: 'User Accounts' },
      },
      {
        path: 'user-accounts/:id',
        name: 'user-accounts-detail',
        component: () => import('@/pages/UserAccountDetailPage.vue'),
        meta: { title: 'User Account Details' },
      },
      {
        path: 'user-accounts/new',
        name: 'user-accounts-new',
        component: () => import('@/pages/UserAccountFormPage.vue'),
        meta: { title: 'Create User Account' },
      },
      {
        path: 'user-accounts/:id/edit',
        name: 'user-accounts-edit',
        component: () => import('@/pages/UserAccountFormPage.vue'),
        meta: { title: 'Edit User Account' },
      },
      {
        path: 'expense-categories/new',
        name: 'expense-categories-new',
        component: () => import('@/pages/ExpenseCategoryFormPage.vue'),
        meta: { title: 'Add Expense Category' },
      },
      {
        path: 'expense-categories/:id/edit',
        name: 'expense-categories-edit',
        component: () => import('@/pages/ExpenseCategoryFormPage.vue'),
        meta: { title: 'Edit Expense Category' },
      },
      {
        path: 'staff/new',
        name: 'staff-new',
        component: () => import('@/pages/StaffFormPage.vue'),
        meta: { title: 'Add Staff' },
      },
      {
        path: 'staff/:id/edit',
        name: 'staff-edit',
        component: () => import('@/pages/StaffFormPage.vue'),
        meta: { title: 'Edit Staff' },
      },
      {
        path: 'tax-table',
        name: 'tax-table',
        component: () => import('@/pages/TaxTablePage.vue'),
        meta: { title: 'Tax Table' },
      },
      {
        path: 'tax-table/new',
        name: 'tax-table-new',
        component: () => import('@/pages/TaxFormPage.vue'),
        meta: { title: 'Add Tax Entry' },
      },
      {
        path: 'tax-table/:id/edit',
        name: 'tax-table-edit',
        component: () => import('@/pages/TaxFormPage.vue'),
        meta: { title: 'Edit Tax Entry' },
      },
      {
        path: 'fund-sources',
        name: 'fund-sources',
        component: () => import('@/pages/FundSourcesPage.vue'),
        meta: { title: 'Fund Sources' },
      },
      {
        path: 'fund-sources/:id',
        name: 'fund-sources-detail',
        component: () => import('@/pages/FundSourceDetailPage.vue'),
        meta: { title: 'Fund Source Breakdown' },
      },
      {
        path: 'fund-sources/:id/breakdowns/new',
        name: 'fund-sources-breakdowns-new',
        component: () => import('@/pages/FundSourceBreakdownFormPage.vue'),
        meta: { title: 'Add Breakdown' },
      },
      {
        path: 'fund-sources/:id/breakdowns/:breakdownId/edit',
        name: 'fund-sources-breakdowns-edit',
        component: () => import('@/pages/FundSourceBreakdownFormPage.vue'),
        meta: { title: 'Edit Breakdown' },
      },
      {
        path: 'fund-sources/new',
        name: 'fund-sources-new',
        component: () => import('@/pages/FundSourceFormPage.vue'),
        meta: { title: 'Add Fund Source' },
      },
      {
        path: 'fund-sources/:id/edit',
        name: 'fund-sources-edit',
        component: () => import('@/pages/FundSourceFormPage.vue'),
        meta: { title: 'Edit Fund Source' },
      },
      {
        path: 'report',
        name: 'expenses-report',
        component: () => import('@/pages/ExpensesReportPage.vue'),
        meta: { title: 'Expenses' },
      },
      {
        path: 'fund-report',
        name: 'fund-report',
        component: () => import('@/pages/FundReportPage.vue'),
        meta: { title: 'Fund Report' },
      },
      {
        path: 'mooe-report',
        name: 'mooe-report',
        component: () => import('@/pages/MooeReportPage.vue'),
        meta: { title: 'MOOE Report' },
      },
      {
        path: 'negosyo-center-report',
        name: 'negosyo-center-report',
        component: () => import('@/pages/NegosyoCenterReportPage.vue'),
        meta: { title: 'Negosyo Center Report' },
      },
      {
        path: 'suppliers/new',
        name: 'suppliers-new',
        component: () => import('@/pages/SupplierFormPage.vue'),
        meta: { title: 'New Supplier' },
      },
      {
        path: 'suppliers/:id/edit',
        name: 'suppliers-edit',
        component: () => import('@/pages/SupplierFormPage.vue'),
        meta: { title: 'Edit Supplier' },
      },
      {
        path: 'bank-statements/:id/edit',
        name: 'bank-statements-edit',
        component: () => import('@/pages/BankStatementFormPage.vue'),
        meta: { title: 'Edit Bank Statement' },
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/pages/SettingsPage.vue'),
        meta: { title: 'Settings' },
      },
      {
        path: 'change-password',
        name: 'change-password',
        component: () => import('@/pages/ChangePasswordPage.vue'),
        meta: { title: 'Change Password' },
      },
      {
        path: 'activity-logs',
        name: 'activity-logs',
        component: () => import('@/pages/ActivityLogsPage.vue'),
        meta: { title: 'Activity Logs' },
      },
      {
        path: 'activity-logs/summary',
        name: 'activity-summary',
        component: () => import('@/pages/ActivitySummaryPage.vue'),
        meta: { title: 'Activity Summary' },
      },
      {
        path: 'activity-logs/model/:modelName',
        name: 'model-activity-logs',
        component: () => import('@/pages/ModelActivityLogsPage.vue'),
        meta: { title: 'Model Activity Logs' },
      },
      {
        path: 'activity-logs/user/:userId',
        name: 'user-activity-logs',
        component: () => import('@/pages/UserActivityLogsPage.vue'),
        meta: { title: 'User Activity Logs' },
      },
      {
        path: 'archive',
        name: 'archive-dashboard',
        component: () => import('@/pages/ArchiveDashboardPage.vue'),
        meta: { title: 'Archive Management' },
      },
      {
        path: 'archive/statements',
        name: 'archived-statements',
        component: () => import('@/pages/ArchivedStatementsPage.vue'),
        meta: { title: 'Archived Statements' },
      },
      {
        path: 'archive/transactions',
        name: 'archived-transactions',
        component: () => import('@/pages/ArchivedTransactionsPage.vue'),
        meta: { title: 'Archived Transactions' },
      },
      {
        path: 'import',
        name: 'import-data',
        component: () => import('@/pages/ImportFormPage.vue'),
        meta: { title: 'Import Data' },
      },
      {
        path: 'import/result',
        name: 'import-result',
        component: () => import('@/pages/ImportResultPage.vue'),
        meta: { title: 'Import Results' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { left: 0, top: 0 }
  },
})

router.beforeEach((to) => {
  if (to.name === 'login') {
    return true
  }

  if (!hasAuthenticatedSession()) {
    return {
      name: 'login',
      query: { redirect: to.fullPath },
    }
  }

  return true
})

export default router
