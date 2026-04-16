<template>
  <DashboardPageLayout class="settings-page">
    <div class="settings-container">

      <div class="settings-toast-stack">
        <UiToast v-model="showSaveToast" title="Success" :message="saveSuccessMessage" variant="success" />
        <UiToast v-model="showErrorToast" title="Error" :message="loadError" variant="danger" :auto-close="false" />
      </div>

      <div class="settings-layout">

        <!-- Sidebar Nav -->
        <nav class="settings-nav">
          <div class="settings-nav-header">
              <UiButton :to="'/dashboard'" variant="ghost" size="sm" class="back-btn">
              <ui-icon name="chevron-left" /> Dashboard
            </UiButton>
          </div>
          <div class="settings-nav-title">Settings</div>
          <UiButton
            v-for="tab in settingsTabs"
            :key="tab.value"
            variant="ghost"
            size="sm"
            class="settings-nav-item"
            :class="{ active: activeSettingsTab === tab.value }"
            @click="activeSettingsTab = tab.value"
          >
            <ui-icon :name="tab.icon" size="18" />
            {{ tab.label }}
          </UiButton>
          <hr class="nav-divider">
          <UiButton variant="ghost" size="sm" class="settings-nav-item" @click="isQuickActionsDrawerOpen = true">
            <ui-icon name="zap" size="18" />
            Quick Actions
          </UiButton>
        </nav>

        <!-- Main Content -->
        <div class="settings-main">

          <!-- Preferences Tab -->
          <template v-if="activeSettingsTab === 'preferences'">
            <div class="card settings-card">
              <div class="card-header">
                <span class="card-section-label">Appearance</span>
                <UiBadge :text="`Theme: ${form.theme}`" variant="info" size="sm" />
              </div>
              <div class="settings-card-body">
                <fieldset class="field-group theme-fieldset">
                  <legend class="field-label">Color theme</legend>
                  <p class="field-hint">Applied instantly across all pages</p>
                  <div class="theme-grid">
                    <label
                      class="theme-card"
                      :class="{ selected: form.theme === 'dark' }"
                    >
                      <input v-model="form.theme" type="radio" name="theme" value="dark" class="sr-only" @change="applyTheme('dark')">
                      <div class="theme-preview dark-preview">
                        <div class="preview-bars">
                          <div class="pb w50"></div>
                          <div class="pb w75"></div>
                          <div class="pb w35"></div>
                        </div>
                      </div>
                      <span class="theme-card-name">
                        <span class="theme-radio-indicator"></span>
                        Dark
                      </span>
                    </label>
                    <label
                      class="theme-card"
                      :class="{ selected: form.theme === 'light' }"
                    >
                      <input v-model="form.theme" type="radio" name="theme" value="light" class="sr-only" @change="applyTheme('light')">
                      <div class="theme-preview light-preview">
                        <div class="preview-bars">
                          <div class="pb w50"></div>
                          <div class="pb w75"></div>
                          <div class="pb w35"></div>
                        </div>
                      </div>
                      <span class="theme-card-name">
                        <span class="theme-radio-indicator"></span>
                        Light
                      </span>
                    </label>
                  </div>
                </fieldset>
              </div>
            </div>

            <div class="card settings-card">
              <div class="card-header">
                <span class="card-section-label">Notifications & display</span>
              </div>
              <div class="settings-card-body flush">
                <div class="toggle-row">
                  <div class="toggle-info">
                    <span class="toggle-title">Enable notifications</span>
                    <span class="toggle-desc">Receive system alerts and updates</span>
                  </div>
                  <button
                    class="toggle-switch"
                    :class="{ on: form.notifications_enabled }"
                    type="button"
                    role="switch"
                    :aria-checked="form.notifications_enabled"
                    @click="form.notifications_enabled = !form.notifications_enabled"
                  ></button>
                </div>
                <div class="toggle-row">
                  <div class="toggle-info">
                    <span class="toggle-title">Items per page</span>
                    <span class="toggle-desc">Default rows displayed in tables</span>
                  </div>
                  <UiSelect
                    id="items-per-page"
                    :model-value="String(form.items_per_page)"
                    :options="pageSizeSelectOptions"
                    class="inline-select"
                    @update:modelValue="updateItemsPerPage"
                  />
                </div>
              </div>
            </div>

            <div class="card settings-card action-bar">
              <div class="action-group">
                <UiButton type="button" variant="primary" size="md" :disabled="saving" @click="saveSettings" class="action-btn-primary">
                  <ui-icon :name="saving ? 'hourglass' : 'check-circle-2'" size="18" />
                  {{ saving ? 'Saving...' : 'Save settings' }}
                </UiButton>
                <UiButton type="button" variant="ghost" size="md" @click="loadSettingsData" class="action-btn-secondary">
                  <ui-icon name="rotate-ccw" size="18"/>
                  Discard changes
                </UiButton>
              </div>
              <Transition name="fade">
                <span v-if="saveSuccessMessage" class="saved-indicator">
                  <ui-icon name="check-circle-2" size="18" /> Saved
                </span>
              </Transition>
            </div>
          </template>

          <!-- Account Tab -->
          <template v-else-if="activeSettingsTab === 'account'">
            <div class="card settings-card">
              <div class="card-header">
                <span class="card-section-label">Account information</span>
              </div>
              <div class="settings-card-body">
                <div class="account-grid">
                  <div class="account-field">
                    <span class="af-label">Username</span>
                    <span class="af-value">{{ accountInfo.username || 'Unavailable' }}</span>
                  </div>
                  <div class="account-field">
                    <span class="af-label">Email</span>
                    <span class="af-value">{{ accountInfo.email || 'Not set' }}</span>
                  </div>
                  <div class="account-field">
                    <span class="af-label">Last login</span>
                    <span class="af-value">{{ formattedLastLogin }}</span>
                  </div>
                  <div class="account-field">
                    <span class="af-label">Member since</span>
                    <span class="af-value">{{ formattedDateJoined }}</span>
                  </div>
                </div>
                <div class="info-banner">
                  <ui-icon name="info" size="16"/>
                  <span>Contact support to update your username or email address</span>
                </div>
              </div>
            </div>
          </template>

          <!-- Security Tab -->
          <template v-else-if="activeSettingsTab === 'security'">
            <div class="card settings-card">
              <div class="card-header">
                <span class="card-section-label">Password</span>
              </div>
              <div class="settings-card-body">
                <div class="security-block">
                  <div>
                    <div class="security-block-title">Change password</div>
                    <div class="security-block-desc">Use a strong, unique password you don't use elsewhere</div>
                  </div>
                  <UiButton type="button" variant="primary" size="sm" @click="openPasswordModal" class="security-action-btn">
                    <ui-icon name="lock" size="18" /> Update password
                  </UiButton>
                </div>
              </div>
            </div>

            <div class="card settings-card action-bar danger-action-bar">
              <div class="danger-notice">
                <ui-icon name="alert-triangle" size="16" />
                <span>This action cannot be undone. All data will be permanently deleted.</span>
              </div>
              <UiButton type="button" variant="danger" size="md" class="danger-action-btn">
                <ui-icon name="trash-2" size="18"/> Delete account permanently
              </UiButton>
            </div>
          </template>

        </div>
      </div>
    </div>

    <!-- Quick Actions Drawer -->
    <UiDrawer v-model="isQuickActionsDrawerOpen" title="Quick Actions" side="right">
      <div class="drawer-actions">
        <UiButton variant="ghost" size="sm" class="drawer-action-btn" @click="setTheme('dark')">
          <ui-icon name="moon" size="18"/>
          <span>Test Dark Theme</span>
        </UiButton>
        <UiButton variant="ghost" size="sm" class="drawer-action-btn" @click="setTheme('light')">
          <ui-icon name="sun" size="18"/>
          <span>Test Light Theme</span>
        </UiButton>
        <UiButton variant="ghost" size="sm" class="drawer-action-btn" @click="openPasswordModal">
          <ui-icon name="key" size="18"/>
          <span>Change Password</span>
        </UiButton>
      </div>
    </UiDrawer>

    <!-- Change Password Modal -->
    <UiModal v-model="isPasswordModalOpen" size="md">
      <div class="modal-header settings-modal-header">
        <h5 class="modal-title">
          <ui-icon name="lock" size="18" /> Change Password
        </h5>
        <button type="button" class="btn-close" @click="closePasswordModal"></button>
      </div>

      <form @submit.prevent="submitPasswordChange">
        <div class="modal-body settings-modal-body">
          <Transition name="fade">
            <div v-if="passwordSuccessMessage" class="alert alert--success" role="alert">
              <ui-icon name="check-circle-2" size="18" /> {{ passwordSuccessMessage }}
              <UiButton variant="ghost" size="sm" class="alert-close" aria-label="Close" @click="passwordSuccessMessage = ''">
                <ui-icon name="x" size="18" />
              </UiButton>
            </div>
          </Transition>

          <Transition name="fade">
            <div v-if="passwordGeneralError" class="alert alert--danger" role="alert">
              <ui-icon name="circle-alert" size="18"/> {{ passwordGeneralError }}
              <UiButton variant="ghost" size="sm" class="alert-close" aria-label="Close" @click="passwordGeneralError = ''">
                <ui-icon name="x" size="18"/>
              </UiButton>
            </div>
          </Transition>

          <div v-for="field in passwordFields" :key="field.key" class="form-group">
            <label :for="`id_${field.key}`" class="form-label">
              <ui-icon :name="field.icon" size="16" /> {{ field.label }}
            </label>
            <div class="password-input-wrapper">
              <input
                :id="`id_${field.key}`"
                v-model="passwordForm[field.key]"
                :type="showPassword[field.key] ? 'text' : 'password'"
                :name="field.key"
                class="input"
                :placeholder="field.placeholder"
                required
              >
              <button
                type="button"
                class="password-toggle-btn"
                aria-label="Toggle password visibility"
                @click="togglePasswordVisibility(field.key)"
              >
                <ui-icon :name="showPassword[field.key] ? 'eye-off' : 'eye'" size="18" />
              </button>
            </div>
            <small v-if="passwordFieldErrors[field.key]" class="form-error">
              {{ passwordFieldErrors[field.key] }}
            </small>
          </div>
        </div>

        <div class="modal-footer settings-modal-footer">
          <UiButton type="button" variant="secondary" @click="closePasswordModal">
            <ui-icon name="x" size="18"/> Cancel
          </UiButton>
          <UiButton type="submit" variant="primary" :disabled="passwordSubmitting">
            <ui-icon name="check" size="18"/> {{ passwordSubmitting ? 'Changing...' : 'Change Password' }}
          </UiButton>
        </div>
      </form>
    </UiModal>
  </DashboardPageLayout>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import DashboardPageLayout from '@/components/patterns/DashboardPageLayout.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiDrawer from '@/components/ui/UiDrawer.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiToast from '@/components/ui/UiToast.vue'
