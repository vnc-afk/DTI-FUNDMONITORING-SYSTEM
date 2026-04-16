<template>
  <header class="topbar" ref="topbarRoot">
    <div class="topbar-primary">
      <button
        class="topbar-icon-btn topbar-menu-btn"
        type="button"
        aria-controls="app-sidebar"
        :aria-expanded="!sidebarCollapsed"
        :aria-label="sidebarToggleLabel"
        @click="emit('toggle-sidebar')"
      >
        <ui-icon :name="sidebarToggleIcon" size="20" />
      </button>

      <!-- Breadcrumbs -->
      <nav class="topbar-breadcrumb" v-if="breadcrumbs.length" aria-label="Breadcrumb">
        <span v-for="(item, idx) in breadcrumbs" :key="idx" class="breadcrumb-segment">
          <router-link v-if="item.to" :to="item.to" class="breadcrumb-link">
            {{ item.label }}
          </router-link>
          <span v-else class="breadcrumb-current" :aria-current="idx === breadcrumbs.length - 1 ? 'page' : undefined">
            {{ item.label }}
          </span>
          <span v-if="idx < breadcrumbs.length - 1" class="breadcrumb-sep" aria-hidden="true">/</span>
        </span>
      </nav>
      <div v-else class="topbar-title">{{ resolvedPageTitle }}</div>
    </div>

    <!-- Actions -->
    <div class="topbar-actions">
      <slot />

      <!-- Notifications -->
      <div class="topbar-menu-wrapper">
        <button
          class="topbar-icon-btn"
          :class="{ 'is-active': isNotificationsOpen }"
          @click="toggleNotificationsMenu"
          :aria-expanded="isNotificationsOpen"
          :aria-label="`Notifications — ${unreadCount} unread`"
        >
          <ui-icon name="bell" size="20" />
          <span v-if="unreadCount > 0" class="badge" aria-hidden="true">{{ unreadBadgeText }}</span>
        </button>

        <Transition name="dropdown">
          <div v-if="isNotificationsOpen" class="dropdown notifications-dropdown" role="dialog" aria-label="Notifications">
            <div class="dropdown-header">
              <span class="dropdown-title">Notifications</span>
              <button
                v-if="unreadCount > 0"
                class="mark-read-btn"
                @click="handleMarkAllRead"
              >
                Mark all read
              </button>
            </div>

            <div class="dropdown-body">
              <div v-if="notifications.length === 0" class="empty-state">
                <ui-icon name="bell-off" size="24" />
                <p>You're all caught up</p>
              </div>

              <button
                v-for="notif in notifications"
                :key="notif.id"
                class="notification-item"
                :class="{ 'is-unread': !notif.is_read }"
                @click="handleNotificationClick(notif)"
              >
                <span v-if="!notif.is_read" class="unread-dot" aria-label="Unread" />
                <span class="notif-content">
                  <span class="notif-text">{{ notif.message }}</span>
                  <span class="notif-time">{{ notif.created_at }}</span>
                </span>
              </button>
            </div>
          </div>
        </Transition>
      </div>

      <!-- User Menu -->
      <div class="topbar-menu-wrapper">
        <button
          class="topbar-icon-btn user-btn"
          :class="{ 'is-active': isUserMenuOpen }"
          @click="toggleUserMenu"
          :aria-expanded="isUserMenuOpen"
          :aria-label="`Account menu for ${userDisplayName}`"
        >
          <span class="user-avatar" aria-hidden="true">{{ userInitials }}</span>
        </button>

        <Transition name="dropdown">
          <div v-if="isUserMenuOpen" class="dropdown user-dropdown" role="dialog" :aria-label="`${userDisplayName} menu`">
            <div class="dropdown-header user-header">
              <span class="user-avatar user-avatar--lg" aria-hidden="true">{{ userInitials }}</span>
              <span class="user-info">
                <span class="user-display-name">{{ userDisplayName }}</span>
              </span>
            </div>

            <div class="dropdown-body">
              <router-link :to="settingsRoute" class="dropdown-item" @click="isUserMenuOpen = false">
                <ui-icon name="settings" size="18" />
                Settings
              </router-link>

              <button class="dropdown-item dropdown-item--danger" @click="handleLogout">
                <ui-icon name="log-out" size="18" />
                Sign out
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notificationsStore'
import UiIcon from '@/components/ui/UiIcon.vue'
import {
  fetchNotifications,
  fetchTopbarData,
  markAllNotificationsRead,
  markNotificationRead,
} from '@/services/topbarService'

