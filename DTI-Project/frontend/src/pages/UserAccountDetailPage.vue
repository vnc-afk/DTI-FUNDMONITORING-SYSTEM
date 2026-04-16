<template>
  <FormPage root-class="user-account-detail" card-padding="none">
    <template #card>
      <!-- Page Header -->
      <div class="detail-back-row">
        <UiButton tag="router-link" to="/user-accounts" variant="ghost" size="sm">
          <UiIcon name="chevron-left" size="18" />
          Back to User Accounts
        </UiButton>
      </div>

      <UiPageHeader :title="displayName" description="User account information and status" />

      <!-- Alerts -->
      <div v-if="errorMessage || successMessage" class="alerts-container">
        <div v-if="errorMessage" class="alert alert-danger">
          <UiIcon name="alert-triangle" size="18" />
          <span>{{ errorMessage }}</span>
        </div>

        <div v-if="successMessage" class="alert alert-success">
          <UiIcon name="check-circle-2" size="18" />
          <span>{{ successMessage }}</span>
        </div>
      </div>

      <DeleteConfirmModal
        ref="confirmModal"
        :title="confirmModalTitle"
        :message="confirmModalMessage"
        :details="confirmModalDetails"
        :confirm-label="confirmModalConfirmLabel"
        :loading-label="confirmModalLoadingLabel"
        :is-loading="actionLoading"
        cancel-label="Cancel"
        @confirm="confirmPendingAction"
        @close="resetConfirmModal"
      />

      <!-- Main Content -->
      <div class="detail-content">
        <!-- Header Card with User Info -->
        <UiCard class="detail-user-card">
          <div class="detail-user-header">
            <div class="detail-user-avatar">{{ avatarText }}</div>
            <div class="detail-user-info">
              <h2 class="detail-user-name">{{ displayName }}</h2>
              <UiBadge
                :text="viewedUser.is_active ? 'Active' : 'Inactive'"
                :variant="viewedUser.is_active ? 'success' : 'danger'"
                size="sm"
              />
            </div>
          </div>
        </UiCard>

        <!-- Account Information Section -->
        <UiCard title="Account Information">
          <div class="form-grid">
            <div class="info-row">
              <span class="info-label">Username</span>
              <span class="info-value">{{ viewedUser.username || '—' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Email Address</span>
              <span class="info-value">
                <a v-if="viewedUser.email" :href="`mailto:${viewedUser.email}`">{{ viewedUser.email }}</a>
                <span v-else>—</span>
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">First Name</span>
              <span class="info-value">{{ viewedUser.first_name || '—' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Last Name</span>
              <span class="info-value">{{ viewedUser.last_name || '—' }}</span>
            </div>
          </div>
        </UiCard>

        <!-- Status & Activity Section -->
        <UiCard title="Account Status & Activity">
          <div class="form-grid">
            <div class="info-row">
              <span class="info-label">Status</span>
              <UiBadge
                :text="viewedUser.is_active ? 'Active Account' : 'Inactive Account'"
                :variant="viewedUser.is_active ? 'success' : 'danger'"
                size="sm"
              />
            </div>
            <div class="info-row">
              <span class="info-label">Member Since</span>
              <span class="info-value" :title="formatDateTitle(viewedUser.date_joined)">
                {{ formatLongDate(viewedUser.date_joined) }}
                <span class="text-muted">({{ daysActive }} days)</span>
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">Last Login</span>
              <span class="info-value" :title="formatDateTitle(viewedUser.last_login)">
                <template v-if="viewedUser.last_login">
                  {{ formatLongDateTime(viewedUser.last_login) }}
                </template>
                <span v-else>Never logged in</span>
              </span>
            </div>
          </div>
        </UiCard>

        <!-- Permissions & Roles Section -->
        <UiCard title="Permissions & Roles">
          <div class="roles-section">
            <div v-for="role in roles" :key="role.label" class="role-item">
              <UiIcon :name="getIconForRole(role)" size="20" />
              <span>{{ role.label }}</span>
            </div>
          </div>
        </UiCard>

        <!-- Account Actions Section -->
        <UiCard title="Account Actions">
          <div class="actions-grid">
            <UiButton
              tag="router-link"
              :to="`/user-accounts/${viewedUser.id}/edit`"
              variant="primary"
              size="md"
            >
              <UiIcon name="pencil" size="16" />
              Edit Account
            </UiButton>

            <template v-if="!isSelf">
              <UiButton
                variant="secondary"
                :disabled="actionLoading"
                @click="toggleStatus"
              >
                <UiIcon :name="viewedUser.is_active ? 'lock' : 'unlock'" size="16" />
                {{ viewedUser.is_active ? 'Disable Account' : 'Activate Account' }}
              </UiButton>

              <UiButton
                variant="secondary"
                :disabled="actionLoading"
                @click="openResetPasswordModal"
              >
                <UiIcon name="key" size="16" />
                Reset Password
              </UiButton>

              <UiButton
                variant="danger"
                :disabled="actionLoading"
                @click="openDeleteAccountModal"
              >
                <UiIcon name="trash-2" size="16" />
                Delete Account
              </UiButton>
            </template>

            <div v-else class="self-notice">
              <UiIcon name="info" size="16" />
              <span>You cannot modify your own account</span>
            </div>
          </div>
        </UiCard>
      </div>
    </template>
  </FormPage>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FormPage from '@/components/patterns/FormPage.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiPageHeader from '@/components/ui/UiPageHeader.vue'
import DeleteConfirmModal from '@/components/ui/DeleteConfirmModal.vue'
import {
  deleteUserAccount,
  fetchCurrentUserProfile,
  fetchUserAccountById,
  resetUserAccountPassword,
  updateUserAccount,
} from '@/services/userAccountsService'

const route = useRoute()
const router = useRouter()

const viewedUser = ref({
  id: null,
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  is_active: false,
  is_staff: false,
  is_superuser: false,
  date_joined: null,
  last_login: null,
})

const currentUserId = ref(null)
const actionLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const confirmModal = ref(null)
const pendingAction = ref('')
const confirmModalTitle = ref('Confirm Action')
const confirmModalMessage = ref('')
const confirmModalDetails = ref('')
const confirmModalConfirmLabel = ref('Confirm')
const confirmModalLoadingLabel = ref('Processing...')

const displayName = computed(() => {
  const fullName = [viewedUser.value.first_name, viewedUser.value.last_name].filter(Boolean).join(' ').trim()
  return fullName || viewedUser.value.username || 'User'
})

const avatarText = computed(() => {
  const first = (viewedUser.value.first_name || '').trim()
  const last = (viewedUser.value.last_name || '').trim()

  if (first && last) {
    return `${first.charAt(0).toUpperCase()}${last.charAt(0).toUpperCase()}`
  }

  const username = (viewedUser.value.username || '').trim()
  return username ? username.charAt(0).toUpperCase() : 'U'
})

const isSelf = computed(() => viewedUser.value.id === currentUserId.value)

const daysActive = computed(() => {
  if (!viewedUser.value.date_joined) {
    return 0
  }

  const joined = new Date(viewedUser.value.date_joined)
  if (Number.isNaN(joined.getTime())) {
    return 0
  }

  const now = new Date()
  const diffMs = now.getTime() - joined.getTime()
  return Math.max(Math.floor(diffMs / (1000 * 60 * 60 * 24)), 0)
})

const roles = computed(() => {
  if (viewedUser.value.is_superuser) {
    return [{ label: 'Superuser (Full permissions)', role: 'superuser' }]
  }

  if (viewedUser.value.is_staff) {
    return [{ label: 'Staff (Admin access)', role: 'staff' }]
  }

  return [{ label: 'Regular User', role: 'user' }]
})

function getIconForRole(role) {
  const iconMap = {
    superuser: 'crown',
    staff: 'shield-check',
    user: 'user',
  }
  return iconMap[role.role] || 'user'
}

function formatDateTitle(value) {
  if (!value) {
    return 'Never'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return 'Never'
  }

  return date.toLocaleString('sv-SE').replace('T', ' ')
}

function formatLongDate(value) {
  if (!value) {
    return 'Not available'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return 'Not available'
  }

  return date.toLocaleDateString('en-US', {
    month: 'long',
    day: '2-digit',
    year: 'numeric',
  })
}

function formatLongDateTime(value) {
  if (!value) {
    return 'Never logged in'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return 'Never logged in'
  }

  return date.toLocaleString('en-US', {
    month: 'long',
    day: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

async function loadData() {
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const [profile, userData] = await Promise.all([
      fetchCurrentUserProfile(),
      fetchUserAccountById(route.params.id),
    ])

    currentUserId.value = profile?.id || null
    viewedUser.value = {
      ...viewedUser.value,
      ...userData,
    }
  } catch (error) {
    errorMessage.value = error.message || 'Failed to load user account details.'
  }
}

async function toggleStatus() {
  actionLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const updated = await updateUserAccount(viewedUser.value.id, {
      is_active: !viewedUser.value.is_active,
    })

    viewedUser.value = {
      ...viewedUser.value,
      ...updated,
    }

    successMessage.value = viewedUser.value.is_active ? 'Account activated successfully.' : 'Account disabled successfully.'
  } catch (error) {
    errorMessage.value = error.message || 'Failed to toggle account status.'
  } finally {
    actionLoading.value = false
  }
}

function openResetPasswordModal() {
  pendingAction.value = 'resetPassword'
  confirmModalTitle.value = 'Reset Password'
  confirmModalMessage.value = 'Reset this user account password?'
  confirmModalDetails.value = viewedUser.value.username || ''
  confirmModalConfirmLabel.value = 'Reset Password'
  confirmModalLoadingLabel.value = 'Resetting...'
  if (confirmModal.value) {
    confirmModal.value.open()
  }
}

function openDeleteAccountModal() {
  pendingAction.value = 'deleteAccount'
  confirmModalTitle.value = 'Delete Account'
  confirmModalMessage.value = `Delete account ${viewedUser.value.username || ''}?`
  confirmModalDetails.value = 'This action cannot be undone.'
  confirmModalConfirmLabel.value = 'Delete Account'
  confirmModalLoadingLabel.value = 'Deleting...'
  if (confirmModal.value) {
    confirmModal.value.open()
  }
}

function resetConfirmModal() {
  pendingAction.value = ''
  confirmModalTitle.value = 'Confirm Action'
  confirmModalMessage.value = ''
  confirmModalDetails.value = ''
  confirmModalConfirmLabel.value = 'Confirm'
  confirmModalLoadingLabel.value = 'Processing...'
}

function confirmPendingAction() {
  if (pendingAction.value === 'resetPassword') {
    resetPassword()
    return
  }

  if (pendingAction.value === 'deleteAccount') {
    deleteAccount()
  }
}

async function resetPassword() {
  actionLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const data = await resetUserAccountPassword(viewedUser.value.id)
    successMessage.value = data?.message || 'Password reset successfully.'
    if (confirmModal.value) {
      confirmModal.value.close()
    }
  } catch (error) {
    errorMessage.value = error.message || 'Failed to reset password.'
  } finally {
    actionLoading.value = false
  }
}

async function deleteAccount() {
  actionLoading.value = true
  errorMessage.value = ''

  try {
    await deleteUserAccount(viewedUser.value.id)
    router.push('/user-accounts')
  } catch (error) {
    errorMessage.value = error.message || 'Failed to delete account.'
  } finally {
    actionLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
