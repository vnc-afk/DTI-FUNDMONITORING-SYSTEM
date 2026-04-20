<template>
  <div class="bank-statements-page">
    <!-- Page Header -->
    <UiPageHeader
      title="Bank Statements"
      description="Track all debit, credit, and balance movements"
      eyebrow="Financial Records"
    >
      <UiButton v-if="canManageRecords" tag="router-link" to="/bank-statements/new" variant="primary">
        <ui-icon name="plus" size="16" />
        Add Statement
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
        placeholder="Search transactions..."
        @search="loadStatements(1)"
        @clear="handleClear"
      />

      <FilterChips
        v-model="statusFilter"
        :chips="normalizedStatusPills"
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
        :disabled="loading || !statements.length"
        @click="exportStatements"
      >
        <ui-icon name="download" size="14" />
        Export
      </UiButton>
    </div>

    <!-- Delete Confirmation Modal -->
    <DeleteConfirmModal
      ref="deleteModal"
      :title="deleteModalTitle"
      :message="deleteModalMessage"
      :details="deleteModalDetails"
      :is-loading="confirmBusy"
      confirm-label="Delete Statement"
      cancel-label="Cancel"
      @confirm="confirmDeleteStatement"
      @close="resetDeleteModal"
    />

    <!-- Loading State -->
    <LoadingState v-if="loading" message="Loading bank statements..." />

    <!-- Empty State -->
    <EmptyState
      v-else-if="!statements.length"
      icon="credit-card"
      title="No bank statements yet"
      description="Start by adding your first transaction or clear your active filters to see matching records."
    >
      <template #actions>
        <UiButton v-if="canManageRecords" tag="router-link" to="/bank-statements/new" variant="primary">Add Statement</UiButton>
        <UiButton v-if="isSearching" variant="secondary" @click="handleClear">
          Clear Filters
        </UiButton>
      </template>
    </EmptyState>

    <!-- Data Table -->
    <div v-else class="table-container">
      <UiTable
        :columns="tableColumns"
      :rows="tableRows"
      >
        <template #cell-date="{ value }">
          <div class="cell-date">
            <div class="date-label">{{ formatDate(value) }}</div>
            <div class="date-day">{{ formatDay(value) }}</div>
          </div>
        </template>

        <template #cell-description="{ row }">
          <div class="cell-description">
            <div class="desc-text">{{ row.description }}</div>
          </div>
        </template>

        <template #cell-check_number="{ value }">
          <span class="text-muted">{{ value || '—' }}</span>
        </template>

        <template #cell-debit="{ value }">
          <span class="amount-debit">₱ {{ formatCurrencyRaw(value) }}</span>
        </template>

        <template #cell-credit="{ value }">
          <span class="amount-credit">₱ {{ formatCurrencyRaw(value) }}</span>
        </template>

        <template #cell-balance="{ value }">
          <div class="balance-cell">
            <div class="balance-value">₱ {{ formatCurrencyRaw(value) }}</div>
            <div class="balance-bar">
              <div class="balance-fill" :style="{ width: balanceBarWidth({ balance: value }) + '%' }"></div>
            </div>
          </div>
        </template>

        <template #cell-status="{ value }">
          <UiBadge
            :text="value"
            :variant="value === 'Cleared' ? 'success' : 'warning'"
            size="sm"
          />
        </template>

        <template v-if="canManageRecords" #cell-actions="{ row }">
          <div class="action-buttons">
            <ActionButton
              v-if="row.status !== 'Cleared'"
              variant="success"
              title="Mark as cleared"
              @click="markAsCleared(row)"
            >
              <ui-icon name="square-check-big" size="18" />
            </ActionButton>
            <ActionButton
              tag="router-link"
              variant="primary"
              :to="`/bank-statements/${row.id}/edit`"
              title="Edit statement"
            >
              <ui-icon name="edit" size="18" />
            </ActionButton>
            <ActionButton
              variant="danger"
              title="Delete statement"
              @click="openDeleteModal(row)"
            >
              <ui-icon name="trash-2" size="18" />
            </ActionButton>
          </div>
        </template>
      </UiTable>
    </div>

    <!-- Pagination Footer -->
    <UiTableFooter
      v-if="statements.length"
      :current-page="page"
      :page-size="pageSize"
      :total-items="statementCount"
      @prev-page="changePage(page - 1)"
      @next-page="changePage(page + 1)"
    />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import UiPageHeader from '@/components/ui/UiPageHeader.vue'
import UiSummaryCards from '@/components/ui/UiSummaryCards.vue'
import UiTable from '@/components/ui/UiTable.vue'
import UiTableFooter from '@/components/ui/UiTableFooter.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import ActionButton from '@/components/ui/ActionButton.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import DeleteConfirmModal from '@/components/ui/DeleteConfirmModal.vue'
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
  bulkDeleteBankStatements,
  deleteBankStatement,
  fetchBankStatements,
  updateBankStatementStatus,
} from '@/services/bankStatementService'

