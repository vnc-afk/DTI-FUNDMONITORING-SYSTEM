<template>
  <FormPage
    :title="config.title"
    :description="config.subtitle"
    eyebrow="Dashboard"
    submit-label="Import Data"
    cancel-label="Cancel"
    @submit="handleSubmit"
    @cancel="handleCancel"
  >
    <!-- Alerts -->
    <div v-if="alerts.length" class="alerts-container">
      <div
        v-for="(alert, index) in alerts"
        :key="`alert-${index}`"
        :class="['alert', `alert-${alert.type}`]"
        role="alert"
      >
        <ui-icon :name="getAlertIcon(alert.type)" />
        <span>{{ alert.message }}</span>
        <button type="button" class="alert-close" @click="dismissAlert(index)" aria-label="Close">
          <ui-icon name="x" />
        </button>
      </div>
    </div>

    <!-- Data Type Section -->
    <BaseFormSection>
      <template #title>
        <ui-icon name="list-checks" />
        Select Data Type
      </template>
      <div class="data-type-selector">
        <button
          v-for="choice in config.dataTypeChoices"
          :key="choice.value"
          type="button"
          :class="['data-type-btn', { active: form.data_type === choice.value }]"
          :title="getDataTypeTitle(choice.value)"
          @click="form.data_type = choice.value"
        >
          <ui-icon :name="getDataTypeIcon(choice.value)" />
          <span class="btn-label">{{ choice.label }}</span>
          <span v-if="form.data_type === choice.value" class="check-icon">
            <ui-icon name="circle-check" />
          </span>
        </button>
      </div>
      <div v-if="fieldErrors.data_type" class="form-error">
        <ui-icon name="alert-triangle" />
        {{ fieldErrors.data_type }}
      </div>
    </BaseFormSection>

    <!-- File Selection Section -->
    <BaseFormSection>
      <template #title>
        <ui-icon name="file" />
        File Selection
      </template>
      <div class="form-group">
        <div id="import-file-label" class="form-label">
          {{ config.fileLabel }} <span class="required">*</span>
        </div>
        <div
          class="file-upload-wrapper"
          :class="{ dragover: dragOver }"
          @dragenter.prevent="dragOver = true"
          @dragover.prevent="dragOver = true"
          @dragleave.prevent="dragOver = false"
          @drop.prevent="onDrop"
        >
          <input
            id="import-file"
            ref="fileInput"
            name="file"
            type="file"
            class="file-input sr-only"
            accept=".xlsx,.xls,.csv"
            required
            aria-labelledby="import-file-label"
            @change="onFileChange"
          >
          <label for="import-file" class="file-upload-label">
            <ui-icon name="upload-cloud" size="24" class="upload-icon" />
            <span class="upload-text">{{ fileLabelText }}</span>
            <small class="upload-hint">{{ config.fileHelp }}</small>
          </label>
        </div>
        <transition name="fade">
          <div v-if="selectedFile" class="file-info">
            <ui-icon name="check-circle-2" />
            <span>{{ selectedFile.name }}</span>
            <button type="button" class="file-remove" @click="selectedFile = null" title="Remove file">
              <ui-icon name="x" />
            </button>
          </div>
        </transition>
        <div v-if="fieldErrors.file" class="form-error">
          <ui-icon name="alert-triangle" />
          {{ fieldErrors.file }}
        </div>
      </div>

      <div class="form-grid">
        <UiInput
          v-model="form.sheet_name"
          :label="config.sheetNameLabel"
          :placeholder="config.sheetNamePlaceholder"
          :hint="config.sheetNameHelp"
          :error="fieldErrors.sheet_name"
        />

        <UiInput
          v-model.number="form.skip_rows"
          type="number"
          :label="config.skipRowsLabel"
          placeholder="0"
          min="0"
          :hint="config.skipRowsHelp"
          :error="fieldErrors.skip_rows"
        />
      </div>
    </BaseFormSection>

    <!-- Import Options Section -->
    <BaseFormSection>
      <template #title>
        <ui-icon name="sliders-horizontal" />
        Import Options
      </template>
      <UiCheckbox
        v-model="form.skip_errors"
        :label="config.skipErrorsLabel"
      />
      <small class="form-hint">{{ config.skipErrorsHelp }}</small>
    </BaseFormSection>

    <!-- Processing Modal -->
    <div v-if="submitting" class="modal-overlay">
      <div class="modal-content">
        <div class="spinner-container">
          <div class="spinner"></div>
          <h5 class="modal-title">Processing Import</h5>
          <p class="modal-message">Please wait while we import your data...</p>
        </div>
      </div>
    </div>

    <!-- Import Guide Section -->
    <UiCard :title="guideTitle">

      <div class="guide-accordion">
        <div v-for="item in guideItems" :key="item.id" class="accordion-item">
          <button
            class="accordion-button"
            :class="{ collapsed: !isOpen(item.id) }"
            type="button"
            @click="toggleGuide(item.id)"
          >
            <ui-icon :name="item.icon" />
            <span>{{ item.title }}</span>
            <ui-icon name="chevron-down" class="chevron" />
          </button>
          <transition name="expand">
            <div v-if="isOpen(item.id)" class="accordion-body">
              <div v-html="item.html"></div>
            </div>
          </transition>
        </div>
      </div>
    </UiCard>
  </FormPage>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import FormPage from '@/components/patterns/FormPage.vue'
