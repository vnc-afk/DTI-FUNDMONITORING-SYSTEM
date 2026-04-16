<template>
  <div class="expense-objects-page">
    <!-- Page Header -->
    <UiPageHeader
      title="Expense Objects"
      description="Manage account titles and expense object classifications"
      eyebrow="Financial Records"
    >
      <UiButton v-if="canManageRecords" tag="router-link" to="/expense-objects/new" variant="primary">
        <ui-icon name="plus" size="16" />
        Add Expense Object
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
        placeholder="Search expense objects..."
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
        :disabled="loading || !filteredObjects.length"
        @click="exportObjects"
      >
        <ui-icon name="download" size="14" />
        Export
      </UiButton>

      <UiButton
        v-if="canManageRecords && filteredObjects.length"
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
    <LoadingState v-if="loading" message="Loading expense objects..." />

    <!-- Empty State -->
    <EmptyState
      v-else-if="!filteredObjects.length"
      icon="box"
      title="No expense objects found"
      description="Start by adding your first expense object or clear your active filters to see matching records."
    >
      <template #actions>
        <UiButton v-if="canManageRecords" tag="router-link" to="/expense-objects/new" variant="primary">Add Object</UiButton>
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
        <template #cell-code="{ value }">
          <span class="cell-code">{{ value }}</span>
        </template>

        <template #cell-name="{ value }">
          <div class="cell-name">
            <strong class="name-label">{{ value }}</strong>
          </div>
        </template>

        <template #cell-description="{ value }">
          <span class="text-muted">{{ value || '—' }}</span>
        </template>

        <template #cell-status="{ value }">
          <UiBadge
            :text="value"
            :variant="value === 'Active' ? 'success' : 'error'"
            size="sm"
          />
        </template>

        <template v-if="canManageRecords" #cell-actions="{ row }">
          <div class="action-buttons">
            <ActionButton
              tag="router-link"
              variant="primary"
              :to="`/expense-objects/${row.id}/edit`"
              title="Edit expense object"
            >
              <ui-icon name="edit" size="18" />
            </ActionButton>
            <ActionButton
              variant="danger"
              title="Delete expense object"
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
      v-if="filteredObjects.length"
      :current-page="page"
      :page-size="pageSize"
      :total-items="totalCount"
      @prev-page="changePage(page - 1)"
      @next-page="changePage(page + 1)"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import UiPageHeader from '@/components/ui/UiPageHeader.vue'
import UiSummaryCards from '@/components/ui/UiSummaryCards.vue'
import UiTable from '@/components/ui/UiTable.vue'
import UiTableFooter from '@/components/ui/UiTableFooter.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import DeleteConfirmModal from '@/components/ui/DeleteConfirmModal.vue'
import ActionButton from '@/components/ui/ActionButton.vue'
import SearchInput from '@/components/ui/SearchInput.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import FilterChips from '@/components/ui/FilterChips.vue'
import ExcelJS from 'exceljs'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { canManageRecords as canManageRecordsAccess } from '@/utils/roleAccess'
import { downloadWorkbook } from '@/utils/excelExport'
import {
  bulkDeleteExpenseObjects,
  deleteExpenseObject,
  fetchExpenseObjects,
} from '@/services/expenseObjectService'

const notificationsStore = useNotificationsStore()
const deleteModal = ref(null)
const canManageRecords = canManageRecordsAccess()

const loading = ref(false)
const query = ref('')
const statusFilter = ref('')
const page = ref(1)
const toolbarResetToken = ref(0)

const expenseObjects = ref([])
const totalPages = ref(1)
const totalObjectCount = ref(0)
const currentPageSize = ref(20)
const confirmBusy = ref(false)
const pendingDeleteId = ref(null)
const pendingDeleteIds = ref([])
const deleteModalTitle = ref('Delete Expense Object')
const deleteModalMessage = ref('')
const deleteModalDetails = ref('')
const deleteConfirmLabel = ref('Delete Object')
const isBulkDelete = ref(false)

const statusFilterOptions = ref([
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
])

const pageSize = computed(() => currentPageSize.value)

const isSearching = computed(() => Boolean(query.value.trim() || statusFilter.value))

const normalizedStatusPills = computed(() =>
  statusFilterOptions.value
    .map((option) => ({
      value: String(option?.value || '').trim(),
      label: String(option?.label || option?.value || '').trim(),
    }))
    .filter((option) => option.value)
)

const filteredObjects = computed(() => {
  const q = query.value.toLowerCase().trim()

  return expenseObjects.value.filter((obj) => {
    const status = obj.is_active ? 'active' : 'inactive'
    const statusMatches = !statusFilter.value || statusFilter.value === status

    if (!statusMatches) return false
    if (!q) return true

    const haystack = [obj.code, obj.name, obj.description, status]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()

    return haystack.includes(q)
  })
})

const totalCount = computed(() => totalObjectCount.value)
const activeCount = computed(() => expenseObjects.value.filter((item) => Boolean(item.is_active)).length)
const inactiveCount = computed(() => expenseObjects.value.filter((item) => !item.is_active).length)

const summaryCards = computed(() => [
  {
    id: 'total',
    label: 'Expense Objects',
    value: expenseObjects.value.length,
    accentColor: 'var(--brand-navy-600)',
    iconBg: 'var(--brand-navy-50)',
    iconColor: 'var(--brand-navy-600)',
  },
  {
    id: 'active',
    label: 'Active',
    value: activeCount.value,
    accentColor: 'var(--status-success)',
    iconBg: 'var(--status-success-bg)',
    iconColor: 'var(--status-success)',
  },
  {
    id: 'inactive',
    label: 'Inactive',
    value: inactiveCount.value,
    accentColor: 'var(--status-danger)',
    iconBg: 'var(--status-danger-bg)',
    iconColor: 'var(--status-danger)',
  },
])

