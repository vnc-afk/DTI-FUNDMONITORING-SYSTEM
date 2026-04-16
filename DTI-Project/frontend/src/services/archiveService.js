import { apiClient } from '@/services/http/clients'

export async function fetchArchiveDashboard() {
  const response = await apiClient.get('/api/dashboard-app/archive/dashboard/')
  return response.data
}

export async function archiveYear(payload) {
  const response = await apiClient.post('/api/dashboard-app/archive/year/', payload)
  return response.data
}

export async function unarchiveYear(payload) {
  const response = await apiClient.post('/api/dashboard-app/archive/unarchive/', payload)
  return response.data
}

export async function fetchArchivedStatements(params = {}) {
  const response = await apiClient.get('/api/dashboard-app/archive/statements/', { params })
  return response.data
}

export async function restoreArchivedStatement(statementId) {
  const response = await apiClient.post(`/api/dashboard-app/archive/statements/${statementId}/restore/`)
  return response.data
}

export async function fetchArchivedTransactions(params = {}) {
  const response = await apiClient.get('/api/dashboard-app/archive/transactions/', { params })
  return response.data
}

export async function restoreArchivedTransaction(transactionId) {
  const response = await apiClient.post(`/api/dashboard-app/archive/transactions/${transactionId}/restore/`)
  return response.data
}
