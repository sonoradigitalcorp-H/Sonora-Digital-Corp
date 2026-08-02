import { GalaxyConfig } from '@/types'
import { GALAXY_CONFIGS } from '@/types'

interface AgentaraGalaxyProps {
  config: GalaxyConfig
  phase: string
}

export function AgentaraGalaxy({ config, phase }: AgentaraGalaxyProps) {
  // Constellations = agent swarms, orbital paths = workflows
  
  return (
    <group position={config.position}>
      <AgentaraCore config={config} />
      <AgentConstellations />
      <WorkflowOrbits />
    </group>
  )
}

function AgentaraCore({ config }: { config: GalaxyConfig }) {
  return (
    <group>
      <Mesh
        geometry={new THREE.IcosahedronGeometry(10, 2)}
        material={new THREE.MeshPhysicalMaterial({
          color: config.color,
          emissive: config.color,
          emissiveIntensity: 0.5,
          roughness: 0.1,
          metalness: 0.9,
          transparent: true,
          opacity: 0.85,
        })}
      />
      <PointLight color={config.color} intensity={2} distance={150} decay={2} />
    </group>
  )
}

function AgentConstellations() {
  // Constellations where each star = agent, lines = communication
  return <group />
}

function WorkflowOrbits() {
  // Orbital paths showing workflow execution flows
  return <group />
}

// Imports
import { Mesh, PointLight, group } from 'three'