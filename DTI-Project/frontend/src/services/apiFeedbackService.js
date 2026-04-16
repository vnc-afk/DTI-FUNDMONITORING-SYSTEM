import router from '@/router'
import { apiClient, publicClient } from '@/services/http/clients'
import { clearAuthSession } from '@/services/http/authSession'
import { useNotificationsStore } from '@/stores/notificationsStore'

const MUTATING_METHODS = new Set(['post', 'put', 'patch', 'delete'])
const AUTH_ENDPOINTS = ['/api/user-app/auth/login/', '/api/user-app/auth/register/', '/api/user-app/auth/refresh/']

let initialized = false

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

function isAuthEndpoint(url = '') {
  return AUTH_ENDPOINTS.some((endpoint) => String(url).includes(endpoint))
}

function redirectToLogin() {
  if (window.location.pathname !== '/login') {
    router.replace('/login').catch(() => {})
  }
}

function attachFeedbackInterceptors(client, notificationsStore) {
  client.interceptors.request.use(
    (config) => {
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
      if (MUTATING_METHODS.has(method) && !isAuthEndpoint(response?.config?.url || '')) {
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
    (error) => {
      notificationsStore.endApiCall()

      const status = Number(error?.response?.status || 0)
      const requestUrl = String(error?.config?.url || '')

      if (status === 401 && !isAuthEndpoint(requestUrl)) {
        clearAuthSession()
        redirectToLogin()
        return Promise.reject(error)
      }

      if (status !== 401) {
        notificationsStore.pushToast({
          title: 'Request Error',
          message: extractErrorMessage(error),
          variant: 'danger',
          autoClose: false,
        })
      }

      return Promise.reject(error)
    }
  )
}

export function setupGlobalApiFeedback(pinia) {
  if (initialized) {
    return
  }

  initialized = true
  const notificationsStore = useNotificationsStore(pinia)

  attachFeedbackInterceptors(apiClient, notificationsStore)
  attachFeedbackInterceptors(publicClient, notificationsStore)

  const nativeFetch = window.fetch.bind(window)
  window.fetch = async (...args) => {
    notificationsStore.beginApiCall()
    try {
      const response = await nativeFetch(...args)

      if (!response.ok && response.status !== 401) {
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
