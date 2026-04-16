<template>
  <DashboardPageLayout root-class="dashboard-wrapper">
    <template #header>
      <div class="dashboard-header">
        <div>
          <div class="header-eyebrow">DTI Fund Monitoring System</div>
          <h1>Financial Dashboard</h1>
          <p>Comprehensive fund monitoring and budget analysis</p>
        </div>
        <div class="header-controls">
          <div class="live-badge">
            <span class="dot"></span>
            Live data
          </div>
          <button class="btn-print" @click="printReport">
            <ui-icon name="printer" size="20" /> Print Report
          </button>
        </div>
      </div>
    </template>

    <template #filters>
      <form id="filterForm" class="filter-bar filter-bar--dashboard" @submit.prevent="applyFilters">
        <div class="filter-group">
          <label for="yearFilter">Year</label>
          <select id="yearFilter" v-model="filterForm.year" name="year">
            <option value="">All Years</option>
            <option v-for="year in yearOptions" :key="year" :value="String(year)">{{ year }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="fundSourceFilter">Fund Source</label>
          <select id="fundSourceFilter" v-model="filterForm.fund_source" name="fund_source">
            <option value="">All Fund Sources</option>
            <option v-for="item in fundSourceOptions" :key="item.id" :value="String(item.id)">{{ item.name }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="divisionFilter">Division</label>
          <select id="divisionFilter" v-model="filterForm.division" name="division">
            <option value="">All Divisions</option>
            <option v-for="item in divisionOptions" :key="item.id" :value="String(item.id)">{{ item.name }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="dateFilter">Month</label>
          <select id="dateFilter" v-model="filterForm.date_month" name="date_month">
            <option value="">All Months</option>
            <option v-for="month in monthOptions" :key="month.value" :value="month.value">{{ month.label }}</option>
          </select>
        </div>

        <div class="filter-actions">
          <button type="submit" class="btn-apply">
            <ui-icon name="filter" size="18" /> Apply Filters
          </button>
          <button type="button" class="btn-reset" @click="resetFilters">
            <ui-icon name="rotate-ccw" size="18" /> Reset
          </button>
        </div>
      </form>
    </template>

    <template #summary>
      <section class="summary-section">
        <h2 class="section-title">Key Performance Indicators</h2>
        <div class="metrics-grid">
          <div class="metric-card primary">
            <div class="metric-card-top"><div class="metric-icon"><ui-icon name="wallet" size="24" /></div></div>
            <p class="metric-label">Total Annual Budget</p>
            <h3 class="metric-value">{{ formatCurrency(kpis.totalBudget) }}</h3>
            <span class="metric-footer">Allocated funds</span>
          </div>

          <div class="metric-card accent">
            <div class="metric-card-top"><div class="metric-icon"><ui-icon name="check-circle-2" size="24" /></div></div>
            <p class="metric-label">Active Pooling Funds</p>
            <h3 class="metric-value">{{ formatNumber(kpis.activeFunds) }}<span class="metric-value__suffix">/ total</span></h3>
            <span class="metric-footer">{{ formatCurrency(kpis.activeBudget) }}</span>
          </div>

          <div class="metric-card success">
            <div class="metric-card-top"><div class="metric-icon"><ui-icon name="banknote-arrow-down" size="24" /></div></div>
            <p class="metric-label">Total Disbursement</p>
            <h3 class="metric-value">{{ formatCurrency(kpis.totalDisbursement) }}</h3>
            <span class="metric-footer">Amount released</span>
          </div>

          <div class="metric-card warning">
            <div class="metric-card-top"><div class="metric-icon"><ui-icon name="banknote" size="24" /></div></div>
            <p class="metric-label">Remaining Balance</p>
            <h3 class="metric-value">{{ formatCurrency(kpis.remainingBalance) }}</h3>
            <span class="metric-footer">Available funds</span>
          </div>

          <div class="metric-card info">
            <div class="metric-card-top"><div class="metric-icon"><ui-icon name="percent" size="24" /></div></div>
            <p class="metric-label">Budget Utilization Rate</p>
            <h3 class="metric-value">{{ Number(kpis.budgetUtilizationRate || 0).toFixed(2) }}%</h3>
            <span class="metric-footer">Budget usage</span>
          </div>

          <div class="metric-card secondary">
            <div class="metric-card-top"><div class="metric-icon"><ui-icon name="arrow-right-left" size="24" /></div></div>
            <p class="metric-label">Total Transactions</p>
            <h3 class="metric-value">{{ formatNumber(kpis.totalTransactions) }}</h3>
            <span class="metric-footer">Records</span>
          </div>

          <div class="metric-card tertiary">
            <div class="metric-card-top"><div class="metric-icon"><ui-icon name="users" size="24" /></div></div>
            <p class="metric-label">Total Payees Paid</p>
            <h3 class="metric-value">{{ formatNumber(kpis.totalSuppliersPaid) }}</h3>
            <span class="metric-footer">Payee</span>
          </div>
        </div>
      </section>
    </template>

    <template #content>
      <section class="quick-links-section">
        <h3 class="quick-links-title">Quick Links Reports</h3>
        <div class="quick-links-grid">
          <RouterLink v-for="link in quickLinks" :key="link.to" :to="link.to" class="quick-link-btn">
            <ui-icon name="file-symlink" size="18" />
            <span>{{ link.label }}</span>
          </RouterLink>
        </div>
      </section>

      <section class="charts-section">
        <h2 class="section-title">Financial Analysis</h2>

        <div class="chart-card full-width">
          <div class="chart-header">
            <div class="chart-header-text"><h3>Monthly Disbursement Trend</h3><p>Spending pattern throughout the year</p></div>
            <span class="chart-badge">Line Chart</span>
          </div>
          <div id="monthlyChart" class="chart-plot"></div>
        </div>

        <div class="chart-card full-width">
          <div class="chart-header">
            <div class="chart-header-text"><h3>Monthly Downloads Trend</h3><p>Fund allocations received from higher office (MDP)</p></div>
            <span class="chart-badge">Line Chart</span>
          </div>
          <div id="monthlyDownloadsChart" class="chart-plot"></div>
        </div>

        <div class="charts-grid two-col">
          <div class="chart-card">
            <div class="chart-header">
              <div class="chart-header-text"><h3>Remaining Balance by Fund Source</h3><p>Available funds after disbursements</p></div>
              <span class="chart-badge">Donut</span>
            </div>
            <div id="fundChart" class="chart-plot"></div>
          </div>
          <div class="chart-card">
            <div class="chart-header">
              <div class="chart-header-text"><h3>Budget vs Disbursement</h3><p>Comparison by fund source</p></div>
              <span class="chart-badge">Bar Chart</span>
            </div>
            <div id="budgetChart" class="chart-plot"></div>
          </div>
        </div>

        <div class="chart-card full-width">
          <div class="chart-header">
            <div class="chart-header-text"><h3>Account Title / Expense Objects Analysis</h3><p>Top expense objects by amount</p></div>
            <span class="chart-badge">Horizontal Bar</span>
          </div>
          <div id="expenseChart" class="chart-plot"></div>
        </div>

        <div class="charts-grid two-col">
          <div class="chart-card">
            <div class="chart-header">
              <div class="chart-header-text"><h3>Top Payees</h3><p>Highest payment recipients</p></div>
              <span class="chart-badge">Bar Chart (Top 10)</span>
            </div>
            <div id="supplierChart" class="chart-plot"></div>
          </div>
          <div class="chart-card">
            <div class="chart-header">
              <div class="chart-header-text"><h3>MOOE Breakdown Remaining Balance</h3><p>Available budget in each MOOE category</p></div>
              <span class="chart-badge">Donut</span>
            </div>
            <div id="mooeChart" class="chart-plot"></div>
          </div>
        </div>

        <div class="charts-grid two-col">
          <div class="chart-card">
            <div class="chart-header">
              <div class="chart-header-text"><h3>Cheque Monitoring</h3><p>Payment status distribution</p></div>
              <span class="chart-badge">Donut</span>
            </div>
            <div id="chequeChart" class="chart-plot"></div>
          </div>
          <div class="chart-card">
            <div class="chart-header">
              <div class="chart-header-text"><h3>District Spending</h3><p>Allocation across districts</p></div>
              <span class="chart-badge">Bar Chart</span>
            </div>
            <div id="districtChart" class="chart-plot"></div>
          </div>
        </div>

        <div class="chart-card full-width">
          <div class="chart-header">
            <div class="chart-header-text"><h3>Bank Balance Trend</h3><p>Debit, credit, and running balance</p></div>
            <span class="chart-badge">Area Chart</span>
          </div>
          <div id="bankChart" class="chart-plot"></div>
        </div>
      </section>

      <!-- Shared D3 Tooltip -->
      <div id="d3-tooltip" class="d3-tooltip" style="display:none;"></div>
    </template>
  </DashboardPageLayout>
</template>

<script setup>
import UiIcon from '@/components/ui/UiIcon.vue'
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import * as d3 from 'd3'
import DashboardPageLayout from '@/components/patterns/DashboardPageLayout.vue'
import {
  fetchDashboardCharts,
  fetchDashboardFilters,
  fetchDashboardKpis,
} from '@/services/dashboardService'

// ─── Constants ───────────────────────────────────────────────────────────────

const quickLinks = [
  { to: '/fund-report', label: 'Fund Report' },
  { to: '/mooe-report', label: 'MOOE Report' },
  { to: '/negosyo-center-report', label: 'NC Report' },
  { to: '/report', label: 'Expense Report' },
]

const monthOptions = [
  { value: '1', label: 'January' }, { value: '2', label: 'February' },
  { value: '3', label: 'March' },   { value: '4', label: 'April' },
  { value: '5', label: 'May' },     { value: '6', label: 'June' },
  { value: '7', label: 'July' },    { value: '8', label: 'August' },
  { value: '9', label: 'September' },{ value: '10', label: 'October' },
  { value: '11', label: 'November' },{ value: '12', label: 'December' },
]

// ─── State ────────────────────────────────────────────────────────────────────

const filterForm = ref({ year: '', fund_source: '', division: '', date_month: '' })
const yearOptions = ref([])
const fundSourceOptions = ref([])
const divisionOptions = ref([])
const chartsData = ref({})
const kpis = ref({
  totalBudget: 0, activeFunds: 0, activeBudget: 0, totalDisbursement: 0,
  remainingBalance: 0, budgetUtilizationRate: 0, totalTransactions: 0, totalSuppliersPaid: 0,
})

let resizeObserver = null

// ─── Helpers ──────────────────────────────────────────────────────────────────

const formatCurrency = (v) => `₱${Number(v || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`
const formatNumber   = (v) => Number(v || 0).toLocaleString()
const printReport    = () => window.print()
const normalizeArray  = (v) => Array.isArray(v) ? v : []
const normalizeObject = (v) => (v && typeof v === 'object' && !Array.isArray(v)) ? v : {}

function getParams() {
  const p = {}
  if (filterForm.value.year)       p.year       = filterForm.value.year
  if (filterForm.value.fund_source) p.fund_source = filterForm.value.fund_source
  if (filterForm.value.division)   p.division   = filterForm.value.division
  if (filterForm.value.date_month) p.date_month = filterForm.value.date_month
  return p
}

// ─── Theme / Palette ─────────────────────────────────────────────────────────

function getTheme() {
  const cs = getComputedStyle(document.documentElement)
  return {
    text:     cs.getPropertyValue('--text-secondary').trim() || '#8b90a8',
    textPri:  cs.getPropertyValue('--text-primary').trim()   || '#e2e8f0',
    grid:     'rgba(255,255,255,0.06)',
    palette:  ['#3b82f6','#10b981','#f59e0b','#f43f5e','#8b5cf6','#38bdf8','#a3e635','#fb923c','#ec4899','#06b6d4'],
    blue:     '#3b82f6',
    green:    '#10b981',
    amber:    '#f59e0b',
    rose:     '#f43f5e',
    violet:   '#8b5cf6',
    sky:      '#38bdf8',
  }
}

// ─── Tooltip ─────────────────────────────────────────────────────────────────

function getTooltip() {
  return document.getElementById('d3-tooltip')
}
function showTip(html, event) {
  const tip = getTooltip()
  if (!tip) return
  tip.innerHTML = html
  tip.style.display = 'block'
  moveTip(event)
}
function moveTip(event) {
  const tip = getTooltip()
  if (!tip) return
  tip.style.left = (event.clientX + 14) + 'px'
  tip.style.top  = (event.clientY - 28) + 'px'
}
function hideTip() {
  const tip = getTooltip()
  if (tip) tip.style.display = 'none'
}

// ─── Empty State ─────────────────────────────────────────────────────────────

function showEmptyState(id, msg = 'No data available for the selected period') {
  const el = document.getElementById(id)
  if (!el) return
  el.innerHTML = `<div class="chart-empty">${msg}</div>`
}

function clearChart(id) {
  const el = document.getElementById(id)
  if (!el) return
  el.innerHTML = ''
}

// ─── Chart: Line / Area ───────────────────────────────────────────────────────

function drawLineChart(id, labels, values, color) {
  if (!labels?.length) return showEmptyState(id)
  const T   = getTheme()
  const el  = document.getElementById(id)
  if (!el) return
  clearChart(id)

  const W  = el.clientWidth  || 600
  const H  = el.clientHeight || 220
  const m  = { top: 12, right: 16, bottom: 32, left: 56 }
  const iW = W - m.left - m.right
  const iH = H - m.top  - m.bottom

  const data = labels.map((l, i) => ({ label: l, value: +values[i] }))

  const x = d3.scalePoint().domain(data.map(d => d.label)).range([0, iW]).padding(0.1)
  const y = d3.scaleLinear().domain([0, d3.max(data, d => d.value) * 1.12]).range([iH, 0])

  const svg = d3.select(el).append('svg')
    .attr('width', W).attr('height', H)
    .append('g').attr('transform', `translate(${m.left},${m.top})`)

  // Gradient fill
  const gradId = `grad-${id}`
  const defs   = svg.append('defs')
  const grad   = defs.append('linearGradient').attr('id', gradId).attr('x1','0').attr('y1','0').attr('x2','0').attr('y2','1')
  grad.append('stop').attr('offset','0%').attr('stop-color', color).attr('stop-opacity', 0.22)
  grad.append('stop').attr('offset','100%').attr('stop-color', color).attr('stop-opacity', 0.01)

  // Grid lines
  svg.append('g').attr('class', 'd3-grid')
    .call(d3.axisLeft(y).ticks(4).tickSize(-iW).tickFormat(''))
    .call(g => { g.select('.domain').remove(); g.selectAll('line').attr('stroke', T.grid) })

  // Area
  const area = d3.area()
    .x(d => x(d.label)).y0(iH).y1(d => y(d.value)).curve(d3.curveCatmullRom)

  svg.append('path').datum(data)
    .attr('fill', `url(#${gradId})`).attr('d', area)

  // Line
  const line = d3.line()
    .x(d => x(d.label)).y(d => y(d.value)).curve(d3.curveCatmullRom)

  const path = svg.append('path').datum(data)
    .attr('fill', 'none').attr('stroke', color).attr('stroke-width', 2.5).attr('d', line)

  // Animate stroke
  const totalLen = path.node().getTotalLength()
  path.attr('stroke-dasharray', totalLen).attr('stroke-dashoffset', totalLen)
    .transition().duration(900).ease(d3.easeCubicOut).attr('stroke-dashoffset', 0)

  // Dots
  svg.selectAll('.dot').data(data).enter().append('circle')
    .attr('class', 'dot').attr('cx', d => x(d.label)).attr('cy', d => y(d.value))
    .attr('r', 0).attr('fill', color).attr('stroke', '#12141e').attr('stroke-width', 2)
    .on('mouseover', (event, d) => showTip(`<b>${d.label}</b><br>₱${d.value.toLocaleString()}`, event))
    .on('mousemove', moveTip).on('mouseout', hideTip)
    .transition().delay((_, i) => i * 40).duration(300).attr('r', 4.5)

  // Axes
  svg.append('g').attr('transform', `translate(0,${iH})`)
    .call(d3.axisBottom(x).tickSize(0))
    .call(g => { g.select('.domain').attr('stroke', T.grid); g.selectAll('text').attr('fill', T.text).attr('dy', '1.2em') })

  svg.append('g')
    .call(d3.axisLeft(y).ticks(4).tickFormat(v => `₱${d3.format('.2s')(v)}`))
    .call(g => { g.select('.domain').remove(); g.selectAll('text').attr('fill', T.text) })
}

// ─── Chart: Donut / Pie ───────────────────────────────────────────────────────

function drawDonutChart(id, labels, values, fmtFn = v => `₱${Number(v).toLocaleString()}`) {
  if (!labels?.length) return showEmptyState(id)
  const T   = getTheme()
  const el  = document.getElementById(id)
  if (!el) return
  clearChart(id)

  const W   = el.clientWidth  || 340
  const H   = el.clientHeight || 260
  const R   = Math.min(W * 0.38, H * 0.42)
  const data = labels.map((l, i) => ({ label: l, value: +values[i] }))
  const color = d3.scaleOrdinal(T.palette)

  const svg = d3.select(el).append('svg').attr('width', W).attr('height', H)
  const g   = svg.append('g').attr('transform', `translate(${W * 0.38},${H / 2})`)

  const pie  = d3.pie().value(d => d.value).sort(null)
  const arc  = d3.arc().innerRadius(R * 0.58).outerRadius(R)
  const arcH = d3.arc().innerRadius(R * 0.58).outerRadius(R * 1.06)

  const arcs = g.selectAll('.arc').data(pie(data)).enter().append('g').attr('class', 'arc')

  arcs.append('path')
    .attr('fill', d => color(d.data.label))
    .attr('stroke', '#12141e').attr('stroke-width', 2)
    .on('mouseover', function(event, d) {
      d3.select(this).transition().duration(150).attr('d', arcH)
      showTip(`<b>${d.data.label}</b><br>${fmtFn(d.data.value)}`, event)
    })
    .on('mousemove', moveTip)
    .on('mouseout', function() {
      d3.select(this).transition().duration(150).attr('d', arc)
      hideTip()
    })
    .transition().duration(700).ease(d3.easeCubicOut)
    .attrTween('d', function(d) {
      const i = d3.interpolate({ startAngle: 0, endAngle: 0 }, d)
      return t => arc(i(t))
    })

  // Center total
  const total = d3.sum(data, d => d.value)
  g.append('text').attr('text-anchor', 'middle').attr('dy', '-0.3em')
    .attr('fill', T.text).attr('font-size', '10px').text('Total')
  g.append('text').attr('text-anchor', 'middle').attr('dy', '1.1em')
    .attr('fill', T.textPri).attr('font-size', '13px').attr('font-weight', '600')
    .text(fmtFn === null ? total.toLocaleString() : `₱${d3.format('.2s')(total)}`)

  // Legend
  const legend = svg.append('g').attr('transform', `translate(${W * 0.76}, ${H / 2 - (data.length * 14) / 2})`)
  data.forEach((d, i) => {
    const row = legend.append('g').attr('transform', `translate(0, ${i * 20})`)
    row.append('rect').attr('width', 10).attr('height', 10).attr('rx', 2)
      .attr('fill', color(d.label)).attr('y', -1)
    row.append('text').attr('x', 14).attr('y', 8).attr('fill', T.text).attr('font-size', '10px')
      .text(d.label.length > 18 ? d.label.slice(0, 17) + '…' : d.label)
  })
}

// ─── Chart: Grouped Bar ───────────────────────────────────────────────────────

function drawGroupedBarChart(id, labels, series) {
  // series: [{ name, values, color }]
  if (!labels?.length) return showEmptyState(id)
  const T  = getTheme()
  const el = document.getElementById(id)
  if (!el) return
  clearChart(id)

  const W  = el.clientWidth  || 400
  const H  = el.clientHeight || 260
  const m  = { top: 32, right: 16, bottom: 48, left: 60 }
  const iW = W - m.left - m.right
  const iH = H - m.top  - m.bottom

  const svg = d3.select(el).append('svg').attr('width', W).attr('height', H)
    .append('g').attr('transform', `translate(${m.left},${m.top})`)

  const x0 = d3.scaleBand().domain(labels).range([0, iW]).padding(0.25)
  const x1 = d3.scaleBand().domain(series.map(s => s.name)).range([0, x0.bandwidth()]).padding(0.08)
  const maxVal = d3.max(series.flatMap(s => s.values.map(v => +v)))
  const y  = d3.scaleLinear().domain([0, maxVal * 1.1]).range([iH, 0])

  // Grid
  svg.append('g').call(d3.axisLeft(y).ticks(4).tickSize(-iW).tickFormat(''))
    .call(g => { g.select('.domain').remove(); g.selectAll('line').attr('stroke', T.grid) })

  // Bars
  const groups = svg.selectAll('.bar-group').data(labels).enter().append('g')
    .attr('class', 'bar-group').attr('transform', l => `translate(${x0(l)},0)`)

  series.forEach(s => {
    groups.append('rect')
      .attr('x', x1(s.name)).attr('width', x1.bandwidth())
      .attr('y', iH).attr('height', 0)
      .attr('rx', 3).attr('fill', s.color).attr('opacity', 0.85)
      .on('mouseover', function(event, l) {
        const i = labels.indexOf(l)
        d3.select(this).attr('opacity', 1)
        showTip(`<b>${l}</b><br>${s.name}: ₱${Number(s.values[i]).toLocaleString()}`, event)
      })
      .on('mousemove', moveTip).on('mouseout', function() { d3.select(this).attr('opacity', 0.85); hideTip() })
      .transition().duration(600).ease(d3.easeCubicOut)
      .attr('y', (l) => { const i = labels.indexOf(l); return y(+s.values[i]) })
      .attr('height', (l) => { const i = labels.indexOf(l); return iH - y(+s.values[i]) })
  })

  // Axes
  svg.append('g').attr('transform', `translate(0,${iH})`)
    .call(d3.axisBottom(x0).tickSize(0))
    .call(g => {
      g.select('.domain').attr('stroke', T.grid)
      g.selectAll('text').attr('fill', T.text).attr('dy', '1.2em')
        .text(l => l.length > 10 ? l.slice(0, 9) + '…' : l)
    })

  svg.append('g').call(d3.axisLeft(y).ticks(4).tickFormat(v => `₱${d3.format('.2s')(v)}`))
    .call(g => { g.select('.domain').remove(); g.selectAll('text').attr('fill', T.text) })

  // Legend
  const lg = svg.append('g').attr('transform', `translate(0, -24)`)
  series.forEach((s, i) => {
    const row = lg.append('g').attr('transform', `translate(${i * 110}, 0)`)
    row.append('rect').attr('width', 10).attr('height', 10).attr('rx', 2).attr('fill', s.color)
    row.append('text').attr('x', 14).attr('y', 9).attr('fill', T.text).attr('font-size', '10px').text(s.name)
  })
}

// ─── Chart: Horizontal Bar ───────────────────────────────────────────────────

function drawHorizontalBarChart(id, labels, values, color) {
  if (!labels?.length) return showEmptyState(id)
  const T  = getTheme()
  const el = document.getElementById(id)
  if (!el) return
  clearChart(id)

  const rowH  = 32
  const m     = { top: 8, right: 60, bottom: 8, left: 10 }
  const W     = el.clientWidth || 600
  const H     = labels.length * rowH + m.top + m.bottom
  const iW    = W - m.left - m.right - 180   // 180px for label column
  const labelW = 180

  el.style.height = H + 'px'

  const svg = d3.select(el).append('svg').attr('width', W).attr('height', H)
    .append('g').attr('transform', `translate(${m.left},${m.top})`)

  const y = d3.scaleBand().domain(labels).range([0, H - m.top - m.bottom]).padding(0.3)
  const x = d3.scaleLinear().domain([0, d3.max(values.map(v => +v)) * 1.1]).range([0, iW])

  // Row labels
  svg.selectAll('.bar-label').data(labels).enter().append('text')
    .attr('class', 'bar-label')
    .attr('x', labelW - 8).attr('y', l => y(l) + y.bandwidth() / 2 + 4)
    .attr('text-anchor', 'end').attr('fill', T.text).attr('font-size', '10px')
    .text(l => l.length > 26 ? l.slice(0, 25) + '…' : l)

  // Bars
  svg.selectAll('.hbar').data(labels).enter().append('rect')
    .attr('class', 'hbar').attr('x', labelW)
    .attr('y', l => y(l)).attr('height', y.bandwidth())
    .attr('rx', 3).attr('fill', color).attr('opacity', 0.82)
    .attr('width', 0)
    .on('mouseover', function(event, l) {
      d3.select(this).attr('opacity', 1)
      const i = labels.indexOf(l)
      showTip(`<b>${l}</b><br>₱${Number(values[i]).toLocaleString()}`, event)
    })
    .on('mousemove', moveTip).on('mouseout', function() { d3.select(this).attr('opacity', 0.82); hideTip() })
    .transition().duration(600).ease(d3.easeCubicOut)
    .attr('width', l => { const i = labels.indexOf(l); return x(+values[i]) })

  // Value labels
  svg.selectAll('.val-label').data(labels).enter().append('text')
    .attr('class', 'val-label')
    .attr('x', l => { const i = labels.indexOf(l); return labelW + x(+values[i]) + 6 })
    .attr('y', l => y(l) + y.bandwidth() / 2 + 4)
    .attr('fill', T.text).attr('font-size', '10px')
    .text(l => { const i = labels.indexOf(l); return `₱${d3.format('.2s')(+values[i])}` })
}

// ─── Chart: Vertical Bar ─────────────────────────────────────────────────────

function drawBarChart(id, labels, values, color) {
  if (!labels?.length) return showEmptyState(id)
  const T  = getTheme()
  const el = document.getElementById(id)
  if (!el) return
  clearChart(id)

  const W  = el.clientWidth  || 400
  const H  = el.clientHeight || 260
  const m  = { top: 12, right: 16, bottom: 54, left: 60 }
  const iW = W - m.left - m.right
  const iH = H - m.top  - m.bottom

  const svg = d3.select(el).append('svg').attr('width', W).attr('height', H)
    .append('g').attr('transform', `translate(${m.left},${m.top})`)

  const x = d3.scaleBand().domain(labels).range([0, iW]).padding(0.25)
  const y = d3.scaleLinear().domain([0, d3.max(values.map(v => +v)) * 1.12]).range([iH, 0])

  svg.append('g').call(d3.axisLeft(y).ticks(4).tickSize(-iW).tickFormat(''))
    .call(g => { g.select('.domain').remove(); g.selectAll('line').attr('stroke', T.grid) })

  svg.selectAll('.bar').data(labels).enter().append('rect')
    .attr('class', 'bar').attr('x', l => x(l)).attr('width', x.bandwidth())
    .attr('y', iH).attr('height', 0).attr('rx', 3)
    .attr('fill', color).attr('opacity', 0.85)
    .on('mouseover', function(event, l) {
      d3.select(this).attr('opacity', 1)
      const i = labels.indexOf(l)
      showTip(`<b>${l}</b><br>₱${Number(values[i]).toLocaleString()}`, event)
    })
    .on('mousemove', moveTip).on('mouseout', function() { d3.select(this).attr('opacity', 0.85); hideTip() })
    .transition().duration(600).ease(d3.easeCubicOut)
    .attr('y', l => { const i = labels.indexOf(l); return y(+values[i]) })
    .attr('height', l => { const i = labels.indexOf(l); return iH - y(+values[i]) })

  svg.append('g').attr('transform', `translate(0,${iH})`)
    .call(d3.axisBottom(x).tickSize(0))
    .call(g => {
      g.select('.domain').attr('stroke', T.grid)
      g.selectAll('text').attr('fill', T.text).attr('dy', '1.2em')
        .attr('transform', 'rotate(-22)').attr('text-anchor', 'end')
        .text(l => l.length > 12 ? l.slice(0, 11) + '…' : l)
    })

  svg.append('g').call(d3.axisLeft(y).ticks(4).tickFormat(v => `₱${d3.format('.2s')(v)}`))
    .call(g => { g.select('.domain').remove(); g.selectAll('text').attr('fill', T.text) })
}

// ─── Chart: Multi-series Area (Bank) ──────────────────────────────────────────

function drawBankChart(id, dates, debits, credits, balances) {
  if (!dates?.length) return showEmptyState(id)
  const T   = getTheme()
  const el  = document.getElementById(id)
  if (!el) return
  clearChart(id)

  const W  = el.clientWidth  || 600
  const H  = el.clientHeight || 240
  const m  = { top: 32, right: 16, bottom: 34, left: 62 }
  const iW = W - m.left - m.right
  const iH = H - m.top  - m.bottom

  const data = dates.map((d, i) => ({
    date: d, debit: +debits[i], credit: +credits[i], balance: +balances[i],
  }))

  const x     = d3.scalePoint().domain(dates).range([0, iW]).padding(0.05)
  const allVals = [...debits, ...credits, ...balances].map(v => +v)
  const y     = d3.scaleLinear().domain([d3.min(allVals) * 0.95, d3.max(allVals) * 1.08]).range([iH, 0])

  const svg = d3.select(el).append('svg').attr('width', W).attr('height', H)
    .append('g').attr('transform', `translate(${m.left},${m.top})`)

  // Defs for fills
  const defs = svg.append('defs')
  ;[
    { id: 'fillC', color: T.green },
    { id: 'fillD', color: T.rose  },
    { id: 'fillB', color: T.blue  },
  ].forEach(({ id: gId, color }) => {
    const g = defs.append('linearGradient').attr('id', gId).attr('x1','0').attr('y1','0').attr('x2','0').attr('y2','1')
    g.append('stop').attr('offset','0%').attr('stop-color', color).attr('stop-opacity', 0.18)
    g.append('stop').attr('offset','100%').attr('stop-color', color).attr('stop-opacity', 0.01)
  })

  svg.append('g').call(d3.axisLeft(y).ticks(4).tickSize(-iW).tickFormat(''))
    .call(g => { g.select('.domain').remove(); g.selectAll('line').attr('stroke', T.grid) })

  const areaFn = field => d3.area()
    .x(d => x(d.date)).y0(Math.min(iH, y(0))).y1(d => y(d[field])).curve(d3.curveCatmullRom)

  const lineFn = field => d3.line()
    .x(d => x(d.date)).y(d => y(d[field])).curve(d3.curveCatmullRom)

  ;[
    { field: 'credit',  fill: 'fillC', color: T.green, w: 1.5, label: 'Credit' },
    { field: 'debit',   fill: 'fillD', color: T.rose,  w: 1.5, label: 'Debit'  },
    { field: 'balance', fill: 'fillB', color: T.blue,  w: 2.5, label: 'Balance'},
  ].forEach(s => {
    svg.append('path').datum(data).attr('fill', `url(#${s.fill})`).attr('d', areaFn(s.field))

    const path = svg.append('path').datum(data)
      .attr('fill', 'none').attr('stroke', s.color).attr('stroke-width', s.w).attr('d', lineFn(s.field))

    const len = path.node().getTotalLength()
    path.attr('stroke-dasharray', len).attr('stroke-dashoffset', len)
      .transition().duration(900).ease(d3.easeCubicOut).attr('stroke-dashoffset', 0)
  })

  svg.append('g').attr('transform', `translate(0,${iH})`)
    .call(d3.axisBottom(x).tickValues(x.domain().filter((_, i) => i % Math.ceil(dates.length / 8) === 0)).tickSize(0))
    .call(g => { g.select('.domain').attr('stroke', T.grid); g.selectAll('text').attr('fill', T.text).attr('dy', '1.2em') })

  svg.append('g').call(d3.axisLeft(y).ticks(4).tickFormat(v => `₱${d3.format('.2s')(v)}`))
    .call(g => { g.select('.domain').remove(); g.selectAll('text').attr('fill', T.text) })

  // Legend
  const lg = svg.append('g').attr('transform', 'translate(0,-24)')
  ;[
    { color: T.green, label: 'Credit' },
    { color: T.rose,  label: 'Debit'  },
    { color: T.blue,  label: 'Balance'},
  ].forEach((s, i) => {
    const row = lg.append('g').attr('transform', `translate(${i * 90}, 0)`)
    row.append('line').attr('x1', 0).attr('y1', 5).attr('x2', 18).attr('y2', 5)
      .attr('stroke', s.color).attr('stroke-width', 2)
    row.append('text').attr('x', 22).attr('y', 9).attr('fill', T.text).attr('font-size', '10px').text(s.label)
  })

  // Hover overlay
  const bisect = d3.bisector(d => d.date).left
  svg.append('rect').attr('width', iW).attr('height', iH).attr('fill', 'none').attr('pointer-events', 'all')
    .on('mousemove', function(event) {
      const [mx] = d3.pointer(event)
      const domain = x.domain()
      const eachBand = iW / (domain.length - 1)
      const idx = Math.min(Math.round(mx / eachBand), domain.length - 1)
      const d = data[idx]
      if (!d) return
      showTip(
        `<b>${d.date}</b><br>Credit: ₱${d.credit.toLocaleString()}<br>Debit: ₱${d.debit.toLocaleString()}<br>Balance: ₱${d.balance.toLocaleString()}`,
        event
      )
    })
    .on('mouseout', hideTip)
}

// ─── Render All Charts ───────────────────────────────────────────────────────

function renderCharts() {
  const cd = chartsData.value
  const T  = getTheme()

  // Line charts
  const mObj  = normalizeObject(cd.monthlyData)
  drawLineChart('monthlyChart',       Object.keys(mObj),  Object.values(mObj),  T.blue)

  const dlObj = normalizeObject(cd.monthlyDownloads)
  drawLineChart('monthlyDownloadsChart', Object.keys(dlObj), Object.values(dlObj), T.green)

  // Donuts
  drawDonutChart('fundChart',   normalizeArray(cd.fundLabels),   normalizeArray(cd.fundValues))
  drawDonutChart('mooeChart',   normalizeArray(cd.mooeLabels),   normalizeArray(cd.mooeValues))
  drawDonutChart('chequeChart', normalizeArray(cd.chequeLabels), normalizeArray(cd.chequeCounts),
    v => Number(v).toLocaleString() + ' txns')

  // Grouped bar
  drawGroupedBarChart('budgetChart',
    normalizeArray(cd.budgetLabels),
    [
      { name: 'Budget',    values: normalizeArray(cd.budgetAmounts),   color: T.violet },
      { name: 'Disbursed', values: normalizeArray(cd.disburseAmounts), color: T.sky    },
    ]
  )

  // Horizontal bar
  drawHorizontalBarChart('expenseChart',
    normalizeArray(cd.expenseLabels), normalizeArray(cd.expenseValues), T.blue)

  // Vertical bars
  drawBarChart('supplierChart',  normalizeArray(cd.supplierLabels), normalizeArray(cd.supplierValues), T.amber)
  drawBarChart('districtChart',  normalizeArray(cd.districtLabels), normalizeArray(cd.districtValues), T.green)

  // Bank area
  drawBankChart('bankChart',
    normalizeArray(cd.bankDates), normalizeArray(cd.bankDebits),
    normalizeArray(cd.bankCredits), normalizeArray(cd.bankBalances))
}

// ─── Data Fetching ───────────────────────────────────────────────────────────

async function loadFilters() {
  try {
    const payload = await fetchDashboardFilters()
    yearOptions.value = (payload?.years || []).filter(y => Number.isFinite(Number(y))).sort((a, b) => Number(b) - Number(a))
    fundSourceOptions.value = payload?.fundSources || []
    divisionOptions.value   = payload?.divisions   || []
    if (!filterForm.value.year && yearOptions.value.length > 0) {
      filterForm.value.year = String(yearOptions.value[0])
    }
  } catch (error) {
    yearOptions.value = []
    fundSourceOptions.value = []
    divisionOptions.value = []
    console.error('Failed to load dashboard filters', error)
  }
}

async function applyFilters() {
  try {
    const params = getParams()
    const [kpiPayload, chartPayload] = await Promise.all([
      fetchDashboardKpis(params),
      fetchDashboardCharts(params),
    ])
    kpis.value = {
      totalBudget:           kpiPayload?.totalBudget           || 0,
      activeFunds:           kpiPayload?.activeFunds           || 0,
      activeBudget:          kpiPayload?.activeBudget          || 0,
      totalDisbursement:     kpiPayload?.totalDisbursement     || 0,
      remainingBalance:      kpiPayload?.remainingBalance      || 0,
      budgetUtilizationRate: kpiPayload?.budgetUtilizationRate || 0,
      totalTransactions:     kpiPayload?.totalTransactions     || 0,
      totalSuppliersPaid:    kpiPayload?.totalSuppliersPaid    || 0,
    }
    chartsData.value = chartPayload || {}
    await nextTick()
    renderCharts()
  } catch (error) {
    kpis.value = {
      totalBudget: 0,
      activeFunds: 0,
      activeBudget: 0,
      totalDisbursement: 0,
      remainingBalance: 0,
      budgetUtilizationRate: 0,
      totalTransactions: 0,
      totalSuppliersPaid: 0,
    }
    chartsData.value = {}
    await nextTick()
    renderCharts()
    console.error('Failed to load dashboard data', error)
  }
}

async function resetFilters() {
  filterForm.value.fund_source = ''
  filterForm.value.division    = ''
  filterForm.value.date_month  = ''
  await applyFilters()
}

// ─── Lifecycle ────────────────────────────────────────────────────────────────

onMounted(async () => {
  await loadFilters()
  await applyFilters()

  // Redraw charts on container resize
  resizeObserver = new ResizeObserver(() => renderCharts())
  const section  = document.querySelector('.charts-section')
  if (section) resizeObserver.observe(section)
})

onBeforeUnmount(() => {
  if (resizeObserver) resizeObserver.disconnect()
  hideTip()
})
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════════
   DASHBOARD PAGE — Enhanced UI Design
   Modern styling with improved visual hierarchy, animations, and accessibility
═══════════════════════════════════════════════════════════════════════════════ */

/* ── Dashboard Header ────────────────────────────────────────── */
.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-6);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
}

.dashboard-header h1 {
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  margin: var(--space-2) 0 var(--space-1);
}

.dashboard-header p {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
}

.header-eyebrow {
  display: inline-block;
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
  color: var(--brand-navy-600);
  margin-bottom: var(--space-1);
}

.header-controls {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.live-badge {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: rgba(16, 185, 129, 0.1);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.live-badge .dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  background: #10b981;
  animation: pulse-dot 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.btn-print {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--brand-gold-400);
  color: var(--brand-navy-900);
  border: none;
  border-radius: var(--radius-lg);
  font-weight: var(--weight-semibold);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out);
}

.btn-print:hover {
  background: var(--brand-gold-300);
  box-shadow: 0 8px 16px rgba(230, 162, 0, 0.2);
  transform: translateY(-2px);
}

.btn-print:active {
  transform: translateY(0);
}

/* ── Filter Bar ────────────────────────────────────────────── */
.filter-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--space-4);
  padding: var(--space-4);
  background: linear-gradient(135deg, var(--surface-base) 0%, var(--surface-subtle) 100%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  margin-bottom: var(--space-6);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.filter-group label {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-group select {
  padding: var(--space-2) var(--space-3);
  background: var(--surface-base);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.filter-group select:hover {
  border-color: var(--border-strong);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.filter-group select:focus {
  outline: none;
  border-color: var(--brand-navy-600);
  box-shadow: 0 0 0 3px rgba(46, 80, 128, 0.1);
}

.filter-actions {
  display: flex;
  gap: var(--space-3);
  grid-column: 1 / -1;
}

.btn-apply,
.btn-reset {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border: none;
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out);
  white-space: nowrap;
  flex: 1;
}

.btn-apply {
  background: var(--brand-navy-700);
  color: var(--text-inverse);
}

.btn-apply:hover {
  background: var(--brand-navy-600);
  box-shadow: 0 8px 16px rgba(46, 80, 128, 0.2);
  transform: translateY(-2px);
}

.btn-apply:active {
  transform: translateY(0);
}

.btn-reset {
  background: var(--surface-subtle);
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
}

.btn-reset:hover {
  background: var(--surface-raised);
  color: var(--text-primary);
  border-color: var(--border-strong);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* ── Summary Section ────────────────────────────────────────── */
.summary-section {
  margin-bottom: var(--space-6);
}

.section-title {
  font-size: var(--text-xl);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-4);
}

@media (min-width: 1280px) {
  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
}

/* ── Metric Cards ────────────────────────────────────────────── */
.metric-card {
  position: relative;
  padding: var(--space-5);
  background: var(--surface-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
  transition: all var(--duration-normal) var(--ease-out);
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: currentColor;
}

.metric-card:hover {
  border-color: var(--border-default);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px);
}

.metric-card.primary {
  color: var(--brand-navy-700);
  background: linear-gradient(135deg, rgba(46, 80, 128, 0.06) 0%, rgba(46, 80, 128, 0.02) 100%);
}

.metric-card.accent {
  color: var(--brand-gold-600);
  background: linear-gradient(135deg, rgba(230, 162, 0, 0.06) 0%, rgba(230, 162, 0, 0.02) 100%);
}

.metric-card.success {
  color: #10b981;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.06) 0%, rgba(16, 185, 129, 0.02) 100%);
}

.metric-card.warning {
  color: #f59e0b;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.06) 0%, rgba(245, 158, 11, 0.02) 100%);
}

.metric-card.info {
  color: #3b82f6;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.06) 0%, rgba(59, 130, 246, 0.02) 100%);
}

.metric-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-3);
}

.metric-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-lg);
  font-size: 1.5rem;
  opacity: 0.85;
}

