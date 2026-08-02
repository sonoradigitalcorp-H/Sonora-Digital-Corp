import { motion, AnimatePresence } from 'framer-motion'
import { ChevronLeft, ChevronRight, Brain, Users, Bot, Cpu, TrendingUp, DollarSign, X, Settings, Sparkles, Zap, Search, Mic, Menu } from 'lucide-react'
import { cn } from '@/lib/utils/helpers'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Avatar, Badge } from '@/components/ui/Badge'
import { useGalaxy } from '@/contexts/GalaxyContext'
import { useJARVIS } from '@/contexts/JARVISContext'
import { useTenant } from '@/contexts/TenantContext'
import { GALAXY_CONFIGS } from '@/types'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
  galaxies: typeof GALAXY_CONFIGS[keyof typeof GALAXY_CONFIGS][]
  activeTenant: string
}

export function Sidebar({ isOpen, onToggle, galaxies, activeTenant }: SidebarProps) {
  const { currentGalaxy, phase, enterGalaxy, exitGalaxy } = useGalaxy()
  const { status: jarvisStatus, mode, connectWebSocket, disconnectWebSocket } = useJARVIS()
  const { tenants, setActiveTenant } = useTenant()

  const currentTenant = tenants.find(t => t.tenant_id === activeTenant)

  return (
    <>
      {/* Overlay for mobile */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-30 bg-black/50 lg:hidden"
            onClick={onToggle}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={{ x: -300 }}
        animate={{ x: isOpen ? 0 : -300 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        className={cn(
          'fixed left-0 top-0 bottom-16 z-40 w-72 lg:w-80 bg-cosmic-bgSecondary border-r border-cosmic-border flex flex-col',
          'shadow-[0_0_40px_-10px_rgb(124_92_252_/_0.1)]'
        )}
      >
        {/* Header */}
        <div className="p-4 border-b border-cosmic-border flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-primary to-cosmic-gold flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-cosmic-bg" />
            </div>
            <div>
              <h1 className="font-bold text-white text-lg">Sonora OS</h1>
              <p className="text-xs text-white/40">Agentic Dashboard</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onToggle} className="lg:hidden">
            <ChevronLeft className="w-5 h-5" />
          </Button>
        </div>

        {/* JARVIS Status */}
        <div className="p-4 border-b border-cosmic-border/50">
          <div className="flex items-center gap-3 mb-3">
            <div className={cn('w-8 h-8 rounded-xl flex items-center justify-center text-sm',
              jarvisStatus === 'listening' && 'bg-green-500/20 animate-pulse',
              jarvisStatus === 'thinking' && 'bg-cyan-500/20',
              jarvisStatus === 'speaking' && 'bg-purple-500/20',
              jarvisStatus === 'executing' && 'bg-orange-500/20',
              'bg-cosmic-card'
            )}>
              {jarvisStatus === 'listening' && '🎤'}
              {jarvisStatus === 'thinking' && '🧠'}
              {jarvisStatus === 'speaking' && '🔊'}
              {jarvisStatus === 'executing' && '⚡'}
              {jarvisStatus === 'offline' && '⭘'}
              {jarvisStatus === 'initializing' && '⟳'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-white text-sm">JARVIS</p>
              <p className="text-xs text-white/50 capitalize">{jarvisStatus} • {mode}</p>
            </div>
            <Badge variant="cosmic" size="sm" dot>{mode}</Badge>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" className="flex-1" onClick={() => connectWebSocket(activeTenant)}>
              <Zap className="w-4 h-4 mr-1" /> Connect
            </Button>
            <Button variant="ghost" size="sm" onClick={disconnectWebSocket}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Tenant Selector */}
        <div className="p-4 border-b border-cosmic-border/50">
          <p className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3">Active Tenant</p>
          <div className="space-y-2">
            {tenants.map(tenant => (
              <Button
                key={tenant.tenant_id}
                variant={activeTenant === tenant.tenant_id ? 'primary' : 'ghost'}
                size="sm"
                className="w-full justify-start gap-3"
                onClick={() => setActiveTenant(tenant.tenant_id)}
              >
                <Avatar name={tenant.name} size="sm" status={tenant.status === 'active' ? 'online' : tenant.status === 'provisioning' ? 'away' : 'offline'} />
                <div className="flex-1 min-w-0 text-left">
                  <p className="font-medium text-sm truncate">{tenant.name}</p>
                  <p className="text-xs text-white/40 truncate">{tenant.tenant_id}</p>
                </div>
                <Badge variant={tenant.status === 'active' ? 'success' : tenant.status === 'provisioning' ? 'warning' : 'danger'} size="sm">
                  {tenant.status}
                </Badge>
              </Button>
            ))}
          </div>
        </div>

        {/* Galaxy Navigator */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <p className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3">Galaxies</p>
          
          {galaxies.map(galaxy => {
            const config = GALAXY_CONFIGS[galaxy.id]
            const isActive = currentGalaxy === galaxy.id
            const isInGalaxy = phase !== 'MACRO_VIEW'
            
            return (
              <Button
                key={galaxy.id}
                variant={isActive ? 'primary' : 'ghost'}
                size="sm"
                className={cn('w-full justify-start gap-3', isInGalaxy && !isActive && 'opacity-50')}
                onClick={() => isActive ? exitGalaxy() : enterGalaxy(galaxy.id)}
                disabled={isInGalaxy && !isActive}
              >
                <span className="w-8 h-8 rounded-xl bg-gradient-to-br flex items-center justify-center text-lg">
                  {config.icon}
                </span>
                <div className="flex-1 min-w-0 text-left">
                  <p className="font-medium text-sm truncate">{config.name}</p>
                  <p className="text-xs text-white/40 truncate">{config.descriptionShort}</p>
                </div>
                {isActive && <Zap className="w-4 h-4 text-cosmic-primary animate-pulse" />}
              </Button>
            )
          })}

          {/* Quick Actions */}
          <div className="pt-4 border-t border-cosmic-border/50">
            <p className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3">Quick Actions</p>
            <div className="grid grid-cols-2 gap-2">
              <Button variant="ghost" size="sm" className="h-auto py-3 flex flex-col items-start gap-1">
                <Search className="w-5 h-5" />
                <span className="text-xs">Search</span>
              </Button>
              <Button variant="ghost" size="sm" className="h-auto py-3 flex flex-col items-start gap-1">
                <Mic className="w-5 h-5" />
                <span className="text-xs">Voice</span>
              </Button>
              <Button variant="ghost" size="sm" className="h-auto py-3 flex flex-col items-start gap-1">
                <Settings className="w-5 h-5" />
                <span className="text-xs">Settings</span>
              </Button>
              <Button variant="ghost" size="sm" className="h-auto py-3 flex flex-col items-start gap-1">
                <Terminal className="w-5 h-5" />
                <span className="text-xs">Terminal</span>
              </Button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-cosmic-border">
          <div className="flex items-center gap-3">
            <Avatar name="Mystic" size="sm" status="online" />
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm truncate">Mystic</p>
              <p className="text-xs text-white/40">Founder & CEO</p>
            </div>
          </div>
        </div>
      </motion.aside>
    </>
  )
}