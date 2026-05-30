<template>
  <div class="auth-container">
    <div class="auth-card">
      <button 
        class="theme-toggle-auth" 
        type="button" 
        :title="themeToggleTitle" 
        @click="toggleTheme"
        :aria-label="themeToggleTitle"
      >
        <ui-icon :name="themeIcon" />
      </button>

      <div class="auth-header">
        <div class="auth-logos">
          <div class="auth-logo">
            <img :src="logoSrc" alt="DTI Logo" class="dti-logo">
          </div>
          <div class="auth-logo">
            <img :src="bagongLogoSrc" alt="Bagong Pilipinas Logo" class="bagong-logo">
          </div>
        </div>
        <h1>DTI APO Fund Monitoring</h1>
        <p>Fund Management System</p>
      </div>

      <div class="auth-info-box">
        <ui-icon name="info" />
        <span>Enter your credentials to access the fund monitoring dashboard</span>
      </div>

      <form @submit.prevent="submitLogin" novalidate>
        <div v-if="generalError" class="auth-error-message">
          <ui-icon name="circle-alert"/>
          <span>{{ generalError }}</span>
        </div>

        <div class="auth-form-group">
          <label for="id_username" class="auth-form-label">
            <ui-icon name="user" size="20" /> Username
          </label>
          <UiInput
            id="id_username"
            v-model.trim="form.username"
            type="text"
            name="username"
            placeholder="Enter your username"
            autofocus
            required
            :error="fieldErrors.username"
          />
        </div>

        <div class="auth-form-group">
          <label for="id_password" class="auth-form-label">
            <ui-icon name="lock" size="20" /> Password
          </label>
          <UiInput
            id="id_password"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            name="password"
            placeholder="Enter your password"
            required
            :error="fieldErrors.password"
          >
            <template #suffix>
              <UiButton
                type="button"
                variant="ghost"
                size="sm"
                class="auth-password-toggle"
                :aria-label="showPassword ? 'Hide password' : 'Show password'"
                :aria-pressed="showPassword ? 'true' : 'false'"
                :title="showPassword ? 'Hide password' : 'Show password'"
                @click="showPassword = !showPassword"
              >
                <ui-icon :name="showPassword ? 'eye-off' : 'eye'" />
              </UiButton>
            </template>
          </UiInput>
        </div>

        <div class="auth-form-check">
          <UiCheckbox
            id="id_remember"
            v-model="form.remember_me"
            label="Remember me on this device"
          />
        </div>

        <UiButton
          type="submit"
          block
          size="lg"
          :loading="submitting"
          :disabled="submitting"
          class="auth-submit-btn"
        >
          <ui-icon name="log-in" />
          {{ submitting ? 'Signing In...' : 'Sign In' }}
        </UiButton>
      </form>

      <div class="auth-footer">
        <p>Don't have an account? <a href="/admin/">Contact Administrator</a></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import logoSrc from '@/assets/images/DTI_Logo_2019.png'
import bagongLogoSrc from '@/assets/images/Bagong_Pilipinas_logo.png'
import UiIcon from '@/components/ui/UiIcon.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCheckbox from '@/components/ui/UiCheckbox.vue'
import { hasAuthenticatedSession, login, storeAuthSession } from '@/services/authService'

const router = useRouter()

const submitting = ref(false)
const showPassword = ref(false)
const currentTheme = ref('dark')

const generalError = ref('')
const fieldErrors = reactive({
  username: '',
  password: '',
})

const form = reactive({
  username: '',
  password: '',
  remember_me: false,
})

const themeIcon = computed(() => (currentTheme.value === 'light' ? 'moon' : 'sun'))
const themeToggleTitle = computed(() => (currentTheme.value === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'))

function clearErrors() {
  generalError.value = ''
  fieldErrors.username = ''
  fieldErrors.password = ''
}

function applyTheme(theme) {
  const normalized = theme === 'light' ? 'light' : 'dark'
  currentTheme.value = normalized
  document.documentElement.setAttribute('data-theme', normalized)
  localStorage.setItem('dti-theme-preference', normalized)
}

function toggleTheme() {
  const nextTheme = currentTheme.value === 'dark' ? 'light' : 'dark'
  applyTheme(nextTheme)
}

function setBodyAuthMode(enabled) {
  if (enabled) {
    document.body.classList.add('auth-page-body')
  } else {
    document.body.classList.remove('auth-page-body')
  }
}

function parseLoginErrors(error) {
  clearErrors()

  if (!axios.isAxiosError(error)) {
    generalError.value = 'Unable to sign in. Please try again.'
    return
  }

  const payload = error.response?.data || {}

  if (Array.isArray(payload.username) && payload.username.length) {
    fieldErrors.username = String(payload.username[0])
  }

  if (Array.isArray(payload.password) && payload.password.length) {
    fieldErrors.password = String(payload.password[0])
  }

  if (!fieldErrors.username && !fieldErrors.password) {
    generalError.value = payload.detail || payload.message || 'Invalid username or password.'
  }
}

async function submitLogin() {
  submitting.value = true
  clearErrors()

  try {
    const data = await login({
      username: (form.username || '').trim(),
      password: form.password || '',
    })

    storeAuthSession(data)
    const forcePasswordChange = Boolean(data?.user?.force_password_change)
    router.push(forcePasswordChange ? '/change-password' : '/dashboard')
  } catch (error) {
    parseLoginErrors(error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('dti-theme-preference') || 'dark'
  applyTheme(savedTheme)
  setBodyAuthMode(true)

  if (hasAuthenticatedSession()) {
    router.push('/dashboard')
  }
})

onUnmounted(() => {
  setBodyAuthMode(false)
})
</script>