import BaseFormSection from '@/components/patterns/BaseFormSection.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiCheckbox from '@/components/ui/UiCheckbox.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import { fetchImportFormConfig, submitImportData } from '@/services/importService'
import { useSharedStore } from '@/stores/sharedStore'

const router = useRouter()
const sharedStore = useSharedStore()

const form = ref({
  data_type: 'master_fund_monitoring',
  sheet_name: '',
  skip_rows: 0,
  skip_errors: false,
})

const selectedFile = ref(null)
const submitting = ref(false)
const dragOver = ref(false)
const alerts = ref([])
const fieldErrors = ref({})

const config = ref({
  title: 'Import Data',
  subtitle: 'Bulk import suppliers, bank statements, staff, or fund monitoring data from Excel/CSV files',
  dataTypeLabel: 'What data are you importing?',
  dataTypeChoices: [
    { value: 'master_fund_monitoring', label: 'Master Fund Monitoring' },
    { value: 'bank_statement', label: 'Bank Statements' },
    { value: 'supplier', label: 'Suppliers' },
    { value: 'staff', label: 'Staff' },
  ],
  fileLabel: 'Select Excel or CSV file',
  fileHelp: 'Supported formats: .xlsx, .xls, .csv',
  sheetNameLabel: 'Sheet name (for Excel files)',
  sheetNameHelp: 'Leave blank to use first sheet. Or specify sheet name.',
  sheetNamePlaceholder: 'e.g., Suppliers, Bank Statements, Sheet1',
  skipRowsLabel: 'Skip rows',
  skipRowsHelp: 'Number of rows to skip before the header (e.g., if your file has a title row, set this to 1)',
  skipErrorsLabel: 'Skip errors and continue importing',
  skipErrorsHelp: 'If checked, rows with errors will be skipped. If unchecked, import will stop at first error.',
})

const openGuides = ref(new Set(['multi-sheet']))

