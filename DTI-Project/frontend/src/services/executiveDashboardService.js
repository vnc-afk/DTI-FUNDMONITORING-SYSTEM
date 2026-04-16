// Executive Dashboard Service
// Fetches KPI data, alerts, fund status, and performance metrics

import { apiClient } from '@/services/http/clients'

/**
 * Fetch executive dashboard KPIs (summary metrics)
 * @param {number} year - Fiscal year
 * @returns {Promise<Object>} KPI data
 */
async function fetchExecutiveDashboardKpis(year = new Date().getFullYear()) {
  try {
    const params = { year }
    const response = await apiClient.get('/api/dashboard/executive-kpis/', { params })
    return response.data
  } catch (error) {
    console.error('Error fetching executive dashboard KPIs:', error)
    throw error
  }
}

/**
 * Fetch fund-by-fund status data
 * @param {number} year - Fiscal year
 * @returns {Promise<Array>} Fund status data
 */
async function fetchFundStatus(year = new Date().getFullYear()) {
  try {
    const params = { year }
    const response = await apiClient.get('/api/dashboard/fund-status/', { params })
    return response.data
  } catch (error) {
    console.error('Error fetching fund status:', error)
    throw error
  }
}

/**
 * Fetch performance metrics
 * @param {number} year - Fiscal year
 * @returns {Promise<Object>} Performance metrics
 */
async function fetchPerformanceMetrics(year = new Date().getFullYear()) {
  try {
    const params = { year }
    const response = await apiClient.get('/api/dashboard/performance-metrics/', { params })
    return response.data
  } catch (error) {
    console.error('Error fetching performance metrics:', error)
    throw error
  }
}

/**
 * Fetch monthly spending data
 * @param {number} year - Fiscal year
 * @returns {Promise<Object>} Monthly spending data
 */
async function fetchMonthlySpendings(year = new Date().getFullYear()) {
  try {
    const params = { year }
    const response = await apiClient.get('/api/dashboard/monthly-spendings/', { params })
    return response.data
  } catch (error) {
    console.error('Error fetching monthly spendings:', error)
    throw error
  }
}

/**
 * Fetch executive alerts
 * @param {number} year - Fiscal year
 * @returns {Promise<Array>} Alerts data
 */
async function fetchExecutiveAlerts(year = new Date().getFullYear()) {
  try {
    const params = { year }
    const response = await apiClient.get('/api/dashboard/executive-alerts/', { params })
    return response.data
  } catch (error) {
    console.error('Error fetching executive alerts:', error)
    // Return empty array if no alerts are available
    return []
  }
}

/**
 * Fetch all executive dashboard data
 * @param {number} year - Fiscal year
 * @returns {Promise<Object>} Complete dashboard data
 */
export async function fetchExecutiveDashboardData(year = new Date().getFullYear()) {
  try {
    const [kpis, funds, metrics, spendings, alerts] = await Promise.all([
      fetchExecutiveDashboardKpis(year),
      fetchFundStatus(year),
      fetchPerformanceMetrics(year),
      fetchMonthlySpendings(year),
      fetchExecutiveAlerts(year),
    ])

    return {
      kpis,
      funds,
      metrics,
      spendings,
      alerts,
      year,
    }
  } catch (error) {
    console.error('Error fetching executive dashboard data:', error)
    throw error
  }
}

/**
 * Fetch available fiscal years
 * @returns {Promise<Array>} Array of available years
 */
export async function fetchAvailableYears() {
  try {
    const response = await apiClient.get('/api/dashboard/available-years/')
    return response.data
  } catch (error) {
    console.error('Error fetching available years:', error)
    // Return current year as fallback
    return [new Date().getFullYear()]
  }
}

