import { useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import type { Mesh, Points, BufferGeometry } from 'three'
import { GALAXY_CONFIGS } from '@/types'

interface DevopsaraGalaxyProps {
  config: typeof GALAXY_CONFIGS['devopsara']
  phase: string
}

export function DevopsaraGalaxy({ config, phase }: DevopsaraGalaxyProps) {
  const timeRef = useRef(0)

  const asteroidBelt = useMemo(() => {
    const positions = new Float32Array(1000 * 3)
    const velocities = new Float32Array(1000 * 3)
    
    for (let i = 0; i < 1000; i++) {
      const radius = 5 + Math.random() * 30
      const theta = Math.random() * Math.PI * 2
      const phi = (Math.random() - 0.5) * Math.PI * 0.3
      
      positions[i * 3] = radius * Math.cos(phi) * Math.cos(theta) + config.position[0]
      positions[i * 3 + 1] = radius * Math.sin(phi) + config.position[1]
      positions[i * 3 + 2] = radius * Math.cos(phi) * Math.sin(theta) + config.position[2]
      
      velocities[i * 3] = Math.cos(theta) * 0.02
      velocities[i * 3 + 1] = Math.sin(phi) * 0.01
      velocities[i * 3 + 2] = Math.sin(theta) * 0.02
    }
    
    return { positions, velocities }
  }, [])

  const deploymentRings = useMemo(() => {
    return [15, 25, 35, 45, 55].map(radius => new THREE.RingGeometry(radius, radius + 0.2, 128))
  }, [])

  useFrame((_, delta) => {
    timeRef.current += delta
  })

  return (
    <group position={config.position}>
      <mesh
        geometry={new THREE.IcosahedronGeometry(8, 2)}
        material={new THREE.MeshPhysicalMaterial({
          color: config.color,
          emissive: config.color,
          emissiveIntensity: 0.4,
          roughness: 0.1,
          metalness: 0.8,
          transparent: true,
          opacity: 0.8,
        })}
      />
      <pointLight color={config.color} intensity={2} distance={100} decay={2} />

      {deploymentRings.map((geo, i) => (
        <mesh
          key={i}
          geometry={geo}
          material={new THREE.MeshBasicMaterial({
            color: config.secondaryColor,
            transparent: true,
            opacity: 0.1 - i * 0.015,
            side: THREE.DoubleSide,
          })}
          rotationX={-Math.PI / 2}
        />
      ))}

      <points>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" count={asteroidBelt.positions.length / 3} array={asteroidBelt.positions} itemSize={3} />
          <bufferAttribute attach="attributes-velocity" count={asteroidBelt.velocities.length / 3} array={asteroidBelt.velocities} itemSize={3} />
        </bufferGeometry>
        <pointsMaterial
          size={0.2}
          color={config.secondaryColor}
          transparent
          opacity={0.6}
          sizeAttenuation
        />
      </points>
    </group>
  )
}

// Imports
import { useRef } from 'react'
