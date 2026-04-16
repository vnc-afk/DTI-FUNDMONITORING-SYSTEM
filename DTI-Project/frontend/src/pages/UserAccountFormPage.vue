<template>
  <FormPage
    :title="`${isEditMode ? 'Edit' : 'Create New'} User Account`"
    :description="isEditMode ? 'Update user account information and permissions' : 'Add a new user to the system'"
    eyebrow="User Accounts"
    :submit-label="isEditMode ? 'Update User' : 'Create User'"
    cancel-label="Cancel"
    @submit="submitForm"
    @cancel="handleCancel"
  >
    <!-- Error Alert -->
    <div v-if="nonFieldErrors.length || generalError" class="form-error" role="alert">
      <ui-icon name="alert-circle" size="16" />
      <span>{{ generalError || nonFieldErrors[0] }}</span>
    </div>

    <!-- Login Credentials Section -->
    <BaseFormSection title="Login Credentials">
      <div class="form-grid">
        <UiInput
          v-model="form.username"
          type="text"
          label="Username"
          placeholder="username"
          required
          :error="fieldErrors.username?.[0]"
          hint="Required. 3-150 characters. Letters, numbers, dots, underscores, and hyphens only."
        />

        <UiInput
          v-model="form.email"
          type="email"
          label="Email Address"
          placeholder="email@example.com"
          required
          :error="fieldErrors.email?.[0]"
          hint="Primary email address for this account"
        />

        <UiInput
          v-model="form.password"
          type="password"
          label="Password"
          placeholder="Leave blank to keep current"
          :error="fieldErrors.password?.[0]"
          :hint="isEditMode
            ? 'Leave blank to keep current password'
            : 'Leave blank to use temporary password (TempPass123!) — user will change on first login'"
        />
      </div>
    </BaseFormSection>

    <!-- Personal Information Section -->
    <BaseFormSection title="Personal Information">
      <div class="form-grid">
        <UiInput
          v-model="form.first_name"
          type="text"
          label="First Name"
          placeholder="First name"
          :error="fieldErrors.first_name?.[0]"
          hint="Legal first name of the user"
        />

        <UiInput
          v-model="form.last_name"
          type="text"
          label="Last Name"
          placeholder="Last name"
          :error="fieldErrors.last_name?.[0]"
          hint="Legal last name of the user"
        />
      </div>
    </BaseFormSection>

    <!-- Permissions Section -->
    <BaseFormSection title="Permissions">
      <div class="status-grid" role="radiogroup" aria-label="Permission level">
        <button
          v-for="option in permissionOptions"
          :key="option.value"
          type="button"
          class="status-card"
          :class="{ active: form.permission_level === option.value }"
          :aria-checked="form.permission_level === option.value"
          role="radio"
          @click="form.permission_level = option.value"
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

      <p v-if="fieldErrors.is_staff || fieldErrors.is_superuser" class="field-error">
        {{ fieldErrors.is_staff?.[0] || fieldErrors.is_superuser?.[0] }}
      </p>
    </BaseFormSection>

    <!-- Security Note -->
    <div class="security-note">
      <ui-icon name="lock" size="16" />
      <span>All user account data is encrypted and securely stored</span>
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
import {
  createUserAccount,
  fetchUserAccountById,
  updateUserAccount,
} from '@/services/userAccountsService'

const route = useRoute()
const router = useRouter()

const userId = computed(() => route.params.id)
const isEditMode = computed(() => Boolean(userId.value))

const submitting = ref(false)
const generalError = ref('')
const nonFieldErrors = ref([])
const fieldErrors = reactive({})

const permissionOptions = [
  {
    value: 'regular',
    label: 'Regular User',
    description: 'Can access dashboard and view reports',
    tone: 'regular',
  },
  {
    value: 'staff',
    label: 'Staff',
    description: 'Can manage data and access admin interface',
    tone: 'staff',
  },
  {
    value: 'superuser',
    label: 'Superuser',
    description: 'Full system permissions and account management access',
    tone: 'superuser',
  },
]

const form = reactive({
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  permission_level: 'regular',
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

// ─── Permission Helpers ───────────────────────────────────────────────────────

function permissionFlags(level) {
  if (level === 'superuser') return { is_staff: true, is_superuser: true }
  if (level === 'staff') return { is_staff: true, is_superuser: false }
  return { is_staff: false, is_superuser: false }
}

function permissionLevelFromRecord(record) {
  if (record.is_superuser) return 'superuser'
  if (record.is_staff) return 'staff'
  return 'regular'
}

// ─── Payload ──────────────────────────────────────────────────────────────────

function normalizePayload() {
  const { is_staff, is_superuser } = permissionFlags(form.permission_level)
  const payload = {
    username: (form.username || '').trim(),
    email: (form.email || '').trim(),
    first_name: (form.first_name || '').trim(),
    last_name: (form.last_name || '').trim(),
    is_staff,
    is_superuser,
  }
  if (form.password && form.password.trim()) {
    payload.password = form.password.trim()
  }
  return payload
}

// ─── Navigation ───────────────────────────────────────────────────────────────

function handleCancel() {
  router.push('/user-accounts')
}

// ─── Bootstrap ────────────────────────────────────────────────────────────────

async function bootstrapForm() {
  if (!isEditMode.value) return

  clearErrors()

  try {
    const data = await fetchUserAccountById(userId.value)
    form.username = data.username || ''
    form.email = data.email || ''
    form.password = ''
    form.first_name = data.first_name || ''
    form.last_name = data.last_name || ''
    form.permission_level = permissionLevelFromRecord(data)
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
      await updateUserAccount(userId.value, payload)
    } else {
      await createUserAccount(payload)
    }

    router.push('/user-accounts')
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
