import { getAuthSessionState, refreshAuthSession } from '@/services/authService'
import { buildSocketUrl } from '@/services/http/socketUrl'

const DEFAULT_RECONNECT_BASE_MS = 1000
const DEFAULT_RECONNECT_MAX_MS = 15000

class RealtimeService {
  constructor() {
    this.socket = null
    this.token = ''
    this.handlers = new Set()
    this.connectionHandlers = new Set()
    this.reconnectAttempts = 0
    this.reconnectTimer = null
    this.closedByUser = false
  }

  async connect(token) {
    this.closedByUser = false
    const effectiveToken = await this.resolveToken(token)

    if (this.closedByUser) {
      return
    }

    if (!effectiveToken) {
      this.disconnect()
      return
    }

    if (
      this.socket &&
      (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)
    ) {
      if (this.token === effectiveToken) {
        return
      }

      this.socket.close()
      this.socket = null
    }

    this.token = effectiveToken
    this.closedByUser = false

    const wsUrl = this.buildSocketUrl(effectiveToken)
    if (!wsUrl) {
      this.emitConnection({ status: 'disabled' })
      return
    }

    this.socket = new WebSocket(wsUrl)

    this.socket.onopen = () => {
      this.reconnectAttempts = 0
      this.emitConnection({ status: 'connected' })
    }

    this.socket.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data)
        this.emitEvent(parsed)
      } catch {
        // Ignore malformed payloads.
      }
    }

    this.socket.onclose = () => {
      this.emitConnection({ status: 'disconnected' })
      this.socket = null
      if (!this.closedByUser) {
        this.scheduleReconnect()
      }
    }

    this.socket.onerror = () => {
      this.emitConnection({ status: 'error' })
    }
  }

  disconnect() {
    this.closedByUser = true
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
  }

  subscribe(handler) {
    if (typeof handler !== 'function') {
      return () => {}
    }

    this.handlers.add(handler)
    return () => {
      this.handlers.delete(handler)
    }
  }

  onConnectionChange(handler) {
    if (typeof handler !== 'function') {
      return () => {}
    }

    this.connectionHandlers.add(handler)
    return () => {
      this.connectionHandlers.delete(handler)
    }
  }

  buildSocketUrl(token) {
    return buildSocketUrl('/ws/realtime/', { token })
  }

  async resolveToken(token) {
    const session = getAuthSessionState()
    const currentToken = String(token || session.accessToken || '').trim()

    if (currentToken && !session.accessExpired) {
      return currentToken
    }

    if (session.canRefresh) {
      await refreshAuthSession()
      const refreshedSession = getAuthSessionState()

      if (refreshedSession.accessToken && !refreshedSession.accessExpired) {
        return refreshedSession.accessToken
      }
    }

    return ''
  }

  emitEvent(payload) {
    this.handlers.forEach((handler) => {
      handler(payload)
    })
  }

  emitConnection(payload) {
    this.connectionHandlers.forEach((handler) => {
      handler(payload)
    })
  }

  scheduleReconnect() {
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    this.reconnectAttempts += 1
    const delay = Math.min(
      DEFAULT_RECONNECT_BASE_MS * 2 ** (this.reconnectAttempts - 1),
      DEFAULT_RECONNECT_MAX_MS
    )

    this.reconnectTimer = window.setTimeout(() => {
      this.connect(this.token)
    }, delay)
  }
}

const realtimeService = new RealtimeService()

export default realtimeService
