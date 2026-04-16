import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export const useNotificationsStore = defineStore('notifications', () => {
  const items = ref([])
  const uiToasts = ref([])
  const apiLoadingCount = ref(0)

  const unreadCount = computed(() => items.value.filter((notification) => !notification.is_read).length)
  const isApiLoading = computed(() => apiLoadingCount.value > 0)

  function setNotifications(list = []) {
    items.value = Array.isArray(list) ? list : []
  }

  function upsertNotification(notification) {
    if (!notification || typeof notification !== 'object') return

    const index = items.value.findIndex((item) => item.id === notification.id)
    if (index >= 0) {
      items.value[index] = { ...items.value[index], ...notification }
      return
    }

    items.value.unshift(notification)
  }

  function markAsRead(notificationId) {
    items.value = items.value.map((item) => {
      if (item.id !== notificationId) return item
      return { ...item, is_read: true }
    })
  }

  function markAllAsRead() {
    items.value = items.value.map((item) => ({ ...item, is_read: true }))
  }

  function removeNotification(notificationId) {
    items.value = items.value.filter((item) => item.id !== notificationId)
  }

  function clearNotifications() {
    items.value = []
  }

  function beginApiCall() {
    apiLoadingCount.value += 1
  }

  function endApiCall() {
    apiLoadingCount.value = Math.max(0, apiLoadingCount.value - 1)
  }

  function pushToast(payload = {}) {
    const id = payload.id || `${Date.now()}-${Math.random().toString(16).slice(2)}`
    const toast = {
      id,
      title: payload.title || '',
      message: payload.message || '',
      variant: payload.variant || 'info',
      autoClose: payload.autoClose !== false,
      duration: Number(payload.duration || 3200),
      dismissible: payload.dismissible !== false,
    }

    uiToasts.value.push(toast)
    return id
  }

  function removeToast(id) {
    uiToasts.value = uiToasts.value.filter((toast) => toast.id !== id)
  }

  function clearToasts() {
    uiToasts.value = []
  }

  return {
    items,
    uiToasts,
    apiLoadingCount,
    unreadCount,
    isApiLoading,
    setNotifications,
    upsertNotification,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearNotifications,
    beginApiCall,
    endApiCall,
    pushToast,
    removeToast,
    clearToasts,
  }
})
