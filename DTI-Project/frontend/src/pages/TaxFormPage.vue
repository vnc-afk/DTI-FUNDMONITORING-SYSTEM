<template>
  <FormPage
    class="tax-form-page"
    :title="`${isEditMode ? 'Edit' : 'Add'} Tax Entry`"
    description="Provide the tax code details below"
    eyebrow="Tax Table"
    submit-label="Save Tax Entry"
    cancel-label="Cancel"
    @submit="submitForm"
    @cancel="handleCancel"
  >
    <!-- Error Alert -->
    <div v-if="nonFieldErrors.length || generalError" class="form-error">
      <ui-icon name="alert-circle" size="16" />
      <span>{{ generalError || nonFieldErrors[0] }}</span>
    </div>

    <!-- Tax Details Section -->
    <BaseFormSection title="Tax Details">
      <div class="form-grid">
        <UiSelect
          v-model="form.purchase_type"
          label="Purchase Type"
          placeholder="Select purchase type"
          required
          :options="purchaseTypes.map((item) => ({ value: String(item.id), label: item.name }))"
          :error="fieldErrors.purchase_type?.[0]"
          hint="Select the applicable purchase category"
        />
      </div>
    </BaseFormSection>

    <!-- VAT Section -->
    <BaseFormSection title="VAT (20201010-00-01-02)">
      <div class="form-grid">
        <div class="formula-field">
          <UiInput
            v-model="formulaInputs.vat_goods_5"
            label="Goods (5%)"
            placeholder="e.g 0.05/1.12"
            :error="formulaErrors.vat_goods_5 || fieldErrors.vat_goods_5?.[0]"
            hint="Enter a number or formula (e.g. 0.05/1.12)"
          />
          <div class="formula-result" aria-live="polite">
            <span class="formula-result-label">Result</span>
            <div class="formula-result-box">{{ computedResults.vat_goods_5 || '—' }}</div>
          </div>
        </div>

        <div class="formula-field">
          <UiInput
            v-model="formulaInputs.vat_services_5"
            label="Services (5%)"
            placeholder="e.g. 0.1/1.12"
            :error="formulaErrors.vat_services_5 || fieldErrors.vat_services_5?.[0]"
            hint="Enter a number or formula (e.g. 0.05/1.12)"
          />
          <div class="formula-result" aria-live="polite">
            <span class="formula-result-label">Result</span>
            <div class="formula-result-box">{{ computedResults.vat_services_5 || '—' }}</div>
          </div>
        </div>
      </div>
    </BaseFormSection>

    <!-- PT Section -->
    <BaseFormSection title="PT (20201010-00-01-03)">
      <div class="form-grid">
        <div class="formula-field">
          <UiInput
            v-model="formulaInputs.vat_goods_services_3"
            label="Goods &amp; Services (3%)"
            placeholder="e.g. 0.05/1.12"
            :error="formulaErrors.vat_goods_services_3 || fieldErrors.vat_goods_services_3?.[0]"
            hint="Enter a number or formula (e.g. 0.05/1.12, 0.03, 0.01)"
          />
          <div class="formula-result" aria-live="polite">
            <span class="formula-result-label">Result</span>
            <div class="formula-result-box">{{ computedResults.vat_goods_services_3 || '—' }}</div>
          </div>
        </div>
      </div>
    </BaseFormSection>

    <!-- EWT Section -->
    <BaseFormSection title="EWT (20201010-00-01-04)">
      <div class="form-grid">
        <div class="formula-field">
          <UiInput
            v-model="formulaInputs.vat_goods_1"
            label="Goods (1%)"
            placeholder="e.g. =0.01/1.12"
            :error="formulaErrors.vat_goods_1 || fieldErrors.vat_goods_1?.[0]"
            hint="Enter a number or formula (e.g. 0.01/1.12, 0.01)"
          />
          <div class="formula-result" aria-live="polite">
            <span class="formula-result-label">Result</span>
            <div class="formula-result-box">{{ computedResults.vat_goods_1 || '—' }}</div>
          </div>
        </div>

        <div class="formula-field">
          <UiInput
            v-model="formulaInputs.vat_services_2"
            label="Services (2%)"
            placeholder="e.g. 0.05/1.12"
            :error="formulaErrors.vat_services_2 || fieldErrors.vat_services_2?.[0]"
            hint="Enter a number or formula (e.g. 0.05/1.12, 0.02)"
          />
          <div class="formula-result" aria-live="polite">
            <span class="formula-result-label">Result</span>
            <div class="formula-result-box">{{ computedResults.vat_services_2 || '—' }}</div>
          </div>
        </div>

        <div class="formula-field">
          <UiInput
            v-model="formulaInputs.vat_rental_5"
            label="Rental (5%)"
            placeholder="e.g. 0.05/1.12"
            :error="formulaErrors.vat_rental_5 || fieldErrors.vat_rental_5?.[0]"
            hint="Enter a number or formula (e.g. 0.05/1.12, 0.05)"
          />
          <div class="formula-result" aria-live="polite">
            <span class="formula-result-label">Result</span>
            <div class="formula-result-box">{{ computedResults.vat_rental_5 || '—' }}</div>
          </div>
        </div>

        <div class="formula-field">
          <UiInput
            v-model="formulaInputs.vat_prof_fee_10"
            label="Prof. Fee (10%)"
            placeholder="e.g. 0.1/1.12"
            :error="formulaErrors.vat_prof_fee_10 || fieldErrors.vat_prof_fee_10?.[0]"
            hint="Enter a number or formula (e.g. 0.1/1.12, 0.1)"
          />
          <div class="formula-result" aria-live="polite">
            <span class="formula-result-label">Result</span>
            <div class="formula-result-box">{{ computedResults.vat_prof_fee_10 || '—' }}</div>
          </div>
        </div>
      </div>
    </BaseFormSection>

    <!-- Security Note -->
    <div class="security-note">
      <ui-icon name="lock" size="16" />
      <span>All tax data is encrypted and securely stored</span>
    </div>
  </FormPage>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseFormSection from '@/components/patterns/BaseFormSection.vue'