const guideItems = [
  {
    id: 'multi-sheet',
    icon: 'columns',
    title: 'Multiple Sheets & Title Rows',
    html: `
      <div class="guide-section">
        <h4>Excel with Multiple Sheets</h4>
        <p>If your Excel file has multiple sheets, specify the exact sheet name in the <strong>"Sheet name"</strong> field:</p>
        <div class="guide-example">
          <strong>Example:</strong><br/>
          Sheet names: "Database", "Bank Statements", "Tin"<br/>
          → Enter: <code>Database</code>
        </div>
        
        <h4 style="margin-top: var(--space-6)">Title Rows & Headers</h4>
        <p>If your file has title rows before the actual headers, use the <strong>"Skip rows"</strong> field:</p>
        <div class="guide-example">
          <strong>Example:</strong><br/>
          Row 1: "DTI Fund Monitoring Report - Q1 2024"<br/>
          Row 2: "Supplier Data"<br/>
          Row 3: supplier | tin | address<br/>
          → Set "Skip rows" to <code>2</code>
        </div>
        
        <div class="alert alert-warning" style="margin-top: var(--space-4)">
          <strong>⚠ Column names must match exactly</strong> (case-insensitive). Unrecognized columns are skipped.
        </div>
      </div>
    `,
  },
  {
    id: 'mfm',
    icon: 'trending-up',
    title: 'Master Fund Monitoring Import Format',
    html: `
      <div class="guide-section">
        <h4>Core Transaction Fields (Required)</h4>
        <table class="guide-table">
          <thead>
            <tr>
              <th>Column Name</th>
              <th>Type</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr class="required-row">
              <td><code>date</code></td>
              <td>Date</td>
              <td>Transaction date (YYYY-MM-DD)</td>
            </tr>
            <tr class="required-row">
              <td><code>payee</code></td>
              <td>Text</td>
              <td>Supplier/Vendor name (must exist in Suppliers or will be auto-created)</td>
            </tr>
            <tr class="required-row">
              <td><code>particulars</code></td>
              <td>Text</td>
              <td>Description of the transaction/purchase</td>
            </tr>
          </tbody>
        </table>

        <h4 style="margin-top: var(--space-6)">Organization & Fund Fields</h4>
        <div class="guide-columns">
          <div>
            <strong>Budget Details:</strong><br/>
            <code>month</code> - Month (1-12 or Jan-Dec)<br/>
            <code>division</code> - Division/Department<br/>
            <code>fund_source</code> - Fund source code<br/>
            <code>mooe</code> - Maintenance & Other Operating Expenses<br/>
            <code>nc</code> - Non-Consumables budget
          </div>
          <div style="margin-top: var(--space-4)">
            <strong>Supplier & Payment:</strong><br/>
            <code>tin</code> - Supplier Tax ID<br/>
            <code>tax_type</code> - Tax classification<br/>
            <code>purchase_type</code> - Type of purchase<br/>
            <code>payments</code> - Payment amount<br/>
            <code>dv_number</code> - DV (Disbursement Voucher) number
          </div>
        </div>

        <h4 style="margin-top: var(--space-6)">Check & Reconciliation Fields</h4>
        <div class="guide-columns">
          <code>cheque_number</code> - Check number<br/>
          <code>cleared_date</code> - Date cleared by bank<br/>
          <code>cheque_status</code> - Status (Cleared, On Process, Cancelled)<br/>
          <code>downloads</code> - Downloads count/tracking<br/>
          <code>account_title</code> - Bank account name<br/>
          <code>expense_classification</code> - Expense category<br/>
          <code>staff</code> - Staff member responsible
        </div>

        <h4 style="margin-top: var(--space-6)">💰 Tax Breakdown Columns (Optional)</h4>
        <p>Include these if you need detailed tax tracking (amounts should be numbers):</p>
        <div class="guide-columns">
          <div>
            <strong>Standard Rates:</strong><br/>
            <code>goods (5%)</code><br/>
            <code>services (5%)</code><br/>
            <code>goods & services (3%)</code>
          </div>
          <div style="margin-top: var(--space-4)">
            <strong>Other Rates:</strong><br/>
            <code>goods (1%)</code><br/>
            <code>services (2%)</code><br/>
            <code>rental (5%)</code><br/>
            <code>prof. fee (10%)</code>
          </div>
        </div>

        <div class="guide-example">
          <strong>Minimal Example (required fields only):</strong><br/>
          2024-03-20 | ABC Suppliers Inc | Office Supplies | Payee auto-created if needed
        </div>
        <div class="guide-tip" style="margin-top: var(--space-4)">
          <strong>💡 Pro Tip:</strong> Include as many optional fields as available in your source data for better reporting and tracking.
        </div>
      </div>
    `,
  },
  {
    id: 'bank',
    icon: 'building-2',
    title: 'Bank Statement Import Format',
    html: `
      <div class="guide-section">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Column Name</th>
              <th>Type</th>
              <th>Required</th>
              <th>Description & Format</th>
            </tr>
          </thead>
          <tbody>
            <tr class="required-row">
              <td><code>date</code></td>
              <td>Date</td>
              <td>✓</td>
              <td>Transaction date (YYYY-MM-DD)</td>
            </tr>
            <tr class="required-row">
              <td><code>description</code></td>
              <td>Text</td>
              <td>✓</td>
              <td>Transaction description or details</td>
            </tr>
            <tr class="required-row">
              <td><code>balance</code></td>
              <td>Number</td>
              <td>✓</td>
              <td>Account balance after transaction</td>
            </tr>
            <tr>
              <td><code>check_number</code></td>
              <td>Text</td>
              <td></td>
              <td>Check or reference number</td>
            </tr>
            <tr>
              <td><code>debit</code></td>
              <td>Number</td>
              <td></td>
              <td>Money going out (expenditure). Use 0 or leave blank for credits.</td>
            </tr>
            <tr>
              <td><code>credit</code></td>
              <td>Number</td>
              <td></td>
              <td>Money coming in (deposit). Use 0 or leave blank for debits.</td>
            </tr>
            <tr>
              <td><code>status</code></td>
              <td>Text</td>
              <td></td>
              <td>Status: <code>Cleared</code> or <code>On Process</code></td>
            </tr>
          </tbody>
        </table>
        <div class="guide-example">
          <strong>Example Row:</strong><br/>
          2024-01-15 | Supplier Payment | 45000 | CHK-001 | 5000 | | Cleared
        </div>
        <div class="alert alert-danger" style="margin-top: var(--space-4)">
          <strong>⚠ Important:</strong> Each row must have EITHER debit OR credit, not both. Both values cannot be greater than 0.
        </div>
      </div>
    `,
  },
  {
    id: 'supplier',
    icon: 'truck',
    title: 'Supplier Import Format',
    html: `
      <div class="guide-section">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Column Name</th>
              <th>Type</th>
              <th>Required</th>
              <th>Description & Format</th>
            </tr>
          </thead>
          <tbody>
            <tr class="required-row">
              <td><code>supplier</code></td>
              <td>Text</td>
              <td>✓</td>
              <td>Supplier company or business name</td>
            </tr>
            <tr>
              <td><code>tin</code></td>
              <td>Text</td>
              <td></td>
              <td>Tax ID (Format: ###-###-###-###)</td>
            </tr>
            <tr>
              <td><code>vat_status</code></td>
              <td>Text</td>
              <td></td>
              <td>VAT Status: <code>NV</code> (Non-VAT), <code>V</code> (VAT), <code>NA</code> (Not Applicable)</td>
            </tr>
            <tr>
              <td><code>philgeps_registration</code></td>
              <td>Text</td>
              <td></td>
              <td>PhilGEPS registration code or ID</td>
            </tr>
            <tr>
              <td><code>address</code></td>
              <td>Text</td>
              <td></td>
              <td>Business address</td>
            </tr>
            <tr>
              <td><code>proprietor</code></td>
              <td>Text</td>
              <td></td>
              <td>Owner or proprietor name</td>
            </tr>
            <tr>
              <td><code>contact_number</code></td>
              <td>Text</td>
              <td></td>
              <td>Phone number (any format)</td>
            </tr>
          </tbody>
        </table>
        <div class="guide-tip">
          <strong>💡 Tip:</strong> VAT Status defaults to "NV" if not provided.
        </div>
      </div>
    `,
  },
  {
    id: 'staff',
    icon: 'users',
    title: 'Staff Import Format',
    html: `
      <div class="guide-section">
        <p><strong>Single-column format</strong> - List staff members one per row in a single column.</p>
        
        <h4>Supported Name Formats</h4>
        <table class="guide-table">
          <thead>
            <tr>
              <th>Format</th>
              <th>Example</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>First Middle Last</strong></td>
              <td>John Michael G Smith</td>
              <td>Standard Western format</td>
            </tr>
            <tr>
              <td><strong>Last, First Middle</strong></td>
              <td>Smith, John Michael G</td>
              <td>Formal/Database format</td>
            </tr>
            <tr>
              <td><strong>First Last</strong></td>
              <td>John Smith</td>
              <td>Simple format (no middle name)</td>
            </tr>
            <tr>
              <td><strong>Last, First</strong></td>
              <td>Smith, John</td>
              <td>Simple formal format</td>
            </tr>
          </tbody>
        </table>

        <h4 style="margin-top: var(--space-6)">File Guidelines</h4>
        <ul style="margin: var(--space-3) 0">
          <li><strong>Column header:</strong> Optional (e.g., "Name" is ignored if present)</li>
          <li><strong>Empty rows:</strong> Automatically skipped</li>
          <li><strong>Duplicate names:</strong> Updated with latest information</li>
          <li><strong>Case-insensitive:</strong> Names are normalized on import</li>
        </ul>

        <div class="guide-example">
          <strong>Example File:</strong><br/>
          Name<br/>
          Maria Cruz Santos<br/>
          Santos, Miguel A<br/>
          Juan Dela Cruz<br/>
          Reyes, Ana Maria<br/>
          (empty row is skipped)
        </div>

        <div class="guide-tip">
          <strong>💡 Tip:</strong> You can update existing staff by importing the same names again.
        </div>
      </div>
    `,
  },
]

