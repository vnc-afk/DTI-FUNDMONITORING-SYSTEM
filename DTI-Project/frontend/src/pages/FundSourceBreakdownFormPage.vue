<template>
  <FormPage
    :title="isEditMode ? 'Edit Breakdown' : 'Add Breakdown'"
    :description="`${displayValue(fund?.name)} — Budget allocation configuration`"
    eyebrow="Fund Sources"
    :submit-label="isEditMode ? 'Update Breakdown' : 'Add Breakdown'"
    cancel-label="Cancel"
    @submit="submitForm"
    @cancel="handleCancel"
  >
    <!-- Error Alert -->
    <div v-if="nonFieldErrors.length || generalError" class="form-error" role="alert">
      <ui-icon name="alert-circle" size="16" />
      <span>{{ generalError || nonFieldErrors[0] }}</span>
    </div>

    <!-- Breakdown Details Section -->
    <BaseFormSection title="Breakdown Details">
      <div class="form-grid">
        <UiSelect
          v-model="form.category"
          label="Category"
          placeholder="Select category"
          :options="selectableCategories.map((item) => ({ value: item.id, label: item.code }))"
          :error="fieldErrors.category?.[0]"
          :disabled="isEditMode"
          required
          hint="Select a predefined breakdown category (OO1-OO3, 4.1A-4.2)"
        />

        <UiCurrencyInput
          v-model="form.budget_amount"
          label="Budget Amount"
          :error="fieldErrors.budget_amount?.[0]"
          required
          :hint="`Max: ₱ ${formatCurrencyRaw(maxBudgetHint)}`"
        />
      </div>
    </BaseFormSection>

    <!-- Security Note -->
    <div class="security-note">
      <ui-icon name="lock" size="16" />
      <span>All budget allocation data is encrypted and securely stored</span>
    </div>
  </FormPage>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseFormSection from '@/components/patterns/BaseFormSection.vue'
import FormPage from '@/components/patterns/FormPage.vue'
import UiCurrencyInput from '@/components/ui/UiCurrencyInput.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import {
  createFundSourceBreakdown,
  fetchBreakdownCategories,
  fetchFundSourceBreakdownById,
  fetchFundSourceBreakdowns,
  fetchFundSourceById,
  updateFundSourceBreakdown,
} from '@/services/fundSourceService'

const route = useRoute()
const router = useRouter()

const fundId = computed(() => Number(route.params.id))
const breakdownId = computed(() => route.params.breakdownId)
const isEditMode = computed(() => Boolean(breakdownId.value))

const submitting = ref(false)
const generalError = ref('')
const nonFieldErrors = ref([])
const fieldErrors = reactive({})

const fund = ref(null)
const categories = ref([])
const existingBreakdowns = ref([])

const form = reactive({
  category: '',
  budget_amount: null,
})

// ─── Derived State ────────────────────────────────────────────────────────────

const usedCategoryIds = computed(() => {
  const ids = new Set(existingBreakdowns.value.map((item) => Number(item.category)))
  if (isEditMode.value && form.category) {
    ids.delete(Number(form.category))
  }
  return ids
})

const selectableCategories = computed(() =>
  categories.value.filter((item) => !usedCategoryIds.value.has(Number(item.id))),
)

const totalAllocatedExcludingCurrent = computed(() =>
  existingBreakdowns.value.reduce((sum, item) => {
    if (isEditMode.value && Number(item.id) === Number(breakdownId.value)) {
      return sum
    }
    return sum + Number(item.budget_amount || 0)
  }, 0),
)

const maxBudgetHint = computed(() => {
  const annual = Number(fund.value?.annual_budget || 0)
  return Math.max(annual - totalAllocatedExcludingCurrent.value, 0)
})

// ─── Formatters ───────────────────────────────────────────────────────────────

function displayValue(value) {
  if (value === null || value === undefined || value === '') return '—'
  return value
}

function formatCurrencyRaw(value) {
  return Number(value || 0).toLocaleString('en-PH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

// ─── Error Handling ───────────────────────────────────────────────────────────

function clearErrors() {
  generalError.value = ''
  nonFieldErrors.value = []
  Object.keys(fieldErrors).forEach((key) => {
    delete fieldErrors[key]
  })
}

function normalizeErrorList(value) {
  if (Array.isArray(value)) return value.map((item) => String(item))
  if (value == null) return []
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
      nonFieldErrors.value = normalizeErrorList(value)
      return
    }
    fieldErrors[key] = normalizeErrorList(value)
  })

  if (!Object.keys(fieldErrors).length && !nonFieldErrors.value.length) {
    generalError.value = payload.message || payload.detail || 'Please correct the errors below.'
  }
}

// ─── Payload ──────────────────────────────────────────────────────────────────

function normalizePayload() {
  return {
    fund_source: fundId.value,
    category: form.category ? Number(form.category) : null,
    budget_amount:
      form.budget_amount == null || form.budget_amount === ''
        ? null
        : Number(form.budget_amount),
  }
}

// ─── Navigation ───────────────────────────────────────────────────────────────

function handleCancel() {
  router.push(`/fund-sources/${fundId.value}`)
}

// ─── Bootstrap ────────────────────────────────────────────────────────────────

async function bootstrapForm() {
  clearErrors()

  try {
    const [fundItem, categoryItems, breakdownItems] = await Promise.all([
      fetchFundSourceById(fundId.value),
      fetchBreakdownCategories(),
      fetchFundSourceBreakdowns(fundId.value),
    ])

    fund.value = fundItem
    categories.value = categoryItems
    existingBreakdowns.value = breakdownItems

    if (isEditMode.value) {
      const breakdown = await fetchFundSourceBreakdownById(breakdownId.value)
      form.category = breakdown.category ? Number(breakdown.category) : ''
      form.budget_amount = breakdown.budget_amount == null ? null : Number(breakdown.budget_amount)
    }
  } catch (error) {
    applyBackendErrors(error)
  }
}

// ─── Submit ───────────────────────────────────────────────────────────────────

async function submitForm() {
  submitting.value = true
  clearErrors()

  try {
    const payload = normalizePayload()

    if (isEditMode.value) {
      await updateFundSourceBreakdown(breakdownId.value, payload)
    } else {
      await createFundSourceBreakdown(payload)
    }

    router.push(`/fund-sources/${fundId.value}`)
  } catch (error) {
    applyBackendErrors(error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  bootstrapForm()
})
</script>