<template>
  <section class="pt-24 px-5 max-w-4xl mx-auto pb-16">
    <div class="flex items-center gap-3 mb-8">
      <button @click="$router.back()" class="w-11 h-11 rounded-xl glass hover:bg-white/10 flex items-center justify-center text-xl" title="Regresar">←</button>
      <div>
        <div class="text-emerald-400 text-xs font-bold tracking-[.25em] uppercase">Video</div>
        <h1 class="text-3xl font-extrabold">Mira cómo trabajamos</h1>
      </div>
    </div>
    <div class="grid md:grid-cols-2 gap-8 items-start">
      <div class="glass rounded-3xl p-3">
        <video controls playsinline class="rounded-2xl w-full aspect-video bg-black" :src="reelUrl" preload="metadata"></video>
        <div class="flex justify-between items-center px-2 py-3 text-xs text-zinc-400">
          <span>Reel Nathaly · Contabilidad</span>
          <a :href="waLink('El reel de contabilidad')" target="_blank" class="text-emerald-400 hover:underline">Quiero uno así</a>
        </div>
      </div>
      <div class="space-y-4 text-sm text-zinc-400 leading-relaxed">
        <div class="glass rounded-2xl p-5">
          <h3 class="font-bold text-white mb-2">🎬 Marketing para negocios</h3>
          <p>Videos y reels con tu marca, listos para subir a redes. Estilo cinematográfico, dopamina en cada corte.</p>
        </div>
        <div class="glass rounded-2xl p-5">
          <h3 class="font-bold text-white mb-2">📱 Presencia digital</h3>
          <p>Publicaciones diarias, historias, encuestas y reels que mantienen tu negocio visible y en crecimiento.</p>
        </div>
        <div class="glass rounded-2xl p-5">
          <h3 class="font-bold text-white mb-2">🤖 Asistente IA 24/7</h3>
          <p>Respondemos a tus clientes al momento, en texto y voz, para que no pierdas una oportunidad.</p>
        </div>
        <a :href="waLink('Marketing para mi negocio')" target="_blank" class="block text-center bg-emerald-500 hover:bg-emerald-400 text-black font-bold rounded-2xl px-6 py-4 transition">Quiero marketing para mi negocio</a>
      </div>
    </div>
  </section>
</template>

<script setup>
import { waLink } from '../composables/useChat'
const reelUrl = './hermosillo_assets/reel_hermosillo.mp4'
</script>