const tableColumns = computed(() => {
  const columns = [
    { id: 'code', label: 'Code', width: '110px' },
    { id: 'name', label: 'Name', width: '200px' },
    { id: 'description', label: 'Description', width: 'flex' },
    { id: 'status', label: 'Status', width: '100px' },
  ]
  if (canManageRecords) {
    columns.push({ id: 'actions', label: 'Actions', width: '110px' })
  }
  return columns
})

const tableRows = computed(() =>
  filteredObjects.value.map((obj) => ({
    id: obj.id,
    code: obj.code,
    name: obj.name,
    description: obj.description || '',
    status: obj.is_active ? 'Active' : 'Inactive',
    ...obj,
  }))
)

function pushErrorToast(message) {
  notificationsStore.pushToast({
    title: 'Expense Objects',
    message,
    variant: 'danger',
  })
}

function pushSuccessToast(message) {
  notificationsStore.pushToast({
    title: 'Expense Objects',
    message,
    variant: 'success',
  })
}

function setStatusFilter(value) {
  statusFilter.value = String(value || '').trim()
}

function handleClear() {
  query.value = ''
  statusFilter.value = ''
  toolbarResetToken.value += 1
}

function refreshCurrentPage() {
  loadExpenseObjects(page.value)
}

async function exportObjects() {
  if (!filteredObjects.value.length) {
    pushErrorToast('No expense objects to export.')
    return
  }

  try {
    const workbook = new ExcelJS.Workbook()
    const worksheet = workbook.addWorksheet('Expense Objects')

    worksheet.addRow(['Code', 'Name', 'Description', 'Status'])
    filteredObjects.value.forEach((obj) => {
      worksheet.addRow([
        obj.code || '',
        obj.name || '',
        obj.description || '',
        obj.is_active ? 'Active' : 'Inactive',
      ])
    })

    const fileDate = new Date().toISOString().split('T')[0]
    await downloadWorkbook(workbook, `Expense_Objects_${fileDate}.xlsx`)
    pushSuccessToast('Expense objects exported successfully.')
  } catch (error) {
    pushErrorToast(error.message || 'Failed to export expense objects.')
  }
}

function openDeleteModal(obj) {
  pendingDeleteId.value = obj.id
  deleteModalMessage.value = `Are you sure you want to delete the expense object "${obj.name}"?`
  deleteModalDetails.value = obj.code ? `Code: ${obj.code}` : ''
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

function resetDeleteModal() {
  pendingDeleteId.value = null
  pendingDeleteIds.value = []
  isBulkDelete.value = false
  deleteModalTitle.value = 'Delete Expense Object'
  deleteConfirmLabel.value = 'Delete Object'
  deleteModalMessage.value = ''
  deleteModalDetails.value = ''
}

function openBulkDeleteModal() {
  const ids = filteredObjects.value.map((item) => item.id)
  if (!ids.length) return

  pendingDeleteIds.value = ids
  isBulkDelete.value = true
  deleteModalTitle.value = 'Delete Expense Objects'
  deleteConfirmLabel.value = 'Delete All'
  deleteModalMessage.value = `Delete ${ids.length} expense object${ids.length === 1 ? '' : 's'} from this page? This action cannot be undone.`
  deleteModalDetails.value = `${ids.length} object${ids.length === 1 ? '' : 's'} will be permanently deleted.`
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

async function confirmPendingAction() {
  if (isBulkDelete.value) {
    await bulkDelete()
  } else {
    await confirmDeleteObject()
  }
}

async function confirmDeleteObject() {
  if (!pendingDeleteId.value) return

  confirmBusy.value = true

  try {
    await deleteExpenseObject(pendingDeleteId.value)
    await loadExpenseObjects(page.value)
    pushSuccessToast('Expense object deleted successfully.')

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to delete expense object.')
  } finally {
    confirmBusy.value = false
  }
}

async function bulkDelete() {
  if (!pendingDeleteIds.value.length) return

  confirmBusy.value = true

  try {
    await bulkDeleteExpenseObjects(pendingDeleteIds.value)
    await loadExpenseObjects(page.value)
    pushSuccessToast(`${pendingDeleteIds.value.length} expense object${pendingDeleteIds.value.length === 1 ? '' : 's'} deleted.`)

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to bulk delete expense objects.')
  } finally {
    confirmBusy.value = false
  }
}

async function loadExpenseObjects(targetPage = 1) {
  loading.value = true

  try {
    const data = await fetchExpenseObjects({ page: targetPage })
    expenseObjects.value = data.objects || []
    page.value = data.pagination?.page || targetPage
    totalPages.value = data.pagination?.pages || 1
    totalObjectCount.value = data.pagination?.count || 0
    currentPageSize.value = data.pagination?.page_size || 20
  } catch (error) {
    pushErrorToast(error.message || 'Failed to fetch expense objects.')
  } finally {
    loading.value = false
  }
}

function changePage(nextPage) {
  if (nextPage < 1 || nextPage > totalPages.value) return
  loadExpenseObjects(nextPage)
}

onMounted(() => {
  loadExpenseObjects(1)
})
</script>