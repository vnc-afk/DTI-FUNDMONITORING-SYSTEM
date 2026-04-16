<template>
  <ReportPageLayout title="Archive Management" description="Organize and manage your financial records by year">
    <!-- Alerts -->
    <UiToast
      v-for="(alert, index) in alerts"
      :key="`${alert.message}-${index}`"
      :title="alert.title"
      :message="alert.message"
      :variant="alert.type"
      @close="dismissAlert(index)"
    />

    <!-- Stats Overview -->
    <section class="mt-6">
      <h2 class="section-title">Overview</h2>
      <div class="summary-grid">
        <div class="stat-card stat-card--success">
          <div class="stat-card-label">Active</div>
          <div class="stat-card-value">{{ formatNumber(stats.active_fund_monitoring) }}</div>
          <div class="stat-card-sub">Transactions</div>
        </div>
        <div class="stat-card stat-card--warning">
          <div class="stat-card-label">Archived</div>
          <div class="stat-card-value">{{ formatNumber(stats.archived_fund_monitoring) }}</div>
          <div class="stat-card-sub">Transactions</div>
        </div>
        <div class="stat-card stat-card--success">
          <div class="stat-card-label">Active</div>
          <div class="stat-card-value">{{ formatNumber(stats.active_bank_statements) }}</div>
          <div class="stat-card-sub">Statements</div>
        </div>
        <div class="stat-card stat-card--warning">
          <div class="stat-card-label">Archived</div>
          <div class="stat-card-value">{{ formatNumber(stats.archived_bank_statements) }}</div>
          <div class="stat-card-sub">Statements</div>
        </div>
      </div>
    </section>

    <!-- Archive Actions -->
    <section class="mt-6">
      <h2 class="section-title">Archive actions</h2>
      <div class="form-grid">
        <!-- Archive Form -->
        <BaseFormSection title="Archive a year">
          <form @submit.prevent="onArchiveYear" class="flex flex-col gap-4">
            <UiSelect
              v-model="archiveForm.year"
              label="Select year"
              :options="archiveYearOptions"
              :placeholder="archiveYearPlaceholder"
              required
              :disabled="!archiveYearOptions.length"
              :error="archiveValidated && !archiveForm.year ? 'Year is required' : ''"
            />
            <UiInput
              v-model="archiveForm.reason"
              type="text"
              label="Reason (optional)"
              placeholder="Add notes about this archive..."
            />
            <UiButton
              variant="primary"
              type="submit"
              :disabled="submitting.archive"
              :loading="submitting.archive"
              block
            >
              <ui-icon name="archive" size="20" />
              {{ submitting.archive ? 'Archiving...' : 'Archive Year' }}
            </UiButton>
          </form>
        </BaseFormSection>

        <!-- Restore Form -->
        <BaseFormSection title="Restore a year">
          <form @submit.prevent="onUnarchiveYear" class="flex flex-col gap-4">
            <UiSelect
              v-model="unarchiveForm.year"
              label="Select year to restore"
              :options="restoreYearOptions"
              :placeholder="restoreYearPlaceholder"
              required
              :disabled="!restoreYearOptions.length"
              :error="unarchiveValidated && !unarchiveForm.year ? 'Year is required' : ''"
            />
            <UiButton
              variant="primary"
              type="submit"
              :disabled="submitting.unarchive"
              :loading="submitting.unarchive"
              block
            >
              <ui-icon name="rotate-ccw" size="20" />
              {{ submitting.unarchive ? 'Restoring...' : 'Restore Year' }}
            </UiButton>
          </form>
        </BaseFormSection>
      </div>
    </section>

    <!-- Browse Archives -->
    <section class="mt-6">
      <h2 class="section-title">Browse archives</h2>
      <div class="dashboard-grid">
        <RouterLink to="/archive/transactions" class="quick-link-card">
          <div class="quick-link-icon">
            <ui-icon name="receipt" size="20" />
          </div>
          <div class="quick-link-content">
            <h3 class="quick-link-title">Archived Transactions</h3>
            <p class="quick-link-description">View and manage archived transaction records</p>
          </div>
          <ui-icon name="arrow-right" size="18" />
        </RouterLink>
        <RouterLink to="/archive/statements" class="quick-link-card">
          <div class="quick-link-icon">
            <ui-icon name="file-text" size="20" />
          </div>
          <div class="quick-link-content">
            <h3 class="quick-link-title">Archived Statements</h3>
            <p class="quick-link-description">Browse archived bank statements</p>
          </div>
          <ui-icon name="arrow-right" size="18" />
        </RouterLink>
      </div>
    </section>

    <!-- How It Works -->
    <section class="mt-6 mb-8">
      <h2 class="section-title">How archiving works</h2>
      <div class="archive-info-banner">
        <ui-icon name="info" size="20" class="archive-info-banner-icon" />
        <p>Think of archiving like moving old paperwork to a filing cabinet — it's still there when you need it, but it won't clutter your active dashboard.</p>
      </div>
      <div class="summary-grid">
        <div class="archive-step-card">
          <div class="archive-step-number">1</div>
          <h3 class="archive-step-title">Dashboard stays clean</h3>
          <p class="archive-step-description">Only current records appear in your main view</p>
        </div>
        <div class="archive-step-card">
          <div class="archive-step-number">2</div>
          <h3 class="archive-step-title">Nothing is deleted</h3>
          <p class="archive-step-description">All records are safely stored in the system</p>
        </div>
        <div class="archive-step-card">
          <div class="archive-step-number">3</div>
          <h3 class="archive-step-title">Always searchable</h3>
          <p class="archive-step-description">Browse archives using search and filters</p>
        </div>
        <div class="archive-step-card">
          <div class="archive-step-number">4</div>
          <h3 class="archive-step-title">Easy to restore</h3>
          <p class="archive-step-description">One click to bring any year back to active</p>
        </div>
      </div>
    </section>
  </ReportPageLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import UiIcon from '@/components/ui/UiIcon.vue'
