<template>
  <div class="container-fluid">
    <ui-page-header title="Archived bank statements" description="Browse and restore records safely stored from previous years">
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
          placeholder="Search by description, check #, or date…"
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
        <span class="archive-chip-label">Total debit</span>
        <span class="archive-chip-value">{{ formatCurrency(totalDebit) }}</span>
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
    <div v-if="statements.length" class="archive-table-card">
      <div class="archive-table-toolbar">
        <div class="archive-toolbar-title">
          <ui-icon name="building-2" size="18" />
          Bank statements
          <span class="archive-record-count">{{ formatNumber(totalRecords) }}</span>
        </div>
      </div>

      <div class="archive-table-wrapper">
        <table class="archive-data-table">
          <thead>
            <tr>
              <th class="archive-table-header archive-table-header--expand" />
              <th class="archive-table-header">Date</th>
              <th class="archive-table-header">Description</th>
              <th class="archive-table-header archive-table-header--center">Check #</th>
              <th class="archive-table-header archive-table-header--right">Debit</th>
              <th class="archive-table-header archive-table-header--right">Credit</th>
              <th class="archive-table-header archive-table-header--right">Action</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="stmt in statements" :key="stmt.id">
              <!-- Main row -->
              <tr
                class="archive-table-row"
                :class="{ 'is-expanded': isExpanded(stmt.id) }"
                @click="toggleExpand(stmt.id)"
              >
                <td class="archive-table-cell archive-table-cell--center">
                  <ui-icon
                    name="chevron-down"
                    size="18"
                    class="archive-expand-icon"
                    :class="{ 'is-open': isExpanded(stmt.id) }"
                  />
                </td>
                <td class="archive-table-cell">{{ formatDate(stmt.date) }}</td>
                <td class="archive-table-cell"><strong>{{ stmt.description }}</strong></td>
                <td class="archive-table-cell archive-table-cell--center archive-table-cell--muted">{{ stmt.check_number || '—' }}</td>
                <td class="archive-table-cell archive-table-cell--right archive-amount-debit">
                  {{ stmt.debit ? formatCurrency(stmt.debit) : '—' }}
                </td>
                <td class="archive-table-cell archive-table-cell--right archive-amount-credit">
                  {{ stmt.credit ? formatCurrency(stmt.credit) : '—' }}
                </td>
                <td class="archive-table-cell archive-table-cell--right" @click.stop>
                  <UiButton
                    variant="primary"
                    size="sm"
                    :disabled="restoringIds.has(stmt.id)"
                    :loading="restoringIds.has(stmt.id)"
                    @click="restoreStatement(stmt.id)"
                  >
                    <ui-icon name="rotate-ccw" size="18" /> Restore
                  </UiButton>
                </td>
              </tr>

              <!-- Detail row -->
              <tr v-if="isExpanded(stmt.id)" class="archive-detail-row">
                <td colspan="7" class="archive-detail-cell">
                  <div class="archive-detail-grid">
                    <div class="archive-detail-section">
                      <div class="archive-detail-section-title">Statement info</div>
                      <div class="archive-detail-item">
                        <span class="archive-detail-label">Statement date</span>
                        <span class="archive-detail-value">{{ formatDate(stmt.date) }}</span>
                      </div>
                      <div class="archive-detail-item">
                        <span class="archive-detail-label">Archived on</span>
                        <span class="archive-detail-value">{{ formatDate(stmt.archived_at) }}</span>
                      </div>
                      <div class="archive-detail-item">
                        <span class="archive-detail-label">Balance</span>
                        <span class="archive-detail-value"><strong>{{ formatCurrency(stmt.balance) }}</strong></span>
                      </div>
                      <div class="archive-detail-item">
                        <span class="archive-detail-label">Status</span>
                        <UiBadge variant="neutral" size="sm">Archived</UiBadge>
                      </div>
                    </div>
                    <div class="archive-detail-section">
                      <div class="archive-detail-section-title">Totals</div>
                      <div class="archive-detail-item">
                        <span class="archive-detail-label">Total debit</span>
                        <span class="archive-detail-value archive-amount-debit"><strong>{{ formatCurrency(stmt.debit) }}</strong></span>
                      </div>
                      <div class="archive-detail-item">
                        <span class="archive-detail-label">Total credit</span>
                        <span class="archive-detail-value archive-amount-credit"><strong>{{ formatCurrency(stmt.credit) }}</strong></span>
                      </div>
                    </div>
                    <div class="archive-detail-section">
                      <div class="archive-detail-section-title">Description</div>
                      <div class="archive-detail-item">
                        <span class="archive-detail-label">Details</span>
                        <span class="archive-detail-value">{{ stmt.description }}</span>
                      </div>
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
    <ui-no-results v-else title="No archived bank statements found" :description="emptyStateDesc">
      <UiButton v-if="searchQuery" variant="secondary" size="md" @click="clearSearch">
        <ui-icon name="rotate-ccw" size="18" /> Clear search
      </UiButton>
    </ui-no-results>

    <!-- Info box -->
    <div class="archive-info-box">
      <ui-icon name="lightbulb" size="18" class="archive-info-box-icon" />
      <div>
        <strong>What are archived bank statements?</strong>
        <span>Archived records are safely stored for reference but hidden from your main dashboard.
          You can restore any statement using the restore button.</span>
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