import FormPage from '@/components/patterns/FormPage.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import {
  createTaxTableEntry,
  fetchPurchaseTypes,
  fetchTaxTableEntryById,
  updateTaxTableEntry,
} from '@/services/taxTableService'

const route = useRoute()
const router = useRouter()

const entryId = computed(() => route.params.id)
const isEditMode = computed(() => Boolean(entryId.value))

const submitting = ref(false)
const generalError = ref('')
const nonFieldErrors = ref([])
const fieldErrors = reactive({})

const purchaseTypes = ref([])

const taxRateFields = [
  'vat_goods_5',
  'vat_services_5',
  'vat_goods_services_3',
  'vat_goods_1',
  'vat_services_2',
  'vat_rental_5',
  'vat_prof_fee_10',
]

const form = reactive({
  purchase_type: '',
  vat_goods_5: '',
  vat_services_5: '',
  vat_goods_services_3: '',
  vat_goods_1: '',
  vat_services_2: '',
  vat_rental_5: '',
  vat_prof_fee_10: '',
})

const formulaInputs = reactive({})
const computedResults = reactive({})
const formulaErrors = reactive({})

taxRateFields.forEach((key) => {
  formulaInputs[key] = ''
  computedResults[key] = ''
  formulaErrors[key] = ''
})

function formatComputedNumber(value) {
  if (!Number.isFinite(value)) return ''
  return value.toFixed(5)
}

function tokenizeExpression(expression) {
  const tokens = []
  const src = String(expression || '')
  let i = 0
  let prevType = 'start'

  while (i < src.length) {
    const ch = src[i]
    if (ch === ' ' || ch === '\t' || ch === '\n' || ch === '\r') {
      i += 1
      continue
    }

    if ((ch >= '0' && ch <= '9') || ch === '.') {
      let j = i
      let seenDot = false
      while (j < src.length) {
        const cj = src[j]
        if (cj === '.') {
          if (seenDot) break
          seenDot = true
          j += 1
          continue
        }
        if (cj >= '0' && cj <= '9') {
          j += 1
          continue
        }
        break
      }
      const numStr = src.slice(i, j)
      const num = Number(numStr)
      if (!Number.isFinite(num)) {
        return { tokens: [], error: 'Invalid number' }
      }
      tokens.push({ type: 'number', value: num })
      prevType = 'number'
      i = j
      continue
    }

    if (ch === '(') {
      tokens.push({ type: 'lparen', value: ch })
      prevType = 'lparen'
      i += 1
      continue
    }

    if (ch === ')') {
      tokens.push({ type: 'rparen', value: ch })
      prevType = 'rparen'
      i += 1
      continue
    }

    if (ch === '+' || ch === '-' || ch === '*' || ch === '/') {
      const isUnaryMinus = ch === '-' && (prevType === 'start' || prevType === 'operator' || prevType === 'lparen')
      tokens.push({ type: 'operator', value: isUnaryMinus ? 'u-' : ch })
      prevType = 'operator'
      i += 1
      continue
    }

    return { tokens: [], error: `Invalid character: "${ch}"` }
  }

  return { tokens, error: '' }
}