const fileLabelText = computed(() => {
  if (selectedFile.value?.name) {
    return `File selected: ${selectedFile.value.name}`
  }
  return 'Choose file or drag & drop'
})

const guideTitle = computed(() => {
  const titles = {
    supplier: 'Supplier Import Guide',
    bank_statement: 'Bank Statement Import Guide',
    master_fund_monitoring: 'Master Fund Monitoring Import Guide',
    staff: 'Staff Import Guide',
  }
  return titles[form.value.data_type] || 'Import Guide'
})

const guideSubtitle = computed(() => {
  const subtitles = {
    supplier: 'Format requirements and optional fields for supplier data',
    bank_statement: 'Format requirements for bank statement transactions',
    master_fund_monitoring: 'Complete format with tax breakdown columns',
    staff: 'Format for importing staff names',
  }
  return subtitles[form.value.data_type] || 'Learn how to prepare and import your data'
})

function dismissAlert(index) {
  alerts.value.splice(index, 1)
}

function getAlertIcon(type) {
  const icons = {
    success: 'check-circle-2',
    warning: 'alert-triangle',
    danger: 'circle-alert',
    info: 'info', 
  }
  return icons[type] || 'info'
}

function getDataTypeIcon(dataType) {
  const icons = {
    supplier: 'truck',
    bank_statement: 'building-2',
    master_fund_monitoring: 'trending-up',
    staff: 'users',
  }
  return icons[dataType] || 'box'
}

