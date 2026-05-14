<template>
  <div class="app-feedback-shell">
    <div class="api-loading-indicator" :class="{ 'is-active': notificationsStore.isApiLoading }" aria-hidden="true"></div>

    <div class="toast-stack" aria-live="polite" aria-atomic="true">
      <UiToast
        v-for="toast in notificationsStore.uiToasts"
        :key="toast.id"
        :model-value="true"
        :title="toast.title"
        :message="toast.message"
        :variant="toast.variant"
        :auto-close="toast.autoClose"
        :duration="toast.duration"
        :dismissible="toast.dismissible"
        @close="notificationsStore.removeToast(toast.id)"
      />
    </div>

    <router-view v-slot="{ Component, route }">
      <Transition name="page-fade" mode="out-in" appear>
        <component :is="Component" :key="route.matched?.[0]?.path || route.path" />
      </Transition>
    </router-view>

    <ChatBot v-if="routeName !== 'login' && routePath !== '/login'" />
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, watch, computed } from 'vue'

import ChatBot from '@/components/ui/ChatbotWidget.vue'
import UiToast from '@/components/ui/UiToast.vue'
import { useAuthStore } from '@/stores/authStore'
import { useRoute } from 'vue-router'
import { getAuthSessionState, clearAuthSession } from '@/services/http/authSession'
import { useNotificationsStore } from '@/stores/notificationsStore'
import { useSharedStore } from '@/stores/sharedStore'
import realtimeService from '@/services/realtimeService'

const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()
const sharedStore = useSharedStore()

const route = useRoute()
const routeName = computed(() => route.name)
const routePath = computed(() => route.path)

let unsubscribeRealtime = null
let unsubscribeConnection = null

function handleRealtimeEvent(event) {
  const eventType = event?.type
  const payload = event?.payload || {}

  if (eventType === 'notification.new' || eventType === 'notification.updated') {
    notificationsStore.upsertNotification(payload)
    return
  }

  if (eventType === 'live.update') {
    sharedStore.setShared('latestLiveUpdate', payload)
    return
  }

  if (eventType === 'connection.ready') {
    sharedStore.setShared('realtimeUserGroups', payload?.groups || [])
  }
}

function connectRealtime(token) {
  if (!token) {
    realtimeService.disconnect()
    sharedStore.setShared('realtimeStatus', 'disconnected')
    return
  }

  realtimeService.connect(token)
}

onMounted(() => {

  authStore.initializeFromStorage()

  // Check for expired token and force logout if needed
  const session = getAuthSessionState()
  if (session.accessExpired) {
    clearAuthSession()
    authStore.clearAuth()
    // Redirect to login if not already there
    if (window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
    return
  }

  unsubscribeRealtime = realtimeService.subscribe(handleRealtimeEvent)
  unsubscribeConnection = realtimeService.onConnectionChange(({ status }) => {
    sharedStore.setShared('realtimeStatus', status || 'unknown')
  })

  connectRealtime(authStore.token)
})

watch(
  () => authStore.token,
  (token) => {
    connectRealtime(token)
  }
)

onBeforeUnmount(() => {
  if (unsubscribeRealtime) {
    unsubscribeRealtime()
  }
  if (unsubscribeConnection) {
    unsubscribeConnection()
  }
  realtimeService.disconnect()
})
</script>

<style scoped>
.app-feedback-shell {
  min-height: 100%;
}

.api-loading-indicator {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  z-index: 1200;
  background: linear-gradient(90deg, var(--accent), var(--primary-light));
  transform-origin: left;
  transform: scaleX(0);
  opacity: 0;
  transition: transform var(--transition-fast), opacity var(--transition-fast);
}

.api-loading-indicator.is-active {
  opacity: 1;
  transform: scaleX(1);
}

.toast-stack {
  position: fixed;
  top: calc(var(--space-lg) + 2px);
  right: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  z-index: 1150;
  pointer-events: none;
}

.toast-stack :deep(.ui-toast) {
  pointer-events: auto;
}
</style>
