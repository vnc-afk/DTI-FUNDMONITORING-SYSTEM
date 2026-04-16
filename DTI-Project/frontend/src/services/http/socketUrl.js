import { getWsBaseUrl } from '@/services/http/config'

export function buildSocketUrl(path = '/ws/realtime/', params = {}) {
  const wsBase = getWsBaseUrl()
  if (!wsBase) {
    return null
  }

  let baseUrl
  try {
    baseUrl = new URL(wsBase)
  } catch {
    return null
  }

  if (baseUrl.protocol === 'http:') {
    baseUrl.protocol = 'ws:'
  } else if (baseUrl.protocol === 'https:') {
    baseUrl.protocol = 'wss:'
  }

  if (!/^wss?:$/.test(baseUrl.protocol)) {
    return null
  }

  const normalizedPath = String(path || '/ws/realtime/').startsWith('/')
    ? String(path || '/ws/realtime/')
    : `/${path}`

  baseUrl.pathname = normalizedPath
  baseUrl.search = ''

  Object.entries(params || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== '') {
      baseUrl.searchParams.set(key, String(value))
    }
  })

  return baseUrl.toString()
}
