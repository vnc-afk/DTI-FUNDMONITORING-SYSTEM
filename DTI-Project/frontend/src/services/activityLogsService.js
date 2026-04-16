import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

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

export async function fetchActivityLogs(params = {}) {
  const response = await apiClient.get('/api/dashboard-app/activity-logs/', { params })
  return response.data
}

export async function fetchActivityLogFilters(params = {}) {
  const response = await apiClient.get('/api/dashboard-app/activity-logs/filters/', { params })
  return response.data
}

export async function fetchActivitySummary() {
  const response = await apiClient.get('/api/dashboard-app/activity-logs/summary/')
  return response.data
}

export async function fetchUserActivityLogs(userId, params = {}) {
  const response = await apiClient.get(`/api/dashboard-app/activity-logs/user/${userId}/`, { params })
  return response.data
}
