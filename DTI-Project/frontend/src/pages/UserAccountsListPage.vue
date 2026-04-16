<template>
  <div class="user-accounts-page">
    <!-- Page Header -->
    <UiPageHeader
      title="User Accounts"
      description="Manage system users, roles, and access permissions"
      eyebrow="Administration"
    >
      <UiButton tag="router-link" to="/user-accounts/new" variant="primary">
        <ui-icon name="plus" size="16" />
        Add User
      </UiButton>
    </UiPageHeader>

    <!-- Summary Cards -->
    <UiSummaryCards
      v-if="summaryCards.length"
      :cards="summaryCards"
    />

    <!-- Toolbar & Filtering -->
    <div class="search-toolbar">
      <SearchInput
        v-model="query"
        placeholder="Search users..."
      />

      <FilterChips
        v-model="statusFilter"
        :chips="normalizedStatusPills"
      />

      <UiButton
        v-if="isSearching"
        variant="secondary"
        @click="handleClear"
      >
        Clear Filters
      </UiButton>

      <UiButton
        variant="secondary"
        :disabled="loading"
        @click="refreshCurrentPage"
      >
        <ui-icon name="rotate-cw" size="14" />
        Refresh
      </UiButton>

      <UiButton
        variant="secondary"
        :disabled="loading || !displayedUsers.length"
        @click="exportUsers"
      >
        <ui-icon name="download" size="14" />
        Export
      </UiButton>

      <UiButton
        v-if="filteredUsers.length"
        variant="secondary"
        @click="openBulkDeleteModal"
      >
        Delete All
      </UiButton>
    </div>

    <!-- Delete Confirmation Modal -->
    <DeleteConfirmModal
      ref="deleteModal"
      :title="deleteModalTitle"
      :message="deleteModalMessage"
      :details="deleteModalDetails"
      :is-loading="confirmBusy"
      :confirm-label="deleteConfirmLabel"
      cancel-label="Cancel"
      @confirm="confirmPendingAction"
      @close="resetDeleteModal"
    />

    <!-- Loading State -->
    <LoadingState v-if="loading" message="Loading user accounts..." />

    <!-- Empty State -->
    <EmptyState
      v-else-if="!displayedUsers.length"
      icon="users"
      title="No user accounts found"
      description="Start by adding your first user or clear your active filters to see matching records."
    >
      <template #actions>
        <UiButton tag="router-link" to="/user-accounts/new" variant="primary">Add User</UiButton>
        <UiButton v-if="isSearching" variant="secondary" @click="handleClear">
          Clear Filters
        </UiButton>
      </template>
    </EmptyState>

    <!-- Data Table -->
    <div v-else class="table-container">
      <UiTable
        :columns="tableColumns"
        :rows="tableRows"
      >
        <template #cell-username="{ value }">
          <span class="cell-username">{{ value }}</span>
        </template>

        <template #cell-full_name="{ value }">
          <div class="cell-name">
            <strong class="name-label">{{ value || '—' }}</strong>
          </div>
        </template>

        <template #cell-role="{ row }">
          <UiBadge
            :text="roleBadgeText(row)"
            :variant="roleBadgeVariant(row)"
            size="sm"
          />
        </template>

        <template #cell-last_login="{ value }">
          <div class="cell-date">
            <div class="date-label">{{ formatLastLogin(value) }}</div>
          </div>
        </template>

        <template #cell-actions="{ row }">
          <div class="action-buttons">
            <ActionButton
              tag="router-link"
              variant="primary"
              :to="`/user-accounts/${row.id}`"
              title="View details"
            >
              <ui-icon name="eye" size="18" />
            </ActionButton>
            <ActionButton
              tag="router-link"
              variant="primary"
              :to="`/user-accounts/${row.id}/edit`"
              title="Edit user"
            >
              <ui-icon name="edit" size="18" />
            </ActionButton>
            <ActionButton
              variant="danger"
              title="Delete user"
              @click="openDeleteModal(row)"
            >
              <ui-icon name="trash-2" size="18" />
            </ActionButton>
          </div>
        </template>
      </UiTable>
    </div>

    <!-- Pagination Footer -->
    <UiTableFooter
      v-if="displayedUsers.length"
      :current-page="currentPage"
      :page-size="pageSize"
      :total-items="allUsers.length"
      @prev-page="handlePageChange(currentPage - 1)"
      @next-page="handlePageChange(currentPage + 1)"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import UiPageHeader from '@/components/ui/UiPageHeader.vue'
