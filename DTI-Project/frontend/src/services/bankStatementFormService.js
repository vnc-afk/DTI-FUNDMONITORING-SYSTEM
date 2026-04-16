import { apiClient } from '@/services/http/clients'

export async function fetchBankStatementMeta() {
  const response = await apiClient.get('/api/bank_statement/', {
    params: {
      page: 1,
    },
  })

  const payload = response.data || {}
  const cards = payload.summary_cards || []
  const currentBalanceCard = cards.find((card) => card.title === 'Current Balance')

  return {
    statementCount: payload.statement_count || 0,
    previousBalance: Number(currentBalanceCard?.value || 0),
    isFirstTransaction: (payload.statement_count || 0) === 0,
  }
}

export async function fetchBankStatementById(id) {
  const response = await apiClient.get(`/api/bank_statement/${id}/`)
  return response.data
}

export async function createBankStatement(payload) {
  const response = await apiClient.post('/api/bank_statement/', payload)
  return response.data
}

export async function updateBankStatement(id, payload) {
  const response = await apiClient.put(`/api/bank_statement/${id}/`, payload)
  return response.data
}

