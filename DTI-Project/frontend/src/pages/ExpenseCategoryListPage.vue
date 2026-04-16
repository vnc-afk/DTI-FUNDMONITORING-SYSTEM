<template>
  <div class="expense-categories-page">
    <!-- Page Header -->
    <UiPageHeader
      title="Expense Categories"
      description="Manage and classify expense categories used across transactions"
      eyebrow="Financial Records"
    >
      <UiButton tag="router-link" to="/expense-categories/new" variant="primary">
        <ui-icon name="plus" size="16" />
        Add Expense Category
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
        placeholder="Search expense categories..."
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
        :disabled="loading || !filteredCategories.length"
        @click="exportCategories"
      >
        <ui-icon name="download" size="14" />
        Export
      </UiButton>

      <UiButton
        v-if="filteredCategories.length"
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
    <LoadingState v-if="loading" message="Loading expense categories..." />

    <!-- Empty State -->
    <EmptyState
      v-else-if="!filteredCategories.length"
      icon="tag"
      title="No expense categories found"
      description="Start by adding your first expense category or clear your active filters to see matching records."
    >
      <template #actions>
        <UiButton tag="router-link" to="/expense-categories/new" variant="primary">Add Category</UiButton>
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

        <template #cell-actions="{ row }">
          <div class="action-buttons">
            <ActionButton
              tag="router-link"
              variant="primary"
              :to="`/expense-categories/${row.id}/edit`"
              title="Edit category"
            >
              <ui-icon name="edit" size="18" />
            </ActionButton>
            <ActionButton
              variant="danger"
              title="Delete category"
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
      v-if="filteredCategories.length"
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
import { downloadWorkbook } from '@/utils/excelExport'
import {
  bulkDeleteExpenseCategories,
  deleteExpenseCategory,
  fetchExpenseCategories,
} from '@/services/expenseCategoryService'

const notificationsStore = useNotificationsStore()
const deleteModal = ref(null)

const loading = ref(false)
const query = ref('')
const statusFilter = ref('')
const page = ref(1)
const toolbarResetToken = ref(0)

const categories = ref([])
const totalPages = ref(1)
const totalCategoryCount = ref(0)
const currentPageSize = ref(20)
const confirmBusy = ref(false)
const pendingDeleteId = ref(null)
const pendingDeleteIds = ref([])
const deleteModalTitle = ref('Delete Expense Category')
const deleteModalMessage = ref('')
const deleteModalDetails = ref('')
const deleteConfirmLabel = ref('Delete Category')
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

const filteredCategories = computed(() => {
  const q = query.value.toLowerCase().trim()

  return categories.value.filter((category) => {
    const status = category.is_active ? 'active' : 'inactive'
    const statusMatches = !statusFilter.value || statusFilter.value === status

    if (!statusMatches) return false
    if (!q) return true

    const haystack = [category.name, category.description, status]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()

    return haystack.includes(q)
  })
})

const totalCount = computed(() => totalCategoryCount.value)
const activeCount = computed(() => categories.value.filter((item) => Boolean(item.is_active)).length)
const inactiveCount = computed(() => categories.value.filter((item) => !item.is_active).length)

