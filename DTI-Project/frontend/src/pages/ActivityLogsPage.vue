<template>
  <div class="activity-logs-page">
    <!-- Header -->
    <header class="page-header">
      <div class="page-header-info">
        <div class="page-header-eyebrow">
          <ui-icon name="history" size="20" />
          <span>Activity Logs</span>
        </div>
        <h1 class="page-header-title">User Activity & System Changes</h1>
        <p class="page-header-desc">Track all user activities and system changes across the platform</p>
      </div>
      <RouterLink to="/activity-logs/summary" class="btn-primary-action">
        <ui-icon name="trending-up" size="20" />
        <span>View Summary</span>
        <ui-icon name="arrow-right" size="20" class="btn-arrow" />
      </RouterLink>
    </header>

    <!-- Filters -->
    <div class="filter-bar">
      <div class="filter-bar-row">
        <!-- Search -->
        <div class="search-wrap">
          <ui-icon name="search" size="20" class="search-icon" />
          <input
            v-model="filters.search"
            type="text"
            class="search-input"
            placeholder="Search object, description, user…"
            @keydown.enter="applyFilters"
          />
          <button v-if="filters.search" class="search-clear" @click="filters.search = ''; applyFilters()">
            <ui-icon name="x" size="18" />
          </button>
        </div>

        <!-- Filter selects -->
        <div class="filter-selects">
          <label class="filter-select-wrap">
            <span class="filter-select-label">Action</span>
            <select v-model="filters.action" class="filter-select" @change="applyFilters">
              <option value="">All Actions</option>
              <option v-for="a in actionOptions" :key="a.code" :value="a.code">{{ a.name }}</option>
            </select>
            <ui-icon name="chevron-down" size="18" class="filter-select-caret" />
          </label>

          <label class="filter-select-wrap">
            <span class="filter-select-label">User</span>
            <select v-model="filters.user" class="filter-select" @change="applyFilters">
              <option value="">All Users</option>
              <option v-for="u in userOptions" :key="u.id" :value="String(u.id)">{{ u.display_name }}</option>
            </select>
            <ui-icon name="chevron-down" size="18" class="filter-select-caret" />
          </label>

          <label class="filter-select-wrap">
            <span class="filter-select-label">Model</span>
            <select v-model="filters.model" class="filter-select" @change="applyFilters">
              <option value="">All Models</option>
              <option v-for="m in modelOptions" :key="m" :value="m">{{ m }}</option>
            </select>
            <ui-icon name="chevron-down" size="18" class="filter-select-caret" />
          </label>

          <label class="filter-select-wrap">
            <span class="filter-select-label">Date</span>
            <select v-model="filters.date" class="filter-select" @change="applyFilters">
              <option value="">All Time</option>
              <option value="today">Today</option>
              <option value="week">Last 7 Days</option>
              <option value="month">Last 30 Days</option>
            </select>
            <ui-icon name="chevron-down" size="18" class="filter-select-caret" />
          </label>
        </div>

        <!-- Actions -->
        <div class="filter-actions">
          <button class="btn-filter-apply" @click="applyFilters">
            <ui-icon name="filter" size="18" /> Filter
          </button>
          <button v-if="hasActiveFilters" class="btn-filter-reset" @click="resetFilters">
            <ui-icon name="x-circle" size="18" /> Clear
          </button>
        </div>
      </div>

      <!-- Active filter chips -->
      <div v-if="hasActiveFilters" class="filter-chips">
        <span v-if="filters.search" class="filter-chip">
          Search: "{{ filters.search }}"
          <button @click="filters.search = ''; applyFilters()"><ui-icon name="x" size="16" /></button>
        </span>
        <span v-if="filters.action" class="filter-chip">
          Action: {{ filters.action }}
          <button @click="filters.action = ''; applyFilters()"><ui-icon name="x" size="16" /></button>
        </span>
        <span v-if="filters.user" class="filter-chip">
          User: {{ userOptions.find(u => String(u.id) === filters.user)?.display_name || filters.user }}
          <button @click="filters.user = ''; applyFilters()"><ui-icon name="x" size="16" /></button>
        </span>
        <span v-if="filters.model" class="filter-chip">
          Model: {{ filters.model }}
          <button @click="filters.model = ''; applyFilters()"><ui-icon name="x" size="16" /></button>
        </span>
        <span v-if="filters.date" class="filter-chip">
          {{ { today: 'Today', week: 'Last 7 Days', month: 'Last 30 Days' }[filters.date] }}
          <button @click="filters.date = ''; applyFilters()"><ui-icon name="x" size="16" /></button>
        </span>
      </div>
    </div>

    <!-- Results bar -->
    <div class="results-bar">
      <span class="results-count">{{ formatNumber(totalLogs) }}</span>
      <span class="results-label">activities found</span>
      <span v-if="totalPages > 1" class="results-sep">·</span>
      <span v-if="totalPages > 1" class="results-label">page {{ currentPage }} of {{ totalPages }}</span>
    </div>

    <!-- Table -->
    <div class="table-card">
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 150px">Timestamp</th>
              <th style="width: 200px">User</th>
              <th style="width: 110px">Action</th>
              <th>Model</th>
              <th>Object</th>
              <th style="width: 56px" class="text-center">↗</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!logs.length">
              <td colspan="6">
                <div class="empty-state">
                  <div class="empty-icon-wrap">
                    <ui-icon name="inbox" size="32" />
                  </div>
                  <p class="empty-title">No activity logs found</p>
                  <p class="empty-sub">Try adjusting your filters or search query</p>
                </div>
              </td>
            </tr>

            <tr
              v-for="log in logs"
              :key="log.id"
              class="table-row"
              :class="{ 'table-row--delete': log.action === 'DELETE' }"
              @click="activeLog = log"
            >
              <td>
                <div class="time-cell">
                  <span class="time-primary">{{ formatRelativeTime(log.timestamp) }}</span>
                  <span class="time-secondary">{{ formatDateTime(log.timestamp) }}</span>
                </div>
              </td>

              <td>
                <div class="user-cell">
                  <div class="avatar" :style="{ background: avatarColor(log.user_full_name) }">
                    {{ initials(log.user_full_name) }}
                  </div>
                  <div class="user-info">
                    <span class="user-name">{{ log.user_full_name }}</span>
                    <div class="user-badges">
                      <span v-if="log.user_is_superuser" class="role-badge role-badge--super">Superuser</span>
                      <span v-else-if="log.user_is_staff" class="role-badge role-badge--staff">Staff</span>
                      <span v-if="log.user_groups?.length" class="user-group">{{ log.user_groups.join(', ') }}</span>
                    </div>
                  </div>
                </div>
              </td>

              <td>
                <span class="action-tag" :class="`action-tag--${(log.action || '').toLowerCase()}`">
                  {{ log.action_display }}
                </span>
              </td>

              <td>
                <RouterLink
                  :to="`/activity-logs/model/${encodeURIComponent(log.model_name)}`"
                  class="model-link"
                  @click.stop
                >{{ log.model_name }}</RouterLink>
              </td>

              <td>
                <code v-if="log.object_repr" class="obj-code">{{ truncateWords(log.object_repr, 5) }}</code>
                <span v-else class="text-muted">—</span>
              </td>

              <td class="text-center">
                <button class="detail-btn" title="View details" @click.stop="activeLog = log">
                  <ui-icon name="arrow-right" size="18" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <nav v-if="totalPages > 1" class="pagination" aria-label="Page navigation">
      <button class="page-btn" :disabled="currentPage <= 1" @click="goToPage(1)" title="First">
        <ui-icon name="chevrons-left" size="18" />
      </button>
      <button class="page-btn" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)" title="Previous">
        <ui-icon name="chevron-left" size="18" />
      </button>

      <span v-if="visiblePages[0] > 1" class="page-ellipsis">…</span>
      <button
        v-for="num in visiblePages"
        :key="num"
        class="page-btn"
        :class="{ 'page-btn--active': currentPage === num }"
        @click="goToPage(num)"
      >{{ num }}</button>
      <span v-if="visiblePages[visiblePages.length - 1] < totalPages" class="page-ellipsis">…</span>

      <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)" title="Next">
        <ui-icon name="chevron-right" size="18" />
      </button>
      <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(totalPages)" title="Last">
        <ui-icon name="chevrons-right" size="18" />
      </button>
    </nav>

    <!-- Detail Drawer / Modal -->
    <Teleport to="body">
      <Transition name="drawer">
        <div v-if="activeLog" class="drawer-overlay" @click.self="activeLog = null">
          <div class="drawer">
            <!-- Drawer Header -->
            <div class="drawer-header">
              <div class="drawer-title-group">
                <span class="action-tag" :class="`action-tag--${(activeLog.action || '').toLowerCase()}`">
                  {{ activeLog.action_display }}
                </span>
                <h2 class="drawer-title">Activity Details</h2>
              </div>
              <button class="drawer-close" @click="activeLog = null">
                <ui-icon name="x-lg" />
              </button>
            </div>

            <!-- Drawer Body -->
            <div class="drawer-body">
              <!-- Meta grid -->
              <div class="detail-grid">
                <div class="detail-field">
                  <span class="detail-label">User</span>
                  <div class="detail-user">
                    <div class="avatar avatar--sm" :style="{ background: avatarColor(activeLog.user_full_name) }">
                      {{ initials(activeLog.user_full_name) }}
                    </div>
                    <span class="detail-value">{{ activeLog.user_full_name }}</span>
                  </div>
                </div>
                <div class="detail-field">
                  <span class="detail-label">Model</span>
                  <span class="detail-value">{{ activeLog.model_name }}</span>
                </div>
                <div class="detail-field">
                  <span class="detail-label">Timestamp</span>
                  <span class="detail-value">{{ activeLog.formatted_timestamp }}</span>
                </div>
                <div class="detail-field">
                  <span class="detail-label">IP Address</span>
                  <code class="detail-code">{{ activeLog.ip_address || 'Unknown' }}</code>
                </div>
              </div>

              <!-- Description -->
              <template v-if="activeLog.description">
                <div class="drawer-section">
                  <h3 class="drawer-section-title">Description</h3>
                  <p class="drawer-section-text">{{ activeLog.description }}</p>
                </div>
              </template>

              <!-- Changed Fields -->
              <template v-if="activeLog.changed_fields && Object.keys(activeLog.changed_fields).length">
                <div class="drawer-section">
                  <h3 class="drawer-section-title">
                    Changed Fields
                    <span class="section-count">{{ Object.keys(activeLog.changed_fields).length }}</span>
                  </h3>
                  <div class="diff-table-wrap">
                    <table class="diff-table">
                      <thead>
                        <tr>
                          <th>Field</th>
                          <th>Before</th>
                          <th>After</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="entry in changedFieldEntries(activeLog.changed_fields)" :key="entry.field">
                          <td><strong>{{ entry.field }}</strong></td>
                          <td><code class="diff-old">{{ entry.oldValue }}</code></td>
                          <td><code class="diff-new">{{ entry.newValue }}</code></td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </template>

              <!-- User Agent -->
              <template v-if="activeLog.user_agent">
                <div class="drawer-section">
                  <h3 class="drawer-section-title">User Agent</h3>
                  <code class="detail-code detail-code--block">{{ activeLog.user_agent }}</code>
                </div>
              </template>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import UiIcon from '@/components/ui/UiIcon.vue'
