<template>
  <FormPage
    :title="`${isEditMode ? 'Edit' : 'Add'} Fund Source`"
    description="Provide the fund source details below"
    eyebrow="Fund Sources"
    submit-label="Save Fund Source"
    cancel-label="Cancel"
    @submit="submitForm"
    @cancel="handleCancel"
  >
    <!-- Error Alert -->
    <div v-if="nonFieldErrors.length || generalError" class="form-error">
      <ui-icon name="alert-circle" size="16" />
      <span>{{ generalError || nonFieldErrors[0] }}</span>
    </div>

    <!-- Fund Source Information Section -->
    <BaseFormSection title="Fund Source Information">
      <div class="form-grid">
        <UiInput
          v-model="form.name"
          type="text"
          label="Fund Source"
          placeholder="Fund source name"
          required
          :error="fieldErrors.name?.[0]"
          hint="Provide a unique name for this fund source"
        />

        <UiCurrencyInput
          v-model="form.annual_budget"
          label="Annual Budget"
          :error="fieldErrors.annual_budget?.[0]"
          hint="Total annual budget allocation"
        />
      </div>
    </BaseFormSection>

    <!-- Security Note -->
    <div class="security-note">
      <ui-icon name="lock" size="16" />
      <span>All fund source data is encrypted and securely stored</span>
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
import UiInput from '@/components/ui/UiInput.vue'
import {
  createFundSource,
  fetchFundSourceById,
  updateFundSource,
} from '@/services/fundSourceService'

const route = useRoute()
const router = useRouter()

const fundSourceId = computed(() => route.params.id)
const isEditMode = computed(() => Boolean(fundSourceId.value))

const submitting = ref(false)
const generalError = ref('')
const nonFieldErrors = ref([])
const fieldErrors = reactive({})

const form = reactive({
  name: '',
  annual_budget: null,
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
  const annualBudget = form.annual_budget
  return {
    name: (form.name || '').trim(),
    annual_budget:
      annualBudget === '' || annualBudget == null ? null : Number(annualBudget),
  }
}

// ─── Navigation ───────────────────────────────────────────────────────────────

function handleCancel() {
  router.push('/fund-sources')
}

// ─── Bootstrap ────────────────────────────────────────────────────────────────

async function bootstrapForm() {
  if (!isEditMode.value) return

  clearErrors()

  try {
    const data = await fetchFundSourceById(fundSourceId.value)
    form.name = data.name || ''
    form.annual_budget = data.annual_budget == null ? null : Number(data.annual_budget)
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
      await updateFundSource(fundSourceId.value, payload)
    } else {
      await createFundSource(payload)
    }

    router.push('/fund-sources')
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
