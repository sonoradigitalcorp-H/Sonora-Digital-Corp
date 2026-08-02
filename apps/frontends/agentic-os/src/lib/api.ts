const API_BASE = '/api/v1'
const WS_BASE = '/ws'

class APIClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL = API_BASE) {
    this.baseURL = baseURL
  }

  setToken(token: string) {
    this.token = token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }))
      throw new Error(error.message || `HTTP ${response.status}`)
    }

    return response.json()
  }

  // Dashboard
  async getRevenueStats(tenantId: string) {
    return this.request(`/dashboard/revenue?tenant_id=${tenantId}`)
  }

  async getTokenStats(tenantId: string) {
    return this.request(`/dashboard/tokens?tenant_id=${tenantId}`)
  }

  async getGreetingStats(tenantId: string) {
    return this.request(`/dashboard/greetings?tenant_id=${tenantId}`)
  }

  async getQuestStats(tenantId: string) {
    return this.request(`/dashboard/quests?tenant_id=${tenantId}`)
  }

  async getLeaderboard(tenantId: string, metric = 'xp', limit = 10) {
    return this.request(`/dashboard/leaderboard?tenant_id=${tenantId}&metric=${metric}&limit=${limit}`)
  }

  async getArtistStreams(tenantId: string) {
    return this.request(`/dashboard/streams?tenant_id=${tenantId}`)
  }

  // RAG
  async queryRAG(tenantId: string, query: string, limit = 5) {
    return this.request(`/rag/query?tenant_id=${tenantId}&q=${encodeURIComponent(query)}&limit=${limit}`)
  }

  async listRAGCollections() {
    return this.request('/rag/collections')
  }

  // Auth
  async getAuthStatus() {
    return this.request('/auth/me')
  }

  // Events
  async getEvents(tenantId: string, limit = 50) {
    return this.request(`/events/${tenantId}?limit=${limit}`)
  }

  // Health
  async healthCheck() {
    return this.request('/health')
  }

  // Seed (dev only)
  async seedDemoData(tenantId = 'abe-music') {
    return this.request(`/dashboard/seed?tenant_id=${tenantId}`)
  }
}

export const api = new APIClient()

// WebSocket connection manager
export class WSManager {
  private ws: WebSocket | null = null
  private tenantId: string
  private handlers: Map<string, Set<(data: unknown) => void>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  constructor(tenantId: string) {
    this.tenantId = tenantId
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}${WS_BASE}/${this.tenantId}`
      
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('[WS] Connected to', this.tenantId)
        this.reconnectAttempts = 0
        resolve()
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.emit(data.event_type, data)
        } catch (e) {
          console.error('[WS] Parse error:', e)
        }
      }

      this.ws.onclose = () => {
        console.log('[WS] Disconnected')
        this.attemptReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('[WS] Error:', error)
        reject(error)
      }
    })
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
      console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)
      setTimeout(() => this.connect(), delay)
    }
  }

  disconnect() {
    this.ws?.close()
    this.ws = null
  }

  on(event: string, handler: (data: unknown) => void) {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set())
    }
    this.handlers.get(event)!.add(handler)
    return () => this.off(event, handler)
  }

  off(event: string, handler: (data: unknown) => void) {
    this.handlers.get(event)?.delete(handler)
  }

  private emit(event: string, data: unknown) {
    this.handlers.get(event)?.forEach(handler => handler(data))
    this.handlers.get('*')?.forEach(handler => handler({ event, data }))
  }

  send(data: unknown) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  get readyState() {
    return this.ws?.readyState ?? WebSocket.CLOSED
  }
}