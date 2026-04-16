import { apiClient } from '@/services/http/clients'

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

