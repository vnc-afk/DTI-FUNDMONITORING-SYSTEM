import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

function resolveApiBaseUrl() {
  const envBaseUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim()
  if (envBaseUrl) {
    return envBaseUrl.replace(/\/+$/, '')
  }

  const protocol = window.location.protocol || 'http:'
  const rawHost = String(window.location.hostname || '').trim()

  // `localhost` can resolve to IPv6 (::1) first on some systems.
  // Our dev servers are often bound to IPv4, so prefer 127.0.0.1.
const API_BASE_URL = import.meta.env.VITE_API_URL;

return API_BASE_URL;
}

const API_BASE_URL = resolveApiBaseUrl()
const PUBLIC_AUTH_ENDPOINTS = ['/api/user-app/auth/login/', '/api/user-app/auth/register/', '/api/user-app/auth/refresh/']
const TOKEN_EXPIRY_BUFFER_MS = 30 * 1000

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

let refreshPromise = null

function normalizeToken(value) {
  return String(value || '').trim()
}

function readStoredToken(primaryKey, legacyKey) {
  const primaryValue = normalizeToken(localStorage.getItem(primaryKey))
  if (primaryValue) {
    return primaryValue
  }

  return normalizeToken(localStorage.getItem(legacyKey))
}

function decodeJwtPayload(token = '') {
  const parts = String(token || '').split('.')
  if (parts.length < 2) {
    return null
  }

  const base64Url = parts[1].replace(/-/g, '+').replace(/_/g, '/')
  const padded = base64Url.padEnd(Math.ceil(base64Url.length / 4) * 4, '=')

  try {
    const decoded = typeof globalThis.atob === 'function'
      ? globalThis.atob(padded)
      : typeof Buffer !== 'undefined'
        ? Buffer.from(padded, 'base64').toString('binary')
        : ''
    return JSON.parse(decoded)
  } catch {
    return null
  }
}

function getTokenExpiryMs(token = '') {
  const payload = decodeJwtPayload(token)
  const expiry = Number(payload?.exp || 0)
  return Number.isFinite(expiry) && expiry > 0 ? expiry * 1000 : 0
}

function isTokenExpired(token = '', bufferMs = TOKEN_EXPIRY_BUFFER_MS) {
  const expiryMs = getTokenExpiryMs(token)
  if (!expiryMs) {
    return true
  }

  return Date.now() >= expiryMs - bufferMs
}

function getStoredUser() {
  try {
    const rawUser = localStorage.getItem('current_user')
    return rawUser ? JSON.parse(rawUser) : null
  } catch {
    return null
  }
}

function syncAuthStoreSession({ accessToken, refreshToken, user, hasUserProperty = false } = {}) {
  try {
    const authStore = useAuthStore()
    const resolvedUser = hasUserProperty ? user : authStore.user || getStoredUser()
    const resolvedAccessToken = accessToken !== undefined ? accessToken : authStore.token || readStoredToken('access_token', 'access')
    const resolvedRefreshToken = refreshToken !== undefined ? refreshToken : authStore.refreshToken || readStoredToken('refresh_token', 'refresh')

    authStore.setAuth({
      nextUser: resolvedUser ?? null,
      nextToken: resolvedAccessToken || '',
      nextRefreshToken: resolvedRefreshToken || '',
    })
  } catch {
    // Pinia may not be ready yet during app bootstrap.
  }
}

function clearStoredAuthSession() {
  ;['access_token', 'access', 'refresh_token', 'refresh', 'current_user'].forEach((key) => {
    localStorage.removeItem(key)
  })

  try {
    useAuthStore().clearAuth()
  } catch {
    // Ignore when Pinia has not been initialized yet.
  }
}

function getStoredSessionState() {
  const accessToken = readStoredToken('access_token', 'access')
  const refreshToken = readStoredToken('refresh_token', 'refresh')

  return {
    accessToken,
    refreshToken,
    accessExpired: isTokenExpired(accessToken),
    refreshExpired: isTokenExpired(refreshToken),
    canRefresh: Boolean(refreshToken) && !isTokenExpired(refreshToken),
    hasSession: Boolean((accessToken && !isTokenExpired(accessToken)) || (refreshToken && !isTokenExpired(refreshToken))),
  }
}

function isPublicAuthEndpoint(requestUrl = '') {
  return PUBLIC_AUTH_ENDPOINTS.some((endpoint) => String(requestUrl).includes(endpoint))
}

export function getAuthSessionState() {
  return getStoredSessionState()
}

export async function refreshAuthSession() {
  const session = getStoredSessionState()
  if (!session.canRefresh) {
    return null
  }

  if (!refreshPromise) {
    refreshPromise = refreshClient
      .post('/api/user-app/auth/refresh/', { refresh: session.refreshToken })
      .then((response) => {
        const nextToken = normalizeToken(response?.data?.access || '')
        if (!nextToken) {
          return null
        }

        storeAuthSession({
          access: nextToken,
          refresh: response?.data?.refresh || session.refreshToken,
        })

        return response.data
      })
      .catch(() => null)
      .finally(() => {
        refreshPromise = null
      })
  }

  return refreshPromise
}

apiClient.interceptors.request.use((config) => {
  const requestUrl = String(config?.url || '')
  if (!isPublicAuthEndpoint(requestUrl)) {
    const session = getStoredSessionState()

    if (session.accessToken && !session.accessExpired) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${session.accessToken}`
      return config
    }

    if (session.canRefresh) {
      return refreshAuthSession().then((response) => {
        const nextSession = getStoredSessionState()
        if (response?.access && nextSession.accessToken && !nextSession.accessExpired) {
          config.headers = config.headers || {}
          config.headers.Authorization = `Bearer ${nextSession.accessToken}`
          return config
        }

        clearStoredAuthSession()
        throw new Error('Authentication required.')
      })
    }

    clearStoredAuthSession()
    throw new Error('Authentication required.')
  }

  return config
})

export async function login(payload) {
  const response = await apiClient.post('/api/user-app/auth/login/', payload)
  return response.data
}

export async function fetchInitialPasswordContext() {
  const response = await apiClient.get('/api/user-app/auth/initial-password/')
  return response.data
}

export async function changeInitialPassword(payload) {
  const response = await apiClient.post('/api/user-app/auth/initial-password/', {
    new_password1: payload.new_password1 || '',
    new_password2: payload.new_password2 || '',
  })
  return response.data
}

export function storeAuthSession(data) {
  const access = normalizeToken(data?.access || '')
  const refresh = normalizeToken(data?.refresh || '')
  const hasUserProperty = Object.prototype.hasOwnProperty.call(data || {}, 'user')

  if (access) {
    localStorage.setItem('access_token', access)
    localStorage.setItem('access', access)
  }

  if (refresh) {
    localStorage.setItem('refresh_token', refresh)
    localStorage.setItem('refresh', refresh)
  }

  if (hasUserProperty) {
    if (data.user) {
      localStorage.setItem('current_user', JSON.stringify(data.user))
    } else {
      localStorage.removeItem('current_user')
    }
  }

  syncAuthStoreSession({
    accessToken: access || undefined,
    refreshToken: refresh || undefined,
    user: hasUserProperty ? data.user : undefined,
    hasUserProperty,
  })
}

export function hasAuthenticatedSession() {
  return getStoredSessionState().hasSession
}
