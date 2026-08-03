import { Suspense, useEffect, useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Stars } from '@react-three/drei'
import * as THREE from 'three'
import { GalaxyNavigator } from '@/components/galaxy/GalaxyNavigator'
import { GalaxyProvider } from '@/contexts/GalaxyContext'
import { JARVISProvider } from '@/contexts/JARVISContext'
import { TenantProvider } from '@/contexts/TenantContext'
import { MotionProvider } from '@/contexts/MotionContext'
import { JARVISInterface } from '@/components/jarvis/JARVISInterface'
import { CommandPalette } from '@/components/jarvis/CommandPalette'
import { Sidebar } from '@/components/layout/Sidebar'
import { TopBar } from '@/components/layout/TopBar'
import { PhaseTransition } from '@/components/layout/PhaseTransition'
import { AgentDashboard } from '@/components/agents/AgentDashboard'
import { GALAXY_CONFIGS } from '@/types'

const GALAXIES = Object.values(GALAXY_CONFIGS)

function GalaxyCore({ config, isActive }: { config: typeof GALAXY_CONFIGS[keyof typeof GALAXY_CONFIGS]; isActive: boolean }) {
  const coreRef = useRef<THREE.Mesh>(null)
  const timeRef = useRef(0)

  useFrame((_, delta) => {
    timeRef.current += delta
    if (coreRef.current) {
      coreRef.current.rotation.y = timeRef.current * config.rotationSpeed * 0.5
      coreRef.current.rotation.x = Math.sin(timeRef.current * 0.1) * 0.05
    }
  })

  return (
    <THREE.Group position={config.position}>
      <THREE.Mesh
        ref={coreRef}
        geometry={new THREE.IcosahedronGeometry(8, 1)}
        material={new THREE.MeshPhysicalMaterial({
          color: config.color,
          emissive: config.color,
          emissiveIntensity: isActive ? 0.5 : 0.2,
          roughness: 0.2,
          metalness: 0.8,
          transparent: true,
          opacity: 0.8,
        })}
      />
      <THREE.PointLight color={config.color} intensity={isActive ? 2 : 0.5} distance={100} decay={2} />
    </THREE.Group>
  )
}

function AppContent() {
  const [jarvisOpen, setJarvisOpen] = useState(false)
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [activeTenant, setActiveTenant] = useState('abe-music')
  const [agentDashboardOpen, setAgentDashboardOpen] = useState(true)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setCommandPaletteOpen(true)
      }
      if (e.key === 'Escape') {
        setCommandPaletteOpen(false)
        setJarvisOpen(false)
      }
      if (e.key === '`') {
        e.preventDefault()
        setJarvisOpen(!jarvisOpen)
      }
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'a') {
        e.preventDefault()
        setAgentDashboardOpen(!agentDashboardOpen)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [jarvisOpen])

  return (
    <div className="relative w-full h-screen overflow-hidden">
      {/* Three.js Canvas - Full Screen */}
      <div className="absolute inset-0 z-0">
        <Canvas
          camera={{ position: [0, 0, 200], fov: 50, near: 0.1, far: 10000 }}
          gl={{ antialias: true, alpha: true, preserveDrawingBuffer: false }}
          onCreated={({ gl }) => {
            gl.setPixelRatio(Math.min(window.devicePixelRatio, 2))
            gl.outputEncoding = 3000
          }}
        >
          <THREE.Fog attach="fog" args={["#0a0a0f", 100, 5000]} />
          
          {/* Global starfield */}
          <Stars radius={5000} depth={1000} count={2000} factor={4} saturation={0} fade speed={0.5} />
          
          {/* All galaxies in macro view */}
          {GALAXIES.map(galaxy => (
            <GalaxyCore key={galaxy.id} config={galaxy} isActive={false} />
          ))}
        </Canvas>
      </div>

      {/* UI Overlay */}
      <div className="relative z-10 w-full h-screen flex flex-col">
        <TopBar 
          activeTenant={activeTenant}
          onTenantChange={setActiveTenant}
          onJarvisClick={() => setJarvisOpen(!jarvisOpen)}
          onCommandPalette={() => setCommandPaletteOpen(true)}
          onAgentToggle={() => setAgentDashboardOpen(!agentDashboardOpen)}
          jarvisOpen={jarvisOpen}
          agentDashboardOpen={agentDashboardOpen}
        />

        <div className="flex-1 flex overflow-hidden">
          <Sidebar 
            isOpen={sidebarOpen}
            onToggle={() => setSidebarOpen(!sidebarOpen)}
            galaxies={GALAXIES}
            activeTenant={activeTenant}
          />

          <main className="flex-1 relative overflow-hidden">
            {agentDashboardOpen ? (
              <AgentDashboard />
            ) : (
              <GalaxyNavigator 
                galaxies={GALAXIES}
                onObjectSelect={(obj) => console.log('Selected:', obj)}
              />
            )}
          </main>
        </div>

        <PhaseTransition />
      </div>

      {jarvisOpen && (
        <JARVISInterface 
          onClose={() => setJarvisOpen(false)}
          tenantId={activeTenant}
        />
      )}

      {commandPaletteOpen && (
        <CommandPalette 
          onClose={() => setCommandPaletteOpen(false)}
          onCommand={(cmd) => console.log('Command:', cmd)}
        />
      )}
    </div>
  )
}

export default function App() {
  return (
    <GalaxyProvider>
      <JARVISProvider>
        <TenantProvider>
          <MotionProvider>
            <AppContent />
          </MotionProvider>
        </TenantProvider>
      </JARVISProvider>
    </GalaxyProvider>
  )
}