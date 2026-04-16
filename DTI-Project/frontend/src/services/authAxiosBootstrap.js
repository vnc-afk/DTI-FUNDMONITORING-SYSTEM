import axios from 'axios'

import { getAuthSessionState, refreshAuthSession } from '@/services/authService'
import { useAuthStore } from '@/stores/authStore'

const PUBLIC_AUTH_ENDPOINTS = ['/api/user-app/auth/login/', '/api/user-app/auth/register/', '/api/user-app/auth/refresh/']
const AUTH_STORAGE_KEYS = ['access_token', 'access', 'refresh_token', 'refresh', 'current_user']

let isInstalled = false

function isPublicAuthEndpoint(requestUrl = '') {
  return PUBLIC_AUTH_ENDPOINTS.some((endpoint) => String(requestUrl).includes(endpoint))
}

function clearStoredAuthSession() {
  AUTH_STORAGE_KEYS.forEach((key) => {
    localStorage.removeItem(key)
  })

  try {
    useAuthStore().clearAuth()
  } catch {
    // Pinia may not be initialized yet during bootstrap.
  }
}

function attachAuthInterceptors(client) {
  client.interceptors.request.use(async (config) => {
    const requestUrl = String(config?.url || '')

    if (isPublicAuthEndpoint(requestUrl)) {
      return config
    }

    const session = getAuthSessionState()

    if (session.accessToken && !session.accessExpired) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${session.accessToken}`
      return config
    }

    if (session.canRefresh) {
      const refreshed = await refreshAuthSession()
      const refreshedSession = getAuthSessionState()

      if (refreshed?.access && refreshedSession.accessToken && !refreshedSession.accessExpired) {
        config.headers = config.headers || {}
        config.headers.Authorization = `Bearer ${refreshedSession.accessToken}`
        return config
      }
    }

    clearStoredAuthSession()
    return Promise.reject(new Error('Authentication required.'))
  })

  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const status = Number(error?.response?.status || 0)
      const requestUrl = String(error?.config?.url || '')
      const originalRequest = error?.config || {}

      if (status === 401 && !isPublicAuthEndpoint(requestUrl) && !originalRequest._retry) {
        originalRequest._retry = true

        try {
          const refreshed = await refreshAuthSession()
          const refreshedSession = getAuthSessionState()

          if (refreshed?.access && refreshedSession.accessToken && !refreshedSession.accessExpired) {
            originalRequest.headers = originalRequest.headers || {}
            originalRequest.headers.Authorization = `Bearer ${refreshedSession.accessToken}`
            return client(originalRequest)
          }
        } catch {
          // Fall through to clearing session state below.
        }

        clearStoredAuthSession()
      }

      return Promise.reject(error)
    }
  )

  return client
}

function installAuthAxiosBootstrap() {
  if (isInstalled) {
    return
  }

  isInstalled = true
  const originalCreate = axios.create.bind(axios)

  axios.create = (...args) => attachAuthInterceptors(originalCreate(...args))
}

installAuthAxiosBootstrap()