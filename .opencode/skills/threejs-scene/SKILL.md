---
name: threejs-scene
description: "Crear escenas 3D interactivas con Three.js para páginas web."
version: 1.0.0
---

# Three.js Scene Creator

**Propósito**: Crear visualizaciones 3D impresionantes para el ecosistema.

## Setup Estándar

```html
<script src="/static/threejs/three.min.js"></script>
<script src="/static/threejs/OrbitControls.js"></script>
```

## Patrones Comunes

### 1. Particle System (fondo)
- 3000 partículas con BufferGeometry
- Colores: primary (#00d4ff), secondary (#7b2ff7), accent (#ff6b35)
- Additive blending para efecto glow
- Rotación automática + interacción con mouse

### 2. Central Core (esfera wireframe)
- SphereGeometry(2, 32, 32)
- Wireframe con opacity 0.1
- Pulse animation con scale

### 3. Orbiting Rings
- TorusGeometry para anillos orbitales
- 3 anillos con colores diferentes
- Rotación en ejes diferentes

## Performance

- Usar BufferGeometry (no Geometry)
- Limitar partículas a 5000 max
- Usar requestAnimationFrame
- Resize handler para responsive

## Ejemplo mínimo

```javascript
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, w/h, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
renderer.setSize(w, h);
document.getElementById('canvas').appendChild(renderer.domElement);

const particles = new THREE.Points(geometry, material);
scene.add(particles);

function animate() {
  requestAnimationFrame(animate);
  particles.rotation.y += 0.001;
  renderer.render(scene, camera);
}
animate();
```
