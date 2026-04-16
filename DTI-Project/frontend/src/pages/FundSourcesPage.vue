<template>
  <div class="fund-sources-page">
    <!-- Page Header -->
    <UiPageHeader
      title="Fund Sources"
      description="Manage and monitor available funding pools and annual budget allocations"
      eyebrow="Financial Records"
    >
      <UiButton tag="router-link" to="/fund-sources/new" variant="primary">
        <ui-icon name="plus" size="16" />
        Add Fund Source
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
        placeholder="Search fund sources..."
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
        :disabled="loading || !filteredFunds.length"
        @click="exportFunds"
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
      confirm-label="Delete Fund Source"
      cancel-label="Cancel"
      @confirm="confirmDeleteFund"
      @close="resetDeleteModal"
    />

    <!-- Loading State -->
    <LoadingState v-if="loading" message="Loading fund sources..." />

    <!-- Empty State -->
    <EmptyState
      v-else-if="!filteredFunds.length"
      icon="briefcase"
      title="No fund sources found"
      description="Start by adding your first fund source or clear your active filters to see matching records."
    >
      <template #actions>
        <UiButton tag="router-link" to="/fund-sources/new" variant="primary">Add Fund Source</UiButton>
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
            <span v-if="isMooeFund(value)" class="mooe-badge">MOOE Fund</span>
          </div>
        </template>

        <template #cell-annual_budget="{ value }">
          <span class="amount-credit">₱ {{ formatCurrencyRaw(value) }}</span>
        </template>

        <template #cell-actions="{ row }">
          <div class="action-buttons">
            <ActionButton
              v-if="isMooeFund(row.name)"
              tag="router-link"
              variant="secondary"
              :to="`/fund-sources/${row.id}`"
              title="View fund source"
            >
              <ui-icon name="eye" size="18" />
            </ActionButton>
            <ActionButton
              tag="router-link"
              variant="primary"
              :to="`/fund-sources/${row.id}/edit`"
              title="Edit fund source"
            >
              <ui-icon name="edit" size="18" />
            </ActionButton>
            <ActionButton
              variant="danger"
              title="Delete fund source"
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
      v-if="filteredFunds.length"
      :current-page="page"
      :page-size="pageSize"
      :total-items="fundCount"
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
import UiButton from '@/components/ui/UiButton.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import ActionButton from '@/components/ui/ActionButton.vue'
import SearchInput from '@/components/ui/SearchInput.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import DeleteConfirmModal from '@/components/ui/DeleteConfirmModal.vue'
import ExcelJS from 'exceljs'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { downloadWorkbook } from '@/utils/excelExport'
import { bulkDeleteFundSources, deleteFundSource, fetchFundSources } from '@/services/fundSourceService'

const notificationsStore = useNotificationsStore()
const deleteModal = ref(null)

const loading = ref(false)
const query = ref('')
const page = ref(1)
const toolbarResetToken = ref(0)

const funds = ref([])
const totalPages = ref(1)
const totalFundCount = ref(0)
const currentPageSize = ref(20)
const confirmBusy = ref(false)
const pendingDeleteId = ref(null)
const deleteModalTitle = ref('Delete Fund Source')
const deleteModalMessage = ref('')
const deleteModalDetails = ref('')

const pageSize = computed(() => currentPageSize.value)
const isSearching = computed(() => Boolean(query.value.trim()))
const fundCount = computed(() => totalFundCount.value)

const totalBudget = computed(() =>
  funds.value.reduce((sum, fund) => sum + Number(fund.annual_budget || 0), 0)
)

const activeFundCount = computed(() =>
  funds.value.filter((fund) => Number(fund.annual_budget || 0) > 0).length
)

const filteredFunds = computed(() => {
  const q = query.value.toLowerCase().trim()
  if (!q) return funds.value

  return funds.value.filter((fund) => {
    const haystack = [fund.name, fund.annual_budget]
      .filter((v) => v !== null && v !== undefined)
      .join(' ')
      .toLowerCase()
    return haystack.includes(q)
  })
})

