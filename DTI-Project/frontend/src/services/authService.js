import { publicClient, apiClient } from '@/services/http/clients'
import {
  getAuthSessionState,
  hasAuthenticatedSession,
  persistAuthSession as storeAuthSession,
  refreshAuthSession,
} from '@/services/http/authSession'

export { getAuthSessionState, hasAuthenticatedSession, refreshAuthSession, storeAuthSession }

export async function login(payload) {
  const response = await publicClient.post('/api/user-app/auth/login/', payload)
  return response.data
}

export async function fetchInitialPasswordContext() {
  const response = await apiClient.get('/api/user-app/auth/initial-password/')
  return response.data
}

export async function changeInitialPassword(payload) {
  const response = await apiClient.post('/api/user-app/auth/initial-password/', {
    new_password1: payload.new_password1 || '',
    new_password2: payload.new_password2 || '',
  })
  return response.data
}
