<template>
  <FormPage
    :title="`${isEditMode ? 'Edit' : 'New'} Transaction Entry`"
    description="Fill in the details below to record a transaction"
    eyebrow="Bank Statements"
    submit-label="Save Statement"
    cancel-label="Cancel"
    @submit="submitForm"
    @cancel="handleCancel"
  >
    <!-- Error Alert -->
    <div v-if="nonFieldErrors.length || generalError" class="form-error">
      <ui-icon name="alert-circle" size="16" />
      <span>{{ generalError || nonFieldErrors[0] }}</span>
    </div>

    <!-- Transaction Information Section -->
    <BaseFormSection title="Transaction Information">
      <div class="form-grid">
        <UiInput
          v-model="form.date"
          type="date"
          label="Date"
          required
          :error="fieldErrors.date?.[0]"
          hint="Select the transaction date"
        />

        <UiInput
          v-model="form.check_number"
          type="text"
          label="Check/Reference No."
          placeholder="Optional for transfers"
          :error="fieldErrors.check_number?.[0]"
          hint="Optional for transfers"
        />

        <div class="col-span-full">
          <UiTextarea
            v-model="form.description"
            label="Description"
            required
            :rows="3"
            placeholder="Transaction description"
            :error="fieldErrors.description?.[0]"
            hint="Describe the transaction"
          />
        </div>
      </div>
    </BaseFormSection>

    <!-- Amount Details Section -->
    <BaseFormSection title="Amount Details">
      <div class="form-grid">
        <UiCurrencyInput
          v-model="form.debit"
          label="Debit (Money Out)"
          :error="fieldErrors.debit?.[0]"
          hint="Amount going out"
        />

        <UiCurrencyInput
          v-model="form.credit"
          label="Credit (Money In)"
          :error="fieldErrors.credit?.[0]"
          hint="Amount coming in"
        />

        <UiCurrencyInput
          v-model="form.balance"
          label="Balance"
          :error="fieldErrors.balance?.[0]"
          :readonly="isBalanceReadonly"
          required
          :hint="isFirstTransaction ? 'Enter opening balance' : 'Auto-calculated from amounts'"
        />
      </div>

      <!-- Balance Preview -->
      <div v-if="isBalanceReadonly" class="balance-preview" role="status" aria-live="polite">
        <div class="balance-preview-label">Balance Calculation</div>
        <div class="balance-equation">
          <span>₱ {{ formatCurrency(previousBalanceForCalculation) }}</span>
          <span class="operator">+</span>
          <span class="credit-amount">₱ {{ formatCurrency(form.credit || 0) }}</span>
          <span class="operator">−</span>
          <span class="debit-amount">₱ {{ formatCurrency(form.debit || 0) }}</span>
          <span class="operator">=</span>
          <span class="result-amount">₱ {{ formatCurrency(calculatedBalance) }}</span>
        </div>
      </div>
    </BaseFormSection>

    <!-- Transaction Status Section -->
    <BaseFormSection title="Transaction Status">
      <div class="status-grid" role="radiogroup" aria-label="Transaction status">
        <button
          v-for="option in statusOptions"
          :key="option.value"
          type="button"
          class="status-card"
          :class="{ 'active': form.status === option.value }"
          :aria-checked="form.status === option.value"
          role="radio"
          @click="selectStatus(option.value)"
        >
          <div class="status-indicator" :class="`status-${option.tone}`" aria-hidden="true"></div>
          <div class="status-content">
            <div class="status-label">{{ option.label }}</div>
            <div class="status-desc">{{ option.description }}</div>
          </div>
        </button>
      </div>
      
      <p v-if="fieldErrors.status" class="form-error">{{ fieldErrors.status[0] }}</p>
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
import BaseFormSection from '@/components/patterns/BaseFormSection.vue'
import FormPage from '@/components/patterns/FormPage.vue'
import UiCurrencyInput from '@/components/ui/UiCurrencyInput.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiTextarea from '@/components/ui/UiTextarea.vue'
import {
  createBankStatement,
  fetchBankStatementById,
  fetchBankStatementMeta,
  updateBankStatement,
} from '@/services/bankStatementFormService'

