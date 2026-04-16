<template>
  <div class="staff-page">
    <!-- Page Header -->
    <UiPageHeader
      title="Staff Members"
      description="Manage and organize personnel records across all divisions"
      eyebrow="Personnel"
    >

      <UiButton v-if="canManageRecords" tag="router-link" to="/staff/new" variant="primary">
        <ui-icon name="plus" size="16" />
         Add Staff
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
        placeholder="Search staff members..."
      />

      <FilterChips
        v-model="divisionFilter"
        :chips="normalizedDivisionPills"
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
        :disabled="loading || !filteredStaff.length"
        @click="exportStaff"
      >
        <ui-icon name="download" size="14" />
        Export
      </UiButton>

      <UiButton
        v-if="canManageRecords && filteredStaff.length"
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
    <LoadingState v-if="loading" message="Loading staff members..." />

    <!-- Empty State -->
    <EmptyState
      v-else-if="!filteredStaff.length"
      icon="users"
      title="No staff members found"
      description="Start by adding your first staff member or clear your active filters to see matching records."
    >
      <template #actions>
        <UiButton v-if="canManageRecords" tag="router-link" to="/staff/new" variant="primary">Add Staff</UiButton>
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
        <template #cell-full_name="{ value }">
          <div class="cell-name">
            <strong class="name-label">{{ value }}</strong>
          </div>
        </template>

        <template #cell-division_name="{ value }">
          <span :class="value === '—' ? 'text-muted' : 'cell-division'">{{ value }}</span>
        </template>

        <template v-if="canManageRecords" #cell-actions="{ row }">
          <div class="action-buttons">
            <ActionButton
              tag="router-link"
              variant="primary"
              :to="`/staff/${row.id}/edit`"
              title="Edit staff member"
            >
              <ui-icon name="edit" size="18" />
            </ActionButton>
            <ActionButton
              variant="danger"
              title="Delete staff member"
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
      v-if="filteredStaff.length"
      :current-page="page"
      :page-size="pageSize"
      :total-items="totalCount"
      @prev-page="changePage(page - 1)"
      @next-page="changePage(page + 1)"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import UiPageHeader from '@/components/ui/UiPageHeader.vue'
import UiSummaryCards from '@/components/ui/UiSummaryCards.vue'
import UiTable from '@/components/ui/UiTable.vue'
import UiTableFooter from '@/components/ui/UiTableFooter.vue'
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
import { canManageRecords as canManageRecordsAccess } from '@/utils/roleAccess'
import { downloadWorkbook } from '@/utils/excelExport'
import {
  bulkDeleteStaffMembers,
  deleteStaffMember,
  fetchDivisions,
  fetchStaffMembers,
} from '@/services/staffService'

const notificationsStore = useNotificationsStore()
const deleteModal = ref(null)
const canManageRecords = canManageRecordsAccess()

const loading = ref(false)
const query = ref('')
const divisionFilter = ref('')
const page = ref(1)
const toolbarResetToken = ref(0)

const staffMembers = ref([])
const divisionOptions = ref([])
const totalPages = ref(1)
const totalStaffCount = ref(0)
const currentPageSize = ref(20)
const confirmBusy = ref(false)
const pendingDeleteId = ref(null)
const pendingDeleteIds = ref([])
const deleteModalTitle = ref('Delete Staff Member')
const deleteModalMessage = ref('')
const deleteModalDetails = ref('')
const deleteConfirmLabel = ref('Delete Staff')
const isBulkDelete = ref(false)

const pageSize = computed(() => currentPageSize.value)

const isSearching = computed(() => Boolean(query.value.trim() || divisionFilter.value))

const divisionsById = computed(() => {
  const map = new Map()
  divisionOptions.value.forEach((item) => map.set(Number(item.id), item.name))
  return map
})

const normalizedStaff = computed(() =>
  staffMembers.value.map((item) => {
    const first = (item.first_name || '').trim()
    const middle = (item.middle_initial || '').trim()
    const last = (item.last_name || '').trim()
    const fullName = [first, middle, last].filter(Boolean).join(' ').replace(/\s+/g, ' ').trim()
    const divisionName = divisionsById.value.get(Number(item.division)) || '—'
    return { ...item, full_name: fullName, division_name: divisionName }
  })
)

const filteredStaff = computed(() => {
  const q = query.value.toLowerCase().trim()

  return normalizedStaff.value.filter((item) => {
    const divisionMatches = !divisionFilter.value || String(item.division) === divisionFilter.value
    if (!divisionMatches) return false
    if (!q) return true

    const haystack = [item.full_name, item.division_name].join(' ').toLowerCase()
    return haystack.includes(q)
  })
})

const totalCount = computed(() => totalStaffCount.value)

const divisionsCount = computed(() => {
  const used = new Set(normalizedStaff.value.map((s) => Number(s.division)))
  return used.size
})

const summaryCards = computed(() => [
  {
    id: 'staff-total',
    label: 'Staff Members',
    value: totalStaffCount.value,
    accentColor: 'var(--brand-navy-600)',
    iconBg: 'var(--brand-navy-50)',
    iconColor: 'var(--brand-navy-600)',
  },
  {
    id: 'staff-divisions',
    label: 'Divisions',
    value: divisionsCount.value,
    accentColor: 'var(--status-success)',
    iconBg: 'var(--status-success-bg)',
    iconColor: 'var(--status-success)',
  },
  {
    id: 'staff-filtered',
    label: 'Filtered Results',
    value: filteredStaff.value.length,
    accentColor: 'var(--brand-gold-500)',
    iconBg: 'var(--brand-gold-50)',
    iconColor: 'var(--brand-gold-500)',
  },
])

