<template>
  <div class="tax-table-page">
    <!-- Page Header -->
    <UiPageHeader
      title="Tax Table"
      description="Manage tax codes and rates used throughout the system"
      eyebrow="Configuration"
    >
      <UiButton v-if="canManageRecords" tag="router-link" to="/tax-table/new" variant="primary">
        <ui-icon name="plus" size="16" />
        Add Entry
      </UiButton>
    </UiPageHeader>

    <!-- Toolbar & Filtering -->
    <div class="search-toolbar">
      <SearchInput
        v-model="query"
        placeholder="Search tax entries..."
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
        :disabled="loading || !filteredEntries.length"
        @click="exportTaxEntries"
      >
        <ui-icon name="download" size="14" />
        Export
      </UiButton>
    </div>

    <!-- Legend -->
    <div class="legend-container">
      <div class="legend-item">
        <span class="legend-badge legend-vat"></span>
        <span class="legend-text">VAT</span>
      </div>
      <div class="legend-item">
        <span class="legend-badge legend-nvat"></span>
        <span class="legend-text">Non-VAT</span>
      </div>
      <div class="legend-item">
        <span class="legend-badge legend-premium"></span>
        <span class="legend-text">Premium</span>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <DeleteConfirmModal
      ref="deleteModal"
      :title="deleteModalTitle"
      :message="deleteModalMessage"
      :details="deleteModalDetails"
      :is-loading="confirmBusy"
      confirm-label="Delete Entry"
      cancel-label="Cancel"
      @confirm="confirmDeleteEntry"
      @close="resetDeleteModal"
    />

    <!-- Loading State -->
    <LoadingState v-if="loading" message="Loading tax entries..." />

    <!-- Empty State -->
    <EmptyState
      v-else-if="!filteredEntries.length"
      icon="grid"
      title="No tax entries found"
      description="Start by adding your first tax entry or clear your active filters to see all records."
    >
      <template #actions>
        <UiButton v-if="canManageRecords" tag="router-link" to="/tax-table/new" variant="primary">Add Entry</UiButton>
        <UiButton v-if="isSearching" variant="secondary" @click="handleClear">
          Clear Filters
        </UiButton>
      </template>
    </EmptyState>

    <!-- Data Table -->
    <div v-else class="table-container">
      <div class="data-table-wrapper">
        <table class="data-table tax-table">
          <thead>
            <tr>
              <th rowspan="3" class="th-name">Name</th>
              <th colspan="2" class="th-group">VAT</th>
              <th colspan="1" class="th-group">PT</th>
              <th colspan="4" class="th-group">EWT</th>
              <th v-if="canManageRecords" rowspan="3" class="th-actions">Actions</th>
            </tr>
            <tr>
              <th colspan="2" class="th-subgroup">20201010-00-01-02</th>
              <th class="th-subgroup">20201010-00-01-03</th>
              <th colspan="4" class="th-subgroup">20201010-00-01-04</th>
            </tr>
            <tr>
              <th class="th-rate">Goods (5%)</th>
              <th class="th-rate">Services (5%)</th>
              <th class="th-rate">Goods &amp; Services (3%)</th>
              <th class="th-rate">Goods (1%)</th>
              <th class="th-rate">Services (2%)</th>
              <th class="th-rate">Rental (5%)</th>
              <th class="th-rate">Prof. Fee (10%)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in filteredEntries" :key="entry.id">
              <td class="td-name">
                <span class="value-with-legend">
                  <span class="value-dot" :class="dotClassForEntry(entry)"></span>
                  {{ entry.purchase_type_name }}
                </span>
              </td>
              <td class="td-value">
                <span class="value-with-legend">
                  {{ displayTaxValue(entry.vat_goods_5) }}
                </span>
              </td>
              <td class="td-value">
                <span class="value-with-legend">
                  {{ displayTaxValue(entry.vat_services_5) }}
                </span>
              </td>
              <td class="td-value">
                <span class="value-with-legend">
                  {{ displayTaxValue(entry.vat_goods_services_3) }}
                </span>
              </td>
              <td class="td-value">
                <span class="value-with-legend">
                  {{ displayTaxValue(entry.vat_goods_1) }}
                </span>
              </td>
              <td class="td-value">
                <span class="value-with-legend">
                  {{ displayTaxValue(entry.vat_services_2) }}
                </span>
              </td>
              <td class="td-value">
                <span class="value-with-legend">
                  {{ displayTaxValue(entry.vat_rental_5) }}
                </span>
              </td>
              <td class="td-value">
                <span class="value-with-legend">
                  {{ displayTaxValue(entry.vat_prof_fee_10) }}
                </span>
              </td>
              <td v-if="canManageRecords" class="td-actions">
                <div class="action-buttons">
                  <ActionButton
                    tag="router-link"
                    variant="primary"
                    :to="`/tax-table/${entry.id}/edit`"
                    title="Edit entry"
                  >
                    <ui-icon name="edit" size="18" />
                  </ActionButton>
                  <ActionButton
                    variant="danger"
                    title="Delete entry"
                    @click="openDeleteModal(entry)"
                  >
                    <ui-icon name="trash-2" size="18" />
                  </ActionButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination Footer -->
    <UiTableFooter
      v-if="filteredEntries.length"
      :current-page="page"
      :page-size="pageSize"
      :total-items="entryCount"
      @prev-page="changePage(page - 1)"
      @next-page="changePage(page + 1)"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import UiPageHeader from '@/components/ui/UiPageHeader.vue'
