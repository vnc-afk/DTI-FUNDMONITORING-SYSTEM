<template>
  <div class="fund-source-detail-page">
    <!-- Page Header -->
    <UiPageHeader
      :title="fund?.name || 'Fund Source'"
      description="Fund Source Budget Breakdown"
      eyebrow="Financial Records"
    >
      <UiButton tag="router-link" to="/fund-sources" variant="secondary" size="md">
        <ui-icon name="chevron-left" size="16" />
        Back to Fund Sources
      </UiButton>
    </UiPageHeader>

    <!-- Summary Cards -->
    <UiSummaryCards
      v-if="summaryCards.length"
      :cards="summaryCards"
    />

    <!-- Toolbar -->
    <div class="search-toolbar">
      <div class="toolbar-title-block">
        <ui-icon name="receipt" size="16" />
        <span class="toolbar-title-text">Budget Breakdown</span>
        <span class="toolbar-count">{{ breakdownCountText }}</span>
      </div>

      <div class="toolbar-spacer"></div>

      <UiButton
        variant="secondary"
        size="md"
        :disabled="loading"
        @click="loadFundSourceData"
      >
        <ui-icon name="rotate-cw" size="14" />
        Refresh
      </UiButton>

      <UiButton
        v-if="canManageRecords && !allCategoriesAllocated"
        tag="router-link"
        :to="`/fund-sources/${fundId}/breakdowns/new`"
        variant="primary"
        size="md"
      >
        <ui-icon name="plus" size="16" />
        Add Breakdown
      </UiButton>

      <span v-else-if="canManageRecords" class="all-allocated-badge">
        <ui-icon name="check" size="14" />
        All Categories Allocated
      </span>
    </div>

    <!-- Delete Confirmation Modal -->
    <DeleteConfirmModal
      ref="deleteModal"
      :title="deleteModalTitle"
      :message="deleteModalMessage"
      :details="deleteModalDetails"
      :is-loading="confirmBusy"
      confirm-label="Delete Breakdown"
      cancel-label="Cancel"
      @confirm="confirmDeleteBreakdown"
      @close="resetDeleteModal"
    />

    <!-- Loading State -->
    <div v-if="loading" class="loading-state" role="status" aria-live="polite">
      <div class="spinner"></div>
      <p>Loading breakdown data...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!breakdownRows.length" class="empty-state" role="status" aria-live="polite">
      <ui-icon name="credit-card" size="48" />
      <h3>No breakdowns configured yet</h3>
      <p>Add budget breakdowns to allocate this fund source across expense categories.</p>
      <div class="empty-actions">
        <UiButton
          v-if="canManageRecords && !allCategoriesAllocated"
          tag="router-link"
          :to="`/fund-sources/${fundId}/breakdowns/new`"
          variant="primary"
          size="md"
        >
          Add Breakdown
        </UiButton>
      </div>
    </div>

    <!-- Data Table -->
    <div v-else class="table-container">
      <UiTable
        :columns="tableColumns"
        :rows="tableRows"
      >
        <template #cell-category="{ value }">
          <div class="cell-name">
            <strong class="name-label">{{ value }}</strong>
          </div>
        </template>

        <template #cell-budget_amount="{ value }">
          <span class="amount-credit">₱ {{ formatCurrencyRaw(value) }}</span>
        </template>

        <template #cell-percentage="{ value }">
          <div class="cell-percentage">
            <span class="percentage-value">{{ value }}%</span>
            <div class="percentage-bar">
              <div
                class="percentage-fill"
                :style="{ width: `${Math.min(value, 100)}%` }"
              ></div>
            </div>
          </div>
        </template>

        <template v-if="canManageRecords" #cell-actions="{ row }">
          <div class="action-buttons">
            <UiButton
              tag="router-link"
              :to="`/fund-sources/${fundId}/breakdowns/${row.id}/edit`"
              variant="ghost"
              size="sm"
              title="Edit breakdown"
            >
              <ui-icon name="edit" size="18" />
            </UiButton>
            <UiButton
              variant="ghost"
              size="sm"
              title="Delete breakdown"
              @click="openDeleteModal(row)"
            >
              <ui-icon name="trash-2" size="18" />
            </UiButton>
          </div>
        </template>
      </UiTable>

      <!-- Budget Utilization Footer -->
      <UiCard class="utilization-card">
        <div class="utilization-header">
          <span class="utilization-label">Budget Utilization</span>
          <span class="utilization-percent" :class="progressClass">{{ progressPercent }}%</span>
        </div>
        <div class="utilization-track">
          <div
            class="utilization-fill"
            :class="progressFillClass"
            :style="{ width: `${Math.min(progressPercent, 100)}%` }"
          ></div>
        </div>
        <div class="utilization-meta">
          <span v-if="progressPercent > 100" class="utilization-over">
            Over budget by ₱{{ formatCurrencyRaw(overBudgetAmount) }}
          </span>
          <span v-else class="utilization-ok">
            {{ progressPercent }}% allocated · ₱{{ formatCurrencyRaw(remainingBudget) }} remaining
          </span>
          <span class="utilization-ratio">
            ₱{{ formatCurrencyRaw(totalBreakdown) }} / ₱{{ formatCurrencyRaw(annualBudget) }}
          </span>
        </div>
      </UiCard>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import UiPageHeader from '@/components/ui/UiPageHeader.vue'
