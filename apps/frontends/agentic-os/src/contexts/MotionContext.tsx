import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'

interface MotionContextValue {
  reducedMotion: boolean
  performanceTier: 'high' | 'medium' | 'low'
  particleQuality: 'high' | 'medium' | 'low'
  enablePostProcessing: boolean
  enableShadows: boolean
  targetFPS: number
  setReducedMotion: (value: boolean) => void
  setPerformanceTier: (tier: 'high' | 'medium' | 'low') => void
}

const MotionContext = createContext<MotionContextValue | null>(null)

export function MotionProvider({ children }: { children: ReactNode }) {
  const [reducedMotion, setReducedMotion] = useState(false)
  const [performanceTier, setPerformanceTier] = useState<'high' | 'medium' | 'low'>('high')
  const [particleQuality, setParticleQuality] = useState<'high' | 'medium' | 'low'>('high')
  const [enablePostProcessing, setEnablePostProcessing] = useState(true)
  const [enableShadows, setEnableShadows] = useState(true)
  const [targetFPS, setTargetFPS] = useState(60)

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReducedMotion(mediaQuery.matches)
    const handler = (e: MediaQueryListEvent) => setReducedMotion(e.matches)
    mediaQuery.addEventListener('change', handler)
    return () => mediaQuery.removeEventListener('change', handler)
  }, [])

  useEffect(() => {
    // Auto-detect performance tier
    const canvas = document.createElement('canvas')
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl')
    if (gl) {
      const renderer = gl.getParameter(gl.RENDERER)
      const vendor = gl.getParameter(gl.VENDOR)
      console.log('[Motion] GPU:', renderer, vendor)
      
      // Simple heuristic
      const isIntegrated = renderer.toLowerCase().includes('intel') || renderer.toLowerCase().includes('apple')
      if (isIntegrated) {
        setPerformanceTier('medium')
        setParticleQuality('medium')
      }
    }
  }, [])

  return (
    <MotionContext.Provider value={{ reducedMotion, performanceTier, particleQuality, enablePostProcessing, enableShadows, targetFPS, setReducedMotion, setPerformanceTier }}>
      {children}
    </MotionContext.Provider>
  )
}

export function useMotion() {
  const context = useContext(MotionContext)
  if (!context) throw new Error('useMotion must be used within MotionProvider')
  return context
}