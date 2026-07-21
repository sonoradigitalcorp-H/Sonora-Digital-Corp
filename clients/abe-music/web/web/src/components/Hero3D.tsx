"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Center, Sparkles, Text } from "@react-three/drei";
import * as THREE from "three";

function ABELogo3D() {
  const meshRef = useRef<THREE.Mesh>(null!);
  useFrame((state) => {
    meshRef.current.rotation.y = state.clock.elapsedTime * 0.3;
    meshRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1;
  });

  return (
    <group>
      <mesh ref={meshRef}>
        <sphereGeometry args={[1.2, 32, 32]} />
        <meshBasicMaterial color="#c9a84c" transparent opacity={0.08} />
      </mesh>
      <Float speed={2} rotationIntensity={0.2} floatIntensity={0.5}>
        <Center>
          <Text fontSize={0.3} color="#c9a84c">
            ♪
          </Text>
        </Center>
      </Float>
    </group>
  );
}

function Particles() {
  const count = 100;
  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count * 3; i++) pos[i] = (Math.random() - 0.5) * 8;
    return pos;
  }, []);

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial size={0.03} color="#c9a84c" transparent opacity={0.6} />
    </points>
  );
}

export default function Hero3DScene() {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none">
      <Canvas camera={{ position: [0, 0, 3], fov: 45 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 5, 5]} intensity={0.8} />
        <pointLight position={[-2, 2, 2]} intensity={0.5} color="#c9a84c" />
        <Particles />
        <Sparkles count={50} scale={4} size={1} speed={0.3} color="#c9a84c" />
        <ABELogo3D />
      </Canvas>
    </div>
  );
}
