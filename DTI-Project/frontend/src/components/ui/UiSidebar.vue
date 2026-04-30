<template>
  <aside
    id="app-sidebar"
    class="sidebar"
    :class="{ collapsed: isCollapsed }"
    :aria-hidden="isCollapsed"
  >
    <div class="sidebar-brand">
      <router-link to="/" class="sidebar-brand-link" :aria-label="brandLabel" @click="handleNavigate">
        <div class="sidebar-brand-logo">
          <img :src="dtiLogo" alt="DTI logo" class="sidebar-brand-logo-image" />
        </div>
        <div class="sidebar-brand-text">
          <div class="sidebar-brand-name">FundMonitor</div>
          <div class="sidebar-brand-sub">DTI System</div>
        </div>
      </router-link>

      <button
        type="button"
        class="sidebar-close-btn"
        :aria-label="isCollapsed ? 'Open navigation menu' : 'Close navigation menu'"
        @click="emit('close')"
      >
        <ui-icon name="x" size="18" />
      </button>
    </div>

    <nav class="sidebar-nav" aria-label="Primary navigation">
      <div class="sidebar-section-label">Main</div>
      <template v-for="item in mainMenuItems" :key="item.to || item.href">
        <component
          :is="item.type === 'router' ? RouterLink : 'a'"
          :to="item.to"
          :href="item.href"
          :target="item.type === 'href' ? '_self' : undefined"
          :title="item.title"
          :class="['nav-item', { active: isActive(item) }]"
          @click="handleNavigate"
        >
          <ui-icon :name="item.icon" size="20" class="nav-item-icon" />
          <span class="nav-item-text">{{ item.label }}</span>
        </component>
      </template>

      <div class="sidebar-section-label">Data Management</div>
      <template v-for="item in dataManagementItems" :key="item.to || item.href">
        <component
          :is="item.type === 'router' ? RouterLink : 'a'"
          :to="item.to"
          :href="item.href"
          :target="item.type === 'href' ? '_self' : undefined"
          :title="item.title"
          :class="['nav-item', { active: isActive(item) }]"
          @click="handleNavigate"
        >
          <ui-icon :name="item.icon" size="20" class="nav-item-icon" />
          <span class="nav-item-text">{{ item.label }}</span>
        </component>
      </template>

      <div class="sidebar-section-label">Reports</div>
      <template v-for="item in reportsItems" :key="item.to || item.href">
        <component
          :is="item.type === 'router' ? RouterLink : 'a'"
          :to="item.to"
          :href="item.href"
          :target="item.type === 'href' ? '_self' : undefined"
          :title="item.title"
          :class="['nav-item', { active: isActive(item) }]"
          @click="handleNavigate"
        >
          <ui-icon :name="item.icon" size="20" class="nav-item-icon" />
          <span class="nav-item-text">{{ item.label }}</span>
        </component>
      </template>

      <div class="sidebar-section-label">Archive & Audit</div>
      <template v-for="item in archiveAuditItems" :key="item.to || item.href">
        <component
          :is="item.type === 'router' ? RouterLink : 'a'"
          :to="item.to"
          :href="item.href"
          :target="item.type === 'href' ? '_self' : undefined"
          :title="item.title"
          :class="['nav-item', { active: isActive(item) }]"
          @click="handleNavigate"
        >
          <ui-icon :name="item.icon" size="20" class="nav-item-icon" />
          <span class="nav-item-text">{{ item.label }}</span>
        </component>
      </template>
    </nav>

    <div class="sidebar-footer" v-if="$slots.footer || userName || userRole">
      <slot name="footer">
        <button
          type="button"
          class="sidebar-user"
          :aria-label="`Open profile menu for ${displayUserName}`"
          @click="emit('profile-click')"
        >
          <span class="sidebar-avatar" aria-hidden="true">{{ userInitials }}</span>
          <span class="sidebar-user-info">
            <span class="sidebar-user-name">{{ displayUserName }}</span>
            <span class="sidebar-user-role">{{ displayUserRole }}</span>
          </span>
        </button>
      </slot>
    </div>
  </aside>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import { fetchSidebarData } from '@/services/sidebarService'
import UiIcon from '@/components/ui/UiIcon.vue'
import dtiLogo from '@/assets/images/DTI_Logo_2019.png'

const props = defineProps({
  apiEndpoint: { type: String, default: '' },
  isCollapsed: { type: Boolean, default: false },
  userName: { type: String, default: 'Admin User' },
  userRole: { type: String, default: 'Administrator' },
})

const emit = defineEmits(['navigate', 'close', 'profile-click'])

const route = useRoute()
const userState = ref({
  id: 0,
  display_name: '',
  role_label: '',
  is_staff: false,
  is_superuser: false,
})

