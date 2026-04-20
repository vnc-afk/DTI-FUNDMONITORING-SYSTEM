<template>
  <div class="container-fluid">
    <ui-page-header title="Archived transactions" description="Browse and restore fund monitoring records from previous years">
      <RouterLink to="/archive">
        <UiButton variant="secondary" size="md">
          <ui-icon name="chevron-left" size="18" /> Back to archive
        </UiButton>
      </RouterLink>
    </ui-page-header>

    <!-- Search Toolbar -->
    <ui-toolbar>
      <template #filters>
        <search-input
          :model-value="searchInput"
          placeholder="Search by payee, DV #, check #, or date…"
          @update:model-value="searchInput = $event"
          @search="applySearch"
        />
        <UiButton v-if="searchQuery" variant="secondary" type="button" size="md" @click="clearSearch">
          <ui-icon name="x-circle" size="18" /> Clear
        </UiButton>
      </template>
    </ui-toolbar>

    <!-- Summary chips -->
    <div v-if="totalRecords > 0" class="archive-summary-chips">
      <div class="archive-summary-chip">
        <ui-icon name="receipt" size="24" />
        <span class="archive-chip-label">Total records</span>
        <span class="archive-chip-value">{{ formatNumber(totalRecords) }}</span>
      </div>
      <div class="archive-summary-chip">
        <ui-icon name="dollar-sign" size="24" />
        <span class="archive-chip-label">Total amount</span>
        <span class="archive-chip-value">{{ formatCurrency(totalPayments) }}</span>
      </div>
    </div>

    <!-- Search result info -->
    <div v-if="searchQuery" class="archive-search-info">
      <ui-icon name="info" size="18" />
      <span>
        Results for <strong>"{{ searchQuery }}"</strong> —
        {{ formatNumber(totalRecords) }} record{{ totalRecords === 1 ? '' : 's' }} found
      </span>
    </div>

    <!-- Table -->
    <div v-if="transactions.length" class="archive-table-card">
      <div class="archive-table-toolbar">
        <div class="archive-toolbar-title">
          <ui-icon name="check-list" size="18" />
          Transactions
          <span class="archive-record-count">{{ formatNumber(totalRecords) }}</span>
        </div>
        <!-- Type filter pills -->
        <div class="archive-filter-pills">
          <button
            v-for="f in filters"
            :key="f"
            type="button"
            class="archive-filter-pill"
            :class="{ 'is-active': activeFilter === f }"
            @click="setFilter(f)"
          >{{ f }}</button>
        </div>
      </div>

      <div class="archive-table-wrapper">
        <table class="archive-data-table">
          <thead>
            <tr>
              <th class="archive-table-header archive-table-header--expand" />
              <th class="archive-table-header">Date</th>
              <th class="archive-table-header">Payee</th>
              <th class="archive-table-header">Description</th>
              <th class="archive-table-header archive-table-header--right">Amount</th>
              <th class="archive-table-header">Type</th>
              <th class="archive-table-header archive-table-header--right">Action</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="txn in filteredTransactions" :key="txn.id">
              <!-- Main row -->
              <tr
                class="archive-table-row"
                :class="{ 'is-expanded': isExpanded(txn.id) }"
                @click="toggleExpand(txn.id)"
              >
                <td class="archive-table-cell archive-table-cell--center">
                  <ui-icon
                    name="chevron-down"
                    size="18"
                    class="archive-expand-icon"
                    :class="{ 'is-open': isExpanded(txn.id) }"
                  />
                </td>
                <td class="archive-table-cell">
                  <div>{{ formatDate(txn.date) }}</div>
                  <div class="archive-archived-date">
                    <ui-icon name="archive" size="16" /> {{ formatDate(txn.archived_at) }}
                  </div>
                </td>
                <td class="archive-table-cell"><strong>{{ txn.payee || '—' }}</strong></td>
                <td class="archive-table-cell archive-table-cell--muted">{{ truncateWords(txn.particulars, 8) }}</td>
                <td class="archive-table-cell archive-table-cell--right archive-amount-value">{{ formatCurrency(txn.payments) }}</td>
                <td class="archive-table-cell">
                  <UiBadge :variant="typeBadgeVariant(txn.transaction_type)" size="sm">
                    {{ txn.transaction_type || '—' }}
                  </UiBadge>
                </td>
                <td class="archive-table-cell archive-table-cell--right" @click.stop>
                  <UiButton
                    variant="primary"
                    size="sm"
                    :disabled="restoringIds.has(txn.id)"
                    :loading="restoringIds.has(txn.id)"
                    @click="restoreTransaction(txn.id)"
                  >
                    <ui-icon name="rotate-ccw" size="18" /> Restore
                  </UiButton>
                </td>
              </tr>

              <!-- Detail row -->
              <tr v-if="isExpanded(txn.id)" class="archive-detail-row">
                <td colspan="7" class="archive-detail-cell">
                  <div class="archive-detail-grid">

                    <div class="archive-detail-section">
                      <div class="archive-detail-section-title">Transaction info</div>
                      <div class="archive-detail-item"><span class="archive-detail-label">Type</span><span class="archive-detail-value">{{ txn.transaction_type || '—' }}</span></div>
                      <div v-if="txn.cheque_status" class="archive-detail-item"><span class="archive-detail-label">Status</span><span class="archive-detail-value">{{ txn.cheque_status }}</span></div>
                      <div class="archive-detail-item"><span class="archive-detail-label">Date</span><span class="archive-detail-value">{{ formatDate(txn.date) }}</span></div>
                      <div class="archive-detail-item"><span class="archive-detail-label">Archived</span><span class="archive-detail-value">{{ formatDate(txn.archived_at) }}</span></div>
                    </div>

                    <div class="archive-detail-section">
                      <div class="archive-detail-section-title">References</div>
                      <div v-if="txn.dv_number" class="archive-detail-item"><span class="archive-detail-label">DV #</span><span class="archive-detail-value">{{ txn.dv_number }}</span></div>
                      <div v-if="txn.cheque_number" class="archive-detail-item"><span class="archive-detail-label">Check #</span><span class="archive-detail-value">{{ txn.cheque_number }}</span></div>
                      <div v-if="txn.bank_name" class="archive-detail-item"><span class="archive-detail-label">Bank</span><span class="archive-detail-value">{{ txn.bank_name }}</span></div>
                      <div v-if="txn.cleared_date" class="archive-detail-item"><span class="archive-detail-label">Cleared</span><span class="archive-detail-value">{{ formatDate(txn.cleared_date) }}</span></div>
                    </div>

                    <div
                      v-if="txn.division || txn.fund_source || txn.mooe || txn.nc || txn.account_title || txn.expense_classification || txn.staff"
                      class="archive-detail-section"
                    >
                      <div class="archive-detail-section-title">Classification</div>
                      <div v-if="txn.division" class="archive-detail-item"><span class="archive-detail-label">Division</span><span class="archive-detail-value">{{ txn.division }}</span></div>
                      <div v-if="txn.fund_source" class="archive-detail-item"><span class="archive-detail-label">Fund source</span><span class="archive-detail-value">{{ txn.fund_source }}</span></div>
                      <div v-if="txn.mooe" class="archive-detail-item"><span class="archive-detail-label">MOOE</span><span class="archive-detail-value">{{ txn.mooe }}</span></div>
                      <div v-if="txn.nc" class="archive-detail-item"><span class="archive-detail-label">Non-cash</span><span class="archive-detail-value">{{ txn.nc }}</span></div>
                      <div v-if="txn.account_title" class="archive-detail-item"><span class="archive-detail-label">Account title</span><span class="archive-detail-value">{{ txn.account_title }}</span></div>
                      <div v-if="txn.expense_classification" class="archive-detail-item"><span class="archive-detail-label">Classification</span><span class="archive-detail-value">{{ txn.expense_classification }}</span></div>
                      <div v-if="txn.staff" class="archive-detail-item"><span class="archive-detail-label">Staff</span><span class="archive-detail-value">{{ txn.staff }}</span></div>
                    </div>

                    <div v-if="txn.tin || txn.tax_type || txn.purchase_type" class="archive-detail-section">
                      <div class="archive-detail-section-title">Tax & Tin</div>
                      <div v-if="txn.tin" class="archive-detail-item"><span class="archive-detail-label">TIN</span><span class="archive-detail-value">{{ txn.tin }}</span></div>
                      <div v-if="txn.tax_type" class="archive-detail-item"><span class="archive-detail-label">Tax type</span><span class="archive-detail-value">{{ txn.tax_type }}</span></div>
                      <div v-if="txn.purchase_type" class="archive-detail-item"><span class="archive-detail-label">Purchase type</span><span class="archive-detail-value">{{ txn.purchase_type }}</span></div>
                    </div>

                    <div v-if="hasTaxBreakdown(txn)" class="archive-detail-section">
                      <div class="archive-detail-section-title">Tax breakdown</div>
                      <div v-if="amountValue(txn.goods_5_percent)" class="archive-detail-item"><span class="archive-detail-label">Goods 5%</span><span class="archive-detail-value">{{ formatCurrency(txn.goods_5_percent) }}</span></div>
                      <div v-if="amountValue(txn.services_5_percent)" class="archive-detail-item"><span class="archive-detail-label">Services 5%</span><span class="archive-detail-value">{{ formatCurrency(txn.services_5_percent) }}</span></div>
                      <div v-if="amountValue(txn.goods_services_3_percent)" class="archive-detail-item"><span class="archive-detail-label">Goods/Svcs 3%</span><span class="archive-detail-value">{{ formatCurrency(txn.goods_services_3_percent) }}</span></div>
                      <div v-if="amountValue(txn.goods_1_percent)" class="archive-detail-item"><span class="archive-detail-label">Goods 1%</span><span class="archive-detail-value">{{ formatCurrency(txn.goods_1_percent) }}</span></div>
                      <div v-if="amountValue(txn.services_2_percent)" class="archive-detail-item"><span class="archive-detail-label">Services 2%</span><span class="archive-detail-value">{{ formatCurrency(txn.services_2_percent) }}</span></div>
                      <div v-if="amountValue(txn.rental_5_percent)" class="archive-detail-item"><span class="archive-detail-label">Rental 5%</span><span class="archive-detail-value">{{ formatCurrency(txn.rental_5_percent) }}</span></div>
                      <div v-if="amountValue(txn.prof_fee_10_percent)" class="archive-detail-item"><span class="archive-detail-label">Prof fee 10%</span><span class="archive-detail-value">{{ formatCurrency(txn.prof_fee_10_percent) }}</span></div>
                    </div>

                    <div class="archive-detail-section archive-detail-section--full">
                      <div class="archive-detail-section-title">Particulars</div>
                      <div class="archive-detail-particulars">{{ txn.particulars || '—' }}</div>
                    </div>

                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.has_other_pages" class="archive-pagination-controls">
        <button v-if="pagination.has_previous" type="button" class="archive-pagination-btn" @click="goToPage(1)">
          <ui-icon name="chevrons-left" size="18" />
        </button>
        <button v-if="pagination.has_previous" type="button" class="archive-pagination-btn" @click="goToPage(pagination.previous_page)">
          <ui-icon name="chevron-left" size="18" />
        </button>
        <template v-for="num in pagination.page_numbers" :key="`page-${num}`">
          <button
            type="button"
            class="archive-pagination-btn"
            :class="{ 'is-active': pagination.current_page === num }"
            :disabled="pagination.current_page === num"
            @click="goToPage(num)"
          >{{ num }}</button>
        </template>
        <button v-if="pagination.has_next" type="button" class="archive-pagination-btn" @click="goToPage(pagination.next_page)">
          <ui-icon name="chevron-right" size="18" />
        </button>
        <button v-if="pagination.has_next" type="button" class="archive-pagination-btn" @click="goToPage(pagination.total_pages)">
          <ui-icon name="chevrons-right" size="18" />
        </button>
      </div>

    </div>

    <!-- Empty state -->
    <ui-no-results v-else title="No archived transactions found" :description="emptyStateDesc">
      <UiButton v-if="searchQuery" variant="secondary" size="md" @click="clearSearch">
        <ui-icon name="rotate-ccw" size="18" /> Clear search
      </UiButton>
    </ui-no-results>

    <!-- Info box -->
    <div class="archive-info-box">
      <ui-icon name="lightbulb" size="18" class="archive-info-box-icon" />
      <div>
        <strong>What are archived transactions?</strong>
        <span>Archived records are safely stored for reference but hidden from your main dashboard.
          You can restore any transaction using the restore button.</span>
      </div>
    </div>

  </div>

