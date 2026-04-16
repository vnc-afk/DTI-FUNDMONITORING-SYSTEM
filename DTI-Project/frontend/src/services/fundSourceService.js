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

function normalizePaginatedResponse(data, requestedPage = 1) {
  if (Array.isArray(data)) {
    return {
      funds: data,
      pagination: {
        page: requestedPage,
        pages: 1,
        has_next: false,
        has_previous: false,
        count: data.length,
        page_size: data.length,
      },
    }
  }

  if (Array.isArray(data?.results)) {
    const count = Number(data.count || data.results.length)
    const pageSize = Math.max(Number(data.page_size || data.results.length || 1), 1)
    const currentPage = Math.max(Number(data.page || requestedPage), 1)
    const pages = Math.max(Number(data.pages || Math.ceil(count / pageSize) || 1), 1)

    return {
      funds: data.results,
      pagination: {
        page: currentPage,
        pages,
        has_next: data.has_next ?? Boolean(data.next),
        has_previous: data.has_previous ?? Boolean(data.previous),
        count,
        page_size: pageSize,
      },
    }
  }

  return {
    funds: [],
    pagination: {
      page: requestedPage,
      pages: 1,
      has_next: false,
      has_previous: false,
      count: 0,
      page_size: 20,
    },
  }
}

export async function fetchFundSources({ page = 1 } = {}) {
  const response = await apiClient.get('/api/data-management-app/fund-sources/', {
    params: { page },
  })
  return normalizePaginatedResponse(response.data, page)
}

export async function fetchFundSourceById(id) {
  const response = await apiClient.get(`/api/data-management-app/fund-sources/${id}/`)
  return response.data
}

export async function createFundSource(payload) {
  const response = await apiClient.post('/api/data-management-app/fund-sources/', payload)
  return response.data
}

export async function updateFundSource(id, payload) {
  const response = await apiClient.put(`/api/data-management-app/fund-sources/${id}/`, payload)
  return response.data
}

export async function deleteFundSource(id) {
  await apiClient.delete(`/api/data-management-app/fund-sources/${id}/`)
}

export async function bulkDeleteFundSources(ids) {
  await Promise.all(ids.map((id) => deleteFundSource(id)))
}

function normalizeResults(data) {
  if (Array.isArray(data)) {
    return data
  }
  if (Array.isArray(data?.results)) {
    return data.results
  }
  return []
}

export async function fetchBreakdownCategories() {
  const response = await apiClient.get('/api/data-management-app/breakdown-categories/')
  return normalizeResults(response.data)
}

export async function fetchFundSourceBreakdowns(fundSourceId) {
  const response = await apiClient.get('/api/data-management-app/fund-source-breakdowns/')
  const items = normalizeResults(response.data)
  return items.filter((item) => Number(item.fund_source) === Number(fundSourceId))
}

export async function fetchFundSourceBreakdownById(id) {
  const response = await apiClient.get(`/api/data-management-app/fund-source-breakdowns/${id}/`)
  return response.data
}

export async function createFundSourceBreakdown(payload) {
  const response = await apiClient.post('/api/data-management-app/fund-source-breakdowns/', payload)
  return response.data
}

export async function updateFundSourceBreakdown(id, payload) {
  const response = await apiClient.put(`/api/data-management-app/fund-source-breakdowns/${id}/`, payload)
  return response.data
}

export async function deleteFundSourceBreakdown(id) {
  await apiClient.delete(`/api/data-management-app/fund-source-breakdowns/${id}/`)
}