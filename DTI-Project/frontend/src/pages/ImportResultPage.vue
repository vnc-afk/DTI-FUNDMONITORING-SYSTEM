<template>
  <ReportPageLayout
    title="Import Results"
    description="Summary of your import activity"
    eyebrow="Dashboard"
  >
    <!-- Status Alert -->
    <div v-if="statusType" :class="['status-alert', `status-alert-${statusType}`]" role="alert">
      <ui-icon :name="getStatusIcon(statusType)" />
      <div class="alert-content">
        <strong v-if="statusType === 'success'">
          Import Successful!
        </strong>
        <strong v-else-if="statusType === 'warning'">
          Import Completed with {{ formatCount(result.errors) }} Error{{ pluralize(result.errors) }}
        </strong>
        <strong v-else>
          Import Complete
        </strong>
        <p>
          {{ statusMessage }}
        </p>
      </div>
      <button
        type="button"
        class="alert-close"
        @click="dismissStatus"
        aria-label="Close alert"
      >
        <ui-icon name="x" />
      </button>
    </div>

    <!-- Summary Cards -->
    <UiSummaryCards v-if="summaryCards.length" :cards="summaryCards" />

    <!-- Error Details Table -->
    <div v-if="errorDetails.length" class="error-section">
      <div class="section-header">
        <div class="section-title">
          <ui-icon name="circle-alert" />
          Import Errors
        </div>
        <span class="error-count">{{ formatCount(result.errors) }} error{{ pluralize(result.errors) }}</span>
      </div>

      <div class="table-container">
        <table class="error-table">
          <thead>
            <tr>
              <th class="col-row">Row</th>
              <th>Error Message</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(error, index) in errorDetails" :key="`error-${index}`">
              <td class="col-row">
                <span class="row-badge">Row {{ error.row }}</span>
              </td>
              <td>
                <span class="error-message">{{ error.error }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <RouterLink to="/import" class="btn btn-primary">
        <ui-icon name="upload" />
        Import More Data
      </RouterLink>

      <RouterLink v-if="viewTarget" :to="viewTarget.to" class="btn btn-secondary">
        <ui-icon :name="convertBootstrapToLucideIcon(viewTarget.icon)" />
        {{ viewTarget.label }}
      </RouterLink>

      <RouterLink to="/dashboard" class="btn btn-secondary">
        <ui-icon name="home" />
        Back to Dashboard
      </RouterLink>
    </div>

    <!-- Page Error -->
    <div v-if="pageError" class="page-error" role="alert">
      <ui-icon name="info" />
      <span>{{ pageError }}</span>
    </div>
  </ReportPageLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import UiSummaryCards from '@/components/ui/UiSummaryCards.vue'
import ReportPageLayout from '@/components/patterns/ReportPageLayout.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import { fetchImportResult } from '@/services/importService'
import { useSharedStore } from '@/stores/sharedStore'

const sharedStore = useSharedStore()

const result = ref({
  success: false,
  created: 0,
  errors: 0,
  error_details: [],
})
const summaryCards = ref([])
const viewTarget = ref(null)
const pageError = ref('')
const hideStatus = ref(false)

const errorDetails = computed(() => Array.isArray(result.value?.error_details) ? result.value.error_details : [])

const statusType = computed(() => {
  if (hideStatus.value) return ''
  if (result.value?.success) return 'success'
  if (Number(result.value?.errors || 0) > 0) return 'warning'
  return 'info'
})

const statusMessage = computed(() => {
  if (statusType.value === 'success') {
    return `All ${formatCount(result.value.created)} record${pluralize(result.value.created)} have been imported without errors.`
  }
  if (statusType.value === 'warning') {
    return `${formatCount(result.value.created)} record${pluralize(result.value.created)} imported successfully.`
  }
  return 'Review the details below.'
})

function getStatusIcon(type) {
  switch (type) {
    case 'success':
      return 'check-circle-2'
    case 'warning':
      return 'alert-triangle'
    case 'info':
    default:
      return 'info'
  }
}

function convertBootstrapToLucideIcon(bsIcon) {
  // Convert bootstrap icon class to lucide icon name
  if (!bsIcon) return 'help-circle'
  // Remove 'bi-' prefix if present
  const name = bsIcon.replace(/^bi-/, '').replace(/-fill$/, '')
  const iconMapping = {
    'list': 'list',
    'users': 'users',
    'user': 'user',
    'check': 'check',
    'x': 'x',
    'download': 'download',
    'upload': 'upload',
  }
  return iconMapping[name] || name
}

function formatCount(value) {
  return Number(value || 0).toLocaleString('en-PH')
}

function pluralize(value) {
  return Number(value || 0) === 1 ? '' : 's'
}

function dismissStatus() {
  hideStatus.value = true
}

async function loadImportResult() {
  try {
    // First check if we have cached result from the import submission
    const cachedResult = sharedStore.getShared('import_result')
    if (cachedResult) {
      // Use cached result
      result.value = cachedResult
      buildSummaryCards(cachedResult)
      pageError.value = ''
      // Clear it from store after using so it doesn't persist
      sharedStore.removeShared('import_result')
      return
    }

    // If no cached result, try to fetch from API (for page reloads or direct navigation)
    const payload = await fetchImportResult()
    result.value = payload?.result || result.value
    summaryCards.value = Array.isArray(payload?.summary_cards) ? payload.summary_cards : []
    viewTarget.value = payload?.view_target || null
    pageError.value = ''
  } catch (error) {
    const detail = error?.response?.data?.detail
    pageError.value = detail || 'No import results found. Start a new import to see results here.'
    result.value = { success: false, created: 0, errors: 0, error_details: [] }
    summaryCards.value = []
    viewTarget.value = null
  }
}

function buildSummaryCards(resultPayload) {
  const cards = [
    {
      label: 'Total Rows',
      value: resultPayload?.get?.('total_rows') || resultPayload?.total_rows || 0,
      description: 'Rows in file',
      is_currency: false,
    },
    {
      label: 'Created',
      value: resultPayload?.get?.('created') || resultPayload?.created || 0,
      description: 'New records added',
      is_currency: false,
    },
    {
      label: 'Errors',
      value: resultPayload?.get?.('errors') || resultPayload?.errors || 0,
      description: 'Failed to import',
      is_currency: false,
    },
  ]

  if (resultPayload?.get?.('updated') || resultPayload?.updated) {
    cards.splice(2, 0, {
      label: 'Updated',
      value: resultPayload?.get?.('updated') || resultPayload?.updated || 0,
      description: 'Updated existing',
      is_currency: false,
    })
  }

  summaryCards.value = cards

  // Set view target based on data_type
  const dataType = resultPayload?.get?.('data_type') || resultPayload?.data_type || ''
  const targetMap = {
    'Suppliers': { label: 'View Suppliers', to: '/suppliers', icon: 'bi-truck' },
    'Bank Statements': { label: 'View Bank Statements', to: '/bank-statements', icon: 'bi-building' },
    'Master Fund Monitoring': { label: 'View Master Fund Monitoring', to: '/master-fund-monitoring', icon: 'bi-graph-up' },
    'Staff': { label: 'View Staff', to: '/staff', icon: 'bi-people' },
  }
  viewTarget.value = targetMap[dataType] || null
}

onMounted(() => {
  loadImportResult()
})
</script>

<style scoped>
/* Status Alert */
.status-alert {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  border: 1px solid;
  margin-bottom: var(--space-6);
  animation: slideInDown var(--duration-fast) var(--ease-out);
}

.status-alert i {
  flex-shrink: 0;
  font-size: 1.25rem;
  margin-top: 0.125rem;
}

.alert-content {
  flex: 1;
}

.alert-content strong {
  display: block;
  font-weight: var(--weight-semibold);
  margin-bottom: var(--space-1);
}

.alert-content p {
  font-size: var(--text-sm);
  margin: 0;
}

.alert-close {
  flex-shrink: 0;
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.6;
  transition: opacity var(--transition);
}

.alert-close:hover {
  opacity: 1;
}

.status-alert-success {
  background: rgba(34, 197, 94, 0.08);
  border-color: rgba(34, 197, 94, 0.2);
  color: var(--status-success-text);
}

.status-alert-warning {
  background: rgba(245, 158, 11, 0.08);
  border-color: rgba(245, 158, 11, 0.2);
  color: var(--text-primary);
}

.status-alert-info {
  background: rgba(56, 189, 248, 0.08);
  border-color: rgba(56, 189, 248, 0.2);
  color: var(--text-primary);
}

/* Error Section */
.error-section {
  margin-bottom: var(--space-6);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
  padding: var(--space-4);
  background: var(--surface-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  border-bottom: none;
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
}

.section-title i {
  font-size: 1.25rem;
  color: var(--status-danger-text);
}

.error-count {
  display: inline-block;
  padding: var(--space-2) var(--space-3);
  background: var(--surface-subtle);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--text-secondary);
}

/* Table */
.table-container {
  overflow-x: auto;
}

.error-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--surface-base);
  border: 1px solid var(--border-subtle);
  border-top: none;
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
}