const summaryCards = computed(() => [
  {
    id: 'fund-count',
    label: 'Fund Sources',
    value: fundCount.value,
    accentColor: 'var(--brand-navy-600)',
    iconBg: 'var(--brand-navy-50)',
    iconColor: 'var(--brand-navy-600)',
  },
  {
    id: 'fund-budget',
    label: 'Total Budget',
    value: `₱ ${formatCurrencyRaw(totalBudget.value)}`,
    accentColor: 'var(--status-success)',
    iconBg: 'var(--status-success-bg)',
    iconColor: 'var(--status-success)',
  },
  {
    id: 'active-funds',
    label: 'Active Funds',
    value: activeFundCount.value,
    accentColor: 'var(--brand-gold-500)',
    iconBg: 'var(--brand-gold-50)',
    iconColor: 'var(--brand-gold-500)',
  },
])

const tableColumns = computed(() => [
  { id: 'name', label: 'Fund Source Name', width: 'flex' },
  { id: 'annual_budget', label: 'Annual Budget', width: '160px', align: 'right' },
  { id: 'actions', label: 'Actions', width: '130px' },
])

const tableRows = computed(() =>
  filteredFunds.value.map((fund) => ({
    id: fund.id,
    name: fund.name,
    annual_budget: fund.annual_budget,
    ...fund,
  }))
)

function pushErrorToast(message) {
  notificationsStore.pushToast({
    title: 'Fund Sources',
    message,
    variant: 'danger',
  })
}

function pushSuccessToast(message) {
  notificationsStore.pushToast({
    title: 'Fund Sources',
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

function isMooeFund(name) {
  return String(name || '').toLowerCase().includes('mooe')
}

function handleClear() {
  query.value = ''
  toolbarResetToken.value += 1
}

function refreshCurrentPage() {
  loadFunds(page.value)
}

async function exportFunds() {
  if (!filteredFunds.value.length) {
    pushErrorToast('No fund sources to export.')
    return
  }

  try {
    const workbook = new ExcelJS.Workbook()
    const worksheet = workbook.addWorksheet('Fund Sources')

    worksheet.addRow(['Fund Source Name', 'Annual Budget'])
    filteredFunds.value.forEach((fund) => {
      worksheet.addRow([fund.name || '', Number(fund.annual_budget || 0)])
    })

    const fileDate = new Date().toISOString().split('T')[0]
    await downloadWorkbook(workbook, `Fund_Sources_${fileDate}.xlsx`)
    pushSuccessToast('Fund sources exported successfully.')
  } catch (error) {
    pushErrorToast(error.message || 'Failed to export fund sources.')
  }
}

function openDeleteModal(fund) {
  pendingDeleteId.value = fund.id
  deleteModalMessage.value = `Are you sure you want to delete the fund source "${fund.name}"?`
  deleteModalDetails.value = fund.annual_budget
    ? `Annual Budget: ₱ ${formatCurrencyRaw(fund.annual_budget)}`
    : ''
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

function resetDeleteModal() {
  pendingDeleteId.value = null
  deleteModalMessage.value = ''
  deleteModalDetails.value = ''
}

async function confirmDeleteFund() {
  if (!pendingDeleteId.value) return

  confirmBusy.value = true

  try {
    await deleteFundSource(pendingDeleteId.value)
    await loadFunds(page.value)
    pushSuccessToast('Fund source deleted successfully.')

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to delete fund source.')
  } finally {
    confirmBusy.value = false
  }
}

async function loadFunds(targetPage = 1) {
  loading.value = true

  try {
    const data = await fetchFundSources({ page: targetPage })
    funds.value = data.funds || []
    page.value = data.pagination?.page || targetPage
    totalPages.value = data.pagination?.pages || 1
    totalFundCount.value = data.pagination?.count || 0
    currentPageSize.value = data.pagination?.page_size || 20
  } catch (error) {
    pushErrorToast(error.message || 'Failed to fetch fund sources.')
  } finally {
    loading.value = false
  }
}

function changePage(nextPage) {
  if (nextPage < 1 || nextPage > totalPages.value) return
  loadFunds(nextPage)
}

async function bulkDeleteCurrentPage() {
  const ids = filteredFunds.value.map((fund) => fund.id)
  if (!ids.length) return

  const confirmed = window.confirm(
    `Delete ${ids.length} fund source${ids.length === 1 ? '' : 's'} from this page? This action cannot be undone.`
  )
  if (!confirmed) return

  try {
    await bulkDeleteFundSources(ids)
    await loadFunds(page.value)
    pushSuccessToast(`${ids.length} fund source${ids.length === 1 ? '' : 's'} deleted.`)
  } catch (error) {
    pushErrorToast(error.message || 'Failed to bulk delete fund sources.')
  }
}

onMounted(() => {
  loadFunds(1)
})
</script>