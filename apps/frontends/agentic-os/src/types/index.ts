export type GalaxyId = 
  | 'neura' 
  | 'clientara' 
  | 'agentara' 
  | 'devopsara' 
  | 'contentara' 
  | 'econara'

export type GalaxyPhase = 
  | 'MACRO_VIEW' 
  | 'GALAXY_ENTER' 
  | 'SOLAR_SYSTEM' 
  | 'PLANET_SURFACE' 
  | 'MOON_DETAIL'

export interface GalaxyConfig {
  id: GalaxyId
  name: string
  description: string
  color: string
  secondaryColor: string
  icon: string
  position: [number, number, number]
  rotationSpeed: number
  particleCount: number
  descriptionShort: string
}

export const GALAXY_CONFIGS: Record<GalaxyId, GalaxyConfig> = {
  neura: {
    id: 'neura',
    name: 'NEURA',
    description: 'Knowledge & Brain — Quantum neural lattice, memory orbits, RAG nebulae',
    color: '#7c5cfc',
    secondaryColor: '#a88cff',
    icon: '🧠',
    position: [0, 0, 0],
    rotationSpeed: 0.02,
    particleCount: 500,
    descriptionShort: 'Brain Vault, Engram, RAG, Decisions',
  },
  clientara: {
    id: 'clientara',
    name: 'CLIENTARA',
    description: 'Clients & Tenants — Star systems with service planets and MCP moons',
    color: '#22c55e',
    secondaryColor: '#4ade80',
    icon: '🌟',
    position: [100, 0, 50],
    rotationSpeed: 0.015,
    particleCount: 300,
    descriptionShort: 'Tenants, Services, MCPs, Domains',
  },
  agentara: {
    id: 'agentara',
    name: 'AGENTARA',
    description: 'Agent Swarms — Constellations, orbital workflows, comet trails',
    color: '#06b6d4',
    secondaryColor: '#22d3ee',
    icon: '🤖',
    position: [-80, 40, -30],
    rotationSpeed: 0.025,
    particleCount: 400,
    descriptionShort: 'Agents, Workflows, Skills, Router',
  },
  devopsara: {
    id: 'devopsara',
    name: 'DEVOPSARA',
    description: 'Infrastructure — Asteroid fields, deployment rings, health nebulae',
    color: '#f59e0b',
    secondaryColor: '#fbbf24',
    icon: '🔧',
    position: [60, -60, 80],
    rotationSpeed: 0.01,
    particleCount: 600,
    descriptionShort: 'Docker, K8s, MCP Servers, Monitoring',
  },
  contentara: {
    id: 'contentara',
    name: 'CONTENTARA',
    description: 'Content & Marketing — Nebulae (trends), solar flares (viral), black holes',
    color: '#ec4899',
    secondaryColor: '#f472b6',
    icon: '📱',
    position: [-100, -20, -60],
    rotationSpeed: 0.03,
    particleCount: 450,
    descriptionShort: 'IG Trends, Campaigns, Viral Content',
  },
  econara: {
    id: 'econara',
    name: 'ECONARA',
    description: 'Revenue & Analytics — Pulsars ($BEAT), gravity wells, trade routes',
    color: '#c8a87c',
    secondaryColor: '#e8c89c',
    icon: '💰',
    position: [30, 80, -40],
    rotationSpeed: 0.018,
    particleCount: 350,
    descriptionShort: '$BEAT, Funnels, Leaderboards, Pricing',
  },
}

export interface GalaxyState {
  currentGalaxy: GalaxyId | null
  phase: GalaxyPhase
  selectedObject: GalaxyObject | null
  cameraPosition: [number, number, number]
  cameraTarget: [number, number, number]
  isTransitioning: boolean
}

export interface GalaxyObject {
  id: string
  type: 'galaxy' | 'star' | 'planet' | 'moon' | 'nebula' | 'pulsar' | 'asteroid'
  galaxyId: GalaxyId
  name: string
  position: [number, number, number]
  data: Record<string, unknown>
  children?: GalaxyObject[]
}

export interface TenantData {
  tenant_id: string
  name: string
  status: 'provisioning' | 'active' | 'degraded' | 'inactive'
  services: ServiceData[]
  mcp_servers: MCPServerData[]
  domains: string[]
  environment: 'staging' | 'production'
  created_at: string
  metrics?: TenantMetrics
}

export interface ServiceData {
  id: string
  name: string
  type: 'api' | 'frontend' | 'worker' | 'database' | 'cache' | 'queue'
  status: 'operational' | 'degraded' | 'down'
  url?: string
  health_endpoint?: string
  mcp_servers?: string[]
}

export interface MCPServerData {
  id: string
  name: string
  type: string
  status: 'healthy' | 'degraded' | 'down'
  endpoint: string
  tenant_id: string
  capabilities: string[]
  health_metrics?: MCPHealthMetrics
}

export interface MCPHealthMetrics {
  uptime: number
  requests_per_minute: number
  avg_latency_ms: number
  error_rate: number
  cpu_usage: number
  memory_usage: number
}

export interface TenantMetrics {
  revenue: number
  active_users: number
  api_calls: number
  token_balance: number
  greetings_pending: number
  quests_active: number
}

export interface AgentData {
  id: string
  name: string
  type: 'chat' | 'monetization' | 'gamification' | 'knowledge' | 'automation' | 'custom'
  status: 'idle' | 'processing' | 'error'
  tenant_id: string
  capabilities: string[]
  current_task?: string
  metrics: AgentMetrics
}

export interface AgentMetrics {
  tasks_completed: number
  success_rate: number
  avg_response_time_ms: number
  tokens_consumed: number
}

export interface JARVISState {
  status: 'offline' | 'initializing' | 'listening' | 'thinking' | 'speaking' | 'executing' | 'error'
  mode: 'autonomous' | 'assisted' | 'manual'
  currentAction?: JARVISAction
  history: JARVISMessage[]
  capabilities: JARVISCapability[]
  confidence: number
}

export interface JARVISAction {
  id: string
  type: 'perceive' | 'reason' | 'propose' | 'execute' | 'verify' | 'learn'
  description: string
  confidence: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  startedAt: string
  completedAt?: string
  result?: unknown
}

export interface JARVISMessage {
  id: string
  role: 'user' | 'assistant' | 'system' | 'tool'
  content: string
  timestamp: string
  metadata?: Record<string, unknown>
}

export interface JARVISCapability {
  id: string
  name: string
  description: string
  enabled: boolean
  requiresConfirmation: boolean
  confidenceThreshold: number
}

export interface WebSocketEvent {
  event_type: string
  tenant_id: string
  agent?: string
  intent?: string
  payload?: Record<string, unknown>
  timestamp: string
}

export interface RAGQueryResult {
  query: string
  results: RAGResult[]
  total: number
  took_ms: number
}

export interface RAGResult {
  id: string
  content: string
  metadata: Record<string, unknown>
  score: number
}

export interface EngramMemory {
  key: string
  value: string
  layer: number
  importance: number
  tags: string[]
  created_at: string
  updated_at: string
}

export interface BrainVaultFile {
  path: string
  name: string
  content: string
  frontmatter: Record<string, unknown>
  links: string[]
  tags: string[]
}

export interface GitCommit {
  hash: string
  message: string
  author: string
  date: string
  files: string[]
}

export interface ADRRecord {
  id: string
  title: string
  status: 'proposed' | 'accepted' | 'rejected' | 'superseded'
  context: string
  decision: string
  consequences: string
  date: string
}