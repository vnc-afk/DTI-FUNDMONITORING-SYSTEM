<template>
  <div class="master-fund-monitoring-page">
    <!-- Page Header -->
    <UiPageHeader
      title="Master Fund Monitoring"
      description="Track all fund monitoring records and transactions"
      eyebrow="Financial Tracking"
    >
      <UiButton v-if="canManageRecords" tag="router-link" to="/master-fund-monitoring/new" variant="primary">
        <ui-icon name="plus" size="16" />
        Add Record
      </UiButton>
    </UiPageHeader>

    <!-- Summary Cards -->
    <UiSummaryCards
      v-if="summaryCards.length"
      :cards="summaryCards"
    />

    <!-- Toolbar & Filtering -->
    <div class="search-toolbar">
      <SearchInput
        v-model="query"
        placeholder="Search records..."
        @search="loadRecords(1)"
        @clear="handleClear"
      />

      <FilterChips
        v-model="chequeStatusFilter"
        :chips="chequeStatusFilterOptions"
      />

      <UiButton
        v-if="isSearching"
        variant="secondary"
        @click="handleClear"
      >
        Clear Filters
      </UiButton>

      <UiButton
        variant="secondary"
        :disabled="loading"
        @click="refreshCurrentPage"
      >
        <ui-icon name="rotate-cw" size="14" />
        Refresh
      </UiButton>

      <UiButton
        variant="secondary"
        :disabled="loading || !records.length"
        @click="exportRecords"
      >
        <ui-icon name="download" size="14" />
        Export
      </UiButton>

      <UiButton
        v-if="canManageRecords && records.length"
        variant="secondary"
        @click="openBulkDeleteModal"
      >
        Delete All
      </UiButton>
    </div>

    <!-- Delete Confirmation Modal -->
    <DeleteConfirmModal
      ref="deleteModal"
      :title="deleteModalTitle"
      :message="deleteModalMessage"
      :details="deleteModalDetails"
      :is-loading="confirmBusy"
      :confirm-label="deleteConfirmLabel"
      cancel-label="Cancel"
      @confirm="confirmPendingAction"
      @close="resetDeleteModal"
    />

    <!-- Loading State -->
    <LoadingState v-if="loading" message="Loading master fund records..." />

    <!-- Empty State -->
    <EmptyState
      v-else-if="!records.length"
      icon="credit-card"
      title="No records found"
      description="Start by adding your first record or clear your active filters to see matching records."
    >
      <template #actions>
        <UiButton v-if="canManageRecords" tag="router-link" to="/master-fund-monitoring/new" variant="primary">Add Record</UiButton>
        <UiButton v-if="isSearching" variant="secondary" @click="handleClear">
          Clear Filters
        </UiButton>
      </template>
    </EmptyState>

    <!-- Data Table with Expandable Rows -->
    <div v-else class="table-container">
      <div class="data-table-wrapper">
        <table class="data-table">
        <thead>
          <tr>
            <th width="124px" :class="{ sorted: sortBy === 'date' }">
              <button type="button" class="sort-header" @click="setSort('date')">
                Date
                <span class="sort-indicator">{{ sortIndicator('date') }}</span>
              </button>
            </th>
            <th :class="{ sorted: sortBy === 'fund_source' }">
              <button type="button" class="sort-header" @click="setSort('fund_source')">
                Fund Source
                <span class="sort-indicator">{{ sortIndicator('fund_source') }}</span>
              </button>
            </th>
            <th :class="{ sorted: sortBy === 'payee' }">
              <button type="button" class="sort-header" @click="setSort('payee')">
                Payee
                <span class="sort-indicator">{{ sortIndicator('payee') }}</span>
              </button>
            </th>
            <th :class="{ sorted: sortBy === 'particulars' }">
              <button type="button" class="sort-header" @click="setSort('particulars')">
                Particulars
                <span class="sort-indicator">{{ sortIndicator('particulars') }}</span>
              </button>
            </th>
            <th width="104px" class="text-right" :class="{ sorted: sortBy === 'payments' }">
              <button type="button" class="sort-header sort-header-right" @click="setSort('payments')">
                Payment
                <span class="sort-indicator">{{ sortIndicator('payments') }}</span>
              </button>
            </th>
            <th width="104px" class="text-right" :class="{ sorted: sortBy === 'downloads' }">
              <button type="button" class="sort-header sort-header-right" @click="setSort('downloads')">
                Downloads
                <span class="sort-indicator">{{ sortIndicator('downloads') }}</span>
              </button>
            </th>
            <th width="88px" :class="{ sorted: sortBy === 'cheque_number' }">
              <button type="button" class="sort-header" @click="setSort('cheque_number')">
                Cheque No.
                <span class="sort-indicator">{{ sortIndicator('cheque_number') }}</span>
              </button>
            </th>
            <th width="98px" :class="{ sorted: sortBy === 'cheque_status' }">
              <button type="button" class="sort-header" @click="setSort('cheque_status')">
                Cheque Status
                <span class="sort-indicator">{{ sortIndicator('cheque_status') }}</span>
              </button>
            </th>
            <th v-if="canManageRecords" width="120px">Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="record in sortedRecords" :key="record.id">
            <!-- Main Data Row -->
            <tr class="data-row" :data-id="record.id" :data-status="rowStatusTag(record)">
              <td class="expand-cell">
                <button
                  type="button"
                  class="expand-btn"
                  @click="toggleExpanded(record.id)"
                  :aria-expanded="expandedRows.has(record.id)"
                  :aria-label="`${expandedRows.has(record.id) ? 'Collapse' : 'Expand'} details for ${record.fund_source_name || record.fund_source}`"
                >
                  <ui-icon name="chevron-down" size="16" />
                </button>
                <div class="cell-date">
                  <div v-if="record.date" class="date-label">{{ formatDate(record.date) }}</div>
                  <div v-if="record.date" class="date-day">{{ formatDay(record.date) }}</div>
                  <div v-if="!record.date" class="text-muted">—</div>
                </div>
              </td>
              <td>
                <span class="block truncate">{{ displayValue(record.fund_source_name || record.fund_source) }}</span>
              </td>
              <td>
                <span class="block truncate">{{ displayValue(record.payee_name || record.payee) }}</span>
              </td>
              <td>
                <div class="cell-description">
                  <div class="desc-text truncate" :title="record.particulars">{{ displayValue(record.particulars) }}</div>
                </div>
              </td>
              <td class="numeric">
                <span v-if="record.payments > 0" class="amount-debit">₱ {{ formatCurrencyRaw(record.payments) }}</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td class="numeric">
                <span v-if="record.downloads > 0" class="amount-credit">₱ {{ formatCurrencyRaw(record.downloads) }}</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td>
                <span class="font-mono tabular-nums">{{ displayValue(record.cheque_number) }}</span>
              </td>
              <td>
                <UiBadge
                  :text="statusBadgeText(record)"
                  :variant="statusBadgeVariant(record)"
                  size="sm"
                />
              </td>
              <td v-if="canManageRecords">
                <div class="action-buttons">
                  <ActionButton
                    v-if="!isRecordCancelled(record)"
                    tag="router-link"
                    variant="primary"
                    :to="`/master-fund-monitoring/${record.id}/edit`"
                    title="Edit record"
                  >
                    <ui-icon name="edit" size="18" />
                  </ActionButton>
                  <ActionButton
                    v-if="isRecordCancelled(record)"
                    variant="success"
                    title="Uncancel record"
                    @click="uncancelRecord(record)"
                  >
                    <ui-icon name="undo-2" size="18" />
                  </ActionButton>
                  <ActionButton
                    v-else
                    variant="secondary"
                    title="Cancel record"
                    @click="cancelRecord(record)"
                  >
                    <ui-icon name="x-circle" size="18" />
                  </ActionButton>
                  <ActionButton
                    variant="danger"
                    title="Delete record"
                    @click="openDeleteModal(record)"
                  >
                    <ui-icon name="trash-2" size="18" />
                  </ActionButton>
                </div>
              </td>
            </tr>

            <!-- Detail Row (Expandable Section) -->
            <tr v-if="expandedRows.has(record.id)" class="detail-row" :data-id="record.id">
              <td :colspan="canManageRecords ? 9 : 8">
                <div class="detail-inner">
                  <div class="detail-content">
                    <!-- Transaction Details Section -->
                    <div class="detail-section">
                      <div class="detail-section-header">
                        <h4 class="detail-section-title">
                          <ui-icon name="info" size="16" />
                          Transaction Details
                        </h4>
                      </div>
                      <div class="detail-grid">
                        <div class="detail-item">
                          <div class="detail-label">Division</div>
                          <div class="detail-value">{{ displayValue(record.division_name || record.division) }}</div>
                        </div>
                        <div class="detail-item">
                          <div class="detail-label">MOOE</div>
                          <div class="detail-value">{{ displayValue(record.mooe) }}</div>
                        </div>
                        <div class="detail-item">
                          <div class="detail-label">Negosyo Center</div>
                          <div class="detail-value">{{ displayValue(record.nc_name || record.nc) }}</div>
                        </div>
                        <div class="detail-item">
                          <div class="detail-label">Responsible Staff</div>
                          <div class="detail-value">{{ displayValue(record.staff_name || record.staff) }}</div>
                        </div>
                        <div class="detail-item full-width">
                          <div class="detail-label">Particulars</div>
                          <div class="detail-value text-wrap">{{ displayValue(record.particulars) }}</div>
                        </div>
                      </div>
                    </div>

                    <!-- DV and Clearance Section -->
                    <div class="detail-section">
                      <div class="detail-section-header">
                        <h4 class="detail-section-title">
                          <ui-icon name="check-circle" size="16" />
                          DV No. &amp; Clearance Information
                        </h4>
                      </div>
                      <div class="detail-grid">
                        <div class="detail-item">
                          <div class="detail-label">DV No.</div>
                          <div class="detail-value currency font-mono tabular-nums">
                            {{ record.dv_number ? `₱ ${formatCurrencyRaw(record.dv_number)}` : '—' }}
                          </div>
                        </div>
                        <div class="detail-item">
                          <div class="detail-label">Cleared Date</div>
                          <div class="detail-value">{{ record.cleared_date ? formatDate(record.cleared_date) : '—' }}</div>
                        </div>
                      </div>
                    </div>

                    <!-- Account & Expense Section -->
                    <div class="detail-section">
                      <div class="detail-section-header">
                        <h4 class="detail-section-title">
                          <ui-icon name="notebook-tabs" size="16" />
                          Account &amp; Expense
                        </h4>
                      </div>
                      <div class="detail-grid">
                        <div class="detail-item">
                          <div class="detail-label">Account Title</div>
                          <div class="detail-value">{{ displayValue(record.account_title_name || record.account_title) }}</div>
                        </div>
                        <div class="detail-item">
                          <div class="detail-label">Classification</div>
                          <div class="detail-value">{{ displayValue(record.expense_classification_name || record.expense_classification) }}</div>
                        </div>
                      </div>
                    </div>

                    <!-- Tax Information Section -->
                    <div class="detail-section">
                      <div class="detail-section-header">
                        <h4 class="detail-section-title">
                          <ui-icon name="ticket-check" size="16" />
                          Tax Information
                        </h4>
                      </div>
                      <div class="detail-grid">
                        <div class="detail-item">
                          <div class="detail-label">TIN</div>
                          <div class="detail-value">{{ displayValue(record.tin) }}</div>
                        </div>
                        <div class="detail-item">
                          <div class="detail-label">Tax Type</div>
                          <div class="detail-value">{{ displayValue(record.tax_type) }}</div>
                        </div>
                        <div class="detail-item">
                          <div class="detail-label">Purchase Type</div>
                          <div class="detail-value">{{ displayValue(record.purchase_type_name || record.purchase_type) }}</div>
                        </div>
                      </div>
                    </div>

                    <!-- Primary Tax Breakdown -->
                    <div class="detail-section">
                      <div class="detail-section-header">
                        <h4 class="detail-section-title">
                          <ui-icon name="receipt-text" size="16" />
                          Tax Breakdown ({{ displayValue(record.purchase_type_name || 'Purchase Type') }})
                        </h4>
                      </div>
                      <div class="detail-grid detail-grid-tax">
                        <div class="detail-item" v-for="field in primaryTaxFields" :key="field.key">
                          <div class="detail-label">{{ field.label }}</div>
                          <div class="detail-value currency">
                            {{ record[field.key] && record[field.key] > 0 ? `₱ ${formatCurrencyRaw(record[field.key])}` : '—' }}
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Manual Tax Breakdown -->
                    <div class="detail-section">
                      <div class="detail-section-header">
                        <h4 class="detail-section-title">
                          <ui-icon name="receipt-text" size="16" />
                          Manual Tax Breakdown
                        </h4>
                      </div>
                      <div class="detail-grid detail-grid-tax">
                        <div class="detail-item" v-for="field in manualTaxFields" :key="field.key">
                          <div class="detail-label">{{ field.label }}</div>
                          <div class="detail-value currency">
                            {{ record[field.key] && record[field.key] > 0 ? `₱ ${formatCurrencyRaw(record[field.key])}` : '—' }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination Footer -->
    <UiTableFooter
      v-if="records.length"
      :current-page="page"
      :page-size="pageSize"
      :total-items="totalRecords"
      @prev-page="changePage(page - 1)"
      @next-page="changePage(page + 1)"
    />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import UiPageHeader from '@/components/ui/UiPageHeader.vue'
import UiSummaryCards from '@/components/ui/UiSummaryCards.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import UiTableFooter from '@/components/ui/UiTableFooter.vue'
import DeleteConfirmModal from '@/components/ui/DeleteConfirmModal.vue'
import ActionButton from '@/components/ui/ActionButton.vue'
import SearchInput from '@/components/ui/SearchInput.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import FilterChips from '@/components/ui/FilterChips.vue'
import ExcelJS from 'exceljs'
import { subscribeToArchiveUpdates } from '@/utils/archiveRefresh'
import { canManageRecords as canManageRecordsAccess } from '@/utils/roleAccess'
import { downloadWorkbook } from '@/utils/excelExport'
import { useNotificationsStore } from '@/stores/notificationsStore'
import {
  cancelMasterFundMonitoringRecord,
  bulkDeleteMasterFundMonitoringRecords,
  deleteMasterFundMonitoringRecord,
  fetchMasterFundMonitoringRecords,
  uncancelMasterFundMonitoringRecord,
} from '@/services/masterFundMonitoringService'

const notificationsStore = useNotificationsStore()
const deleteModal = ref(null)
const canManageRecords = canManageRecordsAccess()

// Core state
const loading = ref(false)
const page = ref(1)
const records = ref([])
const query = ref('')
const chequeStatusFilter = ref('')
const expandedRows = ref(new Set())
const sortBy = ref('date')
const sortDir = ref('desc')
const totalRecords = ref(0)
const totalPages = ref(1)
const currentPageSize = ref(20)
const confirmBusy = ref(false)

// Delete modal state
const pendingDeleteId = ref(null)
const pendingDeleteIds = ref([])
const deleteModalTitle = ref('Delete Record')
const deleteModalMessage = ref('')
const deleteModalDetails = ref('')
const deleteConfirmLabel = ref('Delete Record')
const isBulkDelete = ref(false)
let unsubscribeArchiveUpdates = null
let searchDebounceTimer = null
let skipNextAutoReloadCount = 0

// Constants
const pageSize = computed(() => currentPageSize.value)
const chequeStatusFilterOptions = [
  { value: 'Pending', label: 'Pending' },
  { value: 'Cleared', label: 'Cleared' },
  { value: 'Cancelled', label: 'Cancelled' },
]
const primaryTaxFields = [
  { key: 'goods_5_percent', label: 'Goods 5%' },
  { key: 'services_5_percent', label: 'Services 5%' },
  { key: 'goods_services_3_percent', label: 'Goods/Services 3%' },
  { key: 'goods_1_percent', label: 'Goods 1%' },
  { key: 'services_2_percent', label: 'Services 2%' },
  { key: 'rental_5_percent', label: 'Rental 5%' },
  { key: 'prof_fee_10_percent', label: 'Prof. Fee 10%' },
]
const manualTaxFields = [
  { key: 'goods_5_percent_2', label: 'Goods 5% (2)' },
  { key: 'services_5_percent_2', label: 'Services 5% (2)' },
  { key: 'goods_services_1_percent', label: 'Goods/Services 1%' },
  { key: 'goods_1_percent_2', label: 'Goods 1% (2)' },
  { key: 'services_2_percent_2', label: 'Services 2% (2)' },
  { key: 'rental_5_percent_2', label: 'Rental 5% (2)' },
  { key: 'prof_fee_10_percent_2', label: 'Prof. Fee 10% (2)' },
]

const sortedRecords = computed(() => {
  const direction = sortDir.value === 'asc' ? 1 : -1
  return [...records.value].sort((left, right) => {
    const leftValue = getSortValue(left, sortBy.value)
    const rightValue = getSortValue(right, sortBy.value)
    return direction * compareSortValues(leftValue, rightValue)
  })
})

const isSearching = computed(() => Boolean(query.value.trim() || chequeStatusFilter.value))

const totalPayments = ref(0)
const totalDownloads = ref(0)

const summaryCards = computed(() => [
  {
    id: 'payments',
    label: 'Total Payments',
    value: `₱ ${formatCurrencyRaw(totalPayments.value)}`,
    accentColor: 'var(--status-danger)',
    iconBg: 'var(--status-danger-bg)',
    iconColor: 'var(--status-danger)',
  },
  {
    id: 'downloads',
    label: 'Total Downloads',
    value: `₱ ${formatCurrencyRaw(totalDownloads.value)}`,
    accentColor: 'var(--status-success)',
    iconBg: 'var(--status-success-bg)',
    iconColor: 'var(--status-success)',
  },
  {
    id: 'records',
    label: 'Total Records',
    value: totalRecords.value,
    accentColor: 'var(--brand-navy-600)',
    iconBg: 'var(--brand-navy-50)',
    iconColor: 'var(--brand-navy-600)',
  },
])

// Notifications
function pushErrorToast(message) {
  notificationsStore.pushToast({
    title: 'Master Fund Monitoring',
    message,
    variant: 'danger',
  })
}

function pushSuccessToast(message) {
  notificationsStore.pushToast({
    title: 'Master Fund Monitoring',
    message,
    variant: 'success',
  })
}

// Data loading
async function loadRecords(targetPage = 1) {
  loading.value = true
  try {
    const response = await fetchMasterFundMonitoringRecords({
      page: targetPage,
      includeCancelled: true,
      chequeStatus: chequeStatusFilter.value,
      pageSize: pageSize.value,
      query: query.value,
    })

    records.value = response.records || []
    page.value = response.pagination?.page || targetPage
    currentPageSize.value = response.pagination?.page_size || currentPageSize.value
    totalPages.value = response.pagination?.pages || 1
    totalRecords.value = response.pagination?.count ?? response.pagination?.total ?? records.value.length
    totalPayments.value = Number(response.totalPayments || 0)
    totalDownloads.value = Number(response.totalDownloads || 0)
    expandedRows.value = new Set()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to fetch records.')
    records.value = []
    totalRecords.value = 0
    totalPayments.value = 0
    totalDownloads.value = 0
  } finally {
    loading.value = false
  }
}

// Filtering and expansion
function toggleStatusFilter(value) {
  chequeStatusFilter.value = chequeStatusFilter.value === value ? '' : value
}

function toggleExpanded(recordId) {
  if (expandedRows.value.has(recordId)) {
    expandedRows.value.delete(recordId)
  } else {
    expandedRows.value.add(recordId)
  }
  expandedRows.value = new Set(expandedRows.value)
}

function setSort(column) {
  if (sortBy.value === column) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
    return
  }
  sortBy.value = column
  sortDir.value = 'asc'
}