const props = defineProps({
  pageTitle: { type: String, default: 'Dashboard' },
  apiEndpoint: { type: String, default: '' },
  pollIntervalMs: { type: Number, default: 30000 },
  sidebarCollapsed: { type: Boolean, default: false },
})

const emit = defineEmits(['toggle-sidebar', 'search-click', 'logout'])

const router = useRouter()
const route = useRoute()
const notificationsStore = useNotificationsStore()
const { items: notifications, unreadCount } = storeToRefs(notificationsStore)

// ── Refs ──────────────────────────────────────────────────────────────────────
const topbarRoot = ref(null)        // ✅ Fixed: now bound in template via ref="topbarRoot"
const isNotificationsOpen = ref(false)
const isUserMenuOpen = ref(false)
const userInitials = ref('U')
const userDisplayName = ref('User')
const settingsRoute = ref('/settings')
const resolvedPageTitle = ref('Dashboard')
let pollHandle = null

// ── Computed ──────────────────────────────────────────────────────────────────
const unreadBadgeText = computed(() => (unreadCount.value > 99 ? '99+' : String(unreadCount.value)))
const sidebarToggleLabel = computed(() => (props.sidebarCollapsed ? 'Open navigation menu' : 'Close navigation menu'))
const sidebarToggleIcon = computed(() => (props.sidebarCollapsed ? 'menu' : 'x'))

const breadcrumbs = computed(() => {
  const title = String(resolvedPageTitle.value || props.pageTitle || route.meta?.title || '').trim()
  if (!title || title.toLowerCase() === 'dashboard') return []
  return [
    { label: 'Dashboard', to: '/dashboard' },
    { label: title },
  ]
})

// ── Data fetching ─────────────────────────────────────────────────────────────
async function loadTopbar() {
  try {
    const payload = await fetchTopbarData({ pageTitle: props.pageTitle, apiEndpoint: props.apiEndpoint })
    resolvedPageTitle.value = payload?.page_title || props.pageTitle || 'Dashboard'
    notificationsStore.setNotifications(Array.isArray(payload?.notifications) ? payload.notifications : [])
    userInitials.value = payload?.user?.initials || 'U'
    userDisplayName.value = payload?.user?.display_name || 'User'
    settingsRoute.value = payload?.settings_url || '/settings'
  } catch {
    resolvedPageTitle.value = props.pageTitle || 'Dashboard'
    notificationsStore.setNotifications([])
  }
}

async function loadNotificationsOnly() {
  try {
    const payload = await fetchNotifications()
    notificationsStore.setNotifications(Array.isArray(payload?.notifications) ? payload.notifications : [])
  } catch { /* silent */ }
}

// ── Handlers ──────────────────────────────────────────────────────────────────
async function handleNotificationClick(notif) {
  if (!notif?.id || notif?.is_read) return
  try {
    await markNotificationRead(notif.id)
    notificationsStore.markAsRead(notif.id)
  } catch { /* silent */ }
}

async function handleMarkAllRead() {
  const unreadItems = notifications.value.filter((item) => !item?.is_read)
  if (!unreadItems.length) return

  try {
    await markAllNotificationsRead()
    notificationsStore.markAllAsRead()
    return
  } catch {
    // Fallback path: keep UX responsive even if bulk endpoint is unavailable.
    try {
      await Promise.all(
        unreadItems
          .map((item) => item?.id)
          .filter(Boolean)
          .map((id) => markNotificationRead(id))
      )
      notificationsStore.markAllAsRead()
    } catch {
      await loadNotificationsOnly()
    }
  }
}

function toggleNotificationsMenu() {
  isNotificationsOpen.value = !isNotificationsOpen.value
  if (isNotificationsOpen.value) {
    isUserMenuOpen.value = false
    loadNotificationsOnly()
  }
}

