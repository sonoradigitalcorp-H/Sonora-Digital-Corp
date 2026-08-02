import { useMemo, useRef } from 'react'
import { Group, Mesh, PointLight } from 'three'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface PlanetOrbitProps {
  planet: { 
    id: string
    name: string
    type: string
    position: [number, number, number]
    data: { type: string; status: string; mcpCount: number }
  }
  galaxyColor: string
  orbitRadius: number
  orbitSpeed: number
  isSelected: boolean
}

export function PlanetOrbit({ planet, galaxyColor, orbitRadius, orbitSpeed, isSelected }: PlanetOrbitProps) {
  const groupRef = useRef<Group>(null)
  const planetRef = useRef<Mesh>(null)
  const angleRef = useRef(Math.random() * Math.PI * 2)

  const planetGeometry = useMemo(() => new THREE.SphereGeometry(2.5, 24, 24), [])
  
  const statusColors: Record<string, string> = {
    operational: '#22c55e',
    degraded: '#f59e0b',
    down: '#ef4444',
  }
  
  const planetColor = statusColors[planet.data.status] || galaxyColor
  
  const planetMaterial = useMemo(() => new THREE.MeshPhysicalMaterial({
    color: planetColor,
    emissive: planetColor,
    emissiveIntensity: isSelected ? 0.6 : 0.3,
    roughness: 0.3,
    metalness: 0.6,
    transparent: true,
    opacity: 0.9,
  }), [planetColor, isSelected])

  const ringGeometry = useMemo(() => new THREE.RingGeometry(orbitRadius - 0.2, orbitRadius + 0.2, 64), [orbitRadius])
  const ringMaterial = useMemo(() => new THREE.MeshBasicMaterial({
    color: galaxyColor,
    transparent: true,
    opacity: isSelected ? 0.3 : 0.1,
    side: 2,
    depthWrite: false,
  }), [galaxyColor, isSelected])

  useFrame((_, delta) => {
    angleRef.current += delta * orbitSpeed
    const x = Math.cos(angleRef.current) * orbitRadius
    const z = Math.sin(angleRef.current) * orbitRadius
    const y = Math.sin(angleRef.current * 0.5) * 2
    
    if (planetRef.current) {
      planetRef.current.position.set(x, y, z)
      planetRef.current.rotation.y += delta * 0.5
    }
  })

  return (
    <Group ref={groupRef}>
      {/* Orbit ring */}
      <Mesh
        geometry={ringGeometry}
        material={ringMaterial}
        rotationX={-Math.PI / 2}
      />
      
      {/* Planet */}
      <Mesh
        ref={planetRef}
        geometry={planetGeometry}
        material={planetMaterial}
        onClick={() => {}}
        userData={{ 
          type: 'planet', 
          id: planet.id, 
          name: planet.name, 
          data: planet.data 
        }}
      >
        {isSelected && <PointLight color={galaxyColor} intensity={1} distance={15} decay={2} />}
      </Mesh>
    </Group>
  )
}