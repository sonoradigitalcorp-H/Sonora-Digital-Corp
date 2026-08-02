import { Suspense, useMemo } from 'react'
import { Canvas } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import { GalaxyConfig } from '@/types'
import { GALAXY_CONFIGS } from '@/types'

interface NeuraGalaxyProps {
  config: GalaxyConfig
  phase: string
}

export function NeuraGalaxy({ config, phase }: NeuraGalaxyProps) {
  const neuralCore = useMemo(() => {
    const positions = new Float32Array(1000 * 3)
    const connections = new Uint16Array(2000 * 2)
    
    // Generate neural lattice
    for (let i = 0; i < 1000; i++) {
      const radius = 2 + Math.random() * 8
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      
      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
      positions[i * 3 + 2] = radius * Math.cos(phi)
    }
    
    // Create connections (simplified)
    for (let i = 0; i < 2000; i++) {
      connections[i * 2] = Math.floor(Math.random() * 1000)
      connections[i * 2 + 1] = Math.floor(Math.random() * 1000)
    }
    
    return { positions, connections }
  }, [])

  return (
    <group position={config.position}>
      {/* Neural lattice core */}
      <NeuralLattice positions={neuralCore.positions} connections={neuralCore.connections} color={config.color} />
      
      {/* Engram orbit rings */}
      <EngramOrbits color={config.color} secondaryColor={config.secondaryColor} />
      
      {/* RAG Nebulae */}
      <RAGNebulae color={config.color} secondaryColor={config.secondaryColor} />
      
      {/* Insight pulsars */}
      <InsightPulsars color={config.color} />
    </group>
  )
}

function NeuralLattice({ positions, connections, color }: { positions: Float32Array; connections: Uint16Array; color: string }) {
  const timeRef = useRef(0)
  
  useFrame((_, delta) => {
    timeRef.current += delta
  })

  return (
    <>
      {/* Nodes */}
      <Points>
        <BufferGeometry>
          <bufferAttribute attach="attributes-position" count={positions.length / 3} array={positions} itemSize={3} />
        </BufferGeometry>
        <PointsMaterial
          size={0.15}
          color={color}
          transparent
          opacity={0.8}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
        />
      </Points>
      
      {/* Synapses */}
      <LineSegments>
        <BufferGeometry>
          <bufferAttribute attach="attributes-position" count={connections.length} array={positions} itemSize={3} />
          <bufferAttribute attach="index" array={connections} itemSize={1} />
        </BufferGeometry>
        <LineBasicMaterial
          color={color}
          transparent
          opacity={0.15}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </LineSegments>
    </>
  )
}

function EngramOrbits({ color, secondaryColor }: { color: string; secondaryColor: string }) {
  const layers = 7
  
  return (
    <group>
      {Array.from({ length: layers }, (_, i) => (
        <Mesh
          key={i}
          geometry={new THREE.RingGeometry(12 + i * 2.5, 12 + i * 2.5 + 0.3, 128)}
          material={new THREE.MeshBasicMaterial({
            color: i % 2 === 0 ? color : secondaryColor,
            transparent: true,
            opacity: 0.1 + (i / layers) * 0.15,
            side: 2,
            depthWrite: false,
          })}
          rotationX={-Math.PI / 2}
          userData={{ type: 'engram-layer', layer: i }}
        />
      ))}
    </group>
  )
}

function RAGNebulae({ color, secondaryColor }: { color: string; secondaryColor: string }) {
  return (
    <group>
      {[1, 2, 3].map((_, i) => (
        <Mesh
          key={i}
          geometry={new THREE.SphereGeometry(25 + i * 15, 16, 16)}
          material={new THREE.MeshBasicMaterial({
            color: i % 2 === 0 ? color : secondaryColor,
            transparent: true,
            opacity: 0.03,
            side: 1, // Backside for volumetric feel
            depthWrite: false,
          })}
          scale={[1, 0.5, 1]}
          userData={{ type: 'rag-nebula', collection: `collection-${i}` }}
        />
      ))}
    </group>
  )
}

function InsightPulsars({ color }: { color: string }) {
  return (
    <group>
      {Array.from({ length: 5 }, (_, i) => (
        <Mesh
          key={i}
          geometry={new THREE.OctahedronGeometry(0.3, 0)}
          material={new THREE.MeshBasicMaterial({
            color,
            transparent: true,
            opacity: 0.9,
          })}
          position={[
            (Math.random() - 0.5) * 40,
            (Math.random() - 0.5) * 40,
            (Math.random() - 0.5) * 40,
          ]}
          userData={{ type: 'insight-pulsar', adr: `ADR-${2024}-${String(i).padStart(3, '0')}` }}
        />
      ))}
    </group>
  )
}

// Need imports
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Points, LineSegments, Mesh, BufferGeometry, LineBasicMaterial, group } from 'three'
import * as THREE from 'three'
import { bufferAttribute } from 'three'