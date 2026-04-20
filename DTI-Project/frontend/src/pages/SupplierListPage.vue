<template>
  <div class="suppliers-page">
    <UiPageHeader
      title="Suppliers"
      description="Manage suppliers and vendor information across all procurement records"
      eyebrow="Procurement"
    >
      <UiButton v-if="canManageRecords" tag="router-link" to="/suppliers/new" variant="primary">
        <ui-icon name="plus" size="16" />
         Add Supplier
      </UiButton>
    </UiPageHeader>

    <UiSummaryCards
      v-if="summaryCards.length"
      :cards="summaryCards"
    />

    <div class="search-toolbar">
      <SearchInput
        v-model="query"
        placeholder="Search suppliers..."
        @search="loadSuppliers(1)"
        @clear="handleClear"
      />

      <FilterChips
        v-model="vatStatusFilter"
        :chips="normalizedVatPills"
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
        :disabled="loading || !suppliers.length"
        @click="exportSuppliers"
      >
        <ui-icon name="download" size="14" />
        Export
      </UiButton>

      <UiButton
        v-if="canManageRecords && suppliers.length"
        variant="secondary"
        @click="openBulkDeleteModal"
      >
        Delete All
      </UiButton>
    </div>

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

    <LoadingState v-if="loading" message="Loading suppliers..." />

    <EmptyState
      v-else-if="!suppliers.length"
      icon="building-2"
      title="No suppliers found"
      description="Start by adding your first supplier or clear your active filters to see matching records."
    >
      <template #actions>
        <UiButton v-if="canManageRecords" tag="router-link" to="/suppliers/new" variant="primary">Add Supplier</UiButton>
        <UiButton v-if="isSearching" variant="secondary" @click="handleClear">
          Clear Filters
        </UiButton>
      </template>
    </EmptyState>

    <div v-else class="table-container">
      <UiTable
        :columns="tableColumns"
        :rows="tableRows"
      >
        <template #cell-supplier="{ value }">
          <div class="cell-name">
            <strong class="name-label">{{ value }}</strong>
          </div>
        </template>

        <template #cell-tin="{ value }">
          <span class="cell-meta">{{ value || '—' }}</span>
        </template>

        <template #cell-propprietor="{ value }">
          <span class="cell-meta">{{ value || '—' }}</span>
        </template>

        <template #cell-contact_number="{ value }">
          <span class="cell-meta">{{ value || '—' }}</span>
        </template>

        <template #cell-vat_status="{ value }">
          <UiBadge
            :text="displayVatStatus(value)"
            :variant="vatBadgeVariant(value)"
            size="sm"
          />
        </template>

        <template v-if="canManageRecords" #cell-actions="{ row }">
          <div class="action-buttons">
            <ActionButton
              tag="router-link"
              variant="primary"
              :to="`/suppliers/${row.id}/edit`"
              title="Edit supplier"
            >
              <ui-icon name="edit" size="18" />
            </ActionButton>
            <ActionButton
              variant="danger"
              title="Delete supplier"
              @click="openDeleteModal(row)"
            >
              <ui-icon name="trash-2" size="18" />
            </ActionButton>
          </div>
        </template>
      </UiTable>
    </div>

    <UiTableFooter
      v-if="suppliers.length"
      :current-page="page"
      :page-size="pageSize"
      :total-items="supplierCount"
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
import { bulkDeleteSuppliers, deleteSupplier, fetchSuppliers } from '@/services/supplierService'

const notificationsStore = useNotificationsStore()
const deleteModal = ref(null)
const canManageRecords = canManageRecordsAccess()

const loading = ref(false)
const query = ref('')
const vatStatusFilter = ref('')
const page = ref(1)

const suppliers = ref([])
const totalPages = ref(1)
const totalSupplierCount = ref(0)
const currentPageSize = ref(20)
const vatCount = ref(0)
const nonVatCount = ref(0)
const confirmBusy = ref(false)
const pendingDeleteId = ref(null)
const pendingDeleteIds = ref([])
const deleteModalTitle = ref('Delete Supplier')
const deleteModalMessage = ref('')
const deleteModalDetails = ref('')
const deleteConfirmLabel = ref('Delete Supplier')
const isBulkDelete = ref(false)
let searchDebounceTimer = null
let skipNextAutoReload = false

