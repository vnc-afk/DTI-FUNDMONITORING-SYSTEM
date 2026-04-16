import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.protocol + '//' + window.location.hostname + ':8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function readCookie(name) {
  const cookieString = document.cookie || ''
  const parts = cookieString.split(';').map((item) => item.trim())
  const target = parts.find((item) => item.startsWith(`${name}=`))
  if (!target) return ''
  return decodeURIComponent(target.split('=').slice(1).join('='))
}

function buildAjaxHeaders(includeCsrf = false) {
  const headers = {
    'X-Requested-With': 'XMLHttpRequest',
  }
  if (includeCsrf) {
    const csrfToken = readCookie('csrftoken')
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken
    }
  }
  return headers
}

function getLocalUser() {
  try {
    return JSON.parse(localStorage.getItem('current_user') || '{}')
  } catch {
    return {}
  }
}

function computeInitials(profile, localUser) {
  const firstName = (profile?.first_name || localUser?.first_name || '').trim()
  const lastName = (profile?.last_name || localUser?.last_name || '').trim()
  const username = (profile?.username || localUser?.username || '').trim()

  if (firstName && lastName) {
    return `${firstName[0]}${lastName[0]}`.toUpperCase()
  }

  if (username) {
    return username[0].toUpperCase()
  }

  return 'U'
}

function computeDisplayName(profile, localUser) {
  const firstName = (profile?.first_name || localUser?.first_name || '').trim()
  const lastName = (profile?.last_name || localUser?.last_name || '').trim()
  const username = (profile?.username || localUser?.username || '').trim()

  if (firstName || lastName) {
    return `${firstName} ${lastName}`.trim()
  }

  return username || 'User'
}

export async function fetchNotifications() {
  const response = await apiClient.get('/api/notifications/', {
    headers: buildAjaxHeaders(),
  })
  return response.data
}

export async function markNotificationRead(notificationId) {
  const endpoints = [
    `/api/notifications/${notificationId}/read/`,
    `/api/user-app/notifications/${notificationId}/read/`,
  ]

  let lastError = null
  for (const endpoint of endpoints) {
    try {
      const response = await apiClient.post(endpoint, null, {
        headers: buildAjaxHeaders(true),
      })
      return response.data
    } catch (error) {
      const status = Number(error?.response?.status || 0)
      if (status !== 404 && status !== 405) {
        throw error
      }
      lastError = error
    }
  }

  throw lastError || new Error('Failed to mark notification as read')
}

export async function markAllNotificationsRead() {
  const endpoints = [
    '/api/notifications/read-all/',
    '/api/user-app/notifications/read-all/',
  ]

  let lastError = null
  for (const endpoint of endpoints) {
    try {
      const response = await apiClient.post(endpoint, null, {
        headers: buildAjaxHeaders(true),
      })
      return response.data
    } catch (error) {
      const status = Number(error?.response?.status || 0)
      if (status !== 404 && status !== 405) {
        throw error
      }
      lastError = error
    }
  }

  throw lastError || new Error('Failed to mark all notifications as read')
}

export async function fetchTopbarData({ pageTitle = 'Dashboard', apiEndpoint = '' } = {}) {
  const localUser = getLocalUser()

  const [profileResult, notificationsResult, topbarResult] = await Promise.allSettled([
    apiClient.get('/api/user-app/auth/profile/'),
    fetchNotifications(),
    apiEndpoint ? apiClient.get(apiEndpoint) : Promise.resolve({ data: null }),
  ])

  const profile = profileResult.status === 'fulfilled' ? profileResult.value.data : {}
  const notificationsPayload = notificationsResult.status === 'fulfilled' ? notificationsResult.value : {}
  const topbarPayload = topbarResult.status === 'fulfilled' ? topbarResult.value.data : null

  const notifications = Array.isArray(notificationsPayload?.notifications)
    ? notificationsPayload.notifications
    : []

  const unreadCount = Number(notificationsPayload?.unread_count || 0)

  return {
    page_title: topbarPayload?.page_title || pageTitle || 'Dashboard',
    notifications,
    unread_count: unreadCount,
    user: {
      initials: topbarPayload?.user?.initials || computeInitials(profile, localUser),
      display_name: topbarPayload?.user?.display_name || computeDisplayName(profile, localUser),
    },
    settings_url: topbarPayload?.settings_url || '/settings',
    logout_url: topbarPayload?.logout_url || '/logout/',
  }
}
