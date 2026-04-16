<template>
  <FormPage
    :title="`${isEditMode ? 'Edit' : 'Add'} Expense Object`"
    description="Set up account title / expense object details below"
    eyebrow="Expense Objects"
    submit-label="Save Expense Object"
    cancel-label="Cancel"
    @submit="submitForm"
    @cancel="handleCancel"
  >
    <!-- Error Alert -->
    <div v-if="nonFieldErrors.length || generalError" class="form-error">
      <ui-icon name="alert-circle" size="16" />
      <span>{{ generalError || nonFieldErrors[0] }}</span>
    </div>

    <!-- General Info Section -->
    <BaseFormSection title="General Info">
      <div class="form-grid">
        <UiInput
          v-model="form.code"
          type="text"
          label="Code"
          placeholder="Enter object code"
          required
          :error="fieldErrors.code?.[0]"
          hint="Unique identifier code for this expense object"
        />

        <UiInput
          v-model="form.name"
          type="text"
          label="Name"
          placeholder="Enter object name"
          required
          :error="fieldErrors.name?.[0]"
          hint="Full descriptive name of the expense object"
        />

        <div class="col-span-full">
          <UiTextarea
            v-model="form.description"
            label="Description"
            placeholder="Add optional description"
            :rows="4"
            :error="fieldErrors.description?.[0]"
            hint="Optional — briefly describe what this expense object covers"
          />
        </div>
      </div>
    </BaseFormSection>

    <!-- Object Status Section -->
    <BaseFormSection title="Object Status">
      <div class="status-grid" role="radiogroup" aria-label="Object status">
        <button
          v-for="option in statusOptions"
          :key="String(option.value)"
          type="button"
          class="status-card"
          :class="{ active: form.is_active === option.value }"
          :aria-checked="form.is_active === option.value"
          role="radio"
          @click="selectStatus(option.value)"
        >
          <div
            class="status-indicator"
            :class="`status-${option.tone}`"
            aria-hidden="true"
          ></div>
          <div class="status-content">
            <div class="status-label">{{ option.label }}</div>
            <div class="status-desc">{{ option.description }}</div>
          </div>
        </button>
      </div>

      <p v-if="fieldErrors.is_active" class="field-error">
        {{ fieldErrors.is_active[0] }}
      </p>
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
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseFormSection from '@/components/patterns/BaseFormSection.vue'
import FormPage from '@/components/patterns/FormPage.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiTextarea from '@/components/ui/UiTextarea.vue'
import {
  createExpenseObject,
  fetchExpenseObjectById,
  updateExpenseObject,
} from '@/services/expenseObjectService'

const route = useRoute()
const router = useRouter()

const objectId = computed(() => route.params.id)
const isEditMode = computed(() => Boolean(objectId.value))

const submitting = ref(false)
const generalError = ref('')
const nonFieldErrors = ref([])
const fieldErrors = reactive({})

const statusOptions = [
  {
    value: true,
    label: 'Active',
    description: 'Object is enabled and available for use',
    tone: 'active',
  },
  {
    value: false,
    label: 'Inactive',
    description: 'Object is disabled and hidden from selection',
    tone: 'inactive',
  },
]

const form = reactive({
  code: '',
  name: '',
  description: '',
  is_active: true,
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

// ─── Status Selection ─────────────────────────────────────────────────────────

function selectStatus(value) {
  form.is_active = value
}

// ─── Payload ──────────────────────────────────────────────────────────────────

function normalizePayload() {
  return {
    code: (form.code || '').trim(),
    name: (form.name || '').trim(),
    description: (form.description || '').trim() || null,
    is_active: Boolean(form.is_active),
  }
}

// ─── Navigation ───────────────────────────────────────────────────────────────

function handleCancel() {
  router.push('/expense-objects')
}

// ─── Bootstrap ────────────────────────────────────────────────────────────────

async function bootstrapForm() {
  clearErrors()

  try {
    if (isEditMode.value) {
      const data = await fetchExpenseObjectById(objectId.value)
      form.code = data.code || ''
      form.name = data.name || ''
      form.description = data.description || ''
      form.is_active = data.is_active == null ? true : Boolean(data.is_active)
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
      await updateExpenseObject(objectId.value, payload)
    } else {
      await createExpenseObject(payload)
    }

    router.push('/expense-objects')
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