function toggleUserMenu() {
  isUserMenuOpen.value = !isUserMenuOpen.value
  if (isUserMenuOpen.value) isNotificationsOpen.value = false
}

// ✅ Fixed: topbarRoot is now properly bound so this handler works correctly
function handleOutsideClick(event) {
  if (topbarRoot.value && !topbarRoot.value.contains(event.target)) {
    isNotificationsOpen.value = false
    isUserMenuOpen.value = false
  }
}

function handleLogout() {
  emit('logout')
  ;['access_token', 'access', 'refresh_token', 'refresh', 'current_user'].forEach(k =>
    localStorage.removeItem(k)
  )
  router.push('/login')
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
watch(
  () => props.pageTitle,
  val => { resolvedPageTitle.value = val || 'Dashboard' },
  { immediate: true }
)

onMounted(async () => {
  await loadTopbar()
  document.addEventListener('click', handleOutsideClick)
  pollHandle = window.setInterval(loadNotificationsOnly, props.pollIntervalMs)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
  if (pollHandle) window.clearInterval(pollHandle)
})
</script>

<style scoped>
/* ════════════════════════════════════════════════════════════════════════════
   Topbar — Uses DTI Design System tokens
   ════════════════════════════════════════════════════════════════════════════ */

/* ── Layout ─────────────────────────────────────────────────────────────────── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  height: var(--topbar-height);
  padding: 0 var(--page-padding-x);
  background: var(--surface-base);
  border-bottom: 1px solid var(--border-subtle);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.topbar-primary {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
  flex: 1 1 auto;
}

.topbar-title {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  letter-spacing: var(--tracking-tight);
  min-width: 0;
  flex: 1 1 auto;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ── Breadcrumbs ────────────────────────────────────────────────────────────── */
.topbar-breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex-wrap: wrap;
  font-size: var(--text-sm);
  min-width: 0;
  flex: 1 1 auto;
}

.breadcrumb-segment {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.breadcrumb-link {
  color: var(--text-tertiary);
  text-decoration: none;
  transition: color var(--duration-fast) var(--ease-out);
}
.breadcrumb-link:hover {
  color: var(--text-primary);
}

.breadcrumb-sep {
  color: var(--border-strong);
  user-select: none;
}

.breadcrumb-current {
  font-weight: var(--weight-medium);
  color: var(--text-primary);
}

/* ── Actions row ────────────────────────────────────────────────────────────── */
.topbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
  flex-shrink: 0;
}

.topbar-menu-btn {
  flex-shrink: 0;
}

/* ── Icon buttons ───────────────────────────────────────────────────────────── */
.topbar-icon-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--radius-md);
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  color: var(--text-secondary);
  transition:
    background var(--duration-fast) var(--ease-out),
    color var(--duration-fast) var(--ease-out),
    border-color var(--duration-fast) var(--ease-out);
}

.topbar-icon-btn:hover,
.topbar-icon-btn.is-active {
  background: var(--surface-subtle);
  color: var(--text-primary);
  border-color: var(--border-default);
}

.topbar-icon-btn .icon {
  width: 1.125rem;
  height: 1.125rem;
}

/* ── Badge ──────────────────────────────────────────────────────────────────── */
.badge {
  position: absolute;
  top: calc(var(--space-1) * -1);
  right: calc(var(--space-1) * -1);
  background: var(--status-danger-bg);
  color: var(--status-danger-text);
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
  min-width: 1.1rem;
  height: 1.1rem;
  padding: 0 var(--space-1);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  box-shadow: 0 0 0 2px var(--surface-base);
}

/* ── Avatar ─────────────────────────────────────────────────────────────────── */
.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 1.875rem;
  height: 1.875rem;
  border-radius: var(--radius-full);
  background: var(--brand-navy-700);
  color: var(--text-inverse);
  font-weight: var(--weight-bold);
  font-size: var(--text-sm);
  letter-spacing: var(--tracking-wide);
}

.user-avatar--lg {
  width: 2.25rem;
  height: 2.25rem;
  font-size: var(--text-base);
}

/* ── Dropdown wrapper ───────────────────────────────────────────────────────── */
.topbar-menu-wrapper {
  position: relative;
}

