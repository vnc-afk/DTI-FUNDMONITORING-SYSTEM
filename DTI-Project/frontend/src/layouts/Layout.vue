<template>
  <div class="app-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <div
      v-if="showSidebarBackdrop"
      class="sidebar-backdrop"
      aria-hidden="true"
      @click="closeSidebar"
    />

    <UiSidebar
      :is-collapsed="sidebarCollapsed"
      :user-name="authStore.user?.name || 'Admin User'"
      :user-role="authStore.user?.role || 'Administrator'"
      @close="closeSidebar"
      @navigate="handleSidebarNavigate"
      @profile-click="showProfileMenu = true"
    />

    <UiTopbar
      :sidebar-collapsed="sidebarCollapsed"
      :notification-count="notificationCount"
      @toggle-sidebar="toggleSidebar"
      @notifications="showNotifications = true"
    />

    <main class="main-content">
      <router-view v-slot="{ Component, route }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" :key="route.fullPath" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import UiSidebar from '@/components/ui/UiSidebar.vue'
import UiTopbar from '@/components/ui/UiTopbar.vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const route = useRoute()
const isCompactViewport = ref(typeof window !== 'undefined' ? window.innerWidth <= 1024 : true)
const sidebarCollapsed = ref(isCompactViewport.value)
const notificationCount = ref(0)
const showNotifications = ref(false)
const showProfileMenu = ref(false)

const showSidebarBackdrop = computed(() => isCompactViewport.value && !sidebarCollapsed.value)

function syncViewportState() {
  if (typeof window === 'undefined') return
  isCompactViewport.value = window.innerWidth <= 1024
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function closeSidebar() {
  sidebarCollapsed.value = true
}

function handleSidebarNavigate() {
  if (isCompactViewport.value) {
    closeSidebar()
  }
}

watch(isCompactViewport, (isCompact) => {
  sidebarCollapsed.value = isCompact
}, { immediate: true })

watch(() => route.fullPath, () => {
  if (isCompactViewport.value) {
    closeSidebar()
  }
})

watch(
  [isCompactViewport, sidebarCollapsed],
  ([isCompact, isCollapsed]) => {
    if (typeof document === 'undefined') return
    document.body.style.overflow = isCompact && !isCollapsed ? 'hidden' : ''
  },
  { immediate: true }
)

onMounted(() => {
  if (typeof window === 'undefined') return
  window.addEventListener('resize', syncViewportState, { passive: true })
})

onBeforeUnmount(() => {
  if (typeof window === 'undefined') return
  window.removeEventListener('resize', syncViewportState)
  document.body.style.overflow = ''
})
</script>

<style>
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 150ms var(--ease-out), transform 150ms var(--ease-out);
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>