import { fetchActivityLogFilters, fetchActivityLogs } from '@/services/activityLogsService'

const logs = ref([])
const totalLogs = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const actionOptions = ref([])
const userOptions = ref([])
const modelOptions = ref([])
const activeLog = ref(null)

const filters = ref({ search: '', action: '', user: '', model: '', date: '' })

const hasActiveFilters = computed(() =>
  Object.values(filters.value).some(v => v !== '')
)

const totalPages = computed(() =>
  Math.max(Math.ceil(totalLogs.value / Math.max(pageSize.value, 1)), 1)
)

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

/* ── Helpers ──────────────────────────────────── */

function formatNumber(value) {
  return Number(value || 0).toLocaleString()
}

function truncateWords(text, count) {
  const src = String(text || '').trim()
  const words = src.split(/\s+/)
  return words.length <= count ? src : `${words.slice(0, count).join(' ')}…`
}

function formatDateTime(value) {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

function formatRelativeTime(value) {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  const diff = Math.round((d.getTime() - Date.now()) / 1000)
  const abs = Math.abs(diff)
  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })
  if (abs < 60) return rtf.format(diff, 'second')
  const mins = Math.round(diff / 60)
  if (Math.abs(mins) < 60) return rtf.format(mins, 'minute')
  const hrs = Math.round(mins / 60)
  if (Math.abs(hrs) < 24) return rtf.format(hrs, 'hour')
  return rtf.format(Math.round(hrs / 24), 'day')
}

