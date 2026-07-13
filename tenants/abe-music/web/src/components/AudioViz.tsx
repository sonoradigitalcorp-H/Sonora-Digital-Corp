"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

export default function AudioViz({ isActive, color = "#FFD700" }: { isActive: boolean; color?: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, canvas.clientWidth / canvas.clientHeight || 1, 0.1, 100);
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const bars: THREE.Mesh[] = [];
    const barCount = 32;
    const barGeo = new THREE.BoxGeometry(0.15, 1, 0.15);
    const c = new THREE.Color(color);
    const barMat = new THREE.MeshPhysicalMaterial({
      color: c,
      metalness: 0.3,
      roughness: 0.4,
      clearcoat: 0.3,
      emissive: c,
      emissiveIntensity: 0.1,
    });

    for (let i = 0; i < barCount; i++) {
      const bar = new THREE.Mesh(barGeo, barMat.clone());
      const angle = (i / barCount) * Math.PI * 2;
      const radius = 1.8;
      bar.position.x = Math.cos(angle) * radius;
      bar.position.z = Math.sin(angle) * radius;
      bar.lookAt(0, 0, 0);
      bar.userData = { angle, baseHeight: 0.3 + Math.random() * 0.5, speed: 0.5 + Math.random() };
      scene.add(bar);
      bars.push(bar);
    }

    camera.position.z = 4;
    camera.position.y = 0.5;
    camera.lookAt(0, 0, 0);

    let animId = 0;
    let time = 0;
    function animate() {
      time += 0.02;
      for (const bar of bars) {
        const ud = bar.userData as any;
        const height = isActive
          ? 0.3 + Math.abs(Math.sin(time * ud.speed + ud.angle)) * 2
          : ud.baseHeight;
        bar.scale.y = height;
        bar.position.y = height / 2;
      }
      camera.position.x = Math.sin(time * 0.2) * 0.3;
      camera.lookAt(0, 0, 0);
      renderer.render(scene, camera);
      animId = requestAnimationFrame(animate);
    }
    animate();

    const resize = () => {
      if (!canvas.parentElement) return;
      const w = canvas.parentElement.clientWidth;
      const h = 100;
      renderer.setSize(w, h);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    };
    window.addEventListener("resize", resize);
    setTimeout(resize, 100);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
      renderer.dispose();
    };
  }, [isActive, color]);

  return (
    <canvas
      ref={canvasRef}
      className="w-full rounded-lg"
      style={{ height: "100px", marginBottom: "0.5rem" }}
    />
  );
}