function toRpn(tokens) {
  const output = []
  const ops = []
  const precedence = { 'u-': 3, '*': 2, '/': 2, '+': 1, '-': 1 }
  const rightAssoc = new Set(['u-'])

  for (const token of tokens) {
    if (token.type === 'number') {
      output.push(token)
      continue
    }

    if (token.type === 'operator') {
      while (ops.length) {
        const top = ops[ops.length - 1]
        if (top.type !== 'operator') break
        const pTop = precedence[top.value]
        const pCur = precedence[token.value]
        const shouldPop = rightAssoc.has(token.value) ? (pCur < pTop) : (pCur <= pTop)
        if (!shouldPop) break
        output.push(ops.pop())
      }
      ops.push(token)
      continue
    }

    if (token.type === 'lparen') {
      ops.push(token)
      continue
    }

    if (token.type === 'rparen') {
      let found = false
      while (ops.length) {
        const op = ops.pop()
        if (op.type === 'lparen') {
          found = true
          break
        }
        output.push(op)
      }
      if (!found) return { rpn: [], error: 'Mismatched parentheses' }
      continue
    }
  }

  while (ops.length) {
    const op = ops.pop()
    if (op.type === 'lparen' || op.type === 'rparen') return { rpn: [], error: 'Mismatched parentheses' }
    output.push(op)
  }

  return { rpn: output, error: '' }
}

function evalRpn(rpn) {
  const stack = []
  for (const token of rpn) {
    if (token.type === 'number') {
      stack.push(token.value)
      continue
    }

    if (token.type === 'operator') {
      if (token.value === 'u-') {
        if (stack.length < 1) return { value: null, error: 'Invalid formula' }
        const a = stack.pop()
        stack.push(-a)
        continue
      }

      if (stack.length < 2) return { value: null, error: 'Invalid formula' }
      const b = stack.pop()
      const a = stack.pop()

      if (token.value === '+') stack.push(a + b)
      else if (token.value === '-') stack.push(a - b)
      else if (token.value === '*') stack.push(a * b)
      else if (token.value === '/') {
        if (b === 0) return { value: null, error: 'Division by zero' }
        stack.push(a / b)
      } else {
        return { value: null, error: 'Invalid operator' }
      }
      continue
    }

    return { value: null, error: 'Invalid formula' }
  }

  if (stack.length !== 1) return { value: null, error: 'Invalid formula' }
  return { value: stack[0], error: '' }
}

function evaluateExpression(expression) {
  const { tokens, error: tokenError } = tokenizeExpression(expression)
  if (tokenError) return { value: null, error: tokenError }
  if (!tokens.length) return { value: null, error: '' }

  const { rpn, error: rpnError } = toRpn(tokens)
  if (rpnError) return { value: null, error: rpnError }

  return evalRpn(rpn)
}

function recomputeField(key) {
  const raw = String(formulaInputs[key] ?? '').trim()
  if (!raw) {
    formulaErrors[key] = ''
    computedResults[key] = ''
    form[key] = ''
    return
  }

  const { value, error } = evaluateExpression(raw)
  if (error) {
    formulaErrors[key] = error
    computedResults[key] = ''
    return
  }

  if (value == null) {
    formulaErrors[key] = 'Invalid formula'
    computedResults[key] = ''
    return
  }

  const computedValue = formatComputedNumber(value)
  formulaErrors[key] = ''
  computedResults[key] = computedValue
  form[key] = computedValue
}

function recomputeAllFields() {
  taxRateFields.forEach((key) => recomputeField(key))
}

const hasFormulaErrors = computed(() =>
  taxRateFields.some((key) => Boolean(String(formulaErrors[key] || '').trim()))
)

taxRateFields.forEach((key) => {
  watch(() => formulaInputs[key], () => recomputeField(key))
})

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
  const payload = { purchase_type: form.purchase_type ? Number(form.purchase_type) : null }
  taxRateFields.forEach((key) => {
    payload[key] = form[key] || ''
  })
  return payload
}

// ─── Navigation ───────────────────────────────────────────────────────────────

function handleCancel() {
  router.push('/tax-table')
}

// ─── Bootstrap ────────────────────────────────────────────────────────────────

async function bootstrapForm() {
  clearErrors()

  try {
    const types = await fetchPurchaseTypes()
    purchaseTypes.value = types || []

    if (isEditMode.value) {
      const data = await fetchTaxTableEntryById(entryId.value)
      form.purchase_type = data.purchase_type == null ? '' : String(data.purchase_type)
      taxRateFields.forEach((key) => {
        const initial = data[key] || ''
        formulaInputs[key] = String(initial)
        computedResults[key] = String(initial)
        form[key] = String(initial)
      })
    }
  } catch (error) {
    applyBackendErrors(error)
  }
}

// ─── Submit ───────────────────────────────────────────────────────────────────

async function submitForm() {
  submitting.value = true
  clearErrors()

  recomputeAllFields()
  if (hasFormulaErrors.value) {
    submitting.value = false
    generalError.value = 'Please fix the invalid tax formulas before saving.'
    return
  }

  try {
    const payload = normalizePayload()

    if (isEditMode.value) {
      await updateTaxTableEntry(entryId.value, payload)
    } else {
      await createTaxTableEntry(payload)
    }

    router.push('/tax-table')
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