function changedFieldEntries(changedFields) {
  if (!changedFields || typeof changedFields !== 'object') return []
  return Object.entries(changedFields).map(([field, changes]) => ({
    field,
    oldValue: changes?.old ?? '(empty)',
    newValue: changes?.new ?? '(empty)',
  }))
}

const AVATAR_COLORS = ['#7c3aed','#2563eb','#0891b2','#059669','#d97706','#dc2626','#db2777']

function avatarColor(name) {
  let hash = 0
  for (const ch of String(name || '')) hash = (hash * 31 + ch.charCodeAt(0)) & 0xffffffff
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length]
}

function initials(name) {
  const parts = String(name || '').trim().split(/\s+/)
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
  return String(name || '?')[0].toUpperCase()
}

/* ── Data loading ─────────────────────────────── */

function getParams() {
  const p = { page: currentPage.value }
  if (filters.value.search) p.search = filters.value.search
  if (filters.value.action) p.action = filters.value.action
  if (filters.value.user) p.user = filters.value.user
  if (filters.value.model) p.model = filters.value.model
  if (filters.value.date) p.date = filters.value.date
  return p
}

async function loadLogs() {
  const payload = await fetchActivityLogs(getParams())
  const rows = Array.isArray(payload?.results) ? payload.results : []
  logs.value = rows
  totalLogs.value = Number(payload?.count || rows.length || 0)
  if (rows.length > 0) pageSize.value = rows.length
}

