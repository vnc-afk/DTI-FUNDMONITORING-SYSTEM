import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.protocol + '//' + window.location.hostname + ':8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function normalizeResults(data) {
  if (Array.isArray(data)) {
    return data
  }
  if (Array.isArray(data?.results)) {
    return data.results
  }
  return []
}

export async function fetchAllUserAccounts() {
  const allAccounts = []
  let page = 1

  while (true) {
    const response = await apiClient.get('/api/user-app/accounts/', {
      params: { page },
    })

    const currentBatch = normalizeResults(response.data)
    allAccounts.push(...currentBatch)

    if (!Array.isArray(response.data?.results)) {
      break
    }

    if (!response.data.next) {
      break
    }

    page += 1
  }

  return allAccounts
}

export async function fetchUserAccountById(id) {
  const response = await apiClient.get(`/api/user-app/accounts/${id}/`)
  return response.data
}

export async function createUserAccount(payload) {
  const response = await apiClient.post('/api/user-app/accounts/', payload)
  return response.data
}

export async function fetchCurrentUserProfile() {
  const response = await apiClient.get('/api/user-app/auth/profile/')
  return response.data
}

export async function updateUserAccount(id, payload) {
  const response = await apiClient.patch(`/api/user-app/accounts/${id}/`, payload)
  return response.data
}

export async function deleteUserAccount(id) {
  await apiClient.delete(`/api/user-app/accounts/${id}/`)
}

export async function resetUserAccountPassword(id) {
  const response = await apiClient.post(`/api/user-app/accounts/${id}/reset-password/`)
  return response.data
}

export async function bulkDeleteUserAccounts(ids) {
  await Promise.all(ids.map((id) => deleteUserAccount(id)))
}