function getDataTypeTitle(dataType) {
  const titles = {
    supplier: 'Import supplier information and details',
    bank_statement: 'Import bank transaction records and statements',
    master_fund_monitoring: 'Import fund monitoring data with tax breakdown',
    staff: 'Import staff names and information',
  }
  return titles[dataType] || 'Select data type to import'
}

function pushAlert(type, message) {
  alerts.value.push({ type, message })
}

function normalizeError(value) {
  if (!value) return ''
  if (Array.isArray(value)) return String(value[0] || '')
  return String(value)
}

function resetErrors() {
  fieldErrors.value = {}
}

function onFileChange(event) {
  selectedFile.value = event.target.files?.[0] || null
}

function onDrop(event) {
  dragOver.value = false
  const droppedFile = event.dataTransfer?.files?.[0]
  if (!droppedFile) return

  const dataTransfer = new DataTransfer()
  dataTransfer.items.add(droppedFile)
  event.currentTarget.querySelector('input[type="file"]').files = dataTransfer.files
  selectedFile.value = droppedFile
}

function isOpen(id) {
  return openGuides.value.has(id)
}

function toggleGuide(id) {
  const next = new Set(openGuides.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  openGuides.value = next
}

async function askConfirmation() {
  if (typeof window.showConfirmation === 'function') {
    return window.showConfirmation(
      'Upload Data',
      'Please review your file selection before importing.',
      'Upload File',
      'Cancel',
      'info'
    )
  }
  return window.confirm('Please review your file selection before importing.')
}

function applyServerConfig(payload) {
  if (!payload) return
  config.value = {
    ...config.value,
    title: payload.title || config.value.title,
    subtitle: payload.subtitle || config.value.subtitle,
    dataTypeLabel: payload.data_type?.label || config.value.dataTypeLabel,
    dataTypeChoices: Array.isArray(payload.data_type?.choices) && payload.data_type.choices.length
      ? payload.data_type.choices
      : config.value.dataTypeChoices,
    fileLabel: payload.file?.label || config.value.fileLabel,
    fileHelp: payload.file?.help_text || config.value.fileHelp,
    sheetNameLabel: payload.sheet_name?.label || config.value.sheetNameLabel,
    sheetNameHelp: payload.sheet_name?.help_text || config.value.sheetNameHelp,
    sheetNamePlaceholder: payload.sheet_name?.placeholder || config.value.sheetNamePlaceholder,
    skipRowsLabel: payload.skip_rows?.label || config.value.skipRowsLabel,
    skipRowsHelp: payload.skip_rows?.help_text || config.value.skipRowsHelp,
    skipErrorsLabel: payload.skip_errors?.label || config.value.skipErrorsLabel,
    skipErrorsHelp: payload.skip_errors?.help_text || config.value.skipErrorsHelp,
  }

  if (typeof payload.skip_rows?.initial === 'number') {
    form.value.skip_rows = payload.skip_rows.initial
  }
}

async function loadConfig() {
  try {
    const payload = await fetchImportFormConfig()
    applyServerConfig(payload)
  } catch (error) {
    pushAlert('warning', error?.response?.data?.detail || 'Failed to load import configuration. You can still fill the form manually.')
  }
}

function handleCancel() {
  router.push('/dashboard')
}

async function handleSubmit() {
  resetErrors()
  alerts.value = []

  if (!selectedFile.value) {
    fieldErrors.value.file = 'Please select a file to import.'
    return
  }

  const confirmed = await askConfirmation()
  if (!confirmed) return

  const payload = new FormData()
  payload.append('data_type', form.value.data_type)
  payload.append('file', selectedFile.value)
  payload.append('sheet_name', form.value.sheet_name || '')
  payload.append('skip_rows', String(form.value.skip_rows ?? 0))
  if (form.value.skip_errors) {
    payload.append('skip_errors', 'on')
  }

  submitting.value = true
  try {
    const response = await submitImportData(payload)
    if (response?.success) {
      // Cache the result in shared store before navigating
      if (response?.result) {
        sharedStore.setShared('import_result', response.result)
      }
      if (response.redirect_url) {
        router.push('/import/result')
        return
      }
      pushAlert('success', 'Import completed successfully.')
    } else {
      pushAlert('danger', response?.error || 'Import failed.')
    }
  } catch (error) {
    const apiData = error?.response?.data || {}
    if (apiData?.errors && typeof apiData.errors === 'object') {
      const mapped = {}
      Object.keys(apiData.errors).forEach((key) => {
        mapped[key] = normalizeError(apiData.errors[key])
      })
      fieldErrors.value = mapped
      pushAlert('danger', 'Please fix the highlighted form errors.')
    } else {
      pushAlert('danger', apiData?.error || apiData?.detail || 'Error processing import request.')
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
/* ── Alerts ──────────────────────────────────────────────────────────────── */
.alerts-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.alert {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  border-left: 4px solid;
  background: var(--surface-subtle);
  font-size: var(--text-sm);
  animation: slideInDown var(--duration-fast) var(--ease-out);
}

.alert i {
  flex-shrink: 0;
  font-size: 1.25rem;
}

.alert-success {
  background: var(--status-success-bg);
  border-left-color: var(--status-success-text);
  color: var(--status-success-text);
}

.alert-warning {
  background: var(--status-warning-bg);
  border-left-color: var(--status-warning-text);
  color: var(--status-warning-text);
}

.alert-danger {
  background: var(--status-danger-bg);
  border-left-color: var(--status-danger-text);
  color: var(--status-danger-text);
}

.alert-info {
  background: var(--status-info-bg);
  border-left-color: var(--status-info-text);
  color: var(--status-info-text);
}

.alert-close {
  margin-left: auto;
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.6;
  transition: opacity var(--duration-fast);
}

.alert-close:hover {
  opacity: 1;
}

/* ── Data Type Selector ──────────────────────────────────────────────────── */
.data-type-selector {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--space-4);
}

.data-type-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-6) var(--space-4);
  border: 2px solid var(--border-subtle);
  background: var(--surface-base);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  position: relative;
  text-align: center;
}

.data-type-btn:hover {
  border-color: var(--brand-navy-300);
  background: var(--surface-subtle);
  transform: translateY(-2px);
}

.data-type-btn.active {
  border-color: var(--color-primary);
  background: rgba(46, 80, 128, 0.05);
  box-shadow: 0 0 0 3px rgba(46, 80, 128, 0.1);
}

.data-type-btn i {
  font-size: 1.75rem;
  color: var(--color-primary);
  opacity: 0.7;
  transition: opacity var(--duration-fast);
}

.data-type-btn.active i {
  opacity: 1;
}

.data-type-btn .btn-label {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
}

.data-type-btn .check-icon {
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  color: var(--status-success-text);
  font-size: 1.25rem;
}

/* ── Form Groups ─────────────────────────────────────────────────────────── */
.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-4);
  margin-top: var(--space-4);
}

