import { apiClient } from '@/services/http/clients'

export async function fetchNegosyoCenterReport() {
  const response = await apiClient.get('/api/reports-app/nc/')
  return response.data
}

