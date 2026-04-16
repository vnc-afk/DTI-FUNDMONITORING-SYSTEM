import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'current_user'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref('')
  const refreshToken = ref('')

  const isAuthenticated = computed(() => Boolean(token.value))
  const displayName = computed(() => {
    const current = user.value || {}
    const fullName = String(current.full_name || '').trim()
    if (fullName) return fullName
    return String(current.username || '')
  })

  function initializeFromStorage() {
    const savedToken = localStorage.getItem(ACCESS_TOKEN_KEY) || localStorage.getItem('access') || ''
    const savedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY) || localStorage.getItem('refresh') || ''

    token.value = savedToken
    refreshToken.value = savedRefreshToken

    try {
      const rawUser = localStorage.getItem(USER_KEY)
      user.value = rawUser ? JSON.parse(rawUser) : null
    } catch {
      user.value = null
    }
  }

  function setAuth({ nextUser = null, nextToken = '', nextRefreshToken = '' } = {}) {
    user.value = nextUser
    token.value = nextToken
    refreshToken.value = nextRefreshToken

    if (nextToken) {
      localStorage.setItem(ACCESS_TOKEN_KEY, nextToken)
      localStorage.setItem('access', nextToken)
    } else {
      localStorage.removeItem(ACCESS_TOKEN_KEY)
      localStorage.removeItem('access')
    }

    if (nextRefreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, nextRefreshToken)
      localStorage.setItem('refresh', nextRefreshToken)
    } else {
      localStorage.removeItem(REFRESH_TOKEN_KEY)
      localStorage.removeItem('refresh')
    }

    if (nextUser) {
      localStorage.setItem(USER_KEY, JSON.stringify(nextUser))
    } else {
      localStorage.removeItem(USER_KEY)
    }
  }

  function updateUser(patch = {}) {
    const mergedUser = { ...(user.value || {}), ...(patch || {}) }
    user.value = mergedUser
    localStorage.setItem(USER_KEY, JSON.stringify(mergedUser))
  }

  function clearAuth() {
    setAuth({ nextUser: null, nextToken: '', nextRefreshToken: '' })
  }

  return {
    user,
    token,
    refreshToken,
    isAuthenticated,
    displayName,
    initializeFromStorage,
    setAuth,
    updateUser,
    clearAuth,
  }
})