.metric-label {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 var(--space-2);
}

.metric-value {
  font-size: clamp(1.5rem, 3vw, 2.25rem);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2);
  letter-spacing: -0.5px;
  line-height: 1.1;
}

.metric-value__suffix {
  font-size: 0.6em;
  opacity: 0.7;
  margin-left: var(--space-1);
  font-weight: var(--weight-semibold);
}

.metric-footer {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0;
}

/* ── Charts Section ─────────────────────────────────────────── */
.charts-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-4);
}

.charts-grid.two-col {
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
}

@media (max-width: 768px) {
  .charts-grid.two-col {
    grid-template-columns: 1fr;
  }
}

/* ── Chart Cards ────────────────────────────────────────────── */
.chart-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--surface-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  overflow: hidden;
  transition: all var(--duration-normal) var(--ease-out);
}

.chart-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(46, 80, 128, 0.02) 0%, transparent 100%);
  pointer-events: none;
  z-index: 0;
}

.chart-card:hover {
  border-color: var(--border-strong);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--border-subtle);
  position: relative;
  z-index: 1;
}

.chart-header-text h3 {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-1);
}

.chart-header-text p {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0;
}

.chart-badge {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
  background: var(--brand-gold-50);
  color: var(--brand-gold-800);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.chart-plot {
  width: 100%;
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
  overflow: visible;
}

.chart-plot svg {
  width: 100%;
  height: 100%;
  display: block;
  overflow: visible;
}

/* ── Empty State ────────────────────────────────────────────── */
:global(.chart-empty) {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 220px;
  width: 100%;
  color: var(--text-tertiary);
  font-size: var(--text-base);
  background: var(--surface-subtle);
  border-radius: var(--radius-lg);
  text-align: center;
  padding: var(--space-4);
}

/* ── Tooltip ────────────────────────────────────────────────── */
:global(.d3-tooltip) {
  position: fixed;
  z-index: 1001;
  pointer-events: none;
  background: var(--brand-navy-950);
  color: var(--text-inverse);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
  max-width: 240px;
  word-wrap: break-word;
  line-height: 1.4;
  border: 1px solid rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(12px);
  animation: tooltip-pop 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

:global(.d3-tooltip) b {
  display: block;
  font-weight: var(--weight-semibold);
  margin-bottom: var(--space-1);
  color: var(--brand-gold-300);
}

@keyframes tooltip-pop {
  from {
    opacity: 0;
    transform: scale(0.92) translateY(-6px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* ── D3 Grid & Axis Styles ────────────────────────────────────── */
:global(.d3-grid line) {
  stroke: var(--border-subtle);
  stroke-dasharray: 3 3;
  opacity: 0.5;
}

:global(.d3-grid .domain) {
  display: none;
}

/* ── Responsive Design ──────────────────────────────────────– */
@media (max-width: 1024px) {
  .filter-bar {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }

  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }

  .charts-grid.two-col {
    grid-template-columns: 1fr;
  }
}

/* ── Responsive Design ──────────────────────────────────────– */
@media (max-width: 1024px) {
  .filter-bar {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }

  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }

  .charts-grid.two-col {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-controls {
    flex-direction: column;
    width: 100%;
    gap: var(--space-2);
  }

  .btn-print,
  .live-badge {
    width: 100%;
    justify-content: center;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .filter-bar {
    grid-template-columns: 1fr;
  }

  .filter-actions {
    flex-direction: column;
  }

  .btn-apply,
  .btn-reset {
    flex: 1;
    width: 100%;
  }

  .chart-card {
    padding: var(--space-4);
  }

  .chart-header {
    flex-direction: column;
  }

  .chart-badge {
    align-self: flex-start;
  }
}

/* ── Quick Links Section ────────────────────────────────────── */
.quick-links-section {
  margin-top: var(--space-2);
  margin-bottom: var(--space-6);
}

.quick-links-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-3);
}

.quick-links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--space-3);
}

.quick-link-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-3);
  background: linear-gradient(135deg, var(--surface-base) 0%, var(--surface-subtle) 100%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  transition: all var(--duration-normal) var(--ease-out);
  cursor: pointer;
}

.quick-link-btn:hover {
  background: linear-gradient(135deg, var(--brand-gold-50) 0%, var(--surface-subtle) 100%);
  border-color: var(--brand-gold-300);
  color: var(--brand-gold-700);
  box-shadow: 0 8px 16px rgba(230, 162, 0, 0.1);
  transform: translateY(-2px);
}

.quick-link-btn i {
  font-size: 1.5rem;
}
</style>