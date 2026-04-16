import { apiClient } from '@/services/http/clients'

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