const brandLabel = 'FundMonitor home'
const displayUserName = computed(() => userState.value.display_name || props.userName || 'User')
const displayUserRole = computed(() => userState.value.role_label || props.userRole || 'User')
const userInitials = computed(() => {
  const nameParts = String(displayUserName.value || 'U')
    .trim()
    .split(/\s+/)
    .filter(Boolean)

  if (nameParts.length === 0) return 'U'

  return nameParts
    .slice(0, 2)
    .map(part => part.charAt(0))
    .join('')
    .toUpperCase()
})

const mainMenuItems = computed(() => ([
  {
    type: 'router',
    to: '/executive-dashboard',
    icon: 'star',
    label: 'Executive Dashboard',
    title: 'Provincial Director Dashboard',
    matchPaths: ['/executive-dashboard'],
  },
  {
    type: 'router',
    to: '/dashboard',
    icon: 'grid-2x2',
    label: 'Dashboard',
    matchPaths: ['/dashboard'],
  },
  {
    type: 'router',
    to: '/master-fund-monitoring',
    icon: 'table-2',
    label: 'Master Fund Monitoring',
    matchPaths: ['/master-fund-monitoring'],
  },
  {
    type: 'router',
    to: '/bank-statements',
    icon: 'building-2',
    label: 'Bank Statements',
    matchPaths: ['/bank-statements'],
  },
]))

const dataManagementItems = computed(() => ([
  {
    type: 'router',
    to: '/import',
    icon: 'upload',
    label: 'Import Data',
    title: 'Import data from Excel or CSV',
    matchPaths: ['/import'],
  },
  {
    type: 'router',
    to: '/suppliers',
    icon: 'user-check',
    label: 'TIN / Suppliers',
    matchPaths: ['/suppliers'],
  },
  {
    type: 'router',
    to: '/fund-sources',
    icon: 'wallet',
    label: 'Fund Sources',
    matchPaths: ['/fund-sources'],
  },
  {
    type: 'router',
    to: '/tax-table',
    icon: 'percent',
    label: 'Tax Table',
    matchPaths: ['/tax-table'],
  },
  {
    type: 'router',
    to: '/staff',
    icon: 'users',
    label: 'Staff List',
    matchPaths: ['/staff'],
  },
  {
    type: 'router',
    to: '/expense-objects',
    icon: 'bookmark',
    label: 'Expense Objects',
    matchPaths: ['/expense-objects'],
  },
  {
    type: 'router',
    to: '/expense-categories',
    icon: 'network',
    label: 'Expense Categories',
    matchPaths: ['/expense-categories'],
  },
]))

const reportsItems = computed(() => ([
  {
    type: 'router',
    to: '/fund-report',
    icon: 'file-chart-column',
    label: 'Fund Report',
    matchPaths: ['/fund-report'],
  },
  {
    type: 'router',
    to: '/mooe-report',
    icon: 'file-text',
    label: 'MOOE Report',
    matchPaths: ['/mooe-report'],
  },
  {
    type: 'router',
    to: '/negosyo-center-report',
    icon: 'building-2',
    label: 'NC Report',
    matchPaths: ['/negosyo-center-report'],
  },
  {
    type: 'router',
    to: '/report',
    icon: 'form',
    label: 'Expenses Report',
    matchPaths: ['/report'],
  },
]))

const archiveAuditItems = computed(() => ([
  {
    type: 'router',
    to: '/archive',
    icon: 'archive',
    label: 'Archive',
    title: 'Archive Management',
    matchPaths: ['/archive'],
  },
  {
    type: 'router',
    to: '/activity-logs',
    icon: 'history',
    label: 'Activity Logs',
    matchPaths: ['/activity-logs'],
  },
  {
    type: 'router',
    to: '/activity-logs/summary',
    icon: 'trending-up',
    label: 'Activity Summary',
    matchPaths: ['/activity-logs/summary'],
  },
  {
    type: 'router',
    to: '/user-accounts',
    icon: 'users',
    label: 'User Accounts',
    title: 'Manage system user accounts',
    matchPaths: ['/user-accounts'],
  },
]))

function isActive(item) {
  const routePath = route.path || '/'
  const browserPath = window.location.pathname || '/'
  const candidates = Array.isArray(item.matchPaths) && item.matchPaths.length ? item.matchPaths : []

  return candidates.some((path) => routePath.startsWith(path) || browserPath.startsWith(path))
}

function handleNavigate() {
  emit('navigate')
}

async function loadSidebarData() {
  try {
    const payload = await fetchSidebarData(props.apiEndpoint)
    userState.value = {
      id: Number(payload?.user?.id || 0),
      display_name: String(payload?.user?.display_name || '').trim(),
      role_label: String(payload?.user?.role_label || '').trim(),
      is_staff: Boolean(payload?.user?.is_staff),
      is_superuser: Boolean(payload?.user?.is_superuser),
    }
  } catch {
    userState.value = {
      id: 0,
      display_name: '',
      role_label: '',
      is_staff: false,
      is_superuser: false,
    }
  }
}

onMounted(() => {
  loadSidebarData()
})
</script>
