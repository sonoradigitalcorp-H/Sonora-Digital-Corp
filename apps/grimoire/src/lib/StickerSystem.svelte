<script>
  import { onMount, onDestroy } from "svelte";
  import * as THREE from "three";

  export let tenantColors = {
    "sonora-digital": { primary: 0xC8924B, secondary: 0xE0AD6E, accent: 0xa8b589 },
    "abe-music": { primary: 0xFF6B35, secondary: 0xf97316, accent: 0xfbbf24 },
    "aztrotech": { primary: 0x00d4ff, secondary: 0x0ea5e9, accent: 0x7c3aed },
    "nathy-conta": { primary: 0x0f1b4d, secondary: 0xc9a84c, accent: 0xffffff },
    "el-joyero": { primary: 0xd4a030, secondary: 0x8b6914, accent: 0xf5e6c8 },
    "mds-corp": { primary: 0x7c3aed, secondary: 0xa855f7, accent: 0x22d3ee },
    "default": { primary: 0xC8924B, secondary: 0xE0AD6E, accent: 0xa8b589 },
  };

  export let activeTenant = "sonora-digital";
  export let audioLevel = 0;

  let container;
  let scene, camera, renderer;
  let stickers = [];
  let clock = 0;
  let animId;

  // SDC Brand Stickers (geometric symbols)
  const BRAND_STICKERS = [
    { id: "star", shape: "star", label: "Mystic Star", sizes: 0.3 },
    { id: "triangle", shape: "triangle", label: "Fire", sizes: 0.25 },
    { id: "circle", shape: "circle", label: "Air", sizes: 0.2 },
    { id: "diamond", shape: "diamond", label: "Premium", sizes: 0.22 },
    { id: "infinity", shape: "infinity", label: "Eternal", sizes: 0.35 },
    { id: "hexagon", shape: "hexagon", label: "Shield", sizes: 0.28 },
    { id: "bolt", shape: "bolt", label: "Speed", sizes: 0.2 },
    { id: "drop", shape: "drop", label: "Data", sizes: 0.18 },
  ];

  onMount(() => {
    initScene();
    buildStickers();
    animate();
  });

  onDestroy(() => {
    if (animId) cancelAnimationFrame(animId);
    if (renderer) {
      renderer.dispose();
      if (renderer.domElement.parentNode) renderer.domElement.parentNode.removeChild(renderer.domElement);
    }
  });

  function getColors() {
    return tenantColors[activeTenant] || tenantColors["default"];
  }

  function initScene() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 100);
    camera.position.set(0, 0, 8);
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);
    window.addEventListener("resize", onResize);
  }

  function buildShape(shape, color, size) {
    const mat = new THREE.MeshBasicMaterial({
      color: color,
      transparent: true,
      opacity: 0.6,
      side: THREE.DoubleSide,
      wireframe: false,
    });
    const glowMat = new THREE.MeshBasicMaterial({
      color: color,
      transparent: true,
      opacity: 0.08,
      side: THREE.DoubleSide,
    });

    let mesh, glow;

    switch(shape) {
      case "star": {
        const shape2d = new THREE.Shape();
        const spikes = 5;
        const outerR = size;
        const innerR = size * 0.4;
        for (let i = 0; i < spikes * 2; i++) {
          const r = i % 2 === 0 ? outerR : innerR;
          const angle = (i * Math.PI) / spikes - Math.PI / 2;
          if (i === 0) shape2d.moveTo(Math.cos(angle) * r, Math.sin(angle) * r);
          else shape2d.lineTo(Math.cos(angle) * r, Math.sin(angle) * r);
        }
        shape2d.closePath();
        const geo = new THREE.ShapeGeometry(shape2d);
        mesh = new THREE.Mesh(geo, mat);
        glow = new THREE.Mesh(geo.clone(), glowMat);
        glow.scale.set(1.5, 1.5, 1);
        break;
      }
      case "triangle": {
        const geo = new THREE.ConeGeometry(size, size * 0.1, 3);
        mesh = new THREE.Mesh(geo, mat);
        mesh.rotation.x = Math.PI / 2;
        glow = new THREE.Mesh(geo.clone(), glowMat);
        glow.scale.set(1.3, 1.3, 1.3);
        glow.rotation.x = Math.PI / 2;
        break;
      }
      case "circle": {
        const geo = new THREE.RingGeometry(size * 0.3, size, 32);
        mesh = new THREE.Mesh(geo, mat);
        glow = new THREE.Mesh(new THREE.RingGeometry(size * 0.1, size * 1.3, 32), glowMat);
        break;
      }
      case "diamond": {
        const shape2d = new THREE.Shape();
        shape2d.moveTo(0, size);
        shape2d.lineTo(size * 0.6, 0);
        shape2d.lineTo(0, -size);
        shape2d.lineTo(-size * 0.6, 0);
        shape2d.closePath();
        const geo = new THREE.ShapeGeometry(shape2d);
        mesh = new THREE.Mesh(geo, mat);
        glow = new THREE.Mesh(geo.clone(), glowMat);
        glow.scale.set(1.4, 1.4, 1);
        break;
      }
      case "infinity": {
        // Simplified infinity as two connected circles
        const g = new THREE.Group();
        const r = size * 0.4;
        const c1 = new THREE.Mesh(new THREE.RingGeometry(r * 0.2, r, 16), mat);
        c1.position.x = -r * 0.7;
        g.add(c1);
        const c2 = new THREE.Mesh(new THREE.RingGeometry(r * 0.2, r, 16), mat);
        c2.position.x = r * 0.7;
        g.add(c2);
        mesh = g;
        // simplified glow
        glow = g.clone();
        glow.scale.set(1.2, 1.2, 1);
        break;
      }
      case "hexagon": {
        const geo = new THREE.CylinderGeometry(size, size, size * 0.05, 6);
        mesh = new THREE.Mesh(geo, mat);
        mesh.rotation.x = Math.PI / 2;
        glow = new THREE.Mesh(geo.clone(), glowMat);
        glow.scale.set(1.3, 1.3, 1.3);
        glow.rotation.x = Math.PI / 2;
        break;
      }
      case "bolt": {
        const shape2d = new THREE.Shape();
        shape2d.moveTo(0, size);
        shape2d.lineTo(size * 0.3, 0);
        shape2d.lineTo(size * 0.1, 0);
        shape2d.lineTo(size * 0.2, -size);
        shape2d.lineTo(-size * 0.25, -size * 0.2);
        shape2d.lineTo(-size * 0.05, -size * 0.2);
        shape2d.lineTo(-size * 0.3, size * 0.5);
        shape2d.lineTo(0, size * 0.5);
        shape2d.closePath();
        const geo = new THREE.ShapeGeometry(shape2d);
        mesh = new THREE.Mesh(geo, mat);
        glow = new THREE.Mesh(geo.clone(), glowMat);
        glow.scale.set(1.3, 1.3, 1);
        break;
      }
      case "drop": {
        const shape2d = new THREE.Shape();
        shape2d.moveTo(0, size);
        shape2d.quadraticCurveTo(size, 0, 0, -size);
        shape2d.quadraticCurveTo(-size, 0, 0, size);
        const geo = new THREE.ShapeGeometry(shape2d);
        mesh = new THREE.Mesh(geo, mat);
        glow = new THREE.Mesh(geo.clone(), glowMat);
        glow.scale.set(1.3, 1.3, 1);
        break;
      }
      default: {
        mesh = new THREE.Mesh(new THREE.BoxGeometry(size, size, size * 0.05), mat);
        glow = new THREE.Mesh(new THREE.BoxGeometry(size * 1.2, size * 1.2, size * 0.05), glowMat);
      }
    }
    return { mesh, glow };
  }

  function buildStickers() {
    const colors = getColors();
    BRAND_STICKERS.forEach((sticker, i) => {
      const angle = (i / BRAND_STICKERS.length) * Math.PI * 2;
      const radius = 3.0 + Math.random() * 1.5;
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle * 2) * 1.5 + Math.sin(angle) * 0.5;
      const z = Math.sin(angle) * radius * 0.3;

      const color = i % 2 === 0 ? colors.primary : colors.secondary;
      const { mesh, glow } = buildShape(sticker.shape, color, sticker.sizes);
      
      mesh.position.set(x, y, z);
      glow.position.set(x, y, z);

      scene.add(mesh);
      scene.add(glow);

      stickers.push({
        mesh, glow, sticker,
        angle, radius,
        baseColor: color,
        speed: 0.2 + Math.random() * 0.3,
        phase: Math.random() * Math.PI * 2,
        z,
      });
    });
  }

  function animate() {
    animId = requestAnimationFrame(animate);
    clock += 0.016;

    const colors = getColors();

    stickers.forEach((s, i) => {
      // Orbit around center
      const a = s.angle + clock * s.speed * 0.05;
      s.mesh.position.x = Math.cos(a) * s.radius;
      s.mesh.position.z = Math.sin(a) * s.radius * 0.3 + s.z;
      s.mesh.position.y += Math.sin(clock * s.speed + s.phase) * 0.002;

      // Rotate
      s.mesh.rotation.z += 0.01 * s.speed;
      s.mesh.rotation.x += 0.005 * s.speed;
      s.mesh.rotation.y += 0.008 * s.speed;

      // Glow follows
      s.glow.position.copy(s.mesh.position);
      s.glow.rotation.copy(s.mesh.rotation);

      // Pulse with audio
      const pulse = 1 + audioLevel * 0.5 + Math.sin(clock * 2 + i) * 0.05;
      s.mesh.scale.set(pulse, pulse, pulse);
      s.glow.scale.set(pulse * 1.3, pulse * 1.3, pulse * 1.3);

      // Color shift with tenant
      const c = i % 2 === 0 ? colors.primary : colors.secondary;
      s.mesh.material.color.setHex(c);
      s.glow.material.color.setHex(colors.accent);

      // Opacity wave
      s.mesh.material.opacity = 0.4 + Math.sin(clock * 0.5 + i) * 0.2;
      s.glow.material.opacity = 0.05 + Math.sin(clock * 0.3 + i * 0.7) * 0.03;
    });

    renderer.render(scene, camera);
  }

  function onResize() {
    if (!container) return;
    const w = container.clientWidth;
    const h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }
</script>

<div bind:this={container} class="sticker-canvas"></div>

<style>
  .sticker-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
    pointer-events: none;
  }
</style>