import UiSummaryCards from '@/components/ui/UiSummaryCards.vue'
import UiTable from '@/components/ui/UiTable.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import DeleteConfirmModal from '@/components/ui/DeleteConfirmModal.vue'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { canManageRecords as canManageRecordsAccess } from '@/utils/roleAccess'
import {
  deleteFundSourceBreakdown,
  fetchBreakdownCategories,
  fetchFundSourceBreakdowns,
  fetchFundSourceById,
} from '@/services/fundSourceService'

const route = useRoute()
const notificationsStore = useNotificationsStore()
const deleteModal = ref(null)
const canManageRecords = canManageRecordsAccess()

const fundId = computed(() => Number(route.params.id))

const loading = ref(false)
const fund = ref(null)
const breakdowns = ref([])
const categories = ref([])
const confirmBusy = ref(false)
const pendingDeleteId = ref(null)
const deleteModalTitle = ref('Delete Breakdown')
const deleteModalMessage = ref('')
const deleteModalDetails = ref('')

// ── Lookups ──────────────────────────────────────────────────────────────────

// Lookups no longer needed - category data comes from API

// ── Derived rows ─────────────────────────────────────────────────────────────

const breakdownRows = computed(() => {
  const annual = Number(fund.value?.annual_budget || 0)
  return breakdowns.value.map((item) => {
    // Try to get category code from the API response
    const categoryLabel = item.category_code || `Category #${item.category}`
    const budgetAmount = Number(item.budget_amount || 0)
    const percentage = annual > 0 ? Math.round((budgetAmount / annual) * 100) : 0
    return { ...item, budget_amount: budgetAmount, categoryLabel, percentage }
  })
})

// ── Budget computeds ─────────────────────────────────────────────────────────

const annualBudget = computed(() => Number(fund.value?.annual_budget || 0))
const totalBreakdown = computed(() =>
  breakdownRows.value.reduce((sum, item) => sum + Number(item.budget_amount || 0), 0)
)
const remainingBudget = computed(() => annualBudget.value - totalBreakdown.value)
const overBudgetAmount = computed(() => Math.max(totalBreakdown.value - annualBudget.value, 0))
const progressPercent = computed(() => {
  if (annualBudget.value <= 0) return 0
  return Math.round((totalBreakdown.value / annualBudget.value) * 100)
})

const progressClass = computed(() => {
  if (progressPercent.value > 100) return 'is-danger'
  if (progressPercent.value > 75) return 'is-warning'
  return 'is-success'
})

const progressFillClass = computed(() => {
  if (progressPercent.value > 100) return 'fill-danger'
  if (progressPercent.value > 75) return 'fill-warning'
  return 'fill-success'
})

// ── Category allocation guards ────────────────────────────────────────────────

