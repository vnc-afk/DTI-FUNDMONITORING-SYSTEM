import { apiClient } from '@/services/http/clients'

function normalizePaginatedResponse(data, requestedPage = 1) {
  if (Array.isArray(data)) {
    const count = data.length
    return {
      records: data,
      pagination: {
        page: 1,
        pages: 1,
        has_next: false,
        has_previous: false,
        count,
        total: count,
      },
    }
  }

  if (Array.isArray(data?.results)) {
    const count = Number(data.count || data.results.length)
    const pageSize = Math.max(Number(data.page_size || data.results.length || 1), 1)
    const currentPage = Math.max(Number(data.page || requestedPage), 1)
    const pages = Math.max(Number(data.pages || Math.ceil(count / pageSize) || 1), 1)

    return {
      records: data.results,
      pagination: {
        page: currentPage,
        pages,
        has_next: data.has_next ?? Boolean(data.next),
        has_previous: data.has_previous ?? Boolean(data.previous),
        count,
        page_size: pageSize,
        total: count,
      },
    }
  }

  return {
    records: [],
    pagination: {
      page: 1,
      pages: 1,
      has_next: false,
      has_previous: false,
      count: 0,
      total: 0,
    },
  }
}

export async function fetchMasterFundMonitoringRecords({
  page = 1,
  includeCancelled = false,
  chequeStatus = '',
} = {}) {
  const params = { page }
  if (includeCancelled) {
    params.include_cancelled = true
  }
  if (chequeStatus && chequeStatus !== 'Cancelled') {
    params.cheque_status = chequeStatus
  }

  const response = await apiClient.get('/api/mater-fundmonitor-app/master-fund-monitoring/', {
    params,
  })

  return normalizePaginatedResponse(response.data, page)
}

export async function cancelMasterFundMonitoringRecord(id, reason = '') {
  const response = await apiClient.post(
    `/api/mater-fundmonitor-app/master-fund-monitoring/${id}/cancel/`,
    { reason },
  )
  return response.data
}

export async function uncancelMasterFundMonitoringRecord(id) {
  const response = await apiClient.post(
    `/api/mater-fundmonitor-app/master-fund-monitoring/${id}/uncancel/`,
  )
  return response.data
}

export async function deleteMasterFundMonitoringRecord(id) {
  await apiClient.delete(`/api/mater-fundmonitor-app/master-fund-monitoring/${id}/`)
}

export async function bulkDeleteMasterFundMonitoringRecords(ids) {
  await Promise.all(ids.map((id) => deleteMasterFundMonitoringRecord(id)))
}

