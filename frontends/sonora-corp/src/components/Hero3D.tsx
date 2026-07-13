"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

export default function Hero3D() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const particles = new THREE.BufferGeometry();
    const count = 2000;
    const pos = new Float32Array(count * 3);
    const sizes = new Float32Array(count);
    for (let i = 0; i < count * 3; i++) {
      pos[i] = (Math.random() - 0.5) * 20;
      if (i % 3 === 2) pos[i] = (Math.random() - 0.5) * 10;
    }
    for (let i = 0; i < count; i++) sizes[i] = Math.random() * 3 + 1;
    particles.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    particles.setAttribute("size", new THREE.BufferAttribute(sizes, 1));

    const texCanvas = document.createElement("canvas");
    texCanvas.width = 32;
    texCanvas.height = 32;
    const ctx = texCanvas.getContext("2d")!;
    const grd = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
    grd.addColorStop(0, "rgba(139,92,246,1)");
    grd.addColorStop(0.5, "rgba(139,92,246,0.5)");
    grd.addColorStop(1, "rgba(139,92,246,0)");
    ctx.fillStyle = grd;
    ctx.fillRect(0, 0, 32, 32);
    const texture = new THREE.CanvasTexture(texCanvas);

    const material = new THREE.PointsMaterial({
      map: texture,
      size: 0.08,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      color: new THREE.Color("#8b5cf6"),
      opacity: 0.6,
    });
    const particleSystem = new THREE.Points(particles, material);
    scene.add(particleSystem);

    const torusGeo = new THREE.TorusKnotGeometry(0.6, 0.25, 100, 16);
    const torusMat = new THREE.MeshPhysicalMaterial({
      color: new THREE.Color("#8b5cf6"),
      metalness: 0.3,
      roughness: 0.2,
      transparent: true,
      opacity: 0.3,
      wireframe: true,
    });
    const torus = new THREE.Mesh(torusGeo, torusMat);
    torus.position.y = 0.5;
    scene.add(torus);

    camera.position.z = 8;
    let mouseX = 0,
      mouseY = 0;
    document.addEventListener("mousemove", (e) => {
      mouseX = (e.clientX / window.innerWidth) * 2 - 1;
      mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
    });

    let animId = 0;
    function animate() {
      animId = requestAnimationFrame(animate);
      particleSystem.rotation.x += 0.0003;
      particleSystem.rotation.y += 0.0005;
      particleSystem.rotation.x += (mouseY * 0.05 - particleSystem.rotation.x) * 0.01;
      particleSystem.rotation.y += (mouseX * 0.05 - particleSystem.rotation.y) * 0.01;
      torus.rotation.x += 0.005;
      torus.rotation.y += 0.01;
      renderer.render(scene, camera);
    }
    animate();

    const resize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener("resize", resize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
      renderer.dispose();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        zIndex: 0,
        pointerEvents: "none",
      }}
    />
  );
}
