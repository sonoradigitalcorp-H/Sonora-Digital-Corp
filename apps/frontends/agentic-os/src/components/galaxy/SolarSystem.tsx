import { useMemo } from 'react'
import { Group, Mesh, Object3D } from 'three'
import { useFrame } from '@react-three/fiber'
import { Planet as PlanetType, ServiceData, MCPServerData } from '@/types'
import { PlanetOrbit } from './PlanetOrbit'
import { MCPMoon } from './MCPMoon'

interface SolarSystemProps {
  galaxyConfig: { color: string; secondaryColor: string }
  selectedObject: PlanetType | null
}

export function SolarSystem({ galaxyConfig, selectedObject }: SolarSystemProps) {
  const starRef = useRef<Group>(null)
  const timeRef = useRef(0)

  // Mock tenant data as star system
  const tenants = useMemo(() => [
    {
      id: 'abe-music',
      name: 'ABE Music',
      position: [0, 0, 0] as [number, number, 0],
      color: '#22c55e',
      services: [
        { id: 'svc-1', name: 'API Gateway', type: 'api', status: 'operational', position: [18, 0, 0] as [number, number, number], mcpCount: 2 },
        { id: 'svc-2', name: 'Frontend', type: 'frontend', status: 'operational', position: [-18, 0, 0] as [number, number, number], mcpCount: 1 },
        { id: 'svc-3', name: 'Worker', type: 'worker', status: 'operational', position: [0, 18, 0] as [number, number, number], mcpCount: 0 },
        { id: 'svc-4', name: 'PostgreSQL', type: 'database', status: 'operational', position: [0, -18, 0] as [number, number, number], mcpCount: 0 },
        { id: 'svc-5', name: 'Redis', type: 'cache', status: 'operational', position: [12, 12, 0] as [number, number, number], mcpCount: 0 },
      ],
      mcps: [
        { id: 'mcp-1', name: 'Social Media MCP', type: 'social', status: 'healthy', position: [25, 5, 0] as [number, number, number] },
        { id: 'mcp-2', name: 'Analytics MCP', type: 'analytics', status: 'healthy', position: [25, -5, 0] as [number, number, number] },
      ]
    },
    {
      id: 'aztrotech',
      name: 'Aztrotech',
      position: [60, 20, 10] as [number, number, number],
      color: '#06b6d4',
      services: [
        { id: 'svc-1', name: 'API Gateway', type: 'api', status: 'operational', position: [15, 0, 0] as [number, number, number], mcpCount: 1 },
        { id: 'svc-2', name: 'Frontend', type: 'frontend', status: 'operational', position: [-15, 0, 0] as [number, number, number], mcpCount: 0 },
        { id: 'svc-3', name: 'Worker', type: 'worker', status: 'degraded', position: [0, 15, 0] as [number, number, number], mcpCount: 0 },
        { id: 'svc-4', name: 'PostgreSQL', type: 'database', status: 'operational', position: [0, -15, 0] as [number, number, number], mcpCount: 0 },
      ],
      mcps: [
        { id: 'mcp-1', name: 'Invoice MCP', type: 'invoice', status: 'healthy', position: [22, 0, 0] as [number, number, number] },
      ]
    },
    {
      id: 'hermosillo-contabilidad',
      name: 'Hermosillo Contabilidad',
      position: [-50, -30, -20] as [number, number, number],
      color: '#f59e0b',
      services: [],
      mcps: []
    }
  ], [])

  useFrame((_, delta) => {
    timeRef.current += delta
    if (starRef.current) {
      starRef.current.rotation.y = timeRef.current * 0.005
    }
  })

  return (
    <Group ref={starRef}>
      {tenants.map(tenant => (
        <TenantStarSystem
          key={tenant.id}
          tenant={tenant}
          galaxyColor={galaxyConfig.color}
          galaxySecondaryColor={galaxyConfig.secondaryColor}
          isSelected={selectedObject?.id === tenant.id}
        />
      ))}
    </Group>
  )
}

function TenantStarSystem({ tenant, galaxyColor, galaxySecondaryColor, isSelected }: {
  tenant: { 
    id: string; 
    name: string; 
    position: [number, number, number]; 
    color: string; 
    services: Array<{ 
      id: string; 
      name: string; 
      type: string; 
      status: string; 
      position: [number, number, number]; 
      mcpCount: number 
    }>; 
    mcps: Array<{ 
      id: string; 
      name: string; 
      type: string; 
      status: string; 
      position: [number, number, number] 
    }> 
  }
  galaxyColor: string
  galaxySecondaryColor: string
  isSelected: boolean
}) {
  const groupRef = useRef<Group>(null)
  const timeRef = useRef(0)

  useFrame((_, delta) => {
    timeRef.current += delta
    if (groupRef.current) {
      groupRef.current.rotation.y = timeRef.current * 0.002
    }
  })

  return (
    <Group ref={groupRef} position={tenant.position}>
      {/* Star (Tenant) */}
      <Mesh
        geometry={new THREE.SphereGeometry(6, 32, 32)}
        material={new THREE.MeshPhysicalMaterial({
          color: tenant.color,
          emissive: tenant.color,
          emissiveIntensity: isSelected ? 0.8 : 0.4,
          roughness: 0.2,
          metalness: 0.8,
          transparent: true,
          opacity: 0.9,
        })}
        onClick={() => {}}
        userData={{ type: 'star', id: tenant.id, name: tenant.name, data: { status: 'active', services: tenant.services.length, mcps: tenant.mcps.length } }}
      >
        <PointLight color={tenant.color} intensity={isSelected ? 2 : 1} distance={50} decay={2} />
      </Mesh>

      {/* Selection ring */}
      {isSelected && (
        <Mesh
          geometry={new THREE.RingGeometry(8, 9, 32)}
          material={new THREE.MeshBasicMaterial({
            color: galaxyColor,
            transparent: true,
            opacity: 0.5,
            side: 2,
          })}
          rotationX={-Math.PI / 2}
        />
      )}

      {/* Service Planets */}
      {tenant.services.map((service, i) => (
        <PlanetOrbit
          key={service.id}
          planet={{
            id: service.id,
            name: service.name,
            type: 'planet',
            position: service.position,
            data: { type: service.type, status: service.status, mcpCount: service.mcpCount }
          }}
          galaxyColor={galaxyColor}
          orbitRadius={Math.sqrt(service.position[0]**2 + service.position[1]**2)}
          orbitSpeed={0.3 + i * 0.1}
          isSelected={selectedObject?.id === service.id}
        />
      ))}

      {/* MCP Moons */}
      {tenant.mcps.map((mcp, i) => (
        <MCPMoon
          key={mcp.id}
          moon={{
            id: mcp.id,
            name: mcp.name,
            type: 'moon',
            position: mcp.position,
            data: { type: mcp.type, status: mcp.status }
          }}
          galaxyColor={galaxySecondaryColor}
          isSelected={selectedObject?.id === mcp.id}
        />
      ))}
    </Group>
  )
}

// Imports
import * as THREE from 'three'
import { useRef } from 'react'
import { Group, useFrame } from '@react-three/fiber'
import { useGalaxy } from '@/contexts/GalaxyContext'

// Actually, let me fix this - the SolarSystem needs to receive selectedObject as prop