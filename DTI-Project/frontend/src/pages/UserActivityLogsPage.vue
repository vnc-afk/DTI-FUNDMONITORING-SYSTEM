<template>
  <DataTablePage root-class="activity-namespace">
    <template #table>
      <div class="container-fluid py-4">
      <div class="page-header">
        <div class="page-header-content">
          <h1><ui-icon name="user-circle" size="24" class="activity-heading-icon" />{{ viewedUser.display_name }}'s Activity</h1>
          <p>User activity log | <strong>{{ formatNumber(totalLogs) }}</strong> activities</p>
        </div>
        <div class="page-header-actions">
          <RouterLink v-if="isCurrentUserSuperuser" to="/activity-logs" class="btn btn-primary activity-header-btn">
            <ui-icon name="arrow-left" size="18" /> Back to All Logs
          </RouterLink>
          <RouterLink v-else to="/dashboard" class="btn btn-primary activity-header-btn">
            <ui-icon name="arrow-left" size="18" /> Back to Dashboard
          </RouterLink>
        </div>
      </div>

      <div class="filter-card">
        <div class="filter-header">
          <h6><ui-icon name="filter" size="18" /> Filters</h6>
        </div>
        <div class="filter-body">
          <form id="filter-form" class="filter-form" @submit.prevent="applyFilters">
            <div class="row">
              <div class="col-lg-6">
                <div class="filter-form-group">
                  <label for="search">Search</label>
                  <input
                    id="search"
                    v-model="filters.search"
                    type="text"
                    class="form-control"
                    name="search"
                    placeholder="Search by object or description..."
                  >
                </div>
              </div>

              <div class="col-lg-6">
                <div class="filter-form-group">
                  <label for="action">Action</label>
                  <select id="action" v-model="filters.action" class="form-control" name="action" @change="applyFilters">
                    <option value="">All Actions</option>
                    <option v-for="action in actionOptions" :key="action.code" :value="action.code">{{ action.name }}</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="row">
              <div class="col-lg-6">
                <div class="filter-form-group">
                  <label for="date">Date Range</label>
                  <select id="date" v-model="filters.date" class="form-control" name="date" @change="applyFilters">
                    <option value="">All Time</option>
                    <option value="today">Today</option>
                    <option value="week">Last 7 Days</option>
                    <option value="month">Last 30 Days</option>
                  </select>
                </div>
              </div>

              <div class="col-lg-6">
                <div class="filter-form-group">
                  <div class="filter-form-spacer" aria-hidden="true" style="min-height: 1.5rem;"></div>
                  <div class="filter-actions">
                    <button type="submit" class="btn btn-primary">
                      <ui-icon name="search" size="16" /> Filter
                    </button>
                    <button type="button" class="btn btn-secondary" @click="resetFilters">
                      <ui-icon name="rotate-cw" size="16" /> Reset
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>

      <div v-if="logs.length" class="results-summary">
        <ui-icon name="info" size="18" />
        <div>Showing <strong>{{ logs.length }}</strong> of <strong>{{ formatNumber(totalLogs) }}</strong> activities</div>
      </div>

      <div class="activity-table-wrapper">
        <table class="activity-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Action</th>
              <th>Model</th>
              <th>Object</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!logs.length">
              <td colspan="5">
                <div class="empty-state">
                  <div class="empty-state-icon"><ui-icon name="inbox" size="32" class="activity-empty-icon" /></div>
                  <div class="empty-state-text">No activity logs found</div>
                </div>
              </td>
            </tr>

            <tr v-for="log in logs" :key="log.id">
              <td>
                <span :title="log.formatted_timestamp" class="activity-time-primary">{{ formatRelativeTime(log.timestamp) }}</span>
                <br>
                <small class="activity-time-secondary">{{ formatDateTime(log.timestamp) }}</small>
              </td>
              <td>
                <span class="activity-badge" :class="actionBadgeClass(log.action)">{{ log.action_display }}</span>
              </td>
              <td>
                <RouterLink v-if="isCurrentUserSuperuser" :to="`/activity-logs/model/${encodeURIComponent(log.model_name)}`" class="activity-model-link">
                  {{ log.model_name }}
                </RouterLink>
                <span v-else class="activity-model-text">{{ log.model_name }}</span>
              </td>
              <td>
                <code v-if="log.object_repr" class="activity-inline-code">{{ truncateWords(log.object_repr, 5) }}</code>
                <em v-else class="activity-na-text">N/A</em>
              </td>
              <td>
                <button class="btn btn-sm btn-secondary" @click="activeLog = log">
                  <ui-icon name="eye" size="16" /> View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="totalPages > 1" class="pagination-wrapper">
        <nav aria-label="Page navigation">
          <ul class="pagination">
            <li v-if="currentPage > 1" class="pagination-item">
              <button class="pagination-link" @click="goToPage(1)"><ui-icon name="chevrons-left" size="16" /></button>
            </li>
            <li v-if="currentPage > 1" class="pagination-item">
              <button class="pagination-link" @click="goToPage(currentPage - 1)"><ui-icon name="chevron-left" size="16" /></button>
            </li>

            <li v-for="num in visiblePages" :key="num" class="pagination-item" :class="{ active: currentPage === num }">
              <button class="pagination-link" @click="goToPage(num)">{{ num }}</button>
            </li>

            <li v-if="currentPage < totalPages" class="pagination-item">
              <button class="pagination-link" @click="goToPage(currentPage + 1)"><ui-icon name="chevron-right" size="16" /></button>
            </li>
            <li v-if="currentPage < totalPages" class="pagination-item">
              <button class="pagination-link" @click="goToPage(totalPages)"><ui-icon name="chevrons-right" size="16" /></button>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <div v-if="activeLog" class="modal-backdrop fade show"></div>
    <div v-if="activeLog" class="modal fade show" style="display: block;" tabindex="-1" @click.self="activeLog = null">
      <div class="modal-dialog modal-lg">
        <div class="modal-content activity-modal-content">
          <div class="modal-header activity-modal-header">
            <h5 class="modal-title activity-modal-title">Activity Details</h5>
            <button type="button" class="btn-close" @click="activeLog = null"></button>
          </div>
          <div class="modal-body activity-modal-body">
            <div class="row mb-3 activity-modal-info-grid">
              <div class="col-md-6">
                <p><strong>Action:</strong> {{ activeLog.action_display }}</p>
                <p><strong>Model:</strong> {{ activeLog.model_name }}</p>
              </div>
              <div class="col-md-6">
                <p><strong>Timestamp:</strong> {{ activeLog.formatted_timestamp }}</p>
                <p><strong>IP Address:</strong> <code>{{ activeLog.ip_address || 'Unknown' }}</code></p>
              </div>
            </div>

            <template v-if="activeLog.description">
              <hr>
              <h6><strong>Description</strong></h6>
              <p class="activity-prewrap-text">{{ activeLog.description }}</p>
            </template>

            <template v-if="activeLog.changed_fields && Object.keys(activeLog.changed_fields).length">
              <hr>
              <h6><strong>Changed Fields</strong></h6>
              <div class="table-responsive">
                <table class="activity-table activity-modal-table">
                  <thead>
                    <tr>
                      <th>Field</th>
                      <th>Old Value</th>
                      <th>New Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="entry in changedFieldEntries(activeLog.changed_fields)" :key="entry.field">
                      <td><strong>{{ entry.field }}</strong></td>
                      <td><code>{{ entry.oldValue }}</code></td>
                      <td><code>{{ entry.newValue }}</code></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </template>
          </div>
        </div>
      </div>
      </div>
    </template>
  </DataTablePage>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import UiIcon from '@/components/ui/UiIcon.vue'

