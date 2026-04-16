import axios from 'axios'

import { getAuthSessionState, refreshAuthSession } from '@/services/authService'

function resolveApiBaseUrl() {
  const envBaseUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim()
  if (envBaseUrl) {
    return envBaseUrl.replace(/\/+$/, '')
  }

  const protocol = window.location.protocol || 'http:'
  const rawHost = String(window.location.hostname || '').trim()
  const API_BASE_URL = import.meta.env.VITE_API_URL;
  return API_BASE_URL;
}

const API_BASE_URL = resolveApiBaseUrl()

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(async (config) => {
  const session = getAuthSessionState()

  if (session.accessToken && !session.accessExpired) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${session.accessToken}`
    return config
  }

  if (session.canRefresh) {
    await refreshAuthSession()
    const refreshedSession = getAuthSessionState()

    if (refreshedSession.accessToken && !refreshedSession.accessExpired) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${refreshedSession.accessToken}`
    }
  }

  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = Number(error?.response?.status || 0)
    const originalRequest = error?.config || {}

    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        await refreshAuthSession()
      } catch {
        return Promise.reject(error)
      }

      const refreshedSession = getAuthSessionState()

      if (refreshedSession.accessToken && !refreshedSession.accessExpired) {
        originalRequest.headers = originalRequest.headers || {}
        originalRequest.headers.Authorization = `Bearer ${refreshedSession.accessToken}`
        return apiClient(originalRequest)
      }
    }

    if (status) {
      console.error('Archive API request failed:', {
        url: originalRequest.url,
        method: originalRequest.method,
        status,
        data: error?.response?.data,
      })
    }

    return Promise.reject(error)
  }
)

export async function fetchArchiveDashboard() {
  const response = await apiClient.get('/api/dashboard-app/archive/dashboard/')
  return response.data
}

export async function archiveYear(payload) {
  const response = await apiClient.post('/api/dashboard-app/archive/year/', payload)
  return response.data
}

export async function unarchiveYear(payload) {
  const response = await apiClient.post('/api/dashboard-app/archive/unarchive/', payload)
  return response.data
}

export async function fetchArchivedStatements(params = {}) {
  const response = await apiClient.get('/api/dashboard-app/archive/statements/', { params })
  return response.data
}

export async function restoreArchivedStatement(statementId) {
  const response = await apiClient.post(`/api/dashboard-app/archive/statements/${statementId}/restore/`)
  return response.data
}

export async function fetchArchivedTransactions(params = {}) {
  const response = await apiClient.get('/api/dashboard-app/archive/transactions/', { params })
  return response.data
}

export async function restoreArchivedTransaction(transactionId) {
  const response = await apiClient.post(`/api/dashboard-app/archive/transactions/${transactionId}/restore/`)
  return response.data
}
