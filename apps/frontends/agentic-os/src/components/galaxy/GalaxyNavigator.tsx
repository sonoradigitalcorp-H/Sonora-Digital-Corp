import { useMemo } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Stars, Html } from '@react-three/drei'
import { Galaxy, GalaxyObject } from '@/types'
import { GalaxyCore } from './GalaxyCore'
import { SolarSystem } from './SolarSystem'
import { Planet } from './Planet'
import { NebulaField } from './NebulaField'
import { PostProcessing } from './PostProcessing'
import { useGalaxyNavigator } from '@/hooks/useGalaxyNavigator'
import { GALAXY_CONFIGS } from '@/types'

interface GalaxyNavigatorProps {
  galaxies: Galaxy[]
  onObjectSelect?: (object: GalaxyObject) => void
}

export function GalaxyNavigator({ galaxies, onObjectSelect }: GalaxyNavigatorProps) {
  const {
    phase,
    currentGalaxy,
    cameraPosition,
    cameraTarget,
    isTransitioning,
    selectedObject,
    getConfig,
  } = useGalaxyNavigator()

  const currentConfig = currentGalaxy ? getConfig(currentGalaxy) : null

  return (
    <div className="relative w-full h-full">
      <Canvas
        camera={{
          position: cameraPosition,
          fov: 50,
          near: 0.1,
          far: 10000,
        }}
        gl={{ antialias: true, alpha: true, preserveDrawingBuffer: false }}
        onCreated={({ gl }) => {
          gl.setPixelRatio(Math.min(window.devicePixelRatio, 2))
          gl.outputEncoding = 3000 // sRGBEncoding
        }}
      >
        <fog attach="fog" args={["#0a0a0f", 100, 5000]} />
        
        {/* Global starfield */}
        <Stars radius={5000} depth={1000} count={2000} factor={4} saturation={0} fade speed={0.5} />
        
        {/* Render all galaxies in macro view */}
        {phase === 'MACRO_VIEW' && galaxies.map(galaxy => (
          <GalaxyCore
            key={galaxy.id}
            config={GALAXY_CONFIGS[galaxy.id]}
            isActive={false}
            onClick={() => {}}
          />
        ))}

        {/* Render active galaxy in detail */}
        {phase !== 'MACRO_VIEW' && currentConfig && (
          <>
            <GalaxyCore
              config={currentConfig}
              isActive={true}
              phase={phase}
              selectedObject={selectedObject}
            />
            {phase === 'SOLAR_SYSTEM' && (
              <SolarSystem galaxyConfig={currentConfig} selectedObject={selectedObject} />
            )}
            {phase === 'PLANET_SURFACE' && selectedObject && (
              <Planet planet={selectedObject} galaxyColor={currentConfig.color} />
            )}
            <NebulaField config={currentConfig} phase={phase} />
          </>
        )}

        {/* Post-processing effects */}
        <PostProcessing 
          intensity={phase !== 'MACRO_VIEW' ? 1.2 : 0.5}
          chromaticAberration={isTransitioning ? 0.02 : 0}
        />
      </Canvas>

      {/* HUD Overlay */}
      <GalaxyHUD 
        phase={phase} 
        currentGalaxy={currentGalaxy} 
        selectedObject={selectedObject}
        onBack={phase !== 'MACRO_VIEW' ? () => {} : undefined}
      />
    </div>
  )
}

function GalaxyHUD({ phase, currentGalaxy, selectedObject, onBack }: {
  phase: string
  currentGalaxy: string | null
  selectedObject: GalaxyObject | null
  onBack?: () => void
}) {
  const configs = GALAXY_CONFIGS
  
  if (phase === 'MACRO_VIEW') return null

  const config = currentGalaxy ? configs[currentGalaxy as keyof typeof configs] : null

  return (
    <div className="fixed inset-0 pointer-events-none p-6">
      <div className="max-w-7xl mx-auto h-full flex flex-col justify-between">
        {/* Top Bar */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="cosmic-button-secondary px-4 py-2 gap-2"
              style={{ opacity: onBack ? 1 : 0.3, pointerEvents: onBack ? 'auto' : 'none' }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="hidden sm:inline">Back to Cosmos</span>
            </button>
            
            {config && (
              <div className="flex items-center gap-3 px-4 py-2 cosmic-card">
                <span className="text-2xl">{config.icon}</span>
                <div>
                  <p className="font-bold text-white">{config.name}</p>
                  <p className="text-xs text-white/50">{config.descriptionShort}</p>
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center gap-4">
            <PhaseIndicator phase={phase} />
            <PerformanceIndicator />
          </div>
        </div>

        {/* Bottom Context Panel */}
        {selectedObject && (
          <div className="cosmic-card p-4 max-w-md mx-auto animate-slide-up">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-cosmic-primary/20 flex items-center justify-center">
                {getObjectIcon(selectedObject.type)}
              </div>
              <div>
                <p className="font-semibold text-white">{selectedObject.name}</p>
                <p className="text-xs text-white/50 capitalize">{selectedObject.type}</p>
              </div>
            </div>
            {selectedObject.data && Object.keys(selectedObject.data).length > 0 && (
              <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                {Object.entries(selectedObject.data).map(([key, value]) => (
                  <div key={key} className="cosmic-bg rounded-lg p-2">
                    <p className="text-white/40">{key}</p>
                    <p className="font-mono text-white">{String(value)}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function PhaseIndicator({ phase }: { phase: string }) {
  const labels: Record<string, string> = {
    MACRO_VIEW: 'COSMIC VIEW',
    GALAXY_ENTER: 'ENTERING GALAXY',
    SOLAR_SYSTEM: 'SOLAR SYSTEM',
    PLANET_SURFACE: 'PLANET SURFACE',
    MOON_DETAIL: 'MOON DETAIL',
  }

  return (
    <div className="cosmic-card px-3 py-1.5 flex items-center gap-2">
      <span className="w-2 h-2 rounded-full bg-cosmic-primary animate-pulse" />
      <span className="text-xs font-mono text-cosmic-primary uppercase tracking-wider">
        {labels[phase] || phase}
      </span>
    </div>
  )
}

function PerformanceIndicator() {
  // In real app, connect to actual FPS monitor
  return (
    <div className="cosmic-card px-3 py-1.5 flex items-center gap-2">
      <span className="w-2 h-2 rounded-full bg-green-400" />
      <span className="text-xs font-mono text-green-400">60 FPS</span>
    </div>
  )
}

function getObjectIcon(type: string) {
  const icons: Record<string, React.ReactNode> = {
    galaxy: '🌌',
    star: '☀️',
    planet: '🪐',
    moon: '🌙',
    nebula: '☁️',
    pulsar: '✨',
    asteroid: '☄️',
  }
  return icons[type] || '⬤'
}