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

async function fetchAllPages(path, params = {}) {
  const items = []
  let nextUrl = path
  let isFirstRequest = true

  while (nextUrl) {
    const response = await apiClient.get(nextUrl, {
      params: isFirstRequest ? params : undefined,
    })
    const payload = response.data

    if (Array.isArray(payload)) {
      items.push(...payload)
      break
    }

    if (Array.isArray(payload?.results)) {
      items.push(...payload.results)
      nextUrl = payload.next || null
      isFirstRequest = false
      continue
    }

    break
  }

  return items
}

export async function fetchMasterFundMonitoringFormOptions() {
  const [
    divisions,
    fundSources,
    mooeCategories,
    negosyoCenters,
    suppliers,
    purchaseTypes,
    accountTitles,
    expenseClassifications,
    staffList,
  ] = await Promise.all([
    fetchAllPages('/api/data-management-app/divisions/', { page_size: 200 }),
    fetchAllPages('/api/data-management-app/fund-sources/', { page_size: 200 }),
    fetchAllPages('/api/data-management-app/breakdown-categories/', { page_size: 200 }),
    fetchAllPages('/api/data-management-app/negosyo-centers/', { page_size: 200 }),
    fetchAllPages('/api/data-management-app/suppliers/', { page_size: 200 }),
    fetchAllPages('/api/data-management-app/purchase-types/', { page_size: 200 }),
    fetchAllPages('/api/data-management-app/expense-objects/', { page_size: 200 }),
    fetchAllPages('/api/data-management-app/expense-categories/', { page_size: 200 }),
    fetchAllPages('/api/data-management-app/staff/', { page_size: 200 }),
  ])

  return {
    divisions,
    fundSources,
    mooeCategories,
    negosyoCenters,
    suppliers,
    purchaseTypes,
    accountTitles,
    expenseClassifications,
    staffList,
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

