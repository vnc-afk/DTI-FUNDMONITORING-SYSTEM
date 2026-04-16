const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.protocol + '//' + window.location.hostname + ':8000'

function getAccessToken() {
  return localStorage.getItem('access_token') || localStorage.getItem('access') || ''
}

function buildHeaders(extraHeaders = {}) {
  const token = getAccessToken()
  const headers = {
    'Content-Type': 'application/json',
    ...extraHeaders,
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  return headers
}

async function handleResponse(response) {
  if (!response.ok) {
    let errorMessage = `Request failed (${response.status})`
    try {
      const errorData = await response.json()
      if (errorData?.message) {
        errorMessage = errorData.message
      } else if (errorData?.detail) {
        errorMessage = errorData.detail
      }
    } catch {
      // Keep fallback error message.
    }
    throw new Error(errorMessage)
  }

  if (response.status === 204) {
    return null
  }

  return response.json()
}

export async function fetchBankStatements({ q = '', status = '', page = 1 } = {}) {
  const params = new URLSearchParams()
  if (q) params.append('q', q)
  if (status) params.append('status', status)
  params.append('page', String(page))

  const response = await fetch(`${API_BASE_URL}/api/bank_statement/?${params.toString()}`, {
    method: 'GET',
    headers: buildHeaders(),
  })

  return handleResponse(response)
}

export async function updateBankStatementStatus(id, payload) {
  const response = await fetch(`${API_BASE_URL}/api/bank_statement/${id}/update_status/`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify(payload),
  })

  return handleResponse(response)
}

export async function deleteBankStatement(id) {
  const response = await fetch(`${API_BASE_URL}/api/bank_statement/${id}/`, {
    method: 'DELETE',
    headers: buildHeaders(),
  })

  return handleResponse(response)
}

export async function bulkDeleteBankStatements(ids) {
  const response = await fetch(`${API_BASE_URL}/api/bank_statement/bulk_delete/`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({ ids }),
  })

  return handleResponse(response)
}