const summaryCards = computed(() => [
  {
    id: 'total',
    label: 'Total Categories',
    value: categories.value.length,
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

const tableColumns = computed(() => [
  { id: 'name', label: 'Name', width: '200px' },
  { id: 'description', label: 'Description', width: 'flex' },
  { id: 'status', label: 'Status', width: '100px' },
  { id: 'actions', label: 'Actions', width: '110px' },
])

const tableRows = computed(() =>
  filteredCategories.value.map((category) => ({
    id: category.id,
    name: category.name,
    description: category.description || '',
    status: category.is_active ? 'Active' : 'Inactive',
    ...category,
  }))
)

function pushErrorToast(message) {
  notificationsStore.pushToast({
    title: 'Expense Categories',
    message,
    variant: 'danger',
  })
}

function pushSuccessToast(message) {
  notificationsStore.pushToast({
    title: 'Expense Categories',
    message,
    variant: 'success',
  })
}

function handleSearchChange() {
  // reactive via v-model; filtering is done in filteredCategories computed
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
  loadCategories(page.value)
}

async function exportCategories() {
  if (!filteredCategories.value.length) {
    pushErrorToast('No expense categories to export.')
    return
  }

  try {
    const workbook = new ExcelJS.Workbook()
    const worksheet = workbook.addWorksheet('Expense Categories')

    worksheet.addRow(['Name', 'Description', 'Status'])
    filteredCategories.value.forEach((category) => {
      worksheet.addRow([
        category.name || '',
        category.description || '',
        category.is_active ? 'Active' : 'Inactive',
      ])
    })

    const fileDate = new Date().toISOString().split('T')[0]
    await downloadWorkbook(workbook, `Expense_Categories_${fileDate}.xlsx`)
    pushSuccessToast('Expense categories exported successfully.')
  } catch (error) {
    pushErrorToast(error.message || 'Failed to export expense categories.')
  }
}

function openDeleteModal(category) {
  pendingDeleteId.value = category.id
  deleteModalMessage.value = `Are you sure you want to delete the expense category "${category.name}"?`
  deleteModalDetails.value = category.description
    ? `${category.description.substring(0, 80)}${category.description.length > 80 ? '...' : ''}`
    : ''
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

function resetDeleteModal() {
  pendingDeleteId.value = null
  pendingDeleteIds.value = []
  isBulkDelete.value = false
  deleteModalTitle.value = 'Delete Expense Category'
  deleteConfirmLabel.value = 'Delete Category'
  deleteModalMessage.value = ''
  deleteModalDetails.value = ''
}

function openBulkDeleteModal() {
  const ids = filteredCategories.value.map((item) => item.id)
  if (!ids.length) return

  pendingDeleteIds.value = ids
  isBulkDelete.value = true
  deleteModalTitle.value = 'Delete Expense Categories'
  deleteConfirmLabel.value = 'Delete All'
  deleteModalMessage.value = `Delete ${ids.length} categor${ids.length === 1 ? 'y' : 'ies'} from this page? This action cannot be undone.`
  deleteModalDetails.value = `${ids.length} categor${ids.length === 1 ? 'y' : 'ies'} will be permanently deleted.`
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

async function confirmPendingAction() {
  if (isBulkDelete.value) {
    await bulkDelete()
  } else {
    await confirmDeleteCategory()
  }
}

async function confirmDeleteCategory() {
  if (!pendingDeleteId.value) return

  confirmBusy.value = true

  try {
    await deleteExpenseCategory(pendingDeleteId.value)
    await loadCategories(page.value)
    pushSuccessToast('Expense category deleted successfully.')

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to delete expense category.')
  } finally {
    confirmBusy.value = false
  }
}

async function bulkDelete() {
  if (!pendingDeleteIds.value.length) return

  confirmBusy.value = true

  try {
    await bulkDeleteExpenseCategories(pendingDeleteIds.value)
    await loadCategories(page.value)
    pushSuccessToast(`${pendingDeleteIds.value.length} categor${pendingDeleteIds.value.length === 1 ? 'y' : 'ies'} deleted.`)

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to bulk delete expense categories.')
  } finally {
    confirmBusy.value = false
  }
}

async function loadCategories(targetPage = 1) {
  loading.value = true

  try {
    const data = await fetchExpenseCategories({ page: targetPage })
    categories.value = data.categories || []
    page.value = data.pagination?.page || targetPage
    totalPages.value = data.pagination?.pages || 1
    totalCategoryCount.value = data.pagination?.count || 0
    currentPageSize.value = data.pagination?.page_size || 20
  } catch (error) {
    pushErrorToast(error.message || 'Failed to fetch expense categories.')
  } finally {
    loading.value = false
  }
}

function changePage(nextPage) {
  if (nextPage < 1 || nextPage > totalPages.value) return
  loadCategories(nextPage)
}



onMounted(() => {
  loadCategories(1)
})
</script>