function sortIndicator(column) {
  if (sortBy.value !== column) return '<>'
  return sortDir.value === 'asc' ? '^' : 'v'
}

function handleSearchChange() {
  loadRecords(1)
}

function handleClear() {
  skipNextAutoReloadCount = 2
  query.value = ''
  chequeStatusFilter.value = ''
  loadRecords(1)
}

function refreshCurrentPage() {
  loadRecords(page.value)
}

function isRecordCancelled(record) {
  return Boolean(record?.is_cancelled)
}

function getDisplayChequeStatus(record) {
  if (isRecordCancelled(record)) {
    return 'Cancelled'
  }

  const normalizedStatus = String(record?.cheque_status || '').trim()
  if (!normalizedStatus) {
    return 'Pending'
  }

  if (normalizedStatus.toLowerCase() === 'cleared') {
    return 'Cleared'
  }

  if (normalizedStatus.toLowerCase() === 'pending') {
    return 'Pending'
  }

  return normalizedStatus
}

function statusBadgeText(record) {
  return getDisplayChequeStatus(record)
}

function statusBadgeVariant(record) {
  const displayStatus = getDisplayChequeStatus(record)
  if (displayStatus === 'Cancelled') return 'warning'
  if (displayStatus === 'Cleared') return 'success'
  return 'info'
}

