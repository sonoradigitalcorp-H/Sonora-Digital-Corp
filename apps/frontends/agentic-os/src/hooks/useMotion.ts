import { useMotionValue, useSpring, useTransform, useAnimationFrame, useReducedMotion } from 'framer-motion'
import { gsap } from 'gsap'
import { useEffect, useRef, useCallback } from 'react'

export function useCosmicSpring(initial = 0, stiffness = 100, damping = 20) {
  const value = useMotionValue(initial)
  const spring = useSpring(value, { stiffness, damping, restDelta: 0.001 })
  return [value, spring] as const
}

export function useOrbitalMotion(radius: number, speed: number, offset = 0) {
  const time = useMotionValue(0)
  const x = useTransform(time, t => Math.cos(t * speed + offset) * radius)
  const z = useTransform(time, t => Math.sin(t * speed + offset) * radius)
  
  useAnimationFrame((t) => {
    time.set(t / 1000)
  })

  return { x, z, time }
}

export function useNeuralPulse(intensity = 1, speed = 1) {
  const pulse = useMotionValue(0)
  const animated = useSpring(pulse, { stiffness: 200, damping: 20 })
  
  useAnimationFrame((t) => {
    const val = Math.sin(t * 0.001 * speed) * intensity
    pulse.set(val)
  })

  return animated
}

export function useGalaxyTransition(from: number, to: number, duration = 1000) {
  const progress = useMotionValue(from)
  const spring = useSpring(progress, { stiffness: 300, damping: 30 })
  
  const trigger = useCallback(() => {
    progress.set(to)
  }, [progress, to])

  return { progress: spring, trigger }
}

export function useGSAP() {
  const ctxRef = useRef<gsap.Context | null>(null)
  
  const getContext = useCallback(() => {
    if (!ctxRef.current) {
      ctxRef.current = gsap.context(() => {})
    }
    return ctxRef.current
  }, [])

  const animate = useCallback((target: gsap.TweenTarget, vars: gsap.TweenVars) => {
    return gsap.to(target, vars)
  }, [])

  const timeline = useCallback(() => {
    return gsap.timeline()
  }, [])

  const killAll = useCallback(() => {
    ctxRef.current?.revert()
    ctxRef.current = null
  }, [])

  useEffect(() => {
    return () => {
      ctxRef.current?.revert()
    }
  }, [])

  return { animate, timeline, killAll, getContext }
}

export function useParallax(strength = 1) {
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      const centerX = window.innerWidth / 2
      const centerY = window.innerHeight / 2
      x.set((e.clientX - centerX) / centerX * strength)
      y.set((e.clientY - centerY) / centerY * strength)
    }
    
    window.addEventListener('mousemove', handler)
    return () => window.removeEventListener('mousemove', handler)
  }, [x, y, strength])

  return { x, y }
}

export function useScrollProgress() {
  const progress = useMotionValue(0)
  
  useEffect(() => {
    const handler = () => {
      const scrollTop = window.scrollY
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      progress.set(scrollTop / docHeight)
    }
    
    window.addEventListener('scroll', handler, { passive: true })
    return () => window.removeEventListener('scroll', handler)
  }, [progress])

  return progress
}

export function useStaggeredAnimation(delay = 0.1) {
  const refs = useRef<(HTMLElement | null)[]>([])
  
  const addRef = useCallback((index: number) => (el: HTMLElement | null) => {
    refs.current[index] = el
  }, [])

  const animateIn = useCallback((vars: gsap.TweenVars = {}) => {
    const elements = refs.current.filter(Boolean) as HTMLElement[]
    gsap.fromTo(elements, 
      { opacity: 0, y: 30, scale: 0.95 },
      { opacity: 1, y: 0, scale: 1, duration: 0.6, stagger: delay, ease: 'power3.out', ...vars }
    )
  }, [delay])

  const animateOut = useCallback((vars: gsap.TweenVars = {}) => {
    const elements = refs.current.filter(Boolean) as HTMLElement[]
    gsap.to(elements, { opacity: 0, y: -20, scale: 0.95, duration: 0.3, stagger: delay * 0.5, ease: 'power2.in', ...vars })
  }, [delay])

  return { addRef, animateIn, animateOut, refs }
}

export function useMagneticHover(strength = 0.3) {
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const ref = useRef<HTMLElement | null>(null)
  
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    x.set((e.clientX - centerX) / (rect.width / 2) * strength * 20)
    y.set((e.clientY - centerY) / (rect.height / 2) * strength * 20)
  }, [x, y, strength])

  const handleMouseLeave = useCallback(() => {
    x.set(0)
    y.set(0)
  }, [x, y])

  const animatedX = useSpring(x, { stiffness: 300, damping: 30 })
  const animatedY = useSpring(y, { stiffness: 300, damping: 30 })

  return { ref, animatedX, animatedY, handleMouseMove, handleMouseLeave }
}

export function useTextReveal() {
  const ref = useRef<HTMLDivElement>(null)
  const animated = useMotionValue(0)
  const spring = useSpring(animated, { stiffness: 200, damping: 20 })
  
  useEffect(() => {
    if (!ref.current) return
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animated.set(1)
        }
      })
    }, { threshold: 0.1 })
    
    observer.observe(ref.current)
    return () => observer.disconnect()
  }, [animated])

  return { ref, animated: spring }
}