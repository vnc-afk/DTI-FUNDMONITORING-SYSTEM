import { apiClient } from '@/services/http/clients'

export async function fetchMooeReport() {
  const response = await apiClient.get('/api/reports-app/mooe/')
  return response.data
}