</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import UiIcon from '@/components/ui/UiIcon.vue'
import UiPageHeader from '@/components/ui/UiPageHeader.vue'
import UiToolbar from '@/components/ui/UiToolbar.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiNoResults from '@/components/ui/UiNoResults.vue'
import SearchInput from '@/components/ui/SearchInput.vue'
import '@/assets/css/patterns/archive-list.css'
import { notifyArchiveUpdated } from '@/utils/archiveRefresh'

import { fetchArchivedTransactions, restoreArchivedTransaction } from '@/services/archiveService'

const route = useRoute()
const router = useRouter()

const searchInput = ref('')
const searchQuery = ref('')
const transactions = ref([])
const expandedRowIds = ref(new Set())
const restoringIds = ref(new Set())
const activeFilter = ref('All')
const filters = ['All', 'Check', 'Cash', 'ADA']

const emptyStateDesc = computed(() => {
  if (searchQuery.value) {
    return `No results for "${searchQuery.value}" • Try a different search term or clear filters`
  }
  return "You haven't archived any transactions yet • Archived records from completed years will appear here"
})

const totalRecords = ref(0)
const totalPayments = ref(0)
const pagination = ref({
  has_other_pages: false,
  has_previous: false,
  has_next: false,
  current_page: 1,
  total_pages: 1,
  previous_page: null,
  next_page: null,
  page_numbers: [],
})