async function loadFilterOptions() {
  const payload = await fetchActivityLogFilters()
  actionOptions.value = Array.isArray(payload?.actions) ? payload.actions : []
  userOptions.value = Array.isArray(payload?.users) ? payload.users : []
  modelOptions.value = Array.isArray(payload?.models) ? payload.models : []
}

async function applyFilters() {
  currentPage.value = 1
  await loadLogs()
}

async function goToPage(page) {
  currentPage.value = Math.min(Math.max(Number(page || 1), 1), totalPages.value)
  await loadLogs()
}

async function resetFilters() {
  filters.value = { search: '', action: '', user: '', model: '', date: '' }
  currentPage.value = 1
  await loadLogs()
}

onMounted(async () => {
  await Promise.all([loadFilterOptions(), loadLogs()])
})
</script>

<style scoped>
.activity-logs-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: var(--space-7) var(--space-5) var(--space-10);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  font-family: var(--font-sans);
}

/* ── Page Header ─────────────────────────────── */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--border-subtle);
}

.page-header-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--brand-navy-700);
  margin-bottom: var(--space-2);
}

.page-header-title {
  font-size: clamp(1.35rem, 3vw, 1.875rem);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.page-header-desc {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.6;
}

.btn-primary-action {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 0.625rem var(--space-4);
  background: var(--brand-navy-700);
  color: #fff;
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  text-decoration: none;
  white-space: nowrap;
  transition: background var(--duration-fast), gap var(--duration-fast);
  align-self: flex-start;
  flex-shrink: 0;
}

.btn-primary-action:hover { background: var(--brand-navy-900); gap: var(--space-3); }
.btn-arrow { font-size: 12px; opacity: 0.7; }

/* ── Filter Bar ──────────────────────────────── */
.filter-bar {
  background: var(--surface-base);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.filter-bar-row {
  display: flex;
  align-items: flex-end;
  gap: var(--space-3);
  flex-wrap: wrap;
}

/* Search */
.search-wrap {
  position: relative;
  flex: 1;
  min-width: 220px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 13px;
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.5rem 2.25rem 0.5rem 2.25rem;
  font-size: var(--text-sm);
  font-family: var(--font-sans);
  background: var(--surface-subtle);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  outline: none;
  transition: border-color var(--duration-fast), box-shadow var(--duration-fast);
  box-sizing: border-box;
}

.search-input:focus {
  border-color: var(--brand-navy-500, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
  background: var(--surface-base);
}

.search-input::placeholder { color: var(--text-muted); }

.search-clear {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px;
  border-radius: 4px;
  font-size: 13px;
  transition: color var(--duration-fast);
}

.search-clear:hover { color: var(--text-primary); }

/* Filter selects */
.filter-selects {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.filter-select-wrap {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-select-label {
  font-size: 0.625rem;
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--text-muted);
  padding-left: 2px;
}

.filter-select {
  appearance: none;
  -webkit-appearance: none;
  padding: 0.4375rem 2rem 0.4375rem 0.75rem;
  font-size: var(--text-sm);
  font-family: var(--font-sans);
  background: var(--surface-subtle);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  cursor: pointer;
  outline: none;
  min-width: 120px;
  transition: border-color var(--duration-fast), box-shadow var(--duration-fast);
}

.filter-select:focus {
  border-color: var(--brand-navy-500, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.filter-select-caret {
  position: absolute;
  right: 9px;
  bottom: 10px;
  font-size: 10px;
  color: var(--text-muted);
  pointer-events: none;
}

/* Filter action buttons */
.filter-actions {
  display: flex;
  gap: var(--space-2);
  align-items: flex-end;
  padding-bottom: 1px;
}

.btn-filter-apply {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 0.4375rem var(--space-4);
  background: var(--brand-navy-700);
  color: #fff;
  border: none;
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  cursor: pointer;
  transition: background var(--duration-fast);
  white-space: nowrap;
}

.btn-filter-apply:hover { background: var(--brand-navy-900); }

.btn-filter-reset {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 0.4375rem var(--space-3);
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  cursor: pointer;
  transition: all var(--duration-fast);
  white-space: nowrap;
}

.btn-filter-reset:hover {
  background: var(--surface-subtle);
  color: var(--text-primary);
}

/* Active filter chips */
.filter-chips {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
  padding-top: var(--space-1);
  border-top: 1px solid var(--border-subtle);
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: 3px 8px 3px 10px;
  background: var(--brand-navy-50, #eff6ff);
  border: 1px solid var(--brand-navy-200, #bfdbfe);
  border-radius: 99px;
  font-size: var(--text-xs);
  color: var(--brand-navy-700);
  font-weight: var(--weight-medium);
}

.filter-chip button {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: var(--brand-navy-500);
  padding: 0;
  font-size: 11px;
  transition: color var(--duration-fast);
}

.filter-chip button:hover { color: var(--brand-navy-900); }

/* ── Results Bar ─────────────────────────────── */
.results-bar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  padding: 0 var(--space-1);
}

.results-count {
  font-weight: var(--weight-bold);
  font-size: var(--text-base);
  color: var(--text-primary);
}

.results-sep { color: var(--border-default); }

/* ── Table ───────────────────────────────────── */
.table-card {
  background: var(--surface-base);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--text-primary);
}

.data-table thead tr {
  background: var(--surface-subtle);
  border-bottom: 1px solid var(--border-default);
}

.data-table th {
  padding: var(--space-3) var(--space-3);
  text-align: left;
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  white-space: nowrap;
}

.data-table tbody tr {
  border-bottom: 1px solid var(--border-subtle);
  cursor: pointer;
  transition: background var(--duration-fast);
}

.data-table tbody tr:last-child { border-bottom: none; }
.data-table tbody tr:hover { background: var(--surface-subtle); }

.table-row--delete { border-left: 2px solid #fca5a5; }

.data-table td {
  padding: var(--space-3) var(--space-3);
  font-size: var(--text-base);
  font-weight: var(--weight-regular);
  vertical-align: middle;
  color: var(--text-primary);
  line-height: var(--leading-normal);
  height: 56px;
}

.text-center { text-align: center; }
.text-muted { color: var(--text-muted); }

/* Time cell */
.time-cell { display: flex; flex-direction: column; gap: 2px; }
.time-primary { font-size: var(--text-base); font-weight: var(--weight-medium); color: var(--text-primary); }
.time-secondary { font-size: var(--text-sm); color: var(--text-muted); }

/* User cell */
.user-cell { display: flex; align-items: center; gap: var(--space-2); }

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  font-weight: var(--weight-bold);
  color: #fff;
  flex-shrink: 0;
  letter-spacing: 0.03em;
}

.avatar--sm { width: 26px; height: 26px; border-radius: 6px; }

.user-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.user-name { font-size: var(--text-base); color: var(--text-primary); font-weight: var(--weight-medium); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.user-badges { display: flex; align-items: center; gap: var(--space-1); flex-wrap: wrap; }

.user-group { font-size: var(--text-xs); color: var(--text-muted); }

/* Model link */
.model-link {
  font-size: var(--text-base);
  color: var(--brand-navy-700);
  text-decoration: none;
  font-weight: var(--weight-medium);
  transition: text-decoration var(--duration-fast);
}

.model-link:hover { text-decoration: underline; }

/* Object code */
.obj-code {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  background: var(--surface-subtle);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
}

/* Detail button */
.detail-btn {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  border: 1px solid var(--border-default);
  background: var(--surface-base);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.detail-btn:hover {
  background: var(--brand-navy-700);
  color: #fff;
  border-color: var(--brand-navy-700);
  transform: translateX(1px);
}

/* ── Empty State ─────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12) var(--space-4);
  gap: var(--space-2);
}

.empty-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: var(--surface-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-2);
}

.empty-icon-wrap i { font-size: 1.5rem; color: var(--text-muted); }

.empty-title {
  margin: 0;
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
}

.empty-sub {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-muted);
}

/* ── Pagination ──────────────────────────────── */
.pagination {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  justify-content: center;
  flex-wrap: wrap;
}

.page-btn {
  min-width: 34px;
  height: 34px;
  padding: 0 var(--space-2);
  border-radius: 8px;
  border: 1px solid var(--border-default);
  background: var(--surface-base);
  font-size: var(--text-sm);
  font-family: var(--font-sans);
  font-weight: var(--weight-medium);
  color: var(--text-secondary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast);
}

.page-btn:hover:not(:disabled) {
  background: var(--surface-subtle);
  color: var(--text-primary);
  border-color: var(--border-default);
}

.page-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.page-btn--active {
  background: var(--brand-navy-700);
  color: #fff;
  border-color: var(--brand-navy-700);
  font-weight: var(--weight-bold);
}

.page-ellipsis {
  font-size: var(--text-sm);
  color: var(--text-muted);
  padding: 0 var(--space-1);
}

/* ── Drawer ──────────────────────────────────── */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(2px);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}

.drawer {
  width: min(560px, 100vw);
  height: 100%;
  background: var(--surface-base);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: -8px 0 40px rgba(0, 0, 0, 0.15);
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-default);
  background: var(--surface-subtle);
  flex-shrink: 0;
}

.drawer-title-group {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.drawer-title {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.drawer-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid var(--border-default);
  background: var(--surface-base);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all var(--duration-fast);
  flex-shrink: 0;
}

.drawer-close:hover {
  background: var(--surface-subtle);
  color: var(--text-primary);
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

/* Detail grid */
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

@media (max-width: 500px) { .detail-grid { grid-template-columns: 1fr; } }

.detail-field { display: flex; flex-direction: column; gap: var(--space-2); }

.detail-label {
  font-size: 0.6875rem;
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--text-muted);
}

.detail-user { display: flex; align-items: center; gap: var(--space-2); }

.detail-value {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--weight-medium);
}

.detail-code {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  background: var(--surface-subtle);
  padding: 3px 8px;
  border-radius: 5px;
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
  display: inline-block;
}

.detail-code--block {
  display: block;
  white-space: pre-wrap;
  word-break: break-all;
  padding: var(--space-3);
  line-height: 1.6;
}

/* Drawer sections */
.drawer-section { display: flex; flex-direction: column; gap: var(--space-3); }

.drawer-section-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 0.6875rem;
  font-weight: var(--weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--text-secondary);
  margin: 0;
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--border-subtle);
}

.section-count {
  background: var(--surface-subtle);
  border: 1px solid var(--border-subtle);
  border-radius: 99px;
  padding: 1px 7px;
  font-size: 0.625rem;
  color: var(--text-muted);
}

.drawer-section-text {
  font-size: var(--text-sm);
  color: var(--text-primary);
  line-height: 1.65;
  margin: 0;
  white-space: pre-wrap;
}

/* Diff table */
.diff-table-wrap { overflow-x: auto; border-radius: var(--radius-lg); border: 1px solid var(--border-default); }

.diff-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-xs);
}

.diff-table th {
  padding: var(--space-2) var(--space-3);
  text-align: left;
  font-size: 0.625rem;
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  background: var(--surface-subtle);
  border-bottom: 1px solid var(--border-default);
}

.diff-table td {
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--border-subtle);
  vertical-align: top;
}

.diff-table tr:last-child td { border-bottom: none; }

.diff-old {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  background: #fee2e2;
  color: #991b1b;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
}

.diff-new {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  background: #dcfce7;
  color: #166534;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
}

/* ── Drawer Transition ───────────────────────── */
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.2s ease;
}

.drawer-enter-active .drawer,
.drawer-leave-active .drawer {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-enter-from { opacity: 0; }
.drawer-leave-to { opacity: 0; }
.drawer-enter-from .drawer { transform: translateX(100%); }
.drawer-leave-to .drawer { transform: translateX(100%); }
</style>