import { useMemo, useRef } from 'react'
import { Mesh, PointLight } from 'three'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface MCPMoonProps {
  moon: {
    id: string
    name: string
    type: string
    position: [number, number, number]
    data: { type: string; status: string }
  }
  galaxyColor: string
  isSelected: boolean
}

export function MCPMoon({ moon, galaxyColor, isSelected }: MCPMoonProps) {
  const moonRef = useRef<Mesh>(null)
  const angleRef = useRef(Math.random() * Math.PI * 2)
  const timeRef = useRef(0)

  const moonGeometry = useMemo(() => new THREE.SphereGeometry(0.8, 16, 16), [])
  
  const statusColors: Record<string, string> = {
    healthy: '#22c55e',
    degraded: '#f59e0b',
    down: '#ef4444',
  }
  
  const moonColor = statusColors[moon.data.status] || galaxyColor
  
  const moonMaterial = useMemo(() => new THREE.MeshPhysicalMaterial({
    color: moonColor,
    emissive: moonColor,
    emissiveIntensity: isSelected ? 0.8 : 0.4,
    roughness: 0.2,
    metalness: 0.9,
    transparent: true,
    opacity: 0.9,
  }), [moonColor, isSelected])

  useFrame((_, delta) => {
    timeRef.current += delta
    // Small orbital wobble around parent planet position
    if (moonRef.current) {
      moonRef.current.rotation.y += delta
      moonRef.current.position.y = moon.position[1] + Math.sin(timeRef.current * 2) * 0.3
    }
  })

  return (
    <Mesh
      ref={moonRef}
      position={moon.position}
      geometry={moonGeometry}
      material={moonMaterial}
      onClick={() => {}}
      userData={{ 
        type: 'moon', 
        id: moon.id, 
        name: moon.name, 
        data: { ...moon.data, mcpType: moon.type }
      }}
    >
      {isSelected && <PointLight color={galaxyColor} intensity={0.5} distance={8} decay={2} />}
    </Mesh>
  )
}