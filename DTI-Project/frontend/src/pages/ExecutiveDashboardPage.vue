<template>
  <ReportPageLayout
    :title="'Executive Dashboard'"
    :description="`Provincial Director Overview · Fiscal Year ${currentYear}`"
  >
    <template #header-actions>
      <div class="dashboard-header-wrapper">
        <div class="year-selector-wrapper">
          <label for="yearSelect" class="year-selector-label">
            <ui-icon name="calendar-check" size="20" /> Fiscal Year:
          </label>
          <select id="yearSelect" v-model="currentYear" @change="fetchDashboardData" class="year-selector">
            <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>
        <div class="header-buttons-group">
          <button class="btn btn-secondary" type="button" @click="printPage" title="Print this report">
            <ui-icon name="printer" size="20" /> Print
          </button>
          <button class="btn btn-primary" type="button" @click="exportData" title="Export data to Excel">
            <ui-icon name="download" size="20" /> Export to Excel
          </button>
        </div>
      </div>
    </template>

    <!-- Last Updated Banner -->
    <div class="last-updated-banner">
      <ui-icon name="calendar-days" size="18" />
      <span>Data as of: <strong>{{ lastUpdatedLabel }}</strong></span>
      <span class="last-updated-divider">·</span>
      <span>Fiscal Year <strong>{{ currentYear }}</strong></span>
    </div>

    <!-- Key Performance Indicators -->
    <div class="dashboard-section">
      <h2 class="section-title">
        <ui-icon name="chart-column-big" size="26" /> Key Performance Indicators
      </h2>
      <div class="summary-cards">

        <div class="scard report-row-budget">
          <div class="kpi-card">
            <div class="kpi-icon-box kpi-icon-box--navy">
              <ui-icon name="wallet2" size="28" />
            </div>
          </div>
          <div class="scard-label">Total Budget Allocated</div>
          <div class="scard-amount">{{ formatCurrencyDisplay(totalBudget) }}</div>
          <div class="kpi-description">All fund sources combined</div>
        </div>

        <div class="scard report-row-disburse">
          <div class="kpi-card">
            <div class="kpi-icon-box kpi-icon-box--gold">
              <ui-icon name="arrow-up-right" size="28" />
            </div>
          </div>
          <div class="scard-label">Amount Spent</div>
          <div class="scard-amount">{{ formatCurrencyDisplay(netDisbursement) }}</div>
          <div class="kpi-description">Total disbursements to date</div>
        </div>

        <div class="scard report-row-balance">
          <div class="kpi-card">
            <div class="kpi-icon-box kpi-icon-box--success">
              <ui-icon name="piggy-bank" size="28" />
            </div>
          </div>
          <div class="scard-label">Remaining Balance</div>
          <div class="scard-amount">{{ formatCurrencyDisplay(remainingBalance) }}</div>
          <div class="kpi-description">Budget still available</div>
        </div>

        <div class="scard report-row-bur">
          <div class="kpi-card">
            <div class="kpi-icon-box kpi-icon-box--navy">
              <ui-icon name="percent" size="28" />
            </div>
          </div>
          <div class="scard-label">Budget Utilization</div>
          <div class="scard-amount">{{ budgetUtilizationPct }}<span class="kpi-utilization-percent">%</span></div>
          <div class="kpi-description">{{ utilizationLabel }}</div>
          <div class="kpi-progress-track">
            <div
              class="kpi-progress-fill"
              :style="{ width: Math.min(budgetUtilizationPct, 100) + '%', backgroundColor: getUtilizationColor() }"
            ></div>
          </div>
        </div>

      </div>
    </div>

    <!-- Alerts Section -->
    <div v-if="alerts.length > 0" class="dashboard-section">
      <h2 class="section-title">
        <ui-icon name="triangle-alert" size="26" /> Alerts &amp; Notices
      </h2>
      <div class="alerts-container">
        <div
          v-for="(alert, idx) in alerts"
          :key="idx"
          class="alert-item"
          :class="[`alert-item--${alert.type}`]"
          role="alert"
        >
          <div class="alert-icon">
            <ui-icon :name="alert.icon" size="24" />
          </div>
          <div class="alert-content">
            <div class="alert-title">{{ alert.title }}</div>
            <div class="alert-message">{{ alert.message }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Fund Status Table -->
    <div class="dashboard-section">
      <h2 class="section-title">
        <ui-icon name="wallet-minimal" size="26" /> Fund-by-Fund Status
      </h2>
      <div v-if="fundsData.length > 0" class="table-wrap">
        <table class="quarterly-table dashboard-table" aria-label="Fund status overview">
          <thead>
            <tr>
              <th scope="col">Fund Source</th>
              <th scope="col">Budget</th>
              <th scope="col">Spent</th>
              <th scope="col">Remaining</th>
              <th scope="col">Utilization</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="fund in fundsData" :key="fund.id">
              <td>{{ fund.name }}</td>
              <td>{{ formatCurrency(fund.budget) }}</td>
              <td>{{ formatCurrency(fund.spent) }}</td>
              <td>{{ formatCurrency(fund.remaining) }}</td>
              <td>
                <div class="utilization-cell">
                  <div class="utilization-bar">
                    <div
                      class="utilization-bar-fill"
                      :style="{ width: Math.min(fund.utilization, 100) + '%', backgroundColor: fund.color }"
                    ></div>
                  </div>
                  <span class="utilization-value" :style="{ color: fund.color }">{{ fund.utilization }}%</span>
                </div>
              </td>
              <td class="status-cell">
                <span :class="['status-badge', `status-badge--${getStatusBadge(fund.status)}`]">
                  <span class="status-dot"></span>
                  {{ fund.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty-state">
        <ui-icon name="inbox" size="52" />
        <p class="empty-state-text">No fund data available for this period.</p>
      </div>
    </div>

    <!-- Performance Metrics -->
    <div class="dashboard-section">
      <h2 class="section-title">
        <ui-icon name="chart-column-big" size="26" /> Performance Metrics
      </h2>
      <div class="metrics-container">
        <div class="scard metric-card">
          <div class="metric-icon-box metric-icon-box--navy"><ui-icon name="arrow-left-right" size="36" /></div>
          <div class="scard-amount metric-value">{{ formatNumber(performanceMetrics.totalTransactions) }}</div>
          <div class="scard-label">Total Transactions</div>
        </div>
        <div class="scard metric-card">
          <div class="metric-icon-box metric-icon-box--gold"><ui-icon name="banknote-arrow-down" size="36" /></div>
          <div class="scard-amount metric-value">{{ formatCurrency(performanceMetrics.totalDownloads) }}</div>
          <div class="scard-label">Downloads</div>
        </div>
        <div class="scard metric-card">
          <div class="metric-icon-box metric-icon-box--success"><ui-icon name="banknote-arrow-up" size="36" /></div>
          <div class="scard-amount metric-value">{{ formatCurrency(performanceMetrics.avgMonthlySpending) }}</div>
          <div class="scard-label">Avg Monthly Spending</div>
        </div>
        <div class="scard metric-card">
          <div class="metric-icon-box metric-icon-box--navy"><ui-icon name="arrow-right-left" size="36" /></div>
          <div class="scard-amount metric-value">{{ formatNumber(performanceMetrics.monthlyTransactionAvg) }}</div>
          <div class="scard-label">Monthly Transaction Avg</div>
        </div>
      </div>
    </div>

    <!-- Monthly Spending Chart -->
    <div class="dashboard-section">
      <h2 class="section-title">
        <ui-icon name="chart-column-decreasing" size="26" /> Monthly Spending Trend
      </h2>
      <div class="scard">
        <div class="chart-wrapper">
          <div id="monthlySpendingChart" class="chart-container"></div>
        </div>
      </div>
    </div>

  </ReportPageLayout>
</template>

<script setup>
import UiIcon from '@/components/ui/UiIcon.vue'
import ReportPageLayout from '@/components/patterns/ReportPageLayout.vue'
import { onMounted, ref, computed } from 'vue'
import * as d3 from 'd3'
import * as XLSX from 'exceljs'
import '@/assets/css/patterns/executive-dashboard.css'
import {
  fetchExecutiveDashboardData,
  fetchAvailableYears,
} from '@/services/executiveDashboardService'

// ─── State ────────────────────────────────────────────────────────────────────

const currentYear = ref(new Date().getFullYear())
const yearOptions = ref([])
const totalBudget = ref(0)
const netDisbursement = ref(0)
const remainingBalance = ref(0)
const budgetUtilizationPct = ref(0)
const utilizationLabel = ref('')
const alerts = ref([])
const fundsData = ref([])
const performanceMetrics = ref({
  totalTransactions: 0,
  totalDownloads: 0,
  avgMonthlySpending: 0,
  monthlyTransactionAvg: 0,
})
const monthlySpendingData = ref({})
const lastUpdatedLabel = ref(new Date().toLocaleDateString('en-PH', { year: 'numeric', month: 'long', day: 'numeric' }))

// ─── Computed ─────────────────────────────────────────────────────────────────

// ─── Helpers ──────────────────────────────────────────────────────────────────

const formatCurrency = (value) => {
  const num = Number(value || 0)
  return `₱${num.toLocaleString('en-PH', { maximumFractionDigits: 0 })}`
}

/** Compact format for large stat cards (e.g. ₱12.5M) */
const formatCurrencyDisplay = (value) => {
  const num = Number(value || 0)
  if (num >= 1_000_000_000) return `₱${(num / 1_000_000_000).toFixed(2)}B`
  if (num >= 1_000_000) return `₱${(num / 1_000_000).toFixed(2)}M`
  return `₱${num.toLocaleString('en-PH', { maximumFractionDigits: 0 })}`
}

const formatNumber = (value) => Number(value || 0).toLocaleString('en-PH')

const getUtilizationColor = () => {
  if (budgetUtilizationPct.value > 100) return '#c0392b'
  if (budgetUtilizationPct.value >= 80) return '#d68910'
  return '#1e8449'
}

const getStatusBadge = (status) => {
  const s = (status || '').toLowerCase()
  if (s.includes('critical') || s.includes('over')) return 'danger'
  if (s.includes('caution') || s.includes('warning')) return 'warning'
  return 'success'
}

// ─── Data Fetching ────────────────────────────────────────────────────────────

async function fetchDashboardData() {
  try {
    const years = await fetchAvailableYears()
    yearOptions.value = Array.isArray(years) ? years : [currentYear.value]

    const data = await fetchExecutiveDashboardData(currentYear.value)

    if (data.kpis) {
      totalBudget.value = data.kpis.total_budget || 0
      netDisbursement.value = data.kpis.net_disbursement || 0
      remainingBalance.value = data.kpis.remaining_balance || 0
      budgetUtilizationPct.value = Math.round(data.kpis.budget_utilization_pct || 0)
      utilizationLabel.value = data.kpis.status_label || 'Normal budget utilization'
    }

    if (Array.isArray(data.alerts)) {
      alerts.value = data.alerts.map(alert => ({
        ...alert,
        type: alert.type || 'info',
        icon: alert.icon || 'info-circle',
      }))
    }

    if (Array.isArray(data.funds)) {
      fundsData.value = data.funds.map(fund => ({
        ...fund,
        color: getFundColor(fund.utilization),
      }))
    }

    if (data.metrics) {
      performanceMetrics.value = {
        totalTransactions: data.metrics.total_transactions || 0,
        totalDownloads: data.metrics.total_downloads || 0,
        avgMonthlySpending: data.metrics.avg_monthly_spending || 0,
        monthlyTransactionAvg: data.metrics.monthly_transaction_avg || 0,
      }
    }

    if (data.spendings && typeof data.spendings === 'object') {
      monthlySpendingData.value = data.spendings
    }

    lastUpdatedLabel.value = new Date().toLocaleDateString('en-PH', { year: 'numeric', month: 'long', day: 'numeric' })

    await new Promise(resolve => setTimeout(resolve, 0))
    drawMonthlyChart()
  } catch (error) {
    console.error('Error fetching dashboard data:', error)
  }
}

function getFundColor(utilization) {
  if (utilization > 100) return '#c0392b'
  if (utilization >= 80) return '#d68910'
  return '#1e8449'
}

// ─── D3 Chart ─────────────────────────────────────────────────────────────────

function drawMonthlyChart() {
  const chartEl = document.getElementById('monthlySpendingChart')
  if (!chartEl) return

  const monthNames = Object.keys(monthlySpendingData.value)
  const monthValues = Object.values(monthlySpendingData.value)

  if (!monthNames.length) {
    chartEl.innerHTML = '<div style="padding:3rem;text-align:center;color:#555;font-size:1.1rem;">No spending data available for this period.</div>'
    return
  }

  const containerWidth = chartEl.clientWidth || 900
  const containerHeight = 420
  const margin = { top: 36, right: 40, bottom: 60, left: 96 }
  const innerWidth = containerWidth - margin.left - margin.right
  const innerHeight = containerHeight - margin.top - margin.bottom

  const chartData = monthNames.map((label, i) => ({ label, value: monthValues[i] }))

  const xScale = d3.scaleBand().domain(monthNames).range([0, innerWidth]).padding(0.38)
  const yScale = d3.scaleLinear().domain([0, d3.max(chartData, d => d.value) * 1.18]).range([innerHeight, 0])

  d3.select(chartEl).selectAll('*').remove()

  const svg = d3.select(chartEl)
    .append('svg')
    .attr('width', containerWidth)
    .attr('height', containerHeight)
    .attr('viewBox', `0 0 ${containerWidth} ${containerHeight}`)
    .attr('preserveAspectRatio', 'xMidYMid meet')

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  // Grid lines
  g.append('g')
    .call(d3.axisLeft(yScale).ticks(6).tickSize(-innerWidth).tickFormat(''))
    .call(grid => {
      grid.select('.domain').remove()
      grid.selectAll('line').attr('stroke', '#ccc').attr('stroke-dasharray', '5,5').attr('opacity', '0.5')
    })

  // Bars
  g.selectAll('.bar')
    .data(chartData)
    .enter()
    .append('rect')
    .attr('class', 'bar')
    .attr('x', d => xScale(d.label))
    .attr('y', d => yScale(d.value))
    .attr('width', xScale.bandwidth())
    .attr('height', d => innerHeight - yScale(d.value))
    .attr('fill', '#1a3a5c')
    .attr('rx', 6)
    .style('cursor', 'pointer')
    .on('mouseover', function (event, d) {
      d3.select(this).attr('fill', '#2e6aad')
      tooltip.style('opacity', 1).html(
        `<div style="font-size:14px;font-weight:700;margin-bottom:4px">${d.label}</div>
         <div style="font-size:16px">₱${(d.value / 1_000_000).toFixed(2)}M</div>`
      )
    })
    .on('mousemove', function (event) {
      tooltip.style('left', event.pageX + 14 + 'px').style('top', event.pageY - 40 + 'px')
    })
    .on('mouseout', function () {
      d3.select(this).attr('fill', '#1a3a5c')
      tooltip.style('opacity', 0)
    })

  // Value labels — larger text
  g.selectAll('.bar-label')
    .data(chartData)
    .enter()
    .append('text')
    .attr('class', 'bar-label')
    .attr('x', d => xScale(d.label) + xScale.bandwidth() / 2)
    .attr('y', d => yScale(d.value) - 12)
    .attr('text-anchor', 'middle')
    .attr('fill', '#1a3a5c')
    .attr('font-size', '13px')
    .attr('font-weight', '700')
    .text(d => `₱${(d.value / 1_000_000).toFixed(1)}M`)

  // X axis — bigger tick labels
  g.append('g')
    .attr('transform', `translate(0,${innerHeight})`)
    .call(d3.axisBottom(xScale))
    .call(axis => {
      axis.select('.domain').attr('stroke', '#aaa')
      axis.selectAll('line').remove()
      axis.selectAll('text').attr('fill', '#444').attr('font-size', '14px').attr('font-weight', '600').attr('dy', '12px')
    })

  // Y axis — bigger labels
  g.append('g')
    .call(d3.axisLeft(yScale).ticks(6).tickFormat(d => `₱${d / 1_000_000}M`))
    .call(axis => {
      axis.select('.domain').attr('stroke', '#aaa')
      axis.selectAll('text').attr('fill', '#444').attr('font-size', '13px')
    })

  // Y axis title
  svg.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('y', 0 - margin.left + 4)
    .attr('x', 0 - (innerHeight / 2) - margin.top)
    .attr('dy', '1em')
    .style('text-anchor', 'middle')
    .attr('fill', '#444')
    .attr('font-size', '13px')
    .attr('font-weight', '700')
    .text('Monthly Spending (₱)')

  // Tooltip
  const tooltip = d3.select('body')
    .append('div')
    .style('position', 'absolute')
    .style('background', 'rgba(10,30,60,0.92)')
    .style('color', '#fff')
    .style('padding', '12px 18px')
    .style('border-radius', '8px')
    .style('font-size', '14px')
    .style('line-height', '1.5')
    .style('pointer-events', 'none')
    .style('opacity', 0)
    .style('z-index', '9999')
    .style('box-shadow', '0 4px 16px rgba(0,0,0,0.3)')
}

// ─── Export & Print ───────────────────────────────────────────────────────────

async function exportData() {
  try {
    const workbook = new XLSX.Workbook()
    const sheet = workbook.addWorksheet('Executive Dashboard')

    sheet.mergeCells('A1:F1')
    const titleCell = sheet.getCell('A1')
    titleCell.value = 'Executive Dashboard Report'
    titleCell.font = { size: 16, bold: true }
    titleCell.alignment = { horizontal: 'center', vertical: 'center' }
    sheet.getRow(1).height = 28

    sheet.mergeCells('A2:F2')
    const metaCell = sheet.getCell('A2')
    metaCell.value = `Fiscal Year ${currentYear.value} · Generated ${new Date().toLocaleDateString('en-PH')}`
    metaCell.font = { size: 11, italic: true, color: { argb: '666666' } }
    metaCell.alignment = { horizontal: 'center' }
    sheet.getRow(2).height = 20

    sheet.addRow([])

    sheet.addRow(['KEY PERFORMANCE INDICATORS']).getCell(1).font = { bold: true, size: 13 }
    sheet.addRow(['Metric', 'Value']).eachCell(c => { c.font = { bold: true }; c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'E8EDF5' } } })
    sheet.addRow(['Total Budget Allocated', formatCurrency(totalBudget.value)])
    sheet.addRow(['Amount Spent', formatCurrency(netDisbursement.value)])
    sheet.addRow(['Remaining Balance', formatCurrency(remainingBalance.value)])
    sheet.addRow(['Budget Utilization', `${budgetUtilizationPct.value}%`])
    sheet.addRow([])

    sheet.addRow(['FUND-BY-FUND STATUS']).getCell(1).font = { bold: true, size: 13 }
    const fundHeader = sheet.addRow(['Fund Source', 'Budget', 'Spent', 'Remaining', 'Utilization %', 'Status'])
    fundHeader.eachCell(c => { c.font = { bold: true }; c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'E8EDF5' } } })
    fundsData.value.forEach(fund => {
      sheet.addRow([fund.name, fund.budget, fund.spent, fund.remaining, `${fund.utilization}%`, fund.status])
    })
    sheet.addRow([])

    sheet.addRow(['PERFORMANCE METRICS']).getCell(1).font = { bold: true, size: 13 }
    sheet.addRow(['Metric', 'Value']).eachCell(c => { c.font = { bold: true }; c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'E8EDF5' } } })
    sheet.addRow(['Total Transactions', performanceMetrics.value.totalTransactions])
    sheet.addRow(['Total Downloads', performanceMetrics.value.totalDownloads])
    sheet.addRow(['Avg Monthly Spending', performanceMetrics.value.avgMonthlySpending])
    sheet.addRow(['Monthly Transaction Avg', performanceMetrics.value.monthlyTransactionAvg])

    sheet.columns = [{ width: 32 }, { width: 20 }, { width: 20 }, { width: 20 }, { width: 18 }, { width: 18 }]
    sheet.eachRow((row, rn) => {
      row.height = 20
      row.eachCell(cell => {
        cell.border = {
          top: { style: 'thin', color: { argb: 'D0D5DD' } },
          bottom: { style: 'thin', color: { argb: 'D0D5DD' } },
          left: { style: 'thin', color: { argb: 'D0D5DD' } },
          right: { style: 'thin', color: { argb: 'D0D5DD' } },
        }
        if (rn > 2) cell.font = { ...(cell.font || {}), size: 11 }
      })
    })

    await workbook.xlsx.writeFile(`ExecutiveDashboard_FY${currentYear.value}_${Date.now()}.xlsx`)
  } catch (error) {
    console.error('Export error:', error)
  }
}

const printPage = () => window.print()

// ─── Lifecycle ────────────────────────────────────────────────────────────────

onMounted(() => {
  fetchDashboardData()
})
</script>
