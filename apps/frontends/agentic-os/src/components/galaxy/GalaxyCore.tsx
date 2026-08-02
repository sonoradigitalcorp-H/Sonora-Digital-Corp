import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Mesh, Group, Points, PointLight, AmbientLight } from 'three'
import { GalaxyConfig } from '@/types'

interface GalaxyCoreProps {
  config: GalaxyConfig
  isActive: boolean
  phase?: string
  selectedObject?: { position: [number, number, number] } | null
}

export function GalaxyCore({ config, isActive, phase, selectedObject }: GalaxyCoreProps) {
  const groupRef = useRef<Group>(null)
  const coreRef = useRef<Mesh>(null)
  const timeRef = useRef(0)

  const coreGeometry = useMemo(() => {
    const geo = new THREE.IcosahedronGeometry(8, 2)
    return geo
  }, [])

  const coreMaterial = useMemo(() => {
    const mat = new THREE.MeshPhysicalMaterial({
      color: config.color,
      emissive: config.color,
      emissiveIntensity: isActive ? 0.6 : 0.3,
      roughness: 0.1,
      metalness: 0.9,
      transparent: true,
      opacity: 0.85,
      transmission: 0.3,
      thickness: 0.5,
      clearcoat: 1,
      clearcoatRoughness: 0.1,
    })
    return mat
  }, [config.color, isActive])

  const ringGeometries = useMemo(() => {
    return [15, 22, 30, 40].map(radius => 
      new THREE.RingGeometry(radius - 0.5, radius + 0.5, 64)
    )
  }, [])

  const ringMaterials = useMemo(() => {
    return ringGeometries.map((_, i) => new THREE.MeshBasicMaterial({
      color: config.color,
      transparent: true,
      opacity: 0.15 - i * 0.03,
      side: 2,
      depthWrite: false,
    }))
  }, [config.color, ringGeometries])

  const particleCount = isActive ? config.particleCount * 2 : config.particleCount
  const particles = useMemo(() => {
    const positions = new Float32Array(particleCount * 3)
    const sizes = new Float32Array(particleCount)
    const colors = new Float32Array(particleCount * 3)
    const color = new THREE.Color(config.color)
    const secondaryColor = new THREE.Color(config.secondaryColor)
    
    for (let i = 0; i < particleCount; i++) {
      const radius = 10 + Math.random() * 50
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      
      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
      positions[i * 3 + 2] = radius * Math.cos(phi)
      
      sizes[i] = 0.1 + Math.random() * 0.3
      
      const t = Math.random()
      colors[i * 3] = color.r * (1 - t) + secondaryColor.r * t
      colors[i * 3 + 1] = color.g * (1 - t) + secondaryColor.g * t
      colors[i * 3 + 2] = color.b * (1 - t) + secondaryColor.b * t
    }
    
    return { positions, sizes, colors }
  }, [particleCount, config.color, config.secondaryColor])

  useFrame((state, delta) => {
    timeRef.current += delta
    const t = timeRef.current

    if (groupRef.current) {
      groupRef.current.rotation.y = t * config.rotationSpeed * 0.5
      groupRef.current.rotation.x = Math.sin(t * 0.1) * 0.05
    }

    if (coreRef.current) {
      coreRef.current.rotation.x = t * config.rotationSpeed * 0.3
      coreRef.current.rotation.y = t * config.rotationSpeed * 0.5
      coreRef.current.scale.setScalar(1 + Math.sin(t * 0.5) * 0.02)
      
      if (coreRef.current.material) {
        const mat = coreRef.current.material as THREE.MeshPhysicalMaterial
        mat.emissiveIntensity = isActive ? 0.6 + Math.sin(t * 2) * 0.1 : 0.3
      }
    }

    // Animate rings
    groupRef.current?.children.forEach((child, i) => {
      if (child instanceof Mesh && child.geometry.type === 'RingGeometry') {
        child.rotation.z = t * (0.1 + i * 0.05) * (i % 2 === 0 ? 1 : -1)
        child.rotation.x = Math.sin(t * 0.2) * 0.2
      }
    })
  })

  return (
    <Group ref={groupRef} position={config.position}>
      {/* Core neural lattice */}
      <Mesh
        ref={coreRef}
        geometry={coreGeometry}
        material={coreMaterial}
      />
      
      {/* Orbital rings */}
      {ringGeometries.map((geo, i) => (
        <Mesh
          key={`ring-${i}`}
          geometry={geo}
          material={ringMaterials[i]}
          rotationX={-Math.PI / 2}
        />
      ))}

      {/* Particle field */}
      <Points>
        <BufferGeometry>
          <bufferAttribute attach="attributes-position" count={particleCount} array={particles.positions} itemSize={3} />
          <bufferAttribute attach="attributes-size" count={particleCount} array={particles.sizes} itemSize={1} />
          <bufferAttribute attach="attributes-color" count={particleCount} array={particles.colors} itemSize={3} />
        </BufferGeometry>
        <PointsMaterial
          size={1}
          vertexColors
          transparent
          opacity={0.7}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
        />
      </Points>

      {/* Central glow */}
      <PointLight color={config.color} intensity={isActive ? 3 : 1.5} distance={100} decay={2} />
      <PointLight color={config.secondaryColor} intensity={1} distance={200} decay={2} position={[20, 20, 20]} />
    </Group>
  )
}

// Need to import THREE
import * as THREE from 'three'
import { BufferGeometry, PointsMaterial, bufferAttribute } from 'three'