import UiSummaryCards from '@/components/ui/UiSummaryCards.vue'
import UiTable from '@/components/ui/UiTable.vue'
import UiTableFooter from '@/components/ui/UiTableFooter.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import DeleteConfirmModal from '@/components/ui/DeleteConfirmModal.vue'
import ActionButton from '@/components/ui/ActionButton.vue'
import SearchInput from '@/components/ui/SearchInput.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import FilterChips from '@/components/ui/FilterChips.vue'
import ExcelJS from 'exceljs'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { downloadWorkbook } from '@/utils/excelExport'
import { deleteUserAccount, fetchAllUserAccounts, bulkDeleteUserAccounts } from '@/services/userAccountsService'

const notificationsStore = useNotificationsStore()
const deleteModal = ref(null)

const loading = ref(false)
const query = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const toolbarResetToken = ref(0)

const allUsers = ref([])
const confirmBusy = ref(false)
const pendingDeleteUser = ref(null)
const pendingDeleteUsers = ref([])
const deleteModalTitle = ref('Delete User Account')
const deleteModalMessage = ref('')
const deleteModalDetails = ref('')
const deleteConfirmLabel = ref('Delete User')
const isBulkDelete = ref(false)

const pageSize = 20

const isSearching = computed(() => Boolean(query.value.trim() || statusFilter.value))

const statusFilterOptions = ref([
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'staff', label: 'Staff' },
  { value: 'superuser', label: 'Superuser' },
])

const normalizedStatusPills = computed(() =>
  statusFilterOptions.value
    .map((option) => ({
      value: String(option?.value || '').trim(),
      label: String(option?.label || option?.value || '').trim(),
    }))
    .filter((option) => option.value)
)

const filteredUsers = computed(() => {
  const q = query.value.toLowerCase().trim()

  return allUsers.value.filter((user) => {
    if (statusFilter.value === 'active' && !user.is_active) return false
    if (statusFilter.value === 'inactive' && user.is_active) return false
    if (statusFilter.value === 'staff' && !user.is_staff) return false
    if (statusFilter.value === 'superuser' && !user.is_superuser) return false
    if (!q) return true

    const haystack = [user.username, user.first_name, user.last_name, user.email]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return haystack.includes(q)
  })
})

const totalPages = computed(() => Math.max(Math.ceil(allUsers.value.length / pageSize), 1))

const displayedUsers = computed(() => {
  if (isSearching.value) return filteredUsers.value
  const start = (currentPage.value - 1) * pageSize
  return allUsers.value.slice(start, start + pageSize)
})

const activeUsersCount = computed(() => allUsers.value.filter((u) => u.is_active).length)
const staffUsersCount = computed(() => allUsers.value.filter((u) => u.is_staff).length)
const superusersCount = computed(() => allUsers.value.filter((u) => u.is_superuser).length)

const summaryCards = computed(() => [
  {
    id: 'active-users',
    label: 'Active Users',
    value: activeUsersCount.value,
    accentColor: 'var(--status-success)',
    iconBg: 'var(--status-success-bg)',
    iconColor: 'var(--status-success)',
  },
  {
    id: 'staff-users',
    label: 'Staff Members',
    value: staffUsersCount.value,
    accentColor: 'var(--brand-navy-600)',
    iconBg: 'var(--brand-navy-50)',
    iconColor: 'var(--brand-navy-600)',
  },
  {
    id: 'superusers',
    label: 'Superusers',
    value: superusersCount.value,
    accentColor: 'var(--status-danger)',
    iconBg: 'var(--status-danger-bg)',
    iconColor: 'var(--status-danger)',
  },
])

const tableColumns = computed(() => [
  { id: 'username', label: 'Username', width: '140px' },
  { id: 'full_name', label: 'Full Name', width: 'flex' },
  { id: 'role', label: 'Role', width: '120px' },
  { id: 'last_login', label: 'Last Login', width: '140px' },
  { id: 'actions', label: 'Actions', width: '110px' },
])

const tableRows = computed(() =>
  displayedUsers.value.map((user) => ({
    id: user.id,
    username: user.username,
    full_name: fullName(user),
    role: user.is_superuser ? 'superuser' : user.is_staff ? 'staff' : 'user',
    last_login: user.last_login,
    is_superuser: user.is_superuser,
    is_staff: user.is_staff,
    is_active: user.is_active,
    ...user,
  }))
)

// Reset to page 1 whenever filters change
watch([query, statusFilter], () => {
  currentPage.value = 1
})

function pushErrorToast(message) {
  notificationsStore.pushToast({
    title: 'User Accounts',
    message,
    variant: 'danger',
  })
}

