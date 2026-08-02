import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import type { JARVISState, JARVISAction, JARVISMessage, JARVISCapability, WebSocketEvent } from '@/types'
import { api, WSManager } from '@/lib/api'

const DEFAULT_CAPABILITIES: JARVISCapability[] = [
  { id: 'tenant_provisioning', name: 'Tenant Provisioning', description: 'Full client onboarding', enabled: true, requiresConfirmation: true, confidenceThreshold: 0.85 },
  { id: 'mcp_deployment', name: 'MCP Deployment', description: 'Spin up MCP servers', enabled: true, requiresConfirmation: true, confidenceThreshold: 0.8 },
  { id: 'campaign_creation', name: 'Campaign Creation', description: 'End-to-end marketing campaigns', enabled: true, requiresConfirmation: true, confidenceThreshold: 0.75 },
  { id: 'agent_spawning', name: 'Agent Spawning', description: 'Create new agent skills', enabled: true, requiresConfirmation: true, confidenceThreshold: 0.8 },
  { id: 'infrastructure_scaling', name: 'Infrastructure Scaling', description: 'K8s, Docker, serverless', enabled: true, requiresConfirmation: true, confidenceThreshold: 0.9 },
  { id: 'content_generation', name: 'Content Generation', description: 'IG reels, landing pages, videos', enabled: true, requiresConfirmation: false, confidenceThreshold: 0.7 },
  { id: 'revenue_optimization', name: 'Revenue Optimization', description: '$BEAT mechanics, pricing', enabled: true, requiresConfirmation: true, confidenceThreshold: 0.85 },
  { id: 'knowledge_synthesis', name: 'Knowledge Synthesis', description: 'RAG queries, brain vault updates', enabled: true, requiresConfirmation: false, confidenceThreshold: 0.65 },
  { id: 'security_auditing', name: 'Security Auditing', description: 'Cyber diagnosis, compliance', enabled: true, requiresConfirmation: true, confidenceThreshold: 0.9 },
  { id: 'autonomous_evolution', name: 'Autonomous Evolution', description: 'Self-improving code/skills', enabled: true, requiresConfirmation: true, confidenceThreshold: 0.95 },
]

interface JARVISContextValue extends JARVISState {
  sendCommand: (command: string) => Promise<void>
  speak: (text: string) => void
  listen: () => Promise<string | null>
  addMessage: (message: Omit<JARVISMessage, 'id' | 'timestamp'>) => void
  clearHistory: () => void
  setMode: (mode: JARVISState['mode']) => void
  connectWebSocket: (tenantId: string) => Promise<void>
  disconnectWebSocket: () => void
  getCapabilities: () => JARVISCapability[]
  toggleCapability: (id: string) => void
}

const JARVISContext = createContext<JARVISContextValue | null>(null)

let wsManager: WSManager | null = null

