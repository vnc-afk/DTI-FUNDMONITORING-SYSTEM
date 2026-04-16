import { apiClient } from '@/services/http/clients'

export async function fetchMasterFundMonitoringById(id) {
  const response = await apiClient.get(`/api/mater-fundmonitor-app/master-fund-monitoring/${id}/`)
  return response.data
}

export async function createMasterFundMonitoring(payload) {
  const response = await apiClient.post('/api/mater-fundmonitor-app/master-fund-monitoring/', payload)
  return response.data
}

export async function updateMasterFundMonitoring(id, payload) {
  const response = await apiClient.put(`/api/mater-fundmonitor-app/master-fund-monitoring/${id}/`, payload)
  return response.data
}

function toResults(payload) {
  if (Array.isArray(payload)) {
    return payload
  }
  if (Array.isArray(payload?.results)) {
    return payload.results
  }
  return []
}

export async function fetchMasterFundMonitoringFormOptions() {
  const [
    divisionsResponse,
    fundSourcesResponse,
    mooeResponse,
    ncResponse,
    suppliersResponse,
    purchaseTypesResponse,
    accountTitlesResponse,
    expenseClassificationsResponse,
    staffResponse,
  ] = await Promise.all([
    apiClient.get('/api/data-management-app/divisions/'),
    apiClient.get('/api/data-management-app/fund-sources/'),
    apiClient.get('/api/data-management-app/breakdown-categories/'),
    apiClient.get('/api/data-management-app/negosyo-centers/'),
    apiClient.get('/api/data-management-app/suppliers/'),
    apiClient.get('/api/data-management-app/purchase-types/'),
    apiClient.get('/api/data-management-app/expense-objects/'),
    apiClient.get('/api/data-management-app/expense-categories/'),
    apiClient.get('/api/data-management-app/staff/'),
  ])

  return {
    divisions: toResults(divisionsResponse.data),
    fundSources: toResults(fundSourcesResponse.data),
    mooeCategories: toResults(mooeResponse.data),
    negosyoCenters: toResults(ncResponse.data),
    suppliers: toResults(suppliersResponse.data),
    purchaseTypes: toResults(purchaseTypesResponse.data),
    accountTitles: toResults(accountTitlesResponse.data),
    expenseClassifications: toResults(expenseClassificationsResponse.data),
    staffList: toResults(staffResponse.data),
  }
}

export async function fetchSupplierData(supplierId) {
  if (!supplierId) {
    return null
  }
  const response = await apiClient.get(`/api/supplier/${supplierId}/`)
  return response.data
}

export async function fetchTaxRates(purchaseTypeId) {
  if (!purchaseTypeId) {
    return null
  }
  const response = await apiClient.get(`/api/tax-rates/${purchaseTypeId}/`)
  return response.data
}

export async function fetchFundBudget(fundId) {
  if (!fundId) {
    return null
  }
  const response = await apiClient.get('/api/fund-budget/', { params: { fund_id: fundId } })
  return response.data
}

export async function fetchMooeBudget(mooeId) {
  if (!mooeId) {
    return null
  }
  const response = await apiClient.get('/api/mooe-budget/', { params: { mooe_id: mooeId } })
  return response.data
}

