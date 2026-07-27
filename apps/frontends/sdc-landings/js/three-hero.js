import * as THREE from 'three'

export function initScene(container) {
  const tier = getDeviceTier()
  const config = TIER_CONFIGS[tier]
  let paused = false
  let animationId = null

  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
  camera.position.z = config.cameraZ

  const renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: false,
    powerPreference: 'high-performance',
  })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, config.dpr))
  renderer.setSize(window.innerWidth, window.innerHeight)
  container.prepend(renderer.domElement)

  const fallback = container.querySelector('.three-fallback')
  if (fallback) fallback.style.opacity = '0'

  const particles = createParticles(scene, config)
  const glows = createGlows(scene, config)

  let mouseX = 0
  let mouseY = 0
  if (tier === 'high') {
    document.addEventListener('mousemove', (e) => {
      mouseX = (e.clientX / window.innerWidth) * 2 - 1
      mouseY = -(e.clientY / window.innerHeight) * 2 + 1
    })
  }

  const clock = new THREE.Clock()

  function animate() {
    if (paused) return
    animationId = requestAnimationFrame(animate)
    const dt = clock.getDelta()

    particles.rotation.y += dt * config.rotationSpeed
    particles.position.y = Math.sin(Date.now() * 0.0003) * 0.3

    if (tier === 'high') {
      particles.rotation.x += (mouseY * 0.05 - particles.rotation.x) * 0.02
      particles.rotation.z += (mouseX * 0.05 - particles.rotation.z) * 0.02
    }

    glows.forEach((glow, i) => {
      const phase = i * 1.5
      glow.material.opacity = 0.3 + Math.sin(Date.now() * 0.001 + phase) * 0.2
      glow.scale.setScalar(1 + Math.sin(Date.now() * 0.0008 + phase) * 0.1)
    })

    renderer.render(scene, camera)
  }

  animate()

  const onResize = () => {
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()
    renderer.setSize(window.innerWidth, window.innerHeight)
  }

  window.addEventListener('resize', onResize)

  document.addEventListener('visibilitychange', () => {
    paused = document.hidden
    if (!paused) animate()
  })

  return () => {
    paused = true
    if (animationId) cancelAnimationFrame(animationId)
    window.removeEventListener('resize', onResize)
    renderer.dispose()
    scene.clear()
  }
}

function getDeviceTier() {
  const mem = navigator.deviceMemory || 4
  const cores = navigator.hardwareConcurrency || 4
  if (mem <= 2 || cores <= 2) return 'low'
  if (mem <= 4 || cores <= 4) return 'medium'
  return 'high'
}

const TIER_CONFIGS = {
  low: { particles: 15, glows: 2, dpr: 1, cameraZ: 8, rotationSpeed: 0.01 },
  medium: { particles: 40, glows: 4, dpr: 1.5, cameraZ: 7, rotationSpeed: 0.015 },
  high: { particles: 100, glows: 8, dpr: 2, cameraZ: 6, rotationSpeed: 0.02 },
}

function createParticles(scene, config) {
  const geometry = new THREE.BufferGeometry()
  const count = config.particles
  const positions = new Float32Array(count * 3)
  const colors = new Float32Array(count * 3)
  const sizes = new Float32Array(count)

  const colorA = new THREE.Color('#00f0ff')
  const colorB = new THREE.Color('#8b5cf6')

  for (let i = 0; i < count; i++) {
    const r = Math.pow(Math.random(), 1.8) * 6
    const theta = Math.random() * Math.PI * 2
    const phi = Math.acos(2 * Math.random() - 1)

    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta)
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta) * 0.5
    positions[i * 3 + 2] = r * Math.cos(phi) * 0.3

    const t = Math.random()
    const c = colorA.clone().lerp(colorB, t)
    colors[i * 3] = c.r
    colors[i * 3 + 1] = c.g
    colors[i * 3 + 2] = c.b

    sizes[i] = Math.random() * 2 + 0.5
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1))

  const material = new THREE.PointsMaterial({
    size: 0.12,
    vertexColors: true,
    transparent: true,
    opacity: 0.6,
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true,
    depthWrite: false,
  })

  const points = new THREE.Points(geometry, material)
  scene.add(points)
  return points
}

function createGlows(scene, config) {
  const glows = []
  const canvas = document.createElement('canvas')
  canvas.width = 64
  canvas.height = 64
  const ctx = canvas.getContext('2d')
  const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32)
  gradient.addColorStop(0, 'rgba(255,255,255,1)')
  gradient.addColorStop(0.2, 'rgba(255,255,255,0.8)')
  gradient.addColorStop(1, 'rgba(255,255,255,0)')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, 64, 64)

  const texture = new THREE.CanvasTexture(canvas)

  for (let i = 0; i < config.glows; i++) {
    const material = new THREE.SpriteMaterial({
      map: texture,
      blending: THREE.AdditiveBlending,
      transparent: true,
      opacity: 0.3,
      color: i % 2 === 0 ? '#00f0ff' : '#8b5cf6',
      depthWrite: false,
    })
    const sprite = new THREE.Sprite(material)
    const angle = (i / config.glows) * Math.PI * 2
    sprite.position.set(Math.cos(angle) * 3, Math.sin(angle * 2) * 2, -2)
    sprite.scale.setScalar(2 + Math.random())
    scene.add(sprite)
    glows.push(sprite)
  }

  return glows
}