const divisionFilterOptions = computed(() =>
  divisionOptions.value.map((option) => ({ value: String(option.id), label: option.name }))
)

const normalizedDivisionPills = computed(() =>
  divisionFilterOptions.value
    .map((option) => ({
      value: String(option?.value || '').trim(),
      label: String(option?.label || option?.value || '').trim(),
    }))
    .filter((option) => option.value)
)

const tableColumns = computed(() => {
  const columns = [
    { id: 'full_name', label: 'Staff Name', width: 'flex' },
    { id: 'division_name', label: 'Division', width: '160px' },
  ]
  if (canManageRecords) {
    columns.push({ id: 'actions', label: 'Actions', width: '110px' })
  }
  return columns
})

const tableRows = computed(() =>
  filteredStaff.value.map((staff) => ({
    id: staff.id,
    full_name: staff.full_name,
    division_name: staff.division_name,
    ...staff,
  }))
)

function pushErrorToast(message) {
  notificationsStore.pushToast({
    title: 'Staff Members',
    message,
    variant: 'danger',
  })
}

function pushSuccessToast(message) {
  notificationsStore.pushToast({
    title: 'Staff Members',
    message,
    variant: 'success',
  })
}

function setDivisionFilter(value) {
  divisionFilter.value = String(value || '').trim()
}

function handleClear() {
  query.value = ''
  divisionFilter.value = ''
  toolbarResetToken.value += 1
}

function refreshCurrentPage() {
  loadStaffMembers(page.value)
}

async function exportStaff() {
  if (!filteredStaff.value.length) {
    pushErrorToast('No staff members to export.')
    return
  }

  try {
    const workbook = new ExcelJS.Workbook()
    const worksheet = workbook.addWorksheet('Staff Members')

    worksheet.addRow(['Full Name', 'Division'])
    filteredStaff.value.forEach((staff) => {
      worksheet.addRow([staff.full_name || '', staff.division_name || '—'])
    })

    const fileDate = new Date().toISOString().split('T')[0]
    await downloadWorkbook(workbook, `Staff_Members_${fileDate}.xlsx`)
    pushSuccessToast('Staff members exported successfully.')
  } catch (error) {
    pushErrorToast(error.message || 'Failed to export staff members.')
  }
}

function openDeleteModal(staff) {
  pendingDeleteId.value = staff.id
  deleteModalMessage.value = `Are you sure you want to delete staff member "${staff.full_name}"?`
  deleteModalDetails.value = staff.division_name && staff.division_name !== '—'
    ? `Division: ${staff.division_name}`
    : ''
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

function resetDeleteModal() {
  pendingDeleteId.value = null
  pendingDeleteIds.value = []
  isBulkDelete.value = false
  deleteModalTitle.value = 'Delete Staff Member'
  deleteConfirmLabel.value = 'Delete Staff'
  deleteModalMessage.value = ''
  deleteModalDetails.value = ''
}

function openBulkDeleteModal() {
  const ids = filteredStaff.value.map((item) => item.id)
  if (!ids.length) return

  pendingDeleteIds.value = ids
  isBulkDelete.value = true
  deleteModalTitle.value = 'Delete Staff Members'
  deleteConfirmLabel.value = 'Delete All'
  deleteModalMessage.value = `Delete ${ids.length} staff record${ids.length === 1 ? '' : 's'} from this page? This action cannot be undone.`
  deleteModalDetails.value = `${ids.length} record${ids.length === 1 ? '' : 's'} will be permanently deleted.`
  if (deleteModal.value) {
    deleteModal.value.open()
  }
}

async function confirmPendingAction() {
  if (isBulkDelete.value) {
    await bulkDelete()
  } else {
    await confirmDeleteStaff()
  }
}

async function confirmDeleteStaff() {
  if (!pendingDeleteId.value) return

  confirmBusy.value = true

  try {
    await deleteStaffMember(pendingDeleteId.value)
    await loadStaffMembers(page.value)
    pushSuccessToast('Staff member deleted successfully.')

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to delete staff member.')
  } finally {
    confirmBusy.value = false
  }
}

async function bulkDelete() {
  if (!pendingDeleteIds.value.length) return

  confirmBusy.value = true

  try {
    await bulkDeleteStaffMembers(pendingDeleteIds.value)
    await loadStaffMembers(page.value)
    pushSuccessToast(`${pendingDeleteIds.value.length} staff record${pendingDeleteIds.value.length === 1 ? '' : 's'} deleted.`)

    if (deleteModal.value) {
      deleteModal.value.close()
    }
    resetDeleteModal()
  } catch (error) {
    pushErrorToast(error.message || 'Failed to bulk delete staff records.')
  } finally {
    confirmBusy.value = false
  }
}

async function loadStaffMembers(targetPage = 1) {
  loading.value = true

  try {
    const [staffData, divisionsData] = await Promise.all([
      fetchStaffMembers({ page: targetPage }),
      fetchDivisions(),
    ])

    staffMembers.value = staffData.staff || []
    divisionOptions.value = divisionsData || []
    page.value = staffData.pagination?.page || targetPage
    totalPages.value = staffData.pagination?.pages || 1
    totalStaffCount.value = staffData.pagination?.count || 0
    currentPageSize.value = staffData.pagination?.page_size || 20
  } catch (error) {
    pushErrorToast(error.message || 'Failed to fetch staff members.')
  } finally {
    loading.value = false
  }
}

function changePage(nextPage) {
  if (nextPage < 1 || nextPage > totalPages.value) return
  loadStaffMembers(nextPage)
}



onMounted(() => {
  loadStaffMembers(1)
})
</script>
