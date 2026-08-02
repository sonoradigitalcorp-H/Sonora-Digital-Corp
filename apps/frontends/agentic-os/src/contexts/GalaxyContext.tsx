import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import type { GalaxyState, GalaxyId, GalaxyPhase, GalaxyObject, GALAXY_CONFIGS } from '@/types'
import { GALAXY_CONFIGS as CONFIGS } from '@/types'

interface GalaxyContextValue extends GalaxyState {
  enterGalaxy: (galaxyId: GalaxyId) => void
  exitGalaxy: () => void
  enterSolarSystem: (star: GalaxyObject) => void
  exitSolarSystem: () => void
  selectPlanet: (planet: GalaxyObject) => void
  selectMoon: (moon: GalaxyObject) => void
  setPhase: (phase: GalaxyPhase) => void
  getConfig: (galaxyId: GalaxyId) => typeof CONFIGS[GalaxyId]
}

const GalaxyContext = createContext<GalaxyContextValue | null>(null)

export function GalaxyProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<GalaxyState>({
    currentGalaxy: null,
    phase: 'MACRO_VIEW',
    selectedObject: null,
    cameraPosition: [0, 0, 200],
    cameraTarget: [0, 0, 0],
    isTransitioning: false,
  })

  const enterGalaxy = useCallback((galaxyId: GalaxyId) => {
    setState(prev => ({
      ...prev,
      currentGalaxy: galaxyId,
      phase: 'GALAXY_ENTER',
      isTransitioning: true,
    }))
    // Transition to solar system after animation
    setTimeout(() => {
      setState(prev => ({
        ...prev,
        phase: 'SOLAR_SYSTEM',
        isTransitioning: false,
      }))
    }, 2000)
  }, [])

  const exitGalaxy = useCallback(() => {
    setState(prev => ({
      ...prev,
      phase: 'MACRO_VIEW',
      currentGalaxy: null,
      selectedObject: null,
      isTransitioning: true,
    }))
    setTimeout(() => {
      setState(prev => ({
        ...prev,
        isTransitioning: false,
        cameraPosition: [0, 0, 200],
        cameraTarget: [0, 0, 0],
      }))
    }, 1500)
  }, [])

  const enterSolarSystem = useCallback((star: GalaxyObject) => {
    setState(prev => ({
      ...prev,
      phase: 'SOLAR_SYSTEM',
      selectedObject: star,
    }))
  }, [])

  const exitSolarSystem = useCallback(() => {
    setState(prev => ({
      ...prev,
      phase: 'GALAXY_ENTER',
      selectedObject: null,
    }))
  }, [])

  const selectPlanet = useCallback((planet: GalaxyObject) => {
    setState(prev => ({
      ...prev,
      phase: 'PLANET_SURFACE',
      selectedObject: planet,
    }))
  }, [])

  const selectMoon = useCallback((moon: GalaxyObject) => {
    setState(prev => ({
      ...prev,
      phase: 'MOON_DETAIL',
      selectedObject: moon,
    }))
  }, [])

  const setPhase = useCallback((phase: GalaxyPhase) => {
    setState(prev => ({ ...prev, phase }))
  }, [])

  const getConfig = useCallback((galaxyId: GalaxyId) => CONFIGS[galaxyId], [])

  return (
    <GalaxyContext.Provider value={{ ...state, enterGalaxy, exitGalaxy, enterSolarSystem, exitSolarSystem, selectPlanet, selectMoon, setPhase, getConfig }}>
      {children}
    </GalaxyContext.Provider>
  )
}

export function useGalaxy() {
  const context = useContext(GalaxyContext)
  if (!context) throw new Error('useGalaxy must be used within GalaxyProvider')
  return context
}