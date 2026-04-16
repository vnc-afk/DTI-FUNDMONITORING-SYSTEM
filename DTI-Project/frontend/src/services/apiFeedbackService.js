import axios from 'axios'

import router from '@/router'
import { getAuthSessionState, refreshAuthSession } from '@/services/authService'
import { useAuthStore } from '@/stores/authStore'
import { useNotificationsStore } from '@/stores/notificationsStore'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.protocol + '//' + window.location.hostname + ':8000'
const MUTATING_METHODS = new Set(['post', 'put', 'patch', 'delete'])
const AUTH_ENDPOINTS = ['/api/user-app/auth/login/', '/api/user-app/auth/register/', '/api/user-app/auth/refresh/']

function normalizeMessage(value, fallback) {
  const text = String(value || '').trim()
  return text || fallback
}

function extractErrorMessage(error) {
  const payload = error?.response?.data || {}

  if (typeof payload?.detail === 'string') {
    return payload.detail
  }

  if (typeof payload?.message === 'string') {
    return payload.message
  }

  if (typeof error?.message === 'string') {
    return error.message
  }

  return 'Request failed. Please try again.'
}

export function setupGlobalApiFeedback(pinia) {
  const notificationsStore = useNotificationsStore(pinia)
  const authStore = useAuthStore(pinia)
  const originalCreate = axios.create.bind(axios)

  function isAuthEndpoint(url = '') {
    return AUTH_ENDPOINTS.some((endpoint) => String(url).includes(endpoint))
  }

  function redirectToLogin() {
    if (window.location.pathname !== '/login') {
      router.replace('/login').catch(() => {})
    }
  }

  function attachInterceptors(client) {
    client.interceptors.request.use(
      async (config) => {
        const requestUrl = String(config?.url || '')

        if (!isAuthEndpoint(requestUrl)) {
          const session = getAuthSessionState()

          if (session.accessToken && !session.accessExpired) {
            config.headers = config.headers || {}
            config.headers.Authorization = `Bearer ${session.accessToken}`
          } else if (session.canRefresh) {
            const refreshed = await refreshAuthSession()
            const refreshedSession = getAuthSessionState()

            if (refreshed?.access && refreshedSession.accessToken && !refreshedSession.accessExpired) {
              config.headers = config.headers || {}
              config.headers.Authorization = `Bearer ${refreshedSession.accessToken}`
            } else {
              authStore.clearAuth()
              redirectToLogin()
              return Promise.reject(new Error('Authentication required.'))
            }
          } else {
            authStore.clearAuth()
            redirectToLogin()
            return Promise.reject(new Error('Authentication required.'))
          }
        }

        notificationsStore.beginApiCall()
        return config
      },
      (error) => {
        notificationsStore.endApiCall()
        return Promise.reject(error)
      }
    )

    client.interceptors.response.use(
      (response) => {
        notificationsStore.endApiCall()

        const method = String(response?.config?.method || 'get').toLowerCase()
        if (MUTATING_METHODS.has(method)) {
          notificationsStore.pushToast({
            title: 'Success',
            message: normalizeMessage(response?.data?.message, 'Changes saved successfully.'),
            variant: 'success',
            autoClose: true,
            duration: 2400,
          })
        }

        return response
      },
      async (error) => {
        notificationsStore.endApiCall()

        const status = Number(error?.response?.status || 0)
        const requestUrl = String(error?.config?.url || '')

        if (status === 401 && !isAuthEndpoint(requestUrl)) {
          const originalRequest = error?.config || {}

          if (!originalRequest._retry) {
            originalRequest._retry = true
            const refreshed = await refreshAuthSession()

            if (refreshed?.access) {
              return client(originalRequest)
            }
          }

          authStore.clearAuth()
          redirectToLogin()
          return Promise.reject(error)
        }

        if (status === 401 && isAuthEndpoint(requestUrl)) {
          return Promise.reject(error)
        }

        notificationsStore.pushToast({
          title: 'Request Error',
          message: extractErrorMessage(error),
          variant: 'danger',
          autoClose: false,
        })
        return Promise.reject(error)
      }
    )

    return client
  }

  axios.create = (...args) => attachInterceptors(originalCreate(...args))

  const nativeFetch = window.fetch.bind(window)
  window.fetch = async (...args) => {
    notificationsStore.beginApiCall()
    try {
      const response = await nativeFetch(...args)

      if (!response.ok) {
        if (response.status === 401) {
          return response
        }

        notificationsStore.pushToast({
          title: 'Request Error',
          message: `Request failed (${response.status}).`,
          variant: 'danger',
          autoClose: false,
        })
      }

      return response
    } catch (error) {
      notificationsStore.pushToast({
        title: 'Network Error',
        message: normalizeMessage(error?.message, 'Unable to reach server.'),
        variant: 'danger',
        autoClose: false,
      })
      throw error
    } finally {
      notificationsStore.endApiCall()
    }
  }
}
