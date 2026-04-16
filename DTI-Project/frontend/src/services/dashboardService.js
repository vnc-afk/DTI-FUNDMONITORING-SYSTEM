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

export async function fetchDashboardKpis(params = {}) {
  const response = await apiClient.get('/api/dashboard/kpis/', { params })
  return response.data
}

export async function fetchDashboardCharts(params = {}) {
  const response = await apiClient.get('/api/dashboard/charts/', { params })
  return response.data
}

export async function fetchDashboardFilters() {
  const response = await apiClient.get('/api/dashboard/filters/')
  return response.data
}
