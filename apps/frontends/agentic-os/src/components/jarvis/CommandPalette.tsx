import { useState, useEffect, useRef, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Zap, Bot, Terminal, Globe, Users, Cpu, TrendingUp, Brain, Settings, X, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils/helpers'
import { useJARVIS } from '@/contexts/JARVISContext'
import { useGalaxy } from '@/contexts/GalaxyContext'
import { useTenant } from '@/contexts/TenantContext'

interface CommandPaletteProps {
  onClose: () => void
  onCommand: (command: string) => void
}

const COMMANDS = [
  // Navigation
  { id: 'nav:cosmos', label: 'Go to Cosmic View', description: 'Return to macro galaxy view', icon: Globe, category: 'Navigation', action: () => {} },
  { id: 'nav:neura', label: 'Enter NEURA Galaxy', description: 'Knowledge & Brain visualization', icon: Brain, category: 'Navigation', action: () => {} },
  { id: 'nav:clientara', label: 'Enter CLIENTARA Galaxy', description: 'Clients & Tenants star systems', icon: Users, category: 'Navigation', action: () => {} },
  { id: 'nav:agentara', label: 'Enter AGENTARA Galaxy', description: 'Agent swarms & workflows', icon: Bot, category: 'Navigation', action: () => {} },
  { id: 'nav:devopsara', label: 'Enter DEVOPSARA Galaxy', description: 'Infrastructure & DevOps', icon: Cpu, category: 'Navigation', action: () => {} },
  { id: 'nav:contentara', label: 'Enter CONTENTARA Galaxy', description: 'Content & Marketing trends', icon: TrendingUp, category: 'Navigation', action: () => {} },
  { id: 'nav:econara', label: 'Enter ECONARA Galaxy', description: 'Revenue & Analytics', icon: Users, category: 'Navigation', action: () => {} },

  // JARVIS Actions
  { id: 'jarvis:provision', label: 'Provision New Tenant', description: 'Full client onboarding workflow', icon: Users, category: 'JARVIS', action: () => {} },
  { id: 'jarvis:deploy-mcp', label: 'Deploy MCP Server', description: 'Spin up MCP for tenant', icon: Cpu, category: 'JARVIS', action: () => {} },
  { id: 'jarvis:campaign', label: 'Create Marketing Campaign', description: 'End-to-end campaign generation', icon: TrendingUp, category: 'JARVIS', action: () => {} },
  { id: 'jarvis:spawn-agent', label: 'Spawn New Agent', description: 'Create custom agent skill', icon: Bot, category: 'JARVIS', action: () => {} },
  { id: 'jarvis:scale', label: 'Scale Infrastructure', description: 'Auto-scale K8s/Docker resources', icon: Cpu, category: 'JARVIS', action: () => {} },
  { id: 'jarvis:analyze-ig', label: 'Analyze Instagram Trends', description: 'Viral pattern detection', icon: TrendingUp, category: 'JARVIS', action: () => {} },
  { id: 'jarvis:optimize', label: 'Optimize Revenue', description: '$BEAT pricing & funnels', icon: TrendingUp, category: 'JARVIS', action: () => {} },
  { id: 'jarvis:synthesize', label: 'Synthesize Knowledge', description: 'RAG query + brain vault update', icon: Brain, category: 'JARVIS', action: () => {} },
  { id: 'jarvis:audit', label: 'Security Audit', description: 'Cyber diagnosis & compliance', icon: Terminal, category: 'JARVIS', action: () => {} },

  // System
  { id: 'sys:toggle-mode', label: 'Toggle JARVIS Mode', description: 'Switch autonomous/assisted/manual', icon: Bot, category: 'System', action: () => {} },
  { id: 'sys:connect-ws', label: 'Connect WebSocket', description: 'Connect to tenant event stream', icon: Globe, category: 'System', action: () => {} },
  { id: 'sys:clear-history', label: 'Clear Chat History', description: 'Reset JARVIS conversation', icon: Terminal, category: 'System', action: () => {} },
  { id: 'sys:settings', label: 'Open Settings', description: 'Configure preferences', icon: Settings, category: 'System', action: () => {} },
]

export function CommandPalette({ onClose, onCommand }: CommandPaletteProps) {
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const { mode, setMode } = useJARVIS()
  const { enterGalaxy, exitGalaxy } = useGalaxy()
  const { tenants, setActiveTenant } = useTenant()

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex(i => Math.min(i + 1, filteredCommands.length - 1))
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex(i => Math.max(i - 1, 0))
      }
      if (e.key === 'Enter') {
        e.preventDefault()
        executeCommand(filteredCommands[selectedIndex])
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [filteredCommands, selectedIndex, onClose])

  const filteredCommands = useMemo(() => {
    if (!query) return COMMANDS.slice(0, 8)
    return COMMANDS.filter(cmd => 
      cmd.label.toLowerCase().includes(query.toLowerCase()) ||
      cmd.description.toLowerCase().includes(query.toLowerCase()) ||
      cmd.category.toLowerCase().includes(query.toLowerCase())
    )
  }, [query])

  const executeCommand = (cmd: typeof COMMANDS[0]) => {
    onCommand(cmd.id)
    
    // Handle specific commands
    if (cmd.id.startsWith('nav:')) {
      const galaxyId = cmd.id.replace('nav:', '') as any
      if (galaxyId === 'cosmos') exitGalaxy()
      else enterGalaxy(galaxyId)
    }
    if (cmd.id === 'sys:toggle-mode') {
      const modes = ['autonomous', 'assisted', 'manual'] as const
      const currentIndex = modes.indexOf(mode)
      setMode(modes[(currentIndex + 1) % 3])
    }
    
    onClose()
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Navigation': return Globe
      case 'JARVIS': return Zap
      case 'System': return Settings
      default: return Terminal
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: -20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95, y: -20 }}
      transition={{ type: 'spring', damping: 25, stiffness: 300 }}
      className="fixed inset-0 z-[100] flex items-start justify-center pt-20 px-4"
      onClick={onClose}
    >
      <motion.div
        className="w-full max-w-2xl cosmic-card overflow-hidden shadow-[0_0_80px_-20px_rgb(124_92_252_/_0.3)]"
        onClick={e => e.stopPropagation()}
      >
        {/* Input */}
        <div className="relative p-4 border-b border-cosmic-border">
          <div className="flex items-center gap-3">
            <Search className="w-5 h-5 text-white/40" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => { setQuery(e.target.value); setSelectedIndex(0) }}
              placeholder="Type a command or search... (⌘K to open)"
              className="flex-1 bg-transparent text-white text-lg font-mono placeholder-white/30 focus:outline-none"
              spellCheck={false}
            />
            <kbd className="px-2 py-1 text-[10px] font-mono text-white/30 bg-cosmic-bg rounded">⌘K</kbd>
          </div>
        </div>

        {/* Results */}
        <AnimatePresence mode="popLayout">
          {filteredCommands.length > 0 ? (
            <div className="max-h-[50vh] overflow-y-auto">
              {groupCommandsByCategory(filteredCommands).map(([category, cmds], catIndex) => (
                <motion.div
                  key={category}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: catIndex * 0.03 }}
                >
                  <div className="px-4 py-2 border-b border-cosmic-border/50">
                       <p className="flex items-center gap-2 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      {(() => {
                        const Icon = getCategoryIcon(category)
                        return Icon ? <Icon className="w-4 h-4" /> : null
                      })()}
                      {category}
                    </p>
                  </div>
                  {cmds.map((cmd, i) => (
                    <motion.button
                      key={cmd.id}
                      onClick={() => executeCommand(cmd)}
                      className={cn(
                        'w-full px-4 py-3 text-left flex items-center gap-3 transition-colors',
                        selectedIndex === getGlobalIndex(category, i, filteredCommands) 
                          ? 'bg-cosmic-primary/10 border-l-2 border-cosmic-primary' 
                          : 'hover:bg-cosmic-border/50'
                      )}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: (catIndex * 10 + i) * 0.01 }}
                    >
                      <cmd.icon className={cn('w-5 h-5 flex-shrink-0', 
                        selectedIndex === getGlobalIndex(category, i, filteredCommands) 
                          ? 'text-cosmic-primary' 
                          : 'text-white/40'
                      )} />
                      <div className="flex-1 min-w-0 text-left">
                        <p className={cn('font-medium text-sm truncate',
                          selectedIndex === getGlobalIndex(category, i, filteredCommands)
                            ? 'text-white'
                            : 'text-white/90'
                        )}>{cmd.label}</p>
                        <p className={cn('text-xs truncate',
                          selectedIndex === getGlobalIndex(category, i, filteredCommands)
                            ? 'text-cosmic-primary/80'
                            : 'text-white/40'
                        )}>{cmd.description}</p>
                      </div>
                      <ChevronRight className={cn('w-4 h-4 flex-shrink-0',
                        selectedIndex === getGlobalIndex(category, i, filteredCommands)
                          ? 'text-cosmic-primary'
                          : 'text-white/20'
                      )} />
                    </motion.button>
                  ))}
                </motion.div>
              ))}
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="p-8 text-center text-white/40"
            >
              <Terminal className="w-12 h-12 mx-auto mb-4 opacity-20" />
              <p>No commands found for "{query}"</p>
              <p className="text-xs mt-1">Try a different search term</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Hints */}
        <div className="px-4 py-3 border-t border-cosmic-border/50">
          <div className="flex flex-wrap gap-4 text-[11px] text-white/30 font-mono">
            <span>↑↓ Navigate</span>
            <span>⏎ Execute</span>
            <span>Esc Close</span>
            <span>⌘K Reopen</span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

function groupCommandsByCategory(cmds: typeof COMMANDS) {
  const groups = new Map<string, typeof COMMANDS>()
  cmds.forEach(cmd => {
    if (!groups.has(cmd.category)) groups.set(cmd.category, [])
    groups.get(cmd.category)!.push(cmd)
  })
  return Array.from(groups.entries())
}

function getGlobalIndex(category: string, index: number, allCmds: typeof COMMANDS) {
  let count = 0
  for (const cmd of allCmds) {
    if (cmd.category === category) {
      if (index === 0) return count
      index--
    }
    count++
  }
   return -1
}