import '@/assets/css/patterns/archive.css'

import ReportPageLayout from '@/components/patterns/ReportPageLayout.vue'
import BaseFormSection from '@/components/patterns/BaseFormSection.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiToast from '@/components/ui/UiToast.vue'
import { notifyArchiveUpdated } from '@/utils/archiveRefresh'
import { archiveYear, fetchArchiveDashboard, unarchiveYear } from '@/services/archiveService'

const stats = ref({
  active_fund_monitoring: 0,
  archived_fund_monitoring: 0,
  active_bank_statements: 0,
  archived_bank_statements: 0,
})

const yearStatuses = ref([])
const alerts = ref([])
const archiveForm = ref({ year: '', reason: '' })
const unarchiveForm = ref({ year: '' })
const archiveValidated = ref(false)
const unarchiveValidated = ref(false)
const submitting = ref({ archive: false, unarchive: false })

function formatNumber(value) {
  return Number(value || 0).toLocaleString()
}

function buildYearLabel(entry) {
  return `${entry.year} • ${formatNumber(entry.active_total)} active, ${formatNumber(entry.archived_total)} archived`
}

function hasYearOption(options, selectedYear) {
  return options.some((option) => option.value === String(selectedYear || ''))
}

const archiveYearOptions = computed(() =>
  yearStatuses.value
    .filter((entry) => entry.can_archive)
    .map((entry) => ({
      label: buildYearLabel(entry),
      value: String(entry.year),
    }))
)

const restoreYearOptions = computed(() =>
  yearStatuses.value
    .filter((entry) => entry.can_restore)
    .map((entry) => ({
      label: buildYearLabel(entry),
      value: String(entry.year),
    }))
)

const archiveYearPlaceholder = computed(() => (
  archiveYearOptions.value.length ? 'Choose a year' : 'No active years available'
))

const restoreYearPlaceholder = computed(() => (
  restoreYearOptions.value.length ? 'Choose a year' : 'No archived years available'
))

const isArchiveSelectionValid = computed(() => hasYearOption(archiveYearOptions.value, archiveForm.value.year))
const isRestoreSelectionValid = computed(() => hasYearOption(restoreYearOptions.value, unarchiveForm.value.year))

function dismissAlert(index) {
  alerts.value.splice(index, 1)
}

function addAlert(type, message, title = '') {
  alerts.value.push({ type, message, title: title || (type === 'success' ? 'Success!' : 'Notice') })
}

