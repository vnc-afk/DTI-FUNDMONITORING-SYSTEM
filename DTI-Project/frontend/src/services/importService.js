import { apiClient } from '@/services/http/clients'

export async function fetchImportFormConfig() {
  const response = await apiClient.get('/api/dashboard-app/import/form/')
  return response.data
}

export async function submitImportData(formData) {
  const response = await apiClient.post('/api/dashboard-app/import/submit/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export async function fetchImportResult() {
  const response = await apiClient.get('/api/dashboard-app/import/result/')
  return response.data
}