const notificationsStore = useNotificationsStore()
const deleteModal = ref(null)
const canManageRecords = canManageRecordsAccess()

const loading = ref(false)
const query = ref('')
const statusFilter = ref('')
const page = ref(1)

const statements = ref([])
const statementCount = ref(0)
const currentPageSize = ref(20)
const totalDebits = ref(0)
const totalCredits = ref(0)
const statusFilterOptions = ref([
  { value: 'On Process', label: 'On Process' },
  { value: 'Cleared', label: 'Cleared' },
])

const totalPages = ref(1)
const confirmBusy = ref(false)
const pendingDeleteId = ref(null)
const deleteModalTitle = ref('Delete Bank Statement')
const deleteModalMessage = ref('')
const deleteModalDetails = ref('')
let unsubscribeArchiveUpdates = null
let searchDebounceTimer = null
let skipNextAutoReload = false

const isSearching = computed(() => Boolean(query.value.trim() || statusFilter.value))
const normalizedStatusPills = computed(() => {
  return statusFilterOptions.value
    .map((option) => ({
      value: String(option?.value || '').trim(),
      label: String(option?.label || option?.value || '').trim(),
    }))
    .filter((option) => option.value)
})

const maxVisibleBalance = computed(() => {
  if (!statements.value.length) {
    return 0
  }
  return statements.value.reduce((max, statement) => {
    return Math.max(max, Number(statement.balance || 0))
  }, 0)
})

const currentBalance = computed(() => {
  if (!statements.value.length) {
    return 0
  }
  return Number(statements.value[0].balance || 0)
})

const summaryCards = computed(() => [
  { 
    id: 'debits', 
    label: 'Total Debits', 
    value: `₱ ${formatCurrencyRaw(totalDebits.value)}`,
    accentColor: 'var(--status-danger-text)',
    iconBg: 'var(--status-danger-bg)',
    iconColor: 'var(--status-danger-text)',
  },
  { 
    id: 'credits', 
    label: 'Total Credits', 
    value: `₱ ${formatCurrencyRaw(totalCredits.value)}`,
    accentColor: 'var(--status-success-text)',
    iconBg: 'var(--status-success-bg)',
    iconColor: 'var(--status-success-text)',
  },
  { 
    id: 'balance', 
    label: 'Current Balance', 
    value: `₱ ${formatCurrencyRaw(currentBalance.value)}`,
    accentColor: 'var(--brand-gold-500)',
    iconBg: 'var(--brand-gold-50)',
    iconColor: 'var(--brand-gold-500)',
  },
  { 
    id: 'transactions', 
    label: 'Transactions', 
    value: statementCount.value,
    accentColor: 'var(--brand-navy-600)',
    iconBg: 'var(--brand-navy-50)',
    iconColor: 'var(--brand-navy-600)',
  },
])

const pageSize = computed(() => currentPageSize.value)

const tableColumns = computed(() => {
  const columns = [
    { id: 'date', label: 'Date', width: '120px' },
    { id: 'description', label: 'Description', width: 'flex' },
    { id: 'check_number', label: 'Check/Ref No.', width: '100px' },
    { id: 'debit', label: 'Debit (Out)', width: '120px', align: 'right' },
    { id: 'credit', label: 'Credit (In)', width: '120px', align: 'right' },
    { id: 'balance', label: 'Balance', width: '130px', align: 'right' },
    { id: 'status', label: 'Status', width: '100px' },
  ]
  if (canManageRecords) {
    columns.push({ id: 'actions', label: 'Actions', width: '110px' })
  }
  return columns
})

const tableRows = computed(() => {
  return statements.value.map((statement) => ({
    id: statement.id,
    date: statement.date,
    description: statement.description,
    check_number: statement.check_number,
    debit: Number(statement.debit || 0),
    credit: Number(statement.credit || 0),
    balance: Number(statement.balance || 0),
    status: statement.status,
    ...statement,
  }))
})

function pushErrorToast(message) {
  notificationsStore.pushToast({
    title: 'Bank Statements',
    message,
    variant: 'danger',
  })
}