const route = useRoute()
const router = useRouter()
const statementId = computed(() => route.params.id)
const isEditMode = computed(() => Boolean(statementId.value))

const submitting = ref(false)
const generalError = ref('')
const fieldErrors = reactive({})
const nonFieldErrors = ref([])

const statusOptions = [
  {
    value: 'Cleared',
    label: 'Cleared',
    description: 'Funds fully posted and reconciled',
    tone: 'cleared',
  },
  {
    value: 'On Process',
    label: 'On Process',
    description: 'Pending clearing or bank confirmation',
    tone: 'process',
  },
]

const isFirstTransaction = ref(true)
const previousBalance = ref(0)

const form = reactive({
  date: '',
  description: '',
  check_number: '',
  debit: 0,
  credit: 0,
  balance: 0,
  status: '',
})

const isBalanceReadonly = computed(() => !isFirstTransaction.value || isEditMode.value)
const previousBalanceForCalculation = computed(() => Number(previousBalance.value || 0))
const calculatedBalance = computed(() => {
  const debit = Number(form.debit || 0)
  const credit = Number(form.credit || 0)
  return previousBalanceForCalculation.value + credit - debit
})

function clearErrors() {
  generalError.value = ''
  nonFieldErrors.value = []
  Object.keys(fieldErrors).forEach((key) => {
    delete fieldErrors[key]
  })
}

function normalizeErrorList(value) {
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
      nonFieldErrors.value = normalizeErrorList(value)
      return
    }

    fieldErrors[key] = normalizeErrorList(value)
  })

  if (!Object.keys(fieldErrors).length && !nonFieldErrors.value.length) {
    generalError.value = payload.message || payload.detail || 'Please correct the errors below.'
  }
}

function selectStatus(value) {
  form.status = value
}

function formatCurrency(value) {
  const parsed = Number(value || 0)
  return parsed.toLocaleString('en-PH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function normalizePayload() {
  return {
    date: form.date,
    description: form.description,
    check_number: String(form.check_number || '').trim() || null,
    debit: Number(form.debit || 0),
    credit: Number(form.credit || 0),
    balance: Number(form.balance || 0),
    status: form.status || null,
  }
}

function handleCancel() {
  router.push('/bank-statements')
}

async function bootstrapForm() {
  clearErrors()

  try {
    const meta = await fetchBankStatementMeta()
    previousBalance.value = Number(meta.previousBalance || 0)
    isFirstTransaction.value = isEditMode.value ? false : Boolean(meta.isFirstTransaction)

    if (isEditMode.value) {
      const data = await fetchBankStatementById(statementId.value)
      form.date = data.date || ''
      form.description = data.description || ''
      form.check_number = data.check_number || ''
      form.debit = Number(data.debit || 0)
      form.credit = Number(data.credit || 0)
      form.balance = Number(data.balance || 0)
      form.status = data.status || ''

      const derivedPreviousBalance = Number(data.balance || 0) - Number(data.credit || 0) + Number(data.debit || 0)
      if (Number.isFinite(derivedPreviousBalance)) {
        previousBalance.value = derivedPreviousBalance
      }
    } else if (!isFirstTransaction.value) {
      form.balance = Number(previousBalance.value || 0)
    }
  } catch (error) {
    applyBackendErrors(error)
  }
}

async function submitForm() {
  submitting.value = true
  clearErrors()

  try {
    const payload = normalizePayload()
    if (isEditMode.value) {
      await updateBankStatement(statementId.value, payload)
    } else {
      await createBankStatement(payload)
    }

    router.push('/bank-statements')
  } catch (error) {
    applyBackendErrors(error)
  } finally {
    submitting.value = false
  }
}

watch(
  () => [form.debit, form.credit, isBalanceReadonly.value, previousBalanceForCalculation.value],
  () => {
    if (isBalanceReadonly.value) {
      form.balance = calculatedBalance.value
    }
  },
  { immediate: true },
)

onMounted(() => {
  bootstrapForm()
})
</script>
