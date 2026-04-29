<template>
  <FormPage
    :title="`${isEditMode ? 'Edit' : 'New'} Fund Monitoring Entry`"
    description="Fill in the details below to record a fund monitoring entry"
    eyebrow="Master Fund Monitoring"
    submit-label="Save Record"
    cancel-label="Cancel"
    :disabled="submitting || loading"
    @submit="submitForm"
    @cancel="handleCancel"
  >

    <!-- Error Alert -->
    <div v-if="nonFieldErrors.length || generalError" class="form-error">
      <ui-icon name="alert-circle" size="16" />
      <span>{{ generalError || nonFieldErrors[0] || 'Please correct the errors below.' }}</span>
    </div>

    <!-- Budget Classification Section -->
    <BaseFormSection title="Budget Classification">
      <div class="form-grid">
        <div class="grid-col-2">
          <UiSelect
            v-model="form.division"
            :options="divisionOptions"
            label="Division"
            placeholder="Select division"
            required
            :error="fieldErrors.division?.[0]"
            hint="Select the division"
          />
        </div>

        <div class="grid-col-2">
          <UiSelect
            v-model="form.fund_source"
            :options="fundSourceOptions"
            label="Fund Source"
            placeholder="Select fund source"
            required
            @update:modelValue="refreshFundBudgetInfo"
            :error="fieldErrors.fund_source?.[0]"
            hint="Select from available fund sources"
          />
        </div>

        <div class="grid-col-2">
          <UiSelect
            v-model="form.mooe"
            :options="mooeCategories"
            label="MOOE"
            placeholder="Select MOOE category"
            required
            @update:modelValue="refreshMooeBudgetInfo"
            :error="fieldErrors.mooe?.[0]"
            hint="Maintenance and Other Operating Expenses"
          />
        </div>

        <div class="grid-col-2">
          <UiSelect
            v-model="form.nc"
            :options="negosyoCenterOptions"
            label="Negosyo Center (NC)"
            placeholder="Select NC"
            required
            :error="fieldErrors.nc?.[0]"
            hint="Negosyo Center"
          />
        </div>
      </div>
    </BaseFormSection>

    <!-- Transaction Information Section -->
    <BaseFormSection title="Transaction Information">
      <div class="form-grid">
        <UiInput
          v-model="form.date"
          type="date"
          label="Date"
          required
          :error="fieldErrors.date?.[0]"
          hint="Transaction date"
        />

        <UiSelect
          v-model="form.payee"
          :options="payeeOptions"
          label="Payee"
          placeholder="Select payee"
          required
          @update:modelValue="onPayeeChange"
          :error="fieldErrors.payee?.[0]"
          hint="Select recipient from supplier list"
        />

        <div class="col-span-full">
          <UiTextarea
            v-model="form.particulars"
            label="Particulars"
            :rows="3"
            placeholder="Transaction details"
            required
            :error="fieldErrors.particulars?.[0]"
            hint="Description of the transaction"
          />
        </div>

        <div class="col-span-full">
          <div class="form-label required">Transaction Type</div>
          <div class="transaction-type-group">
            <div v-for="item in transactionTypes" :key="item.value" class="transaction-type-option">
              <input
                :id="`transaction_type_${item.value}`"
                v-model="form.transaction_type"
                type="radio"
                :value="item.value"
                class="transaction-radio"
              />
              <label :for="`transaction_type_${item.value}`" class="transaction-label">
                <ui-icon :name="item.icon" size="18" />
                <span>{{ item.label }}</span>
              </label>
            </div>
          </div>
          <ul v-if="fieldErrors.transaction_type" class="errorlist">
            <li v-for="err in fieldErrors.transaction_type" :key="err">{{ err }}</li>
          </ul>
        </div>
      </div>
    </BaseFormSection>

    <!-- Financial Details Section -->
    <BaseFormSection title="Financial Details">
      <div class="form-grid">
          <UiCurrencyInput
            v-model="form.payments"
            label="Payments"
            required
            :error="fieldErrors.payments?.[0]"
            hint="Payment amount"
          />

          <UiInput
            v-model="form.dv_number"
            type="number"
            label="DV No."
            :error="fieldErrors.dv_number?.[0]"
            hint="DV number"
          />

          <UiCurrencyInput
            v-model="form.downloads"
            label="Downloads"
            required
            :error="fieldErrors.downloads?.[0]"
            hint="Downloads amount"
          />

        <div class="col-span-full">
          <div class="budget-info">
            <div v-if="fundBudgetInfo" class="budget-card">
              <div class="budget-label"><ui-icon name="wallet" size="18" /> Fund Budget</div>
              <div class="budget-amount">₱{{ formatCurrencyRaw(fundBudgetInfo.available || 0) }}</div>
              <div class="budget-text">Current Available</div>
              <div v-if="paymentPreviewDelta !== 0" class="budget-text">
                Live Preview: ₱{{ formatCurrencyRaw(fundAvailablePreview || 0) }}
              </div>
            </div>

            <div v-if="mooeBudgetInfo" class="budget-card">
              <div class="budget-label"><ui-icon name="coin" size="18" /> MOOE Budget</div>
              <div class="budget-amount">₱{{ formatCurrencyRaw(mooeBudgetInfo.available || 0) }}</div>
              <div class="budget-text">Current Available</div>
              <div v-if="paymentPreviewDelta !== 0" class="budget-text">
                Live Preview: ₱{{ formatCurrencyRaw(mooeAvailablePreview || 0) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </BaseFormSection>

    <!-- Tax Information Section -->
    <BaseFormSection title="Tax Information">
      <div class="form-grid">
        <UiInput
          :model-value="form.tin"
          type="text"
          label="TIN"
          placeholder="Tax Identification Number"
          disabled
          :error="fieldErrors.tin?.[0]"
          hint="Tax Identification Number (auto-populated)"
        />

        <UiInput
          :model-value="form.tax_type"
          type="text"
          label="Tax Type"
          placeholder="Type of tax"
          disabled
          :error="fieldErrors.tax_type?.[0]"
          hint="Type of tax (auto-populated)"
        />

        <UiSelect
          v-model="form.purchase_type"
          :options="purchaseTypeOptions"
          label="Purchase Type"
          placeholder="Select purchase type"
          @update:modelValue="onPurchaseTypeChange"
          :error="fieldErrors.purchase_type?.[0]"
          hint="Type of purchase"
        />
      </div>
    </BaseFormSection>

    <!-- Cheque Information Section -->
    <BaseFormSection title="Cheque Information">
      <div class="form-grid">
        <UiInput
          v-model="form.cheque_number"
          type="text"
          label="Cheque No."
          placeholder="Check number"
          :error="fieldErrors.cheque_number?.[0]"
          hint="Cheque number"
        />

        <UiInput
          v-model="form.cleared_date"
          type="date"
          label="Cleared Date"
          :error="fieldErrors.cleared_date?.[0]"
          hint="Date cheque was cleared"
        />
      </div>
    </BaseFormSection>

    <!-- Account & Classification Section -->
    <BaseFormSection title="Account &amp; Classification">
      <div class="form-grid">
        <div class="grid-col-2">
          <UiSelect
            v-model="form.account_title"
            :options="accountTitleOptions"
            label="Account Title"
            placeholder="Select account title"
            :error="fieldErrors.account_title?.[0]"
            hint="Account title"
          />
        </div>

        <div class="grid-col-2">
          <UiSelect
            v-model="form.expense_classification"
            :options="expenseClassificationOptions"
            label="Expense Classification"
            placeholder="Select classification"
            :error="fieldErrors.expense_classification?.[0]"
            hint="How to classify this expense"
          />
        </div>

        <div class="col-span-full">
          <UiSelect
            v-model="form.staff"
            :options="staffOptions"
            label="Staff"
            placeholder="Select staff"
            :error="fieldErrors.staff?.[0]"
            hint="Responsible staff member"
          />
        </div>
      </div>
    </BaseFormSection>

    <!-- Automatic Tax Calculation Section -->
    <BaseFormSection title="Automatic Tax Calculation">
      <p class="form-hint">These fields are automatically calculated based on the purchase type and payment amount.</p>

      <div class="form-grid-tax">
        <UiCurrencyInput
          v-for="item in automaticTaxFields"
          :key="item.key"
          :model-value="form[item.key]"
          :label="item.label"
          readonly
          :error="fieldErrors[item.key]?.[0]"
        />
      </div>
    </BaseFormSection>

    <!-- Manual Tax Breakdown Section -->
    <BaseFormSection title="Manual Tax Breakdown">

      <div class="manual-override-panel">
        <div class="override-text">
          <p class="override-status">
            {{ manualTaxOverride ? 'Enabled: manual fields are now editable.' : 'Locked: manual fields are protected.' }}
          </p>
        </div>
        <label class="override-switch" for="manualTaxOverrideToggle" title="Toggle manual tax input">
          <input
            id="manualTaxOverrideToggle"
            v-model="manualTaxOverride"
            type="checkbox"
            aria-label="Enable Manual Tax Override"
          />
          <span class="switch-slider"></span>
        </label>
      </div>

      <p class="form-hint">Turn this on only when you need to override the additional tax breakdown manually.</p>

      <div class="form-grid-tax">
        <UiCurrencyInput
          v-for="item in manualTaxFields"
          :key="item.key"
          v-model="form[item.key]"
          :label="item.label"
          :readonly="!manualTaxOverride"
          :error="fieldErrors[item.key]?.[0]"
        />
      </div>
    </BaseFormSection>


    <!-- Security Note -->
    <div class="security-note">
      <ui-icon name="lock" size="16" />
      <span>All data is encrypted and securely stored</span>
    </div>
  </FormPage>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UiIcon from '@/components/ui/UiIcon.vue'
import BaseFormSection from '@/components/patterns/BaseFormSection.vue'
import FormPage from '@/components/patterns/FormPage.vue'
import UiCurrencyInput from '@/components/ui/UiCurrencyInput.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiTextarea from '@/components/ui/UiTextarea.vue'
import {
  createMasterFundMonitoring,
  fetchFundBudget,
  fetchMasterFundMonitoringById,
  fetchMasterFundMonitoringFormOptions,
  fetchMooeBudget,
  fetchSupplierData,
  fetchTaxRates,
  updateMasterFundMonitoring,
} from '@/services/masterFundMonitoringFormService'

const route = useRoute()
const router = useRouter()
const recordId = computed(() => route.params.id)
const isEditMode = computed(() => Boolean(recordId.value))

const submitting = ref(false)
const loading = ref(false)
const generalError = ref('')
const nonFieldErrors = ref([])
const fieldErrors = reactive({})

const manualTaxOverride = ref(false)
const fundBudgetInfo = ref(null)
const mooeBudgetInfo = ref(null)

const options = reactive({
  divisions: [],
  fundSources: [],
  mooeCategories: [],
  negosyoCenters: [],
  suppliers: [],
  purchaseTypes: [],
  accountTitles: [],
  expenseClassifications: [],
  staffList: [],
})

const transactionTypes = [
  { value: 'Disbursement', label: 'Disbursement', icon: 'arrow-right' },
  { value: 'Downloads', label: 'Downloads', icon: 'download' },
]

const automaticTaxFields = [
  { key: 'goods_5_percent', label: 'Goods (5%)' },
  { key: 'services_5_percent', label: 'Services (5%)' },
  { key: 'goods_services_3_percent', label: 'Goods & Services (3%)' },
  { key: 'goods_1_percent', label: 'Goods (1%)' },
  { key: 'services_2_percent', label: 'Services (2%)' },
  { key: 'rental_5_percent', label: 'Rental (5%)' },
  { key: 'prof_fee_10_percent', label: 'Prof. Fee (10%)' },
]

const manualTaxFields = [
  { key: 'goods_5_percent_2', label: 'Goods (5%) (Manual)' },
  { key: 'services_5_percent_2', label: 'Services (5%) (Manual)' },
  { key: 'goods_services_1_percent', label: 'Goods/Services (1%) (Manual)' },
  { key: 'goods_1_percent_2', label: 'Goods (1%) (Manual)' },
  { key: 'services_2_percent_2', label: 'Services (2%) (Manual)' },
  { key: 'rental_5_percent_2', label: 'Rental (5%) (Manual)' },
  { key: 'prof_fee_10_percent_2', label: 'Prof. Fee (10%) (Manual)' },
]

const form = reactive({
  division: '',
  fund_source: '',
  mooe: '',
  nc: '',
  date: '',
  payee: '',
  particulars: '',
  transaction_type: 'Disbursement',
  tin: '',
  tax_type: '',
  purchase_type: '',
  payments: 0,
  dv_number: '',
  downloads: 0,
  cheque_number: '',
  cleared_date: '',
  account_title: '',
  expense_classification: '',
  staff: '',
  goods_5_percent: 0,
  services_5_percent: 0,
  goods_services_3_percent: 0,
  goods_1_percent: 0,
  services_2_percent: 0,
  rental_5_percent: 0,
  prof_fee_10_percent: 0,
  goods_5_percent_2: 0,
  services_5_percent_2: 0,
  goods_services_1_percent: 0,
  goods_1_percent_2: 0,
  services_2_percent_2: 0,
  rental_5_percent_2: 0,
  prof_fee_10_percent_2: 0,
})

// Computed properties for options formatting
const divisionOptions = computed(() =>
  options.divisions.map((item) => ({ value: item.id, label: item.name }))
)

const fundSourceOptions = computed(() =>
  options.fundSources.map((item) => ({ value: item.id, label: item.name }))
)

const mooeCategories = computed(() =>
  options.mooeCategories.map((item) => ({ value: item.id, label: `${item.code}` }))
)

const negosyoCenterOptions = computed(() =>
  options.negosyoCenters.map((item) => ({ value: item.id, label: item.name }))
)

const payeeOptions = computed(() =>
  options.suppliers.map((item) => ({ value: item.id, label: item.supplier }))
)

const purchaseTypeOptions = computed(() =>
  options.purchaseTypes.map((item) => ({ value: item.id, label: item.name }))
)

const accountTitleOptions = computed(() =>
  options.accountTitles.map((item) => ({ value: item.id, label: item.name }))
)

const expenseClassificationOptions = computed(() =>
  options.expenseClassifications.map((item) => ({ value: item.id, label: item.name }))
)

const staffOptions = computed(() =>
  options.staffList.map((item) => ({ value: item.id, label: `${item.first_name} ${item.last_name}` }))
)

const paymentPreviewDelta = computed(() => {
  const paymentAmount = Number(form.payments || 0)

  if (!Number.isFinite(paymentAmount) || paymentAmount <= 0) {
    return 0
  }

  if (form.transaction_type === 'Refund') {
    return paymentAmount
  }

  if (['Disbursement', 'Downloads'].includes(form.transaction_type)) {
    return -paymentAmount
  }

  return 0
})

const fundAvailablePreview = computed(() => {
  const currentAvailable = Number(fundBudgetInfo.value?.available || 0)
  return currentAvailable + paymentPreviewDelta.value
})

const mooeAvailablePreview = computed(() => {
  const currentAvailable = Number(mooeBudgetInfo.value?.available || 0)
  return currentAvailable + paymentPreviewDelta.value
})

function clearErrors() {
  generalError.value = ''
  nonFieldErrors.value = []
  Object.keys(fieldErrors).forEach((key) => {
    delete fieldErrors[key]
  })
}

function toErrorList(value) {
  if (Array.isArray(value)) {
    return value.map((item) => String(item))
  }
  if (value == null) {
    return []
  }
  return [String(value)]
}

function applyBackendErrors(error) {
  clearErrors()

  if (!axios.isAxiosError(error)) {
    generalError.value = 'Unable to submit form. Please try again.'
    return
  }

  const payload = error.response?.data || {}
  const backendErrors = payload.errors || payload

  Object.entries(backendErrors).forEach(([key, value]) => {
    if (key === '__all__' || key === 'non_field_errors') {
      nonFieldErrors.value = toErrorList(value)
      return
    }
    fieldErrors[key] = toErrorList(value)
  })

  if (!Object.keys(fieldErrors).length && !nonFieldErrors.value.length) {
    generalError.value = payload.message || payload.detail || 'Please correct the errors below.'
  }
}

function formatCurrencyRaw(value) {
  const numberValue = Number(value || 0)
  return numberValue.toLocaleString('en-PH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function handleCancel() {
  router.push('/master-fund-monitoring')
}

function sanitizePayload(payload) {
  const result = { ...payload }
  Object.keys(result).forEach((key) => {
    if (result[key] === '') {
      result[key] = null
    }
  })
  return result
}

function setFormFromRecord(record) {
  Object.keys(form).forEach((key) => {
    const value = record[key]

    if (value == null) {
      if (typeof form[key] === 'number') {
        form[key] = 0
      } else {
        form[key] = ''
      }
      return
    }

    if (typeof form[key] === 'number') {
      form[key] = Number(value || 0)
      return
    }

    form[key] = String(value)
  })

  const hasManualValues = manualTaxFields.some((item) => Number(form[item.key] || 0) > 0)
  manualTaxOverride.value = hasManualValues
}

async function bootstrapForm() {
  loading.value = true
  clearErrors()

  try {
    const formOptions = await fetchMasterFundMonitoringFormOptions()
    options.divisions = formOptions.divisions
    options.fundSources = formOptions.fundSources
    options.mooeCategories = formOptions.mooeCategories
    options.negosyoCenters = formOptions.negosyoCenters
    options.suppliers = formOptions.suppliers
    options.purchaseTypes = formOptions.purchaseTypes
    options.accountTitles = formOptions.accountTitles
    options.expenseClassifications = formOptions.expenseClassifications
    options.staffList = formOptions.staffList

    if (isEditMode.value) {
      const record = await fetchMasterFundMonitoringById(recordId.value)
      setFormFromRecord(record)
    }

    await refreshFundBudgetInfo()
    await refreshMooeBudgetInfo()
  } catch (error) {
    applyBackendErrors(error)
  } finally {
    loading.value = false
  }
}

async function onPayeeChange() {
  try {
    const supplierData = await fetchSupplierData(form.payee)
    if (!supplierData) {
      return
    }

    form.tin = supplierData.tin || ''
    form.tax_type = supplierData.vat_status || ''
  } catch {
    // Keep form usable when supplier data API is unavailable.
  }
}

async function onPurchaseTypeChange() {
  try {
    const rates = await fetchTaxRates(form.purchase_type)
    if (!rates) {
      return
    }

    automaticTaxFields.forEach((item) => {
      const rate = Number(rates[item.key] || 0)
      form[item.key] = Number(form.payments || 0) * rate
    })
  } catch {
    // Keep form usable even if tax lookup fails.
  }
}

async function refreshFundBudgetInfo() {
  try {
    fundBudgetInfo.value = await fetchFundBudget(form.fund_source)
  } catch {
    fundBudgetInfo.value = null
  }
}

async function refreshMooeBudgetInfo() {
  try {
    mooeBudgetInfo.value = await fetchMooeBudget(form.mooe)
  } catch {
    mooeBudgetInfo.value = null
  }
}

async function submitForm() {
  submitting.value = true
  clearErrors()

  try {
    const payload = sanitizePayload({ ...form })

    if (isEditMode.value) {
      await updateMasterFundMonitoring(recordId.value, payload)
    } else {
      await createMasterFundMonitoring(payload)
    }

    router.push('/master-fund-monitoring')
  } catch (error) {
    applyBackendErrors(error)
  } finally {
    submitting.value = false
  }
}

watch(
  () => [form.fund_source, form.transaction_type, form.payments],
  () => {
    refreshFundBudgetInfo()
  },
)

watch(
  () => [form.mooe, form.transaction_type, form.payments],
  () => {
    refreshMooeBudgetInfo()
  },
)

watch(
  () => [form.purchase_type, form.payments],
  () => {
    if (form.purchase_type) {
      onPurchaseTypeChange()
    }
  },
)

watch(
  () => form.payments,
  (value) => {
    if (Number(value || 0) > 0) {
      form.transaction_type = 'Disbursement'
    }
  },
)

watch(
  () => form.downloads,
  (value) => {
    if (Number(value || 0) > 0) {
      form.transaction_type = 'Downloads'
    }
  },
)

onMounted(() => {
  bootstrapForm()
})
</script>