import { fetchArchivedStatements, restoreArchivedStatement } from '@/services/archiveService'

const route = useRoute()
const router = useRouter()

const searchInput = ref('')
const searchQuery = ref('')
const statements = ref([])
const expandedRowIds = ref(new Set())
const restoringIds = ref(new Set())

const emptyStateDesc = computed(() => {
  if (searchQuery.value) {
    return `No results for "${searchQuery.value}" • Try a different search term or clear filters`
  }
  return "You haven't archived any bank statements yet • Archived records from completed years will appear here"
})

const totalRecords = ref(0)
const totalDebit = ref(0)
const totalCredit = ref(0)
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

async function loadStatements() {
  const payload = await fetchArchivedStatements({
    q: searchQuery.value || undefined,
    page: currentPageFromRoute(),
  })
  searchQuery.value = payload?.search_query || ''
  searchInput.value = searchQuery.value
  statements.value = Array.isArray(payload?.results) ? payload.results : []
  totalRecords.value = Number(payload?.total_records || 0)
  totalDebit.value = Number(payload?.total_debit || 0)
  totalCredit.value = Number(payload?.total_credit || 0)
  pagination.value = payload?.pagination || pagination.value
  expandedRowIds.value = new Set()
}

async function applySearch() {
  await router.replace({ query: { ...(searchInput.value ? { q: searchInput.value } : {}), page: 1 } })
  searchQuery.value = searchInput.value
  await loadStatements()
}

async function clearSearch() {
  searchInput.value = ''
  searchQuery.value = ''
  await router.replace({ query: { page: 1 } })
  await loadStatements()
}

async function goToPage(page) {
  await router.replace({ query: { ...(searchQuery.value ? { q: searchQuery.value } : {}), page: Number(page || 1) } })
  await loadStatements()
}

async function restoreStatement(statementId) {
  const next = new Set(restoringIds.value)
  next.add(statementId)
  restoringIds.value = next

  try {
    const payload = await restoreArchivedStatement(statementId)
    if (payload?.success) {
      window.alert(payload?.message || 'Statement restored successfully.')
      await loadStatements()
      notifyArchiveUpdated({ action: 'restore-statement', statementId })
    } else {
      window.alert(payload?.error || 'Failed to restore statement')
    }
  } catch (error) {
    window.alert(error?.response?.data?.detail || error?.response?.data?.error || error?.message || 'Unknown error')
  } finally {
    const updated = new Set(restoringIds.value)
    updated.delete(statementId)
    restoringIds.value = updated
  }
}

onMounted(async () => {
  searchInput.value = String(route.query.q || '')
  searchQuery.value = searchInput.value
  await loadStatements()
})
</script>