import DataTablePage from '@/components/patterns/DataTablePage.vue'
import { fetchActivityLogFilters, fetchUserActivityLogs } from '@/services/activityLogsService'

const route = useRoute()

const logs = ref([])
const actionOptions = ref([])
const activeLog = ref(null)
const viewedUser = ref({ id: 0, username: '', display_name: 'User' })
const totalLogs = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const isCurrentUserSuperuser = ref(false)

const filters = ref({
  search: '',
  action: '',
  date: '',
})

const targetUserId = computed(() => Number(route.params.userId || 0))

const totalPages = computed(() => {
  const size = Math.max(pageSize.value, 1)
  return Math.max(Math.ceil(totalLogs.value / size), 1)
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i += 1) pages.push(i)
  return pages
})

function loadCurrentUserRole() {
  try {
    const currentUser = JSON.parse(localStorage.getItem('current_user') || '{}')
    isCurrentUserSuperuser.value = Boolean(currentUser?.is_superuser)
  } catch {
    isCurrentUserSuperuser.value = false
  }
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString()
}

function truncateWords(text, count) {
  const source = String(text || '').trim()
  if (!source) return ''
  const words = source.split(/\s+/)
  if (words.length <= count) return source
  return `${words.slice(0, count).join(' ')}...`
}

function formatDateTime(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hour}:${minute}`
}

function formatRelativeTime(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const diffSeconds = Math.round((date.getTime() - Date.now()) / 1000)
  const absSeconds = Math.abs(diffSeconds)
  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })

  if (absSeconds < 60) return rtf.format(diffSeconds, 'second')
  const diffMinutes = Math.round(diffSeconds / 60)
  if (Math.abs(diffMinutes) < 60) return rtf.format(diffMinutes, 'minute')
  const diffHours = Math.round(diffMinutes / 60)
  if (Math.abs(diffHours) < 24) return rtf.format(diffHours, 'hour')
  return rtf.format(Math.round(diffHours / 24), 'day')
}

function actionBadgeClass(action) {
  if (action === 'CREATE') return 'badge-create'
  if (action === 'UPDATE') return 'badge-update'
  if (action === 'DELETE') return 'badge-delete'
  if (action === 'VIEW') return 'badge-view'
  if (action === 'DOWNLOAD') return 'badge-download'
  if (action === 'IMPORT') return 'badge-import'
  if (action === 'LOGIN') return 'badge-update'
  if (action === 'LOGOUT') return 'badge-update'
  return 'badge-update'
}

function changedFieldEntries(changedFields) {
  if (!changedFields || typeof changedFields !== 'object') return []
  return Object.entries(changedFields).map(([field, changes]) => ({
    field,
    oldValue: changes?.old || '(empty)',
    newValue: changes?.new || '(empty)',
  }))
}

function getParams() {
  const params = { page: currentPage.value }
  if (filters.value.search) params.search = filters.value.search
  if (filters.value.action) params.action = filters.value.action
  if (filters.value.date) params.date = filters.value.date
  return params
}

async function loadFilterOptions() {
  const payload = await fetchActivityLogFilters()
  actionOptions.value = Array.isArray(payload?.actions) ? payload.actions : []
}

async function loadLogs() {
  const payload = await fetchUserActivityLogs(targetUserId.value, getParams())
  const rows = Array.isArray(payload?.results) ? payload.results : []
  logs.value = rows
  totalLogs.value = Number(payload?.total_logs ?? payload?.count ?? rows.length ?? 0)
  viewedUser.value = payload?.viewed_user || viewedUser.value
  if (rows.length > 0) pageSize.value = rows.length
}

async function applyFilters() {
  currentPage.value = 1
  await loadLogs()
}

async function goToPage(page) {
  const next = Math.min(Math.max(Number(page || 1), 1), totalPages.value)
  currentPage.value = next
  await loadLogs()
}

async function resetFilters() {
  filters.value = { search: '', action: '', date: '' }
  currentPage.value = 1
  await loadLogs()
}

onMounted(async () => {
  loadCurrentUserRole()
  await Promise.all([loadFilterOptions(), loadLogs()])
})
</script>
