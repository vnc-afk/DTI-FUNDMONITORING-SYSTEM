import axios from 'axios'

import { API_BASE_URL } from '@/services/http/config'
import {
  clearAuthSession,
  getAuthSessionState,
  isPublicEndpoint,
  refreshAuthSession,
} from '@/services/http/authSession'

function withAuthHeader(config, accessToken) {
  const nextConfig = config || {}
  nextConfig.headers = nextConfig.headers || {}
  nextConfig.headers.Authorization = `Bearer ${accessToken}`
  return nextConfig
}

function redirectToLogin() {
  if (window.location.pathname !== '/login') {
    window.location.assign('/login')
  }
}

async function resolveAccessToken() {
  const session = getAuthSessionState()
  if (session.accessToken && !session.accessExpired) {
    return session.accessToken
  }

  if (session.canRefresh) {
    const refreshed = await refreshAuthSession()
    if (refreshed?.access) {
      return refreshed.access
    }
  }

  return ''
}

export const publicClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(async (config) => {
  if (isPublicEndpoint(config?.url || '')) {
    return config
  }

  const accessToken = await resolveAccessToken()
  if (!accessToken) {
    clearAuthSession()
    redirectToLogin()
    throw new Error('Authentication required.')
  }

  return withAuthHeader(config, accessToken)
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = Number(error?.response?.status || 0)
    const requestUrl = String(error?.config?.url || '')
    const originalRequest = error?.config

    if (
      status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !isPublicEndpoint(requestUrl)
    ) {
      originalRequest._retry = true

      const refreshed = await refreshAuthSession()
      if (refreshed?.access) {
        return apiClient(withAuthHeader(originalRequest, refreshed.access))
      }

      clearAuthSession()
      redirectToLogin()
    }

    return Promise.reject(error)
  }
)
