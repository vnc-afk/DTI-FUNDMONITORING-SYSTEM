function trimTrailingSlash(value) {
  return String(value || '').trim().replace(/\/+$/, '')
}

function normalizeBaseUrl(rawValue, envName) {
  const normalized = trimTrailingSlash(rawValue)
  if (!normalized) {
    throw new Error(`${envName} is required and must be an absolute URL.`)
  }

  const parsed = new URL(normalized)
  if (!/^https?:$/.test(parsed.protocol)) {
    throw new Error(`${envName} must use http or https.`)
  }

  return parsed.toString().replace(/\/+$/, '')
}

export const API_BASE_URL = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL, 'VITE_API_BASE_URL')

export function getWsBaseUrl() {
  const rawWsBase = trimTrailingSlash(import.meta.env.VITE_WS_BASE_URL)
  if (!rawWsBase) {
    return null
  }

  const parsed = new URL(rawWsBase)
  const protocol = parsed.protocol === 'https:' ? 'wss:' : parsed.protocol === 'http:' ? 'ws:' : parsed.protocol

  if (!/^wss?:$/.test(protocol)) {
    throw new Error('VITE_WS_BASE_URL must use ws, wss, http, or https.')
  }

  parsed.protocol = protocol
  return parsed.toString().replace(/\/+$/, '')
}
