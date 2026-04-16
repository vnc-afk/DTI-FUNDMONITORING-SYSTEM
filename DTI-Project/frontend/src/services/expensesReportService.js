import { apiClient } from '@/services/http/clients'

export async function fetchExpensesReport(groupBy = 'classification') {
  const response = await apiClient.get('/api/reports-app/expense/', {
    params: {
      group_by: groupBy === 'object' ? 'object' : 'classification',
    },
  })

  return response.data
}