.error-table thead {
  background: var(--surface-subtle);
  border-bottom: 1px solid var(--border-subtle);
}

.error-table th {
  padding: var(--space-4);
  text-align: left;
  font-weight: var(--weight-semibold);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.error-table td {
  padding: var(--space-4);
  border-top: 1px solid var(--border-subtle);
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.error-table tbody tr:hover {
  background: rgba(59, 130, 246, 0.02);
}

.col-row {
  width: 120px;
}

.row-badge {
  display: inline-block;
  padding: var(--space-2) var(--space-3);
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-md);
  color: var(--status-danger-text);
  font-weight: var(--weight-semibold);
  font-size: var(--text-xs);
}

.error-message {
  color: var(--text-primary);
  line-height: 1.5;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: var(--space-4);
  flex-wrap: wrap;
  padding: var(--space-6);
  background: var(--surface-subtle);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition);
  border: 1px solid transparent;
  white-space: nowrap;
}

.btn i {
  font-size: 1rem;
}

.btn-primary {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.btn-primary:hover {
  background: #60a5fa;
  border-color: #60a5fa;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  transform: translateY(-2px);
}

.btn-secondary {
  background: var(--surface-base);
  color: var(--text-primary);
  border-color: var(--border-strong);
}

.btn-secondary:hover {
  background: var(--surface-base);
  border-color: var(--accent);
  color: var(--accent);
}

/* Page Error */
.page-error {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  font-size: var(--text-sm);
  margin-top: var(--space-6);
}

.page-error i {
  flex-shrink: 0;
  font-size: 1.1rem;
}

/* Animations */
@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-0.5rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .status-alert {
    flex-direction: column;
    gap: var(--space-3);
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-3);
  }

  .error-table {
    font-size: var(--text-xs);
  }

  .error-table th,
  .error-table td {
    padding: var(--space-3);
  }

  .action-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>
