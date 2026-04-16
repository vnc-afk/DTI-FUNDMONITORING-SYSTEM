import { apiClient } from '@/services/http/clients'

function normalizeResults(data) {
  if (Array.isArray(data)) {
    return data
  }
  if (Array.isArray(data?.results)) {
    return data.results
  }
  return []
}

export async function fetchUserPreferences() {
  const response = await apiClient.get('/api/user-app/preferences/')
  return normalizeResults(response.data)
}

export async function createUserPreference(payload) {
  const response = await apiClient.post('/api/user-app/preferences/', payload)
  return response.data
}

export async function updateUserPreference(id, payload) {
  const response = await apiClient.patch(`/api/user-app/preferences/${id}/`, payload)
  return response.data
}

export async function fetchCurrentUserProfile() {
  const response = await apiClient.get('/api/user-app/auth/profile/')
  return response.data
}

export async function fetchUserAccountById(id) {
  const response = await apiClient.get(`/api/user-app/accounts/${id}/`)
  return response.data
}

function readCookie(name) {
  const cookieString = document.cookie || ''
  const parts = cookieString.split(';').map((item) => item.trim())
  const target = parts.find((item) => item.startsWith(`${name}=`))
  if (!target) {
    return ''
  }
  return decodeURIComponent(target.split('=').slice(1).join('='))
}

export async function changePassword(payload) {
  const csrfToken = readCookie('csrftoken')

  const formData = new FormData()
  formData.append('old_password', payload.old_password || '')
  formData.append('new_password1', payload.new_password1 || '')
  formData.append('new_password2', payload.new_password2 || '')

  const response = await apiClient.post('/api/change-password/', formData, {
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
    },
  })

  return response.data
}

