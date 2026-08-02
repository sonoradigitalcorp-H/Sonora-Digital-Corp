<template>
  <div class="min-h-screen bg-[#0a0a0f] text-white font-sans overflow-x-hidden">
    <!-- THREE.JS Background -->
    <canvas ref="bgCanvas" class="fixed inset-0 z-0 pointer-events-none"></canvas>

    <!-- NAV -->
    <nav class="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 bg-gradient-to-b from-[#0a0a0f]/95 to-transparent">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-[#AC6D3E] to-[#CD8D5D] flex items-center justify-center text-sm font-bold text-black">✦</div>
        <span class="font-semibold text-sm">Mystica <span class="font-light text-[#CD8D5D]">AI</span></span>
      </div>
      <div class="flex items-center gap-6 text-xs text-white/50">
        <a href="#servicios" class="hover:text-[#CD8D5D] transition">Servicios</a>
        <a href="#como-funciona" class="hover:text-[#CD8D5D] transition">Cómo funciona</a>
        <a href="#precios" class="hover:text-[#CD8D5D] transition">Precios</a>
        <a href="/call" class="px-4 py-2 rounded-full bg-[#AC6D3E] text-black text-xs font-semibold hover:bg-[#CD8D5D] transition">📞 Llamar ahora</a>
      </div>
    </nav>

    <!-- HERO -->
    <section class="relative z-10 min-h-screen flex flex-col items-center justify-center px-6 pt-20">
      <div ref="orbeRef" class="w-64 h-64 md:w-80 md:h-80 rounded-full cursor-pointer relative mb-8"
           @click="openCall"
           @mousemove="onOrbeMove">
        <div class="absolute inset-0 rounded-full bg-gradient-to-br from-[#AC6D3E]/20 to-[#CD8D5D]/5 animate-pulse-slow"></div>
        <div class="absolute inset-4 rounded-full bg-gradient-to-br from-[#AC6D3E]/10 to-transparent animate-spin-slow"></div>
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="text-6xl md:text-7xl font-light tracking-widest text-[#CD8D5D] opacity-80">𓂀</div>
        </div>
        <div class="absolute -bottom-2 left-1/2 -translate-x-1/2 text-xs text-white/40 whitespace-nowrap">Click para hablar</div>
      </div>

      <h1 class="text-4xl md:text-6xl font-light text-center max-w-3xl leading-tight">
        Tu <span class="text-[#CD8D5D] font-normal">asistente AI</span> que<br>
        <span class="text-white/70">atiende llamadas, agenda citas<br>y cierra ventas</span>
      </h1>
      <p class="text-white/40 text-sm mt-6 max-w-xl text-center leading-relaxed">
        Mystica escucha, entiende y responde como un humano. 
        Sin apps. Sin esperas. Solo habla y ella hace el resto.
      </p>
      <div class="flex gap-4 mt-10">
        <a href="/call" class="px-8 py-3 rounded-full bg-[#AC6D3E] text-black font-semibold text-sm hover:bg-[#CD8D5D] transition shadow-lg shadow-[#AC6D3E]/20">📞 Probar llamada gratis</a>
        <a href="#servicios" class="px-8 py-3 rounded-full border border-white/10 text-white/70 text-sm hover:border-[#AC6D3E]/50 hover:text-[#CD8D5D] transition">Ver servicios →</a>
      </div>

      <!-- Floating sigils -->
      <div class="fixed top-1/4 left-8 text-4xl opacity-[0.03] pointer-events-none animate-float" style="animation-delay:-2s">𓂀</div>
      <div class="fixed top-1/3 right-12 text-3xl opacity-[0.03] pointer-events-none animate-float" style="animation-delay:-7s">⎔</div>
      <div class="fixed bottom-1/4 left-12 text-5xl opacity-[0.03] pointer-events-none animate-float" style="animation-delay:-12s">⏣</div>
    </section>

    <!-- SERVICIOS -->
    <section id="servicios" class="relative z-10 px-6 py-24 max-w-6xl mx-auto">
      <h2 class="text-3xl font-light text-center mb-4">Servicios <span class="text-[#CD8D5D]">inteligentes</span></h2>
      <p class="text-white/40 text-sm text-center mb-16 max-w-lg mx-auto">Cada servicio es un agente AI entrenado para tu industria</p>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="s in servicios" :key="s.titulo"
             class="group p-6 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] hover:border-[#AC6D3E]/30 transition-all duration-500 cursor-pointer"
             @click="openCall">
          <div class="text-3xl mb-4">{{ s.icono }}</div>
          <h3 class="font-semibold text-sm mb-2">{{ s.titulo }}</h3>
          <p class="text-white/40 text-xs leading-relaxed">{{ s.desc }}</p>
        </div>
      </div>
    </section>

    <!-- CÓMO FUNCIONA -->
    <section id="como-funciona" class="relative z-10 px-6 py-24 max-w-6xl mx-auto">
      <h2 class="text-3xl font-light text-center mb-4">Así de <span class="text-[#CD8D5D]">simple</span></h2>
      <p class="text-white/40 text-sm text-center mb-16 max-w-lg mx-auto">Tres pasos y tienes un agente AI atendiendo a tus clientes</p>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div v-for="(p, i) in pasos" :key="i" class="text-center">
          <div class="w-12 h-12 rounded-full bg-[#AC6D3E]/10 border border-[#AC6D3E]/20 flex items-center justify-center mx-auto mb-4">
            <span class="text-[#CD8D5D] font-bold">{{ i+1 }}</span>
          </div>
          <h3 class="font-semibold text-sm mb-2">{{ p.titulo }}</h3>
          <p class="text-white/40 text-xs leading-relaxed">{{ p.desc }}</p>
        </div>
      </div>
    </section>

    <!-- FRASE HERMÉTICA -->
    <section class="relative z-10 py-16 text-center">
      <div class="text-5xl mb-4 opacity-20" id="sigilo">𓂀</div>
      <p class="text-white/30 text-sm italic max-w-md mx-auto" id="frase">"El universo escucha cuando el mago habla"</p>
    </section>

    <!-- CTA FINAL -->
    <section class="relative z-10 px-6 py-24 text-center">
      <h2 class="text-3xl font-light mb-4">¿Listo para <span class="text-[#CD8D5D]">automatizar</span>?</h2>
      <p class="text-white/40 text-sm mb-8 max-w-md mx-auto">Prueba Mystica gratis. Sin tarjeta. Sin compromiso.</p>
      <a href="/call" class="inline-block px-10 py-4 rounded-full bg-[#AC6D3E] text-black font-semibold hover:bg-[#CD8D5D] transition shadow-xl shadow-[#AC6D3E]/20 text-sm">📞 Hacer llamada de prueba</a>
    </section>

    <!-- FOOTER -->
    <footer class="relative z-10 border-t border-white/5 px-6 py-8">
      <div class="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-2 text-xs text-white/30">
          <span class="text-[#CD8D5D]">✦</span> Mystica AI — Sonora Digital Corp
        </div>
        <div class="flex gap-6 text-xs text-white/30">
          <a href="https://wa.me/5216623538272" class="hover:text-[#CD8D5D] transition">WhatsApp</a>
          <a href="https://t.me/sonorabot" class="hover:text-[#CD8D5D] transition">Telegram</a>
          <a href="mailto:sonoradigitalcorp@gmail.com" class="hover:text-[#CD8D5D] transition">Email</a>
          <a href="https://sonoradigitalcorp.com" class="hover:text-[#CD8D5D] transition">Web</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const bgCanvas = ref(null)
const orbeRef = ref(null)
let animId = null

const servicios = [
  { icono: '📞', titulo: 'Atención por Voz', desc: 'Mystica contesta llamadas, entiende lo que necesitan y responde con voz natural. 24/7.' },
  { icono: '💬', titulo: 'WhatsApp AI', desc: 'Integración total con WhatsApp. Responde dudas, agenda citas y califica leads automáticamente.' },
  { icono: '📅', titulo: 'Booking Inteligente', desc: 'Agenda citas directo a Google Calendar. El cliente habla, Mystica agenda, tú solo confirmas.' },
  { icono: '🎯', titulo: 'Campañas Outbound', desc: 'Busca leads automáticamente, los contacta por WhatsApp y los califica como frío/tibio/caliente.' },
  { icono: '🤖', titulo: 'Agentes por Industria', desc: 'Cada negocio tiene su propio agente entrenado en su nicho: barberías, música, bufetes, restaurantes.' },
  { icono: '📊', titulo: 'Analytics + Evolución', desc: 'Mide cada interacción. A/B testing automatico. El sistema mejora solo con cada llamada.' },
  { icono: '🔐', titulo: 'Multi-tenant Seguro', desc: 'Cada empresa tiene su propio espacio, su número y su agente. Datos aislados, memoria persistente.' },
  { icono: '🌐', titulo: 'Widget Web 3D', desc: 'El orbe de Mystica se embeda en tu web. Tus clientes hablan con IA desde tu página.' },
]

const pasos = [
  { titulo: 'Conecta tu negocio', desc: 'Dinos tu industria y número. Mystica se adapta a tu negocio automáticamente.' },
  { titulo: 'Ella atiende', desc: 'Mystica recibe llamadas y mensajes. Entiende, responde, agenda. Sin intervención tuya.' },
  { titulo: 'Tú solo revisas', desc: 'Recibes notificaciones de leads, citas y ventas. El sistema mejora solo.' },
]

const frases = [
  '"El universo escucha cuando el mago habla"',
  '"Cada llamada es un mundo por descubrir"',
  '"La voz es el puente entre el deseo y la realidad"',
  '"En el silencio del cliente está la respuesta"',
  '"El algoritmo es el aliado del chamán digital"',
]

function openCall() { router.push('/call') }

function onOrbeMove(e) {
  if (!orbeRef.value) return
  const r = orbeRef.value.getBoundingClientRect()
  const x = (e.clientX - r.left) / r.width - 0.5
  const y = (e.clientY - r.top) / r.height - 0.5
  orbeRef.value.style.transform = `perspective(800px) rotateY(${x*20}deg) rotateX(${-y*20}deg)`
}

// Three.js
onMounted(() => {
  const h = document.getElementById('frase')
  if (h) h.textContent = frases[Math.floor(Math.random() * frases.length)]

  import('three').then(({ Scene, PerspectiveCamera, WebGLRenderer, BufferGeometry, BufferAttribute, PointsMaterial, Points }) => {
    if (!bgCanvas.value) return
    const sc = new Scene(), ca = new PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000)
    const re = new WebGLRenderer({ canvas: bgCanvas.value, alpha: true, antialias: true })
    re.setSize(window.innerWidth, window.innerHeight)
    re.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    const cnt = 2000, g = new BufferGeometry(), p = new Float32Array(cnt * 3)
    for (let i = 0; i < cnt; i++) { p[i*3] = (Math.random() - .5) * 60; p[i*3+1] = (Math.random() - .5) * 40; p[i*3+2] = (Math.random() - .5) * 40 }
    g.setAttribute('position', new BufferAttribute(p, 3))
    const m = new PointsMaterial({ size: .04, color: 0xAC6D3E, transparent: true, opacity: .3, sizeAttenuation: true })
    const pt = new Points(g, m); sc.add(pt); ca.position.z = 25
    function an() { animId = requestAnimationFrame(an); pt.rotation.y += .0003; re.render(sc, ca) }
    an()
    window.addEventListener('resize', () => { ca.aspect = window.innerWidth / window.innerHeight; ca.updateProjectionMatrix(); re.setSize(window.innerWidth, window.innerHeight) })
  })
})
onUnmounted(() => { if (animId) cancelAnimationFrame(animId) })
</script>

<style>
@keyframes pulse-slow { 0%,100%{opacity:1} 50%{opacity:.7} }
@keyframes spin-slow { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-20px)} }
.animate-pulse-slow { animation:pulse-slow 4s ease-in-out infinite }
.animate-spin-slow { animation:spin-slow 20s linear infinite }
.animate-float { animation:float 12s ease-in-out infinite }
html { scroll-behavior: smooth }
</style>