export function JARVISProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<JARVISState>({
    status: 'offline',
    mode: 'autonomous',
    history: [],
    capabilities: DEFAULT_CAPABILITIES,
    confidence: 0,
  })

  const connectWebSocket = useCallback(async (tenantId: string) => {
    setState(prev => ({ ...prev, status: 'initializing' }))
    try {
      wsManager = new WSManager(tenantId)
      await wsManager.connect()

      wsManager.on('agent:*', (data: unknown) => {
        const event = data as WebSocketEvent
        addMessage({
          role: 'system',
          content: `Agent event: ${event.event_type} for tenant ${event.tenant_id}`,
        })
      })

      wsManager.on('*', (data: unknown) => {
        const event = data as { event: string; data: unknown }
        if (event.event.includes('error') || event.event.includes('down')) {
          setState(prev => ({ ...prev, status: 'error', confidence: 0.2 }))
        }
      })

      setState(prev => ({ ...prev, status: 'listening', confidence: 0.9 }))
    } catch (error) {
      console.error('[JARVIS] WS connection failed:', error)
      setState(prev => ({ ...prev, status: 'error', confidence: 0 }))
    }
  }, [])

  const disconnectWebSocket = useCallback(() => {
    wsManager?.disconnect()
    wsManager = null
    setState(prev => ({ ...prev, status: 'offline', confidence: 0 }))
  }, [])

  const addMessage = useCallback((message: Omit<JARVISMessage, 'id' | 'timestamp'>) => {
    const newMessage: JARVISMessage = {
      ...message,
      id: `msg-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      timestamp: new Date().toISOString(),
    }
    setState(prev => ({
      ...prev,
      history: [...prev.history.slice(-99), newMessage],
    }))
  }, [])

  const clearHistory = useCallback(() => {
    setState(prev => ({ ...prev, history: [] }))
  }, [])

  const setMode = useCallback((mode: JARVISState['mode']) => {
    setState(prev => ({ ...prev, mode }))
  }, [])

  const getCapabilities = useCallback(() => state.capabilities, [state.capabilities])

  const toggleCapability = useCallback((id: string) => {
    setState(prev => ({
      ...prev,
      capabilities: prev.capabilities.map(c => c.id === id ? { ...c, enabled: !c.enabled } : c),
    }))
  }, [])

  const speak = useCallback((text: string) => {
    // Use Web Speech API for TTS
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 1.1
      utterance.pitch = 1
      utterance.volume = 0.8
      const voices = speechSynthesis.getVoices()
      const preferredVoice = voices.find(v => v.name.includes('Google') || v.name.includes('Microsoft') || v.lang.startsWith('es'))
      if (preferredVoice) utterance.voice = preferredVoice
      speechSynthesis.speak(utterance)
    }
  }, [])

  const listen = useCallback(async (): Promise<string | null> => {
    return new Promise((resolve) => {
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        resolve(null)
        return
      }

      const SpeechRecognition = (window as unknown as { SpeechRecognition: new () => SpeechRecognition; webkitSpeechRecognition: new () => SpeechRecognition }).SpeechRecognition || (window as unknown as { webkitSpeechRecognition: new () => SpeechRecognition }).webkitSpeechRecognition
      const recognition = new SpeechRecognition()
      recognition.lang = 'es-MX'
      recognition.continuous = false
      recognition.interimResults = false

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        resolve(transcript)
      }

      recognition.onerror = () => resolve(null)
      recognition.onend = () => resolve(null)

      recognition.start()
    })
  }, [])

  const sendCommand = useCallback(async (command: string) => {
    addMessage({ role: 'user', content: command })
    setState(prev => ({ ...prev, status: 'thinking' }))

    // Simulate autonomous loop
    const actions: JARVISAction[] = [
      { id: 'perceive', type: 'perceive', description: 'Analyzing system events...', confidence: 0.9, status: 'running', startedAt: new Date().toISOString() },
      { id: 'reason', type: 'reason', description: 'Reasoning with LLM + RAG...', confidence: 0.85, status: 'pending', startedAt: new Date().toISOString() },
      { id: 'propose', type: 'propose', description: 'Generating proposals...', confidence: 0.8, status: 'pending', startedAt: new Date().toISOString() },
    ]

    // For now, just echo back with simulated response
    setTimeout(() => {
      const responses = [
        `Entendido. Analizando: "${command}". Como JARVIS autónomo, detecto 3 acciones posibles. ¿Ejecutar?`,
        `Procesando comando: "${command}". Confianza: 87%. Requiere confirmación para acciones críticas.`,
        `Recibido. Consultando brain vault y RAG... Encontré contexto relevante. ¿Proceder?`,
      ]
      const response = responses[Math.floor(Math.random() * responses.length)]
      addMessage({ role: 'assistant', content: response })
      speak(response)
      setState(prev => ({ ...prev, status: 'listening', confidence: 0.87 }))
    }, 1500)
  }, [addMessage, speak])

  return (
    <JARVISContext.Provider value={{ ...state, sendCommand, speak, listen, addMessage, clearHistory, setMode, connectWebSocket, disconnectWebSocket, getCapabilities, toggleCapability }}>
      {children}
    </JARVISContext.Provider>
  )
}

export function useJARVIS() {
  const context = useContext(JARVISContext)
  if (!context) throw new Error('useJARVIS must be used within JARVISProvider')
  return context
}