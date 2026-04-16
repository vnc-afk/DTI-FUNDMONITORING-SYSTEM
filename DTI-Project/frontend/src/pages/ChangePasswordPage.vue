<template>
  <FormPage root-class="password-change-wrapper" card-padding="none">
    <template #card>
      <div class="password-change-container">
      <div class="password-change-header">
        <div class="icon-wrapper">
          <ui-icon name="lock" size="20" />
        </div>
        <h1>{{ pageTitle }}</h1>
        <p>{{ pageSubtitle }}</p>
      </div>

      <div v-if="forceChange" class="alert alert-info" role="alert">
        <ui-icon name="info" size="18" />
        <div>This is your first login. Please create a new secure password to protect your account.</div>
      </div>

      <form @submit.prevent="submitPasswordChange" novalidate class="password-form">
        <div v-if="nonFieldErrors.length" class="form-error" role="alert">
          <ui-icon name="alert-circle" size="16" />
          <span>{{ nonFieldErrors[0] }}</span>
        </div>

        <div class="form-section">
          <div class="form-section-header">
            <ui-icon name="lock" size="18" />
            <h3>New Password</h3>
          </div>

          <div class="form-section-content">
            <UiInput
              id="id_new_password1"
              v-model="form.new_password1"
              :type="showPassword.new_password1 ? 'text' : 'password'"
              label="Password"
              name="new_password1"
              placeholder="Enter new password"
              autocomplete="new-password"
              required
              :error="fieldErrors.new_password1?.[0]"
            >
              <template #suffix>
                <UiButton
                  type="button"
                  variant="ghost"
                  size="sm"
                  class="password-toggle-btn"
                  :aria-label="showPassword.new_password1 ? 'Hide password' : 'Show password'"
                  :aria-pressed="showPassword.new_password1 ? 'true' : 'false'"
                  :title="showPassword.new_password1 ? 'Hide password' : 'Show password'"
                  @click="togglePassword('new_password1')"
                >
                  <ui-icon :name="showPassword.new_password1 ? 'eye-off' : 'eye'" size="18" class="pwd-toggle-icon" />
                </UiButton>
              </template>
            </UiInput>

            <UiInput
              id="id_new_password2"
              v-model="form.new_password2"
              :type="showPassword.new_password2 ? 'text' : 'password'"
              label="Confirm Password"
              name="new_password2"
              placeholder="Confirm new password"
              autocomplete="new-password"
              required
              :error="fieldErrors.new_password2?.[0]"
            >
              <template #suffix>
                <UiButton
                  type="button"
                  variant="ghost"
                  size="sm"
                  class="password-toggle-btn"
                  :aria-label="showPassword.new_password2 ? 'Hide password' : 'Show password'"
                  :aria-pressed="showPassword.new_password2 ? 'true' : 'false'"
                  :title="showPassword.new_password2 ? 'Hide password' : 'Show password'"
                  @click="togglePassword('new_password2')"
                >
                  <ui-icon :name="showPassword.new_password2 ? 'eye-off' : 'eye'" size="18" class="pwd-toggle-icon" />
                </UiButton>
              </template>
            </UiInput>
          </div>
        </div>

        <div class="password-requirements-card">
          <div class="requirements-header">
            <ui-icon name="shield-check" size="18" />
            <h4>Password Requirements</h4>
          </div>
          <ul class="requirements-list">
            <li>
              <span class="requirement-icon">
                <ui-icon name="check" size="16" />
              </span>
              <span>At least 8 characters long</span>
            </li>
            <li>
              <span class="requirement-icon">
                <ui-icon name="check" size="16" />
              </span>
              <span>Mix of uppercase and lowercase letters</span>
            </li>
            <li>
              <span class="requirement-icon">
                <ui-icon name="check" size="16" />
              </span>
              <span>At least one number</span>
            </li>
          </ul>
        </div>

        <div class="form-actions">
          <UiButton type="submit" block :loading="submitting" :disabled="loadingContext || submitting">
            <ui-icon name="check-circle-2" size="18" />
            {{ submitting ? 'Changing Password...' : 'Change Password' }}
          </UiButton>
        </div>
      </form>
      </div>
    </template>
  </FormPage>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import UiIcon from '@/components/ui/UiIcon.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import FormPage from '@/components/patterns/FormPage.vue'
import { changeInitialPassword, fetchInitialPasswordContext } from '@/services/authService'

const router = useRouter()

const loadingContext = ref(true)
const submitting = ref(false)

const forceChange = ref(true)
const pageTitle = ref('Change Your Password')
const subtitleWhenForced = ref('You must change your temporary password before continuing')
const subtitleDefault = ref('Update your account password to keep it secure')
const newPasswordHelpText = ref('Must contain uppercase, lowercase, numbers. At least 8 characters.')

const form = reactive({
  new_password1: '',
  new_password2: '',
})

const showPassword = reactive({
  new_password1: false,
  new_password2: false,
})

const fieldErrors = reactive({
  new_password1: [],
  new_password2: [],
})

const nonFieldErrors = ref([])

const pageSubtitle = computed(() => (forceChange.value ? subtitleWhenForced.value : subtitleDefault.value))

function clearErrors() {
  fieldErrors.new_password1 = []
  fieldErrors.new_password2 = []
  nonFieldErrors.value = []
}

function normalizeErrorList(value) {
  if (Array.isArray(value)) {
    return value.map((item) => String(item))
  }
  if (typeof value === 'string' && value.trim()) {
    return [value.trim()]
  }
  return []
}

function parseApiErrors(error) {
  clearErrors()

  if (!axios.isAxiosError(error)) {
    nonFieldErrors.value = ['Unable to change password. Please try again.']
    return
  }

  const payload = error.response?.data || {}
  const payloadErrors = payload.errors || {}

  fieldErrors.new_password1 = normalizeErrorList(payloadErrors.new_password1)
  fieldErrors.new_password2 = normalizeErrorList(payloadErrors.new_password2)

  const nonField = normalizeErrorList(payload.non_field_errors)
  if (nonField.length) {
    nonFieldErrors.value = nonField
    return
  }

  if (payload.message) {
    nonFieldErrors.value = [String(payload.message)]
    return
  }

  nonFieldErrors.value = ['Please fix the errors below.']
}

function togglePassword(field) {
  showPassword[field] = !showPassword[field]
}

async function loadContext() {
  loadingContext.value = true

  try {
    const data = await fetchInitialPasswordContext()
    forceChange.value = Boolean(data?.force_change)
    pageTitle.value = data?.title || pageTitle.value
    subtitleWhenForced.value = data?.subtitle || subtitleWhenForced.value
    subtitleDefault.value = 'Update your account password to keep it secure'
    newPasswordHelpText.value = data?.new_password_help_text || newPasswordHelpText.value
  } catch (error) {
    parseApiErrors(error)
  } finally {
    loadingContext.value = false
  }
}

async function submitPasswordChange() {
  submitting.value = true
  clearErrors()

  try {
    await changeInitialPassword({
      new_password1: form.new_password1,
      new_password2: form.new_password2,
    })
    router.push('/dashboard')
  } catch (error) {
    parseApiErrors(error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadContext()
})
</script>