const activeCategories = computed(() =>
  categories.value.filter((item) => item.is_active !== false)
)
const usedCategoryIds = computed(() =>
  new Set(breakdowns.value.map((item) => Number(item.category)))
)
const allCategoriesAllocated = computed(() => {
  if (!activeCategories.value.length) return true
  return activeCategories.value.every((item) => usedCategoryIds.value.has(Number(item.id)))
})

// ── Summary cards ─────────────────────────────────────────────────────────────

const summaryCards = computed(() => [
  {
    id: 'annual-budget',
    label: 'Annual Budget',
    value: `₱ ${formatCurrencyRaw(annualBudget.value)}`,
    accentColor: 'var(--brand-navy-600)',
    iconBg: 'var(--brand-navy-50)',
    iconColor: 'var(--brand-navy-600)',
  },
  {
    id: 'allocated',
    label: 'Allocated',
    value: `₱ ${formatCurrencyRaw(totalBreakdown.value)}`,
    accentColor: 'var(--status-success)',
    iconBg: 'var(--status-success-bg)',
    iconColor: 'var(--status-success)',
  },
  {
    id: 'remaining',
    label: remainingBudget.value < 0 ? 'Over Allocated' : 'Remaining',
    value: `₱ ${formatCurrencyRaw(Math.abs(remainingBudget.value))}`,
    accentColor: remainingBudget.value < 0 ? 'var(--status-danger)' : 'var(--brand-gold-500)',
    iconBg: remainingBudget.value < 0 ? 'var(--status-danger-bg)' : 'var(--brand-gold-50)',
    iconColor: remainingBudget.value < 0 ? 'var(--status-danger)' : 'var(--brand-gold-500)',
  },
])

// ── Table ─────────────────────────────────────────────────────────────────────

const breakdownCountText = computed(
  () => `${breakdownRows.value.length} breakdown${breakdownRows.value.length === 1 ? '' : 's'}`
)

const tableColumns = computed(() => {
  const columns = [
    { id: 'category', label: 'Category', width: 'flex' },
    { id: 'budget_amount', label: 'Budget Amount', width: '160px', align: 'right' },
    { id: 'percentage', label: 'Percentage', width: '150px', align: 'right' },
  ]
  if (canManageRecords) {
    columns.push({ id: 'actions', label: 'Actions', width: '110px' })
  }
  return columns
})

const tableRows = computed(() =>
  breakdownRows.value.map((item) => ({
    ...item,
    id: item.id,
    category: item.categoryLabel,
    budget_amount: item.budget_amount,
    percentage: item.percentage,
  }))
)

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatCurrencyRaw(value) {
  return Number(value || 0).toLocaleString('en-PH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function pushErrorToast(message) {
  notificationsStore.pushToast({ title: 'Fund Source', message, variant: 'danger' })
}

function pushSuccessToast(message) {
  notificationsStore.pushToast({ title: 'Fund Source', message, variant: 'success' })
}

// ── Modal ─────────────────────────────────────────────────────────────────────

function openDeleteModal(row) {
  pendingDeleteId.value = row.id
  deleteModalMessage.value = `Are you sure you want to delete the breakdown for "${row.category}"?`
  deleteModalDetails.value = `Budget Amount: ₱ ${formatCurrencyRaw(row.budget_amount)}`
  if (deleteModal.value) deleteModal.value.open()
}

function resetDeleteModal() {
  pendingDeleteId.value = null
  deleteModalMessage.value = ''
  deleteModalDetails.value = ''
}

async function confirmDeleteBreakdown() {
  if (!pendingDeleteId.value) return
  confirmBusy.value = true
  try {
    await deleteFundSourceBreakdown(pendingDeleteId.value)
    await loadFundSourceData()
    pushSuccessToast('Breakdown deleted successfully.')
    if (deleteModal.value) deleteModal.value.close()
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to delete breakdown.')
  } finally {
    confirmBusy.value = false
  }
}

// ── Data loading ──────────────────────────────────────────────────────────────

async function loadFundSourceData() {
  loading.value = true
  try {
    const [fundItem, categoryItems, breakdownItems] = await Promise.all([
      fetchFundSourceById(fundId.value),
      fetchBreakdownCategories(),
      fetchFundSourceBreakdowns(fundId.value),
    ])
    console.log('Breakdown API response:', breakdownItems) // Debug log
    fund.value = fundItem
    categories.value = categoryItems
    breakdowns.value = breakdownItems
  } catch (error) {
    pushErrorToast(error.message || 'Failed to load fund source breakdown data.')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadFundSourceData()
})
</script>

<style scoped>
/* Fund Source Detail Page Styles */

/* ── Toolbar ────────────────────────────────────────────────────────────────── */
.search-toolbar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin: var(--space-4) 0;
  flex-wrap: wrap;
}

