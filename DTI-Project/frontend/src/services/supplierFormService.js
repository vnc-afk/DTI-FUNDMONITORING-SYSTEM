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

export async function fetchSupplierById(id) {
  const response = await apiClient.get(`/api/data-management-app/suppliers/${id}/`)
  return response.data
}

export async function createSupplier(payload) {
  const response = await apiClient.post('/api/data-management-app/suppliers/', payload)
  return response.data
}

export async function updateSupplier(id, payload) {
  const response = await apiClient.put(`/api/data-management-app/suppliers/${id}/`, payload)
  return response.data
}