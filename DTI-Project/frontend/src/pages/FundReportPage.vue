<template>
  <ReportPageLayout root-class="report" :title="'Fund Report'" :description="`Fiscal Year ${currentYear} · All figures in PHP`">
    <template #header-actions>
      <button id="btn-print" class="btn btn-outline" type="button" @click="printPage" title="Print this report">
        <ui-icon name="printer" size="18" /> Print
      </button>
      <button id="btn-export" class="btn btn-primary" type="button" @click="exportAll" title="Export data to Excel">
        <ui-icon name="download" size="18" /> Export All
      </button>
    </template>

      <div class="section-title">Budget Summary</div>
      <div class="summary-cards">
        <div class="scard report-row-budget">
          <div class="scard-label">Annual Budget</div>
          <div class="scard-amount">{{ formatCurrency(grandTotalBudget) }}</div>
          <div class="scard-pct">All Funds</div>
        </div>
        <div class="scard report-row-disburse">
          <div class="scard-label">Total Downloads</div>
          <div class="scard-amount">{{ formatCurrency(grandTotalDownloads) }}</div>
        </div>
        <div class="scard report-row-disburse">
          <div class="scard-label">Total Disbursement</div>
          <div class="scard-amount">{{ formatCurrency(grandTotalDisbursed) }}</div>
        </div>
        <div class="scard report-row-balance">
          <div class="scard-label">Annual Balance</div>
          <div class="scard-amount">{{ formatCurrency(grandTotalBalance) }}</div>
          <div class="scard-pct">Remaining Budget</div>
        </div>
        <div class="scard report-row-bur">
          <div class="scard-label">BUR (Annual)</div>
          <div class="scard-amount">{{ grandTotalBur.toFixed(2) }}%</div>
          <div class="scard-pct">Current Period</div>
        </div>
      </div>
      <div class="section-title">Detailed Breakdown</div>
      <div class="filter-bar">
        <button
          type="button"
          class="filter-btn"
          :class="{ active: activeTab === 'disbursement' }"
          data-tab="disbursement"
          @click="activeTab = 'disbursement'"
          title="View disbursement data"
        >
          <ui-icon name="banknote-arrow-up" size="18" /> Disbursement
        </button>
        <button
          type="button"
          class="filter-btn"
          :class="{ active: activeTab === 'downloads' }"
          data-tab="downloads"
          @click="activeTab = 'downloads'"
          title="View download data"
        >
          <ui-icon name="banknote-arrow-down" size="18" /> Downloads
        </button>
        <div class="flex-1"></div>
        <button id="open-all-btn" type="button" class="filter-btn" @click="openAllAccordions" title="Expand all quarters">
          <ui-icon name="maximize-2" size="18" /> Open All
        </button>
        <button id="close-all-btn" type="button" class="filter-btn" @click="closeAllAccordions" title="Collapse all quarters">
          <ui-icon name="minimize-2" size="18" /> Close All
        </button>
      </div>

    <div id="tab-disbursement" class="tab-panel" :style="{ display: activeTab === 'disbursement' ? 'block' : 'none' }">
      <div class="accordion quarterly-acc" data-breakdown="disbursement">
        <div
          v-for="quarter in disbursementQuarterRows"
          :key="`disbursement-${quarter.label}`"
          class="acc-item"
          :class="{ open: openDisbursement[quarter.label] }"
        >
          <div class="acc-header" @click="toggleQuarter('disbursement', quarter.label)">
            <div class="acc-header-left">
              <ui-icon name="chevron-down" class="acc-chevron" />
              <span class="q-badge" :class="`q${quarter.index}`">{{ quarter.label }}</span>
              <span class="q-range">{{ quarter.range }}</span>
            </div>
            <div class="acc-header-right">
              <span class="q-grand-total" :data-quarter="quarter.index">{{ formatCurrency(quarter.grandTotal) }}</span>
            </div>
          </div>
          <div class="acc-body">
            <div class="table-wrap table-wrap-flat">
              <table class="quarterly-table">
                <thead>
                  <tr>
                    <th>Month</th>
                    <th
                      v-for="fund in funds"
                      :key="`disbursement-head-${quarter.label}-${fund.id}`"
                    >
                      {{ fund.name }}
                    </th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="month in quarter.months" :key="`disbursement-${quarter.label}-${month.month}`" class="month-row">
                    <td class="month-cell">
                      <span class="row-dot"></span>
                      <span class="month-label">{{ month.month }}</span>
                    </td>
                    <td
                      v-for="fund in funds"
                      :key="`disbursement-cell-${quarter.label}-${month.month}-${fund.id}`"
                      class="fund-cell"
                      :data-fund="fund.id"
                      :data-value="toNumber(month.data?.[fund.id])"
                    >
                      {{ formatCurrency(month.data?.[fund.id]) }}
                    </td>
                    <td class="total-cell col-total">{{ formatCurrency(month.total) }}</td>
                  </tr>
                  <tr class="quarter-subtotal-row" :class="`q${quarter.index}`">
                    <td class="month-cell">Quarter Subtotal</td>
                    <td
                      v-for="fund in funds"
                      :key="`disbursement-subtotal-${quarter.label}-${fund.id}`"
                      class="fund-cell"
                    >
                      {{ formatCurrency(quarter.fundTotals[fund.id]) }}
                    </td>
                    <td class="total-cell col-total">{{ formatCurrency(quarter.grandTotal) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      <div class="tab-download-bar">
        <span><ui-icon name="info" size="16" class="me-1" />Quarterly disbursement breakdown by month</span>
        <div class="tab-download-actions">
          <a href="/api/reports-app/fund/download/disbursement/" class="btn btn-outline">
            <ui-icon name="file-spreadsheet" /> Excel
          </a>
          <button type="button" class="btn btn-outline" @click="printPage">
            <ui-icon name="file-pdf" /> PDF
          </button>
        </div>
      </div>
    </div>

    <div id="tab-downloads" class="tab-panel" :style="{ display: activeTab === 'downloads' ? 'block' : 'none' }">
      <div class="accordion quarterly-acc" data-breakdown="downloads">
        <div
          v-for="quarter in downloadsQuarterRows"
          :key="`downloads-${quarter.label}`"
          class="acc-item"
          :class="{ open: openDownloads[quarter.label] }"
        >
          <div class="acc-header" @click="toggleQuarter('downloads', quarter.label)">
            <div class="acc-header-left">
              <ui-icon name="chevron-down" class="acc-chevron" />
              <span class="q-badge" :class="`q${quarter.index}`">{{ quarter.label }}</span>
              <span class="q-range">{{ quarter.range }}</span>
            </div>
            <div class="acc-header-right">
              <span class="q-grand-total" :data-quarter="quarter.index">{{ formatCurrency(quarter.grandTotal) }}</span>
            </div>
          </div>
          <div class="acc-body">
            <div class="table-wrap table-wrap-flat">
              <table class="quarterly-table">
                <thead>
                  <tr>
                    <th>Month</th>
                    <th
                      v-for="fund in funds"
                      :key="`downloads-head-${quarter.label}-${fund.id}`"
                    >
                      {{ fund.name }}
                    </th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="month in quarter.months" :key="`downloads-${quarter.label}-${month.month}`" class="month-row">
                    <td class="month-cell">
                      <span class="row-dot"></span>
                      <span class="month-label">{{ month.month }}</span>
                    </td>
                    <td
                      v-for="fund in funds"
                      :key="`downloads-cell-${quarter.label}-${month.month}-${fund.id}`"
                      class="fund-cell"
                      :data-fund="fund.id"
                      :data-value="toNumber(month.data?.[fund.id])"
                    >
                      {{ formatCurrency(month.data?.[fund.id]) }}
                    </td>
                    <td class="total-cell col-total">{{ formatCurrency(month.total) }}</td>
                  </tr>
                  <tr class="quarter-subtotal-row" :class="`q${quarter.index}`">
                    <td class="month-cell">Quarter Subtotal</td>
                    <td
                      v-for="fund in funds"
                      :key="`downloads-subtotal-${quarter.label}-${fund.id}`"
                      class="fund-cell"
                    >
                      {{ formatCurrency(quarter.fundTotals[fund.id]) }}
                    </td>
                    <td class="total-cell col-total">{{ formatCurrency(quarter.grandTotal) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      <div class="tab-download-bar">
        <span><ui-icon name="info" size="16" class="me-1" />Quarterly download breakdown by month</span>
        <div class="tab-download-actions">
          <a href="/api/reports-app/fund/download/downloads/" class="btn btn-outline">
            <ui-icon name="file-spreadsheet" /> Excel
          </a>
          <button type="button" class="btn btn-outline" @click="printPage">
            <ui-icon name="file-pdf" /> PDF
          </button>
        </div>
      </div>
    </div>

      <div v-if="loadError" class="report-feedback-error">
        {{ loadError }}
      </div>
  </ReportPageLayout>
</template>

<script setup>
import ExcelJS from 'exceljs'
import { computed, onMounted, reactive, ref } from 'vue'
import ReportPageLayout from '@/components/patterns/ReportPageLayout.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import { downloadWorkbook } from '@/utils/excelExport'
import { fetchFundReport } from '@/services/fundReportService'

const FUND_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const FUND_QUARTERS = [
  { label: 'Q1', range: 'January - March', months: [1, 2, 3], index: 1 },
  { label: 'Q2', range: 'April - June', months: [4, 5, 6], index: 2 },
  { label: 'Q3', range: 'July - September', months: [7, 8, 9], index: 3 },
  { label: 'Q4', range: 'October - December', months: [10, 11, 12], index: 4 },
]

const loadError = ref('')
const currentYear = ref(new Date().getFullYear())
const activeTab = ref('disbursement')

const funds = ref([])
const budgetData = ref({})
const disbursementBreakdown = ref([])
const downloadsBreakdown = ref([])

const grandTotalBudget = ref(0)
const grandTotalDisbursed = ref(0)
const grandTotalDownloads = ref(0)
const grandTotalBalance = ref(0)
const grandTotalBur = ref(0)

const openDisbursement = reactive({ Q1: true, Q2: true, Q3: true, Q4: true })
const openDownloads = reactive({ Q1: true, Q2: true, Q3: true, Q4: true })

function toNumber(value) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

function formatCurrency(value) {
  const amount = toNumber(value)
  return amount > 0
    ? `₱ ${amount.toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    : '-'
}

function quarterRowsFromBreakdown(breakdown) {
  return FUND_QUARTERS.map((quarter) => {
    const fundTotals = {}
    funds.value.forEach((fund) => {
      fundTotals[fund.id] = 0
    })

    const months = quarter.months.map((monthNumber) => {
      const monthData = breakdown[monthNumber - 1] || {}
      funds.value.forEach((fund) => {
        fundTotals[fund.id] += toNumber(monthData?.data?.[fund.id])
      })

      return {
        month: FUND_MONTHS[monthNumber - 1] || '',
        data: monthData?.data || {},
        total: toNumber(monthData?.total),
      }
    })

    const grandTotal = months.reduce((sum, month) => sum + toNumber(month.total), 0)

    return {
      ...quarter,
      months,
      fundTotals,
      grandTotal,
    }
  })
}

const disbursementQuarterRows = computed(() => quarterRowsFromBreakdown(disbursementBreakdown.value))
const downloadsQuarterRows = computed(() => quarterRowsFromBreakdown(downloadsBreakdown.value))

function toggleQuarter(type, label) {
  if (type === 'downloads') {
    openDownloads[label] = !openDownloads[label]
  } else {
    openDisbursement[label] = !openDisbursement[label]
  }
}

function openAllAccordions() {
  Object.keys(openDisbursement).forEach((label) => {
    openDisbursement[label] = true
    openDownloads[label] = true
  })
}

function closeAllAccordions() {
  Object.keys(openDisbursement).forEach((label) => {
    openDisbursement[label] = false
    openDownloads[label] = false
  })
}

function printPage() {
  window.print()
}

async function exportAll() {
  if (!funds.value.length) {
    return
  }

  const disbursementRows = [['DISBURSEMENT BREAKDOWN'], ['Month', ...funds.value.map((fund) => fund.name), 'Total']]
  disbursementBreakdown.value.forEach((monthRow, index) => {
    const monthName = FUND_MONTHS[index] || ''
    const row = [monthName]
    funds.value.forEach((fund) => {
      row.push(toNumber(monthRow?.data?.[fund.id]).toFixed(2))
    })
    row.push(toNumber(monthRow?.total).toFixed(2))
    disbursementRows.push(row)
  })

  const downloadsRows = [['DOWNLOADS BREAKDOWN'], ['Month', ...funds.value.map((fund) => fund.name), 'Total']]
  downloadsBreakdown.value.forEach((monthRow, index) => {
    const monthName = FUND_MONTHS[index] || ''
    const row = [monthName]
    funds.value.forEach((fund) => {
      row.push(toNumber(monthRow?.data?.[fund.id]).toFixed(2))
    })
    row.push(toNumber(monthRow?.total).toFixed(2))
    downloadsRows.push(row)
  })

  const summaryRows = [['SUMMARY'], ['Fund', 'Annual Budget', 'Total Disbursed', 'Total Downloads', 'Balance', 'BUR %']]
  funds.value.forEach((fund) => {
    const summary = budgetData.value?.[fund.id] || {}
    summaryRows.push([
      fund.name,
      toNumber(summary.annual_budget).toFixed(2),
      toNumber(summary.total_disbursed).toFixed(2),
      toNumber(summary.total_downloads).toFixed(2),
      toNumber(summary.current_balance).toFixed(2),
      toNumber(summary.bur_percent).toFixed(2),
    ])
  })

  const workbook = new ExcelJS.Workbook()

  const disbursementSheet = workbook.addWorksheet('Disbursement')
  disbursementSheet.addRows(disbursementRows)

  const downloadsSheet = workbook.addWorksheet('Downloads')
  downloadsSheet.addRows(downloadsRows)

  const summarySheet = workbook.addWorksheet('Summary')
  summarySheet.addRows(summaryRows)

  await downloadWorkbook(workbook, `Fund_Report_${new Date().toISOString().split('T')[0]}.xlsx`)
}

async function loadReport() {
  loadError.value = ''

  try {
    const data = await fetchFundReport()
    currentYear.value = toNumber(data?.current_year) || new Date().getFullYear()
    funds.value = Array.isArray(data?.funds) ? data.funds : []
    budgetData.value = data?.budgetData || {}
    disbursementBreakdown.value = Array.isArray(data?.disbursementBreakdown) ? data.disbursementBreakdown : []
    downloadsBreakdown.value = Array.isArray(data?.downloadsBreakdown) ? data.downloadsBreakdown : []

    grandTotalBudget.value = toNumber(data?.grandTotalBudget)
    grandTotalDisbursed.value = toNumber(data?.grandTotalDisbursed)
    grandTotalDownloads.value = toNumber(data?.grandTotalDownloads)
    grandTotalBalance.value = toNumber(data?.grandTotalBalance)
    grandTotalBur.value = toNumber(data?.grandTotalBur)
  } catch (error) {
    loadError.value = 'Unable to load fund report data. Please try again.'
  }
}

onMounted(() => {
  loadReport()
})
</script>
