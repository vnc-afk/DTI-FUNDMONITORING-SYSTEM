<template>
  <FormPage
    :title="`${isEditMode ? 'Edit' : 'Add'} Expense Category`"
    description="Set up expense classification details below"
    eyebrow="Expense Categories"
    submit-label="Save Expense Category"
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
          v-model="form.name"
          type="text"
          label="Category Name"
          placeholder="Enter category name"
          required
          :error="fieldErrors.name?.[0]"
          hint="Provide a unique name for this expense category"
        />

        <div class="col-span-full">
          <UiTextarea
            v-model="form.description"
            label="Description"
            placeholder="Add optional description"
            :rows="4"
            :error="fieldErrors.description?.[0]"
            hint="Optional — briefly describe what this category covers"
          />
        </div>
      </div>
    </BaseFormSection>

    <!-- Category Status Section -->
    <BaseFormSection title="Category Status">
      <div class="status-grid" role="radiogroup" aria-label="Category status">
        <button
          v-for="option in statusOptions"
          :key="option.value"
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
  createExpenseCategory,
  fetchExpenseCategoryById,
  updateExpenseCategory,
} from '@/services/expenseCategoryService'

const route = useRoute()
const router = useRouter()

const categoryId = computed(() => route.params.id)
const isEditMode = computed(() => Boolean(categoryId.value))

const submitting = ref(false)
const generalError = ref('')
const nonFieldErrors = ref([])
const fieldErrors = reactive({})

const statusOptions = [
  {
    value: true,
    label: 'Active',
    description: 'Category is enabled and available for use',
    tone: 'active',
  },
  {
    value: false,
    label: 'Inactive',
    description: 'Category is disabled and hidden from selection',
    tone: 'inactive',
  },
]

const form = reactive({
  name: '',
  description: '',
  is_active: true,
})

// ─── Error Handling ──────────────────────────────────────────────────────────

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
    name: (form.name || '').trim(),
    description: (form.description || '').trim() || null,
    is_active: Boolean(form.is_active),
  }
}

// ─── Navigation ───────────────────────────────────────────────────────────────

function handleCancel() {
  router.push('/expense-categories')
}

// ─── Bootstrap ────────────────────────────────────────────────────────────────

async function bootstrapForm() {
  clearErrors()

  try {
    if (isEditMode.value) {
      const data = await fetchExpenseCategoryById(categoryId.value)
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
      await updateExpenseCategory(categoryId.value, payload)
    } else {
      await createExpenseCategory(payload)
    }

    router.push('/expense-categories')
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

<style scoped>
/* All form styles are now in src/assets/css/patterns/form-pages.css */
</style>