function pushSuccessToast(message) {
  notificationsStore.pushToast({
    title: 'User Accounts',
    message,
    variant: 'success',
  })
}

function fullName(user) {
  return [user.first_name, user.last_name].filter(Boolean).join(' ').trim()
}

function roleBadgeText(row) {
  if (row.is_superuser) return 'Superuser'
  if (row.is_staff) return 'Staff'
  return 'User'
}

function roleBadgeVariant(row) {
  if (row.is_superuser) return 'error'
  if (row.is_staff) return 'warning'
  return 'default'
}

function formatLastLogin(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function setStatusFilter(value) {
  statusFilter.value = String(value || '').trim()
}

function handleClear() {
  query.value = ''
  statusFilter.value = ''
  currentPage.value = 1
  toolbarResetToken.value += 1
}

function refreshCurrentPage() {
  loadUserAccounts()
}

async function exportUsers() {
  if (!displayedUsers.value.length) {
    pushErrorToast('No user accounts to export.')
    return
  }

  try {
    const workbook = new ExcelJS.Workbook()
    const worksheet = workbook.addWorksheet('User Accounts')

    worksheet.addRow(['Username', 'Full Name', 'Role', 'Status', 'Last Login'])
    displayedUsers.value.forEach((user) => {
      const status = user.is_active ? 'Active' : 'Inactive'
      const role = user.is_superuser ? 'Superuser' : user.is_staff ? 'Staff' : 'User'
      worksheet.addRow([
        user.username || '',
        fullName(user) || '',
        role,
        status,
        formatLastLogin(user.last_login),
      ])
    })

    const fileDate = new Date().toISOString().split('T')[0]
    await downloadWorkbook(workbook, `User_Accounts_${fileDate}.xlsx`)
    pushSuccessToast('User accounts exported successfully.')
  } catch (error) {
    pushErrorToast(error.message || 'Failed to export user accounts.')
  }
}

function handlePageChange(nextPage) {
  if (isSearching.value) return
  if (nextPage < 1 || nextPage > totalPages.value) return
  currentPage.value = nextPage
}

function openDeleteModal(user) {
  pendingDeleteUser.value = user
  pendingDeleteUsers.value = [user.id]
  isBulkDelete.value = false
  deleteConfirmLabel.value = 'Delete User'
  deleteModalMessage.value = `Are you sure you want to delete the user account "${user.username}"?`
  deleteModalDetails.value = fullName(user) || ''
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

function openBulkDeleteModal() {
  const ids = filteredUsers.value.map((item) => item.id)
  if (!ids.length) return

  pendingDeleteUsers.value = ids
  isBulkDelete.value = true
  deleteModalTitle.value = 'Delete User Accounts'
  deleteConfirmLabel.value = 'Delete All'
  deleteModalMessage.value = `Delete ${ids.length} user account${ids.length === 1 ? '' : 's'} from this page? This action cannot be undone.`
  deleteModalDetails.value = `${ids.length} account${ids.length === 1 ? '' : 's'} will be permanently deleted.`
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

async function confirmPendingAction() {
  if (isBulkDelete.value) {
    await bulkDelete()
  } else {
    await confirmDeleteUser()
  }
}

function resetDeleteModal() {
  pendingDeleteUser.value = null
  pendingDeleteUsers.value = []
  isBulkDelete.value = false
  deleteModalTitle.value = 'Delete User Account'
  deleteConfirmLabel.value = 'Delete User'
  deleteModalMessage.value = ''
  deleteModalDetails.value = ''
}

async function confirmDeleteUser() {
  if (!pendingDeleteUser.value) return

  confirmBusy.value = true

  try {
    await deleteUserAccount(pendingDeleteUser.value.id)
    await loadUserAccounts()
    pushSuccessToast('User account deleted successfully.')

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to delete user account.')
  } finally {
    confirmBusy.value = false
  }
}

async function bulkDelete() {
  if (!pendingDeleteUsers.value.length) return

  confirmBusy.value = true

  try {
    await bulkDeleteUserAccounts(pendingDeleteUsers.value)
    await loadUserAccounts()
    pushSuccessToast(`${pendingDeleteUsers.value.length} user account${pendingDeleteUsers.value.length === 1 ? '' : 's'} deleted.`)

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to bulk delete user accounts.')
  } finally {
    confirmBusy.value = false
  }
}

async function loadUserAccounts() {
  loading.value = true

  try {
    const data = await fetchAllUserAccounts()
    allUsers.value = data || []
  } catch (error) {
    pushErrorToast(error.message || 'Failed to fetch user accounts.')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUserAccounts()
})
</script>