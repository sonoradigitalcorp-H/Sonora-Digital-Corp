<template>
  <div ref="container"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'

const container = ref(null)
let scene, camera, renderer, orb, particles, frame

onMounted(() => {
  init()
  animate()
})

onUnmounted(() => { cancelAnimationFrame(frame); renderer?.dispose() })

function init() {
  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000)
  camera.position.z = 5

  renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
  renderer.setSize(window.innerWidth, window.innerHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.value.appendChild(renderer.domElement)

  // Orb
  const orbGeo = new THREE.IcosahedronGeometry(1, 4)
  const orbMat = new THREE.MeshPhysicalMaterial({
    color: 0x00d4ff, metalness: 0.3, roughness: 0.2,
    transmission: 0.6, thickness: 1.5, transparent: true, opacity: 0.9
  })
  orb = new THREE.Mesh(orbGeo, orbMat)
  orb.position.set(0, 0.2, 0)
  scene.add(orb)

  // Rings
  for (let i = 1; i <= 3; i++) {
    const ringGeo = new THREE.TorusGeometry(i * 0.8, 0.01, 16, 100)
    const ringMat = new THREE.MeshBasicMaterial({ color: 0x00d4ff, transparent: true, opacity: 0.15 / i })
    const ring = new THREE.Mesh(ringGeo, ringMat)
    ring.rotation.x = Math.PI / 2 + (i * 0.15)
    ring.rotation.z = i * 0.3
    orb.add(ring)
  }

  // Particles
  const count = 400
  const positions = new Float32Array(count * 3)
  for (let i = 0; i < count * 3; i++) positions[i] = (Math.random() - 0.5) * 20
  const pGeo = new THREE.BufferGeometry()
  pGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  const pMat = new THREE.PointsMaterial({ color: 0x00d4ff, size: 0.02, transparent: true, opacity: 0.5 })
  particles = new THREE.Points(pGeo, pMat)
  scene.add(particles)

  // Lights
  scene.add(new THREE.AmbientLight(0x404060, 0.5))
  const light = new THREE.PointLight(0x00d4ff, 2, 20)
  light.position.set(3, 3, 5)
  scene.add(light)
  const light2 = new THREE.PointLight(0x7c3aed, 1.5, 20)
  light2.position.set(-3, -2, 3)
  scene.add(light2)

  window.addEventListener('resize', onResize)
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
}

function animate() {
  frame = requestAnimationFrame(animate)
  const t = Date.now() * 0.001
  orb.rotation.y += 0.003
  orb.rotation.x = Math.sin(t * 0.5) * 0.1
  orb.position.y = Math.sin(t * 0.8) * 0.15
  particles.rotation.y += 0.0002
  renderer.render(scene, camera)
}
</script>
