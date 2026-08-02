import { Menu, Search, Bell, Moon, Sun, ChevronDown, Zap, Bot, Globe, Users, Cpu, TrendingUp, Brain, Settings, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils/helpers'
import { Button } from '@/components/ui/Button'
import { Avatar, Badge } from '@/components/ui/Badge'
import { useTenant } from '@/contexts/TenantContext'
import { useGalaxy } from '@/contexts/GalaxyContext'
import { GALAXY_CONFIGS } from '@/types'

interface TopBarProps {
  activeTenant: string
  onTenantChange: (tenantId: string) => void
  onJarvisClick: () => void
  onCommandPalette: () => void
  jarvisOpen: boolean
}

export function TopBar({ activeTenant, onTenantChange, onJarvisClick, onCommandPalette, jarvisOpen }: TopBarProps) {
  const { tenants } = useTenant()
  const { phase, currentGalaxy } = useGalaxy()

  const currentTenant = tenants.find(t => t.tenant_id === activeTenant)

  return (
    <header className="fixed top-0 left-0 right-0 z-30 h-16 bg-cosmic-bg/80 backdrop-blur-xl border-b border-white/5 flex items-center px-6 lg:pl-80">
      <div className="w-full max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Left: Menu + Brand + Galaxy Context */}
        <div className="flex items-center gap-4 min-w-0">
          <Button variant="ghost" size="sm" className="lg:hidden" onClick={() => {}}>
            <Menu className="w-5 h-5" />
          </Button>

          <div className="hidden lg:flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cosmic-primary to-cosmic-gold flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-cosmic-bg" />
            </div>
            <div>
              <h1 className="font-bold text-white text-lg">Sonora OS</h1>
              <p className="text-xs text-white/40">Agentic Dashboard</p>
            </div>
          </div>

          {/* Galaxy Phase Indicator */}
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 cosmic-card rounded-xl">
            <span className="w-2 h-2 rounded-full bg-cosmic-primary animate-pulse" />
            <span className="text-xs font-mono text-cosmic-primary uppercase tracking-wider">
              {phase === 'MACRO_VIEW' ? 'COSMIC VIEW' : 
               phase === 'GALAXY_ENTER' ? 'ENTERING...' :
               currentGalaxy ? GALAXY_CONFIGS[currentGalaxy as keyof typeof GALAXY_CONFIGS]?.name : 'NAVIGATING'}
            </span>
          </div>
        </div>

        {/* Center: Global Search */}
        <div className="flex-1 max-w-xl mx-8 hidden lg:block">
          <Button 
            variant="ghost" 
            className="w-full justify-start gap-3 px-4 py-2 hover:bg-cosmic-border/50"
            onClick={onCommandPalette}
          >
            <Search className="w-5 h-5 text-white/40" />
            <span className="text-white/50 font-mono text-sm">Search or command... (⌘K)</span>
            <kbd className="px-2 py-0.5 text-[10px] font-mono text-white/30 bg-cosmic-bg rounded ml-auto">⌘K</kbd>
          </Button>
        </div>

        {/* Right: Notifications, JARVIS, Tenant, User */}
        <div className="flex items-center gap-2">
          {/* Notifications */}
          <Button variant="ghost" size="sm" className="relative">
            <Bell className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-[10px] font-bold rounded-full flex items-center justify-center">3</span>
          </Button>

          {/* JARVIS Toggle */}
          <Button 
            variant={jarvisOpen ? 'primary' : 'ghost'} 
            size="sm" 
            className="hidden sm:flex items-center gap-2"
            onClick={onJarvisClick}
          >
            <Bot className="w-5 h-5" />
            <span className="font-medium">JARVIS</span>
          </Button>

          {/* Tenant Selector */}
          <div className="relative hidden lg:block">
            <Button 
              variant="secondary" 
              size="sm" 
              className="flex items-center gap-2 min-w-[200px] justify-between"
              onClick={() => {}} // Dropdown would go here
            >
              <Avatar name={currentTenant?.name || 'Tenant'} size="sm" status={currentTenant?.status === 'active' ? 'online' : 'away'} />
              <div className="text-left min-w-0 flex-1">
                <p className="font-medium text-sm truncate">{currentTenant?.name || 'Select Tenant'}</p>
                <p className="text-xs text-white/40 truncate">{activeTenant}</p>
              </div>
              <ChevronDown className="w-4 h-4 text-white/40" />
            </Button>
          </div>

          {/* User Menu */}
          <div className="relative">
            <Button variant="ghost" size="sm" className="flex items-center gap-2">
              <Avatar name="Mystic" size="sm" status="online" />
              <span className="hidden sm:block font-medium text-sm">Mystic</span>
              <ChevronDown className="w-4 h-4 text-white/40 hidden sm:block" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}