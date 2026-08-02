import { useMemo, useRef } from 'react'
import { Mesh, Group, PointLight, AmbientLight } from 'three'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface PlanetProps {
  planet: {
    id: string
    name: string
    type: string
    position: [number, number, number]
    data: Record<string, unknown>
  }
  galaxyColor: string
}

export function Planet({ planet, galaxyColor }: PlanetProps) {
  const groupRef = useRef<Group>(null)
  const planetRef = useRef<Mesh>(null)
  const timeRef = useRef(0)

  const planetGeometry = useMemo(() => new THREE.SphereGeometry(12, 64, 64), [])
  
  const planetMaterial = useMemo(() => new THREE.MeshPhysicalMaterial({
    color: galaxyColor,
    emissive: galaxyColor,
    emissiveIntensity: 0.2,
    roughness: 0.6,
    metalness: 0.3,
    transparent: true,
    opacity: 0.95,
    displacementScale: 0.5,
  }), [galaxyColor])

  // Generate procedural surface detail
  const detailGeometry = useMemo(() => {
    const geo = new THREE.IcosahedronGeometry(12.2, 3)
    const positions = geo.attributes.position
    const displaced = positions.clone()
    
    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i)
      const y = positions.getY(i)
      const z = positions.getZ(i)
      
      // Simple noise-based displacement
      const noise = Math.sin(x * 0.5) * Math.cos(y * 0.5) * Math.sin(z * 0.5) * 0.3
      const len = Math.sqrt(x * x + y * y + z * z)
      
      displaced.setXYZ(i, 
        x + (x / len) * noise,
        y + (y / len) * noise,
        z + (z / len) * noise
      )
    }
    
    geo.setAttribute('position', displaced)
    geo.computeVertexNormals()
    return geo
  }, [])

  const detailMaterial = useMemo(() => new THREE.MeshBasicMaterial({
    color: galaxyColor,
    transparent: true,
    opacity: 0.1,
    wireframe: true,
    depthWrite: false,
  }), [galaxyColor])

  useFrame((_, delta) => {
    timeRef.current += delta
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.02
    }
    if (planetRef.current) {
      planetRef.current.rotation.y += delta * 0.05
    }
  })

  return (
    <Group ref={groupRef} position={planet.position}>
      {/* Planet surface */}
      <Mesh
        ref={planetRef}
        geometry={planetGeometry}
        material={planetMaterial}
      >
        <PointLight color={galaxyColor} intensity={1} distance={40} decay={2} />
      </Mesh>

      {/* Atmosphere/Detail wireframe */}
      <Mesh
        geometry={detailGeometry}
        material={detailMaterial}
      />

      {/* Status indicator at pole */}
      <Mesh
        geometry={new THREE.ConeGeometry(0.5, 2, 8)}
        material={new THREE.MeshBasicMaterial({
          color: '#22c55e',
          transparent: true,
          opacity: 0.8,
        })}
        position={[0, 13, 0]}
        rotationX={Math.PI}
      />
    </Group>
  )
}