const vatFilterOptions = ref([
  { value: 'V', label: 'VAT Registered' },
  { value: 'NV', label: 'Non-VAT' },
])

const pageSize = computed(() => currentPageSize.value)
const isSearching = computed(() => Boolean(query.value.trim() || vatStatusFilter.value))

const normalizedVatPills = computed(() =>
  vatFilterOptions.value
    .map((option) => ({
      value: String(option?.value || '').trim(),
      label: String(option?.label || option?.value || '').trim(),
    }))
    .filter((option) => option.value)
)

const supplierCount = computed(() => totalSupplierCount.value)

const summaryCards = computed(() => [
  {
    id: 'suppliers',
    label: 'Total Suppliers',
    value: supplierCount.value,
    accentColor: 'var(--brand-navy-600)',
    iconBg: 'var(--brand-navy-50)',
    iconColor: 'var(--brand-navy-600)',
  },
  {
    id: 'vat',
    label: 'VAT Registered',
    value: vatCount.value,
    accentColor: 'var(--status-success)',
    iconBg: 'var(--status-success-bg)',
    iconColor: 'var(--status-success)',
  },
  {
    id: 'non-vat',
    label: 'Non-VAT',
    value: nonVatCount.value,
    accentColor: 'var(--status-warning)',
    iconBg: 'var(--status-warning-bg)',
    iconColor: 'var(--status-warning)',
  },
])

const tableColumns = computed(() => {
  const columns = [
    { id: 'supplier', label: 'Supplier Name', width: 'flex' },
    { id: 'tin', label: 'TIN', width: '130px' },
    { id: 'propprietor', label: 'Proprietor', width: '160px' },
    { id: 'contact_number', label: 'Contact No.', width: '130px' },
    { id: 'vat_status', label: 'VAT Status', width: '110px' },
  ]
  if (canManageRecords) {
    columns.push({ id: 'actions', label: 'Actions', width: '110px' })
  }
  return columns
})

const tableRows = computed(() =>
  suppliers.value.map((supplier) => ({
    id: supplier.id,
    supplier: supplier.supplier,
    tin: supplier.tin,
    propprietor: supplier.propprietor,
    contact_number: supplier.contact_number,
    vat_status: supplier.vat_status,
    ...supplier,
  }))
)

function pushErrorToast(message) {
  notificationsStore.pushToast({
    title: 'Suppliers',
    message,
    variant: 'danger',
  })
}

function pushSuccessToast(message) {
  notificationsStore.pushToast({
    title: 'Suppliers',
    message,
    variant: 'success',
  })
}

function displayVatStatus(value) {
  if (value === 'V') return 'VAT'
  if (value === 'NV') return 'Non-VAT'
  return '—'
}

function vatBadgeVariant(value) {
  if (value === 'V') return 'success'
  if (value === 'NV') return 'warning'
  return 'error'
}

function handleClear() {
  skipNextAutoReload = true
  query.value = ''
  vatStatusFilter.value = ''
  loadSuppliers(1)
}

function refreshCurrentPage() {
  loadSuppliers(page.value)
}

async function exportSuppliers() {
  if (!suppliers.value.length) {
    pushErrorToast('No suppliers to export.')
    return
  }

  try {
    const workbook = new ExcelJS.Workbook()
    const worksheet = workbook.addWorksheet('Suppliers')

    worksheet.addRow(['Supplier Name', 'TIN', 'Proprietor', 'Contact Number', 'VAT Status'])
    suppliers.value.forEach((supplier) => {
      worksheet.addRow([
        supplier.supplier || '',
        supplier.tin || '',
        supplier.propprietor || '',
        supplier.contact_number || '',
        displayVatStatus(supplier.vat_status),
      ])
    })

    const fileDate = new Date().toISOString().split('T')[0]
    await downloadWorkbook(workbook, `Suppliers_${fileDate}.xlsx`)
    pushSuccessToast('Suppliers exported successfully.')
  } catch (error) {
    pushErrorToast(error.message || 'Failed to export suppliers.')
  }
}

