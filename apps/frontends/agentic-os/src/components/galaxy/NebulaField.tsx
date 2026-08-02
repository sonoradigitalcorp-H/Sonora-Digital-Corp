import { useMemo } from 'react'
import { Points, BufferGeometry } from 'three'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { GalaxyConfig } from '@/types'

interface NebulaFieldProps {
  config: GalaxyConfig
  phase: string
}

export function NebulaField({ config, phase }: NebulaFieldProps) {
  const particleCount = phase === 'MACRO_VIEW' ? 200 : config.particleCount
  
  const particles = useMemo(() => {
    const positions = new Float32Array(particleCount * 3)
    const sizes = new Float32Array(particleCount)
    const colors = new Float32Array(particleCount * 3)
    const alphas = new Float32Array(particleCount)
    const velocities = new Float32Array(particleCount * 3)
    
    const color = new THREE.Color(config.color)
    const secondaryColor = new THREE.Color(config.secondaryColor)
    
    for (let i = 0; i < particleCount; i++) {
      // Distribute in galaxy disk shape
      const radius = 5 + Math.random() * 60
      const theta = Math.random() * Math.PI * 2
      const phi = (Math.random() - 0.5) * Math.PI * 0.5 // Flattened disk
      
      positions[i * 3] = radius * Math.cos(phi) * Math.cos(theta) + config.position[0]
      positions[i * 3 + 1] = radius * Math.sin(phi) + config.position[1]
      positions[i * 3 + 2] = radius * Math.cos(phi) * Math.sin(theta) + config.position[2]
      
      sizes[i] = 0.5 + Math.random() * 2
      
      const t = Math.random()
      colors[i * 3] = color.r * (1 - t) + secondaryColor.r * t
      colors[i * 3 + 1] = color.g * (1 - t) + secondaryColor.g * t
      colors[i * 3 + 2] = color.b * (1 - t) + secondaryColor.b * t
      
      alphas[i] = 0.2 + Math.random() * 0.5
      
      // Orbital velocity
      const speed = (0.1 + Math.random() * 0.2) / radius
      velocities[i * 3] = -Math.sin(theta) * speed
      velocities[i * 3 + 1] = 0
      velocities[i * 3 + 2] = Math.cos(theta) * speed
    }
    
    return { positions, sizes, colors, alphas, velocities }
  }, [particleCount, config])

  // We can't easily animate buffer attributes in R3F without custom hooks
  // For now, render static nebula - animation would need a custom component

  return (
    <Points>
      <BufferGeometry>
        <bufferAttribute attach="attributes-position" count={particleCount} array={particles.positions} itemSize={3} />
        <bufferAttribute attach="attributes-size" count={particleCount} array={particles.sizes} itemSize={1} />
        <bufferAttribute attach="attributes-color" count={particleCount} array={particles.colors} itemSize={3} />
        <bufferAttribute attach="attributes-alpha" count={particleCount} array={particles.alphas} itemSize={1} />
      </BufferGeometry>
      <PointsMaterial
        size={2}
        vertexColors
        transparent
        opacity={0.6}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </Points>
  )
}