import { apiClient } from '@/services/http/clients'

export async function fetchSupplierById(id) {
  const response = await apiClient.get(`/api/data-management-app/suppliers/${id}/`)
  return response.data
}

export async function createSupplier(payload) {
  const response = await apiClient.post('/api/data-management-app/suppliers/', payload)
  return response.data
}

export async function updateSupplier(id, payload) {
  const response = await apiClient.put(`/api/data-management-app/suppliers/${id}/`, payload)
  return response.data
}
