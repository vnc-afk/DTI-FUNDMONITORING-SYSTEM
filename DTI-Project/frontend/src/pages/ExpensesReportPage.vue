<template>
  <ReportPageLayout root-class="report" :title="groupLabel" :description="`Fiscal Year ${currentYear} · All figures in PHP`">
    <template #header-actions>
      <button class="btn btn-primary" type="button" @click="exportAll">
        <ui-icon name="download" size="18"/> Export All
      </button>
    </template>

    <!-- Section: Summary Overview -->
    <div class="report-year-total" aria-live="polite">
      <span class="report-year-total-label">Total Expenses ({{ currentYear }})</span>
      <strong class="report-year-total-value">{{ yearTotalDisplay }}</strong>
    </div>
    <div class="section-title">Summary Overview</div>

    <div class="summary-cards">
      <div
        v-for="(item, index) in summaryCards"
        :key="item.name"
        class="scard"
        :data-card-index="index"
        :style="{ '--card-color': item.color, '--card-percent': `${item.percent}%` }"
      >
        <div class="scard-label">{{ item.name }}</div>
        <div class="scard-amount">{{ formatMoney(item.total) }}</div>
        <div class="scard-pct">{{ item.percent.toFixed(1) }}% of total</div>
        <div class="scard-bar">
          <div class="scard-bar-fill"></div>
        </div>
      </div>
    </div>

    <!-- Section: Expense Table with Filters -->
    <div class="section-title">All Expenses</div>
    <div class="filter-bar">
      <label class="filter-label" :for="groupBySelectId">Group by:</label>
      <form class="grouping-form" @submit.prevent>
        <select
          :id="groupBySelectId"
          v-model="groupBy"
          class="group-by-select"
          name="group_by"
          @change="handleGroupByChange"
        >
          <option value="classification">Expense Category</option>
          <option value="object">Object of Expense</option>
        </select>
      </form>

      <span class="filter-label">Quarter:</span>
      <button
        v-for="option in quarterOptions"
        :key="option"
        type="button"
        class="filter-btn"
        :class="{ active: currentFilter === option }"
        @click="currentFilter = option"
      >
        {{ option }}
      </button>

      <label :for="searchInputId" class="sr-only">Search expenses</label>
      <input
        :id="searchInputId"
        name="search"
        v-model="search"
        class="search-box"
        type="text"
        :placeholder="searchPlaceholder"
      >
    </div>

    <!-- Table: Expense Summary -->
    <div class="table-wrap">
      <table class="quarterly-table">
        <thead>
          <tr>
            <th :class="{ sorted: currentSort.col === 'name' }" @click="setSort('name')">
              {{ groupLabel }}<span class="sort-arrow">↕</span>
            </th>
            <th :class="{ sorted: currentSort.col === 'total' }" @click="setSort('total')">
              {{ currentYear }} Total <span class="sort-arrow">↕</span>
            </th>
            <th :class="{ sorted: currentSort.col === 'pct' }" @click="setSort('pct')">
              % <span class="sort-arrow">↕</span>
            </th>
            <th>Q1</th>
            <th>Q2</th>
            <th>Q3</th>
            <th>Q4</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="entry in visibleRows" :key="entry.name">
            <td><span class="cat-dot" :style="{ '--entry-color': entry.color }"></span>{{ entry.name }}</td>
            <td class="amount" :class="entry.total > 0 ? 'pos' : 'empty'">{{ formatMoney(entry.total) }}</td>
            <td>
              <span class="pct-badge">{{ entry.total > 0 ? `${entry.percent.toFixed(2)}%` : '-' }}</span>
            </td>
            <td class="q-cell" :class="entry.q1t > 0 ? 'active' : 'inactive'">{{ formatMoney(entry.q1t) }}</td>
            <td class="q-cell" :class="entry.q2t > 0 ? 'active' : 'inactive'">{{ formatMoney(entry.q2t) }}</td>
            <td class="q-cell" :class="entry.q3t > 0 ? 'active' : 'inactive'">{{ formatMoney(entry.q3t) }}</td>
            <td class="q-cell" :class="entry.q4t > 0 ? 'active' : 'inactive'">{{ formatMoney(entry.q4t) }}</td>
          </tr>
        </tbody>

        <tfoot>
          <tr>
            <td>Subtotal ({{ visibleRows.length }} shown)</td>
            <td>{{ formatMoney(subtotals.total) }}</td>
            <td></td>
            <td>{{ formatMoney(subtotals.q1) }}</td>
            <td>{{ formatMoney(subtotals.q2) }}</td>
            <td>{{ formatMoney(subtotals.q3) }}</td>
            <td>{{ formatMoney(subtotals.q4) }}</td>
          </tr>
        </tfoot>
      </table>

      <div v-if="!visibleRows.length" class="no-results-container">
        <UiNoResults 
          :title="`No ${groupLabel} Found`" 
          :description="`Try adjusting your search or filter criteria`"
        />
      </div>
    </div>

    <!-- Section: Monthly Breakdown -->
    <div class="section-title">Monthly Breakdown</div>
    <UiAccordion :items="accordionItems">
      <template #body="{ item: quarter }">
        <div class="table-wrap table-wrap-flat">
          <table class="quarterly-table">
            <thead>
              <tr>
                <th>{{ groupLabel }}</th>
                <th v-for="month in quarter.months" :key="`${quarter.label}-head-${month.name}`">
                  {{ month.name }}
                </th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in quarter.entries" :key="`${quarter.label}-${entry.name}`">
                <td class="month-cell">
                  <span class="cat-dot" :style="{ '--entry-color': entry.color }"></span>
                  {{ entry.name }}
                </td>
                <td v-for="month in quarter.months" :key="`${quarter.label}-${entry.name}-${month.name}`" class="fund-cell">
                  {{ formatMoney(month.entries.find(e => e.name === entry.name)?.value || 0) }}
                </td>
                <td class="total-cell">
                  {{ formatMoney(entry.total) }}
                </td>
              </tr>
              <tr class="quarter-subtotal-row">
                <td class="month-cell">Quarter Subtotal</td>
                <td v-for="month in quarter.months" :key="`${quarter.label}-subtotal-${month.name}`" class="fund-cell">
                  {{ formatMoney(month.total) }}
                </td>
                <td class="total-cell">
                  {{ formatMoney(quarter.total) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </UiAccordion>

    <!-- Error Feedback -->
    <div v-if="loadError" class="report-feedback-error">
      {{ loadError }}
    </div>
  </ReportPageLayout>
</template>

<script setup>
import ExcelJS from 'exceljs'
import { computed, onMounted, reactive, ref } from 'vue'
import ReportPageLayout from '@/components/patterns/ReportPageLayout.vue'
import UiAccordion from '@/components/ui/UiAccordion.vue'
import UiNoResults from '@/components/ui/UiNoResults.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import { downloadWorkbook } from '@/utils/excelExport'
import { fetchExpensesReport } from '@/services/expensesReportService'

const quarterOptions = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const quarterRanges = ['Jan - Mar', 'Apr - Jun', 'Jul - Sep', 'Oct - Dec']

const loading = ref(false)
const loadError = ref('')
const groupBy = ref('classification')
const currentFilter = ref('All')
const search = ref('')

const currentYear = ref(new Date().getFullYear())
const groupLabel = ref('Expense Category')
const searchPlaceholder = ref('Search expense category...')
const groupBySelectId = 'expenses-report-group-by'
const searchInputId = 'expenses-report-search'

const rows = ref([])

const currentSort = reactive({
  col: 'total',
  dir: -1,
})

function toNumber(value) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

function sum(values) {
  return (values || []).reduce((acc, value) => acc + toNumber(value), 0)
}

function formatMoney(value) {
  const amount = toNumber(value)
  if (amount <= 0) {
    return '-'
  }
  return `₱ ${amount.toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const enrichedRows = computed(() => {
  return (rows.value || []).map((item) => {
    const q1t = sum(item.q1)
    const q2t = sum(item.q2)
    const q3t = sum(item.q3)
    const q4t = sum(item.q4)
    const total = q1t + q2t + q3t + q4t
    return {
      ...item,
      q1t,
      q2t,
      q3t,
      q4t,
      total,
    }
  })
})

const grandTotal = computed(() => enrichedRows.value.reduce((acc, item) => acc + item.total, 0))
const yearTotalDisplay = computed(() => (grandTotal.value > 0
  ? formatMoney(grandTotal.value)
  : '₱ 0.00'))

const tableRows = computed(() => {
  return enrichedRows.value.map((item) => ({
    ...item,
    percent: grandTotal.value > 0 ? (item.total / grandTotal.value) * 100 : 0,
  }))
})

const summaryCards = computed(() => tableRows.value.filter((item) => item.total > 0))

const visibleRows = computed(() => {
  const searchValue = (search.value || '').toLowerCase()

  const filtered = tableRows.value.filter((item) => {
    const matchesSearch = item.name.toLowerCase().includes(searchValue)
    if (currentFilter.value === 'All') {
      return matchesSearch
    }

    const quarterMap = {
      Q1: item.q1t,
      Q2: item.q2t,
      Q3: item.q3t,
      Q4: item.q4t,
    }

    return matchesSearch && toNumber(quarterMap[currentFilter.value]) > 0
  })

  const numericMap = {
    total: 'total',
    pct: 'total',
    q1: 'q1t',
    q2: 'q2t',
    q3: 'q3t',
    q4: 'q4t',
  }

  return [...filtered].sort((a, b) => {
    if (currentSort.col === 'name') {
      return currentSort.dir * a.name.localeCompare(b.name)
    }

    const key = numericMap[currentSort.col]
    return currentSort.dir * (toNumber(a[key]) - toNumber(b[key]))
  })
})

const subtotals = computed(() => {
  return {
    total: visibleRows.value.reduce((acc, item) => acc + item.total, 0),
    q1: visibleRows.value.reduce((acc, item) => acc + item.q1t, 0),
    q2: visibleRows.value.reduce((acc, item) => acc + item.q2t, 0),
    q3: visibleRows.value.reduce((acc, item) => acc + item.q3t, 0),
    q4: visibleRows.value.reduce((acc, item) => acc + item.q4t, 0),
  }
})

const quarters = computed(() => {
  return quarterRanges.map((range, quarterIndex) => {
    const quarterKey = `q${quarterIndex + 1}`
    const totalKey = `${quarterKey}t`
    const total = tableRows.value.reduce((acc, item) => acc + toNumber(item[totalKey]), 0)

    const months = [0, 1, 2].map((offset) => {
      const monthIndex = quarterIndex * 3 + offset
      const monthEntries = tableRows.value
        .map((item) => {
          const qValues = item[quarterKey] || []
          const value = toNumber(qValues[offset])
          return value > 0 ? { name: item.name, color: item.color, value } : null
        })
        .filter(Boolean)

      const monthTotal = monthEntries.reduce((acc, entry) => acc + toNumber(entry.value), 0)

      return {
        name: monthNames[monthIndex],
        total: monthTotal,
        entries: monthEntries,
      }
    })

    return {
      label: `Q${quarterIndex + 1}`,
      range,
      total,
      months,
      badgeActive: quarterIndex === 0,
      badgeText: quarterIndex === 0 ? 'Active' : (total > 0 ? 'Has Data' : 'No Data'),
    }
  })
})

const accordionItems = computed(() => {
  return quarters.value.map((quarter) => {
    // Aggregate entries by name across all months in quarter
    const entriesByName = new Map()
    
    quarter.months.forEach((month) => {
      month.entries.forEach((entry) => {
        if (!entriesByName.has(entry.name)) {
          entriesByName.set(entry.name, {
            name: entry.name,
            color: entry.color,
            total: 0,
          })
        }
        entriesByName.get(entry.name).total += entry.value
      })
    })

    const entries = Array.from(entriesByName.values()).sort((a, b) => b.total - a.total)

    return {
      id: quarter.label,
      label: quarter.label,
      subtitle: quarter.range,
      badge: quarter.badgeText,
      badgeActive: quarter.badgeActive,
      total: quarter.total,
      totalDisplay: quarter.total > 0 ? formatMoney(quarter.total) : 'No expenses',
      months: quarter.months,
      entries: entries,
    }
  })
})

function setSort(column) {
  if (!['name', 'total', 'pct'].includes(column)) {
    return
  }

  if (currentSort.col === column) {
    currentSort.dir = currentSort.dir === 1 ? -1 : 1
  } else {
    currentSort.col = column
    currentSort.dir = -1
  }
}

async function loadReport() {
  loading.value = true
  loadError.value = ''

  try {
    const payload = await fetchExpensesReport(groupBy.value)
    currentYear.value = toNumber(payload?.current_year) || new Date().getFullYear()
    groupLabel.value = payload?.group_label || 'Expense Category'
    searchPlaceholder.value = payload?.search_placeholder || 'Search expense category...'
    groupBy.value = payload?.group_by === 'object' ? 'object' : 'classification'
    rows.value = Array.isArray(payload?.expense_data) ? payload.expense_data : []
    currentFilter.value = 'All'
    search.value = ''
    currentSort.col = 'total'
    currentSort.dir = -1
  } catch (error) {
    loadError.value = 'Unable to load expenses report data. Please try again.'
    rows.value = []
  } finally {
    loading.value = false
  }
}

function handleGroupByChange() {
  loadReport()
}

async function exportAll() {
  if (!tableRows.value.length) {
    return
  }

  const sheetRows = []
  sheetRows.push(['EXPENSES REPORT', '', '', '', '', '', '', ''])
  sheetRows.push([`Fiscal Year ${currentYear.value}`, '', '', '', '', '', '', ''])
  sheetRows.push([''])
  sheetRows.push([groupLabel.value, `${currentYear.value} Total`, '% of Total', 'Q1', 'Q2', 'Q3', 'Q4'])

  tableRows.value.forEach((entry) => {
    sheetRows.push([
      entry.name,
      entry.total.toFixed(2),
      entry.percent.toFixed(1),
      entry.q1t.toFixed(2),
      entry.q2t.toFixed(2),
      entry.q3t.toFixed(2),
      entry.q4t.toFixed(2),
    ])
  })

  sheetRows.push([''])
  sheetRows.push(['TOTAL', grandTotal.value.toFixed(2), '100.0'])

  const workbook = new ExcelJS.Workbook()
  const worksheet = workbook.addWorksheet('Expenses Report')
  worksheet.addRows(sheetRows)

  await downloadWorkbook(workbook, `Expenses_By_Category_Report_${new Date().toISOString().split('T')[0]}.xlsx`)
}

onMounted(() => {
  loadReport()
})
</script>
