<template>
  <FormPage
    :title="`${isEditMode ? 'Edit' : 'Add'} Staff`"
    description="Please fill in the staff details below"
    eyebrow="Staff"
    submit-label="Save Staff"
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
          v-model="form.first_name"
          type="text"
          label="First Name"
          placeholder="Enter first name"
          required
          :error="fieldErrors.first_name?.[0]"
          hint="Legal first name of the staff member"
        />

        <UiInput
          v-model="form.middle_initial"
          type="text"
          label="Middle Initial"
          placeholder="M"
          maxlength="1"
          :error="fieldErrors.middle_initial?.[0]"
          hint="Single character middle initial"
        />

        <UiInput
          v-model="form.last_name"
          type="text"
          label="Last Name"
          placeholder="Enter last name"
          required
          :error="fieldErrors.last_name?.[0]"
          hint="Legal last name of the staff member"
        />

        <div class="col-span-full">
          <UiSelect
            v-model="form.division"
            label="Division"
            placeholder="Select division"
            :options="divisionOptions.map((d) => ({ value: String(d.id), label: d.name }))"
            :error="fieldErrors.division?.[0]"
            hint="Department or staff division"
          />
        </div>
      </div>
    </BaseFormSection>

    <!-- Security Note -->
    <div class="security-note">
      <ui-icon name="lock" size="16" />
      <span>All staff records are securely encrypted and protected</span>
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
import UiSelect from '@/components/ui/UiSelect.vue'
import {
  createStaffMember,
  fetchDivisions,
  fetchStaffMemberById,
  updateStaffMember,
} from '@/services/staffService'

const route = useRoute()
const router = useRouter()

const staffId = computed(() => route.params.id)
const isEditMode = computed(() => Boolean(staffId.value))

const submitting = ref(false)
const generalError = ref('')
const nonFieldErrors = ref([])
const fieldErrors = reactive({})

const divisionOptions = ref([])

const form = reactive({
  first_name: '',
  middle_initial: '',
  last_name: '',
  division: '',
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
  return {
    first_name: (form.first_name || '').trim(),
    middle_initial: (form.middle_initial || '').trim() || null,
    last_name: (form.last_name || '').trim(),
    division: form.division ? Number(form.division) : null,
  }
}

// ─── Navigation ───────────────────────────────────────────────────────────────

function handleCancel() {
  router.push('/staff')
}

// ─── Bootstrap ────────────────────────────────────────────────────────────────

async function bootstrapForm() {
  clearErrors()

  try {
    const divisions = await fetchDivisions()
    divisionOptions.value = divisions || []

    if (isEditMode.value) {
      const data = await fetchStaffMemberById(staffId.value)
      form.first_name = data.first_name || ''
      form.middle_initial = data.middle_initial || ''
      form.last_name = data.last_name || ''
      form.division = data.division == null ? '' : String(data.division)
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
      await updateStaffMember(staffId.value, payload)
    } else {
      await createStaffMember(payload)
    }

    router.push('/staff')
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