async function exportRecords() {
  if (!sortedRecords.value.length) {
    pushErrorToast('No records to export.')
    return
  }

  try {
    const workbook = new ExcelJS.Workbook()
    const worksheet = workbook.addWorksheet('Master Fund Monitoring')

    worksheet.addRow([
      'Date',
      'Fund Source',
      'Payee',
      'Particulars',
      'Payments',
      'Downloads',
      'Cheque Number',
      'Cheque Status',
      'DV Number',
      'Division',
      'MOOE',
      'Negosyo Center',
      'Responsible Staff',
    ])

    sortedRecords.value.forEach((record) => {
      worksheet.addRow([
        record.date ? formatDate(record.date) : '',
        record.fund_source_name || record.fund_source || '',
        record.payee_name || record.payee || '',
        record.particulars || '',
        Number(record.payments || 0),
        Number(record.downloads || 0),
        record.cheque_number || '',
        record.cheque_status || '',
        record.dv_number || '',
        record.division_name || record.division || '',
        record.mooe || '',
        record.nc_name || record.nc || '',
        record.staff_name || record.staff || '',
      ])
    })

    const fileDate = new Date().toISOString().split('T')[0]
    await downloadWorkbook(workbook, `Master_Fund_Monitoring_${fileDate}.xlsx`)
    pushSuccessToast('Master fund monitoring records exported successfully.')
  } catch (error) {
    pushErrorToast(error.message || 'Failed to export records.')
  }
}