.toolbar-title-block {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-primary);
}

.toolbar-title-text {
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--text-primary);
}

.toolbar-count {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-full);
  padding: 0.15rem 0.5rem;
}

.toolbar-spacer {
  flex: 1;
}

.all-allocated-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--status-success);
  background: var(--status-success-bg);
  border: 1px solid color-mix(in srgb, var(--status-success) 30%, transparent);
  border-radius: var(--radius-full);
  padding: var(--space-2) var(--space-3);
}

/* ── Loading & Empty States ────────────────────────────────────────────────── */
.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-8);
  min-height: 300px;
  color: var(--text-secondary);
}

.loading-state h3, .empty-state h3 {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--text-primary);
}

.loading-state p, .empty-state p {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  max-width: 400px;
  text-align: center;
}

.empty-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-soft);
  border-top-color: var(--brand-navy-main);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ── Table ────────────────────────────────────────────────────────────────── */
.table-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  border-radius: var(--radius);
  overflow: hidden;
  border: 1px solid var(--border-soft);
}

.cell-name {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.name-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.amount-credit {
  font-family: 'Courier New', monospace;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--status-success);
  white-space: nowrap;
}

.cell-percentage {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  align-items: flex-end;
}

.percentage-value {
  font-family: 'Courier New', monospace;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.percentage-bar {
  width: 100%;
  height: 4px;
  background: var(--bg-elevated);
  border-radius: 2px;
  overflow: hidden;
}

.percentage-fill {
  height: 100%;
  background: var(--brand-navy-main);
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* ── Action Buttons ────────────────────────────────────────────────────────── */
.fund-source-detail-page :deep(tbody .action-buttons) {
  display: flex;
  gap: var(--space-1);
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition-base);
}

.fund-source-detail-page :deep(tbody tr:hover .action-buttons),
.fund-source-detail-page :deep(tbody tr:focus-within .action-buttons) {
  opacity: 1;
  pointer-events: auto;
}

.fund-source-detail-page :deep(thead th) {
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--bg-card);
}

@media (max-width: 980px) {
  .fund-source-detail-page :deep(tbody .action-buttons) {
    opacity: 1;
    pointer-events: auto;
  }
}

/* ── Budget Utilization Card ───────────────────────────────────────────────── */
.utilization-card {
  border-top: 1px solid var(--border-soft);
  border-radius: 0;
}

.utilization-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.utilization-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-secondary);
}

.utilization-percent {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--status-success-text);
}

.utilization-percent.is-success {
  color: var(--status-success-text);
}

.utilization-percent.is-warning {
  color: var(--status-warning-text);
}

.utilization-percent.is-danger {
  color: var(--status-danger-text);
}

.utilization-track {
  height: 6px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: var(--space-3);
}

.utilization-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}

.utilization-fill.fill-success {
  background: var(--status-success-text);
}

.utilization-fill.fill-warning {
  background: var(--status-warning-text);
}

.utilization-fill.fill-danger {
  background: var(--status-danger-text);
}

.utilization-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-2);
  font-size: var(--text-xs);
}

.utilization-ok {
  color: var(--status-success-text);
  font-weight: 500;
}

.utilization-over {
  color: var(--status-danger-text);
  font-weight: 600;
}

.utilization-ratio {
  font-family: 'Courier New', monospace;
  color: var(--text-tertiary);
  font-weight: 500;
}
</style>