import {
  changePassword,
  createUserPreference,
  fetchCurrentUserProfile,
  fetchUserAccountById,
  fetchUserPreferences,
  updateUserPreference,
} from '@/services/settingsService'

// ── Constants ──────────────────────────────────────────────────────────────────
const pageSizeOptions = [10, 25, 50, 100]

const settingsTabs = [
  { value: 'preferences', label: 'Preferences', icon: 'sliders-horizontal' },
  { value: 'account', label: 'Account', icon: 'user' },
  { value: 'security', label: 'Security', icon: 'shield-check' },
]

const passwordFields = [
  { key: 'old_password', label: 'Current Password', icon: 'lock', placeholder: 'Enter your current password' },
  { key: 'new_password1', label: 'New Password', icon: 'key', placeholder: 'Enter a new password' },
  { key: 'new_password2', label: 'Confirm Password', icon: 'key', placeholder: 'Confirm your new password' },
]

// ── State ──────────────────────────────────────────────────────────────────────
const loadError = ref('')
const saveSuccessMessage = ref('')
const saving = ref(false)
const preferenceId = ref(null)
const activeSettingsTab = ref('preferences')
const isPasswordModalOpen = ref(false)
const isQuickActionsDrawerOpen = ref(false)
const passwordSubmitting = ref(false)
const passwordSuccessMessage = ref('')
const passwordGeneralError = ref('')