function changePage(nextPage) {
  if (nextPage < 1 || nextPage > totalPages.value) {
    return
  }
  loadRecords(nextPage)
}

// Delete modal management
function openDeleteModal(record) {
  pendingDeleteId.value = record.id
  pendingDeleteIds.value = [record.id]
  isBulkDelete.value = false
  deleteModalTitle.value = 'Delete Record'
  deleteConfirmLabel.value = 'Delete Record'
  deleteModalMessage.value = `Are you sure you want to delete this record?`
  deleteModalDetails.value = `${displayValue(record.fund_source_name || record.fund_source)} - ${displayValue(record.particulars)}`
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

function openBulkDeleteModal() {
  const ids = records.value.map((record) => record.id)
  if (!ids.length) return

  pendingDeleteIds.value = ids
  isBulkDelete.value = true
  deleteModalTitle.value = 'Delete Records'
  deleteConfirmLabel.value = 'Delete All'
  deleteModalMessage.value = `Delete ${ids.length} record${ids.length === 1 ? '' : 's'} from this page? This action cannot be undone.`
  deleteModalDetails.value = `${ids.length} record${ids.length === 1 ? '' : 's'} will be permanently deleted.`
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

function resetDeleteModal() {
  pendingDeleteId.value = null
  pendingDeleteIds.value = []
  isBulkDelete.value = false
  deleteModalTitle.value = 'Delete Record'
  deleteConfirmLabel.value = 'Delete Record'
  deleteModalMessage.value = ''
  deleteModalDetails.value = ''
}

async function confirmPendingAction() {
  if (isBulkDelete.value) {
    await bulkDelete()
  } else {
    await deleteRecord()
  }
}

async function deleteRecord() {
  if (!pendingDeleteId.value) {
    return
  }

  confirmBusy.value = true

  try {
    await deleteMasterFundMonitoringRecord(pendingDeleteId.value)
    await loadRecords(page.value)
    pushSuccessToast('Record deleted successfully.')

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to delete record.')
  } finally {
    confirmBusy.value = false
  }
}

async function bulkDelete() {
  if (!pendingDeleteIds.value.length) {
    return
  }

  confirmBusy.value = true

  try {
    await bulkDeleteMasterFundMonitoringRecords(pendingDeleteIds.value)
    await loadRecords(page.value)
    pushSuccessToast(`${pendingDeleteIds.value.length} record${pendingDeleteIds.value.length === 1 ? '' : 's'} deleted.`)

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to bulk delete records.')
  } finally {
    confirmBusy.value = false
  }
}

async function cancelRecord(record) {
  try {
    await cancelMasterFundMonitoringRecord(record.id)
    await loadRecords(page.value)
    pushSuccessToast('Record cancelled successfully.')
  } catch (error) {
    pushErrorToast(error.message || 'Failed to cancel record.')
  }
}

async function uncancelRecord(record) {
  try {
    await uncancelMasterFundMonitoringRecord(record.id)
    await loadRecords(page.value)
    pushSuccessToast('Record uncancelled successfully.')
  } catch (error) {
    pushErrorToast(error.message || 'Failed to uncancel record.')
  }
}

// Display utilities
function displayValue(value) {
  if (value === null || value === undefined || value === '') return '—'
  if (typeof value === 'string' && ['nan', 'none', 'null', '<na>'].includes(value.trim().toLowerCase())) {
    return '—'
  }
  return value
}

function formatCurrencyRaw(value) {
  const numberValue = Number(value || 0)
  return numberValue.toLocaleString('en-PH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function formatDate(dateValue) {
  const date = new Date(dateValue)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: '2-digit',
    year: 'numeric',
  }).format(date)
}

function formatDay(dateValue) {
  const date = new Date(dateValue)
  return new Intl.DateTimeFormat('en-US', { weekday: 'long' }).format(date)
}

function chequeStatusTag(status) {
  if (status === 'Cleared') return 'cleared'
  if (status === 'Pending') return 'pending'
  if (status === 'Cancelled') return 'cancelled'
  return 'unknown'
}

function rowStatusTag(record) {
  return chequeStatusTag(getDisplayChequeStatus(record))
}

function getSortValue(record, column) {
  if (column === 'date') {
    const dateValue = record?.date ? new Date(record.date).getTime() : Number.NaN
    return Number.isNaN(dateValue) ? 0 : dateValue
  }

  if (column === 'fund_source') {
    return String(record?.fund_source_name || record?.fund_source || '')
  }

  if (column === 'payee') {
    return String(record?.payee_name || record?.payee || '')
  }

  if (column === 'particulars') {
    return String(record?.particulars || '')
  }

  if (column === 'payments') {
    return Number(record?.payments || 0)
  }

  if (column === 'downloads') {
    return Number(record?.downloads || 0)
  }

  if (column === 'cheque_number') {
    return String(record?.cheque_number || '')
  }

  if (column === 'cheque_status') {
    return getDisplayChequeStatus(record)
  }

  return ''
}

function compareSortValues(left, right) {
  if (typeof left === 'number' && typeof right === 'number') {
    return left - right
  }

  return String(left).localeCompare(String(right), undefined, {
    numeric: true,
    sensitivity: 'base',
  })
}

// Lifecycle
onMounted(() => {
  loadRecords(1)
  unsubscribeArchiveUpdates = subscribeToArchiveUpdates(() => {
    loadRecords(page.value)
  })
})

watch(
  () => chequeStatusFilter.value,
  () => {
    if (skipNextAutoReloadCount > 0) {
      skipNextAutoReloadCount -= 1
      return
    }

    if (searchDebounceTimer) {
      clearTimeout(searchDebounceTimer)
    }

    searchDebounceTimer = setTimeout(() => {
      loadRecords(1)
    }, 250)
  },
)

watch(
  () => query.value,
  () => {
    if (skipNextAutoReloadCount > 0) {
      skipNextAutoReloadCount -= 1
      return
    }

    if (searchDebounceTimer) {
      clearTimeout(searchDebounceTimer)
    }

    searchDebounceTimer = setTimeout(() => {
      loadRecords(1)
    }, 250)
  },
)

onBeforeUnmount(() => {
  if (unsubscribeArchiveUpdates) {
    unsubscribeArchiveUpdates()
    unsubscribeArchiveUpdates = null
  }

  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = null
  }
})
</script>

<style scoped>
.sort-header {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.4rem;
  border: none;
  background: transparent;
  color: inherit;
  font: inherit;
  font-weight: 600;
  padding: 0;
  cursor: pointer;
}

.sort-header-right {
  justify-content: flex-end;
}

.sort-indicator {
  display: inline-block;
  min-width: 1rem;
  color: var(--text-muted);
  text-align: center;
}

th.sorted .sort-indicator {
  color: var(--brand-navy-600);
}
</style>