function openDeleteModal(supplier) {
  pendingDeleteId.value = supplier.id
  deleteModalMessage.value = `Are you sure you want to delete supplier "${supplier.supplier}"?`
  deleteModalDetails.value = supplier.tin ? `TIN: ${supplier.tin}` : ''
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

function resetDeleteModal() {
  pendingDeleteId.value = null
  pendingDeleteIds.value = []
  isBulkDelete.value = false
  deleteModalTitle.value = 'Delete Supplier'
  deleteConfirmLabel.value = 'Delete Supplier'
  deleteModalMessage.value = ''
  deleteModalDetails.value = ''
}

function openBulkDeleteModal() {
  const ids = suppliers.value.map((item) => item.id)
  if (!ids.length) return

  pendingDeleteIds.value = ids
  isBulkDelete.value = true
  deleteModalTitle.value = 'Delete Suppliers'
  deleteConfirmLabel.value = 'Delete All'
  deleteModalMessage.value = `Delete ${ids.length} supplier${ids.length === 1 ? '' : 's'} from this page? This action cannot be undone.`
  deleteModalDetails.value = `${ids.length} supplier${ids.length === 1 ? '' : 's'} will be permanently deleted.`
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

async function confirmPendingAction() {
  if (isBulkDelete.value) {
    await bulkDelete()
  } else {
    await confirmDeleteSupplier()
  }
}

async function confirmDeleteSupplier() {
  if (!pendingDeleteId.value) return

  confirmBusy.value = true

  try {
    await deleteSupplier(pendingDeleteId.value)
    await loadSuppliers(page.value)
    pushSuccessToast('Supplier deleted successfully.')

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to delete supplier.')
  } finally {
    confirmBusy.value = false
  }
}

async function bulkDelete() {
  if (!pendingDeleteIds.value.length) return

  confirmBusy.value = true

  try {
    await bulkDeleteSuppliers(pendingDeleteIds.value)
    await loadSuppliers(page.value)
    pushSuccessToast(`${pendingDeleteIds.value.length} supplier${pendingDeleteIds.value.length === 1 ? '' : 's'} deleted.`)

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to bulk delete suppliers.')
  } finally {
    confirmBusy.value = false
  }
}

async function loadSuppliers(targetPage = 1) {
  loading.value = true

  try {
    const data = await fetchSuppliers({
      page: targetPage,
      query: query.value,
      vatStatus: vatStatusFilter.value,
      pageSize: pageSize.value,
    })
    suppliers.value = data.suppliers || []
    page.value = data.pagination?.page || targetPage
    totalPages.value = data.pagination?.pages || 1
    totalSupplierCount.value = data.pagination?.count || 0
    currentPageSize.value = data.pagination?.page_size || 20
    vatCount.value = Number(data.vatCount || 0)
    nonVatCount.value = Number(data.nonVatCount || 0)
  } catch (error) {
    pushErrorToast(error.message || 'Failed to fetch suppliers.')
    suppliers.value = []
    totalSupplierCount.value = 0
    vatCount.value = 0
    nonVatCount.value = 0
  } finally {
    loading.value = false
  }
}

function changePage(nextPage) {
  if (nextPage < 1 || nextPage > totalPages.value) return
  loadSuppliers(nextPage)
}

onMounted(() => {
  loadSuppliers(1)
})

watch([() => query.value, () => vatStatusFilter.value], () => {
  if (skipNextAutoReload) {
    skipNextAutoReload = false
    return
  }

  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }

  searchDebounceTimer = setTimeout(() => {
    loadSuppliers(1)
  }, 250)
})

onBeforeUnmount(() => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = null
  }
})
</script>
