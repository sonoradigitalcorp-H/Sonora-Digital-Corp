<template>
  <section class="relative pt-28 pb-10 px-5 max-w-6xl mx-auto">
    <div class="flex flex-col lg:flex-row items-center gap-10">
      <div class="flex-1">
        <div class="text-emerald-400 text-xs font-bold tracking-[.25em] uppercase mb-4">Contadora certificada · Hermosillo</div>
        <h1 class="text-4xl md:text-6xl font-extrabold leading-[1.05] tracking-tight">
          Tu contabilidad <span class="grad-text">en orden</span>,<br>sin pendientes <span class="grad-text">ni estrés.</span>
        </h1>
        <p class="mt-5 text-zinc-400 text-lg leading-relaxed max-w-lg">
          Contabilidad, administración, importaciones y trámites SAT. Un asistente que te escucha y responde al momento.
        </p>
        <div class="mt-7 flex flex-wrap gap-4">
          <router-link to="/asistente" class="px-7 py-3.5 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold transition shadow-lg shadow-emerald-500/30">Probar asistente</router-link>
          <a :href="waLink('Diagnóstico gratis de contabilidad')" target="_blank" class="px-7 py-3.5 rounded-2xl glass hover:bg-white/10 font-bold transition">WhatsApp</a>
          <router-link to="/servicios" class="px-7 py-3.5 rounded-2xl glass hover:bg-white/10 font-bold transition">Ver servicios</router-link>
        </div>
        <div class="mt-8 flex items-center gap-3 text-xs text-zinc-500">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          Asistente en línea · respuesta en segundos
        </div>
      </div>
      <!-- Widget voz-first: LO PRINCIPAL — la gente toca y habla -->
      <div class="flex-1 w-full max-w-md">
        <div class="glass rounded-3xl p-6 text-center relative overflow-hidden">
          <div class="absolute inset-0 -z-0 opacity-30" style="background:radial-gradient(circle at 50% 20%,#0e8a6d33,transparent 60%)"></div>
          <div class="relative">
            <div class="text-sm text-zinc-400 mb-4">Asistente Nathaly IA · escúchame</div>
            <button @click="toggleMic" :class="listening ? 'bg-red-500 animate-pulse scale-105' : 'bg-emerald-500 hover:bg-emerald-400'" class="mx-auto w-24 h-24 rounded-full text-5xl flex items-center justify-center shadow-2xl shadow-emerald-500/40 transition transform">
              {{ listening ? '⏹' : '🎤' }}
            </button>
            <div class="mt-3 font-bold text-lg">{{ listening ? 'Te escucho, habla' : 'Toca y habla' }}</div>
            <div class="text-xs text-zinc-500 mt-1">{{ listening ? 'suelta para enviar' : 'activa el micrófono y habla conmigo' }}</div>
            <button v-show="speaking" @click="stopSpeaking" class="mt-3 mx-auto w-12 h-12 rounded-full bg-zinc-800 border border-white/10 text-lg flex items-center justify-center">■</button>
          </div>
          <div class="relative mt-5 text-left">
            <div v-for="(m,i) in msgs.slice(-3)" :key="i" :class="m.who==='user' ? 'ml-auto bg-white/10 rounded-2xl rounded-br-md px-3 py-2 w-fit max-w-[85%] text-xs mb-2' : 'bg-emerald-500/10 border border-emerald-500/20 rounded-2xl rounded-bl-md px-3 py-2 w-fit max-w-[85%] text-xs mb-2'">
              {{ m.t }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Carrusel Canva: ilustraciones SIN personas -->
  <section class="px-5 max-w-6xl mx-auto pb-4">
    <div class="glass rounded-3xl p-4 overflow-hidden">
      <div class="flex transition-transform duration-500" :style="{transform:`translateX(-${idx*100}%)`}">
        <div v-for="(s,i) in SLIDES" :key="i" class="w-full flex-none rounded-2xl overflow-hidden">
          <img :src="s.img" :alt="s.t" class="w-full aspect-[3.4/1] object-cover" loading="lazy">
          <div class="text-center text-sm text-zinc-300 py-2">{{ s.t }}</div>
        </div>
      </div>
      <div class="flex justify-center gap-2 mt-2">
        <button v-for="(s,i) in SLIDES" :key="i" @click="idx=i" :class="idx===i ? 'bg-emerald-400 w-6' : 'bg-white/15 w-2'" class="h-2 rounded-full transition-all"></button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { useChat, waLink, abVariant } from '../composables/useChat'

const { msgs, listening, speaking, send, stopSpeaking, toggleMic } = useChat([
  { who: 'bot', t: 'Hola, soy la asistente de Nathaly. Toca el micrófono y cuéntame qué necesitas.' }
])

const variant = ref(abVariant())
const idx = ref(0)
const SLIDES = [
  { img: './hermosillo_canva/contabilidad.jpg', t: 'Contabilidad en orden' },
  { img: './hermosillo_canva/citas_sat.jpg', t: 'Citas SAT gestionadas' },
  { img: './hermosillo_canva/declaracion.jpg', t: 'Declaraciones sin errores' },
  { img: './hermosillo_canva/importacion.jpg', t: 'Importaciones en regla' },
  { img: './hermosillo_canva/dashboard.jpg', t: 'Tu negocio en tiempo real' },
]
let carTimer = null
onMounted(() => {
  // A/B: registrar la variante para analytics
  try { console.log('[AB] hermosillo variant:', variant.value) } catch (e) {}
  carTimer = setInterval(() => { idx.value = (idx.value + 1) % SLIDES.length }, 5000)
})
onBeforeUnmount(() => { if (carTimer) clearInterval(carTimer) })
</script>