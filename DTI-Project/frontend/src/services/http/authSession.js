import axios from 'axios'

import { API_BASE_URL } from '@/services/http/config'
import {
  clearStoredSession,
  getAccessToken,
  getRefreshToken,
  getStoredUser,
  storeTokens,
} from '@/services/http/tokenStorage'

const TOKEN_EXPIRY_BUFFER_MS = 30 * 1000
const PUBLIC_ENDPOINTS = new Set([
  '/api/user-app/auth/login/',
  '/api/user-app/auth/register/',
  '/api/user-app/auth/refresh/',
])

const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

let refreshPromise = null

function decodeJwtPayload(token = '') {
  const parts = String(token || '').split('.')
  if (parts.length < 2) {
    return null
  }

  const base64Url = parts[1].replace(/-/g, '+').replace(/_/g, '/')
  const padded = base64Url.padEnd(Math.ceil(base64Url.length / 4) * 4, '=')

  try {
    const decoded = globalThis.atob ? globalThis.atob(padded) : ''
    return JSON.parse(decoded)
  } catch {
    return null
  }
}

function getTokenExpiryMs(token = '') {
  const payload = decodeJwtPayload(token)
  const exp = Number(payload?.exp || 0)
  return Number.isFinite(exp) && exp > 0 ? exp * 1000 : 0
}

function isExpired(token = '', bufferMs = TOKEN_EXPIRY_BUFFER_MS) {
  const expiryMs = getTokenExpiryMs(token)
  if (!expiryMs) {
    return true
  }

  return Date.now() >= expiryMs - bufferMs
}

export function isPublicEndpoint(url = '') {
  const value = String(url || '')
  for (const endpoint of PUBLIC_ENDPOINTS) {
    if (value.includes(endpoint)) {
      return true
    }
  }
  return false
}

export function getAuthSessionState() {
  const accessToken = getAccessToken()
  const refreshToken = getRefreshToken()

  return {
    accessToken,
    refreshToken,
    accessExpired: isExpired(accessToken),
    refreshExpired: isExpired(refreshToken),
    canRefresh: Boolean(refreshToken) && !isExpired(refreshToken),
    hasSession: Boolean(
      (accessToken && !isExpired(accessToken)) ||
      (refreshToken && !isExpired(refreshToken))
    ),
    user: getStoredUser(),
  }
}

export function persistAuthSession(payload = {}) {
  const hasUser = Object.prototype.hasOwnProperty.call(payload || {}, 'user')
  storeTokens({
    access: payload?.access || '',
    refresh: payload?.refresh || '',
    user: payload?.user,
    hasUser,
  })
}

export function clearAuthSession() {
  clearStoredSession()
}

export async function refreshAuthSession() {
  const session = getAuthSessionState()
  if (!session.canRefresh) {
    return null
  }

  if (!refreshPromise) {
    refreshPromise = refreshClient
      .post('/api/user-app/auth/refresh/', { refresh: session.refreshToken })
      .then((response) => {
        const access = String(response?.data?.access || '').trim()
        if (!access) {
          clearAuthSession()
          return null
        }

        persistAuthSession({
          access,
          refresh: response?.data?.refresh || session.refreshToken,
          user: session.user,
        })

        return {
          access,
          refresh: response?.data?.refresh || session.refreshToken,
        }
      })
      .catch(() => {
        clearAuthSession()
        return null
      })
      .finally(() => {
        refreshPromise = null
      })
  }

  return refreshPromise
}

export function hasAuthenticatedSession() {
  return getAuthSessionState().hasSession
}