const form = reactive({
  theme: 'dark',
  notifications_enabled: true,
  items_per_page: 25,
})

const accountInfo = reactive({
  id: null,
  username: '',
  email: '',
  last_login: null,
  date_joined: null,
})

const passwordForm = reactive({
  old_password: '',
  new_password1: '',
  new_password2: '',
})

const showPassword = reactive({
  old_password: false,
  new_password1: false,
  new_password2: false,
})

const passwordFieldErrors = reactive({
  old_password: '',
  new_password1: '',
  new_password2: '',
})

// ── Computed ───────────────────────────────────────────────────────────────────
const formattedLastLogin = computed(() => formatDateTime(accountInfo.last_login, 'Never'))
const formattedDateJoined = computed(() => formatDateTime(accountInfo.date_joined, 'Unavailable', true))

const showSaveToast = computed({
  get: () => Boolean(saveSuccessMessage.value),
  set: (v) => { if (!v) saveSuccessMessage.value = '' },
})

const showErrorToast = computed({
  get: () => Boolean(loadError.value),
  set: (v) => { if (!v) loadError.value = '' },
})

const pageSizeSelectOptions = computed(() =>
  pageSizeOptions.map((o) => ({ value: String(o), label: `${o} items` }))
)

// ── Helpers ────────────────────────────────────────────────────────────────────
function formatDateTime(value, fallback, dateOnly = false) {
  if (!value) return fallback
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return fallback
  if (dateOnly) return date.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })
  return date.toLocaleString('en-US', { month: 'short', day: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false })
}

