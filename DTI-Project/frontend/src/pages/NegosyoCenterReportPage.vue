<template>
  <ReportPageLayout root-class="report" :title="'Negosyo Center Report'" :description="`Fiscal Year ${currentYear} · All figures in PHP`">
    <template #header-actions>
      <button id="btn-print" class="btn btn-outline" type="button" @click="printPage">
        <ui-icon name="printer" size="18" /> Print
      </button>
      <button id="btn-export" class="btn btn-primary" type="button" @click="exportAll">
        <ui-icon name="download" size="18" /> Export All
      </button>
    </template>

      <div class="section-title">Budget Summary</div>
      <div class="summary-cards">
        <div class="scard report-row-budget">
          <div class="scard-label">Annual Budget (Negosyo Center)</div>
          <div class="scard-amount">{{ formatCurrency(annualBudget) }}</div>
          <div class="scard-pct">All Funds</div>
        </div>
        <div class="scard report-row-disburse">
          <div class="scard-label">Total Disbursement</div>
          <div class="scard-amount">{{ formatCurrency(totalDisbursement) }}</div>
        </div>
        <div class="scard report-row-balance">
          <div class="scard-label">Annual Balance</div>
          <div class="scard-amount">{{ formatCurrency(currentBalance) }}</div>
          <div class="scard-pct">Remaining Budget</div>
        </div>
        <div class="scard report-row-bur">
          <div class="scard-label">BUR (Annual)</div>
          <div class="scard-amount">{{ burRate.toFixed(1) }}%</div>
          <div class="scard-pct">Current Period</div>
        </div>
      </div>
      <div class="section-title">District Allocation</div>
      <div class="filter-bar">
        <div class="flex-1"></div>
        <button id="open-all-btn" type="button" class="filter-btn" @click="openAll" title="Expand all districts">
          <ui-icon name="expand" size="18"/> Open All
        </button>
        <button id="close-all-btn" type="button" class="filter-btn" @click="closeAll" title="Collapse all districts">
          <ui-icon name="shrink" size="18"/> Close All
        </button>
      </div>

    <div id="districts-accordion" class="quarterly-acc">
      <div
        v-for="district in districts"
        :key="districtKey(district)"
        class="acc-item"
        :class="{ open: openDistricts[districtKey(district)] }"
      >
        <div class="acc-header" @click="toggleDistrict(district)">
          <div class="acc-header-left">
            <ui-icon name="chevron-down" class="acc-chevron" />
            <div class="acc-title">{{ district.name }}</div>
          </div>
          <div class="acc-header-right">
            <div class="dist-total-container">
              <div class="dist-total-label">Annual Disbursement</div>
              <span class="dist-total">{{ formatCurrency(district.district_total) }}</span>
            </div>
          </div>
        </div>

        <div class="acc-body">
          <div
            v-for="(quarter, quarterIndex) in district.quarters"
            :key="`${districtKey(district)}-${quarter.label}`"
            class="acc-item acc-item--nested"
            :class="{ open: openQuarters[quarterKey(district, quarter)] }"
          >
            <div class="acc-header" @click.stop="toggleQuarter(district, quarter)">
              <div class="acc-header-left">
                <ui-icon name="chevron-down" class="acc-chevron" />
                <span class="q-badge" :class="`q${quarterIndex + 1}`">{{ quarter.label }}</span>
                <span class="q-range">{{ quarter.range }}</span>
              </div>
              <div class="acc-header-right">
                <span class="qtr-total">Qtr Total - {{ formatCurrency(quarter.total) }}</span>
              </div>
            </div>

            <div class="acc-body">
              <div class="table-wrap table-wrap-flat">
                <table class="quarterly-table">
                  <thead>
                    <tr>
                      <th>Month</th>
                      <th
                        v-for="center in district.negosyo_centers"
                        :key="`${districtKey(district)}-${quarter.label}-head-${center.id}`"
                      >
                        {{ center.name }}
                      </th>
                      <th>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="month in quarter.months"
                      :key="`${districtKey(district)}-${quarter.label}-${month.month_num}`"
                      class="month-row"
                    >
                      <td class="month-cell">
                        <span class="row-dot"></span>
                        <span class="month-label">{{ month.name }}</span>
                      </td>
                      <td
                        v-for="center in district.negosyo_centers"
                        :key="`${districtKey(district)}-${quarter.label}-${month.month_num}-${center.id}`"
                        class="fund-cell"
                        :data-center="center.id"
                        :data-value="toNumber(month.nc_data?.[center.id])"
                      >
                        {{ formatCurrency(month.nc_data?.[center.id]) }}
                      </td>
                      <td class="total-cell col-total">{{ formatCurrency(month.month_total) }}</td>
                    </tr>

                    <tr class="quarter-subtotal-row" :class="`q${quarterIndex + 1}`">
                      <td class="month-cell">Quarter Subtotal</td>
                      <td
                        v-for="center in district.negosyo_centers"
                        :key="`${districtKey(district)}-${quarter.label}-subtotal-${center.id}`"
                        class="fund-cell"
                      >
                        {{ formatCurrency(sumCenterQuarter(district, quarter, center.id)) }}
                      </td>
                      <td class="total-cell col-total">{{ formatCurrency(quarter.total) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
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
import { onMounted, reactive, ref } from 'vue'
import ReportPageLayout from '@/components/patterns/ReportPageLayout.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import { downloadWorkbook } from '@/utils/excelExport'
import { fetchNegosyoCenterReport } from '@/services/negosyoCenterReportService'

const currentYear = ref(new Date().getFullYear())
const districts = ref([])

const annualBudget = ref(0)
const totalDisbursement = ref(0)
const currentBalance = ref(0)
const burRate = ref(0)

const loadError = ref('')

const openDistricts = reactive({})
const openQuarters = reactive({})

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

function districtKey(district) {
  const orderPart = district?.order ?? ''
  const namePart = district?.name ?? ''
  return `${String(orderPart)}:${String(namePart)}`
}

function quarterKey(district, quarter) {
  return `${districtKey(district)}-${quarter?.label || ''}`
}

function toggleDistrict(district) {
  const key = districtKey(district)
  openDistricts[key] = !openDistricts[key]
}

function toggleQuarter(district, quarter) {
  const key = quarterKey(district, quarter)
  openQuarters[key] = !openQuarters[key]
}

function openAll() {
  districts.value.forEach((district) => {
    openDistricts[districtKey(district)] = true
    ;(district.quarters || []).forEach((quarter) => {
      openQuarters[quarterKey(district, quarter)] = true
    })
  })
}

function closeAll() {
  districts.value.forEach((district) => {
    openDistricts[districtKey(district)] = false
    ;(district.quarters || []).forEach((quarter) => {
      openQuarters[quarterKey(district, quarter)] = false
    })
  })
}

function sumCenterQuarter(district, quarter, centerId) {
  return (quarter?.months || []).reduce((sum, month) => {
    return sum + toNumber(month?.nc_data?.[centerId])
  }, 0)
}

function printPage() {
  window.print()
}

async function exportAll() {
  if (!districts.value.length) {
    return
  }

  const rows = []
  rows.push(['NEGOSYO CENTER REPORT - ALL DATA'])
  rows.push([`Fiscal Year ${currentYear.value}`])
  rows.push([''])

  districts.value.forEach((district) => {
    rows.push([`DISTRICT: ${district.name}`])
    rows.push(['Month', ...(district.negosyo_centers || []).map((center) => center.name), 'Total'])

    ;(district.quarters || []).forEach((quarter) => {
      ;(quarter.months || []).forEach((month) => {
        const row = [month.name]
        ;(district.negosyo_centers || []).forEach((center) => {
          row.push(toNumber(month?.nc_data?.[center.id]).toFixed(2))
        })
        row.push(toNumber(month.month_total).toFixed(2))
        rows.push(row)
      })
    })

    rows.push(['ANNUAL TOTAL', ...Array((district.negosyo_centers || []).length).fill(''), toNumber(district.district_total).toFixed(2)])
    rows.push([''])
  })

  const workbook = new ExcelJS.Workbook()
  workbook.addWorksheet('Negosyo Center Report').addRows(rows)

  await downloadWorkbook(workbook, `Negosyo_Center_Report_${new Date().toISOString().split('T')[0]}.xlsx`)
}

async function loadReport() {
  loadError.value = ''

  try {
    const data = await fetchNegosyoCenterReport()

    currentYear.value = toNumber(data?.current_year) || new Date().getFullYear()
    districts.value = Array.isArray(data?.districts) ? data.districts : []

    annualBudget.value = toNumber(data?.annualBudget)
    totalDisbursement.value = toNumber(data?.totalDisbursement)
    currentBalance.value = toNumber(data?.currentBalance)
    burRate.value = toNumber(data?.burRate)

    districts.value.forEach((district) => {
      openDistricts[districtKey(district)] = true
      ;(district.quarters || []).forEach((quarter) => {
        openQuarters[quarterKey(district, quarter)] = true
      })
    })
  } catch (error) {
    loadError.value = 'Unable to load Negosyo Center report data. Please try again.'
    districts.value = []
  }
}

onMounted(() => {
  loadReport()
})
</script>