import UiTableFooter from '@/components/ui/UiTableFooter.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import ActionButton from '@/components/ui/ActionButton.vue'
import SearchInput from '@/components/ui/SearchInput.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import DeleteConfirmModal from '@/components/ui/DeleteConfirmModal.vue'
import ExcelJS from 'exceljs'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { canManageRecords as canManageRecordsAccess } from '@/utils/roleAccess'
import { downloadWorkbook } from '@/utils/excelExport'
import {
  deleteTaxTableEntry,
  fetchPurchaseTypes,
  fetchTaxTableEntries,
} from '@/services/taxTableService'

const notificationsStore = useNotificationsStore()
const deleteModal = ref(null)
const canManageRecords = canManageRecordsAccess()

const loading = ref(false)
const query = ref('')
const page = ref(1)
const toolbarResetToken = ref(0)

const entries = ref([])
const purchaseTypes = ref([])
const totalPages = ref(1)
const confirmBusy = ref(false)
const pendingDeleteId = ref(null)
const deleteModalTitle = ref('Delete Tax Entry')
const deleteModalMessage = ref('')
const deleteModalDetails = ref('')

const pageSize = computed(() => 20)
const isSearching = computed(() => Boolean(query.value.trim()))
const entryCount = computed(() => entries.value.length)

const purchaseTypeNamesById = computed(() => {
  const map = new Map()
  purchaseTypes.value.forEach((item) => map.set(Number(item.id), item.name))
  return map
})

function resolveTaxCategory(purchaseTypeName) {
  const normalizedName = String(purchaseTypeName || '').trim().toUpperCase()
  if (normalizedName.startsWith('NV')) return 'nvat'
  if (normalizedName.startsWith('V')) return 'vat'
  if (normalizedName.includes('PREMIUM')) return 'premium'
  return 'vat'
}

const normalizedEntries = computed(() =>
  entries.value.map((item) => ({
    ...item,
    purchase_type_name: purchaseTypeNamesById.value.get(Number(item.purchase_type)) || '—',
    tax_category: resolveTaxCategory(
      purchaseTypeNamesById.value.get(Number(item.purchase_type)) || ''
    ),
  }))
)