function applyTheme(theme) {
  const t = theme === 'light' ? 'light' : 'dark'
  form.theme = t
  document.documentElement.setAttribute('data-theme', t)
  localStorage.setItem('dti-theme-preference', t)
}

function setTheme(theme) { applyTheme(theme) }

function handleStorageThemeSync(event) {
  if (event.key !== 'dti-theme-preference' || !event.newValue) return
  applyTheme(event.newValue)
}

function setPreferenceValues(preference) {
  preferenceId.value = preference.id || null
  form.theme = preference.theme || 'dark'
  form.notifications_enabled = Boolean(preference.notifications_enabled)
  form.items_per_page = Number(preference.items_per_page || 25)
  applyTheme(form.theme)
}

function updateItemsPerPage(value) {
  form.items_per_page = Number(value || 25)
}

function resetPasswordErrors() {
  passwordGeneralError.value = ''
  passwordFieldErrors.old_password = ''
  passwordFieldErrors.new_password1 = ''
  passwordFieldErrors.new_password2 = ''
}

function resetPasswordForm() {
  passwordForm.old_password = ''
  passwordForm.new_password1 = ''
  passwordForm.new_password2 = ''
  showPassword.old_password = false
  showPassword.new_password1 = false
  showPassword.new_password2 = false
  passwordSuccessMessage.value = ''
  resetPasswordErrors()
}

function openPasswordModal() {
  isQuickActionsDrawerOpen.value = false
  resetPasswordForm()
  isPasswordModalOpen.value = true
}

function closePasswordModal() { isPasswordModalOpen.value = false }
function togglePasswordVisibility(field) { showPassword[field] = !showPassword[field] }

