import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.protocol + '//' + window.location.hostname + ':8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function fetchImportFormConfig() {
  const response = await apiClient.get('/api/dashboard-app/import/form/')
  return response.data
}

export async function submitImportData(formData) {
  const response = await apiClient.post('/api/dashboard-app/import/submit/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export async function fetchImportResult() {
  const response = await apiClient.get('/api/dashboard-app/import/result/')
  return response.data
}