function pushSuccessToast(message) {
  notificationsStore.pushToast({
    title: 'Bank Statements',
    message,
    variant: 'success',
  })
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

function handleClear() {
  skipNextAutoReload = true
  query.value = ''
  statusFilter.value = ''
  loadStatements(1)
}

function refreshCurrentPage() {
  loadStatements(page.value)
}

async function exportStatements() {
  if (!statements.value.length) {
    pushErrorToast('No bank statements to export.')
    return
  }

  try {
    const workbook = new ExcelJS.Workbook()
    const worksheet = workbook.addWorksheet('Bank Statements')

    worksheet.addRow(['Date', 'Description', 'Check/Ref No.', 'Debit', 'Credit', 'Balance', 'Status'])
    statements.value.forEach((statement) => {
      worksheet.addRow([
        statement.date ? formatDate(statement.date) : '',
        statement.description || '',
        statement.check_number || '',
        Number(statement.debit || 0),
        Number(statement.credit || 0),
        Number(statement.balance || 0),
        statement.status || '',
      ])
    })

    const fileDate = new Date().toISOString().split('T')[0]
    await downloadWorkbook(workbook, `Bank_Statements_${fileDate}.xlsx`)
    pushSuccessToast('Bank statements exported successfully.')
  } catch (error) {
    pushErrorToast(error.message || 'Failed to export bank statements.')
  }
}

function balanceBarWidth(statement) {
  const maxBalance = Number(maxVisibleBalance.value || 0)
  const value = Number(statement?.balance || 0)

  if (!maxBalance || value <= 0) {
    return 18
  }

  return Math.min(100, Math.max(18, (value / maxBalance) * 100))
}

function openDeleteModal(statement) {
  pendingDeleteId.value = statement.id
  deleteModalMessage.value = `Are you sure you want to delete this transaction dated ${formatDate(statement.date)}?`
  deleteModalDetails.value = `${statement.description.substring(0, 50)}${statement.description.length > 50 ? '...' : ''}`
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

function resetDeleteModal() {
  pendingDeleteId.value = null
  deleteModalMessage.value = ''
  deleteModalDetails.value = ''
}

async function confirmDeleteStatement() {
  if (!pendingDeleteId.value) {
    return
  }

  confirmBusy.value = true

  try {
    await deleteBankStatement(pendingDeleteId.value)
    await loadStatements(page.value)
    pushSuccessToast('Statement deleted successfully.')
    
    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to delete statement.')
  } finally {
    confirmBusy.value = false
  }
}

async function loadStatements(targetPage = 1) {
  loading.value = true

  try {
    const response = await fetchBankStatements({
      q: query.value,
      status: statusFilter.value,
      page: targetPage,
      pageSize: pageSize.value,
    })

    statements.value = response.statements || []
    statementCount.value = response.statement_count || 0
    currentPageSize.value = response.pagination?.page_size || currentPageSize.value
    totalDebits.value = Number(response.total_debits || 0)
    totalCredits.value = Number(response.total_credits || 0)

    if (Array.isArray(response.status_filter_options) && response.status_filter_options.length) {
      statusFilterOptions.value = response.status_filter_options
    }

    page.value = response.pagination?.page || targetPage
    totalPages.value = response.pagination?.pages || 1
  } catch (error) {
    pushErrorToast(error.message || 'Failed to fetch bank statements.')
    statements.value = []
    statementCount.value = 0
    totalDebits.value = 0
    totalCredits.value = 0
  } finally {
    loading.value = false
  }
}

function changePage(nextPage) {
  if (nextPage < 1 || nextPage > totalPages.value) {
    return
  }
  loadStatements(nextPage)
}

async function markAsCleared(statement) {
  const confirmed = window.confirm(`Mark transaction dated ${formatDate(statement.date)} as Cleared?`)
  if (!confirmed) {
    return
  }

  try {
    await updateBankStatementStatus(statement.id, { status: 'Cleared' })
    statements.value = statements.value.map((item) =>
      item.id === statement.id
        ? { ...item, status: 'Cleared' }
        : item
    )
    pushSuccessToast('Transaction was marked as cleared.')
  } catch (error) {
    pushErrorToast(error.message || 'Failed to update statement status.')
  }
}

async function bulkDeleteCurrentPage() {
  const ids = statements.value.map((statement) => statement.id)
  if (!ids.length) {
    return
  }

  const confirmed = window.confirm(
    `Delete ${ids.length} statement${ids.length === 1 ? '' : 's'} from this page? This action cannot be undone.`
  )
  if (!confirmed) {
    return
  }

  try {
    await bulkDeleteBankStatements(ids)
    await loadStatements(page.value)
    pushSuccessToast(`${ids.length} statement${ids.length === 1 ? '' : 's'} deleted.`)
  } catch (error) {
    pushErrorToast(error.message || 'Failed to bulk delete statements.')
  }
}

onMounted(() => {
  loadStatements(1)
  unsubscribeArchiveUpdates = subscribeToArchiveUpdates(() => {
    loadStatements(page.value)
  })
})

watch([() => query.value, () => statusFilter.value], () => {
  if (skipNextAutoReload) {
    skipNextAutoReload = false
    return
  }

  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }

  searchDebounceTimer = setTimeout(() => {
    loadStatements(1)
  }, 250)
})

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