// ── API ────────────────────────────────────────────────────────────────────────
async function loadSettingsData() {
  loadError.value = ''
  try {
    const [profile, preferences] = await Promise.all([
      fetchCurrentUserProfile(),
      fetchUserPreferences(),
    ])

    accountInfo.id = profile?.id || null
    accountInfo.username = profile?.username || ''
    accountInfo.email = profile?.email || ''

    if (accountInfo.id) {
      try {
        const detailed = await fetchUserAccountById(accountInfo.id)
        accountInfo.last_login = detailed?.last_login || null
        accountInfo.date_joined = detailed?.date_joined || null
      } catch {
        accountInfo.last_login = null
        accountInfo.date_joined = null
      }
    }

    if (preferences.length > 0) {
      setPreferenceValues(preferences[0])
      return
    }

    const created = await createUserPreference({
      theme: form.theme,
      notifications_enabled: form.notifications_enabled,
      items_per_page: form.items_per_page,
      password_changed: true,
    })
    setPreferenceValues(created)
  } catch (error) {
    loadError.value = axios.isAxiosError(error)
      ? error.response?.data?.detail || 'Failed to load user settings.'
      : 'Failed to load user settings.'
  }
}

async function saveSettings() {
  saving.value = true
  loadError.value = ''
  saveSuccessMessage.value = ''
  try {
    const payload = {
      theme: form.theme,
      notifications_enabled: Boolean(form.notifications_enabled),
      items_per_page: Number(form.items_per_page || 25),
    }
    const result = preferenceId.value
      ? await updateUserPreference(preferenceId.value, payload)
      : await createUserPreference(payload)
    setPreferenceValues(result)
    saveSuccessMessage.value = 'Settings saved successfully.'
  } catch (error) {
    loadError.value = axios.isAxiosError(error)
      ? error.response?.data?.detail || 'Unable to save settings.'
      : 'Unable to save settings.'
  } finally {
    saving.value = false
  }
}

async function submitPasswordChange() {
  passwordSubmitting.value = true
  passwordSuccessMessage.value = ''
  resetPasswordErrors()
  try {
    const data = await changePassword({ ...passwordForm })

    if (data?.success) {
      passwordSuccessMessage.value = data.message || 'Password changed successfully!'
      passwordForm.old_password = ''
      passwordForm.new_password1 = ''
      passwordForm.new_password2 = ''
      setTimeout(closePasswordModal, 1500)
      return
    }

    const errors = data?.errors || {}
    passwordFieldErrors.old_password = errors.old_password?.join(', ') || ''
    passwordFieldErrors.new_password1 = errors.new_password1?.join(', ') || ''
    passwordFieldErrors.new_password2 = errors.new_password2?.join(', ') || ''

    if (!passwordFieldErrors.old_password && !passwordFieldErrors.new_password1 && !passwordFieldErrors.new_password2) {
      passwordGeneralError.value = data?.message || 'An error occurred'
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const errors = error.response?.data?.errors || {}
      passwordFieldErrors.old_password = errors.old_password?.join(', ') || ''
      passwordFieldErrors.new_password1 = errors.new_password1?.join(', ') || ''
      passwordFieldErrors.new_password2 = errors.new_password2?.join(', ') || ''
      if (!passwordFieldErrors.old_password && !passwordFieldErrors.new_password1 && !passwordFieldErrors.new_password2) {
        passwordGeneralError.value = error.response?.data?.message || 'An error occurred. Please try again.'
      }
    } else {
      passwordGeneralError.value = 'An error occurred. Please try again.'
    }
  } finally {
    passwordSubmitting.value = false
  }
}

// ── Lifecycle ──────────────────────────────────────────────────────────────────
onMounted(() => {
  loadSettingsData()
  window.addEventListener('storage', handleStorageThemeSync)
})

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageThemeSync)
})
</script>