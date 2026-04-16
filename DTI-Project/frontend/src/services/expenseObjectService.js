import { apiClient } from '@/services/http/clients'

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
  const objects = normalizeResults(data)

  if (Array.isArray(data?.results)) {
    const count = Number(data.count || objects.length)
    const pageSize = Math.max(Number(data.page_size || data.results.length || 1), 1)
    const currentPage = Math.max(Number(data.page || requestedPage), 1)
    const pages = Math.max(Number(data.pages || Math.ceil(count / pageSize) || 1), 1)

    return {
      objects,
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
    objects,
    pagination: {
      page: requestedPage,
      pages: 1,
      has_next: false,
      has_previous: false,
      count: objects.length,
      page_size: objects.length,
    },
  }
}

export async function fetchExpenseObjects({ page = 1 } = {}) {
  const response = await apiClient.get('/api/data-management-app/expense-objects/', {
    params: { page },
  })
  return normalizePaginatedResponse(response.data, page)
}

export async function fetchExpenseObjectById(id) {
  const response = await apiClient.get(`/api/data-management-app/expense-objects/${id}/`)
  return response.data
}

export async function createExpenseObject(payload) {
  const response = await apiClient.post('/api/data-management-app/expense-objects/', payload)
  return response.data
}

export async function updateExpenseObject(id, payload) {
  const response = await apiClient.put(`/api/data-management-app/expense-objects/${id}/`, payload)
  return response.data
}

export async function deleteExpenseObject(id) {
  await apiClient.delete(`/api/data-management-app/expense-objects/${id}/`)
}

export async function bulkDeleteExpenseObjects(ids) {
  await Promise.all(ids.map((id) => deleteExpenseObject(id)))
}

