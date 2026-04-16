import { useAuthStore } from '@/stores/authStore'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'current_user'

function normalizeToken(value) {
  return String(value || '').trim()
}

function readToken(primaryKey, legacyKey) {
  const primary = normalizeToken(localStorage.getItem(primaryKey))
  if (primary) {
    return primary
  }

  return normalizeToken(localStorage.getItem(legacyKey))
}

function syncStore({ accessToken = undefined, refreshToken = undefined, user = undefined, hasUser = false } = {}) {
  try {
    const authStore = useAuthStore()
    authStore.setAuth({
      nextUser: hasUser ? user ?? null : authStore.user,
      nextToken: accessToken ?? authStore.token ?? '',
      nextRefreshToken: refreshToken ?? authStore.refreshToken ?? '',
    })
  } catch {
    // Pinia is not available during very early bootstrap.
  }
}

export function getAccessToken() {
  return readToken(ACCESS_TOKEN_KEY, 'access')
}

export function getRefreshToken() {
  return readToken(REFRESH_TOKEN_KEY, 'refresh')
}

export function getStoredUser() {
  try {
    const rawUser = localStorage.getItem(USER_KEY)
    return rawUser ? JSON.parse(rawUser) : null
  } catch {
    return null
  }
}

export function storeTokens({ access = '', refresh = '', user, hasUser = false } = {}) {
  const accessToken = normalizeToken(access)
  const refreshToken = normalizeToken(refresh)

  if (accessToken) {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    localStorage.setItem('access', accessToken)
  }

  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
    localStorage.setItem('refresh', refreshToken)
  }

  if (hasUser) {
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    } else {
      localStorage.removeItem(USER_KEY)
    }
  }

  syncStore({ accessToken: accessToken || undefined, refreshToken: refreshToken || undefined, user, hasUser })
}

export function clearStoredSession() {
  ;['access_token', 'access', 'refresh_token', 'refresh', 'current_user'].forEach((key) => {
    localStorage.removeItem(key)
  })

  try {
    useAuthStore().clearAuth()
  } catch {
    // Pinia is not available during very early bootstrap.
  }
}