.form-label {
  font-weight: var(--weight-semibold);
  font-size: var(--text-sm);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.form-label i {
  font-size: 1rem;
  color: var(--color-primary);
}

.required {
  color: var(--status-danger-text);
}

.form-help {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin-top: var(--space-1);
  line-height: 1.4;
}

.form-hint {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin-top: var(--space-1);
}

/* ── Form Errors ─────────────────────────────────────────────────────────── */
.form-error {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: var(--status-danger-bg);
  border-radius: var(--radius-lg);
  color: var(--status-danger-text);
  font-size: var(--text-sm);
  margin-top: var(--space-2);
  animation: slideInDown var(--duration-fast) var(--ease-out);
}

.form-error i {
  flex-shrink: 0;
}

/* ── File Upload ─────────────────────────────────────────────────────────── */
.file-upload-wrapper {
  position: relative;
  border: 2px dashed var(--border-strong);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: rgba(46, 80, 128, 0.02);
  transition: all var(--duration-fast) var(--ease-out);
}

.file-upload-wrapper:hover {
  border-color: var(--color-primary);
  background: rgba(46, 80, 128, 0.06);
}

.file-upload-wrapper.dragover {
  border-color: var(--color-primary);
  background: rgba(46, 80, 128, 0.1);
  box-shadow: 0 0 0 4px rgba(46, 80, 128, 0.1);
}

.file-upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-8) var(--space-6);
  cursor: pointer;
  text-align: center;
}

