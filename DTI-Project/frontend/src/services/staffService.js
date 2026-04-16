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
  const records = normalizeResults(data)

  if (Array.isArray(data?.results)) {
    const count = Number(data.count || records.length)
    const pageSize = Math.max(Number(data.page_size || data.results.length || 1), 1)
    const currentPage = Math.max(Number(data.page || requestedPage), 1)
    const pages = Math.max(Number(data.pages || Math.ceil(count / pageSize) || 1), 1)

    return {
      staff: records,
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
    staff: records,
    pagination: {
      page: requestedPage,
      pages: 1,
      has_next: false,
      has_previous: false,
      count: records.length,
      page_size: records.length,
    },
  }
}

export async function fetchStaffMembers({ page = 1 } = {}) {
  const response = await apiClient.get('/api/data-management-app/staff/', {
    params: { page },
  })
  return normalizePaginatedResponse(response.data, page)
}

export async function fetchStaffMemberById(id) {
  const response = await apiClient.get(`/api/data-management-app/staff/${id}/`)
  return response.data
}

export async function createStaffMember(payload) {
  const response = await apiClient.post('/api/data-management-app/staff/', payload)
  return response.data
}

export async function updateStaffMember(id, payload) {
  const response = await apiClient.put(`/api/data-management-app/staff/${id}/`, payload)
  return response.data
}

export async function fetchDivisions() {
  const response = await apiClient.get('/api/data-management-app/divisions/')
  return normalizeResults(response.data)
}

export async function deleteStaffMember(id) {
  await apiClient.delete(`/api/data-management-app/staff/${id}/`)
}

export async function bulkDeleteStaffMembers(ids) {
  await Promise.all(ids.map((id) => deleteStaffMember(id)))
}
