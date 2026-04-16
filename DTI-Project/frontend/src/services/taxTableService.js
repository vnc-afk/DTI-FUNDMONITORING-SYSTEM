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

function normalizeResults(data) {
  if (Array.isArray(data)) {
    return data
  }
  if (Array.isArray(data?.results)) {
    return data.results
  }
  return []
}

function normalizePaginatedResponse(data, requestedPage = 1) {
  const entries = normalizeResults(data)

  if (Array.isArray(data?.results)) {
    const count = Number(data.count || entries.length)
    const pageSize = Math.max(Number(data.page_size || data.results.length || 1), 1)
    const currentPage = Math.max(Number(data.page || requestedPage), 1)
    const pages = Math.max(Number(data.pages || Math.ceil(count / pageSize) || 1), 1)

    return {
      entries,
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
    entries,
    pagination: {
      page: 1,
      pages: 1,
      has_next: false,
      has_previous: false,
      count: entries.length,
      page_size: entries.length,
    },
  }
}

export async function fetchTaxTableEntries({ page = 1 } = {}) {
  const response = await apiClient.get('/api/data-management-app/tax-table/', {
    params: { page },
  })
  return normalizePaginatedResponse(response.data, page)
}

export async function fetchTaxTableEntryById(id) {
  const response = await apiClient.get(`/api/data-management-app/tax-table/${id}/`)
  return response.data
}

export async function createTaxTableEntry(payload) {
  const response = await apiClient.post('/api/data-management-app/tax-table/', payload)
  return response.data
}

export async function updateTaxTableEntry(id, payload) {
  const response = await apiClient.put(`/api/data-management-app/tax-table/${id}/`, payload)
  return response.data
}

export async function fetchPurchaseTypes() {
  const response = await apiClient.get('/api/data-management-app/purchase-types/')
  return normalizeResults(response.data)
}

export async function deleteTaxTableEntry(id) {
  await apiClient.delete(`/api/data-management-app/tax-table/${id}/`)
}