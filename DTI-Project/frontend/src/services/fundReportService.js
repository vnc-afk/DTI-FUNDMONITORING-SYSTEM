import { apiClient } from '@/services/http/clients'

export async function fetchFundReport() {
  const response = await apiClient.get('/api/reports-app/fund/')
  return response.data
}

