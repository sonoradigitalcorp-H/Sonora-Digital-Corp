import '../css/app.css'

// --- Three.js lazy load ---
const threeContainer = document.getElementById('three-container')
if (threeContainer) {
  const observer = new IntersectionObserver(async ([entry]) => {
    if (!entry.isIntersecting) return
    observer.disconnect()
    try {
      const { initScene } = await import('./three-hero.js')
      initScene(threeContainer)
    } catch (e) {
      console.warn('Three.js failed to load:', e)
    }
  }, { rootMargin: '200px' })
  observer.observe(threeContainer)
}

// --- Nav hide on scroll down (mobile) ---
const bottomNav = document.getElementById('bottom-nav')
if (bottomNav) {
  let lastScroll = 0
  window.addEventListener('scroll', () => {
    const current = window.scrollY
    if (current > lastScroll && current > 100) {
      bottomNav.classList.add('nav-hidden')
    } else {
      bottomNav.classList.remove('nav-hidden')
    }
    lastScroll = current
  }, { passive: true })
}

// --- Scroll reveal animations ---
const revealElements = document.querySelectorAll('.reveal')
if (revealElements.length) {
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible')
        revealObserver.unobserve(entry.target)
      }
    })
  }, { threshold: 0.1 })

  revealElements.forEach(el => revealObserver.observe(el))
}

// --- Counter animation ---
const counters = document.querySelectorAll('.counter')
if (counters.length) {
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return
      const el = entry.target
      const target = parseInt(el.dataset.target)
      const duration = parseInt(el.dataset.duration) || 1500
      const start = performance.now()

      function update(now) {
        const elapsed = now - start
        const progress = Math.min(elapsed / duration, 1)
        const eased = 1 - Math.pow(1 - progress, 3)
        el.textContent = Math.floor(eased * target)
        if (progress < 1) requestAnimationFrame(update)
      }

      requestAnimationFrame(update)
      counterObserver.unobserve(el)
    })
  }, { threshold: 0.5 })

  counters.forEach(el => counterObserver.observe(el))
}

// --- Age gate (Mysticverse) ---
const ageGate = document.getElementById('age-gate')
const ageGateContent = document.getElementById('age-gate-content')
const enterBtn = document.getElementById('age-gate-enter')
const birthInput = document.getElementById('birth-date')

if (ageGate && enterBtn && birthInput) {
  enterBtn.addEventListener('click', () => {
    const birth = new Date(birthInput.value)
    const today = new Date()
    let age = today.getFullYear() - birth.getFullYear()
    const m = today.getMonth() - birth.getMonth()
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--
    if (age >= 18) {
      ageGate.classList.add('opacity-0', 'pointer-events-none')
      setTimeout(() => {
        ageGate.style.display = 'none'
        if (ageGateContent) ageGateContent.style.display = 'block'
      }, 500)
    } else {
      alert('You must be 18+ to enter Mysticverse.')
    }
  })

  enterBtn.disabled = true
  birthInput.addEventListener('input', () => {
    enterBtn.disabled = !birthInput.value
  })
}

// --- Cart FAB ---
const cartFab = document.getElementById('cart-fab')
const cartSheet = document.getElementById('cart-sheet')
const cartOverlay = document.getElementById('cart-overlay')

if (cartFab && cartSheet && cartOverlay) {
  cartFab.addEventListener('click', () => {
    cartSheet.classList.toggle('translate-y-full')
    cartOverlay.classList.toggle('hidden')
  })
  cartOverlay.addEventListener('click', () => {
    cartSheet.classList.add('translate-y-full')
    cartOverlay.classList.add('hidden')
  })
}
