import { GalaxyConfig } from '@/types'
import { GALAXY_CONFIGS } from '@/types'

interface ClientaraGalaxyProps {
  config: GalaxyConfig
  phase: string
  activeTenant: string
}

export function ClientaraGalaxy({ config, phase, activeTenant }: ClientaraGalaxyProps) {
  // This galaxy shows tenant star systems with service planets and MCP moons
  // Implementation would be similar to SolarSystem but focused on client view
  
  return (
    <group position={config.position}>
      <ClientaraCore config={config} activeTenant={activeTenant} />
      <TenantConstellations activeTenant={activeTenant} />
    </group>
  )
}

function ClientaraCore({ config, activeTenant }: { config: GalaxyConfig; activeTenant: string }) {
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

function TenantConstellations({ activeTenant }: { activeTenant: string }) {
  // Constellations connecting related tenants
  return <group />
}

// Imports
import { Mesh, PointLight, group } from 'three'