.upload-icon {
  width: 3rem;
  height: 3rem;
  color: var(--color-primary);
  opacity: 0.7;
  transition: opacity var(--duration-fast);
}

.file-upload-wrapper:hover .upload-icon {
  opacity: 1;
}

.upload-text {
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  font-size: var(--text-base);
}

.upload-hint {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.file-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--status-success-bg);
  border: 1px solid var(--status-success-border);
  border-radius: var(--radius-lg);
  color: var(--status-success-text);
  font-size: var(--text-sm);
  margin-top: var(--space-2);
  animation: slideInDown var(--duration-fast) var(--ease-out);
}

.file-info i {
  flex-shrink: 0;
  font-size: 1.1rem;
}

.file-remove {
  margin-left: auto;
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: var(--space-1) var(--space-2);
  opacity: 0.6;
  transition: opacity var(--duration-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-remove:hover {
  opacity: 1;
}

/* ── Modal Overlay ───────────────────────────────────────────────────────── */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn var(--duration-fast) var(--ease-out);
}

.modal-content {
  background: var(--surface-base);
  border-radius: var(--radius-xl);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  padding: var(--space-8);
  min-width: 320px;
  max-width: 420px;
  animation: scaleIn var(--duration-fast) var(--ease-out);
}

.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

.spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid var(--border-subtle);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.modal-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.modal-message {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}


/* ── Accordion ───────────────────────────────────────────────────────────── */
.guide-accordion {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.accordion-item {
  border: none;
  margin: 0;
  border-radius: var(--radius-lg);
  background: var(--surface-base);
  border: 1px solid var(--border-subtle);
  overflow: hidden;
}

.accordion-button {
  width: 100%;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  background: transparent;
  border: none;
  font-weight: var(--weight-semibold);
  font-size: var(--text-sm);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  text-align: left;
}

.accordion-button:hover {
  background: var(--surface-subtle);
  color: var(--color-primary);
}

.accordion-button.collapsed .chevron {
  transform: rotate(0deg);
}

.accordion-button:not(.collapsed) .chevron {
  transform: rotate(-180deg);
}

.accordion-button i:first-of-type {
  flex-shrink: 0;
  font-size: 1.1rem;
  color: var(--color-primary);
}

.chevron {
  margin-left: auto;
  flex-shrink: 0;
  transition: transform var(--duration-fast) var(--ease-out);
}

.accordion-body {
  padding: var(--space-4);
  background: var(--surface-subtle);
  border-top: 1px solid var(--border-subtle);
  color: var(--text-primary);
  font-size: var(--text-sm);
  line-height: 1.6;
}

.accordion-body p {
  margin: 0 0 var(--space-3) 0;
}

.accordion-body p:last-child {
  margin-bottom: 0;
}

.accordion-body ul,
.accordion-body ol {
  margin: 0 0 var(--space-3) 0;
  padding-left: var(--space-6);
}

.accordion-body li {
  margin-bottom: var(--space-2);
  color: var(--text-primary);
}

.accordion-body li:last-child {
  margin-bottom: 0;
}

.accordion-body code {
  background: var(--surface-base);
  color: var(--color-primary);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-md);
  font-family: 'Courier New', monospace;
  font-size: var(--text-xs);
}

.accordion-body strong {
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
}

.accordion-body .alert {
  margin-top: var(--space-3);
  margin-bottom: 0;
}

/* ── Guide Sections & Styling ──────────────────────────────────────────────── */
.guide-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.guide-section h4 {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.guide-table {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-3) 0;
  font-size: var(--text-sm);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.guide-table thead {
  background: var(--surface-base);
  border-bottom: 2px solid var(--border-strong);
}

.guide-table thead th {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  background: rgba(46, 80, 128, 0.08);
}

.guide-table tbody tr {
  border-bottom: 1px solid var(--border-subtle);
  transition: background var(--duration-fast);
}

.guide-table tbody tr:hover {
  background: rgba(46, 80, 128, 0.02);
}

.guide-table tbody tr.required-row {
  background: rgba(46, 80, 128, 0.04);
  font-weight: var(--weight-semibold);
}

.guide-table td {
  padding: var(--space-3) var(--space-4);
  color: var(--text-primary);
}

.guide-table code {
  background: var(--surface-base);
  color: var(--color-primary);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-md);
  font-family: 'Courier New', monospace;
  font-size: 0.85em;
  white-space: nowrap;
}

.guide-example {
  background: var(--surface-base);
  border-left: 3px solid var(--color-primary);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  line-height: 1.6;
  color: var(--text-primary);
  font-family: 'Courier New', monospace;
}

.guide-example strong {
  display: block;
  margin-bottom: var(--space-2);
  color: var(--color-primary);
  font-family: inherit;
  font-weight: var(--weight-semibold);
}

.guide-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-4);
  margin: var(--space-4) 0;
}

