import { useState, useEffect, useCallback, useRef } from 'react'
import { api, WSManager } from '@/lib/api'
import type { WebSocketEvent, TenantData } from '@/types'

export function useWebSocket(tenantId: string | null) {
  const [connected, setConnected] = useState(false)
  const [lastEvent, setLastEvent] = useState<WebSocketEvent | null>(null)
  const [events, setEvents] = useState<WebSocketEvent[]>([])
  const wsRef = useRef<WSManager | null>(null)

  useEffect(() => {
    if (!tenantId) return

    const ws = new WSManager(tenantId)
    wsRef.current = ws

    ws.connect()
      .then(() => setConnected(true))
      .catch(() => setConnected(false))

    ws.on('*', (data: unknown) => {
      const event = data as { event: string; data: WebSocketEvent }
      if (event.data) {
        setLastEvent(event.data)
        setEvents(prev => [event.data, ...prev.slice(0, 99)])
      }
    })

    return () => {
      ws.disconnect()
      setConnected(false)
    }
  }, [tenantId])

  const send = useCallback((data: unknown) => {
    wsRef.current?.send(data)
  }, [])

  return { connected, lastEvent, events, send }
}

export function useTenants() {
  const [tenants, setTenants] = useState<TenantData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTenants = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // Mock data for now
      const mockTenants: TenantData[] = [
        {
          tenant_id: 'abe-music',
          name: 'ABE Music',
          status: 'active',
          services: [
            { id: 'svc-1', name: 'API Gateway', type: 'api', status: 'operational', url: 'https://api.abe-music.sonora.com' },
            { id: 'svc-2', name: 'Frontend', type: 'frontend', status: 'operational', url: 'https://abe-music.sonora.com' },
            { id: 'svc-3', name: 'Worker', type: 'worker', status: 'operational' },
            { id: 'svc-4', name: 'PostgreSQL', type: 'database', status: 'operational' },
            { id: 'svc-5', name: 'Redis', type: 'cache', status: 'operational' },
          ],
          mcp_servers: [
            { id: 'mcp-1', name: 'Social Media MCP', type: 'social', status: 'healthy', endpoint: 'https://mcp-social.abe-music.sonora.com', tenant_id: 'abe-music', capabilities: ['post', 'schedule', 'analytics'] },
            { id: 'mcp-2', name: 'Analytics MCP', type: 'analytics', status: 'healthy', endpoint: 'https://mcp-analytics.abe-music.sonora.com', tenant_id: 'abe-music', capabilities: ['track', 'report', 'alert'] },
          ],
          domains: ['abe-music.sonora.com', 'api.abe-music.sonora.com'],
          environment: 'production',
          created_at: '2024-01-15T10:00:00Z',
          metrics: { revenue: 125000, active_users: 3421, api_calls: 2.4e6, token_balance: 50000, greetings_pending: 3, quests_active: 12 },
        },
        {
          tenant_id: 'aztrotech',
          name: 'Aztrotech',
          status: 'active',
          services: [
            { id: 'svc-1', name: 'API Gateway', type: 'api', status: 'operational', url: 'https://api.aztrotech.sonora.com' },
            { id: 'svc-2', name: 'Frontend', type: 'frontend', status: 'operational', url: 'https://aztrotech.sonora.com' },
            { id: 'svc-3', name: 'Worker', type: 'worker', status: 'degraded' },
            { id: 'svc-4', name: 'PostgreSQL', type: 'database', status: 'operational' },
          ],
          mcp_servers: [
            { id: 'mcp-1', name: 'Invoice MCP', type: 'invoice', status: 'healthy', endpoint: 'https://mcp-invoice.aztrotech.sonora.com', tenant_id: 'aztrotech', capabilities: ['parse', 'validate', 'store'] },
          ],
          domains: ['aztrotech.sonora.com'],
          environment: 'production',
          created_at: '2024-02-20T14:30:00Z',
          metrics: { revenue: 89000, active_users: 1205, api_calls: 890000, token_balance: 25000, greetings_pending: 1, quests_active: 5 },
        },
        {
          tenant_id: 'hermosillo-contabilidad',
          name: 'Hermosillo Contabilidad',
          status: 'provisioning',
          services: [],
          mcp_servers: [],
          domains: [],
          environment: 'staging',
          created_at: '2024-03-10T09:00:00Z',
        },
      ]
      setTenants(mockTenants)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tenants')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchTenants()
  }, [fetchTenants])

  return { tenants, loading, error, refetch: fetchTenants }
}

export function useRAG(tenantId: string | null) {
  const [results, setResults] = useState<Array<{ id: string; content: string; score: number }>>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const query = useCallback(async (q: string, limit = 5) => {
    if (!tenantId || !q.trim()) return
    setLoading(true)
    setError(null)
    try {
      const response = await api.queryRAG(tenantId, q, limit)
      setResults(response.results || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'RAG query failed')
    } finally {
      setLoading(false)
    }
  }, [tenantId])

  return { results, loading, error, query }
}

export function useEngram() {
  const [memories, setMemories] = useState<Array<{ key: string; value: string; layer: number }>>([])
  const [loading, setLoading] = useState(false)

  const search = useCallback(async (query: string, layer?: number) => {
    setLoading(true)
    try {
      // Mock for now
      await new Promise(r => setTimeout(r, 500))
      setMemories([
        { key: 'decision:pricing', value: 'Adopted tiered pricing model for MCP servers', layer: 0 },
        { key: 'learning:mcp-pattern', value: 'MCP servers work best when deployed per-tenant with shared registry', layer: 1 },
        { key: 'observation:ig-trends', value: 'Reels with trending audio in first 3s get 3x engagement', layer: 2 },
      ])
    } finally {
      setLoading(false)
    }
  }, [])

  const save = useCallback(async (key: string, value: string, layer = 0, tags: string[] = []) => {
    // Mock for now
    console.log('[Engram] Save:', key, value, layer, tags)
  }, [])

  return { memories, loading, search, save }
}