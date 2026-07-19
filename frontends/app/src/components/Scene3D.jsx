import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Float, MeshDistortMaterial, Environment, Stars } from '@react-three/drei'

function CoreGeometry({ mouse }) {
  const mesh = useRef()
  const time = useRef(0)

  useFrame((state, delta) => {
    time.current += delta
    const t = time.current
    mesh.current.rotation.x = Math.sin(t * 0.1) * 0.1 + mouse.y * 0.3
    mesh.current.rotation.y = Math.sin(t * 0.15) * 0.1 + mouse.x * 0.3
    mesh.current.position.y = Math.sin(t * 0.2) * 0.3
  })

  return (
    <mesh ref={mesh}>
      <icosahedronGeometry args={[2, 1]} />
      <MeshDistortMaterial
        color="#7c5cfc"
        emissive="#5a3cd4"
        emissiveIntensity={0.4}
        roughness={0.2}
        metalness={0.8}
        distort={0.3}
        speed={2}
        transparent
        opacity={0.85}
      />
    </mesh>
  )
}

function OrbitingRing({ radius, color, speed, offset = 0 }) {
  const ref = useRef()

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() * speed + offset
    ref.current.position.x = Math.cos(t) * radius
    ref.current.position.z = Math.sin(t) * radius
    ref.current.position.y = Math.sin(t * 0.5) * 0.5
  })

  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.08, 8, 8]} />
      <meshBasicMaterial color={color} />
    </mesh>
  )
}

function ParticleField({ count = 200 }) {
  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 30
      pos[i * 3 + 1] = (Math.random() - 0.5) * 30
      pos[i * 3 + 2] = (Math.random() - 0.5) * 30
    }
    return pos
  }, [count])

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.05}
        color="#7c5cfc"
        transparent
        opacity={0.6}
        sizeAttenuation
      />
    </points>
  )
}

export default function Scene3D({ className = '' }) {
  const mouse = useRef({ x: 0, y: 0 })

  const handleMouse = (e) => {
    mouse.current.x = (e.clientX / window.innerWidth - 0.5) * 2
    mouse.current.y = -(e.clientY / window.innerHeight - 0.5) * 2
  }

  return (
    <div
      className={`absolute inset-0 pointer-events-none ${className}`}
      onMouseMove={handleMouse}
    >
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={0.8} color="#7c5cfc" />
        <pointLight position={[-10, -5, -10]} intensity={0.4} color="#c8a87c" />
        <Stars radius={100} depth={50} count={1000} factor={4} saturation={0} fade speed={1} />
        <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
          <CoreGeometry mouse={mouse} />
        </Float>
        {[3, 4.5, 6].map((r, i) => (
          <OrbitingRing key={i} radius={r} color={['#7c5cfc', '#c8a87c', '#22c55e'][i]} speed={0.3 + i * 0.1} offset={i * 2} />
        ))}
        <ParticleField count={300} />
        <Environment preset="city" />
      </Canvas>
    </div>
  )
}
