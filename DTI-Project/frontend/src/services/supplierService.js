import { apiClient } from '@/services/http/clients'

function normalizePaginatedResponse(data, requestedPage = 1) {
  if (Array.isArray(data)) {
    return {
      suppliers: data,
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
      suppliers: data.results,
      vatCount: Number(data.vat_count || 0),
      nonVatCount: Number(data.non_vat_count || 0),
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
    suppliers: [],
    vatCount: 0,
    nonVatCount: 0,
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

export async function fetchSuppliers({ page = 1, query = '', vatStatus = '', pageSize = '' } = {}) {
  const response = await apiClient.get('/api/data-management-app/suppliers/', {
    params: {
      page,
      search: query || undefined,
      vat_status: vatStatus || undefined,
      page_size: pageSize || undefined,
    },
  })
  return normalizePaginatedResponse(response.data, page)
}

export async function deleteSupplier(id) {
  await apiClient.delete(`/api/data-management-app/suppliers/${id}/`)
}

export async function bulkDeleteSuppliers(ids) {
  await Promise.all(ids.map((id) => deleteSupplier(id)))
}

