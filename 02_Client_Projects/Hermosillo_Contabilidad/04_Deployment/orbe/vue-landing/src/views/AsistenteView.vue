<template>
  <section class="pt-24 px-5 max-w-3xl mx-auto pb-16">
    <div class="flex items-center gap-3 mb-6">
      <button @click="$router.back()" class="w-11 h-11 rounded-xl glass hover:bg-white/10 flex items-center justify-center text-xl" title="Regresar">←</button>
      <div>
        <div class="text-emerald-400 text-xs font-bold tracking-[.25em] uppercase">Asistente IA</div>
        <h1 class="text-3xl font-extrabold">Habla conmigo <span class="grad-text">ahora</span></h1>
      </div>
    </div>
    <p class="text-zinc-400 mb-6">Toca el micrófono y cuéntame qué necesitas. También puedes escribirme.</p>

    <div class="glass rounded-3xl p-6 text-center relative overflow-hidden">
      <div class="absolute inset-0 opacity-25" style="background:radial-gradient(circle at 50% 15%,#0e8a6d44,transparent 60%)"></div>
      <div class="relative">
        <button @click="toggleMic" :class="listening ? 'bg-red-500 animate-pulse scale-105' : 'bg-emerald-500 hover:bg-emerald-400'" class="mx-auto w-28 h-28 rounded-full text-6xl flex items-center justify-center shadow-2xl shadow-emerald-500/40 transition transform">
          {{ listening ? '⏹' : '🎤' }}
        </button>
        <div class="mt-3 text-lg font-bold">{{ listening ? 'Te escucho, habla' : 'Toca para hablar' }}</div>
        <div class="text-xs text-zinc-500 mt-1">{{ listening ? 'el asistente procesa tu voz al instante' : 'es más rápido que escribir' }}</div>
        <button v-show="speaking" @click="stopSpeaking" class="mt-4 mx-auto w-14 h-14 rounded-full bg-zinc-800 border border-white/20 text-xl flex items-center justify-center hover:bg-red-500 transition" title="Detener voz">■</button>
      </div>
      <div class="relative flex gap-2 mt-6">
        <input v-model="msg" @keydown.enter="send(logEl)" placeholder="O escribe tu mensaje..." class="flex-1 bg-black/30 border border-white/10 rounded-2xl px-4 py-3.5 text-sm outline-none focus:border-emerald-400 transition" />
        <button @click="send(logEl)" class="px-5 rounded-2xl bg-white text-black font-bold text-sm">Enviar</button>
      </div>
      <div class="relative mt-6 space-y-3 max-h-80 overflow-y-auto text-left" ref="logEl">
        <div v-for="(m,i) in msgs" :key="i" :class="m.who==='user' ? 'ml-auto bg-white/10 rounded-2xl rounded-br-md px-4 py-2.5 w-fit max-w-[85%] text-sm' : 'bg-emerald-500/10 border border-emerald-500/20 rounded-2xl rounded-bl-md px-4 py-2.5 w-fit max-w-[85%] text-sm whitespace-pre-wrap'">
          {{ m.t }}
        </div>
      </div>
    </div>

    <div class="mt-6 grid grid-cols-2 gap-3 text-xs">
      <a :href="waLink('Contabilidad mensual')" target="_blank" class="glass rounded-2xl px-4 py-3 hover:bg-white/10 transition">📞 Cotizar contabilidad</a>
      <a :href="waLink('Cita ante el SAT')" target="_blank" class="glass rounded-2xl px-4 py-3 hover:bg-white/10 transition">📅 Cita SAT</a>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useChat, waLink } from '../composables/useChat'

const logEl = ref(null)
const { msgs, msg, listening, speaking, send, stopSpeaking, toggleMic } = useChat([
  { who: 'bot', t: 'Hola, soy la asistente de Nathaly, contadora en Hermosillo. ¿Qué necesitas?' }
])
</script>