const filteredTransactions = computed(() => {
  if (activeFilter.value === 'All') return transactions.value
  return transactions.value.filter((t) => t.transaction_type === activeFilter.value)
})

function setFilter(f) {
  activeFilter.value = f
  expandedRowIds.value = new Set()
}

function typeCls(type) {
  if (type === 'Check') return 'check'
  if (type === 'Cash')  return 'cash'
  if (type === 'ADA')   return 'ada'
  return 'other'
}

function typeBadgeVariant(type) {
  if (type === 'Check') return 'info'
  if (type === 'Cash')  return 'success'
  if (type === 'ADA')   return 'warning'
  return 'neutral'
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString()
}

function formatCurrency(value) {
  const amount = Number(value || 0)
  return `₱${amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })
}

function truncateWords(value, limit) {
  const text = String(value || '').trim()
  if (!text) return '—'
  const words = text.split(/\s+/)
  return words.length <= limit ? text : `${words.slice(0, limit).join(' ')}…`
}

function amountValue(value) {
  return Number(value || 0) > 0
}

function hasTaxBreakdown(txn) {
  return (
    amountValue(txn.goods_5_percent)
    || amountValue(txn.services_5_percent)
    || amountValue(txn.goods_services_3_percent)
    || amountValue(txn.goods_1_percent)
    || amountValue(txn.services_2_percent)
    || amountValue(txn.rental_5_percent)
    || amountValue(txn.prof_fee_10_percent)
  )
}

function isExpanded(id) {
  return expandedRowIds.value.has(id)
}

function toggleExpand(id) {
  const next = new Set(expandedRowIds.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  expandedRowIds.value = next
}

function currentPageFromRoute() {
  const page = Number(route.query.page || 1)
  return Number.isNaN(page) || page < 1 ? 1 : page
}

async function loadTransactions() {
  const payload = await fetchArchivedTransactions({
    q: searchQuery.value || undefined,
    page: currentPageFromRoute(),
  })
  searchQuery.value = payload?.search_query || ''
  searchInput.value = searchQuery.value
  transactions.value = Array.isArray(payload?.results) ? payload.results : []
  totalRecords.value = Number(payload?.total_records || 0)
  totalPayments.value = Number(payload?.total_payments || 0)
  pagination.value = payload?.pagination || pagination.value
  expandedRowIds.value = new Set()
}

async function applySearch() {
  await router.replace({ query: { ...(searchInput.value ? { q: searchInput.value } : {}), page: 1 } })
  searchQuery.value = searchInput.value
  await loadTransactions()
}

async function clearSearch() {
  searchInput.value = ''
  searchQuery.value = ''
  await router.replace({ query: { page: 1 } })
  await loadTransactions()
}

async function goToPage(page) {
  await router.replace({ query: { ...(searchQuery.value ? { q: searchQuery.value } : {}), page: Number(page || 1) } })
  await loadTransactions()
}

async function restoreTransaction(transactionId) {
  const next = new Set(restoringIds.value)
  next.add(transactionId)
  restoringIds.value = next

  try {
    const payload = await restoreArchivedTransaction(transactionId)
    if (payload?.success) {
      window.alert(payload?.message || 'Transaction restored successfully.')
      await loadTransactions()
      notifyArchiveUpdated({ action: 'restore-transaction', transactionId })
    } else {
      window.alert(payload?.error || 'Failed to restore transaction')
    }
  } catch (error) {
    window.alert(error?.response?.data?.detail || error?.response?.data?.error || error?.message || 'Unknown error')
  } finally {
    const updated = new Set(restoringIds.value)
    updated.delete(transactionId)
    restoringIds.value = updated
  }
}

onMounted(async () => {
  searchInput.value = String(route.query.q || '')
  searchQuery.value = searchInput.value
  await loadTransactions()
})
</script>
  