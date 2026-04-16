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
  const categories = normalizeResults(data)

  if (Array.isArray(data?.results)) {
    const count = Number(data.count || categories.length)
    const pageSize = Math.max(Number(data.page_size || data.results.length || 1), 1)
    const currentPage = Math.max(Number(data.page || requestedPage), 1)
    const pages = Math.max(Number(data.pages || Math.ceil(count / pageSize) || 1), 1)

    return {
      categories,
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
    categories,
    pagination: {
      page: requestedPage,
      pages: 1,
      has_next: false,
      has_previous: false,
      count: categories.length,
      page_size: categories.length,
    },
  }
}

export async function fetchExpenseCategories({ page = 1 } = {}) {
  const response = await apiClient.get('/api/data-management-app/expense-categories/', {
    params: { page },
  })
  return normalizePaginatedResponse(response.data, page)
}

export async function fetchExpenseCategoryById(id) {
  const response = await apiClient.get(`/api/data-management-app/expense-categories/${id}/`)
  return response.data
}

export async function createExpenseCategory(payload) {
  const response = await apiClient.post('/api/data-management-app/expense-categories/', payload)
  return response.data
}

export async function updateExpenseCategory(id, payload) {
  const response = await apiClient.put(`/api/data-management-app/expense-categories/${id}/`, payload)
  return response.data
}

export async function deleteExpenseCategory(id) {
  await apiClient.delete(`/api/data-management-app/expense-categories/${id}/`)
}

export async function bulkDeleteExpenseCategories(ids) {
  await Promise.all(ids.map((id) => deleteExpenseCategory(id)))
}
