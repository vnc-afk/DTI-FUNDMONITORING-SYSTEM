import { apiClient } from '@/services/http/clients'

function extractErrorMessage(error) {
  const fallback = 'Request failed.'
  const payload = error?.response?.data || {}

  if (typeof payload?.message === 'string' && payload.message.trim()) {
    return payload.message
  }

  if (typeof payload?.detail === 'string' && payload.detail.trim()) {
    return payload.detail
  }

  return fallback
}

export async function fetchBankStatements({ q = '', status = '', page = 1, pageSize = '' } = {}) {
  try {
    const response = await apiClient.get('/api/bank_statement/', {
      params: {
        q: q || undefined,
        status: status || undefined,
        page,
        page_size: pageSize || undefined,
      },
    })
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export async function updateBankStatementStatus(id, payload) {
  try {
    const response = await apiClient.post(`/api/bank_statement/${id}/update_status/`, payload)
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export async function deleteBankStatement(id) {
  try {
    const response = await apiClient.delete(`/api/bank_statement/${id}/`)
    return response.data || null
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export async function bulkDeleteBankStatements(ids) {
  try {
    const response = await apiClient.post('/api/bank_statement/bulk_delete/', { ids })
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}