function normalizeDashboardPayload(payload) {
  stats.value = {
    active_fund_monitoring: Number(payload?.stats?.active_fund_monitoring || 0),
    archived_fund_monitoring: Number(payload?.stats?.archived_fund_monitoring || 0),
    active_bank_statements: Number(payload?.stats?.active_bank_statements || 0),
    archived_bank_statements: Number(payload?.stats?.archived_bank_statements || 0),
  }

  const statuses = Array.isArray(payload?.year_statuses) && payload.year_statuses.length
    ? payload.year_statuses
    : (Array.isArray(payload?.years_available) ? payload.years_available : []).map((year) => ({
        year,
        active_total: 0,
        archived_total: 0,
        can_archive: true,
        can_restore: true,
      }))

  yearStatuses.value = statuses
    .map((entry) => ({
      year: Number(entry?.year),
      active_total: Number(entry?.active_total || 0),
      archived_total: Number(entry?.archived_total || 0),
      can_archive: Boolean(entry?.can_archive),
      can_restore: Boolean(entry?.can_restore),
    }))
    .filter((entry) => Number.isFinite(entry.year) && entry.year >= 1900 && entry.year <= 2099)
    .sort((a, b) => b.year - a.year)
}

function syncFormSelections() {
  if (!hasYearOption(archiveYearOptions.value, archiveForm.value.year)) {
    archiveForm.value.year = ''
    archiveValidated.value = false
  }

  if (!hasYearOption(restoreYearOptions.value, unarchiveForm.value.year)) {
    unarchiveForm.value.year = ''
    unarchiveValidated.value = false
  }
}

async function loadDashboard() {
  try {
    const payload = await fetchArchiveDashboard()
    normalizeDashboardPayload(payload)
    syncFormSelections()
    return payload
  } catch (error) {
    console.error('Failed to load archive dashboard:', error)
    addAlert(
      'danger',
      error?.response?.data?.detail || error?.message || 'Failed to load archive dashboard.',
      'Error',
    )
    return null
  }
}

async function onArchiveYear() {
  archiveValidated.value = true
  if (!archiveForm.value.year) {
    addAlert('warning', 'Please select a year to archive.')
    return
  }

  if (!isArchiveSelectionValid.value) {
    addAlert('warning', 'No active records are available for the selected year.')
    return
  }

  const year = archiveForm.value.year

  submitting.value.archive = true
  try {
    const payload = await archiveYear({ year, reason: archiveForm.value.reason || '' })
    if (payload?.success) {
      addAlert('success', `Year ${year} has been archived successfully.`)
      archiveForm.value = { year: '', reason: '' }
      archiveValidated.value = false
      await loadDashboard()
      notifyArchiveUpdated({ action: 'archive', year, result: payload?.result || null })
    } else {
      console.error('Archive year API returned an error payload:', payload)
      addAlert('danger', payload?.error || 'Failed to archive year', 'Archive Error')
    }
  } catch (error) {
    console.error('Archive year request failed:', error)
    addAlert('danger', error?.response?.data?.detail || error?.response?.data?.error || error?.message || 'Unknown error', 'Error')
  } finally {
    submitting.value.archive = false
  }
}

async function onUnarchiveYear() {
  unarchiveValidated.value = true
  if (!unarchiveForm.value.year) {
    addAlert('warning', 'Please select a year to restore.')
    return
  }

  if (!isRestoreSelectionValid.value) {
    addAlert('warning', 'No archived records are available for the selected year.')
    return
  }

  const year = unarchiveForm.value.year

  submitting.value.unarchive = true
  try {
    const payload = await unarchiveYear({ year })
    if (payload?.success) {
      addAlert('success', `Year ${year} has been restored successfully.`)
      unarchiveForm.value = { year: '' }
      unarchiveValidated.value = false
      await loadDashboard()
      notifyArchiveUpdated({ action: 'unarchive', year, result: payload?.result || null })
    } else {
      console.error('Restore year API returned an error payload:', payload)
      addAlert('danger', payload?.error || 'Failed to restore year', 'Restore Error')
    }
  } catch (error) {
    console.error('Restore year request failed:', error)
    addAlert('danger', error?.response?.data?.detail || error?.response?.data?.error || error?.message || 'Unknown error', 'Error')
  } finally {
    submitting.value.unarchive = false
  }
}

onMounted(() => {
  void loadDashboard()
})

</script>