<template>
  <div class="suppliers-page">
    <!-- Page Header -->
    <UiPageHeader
      title="Suppliers"
      description="Manage suppliers and vendor information across all procurement records"
      eyebrow="Procurement"
    >
      <UiButton tag="router-link" to="/suppliers/new" variant="primary">
        <ui-icon name="plus" size="16" />
         Add Supplier
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
        placeholder="Search suppliers..."
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
        :disabled="loading || !filteredSuppliers.length"
        @click="exportSuppliers"
      >
        <ui-icon name="download" size="14" />
        Export
      </UiButton>

      <UiButton
        v-if="filteredSuppliers.length"
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
    <LoadingState v-if="loading" message="Loading suppliers..." />

    <!-- Empty State -->
    <EmptyState
      v-else-if="!filteredSuppliers.length"
      icon="building-2"
      title="No suppliers found"
      description="Start by adding your first supplier or clear your active filters to see matching records."
    >
      <template #actions>
        <UiButton tag="router-link" to="/suppliers/new" variant="primary">Add Supplier</UiButton>
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

        <template #cell-actions="{ row }">
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

    <!-- Pagination Footer -->
    <UiTableFooter
      v-if="filteredSuppliers.length"
      :current-page="page"
      :page-size="pageSize"
      :total-items="supplierCount"
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
import { bulkDeleteSuppliers, deleteSupplier, fetchSuppliers } from '@/services/supplierService'

const notificationsStore = useNotificationsStore()
const deleteModal = ref(null)

const loading = ref(false)
const query = ref('')
const vatStatusFilter = ref('')
const page = ref(1)
const toolbarResetToken = ref(0)

const suppliers = ref([])
const totalPages = ref(1)
const totalSupplierCount = ref(0)
const currentPageSize = ref(20)
const confirmBusy = ref(false)
const pendingDeleteId = ref(null)
const pendingDeleteIds = ref([])
const deleteModalTitle = ref('Delete Supplier')
const deleteModalMessage = ref('')
const deleteModalDetails = ref('')
const deleteConfirmLabel = ref('Delete Supplier')
const isBulkDelete = ref(false)

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

const filteredSuppliers = computed(() => {
  const q = query.value.toLowerCase().trim()

  return suppliers.value.filter((supplier) => {
    const vatMatches =
      !vatStatusFilter.value || (supplier.vat_status || '—') === vatStatusFilter.value
    if (!vatMatches) return false
    if (!q) return true

    const haystack = [
      supplier.supplier,
      supplier.tin,
      supplier.propprietor,
      supplier.contact_number,
      supplier.vat_status || '—',
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()

    return haystack.includes(q)
  })
})

const supplierCount = computed(() => totalSupplierCount.value)
const vatCount = computed(() => suppliers.value.filter((item) => item.vat_status === 'V').length)
const nonVatCount = computed(() => suppliers.value.filter((item) => item.vat_status === 'NV').length)

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

const tableColumns = computed(() => [
  { id: 'supplier', label: 'Supplier Name', width: 'flex' },
  { id: 'tin', label: 'TIN', width: '130px' },
  { id: 'propprietor', label: 'Proprietor', width: '160px' },
  { id: 'contact_number', label: 'Contact No.', width: '130px' },
  { id: 'vat_status', label: 'VAT Status', width: '110px' },
  { id: 'actions', label: 'Actions', width: '110px' },
])

const tableRows = computed(() =>
  filteredSuppliers.value.map((supplier) => ({
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

function setVatStatusFilter(value) {
  vatStatusFilter.value = String(value || '').trim()
}

function handleClear() {
  query.value = ''
  vatStatusFilter.value = ''
  toolbarResetToken.value += 1
}

function refreshCurrentPage() {
  loadSuppliers(page.value)
}

async function exportSuppliers() {
  if (!filteredSuppliers.value.length) {
    pushErrorToast('No suppliers to export.')
    return
  }

  try {
    const workbook = new ExcelJS.Workbook()
    const worksheet = workbook.addWorksheet('Suppliers')

    worksheet.addRow(['Supplier Name', 'TIN', 'Proprietor', 'Contact Number', 'VAT Status'])
    filteredSuppliers.value.forEach((supplier) => {
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
  const ids = filteredSuppliers.value.map((item) => item.id)
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
    const data = await fetchSuppliers({ page: targetPage })
    suppliers.value = data.suppliers || []
    page.value = data.pagination?.page || targetPage
    totalPages.value = data.pagination?.pages || 1
    totalSupplierCount.value = data.pagination?.count || 0
    currentPageSize.value = data.pagination?.page_size || 20
  } catch (error) {
    pushErrorToast(error.message || 'Failed to fetch suppliers.')
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
</script>