const filteredEntries = computed(() => {
  const q = query.value.toLowerCase().trim()
  if (!q) return normalizedEntries.value

  return normalizedEntries.value.filter((item) => {
    const haystack = [
      item.purchase_type_name,
      item.vat_goods_5,
      item.vat_services_5,
      item.vat_goods_services_3,
      item.vat_goods_1,
      item.vat_services_2,
      item.vat_rental_5,
      item.vat_prof_fee_10,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()

    return haystack.includes(q)
  })
})

function pushErrorToast(message) {
  notificationsStore.pushToast({
    title: 'Tax Table',
    message,
    variant: 'danger',
  })
}

function pushSuccessToast(message) {
  notificationsStore.pushToast({
    title: 'Tax Table',
    message,
    variant: 'success',
  })
}

function handleClear() {
  query.value = ''
  toolbarResetToken.value += 1
}

function refreshCurrentPage() {
  loadTaxEntries(page.value)
}

function dotClassForEntry(entry) {
  return `legend-${entry.tax_category || 'vat'}`
}

function displayTaxValue(value) {
  return value === null || value === undefined || value === '' ? '—' : value
}

async function exportTaxEntries() {
  if (!filteredEntries.value.length) {
    pushErrorToast('No tax entries to export.')
    return
  }

  try {
    const workbook = new ExcelJS.Workbook()
    const worksheet = workbook.addWorksheet('Tax Table')

    worksheet.addRow([
      'Name',
      'Goods (5%)',
      'Services (5%)',
      'Goods & Services (3%)',
      'Goods (1%)',
      'Services (2%)',
      'Rental (5%)',
      'Prof. Fee (10%)',
    ])

    filteredEntries.value.forEach((entry) => {
      worksheet.addRow([
        entry.purchase_type_name || '',
        entry.vat_goods_5 || '',
        entry.vat_services_5 || '',
        entry.vat_goods_services_3 || '',
        entry.vat_goods_1 || '',
        entry.vat_services_2 || '',
        entry.vat_rental_5 || '',
        entry.vat_prof_fee_10 || '',
      ])
    })

    const fileDate = new Date().toISOString().split('T')[0]
    await downloadWorkbook(workbook, `Tax_Table_${fileDate}.xlsx`)
    pushSuccessToast('Tax table entries exported successfully.')
  } catch (error) {
    pushErrorToast(error.message || 'Failed to export tax entries.')
  }
}

function openDeleteModal(entry) {
  pendingDeleteId.value = entry.id
  deleteModalMessage.value = `Are you sure you want to delete the tax entry "${entry.purchase_type_name}"?`
  deleteModalDetails.value = ''
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

function resetDeleteModal() {
  pendingDeleteId.value = null
  deleteModalMessage.value = ''
  deleteModalDetails.value = ''
}

async function confirmDeleteEntry() {
  if (!pendingDeleteId.value) return

  confirmBusy.value = true

  try {
    await deleteTaxTableEntry(pendingDeleteId.value)
    await loadTaxEntries(page.value)
    pushSuccessToast('Tax entry deleted successfully.')

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to delete tax entry.')
  } finally {
    confirmBusy.value = false
  }
}

async function loadTaxEntries(targetPage = 1) {
  loading.value = true

  try {
    const [entriesData, purchaseTypesData] = await Promise.all([
      fetchTaxTableEntries({ page: targetPage }),
      fetchPurchaseTypes(),
    ])

    entries.value = entriesData.entries || []
    purchaseTypes.value = purchaseTypesData || []
    page.value = entriesData.pagination?.page || targetPage
    totalPages.value = entriesData.pagination?.pages || 1
  } catch (error) {
    pushErrorToast(error.message || 'Failed to fetch tax entries.')
  } finally {
    loading.value = false
  }
}

function changePage(nextPage) {
  if (nextPage < 1 || nextPage > totalPages.value) return
  loadTaxEntries(nextPage)
}

onMounted(() => {
  loadTaxEntries(1)
})
</script>

<style scoped>
.tax-table-page {
  --tax-vat-color: #1d9a5f;
  --tax-nvat-color: #2563eb;
  --tax-premium-color: #d97706;
}

.legend-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 0.75rem 0 1rem;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.3rem 0.6rem;
  border: 1px solid var(--border-default);
  border-radius: 999px;
  background: var(--bg-elevated);
}

.legend-badge,
.value-dot {
  width: 0.6rem;
  height: 0.6rem;
  border-radius: 999px;
  flex: 0 0 0.6rem;
}

.legend-vat {
  background: var(--tax-vat-color);
}

.legend-nvat {
  background: var(--tax-nvat-color);
}

.legend-premium {
  background: var(--tax-premium-color);
}

.value-with-legend {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}
</style>
