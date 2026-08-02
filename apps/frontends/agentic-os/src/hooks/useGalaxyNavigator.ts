import { useState, useEffect, useCallback, useRef } from 'react'
import type { GalaxyId, GalaxyPhase, GalaxyConfig } from '@/types'
import { GALAXY_CONFIGS } from '@/types'
import * as THREE from 'three'

export function useGalaxyNavigator() {
  const [phase, setPhase] = useState<GalaxyPhase>('MACRO_VIEW')
  const [currentGalaxy, setCurrentGalaxy] = useState<GalaxyId | null>(null)
  const [cameraPosition, setCameraPosition] = useState<[number, number, number]>([0, 0, 200])
  const [cameraTarget, setCameraTarget] = useState<[number, number, number]>([0, 0, 0])
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [selectedObject, setSelectedObject] = useState<{ id: string; type: string; data: unknown } | null>(null)
  
  const transitionTimeoutRef = useRef<ReturnType<typeof setTimeout>>()

  const getConfig = useCallback((galaxyId: GalaxyId): GalaxyConfig => GALAXY_CONFIGS[galaxyId], [])

  const lerpVector3 = useCallback((start: THREE.Vector3, end: THREE.Vector3, factor: number) => {
    return new THREE.Vector3().lerpVectors(start, end, factor)
  }, [])

  const enterGalaxy = useCallback((galaxyId: GalaxyId) => {
    setIsTransitioning(true)
    setCurrentGalaxy(galaxyId)
    setPhase('GALAXY_ENTER')
    
    const config = GALAXY_CONFIGS[galaxyId]
    const targetPos: [number, number, number] = [
      config.position[0],
      config.position[1],
      config.position[2] + 50
    ]
    
    animateCamera(targetPos, config.position, 2000)
    
    transitionTimeoutRef.current = setTimeout(() => {
      setPhase('SOLAR_SYSTEM')
      setIsTransitioning(false)
    }, 2000)
  }, [])

  const exitGalaxy = useCallback(() => {
    setIsTransitioning(true)
    setPhase('MACRO_VIEW')
    
    animateCamera([0, 0, 200], [0, 0, 0], 1500)
    
    transitionTimeoutRef.current = setTimeout(() => {
      setCurrentGalaxy(null)
      setSelectedObject(null)
      setIsTransitioning(false)
    }, 1500)
  }, [])

  const enterSolarSystem = useCallback((star: { id: string; position: [number, number, number] }) => {
    setPhase('SOLAR_SYSTEM')
    setSelectedObject(star)
    animateCamera(
      [star.position[0], star.position[1], star.position[2] + 30],
      star.position,
      1000
    )
  }, [])

  const selectPlanet = useCallback((planet: { id: string; position: [number, number, number]; data: unknown }) => {
    setPhase('PLANET_SURFACE')
    setSelectedObject(planet)
    animateCamera(
      [planet.position[0], planet.position[1], planet.position[2] + 15],
      planet.position,
      800
    )
  }, [])

  const selectMoon = useCallback((moon: { id: string; position: [number, number, number]; data: unknown }) => {
    setPhase('MOON_DETAIL')
    setSelectedObject(moon)
    animateCamera(
      [moon.position[0], moon.position[1], moon.position[2] + 5],
      moon.position,
      500
    )
  }, [])

  const animateCamera = useCallback((targetPos: [number, number, number], targetLook: [number, number, number], duration: number) => {
    const startPos = cameraPosition
    const startTarget = cameraTarget
    const startTime = Date.now()
    
    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3) // easeOutCubic
      
      const newPos: [number, number, number] = [
        startPos[0] + (targetPos[0] - startPos[0]) * eased,
        startPos[1] + (targetPos[1] - startPos[1]) * eased,
        startPos[2] + (targetPos[2] - startPos[2]) * eased,
      ]
      
      const newTarget: [number, number, number] = [
        startTarget[0] + (targetLook[0] - startTarget[0]) * eased,
        startTarget[1] + (targetLook[1] - startTarget[1]) * eased,
        startTarget[2] + (targetLook[2] - startTarget[2]) * eased,
      ]
      
      setCameraPosition(newPos)
      setCameraTarget(newTarget)
      
      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }
    
    animate()
  }, [cameraPosition, cameraTarget])

  const setPhaseDirect = useCallback((newPhase: GalaxyPhase) => {
    setPhase(newPhase)
  }, [])

  useEffect(() => {
    return () => {
      if (transitionTimeoutRef.current) {
        clearTimeout(transitionTimeoutRef.current)
      }
    }
  }, [])

  return {
    phase,
    currentGalaxy,
    cameraPosition,
    cameraTarget,
    isTransitioning,
    selectedObject,
    getConfig,
    enterGalaxy,
    exitGalaxy,
    enterSolarSystem,
    selectPlanet,
    selectMoon,
    setPhase: setPhaseDirect,
  }
}