.guide-columns > div {
  background: var(--surface-base);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-subtle);
  font-size: var(--text-sm);
  line-height: 1.7;
}

.guide-columns strong {
  display: block;
  color: var(--color-primary);
  margin-bottom: var(--space-2);
  font-weight: var(--weight-semibold);
}

.guide-columns code {
  background: rgba(46, 80, 128, 0.1);
  color: var(--color-primary);
  padding: 0.15rem 0.35rem;
  border-radius: 0.25rem;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.guide-tip {
  background: var(--status-info-bg);
  border-left: 3px solid var(--status-info-text);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  color: var(--status-info-text);
  font-size: var(--text-sm);
}

.guide-tip strong {
  font-weight: var(--weight-semibold);
}

/* ── Animations ──────────────────────────────────────────────────────────── */
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

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--duration-fast) var(--ease-out);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.expand-enter-active,
.expand-leave-active {
  transition: all var(--duration-fast) var(--ease-out);
}

.expand-enter-from {
  opacity: 0;
  max-height: 0;
}

.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .data-type-selector {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .file-upload-label {
    padding: var(--space-6) var(--space-4);
  }

  .modal-content {
    margin: var(--space-4);
    min-width: auto;
    max-width: calc(100% - var(--space-8));
  }

  .guide-accordion {
    gap: var(--space-2);
  }
}
</style>