/* ── Dropdown panel ─────────────────────────────────────────────────────────── */
.dropdown {
  position: absolute;
  top: calc(100% + var(--space-2));
  right: 0;
  background: var(--surface-base);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-dropdown);
  overflow: hidden;
}

.notifications-dropdown {
  width: 22rem;
  max-height: 26rem;
  display: flex;
  flex-direction: column;
}

.user-dropdown {
  width: 14rem;
}

/* ── Dropdown header ────────────────────────────────────────────────────────── */
.dropdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.dropdown-title {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  letter-spacing: var(--tracking-wider);
  text-transform: uppercase;
}

.user-header {
  gap: var(--space-3);
  justify-content: flex-start;
}

.user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-display-name {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── Mark all read button ───────────────────────────────────────────────────── */
.mark-read-btn {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  color: var(--brand-navy-700);
  transition: opacity var(--duration-fast) var(--ease-out);
  white-space: nowrap;
}
.mark-read-btn:hover { opacity: 0.75; }

/* ── Dropdown body ──────────────────────────────────────────────────────────── */
.dropdown-body {
  overflow-y: auto;
  flex: 1;
}

/* ── Empty state ────────────────────────────────────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-10) var(--space-4);
  color: var(--text-tertiary);
}

.empty-state svg {
  width: 2rem;
  height: 2rem;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: var(--text-base);
}

/* ── Notification items ─────────────────────────────────────────────────────── */
.notification-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: none;
  border-bottom: 1px solid var(--border-subtle);
  background: transparent;
  cursor: pointer;
  text-align: left;
  transition: background var(--duration-fast) var(--ease-out);
}

.notification-item:last-child { border-bottom: none; }

.notification-item:hover {
  background: var(--surface-subtle);
}

.notification-item.is-unread {
  background: rgba(46, 80, 128, 0.04);
}

.notification-item.is-unread:hover {
  background: rgba(46, 80, 128, 0.08);
}

@media (max-width: 640px) {
  .topbar {
    height: auto;
    min-height: var(--topbar-height);
    padding-top: var(--space-3);
    padding-bottom: var(--space-3);
    flex-wrap: wrap;
  }

  .topbar-primary,
  .topbar-actions {
    width: 100%;
  }

  .topbar-primary {
    gap: var(--space-2);
  }

  .topbar-actions {
    justify-content: space-between;
    gap: var(--space-2);
  }

  .notifications-dropdown {
    width: min(22rem, calc(100vw - var(--space-4) * 2));
  }

  .user-dropdown {
    width: min(16rem, calc(100vw - var(--space-4) * 2));
  }
}

@media (min-width: 641px) and (max-width: 1024px) {
  .notifications-dropdown {
    width: min(22rem, calc(100vw - var(--space-6) * 2));
  }
}

.unread-dot {
  flex-shrink: 0;
  width: 0.5rem;
  height: 0.5rem;
  margin-top: var(--space-1);
  border-radius: var(--radius-full);
  background: var(--brand-navy-600);
}

.notif-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 0;
}

.notif-text {
  font-size: var(--text-base);
  color: var(--text-primary);
  line-height: var(--leading-snug);
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notif-time {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

/* ── Dropdown items (user menu) ─────────────────────────────────────────────── */
.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-2) var(--space-4);
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: var(--text-base);
  color: var(--text-secondary);
  text-decoration: none;
  transition: background var(--duration-fast) var(--ease-out);
}

.dropdown-item svg {
  width: 1rem;
  height: 1rem;
  opacity: 0.6;
  flex-shrink: 0;
}

.dropdown-item:hover {
  background: var(--surface-subtle);
  color: var(--text-primary);
}

.dropdown-item--danger {
  color: var(--status-danger-text);
  border-top: 1px solid var(--border-subtle);
}

.dropdown-item--danger svg { opacity: 0.8; }

.dropdown-item--danger:hover {
  background: var(--status-danger-bg);
}

/* ── Dropdown animations ────────────────────────────────────────────────────── */
.dropdown-enter-active,
.dropdown-leave-active {
  transition:
    opacity var(--duration-fast) var(--ease-out),
    transform var(--duration-fast) var(--ease-out);
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(calc(var(--space-1) * -1.5)) scale(0.97);
}
</style>