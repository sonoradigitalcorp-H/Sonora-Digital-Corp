import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import type { TenantData, ServiceData, MCPServerData } from '@/types'
import { api } from '@/lib/api'

interface TenantContextValue {
  tenants: TenantData[]
  activeTenant: TenantData | null
  loading: boolean
  error: string | null
  fetchTenants: () => Promise<void>
  setActiveTenant: (tenantId: string) => Promise<void>
  createTenant: (data: Partial<TenantData>) => Promise<TenantData>
  updateTenant: (tenantId: string, data: Partial<TenantData>) => Promise<void>
  deleteTenant: (tenantId: string) => Promise<void>
  getServices: (tenantId: string) => Promise<ServiceData[]>
  getMCPServers: (tenantId: string) => Promise<MCPServerData[]>
}

const TenantContext = createContext<TenantContextValue | null>(null)

export function TenantProvider({ children }: { children: ReactNode }) {
  const [tenants, setTenants] = useState<TenantData[]>([])
  const [activeTenant, setActiveTenantState] = useState<TenantData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchTenants = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // For now, use mock data since we don't have a real tenants endpoint
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
      if (!activeTenant && mockTenants.length > 0) {
        setActiveTenantState(mockTenants[0])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tenants')
    } finally {
      setLoading(false)
    }
  }, [activeTenant])

  const setActiveTenant = useCallback(async (tenantId: string) => {
    const tenant = tenants.find(t => t.tenant_id === tenantId)
    if (tenant) {
      setActiveTenantState(tenant)
    }
  }, [tenants])

  const createTenant = useCallback(async (data: Partial<TenantData>) => {
    const newTenant: TenantData = {
      tenant_id: data.tenant_id || `tenant-${Date.now()}`,
      name: data.name || 'New Tenant',
      status: 'provisioning',
      services: [],
      mcp_servers: [],
      domains: [],
      environment: 'staging',
      created_at: new Date().toISOString(),
      ...data,
    } as TenantData
    setTenants(prev => [...prev, newTenant])
    return newTenant
  }, [])

  const updateTenant = useCallback(async (tenantId: string, data: Partial<TenantData>) => {
    setTenants(prev => prev.map(t => t.tenant_id === tenantId ? { ...t, ...data } : t))
    if (activeTenant?.tenant_id === tenantId) {
      setActiveTenantState(prev => prev ? { ...prev, ...data } : null)
    }
  }, [activeTenant])

  const deleteTenant = useCallback(async (tenantId: string) => {
    setTenants(prev => prev.filter(t => t.tenant_id !== tenantId))
    if (activeTenant?.tenant_id === tenantId) {
      setActiveTenantState(tenants.find(t => t.tenant_id !== tenantId) || null)
    }
  }, [activeTenant, tenants])

  const getServices = useCallback(async (tenantId: string) => {
    const tenant = tenants.find(t => t.tenant_id === tenantId)
    return tenant?.services || []
  }, [tenants])

  const getMCPServers = useCallback(async (tenantId: string) => {
    const tenant = tenants.find(t => t.tenant_id === tenantId)
    return tenant?.mcp_servers || []
  }, [tenants])

  useEffect(() => {
    fetchTenants()
  }, [fetchTenants])

  return (
    <TenantContext.Provider value={{ tenants, activeTenant, loading, error, fetchTenants, setActiveTenant, createTenant, updateTenant, deleteTenant, getServices, getMCPServers }}>
      {children}
    </TenantContext.Provider>
  )
}

export function useTenant() {
  const context = useContext(TenantContext)
  if (!context) throw new Error('useTenant must be used within TenantProvider')
  return context
}