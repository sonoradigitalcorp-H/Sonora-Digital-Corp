<template>
  <section class="pt-24 px-5 max-w-4xl mx-auto pb-16">
    <div class="flex items-center gap-3 mb-8">
      <button @click="$router.back()" class="w-11 h-11 rounded-xl glass hover:bg-white/10 flex items-center justify-center text-xl" title="Regresar">←</button>
      <div>
        <div class="text-emerald-400 text-xs font-bold tracking-[.25em] uppercase">Contacto</div>
        <h1 class="text-3xl font-extrabold">¿Hablamos?</h1>
      </div>
    </div>
    <p class="text-zinc-400 mb-8">Diagnóstico inicial gratis · respuesta en minutos</p>

    <div class="grid sm:grid-cols-2 gap-5">
      <a :href="waLink('contabilidad')" target="_blank" class="glass rounded-2xl p-6 flex items-center gap-4 hover:bg-white/10 transition">
        <div class="w-14 h-14 rounded-full bg-[#25D366] flex items-center justify-center text-2xl">🟢</div>
        <div><div class="font-bold">WhatsApp</div><div class="text-xs text-zinc-500">habla directo con Nathaly</div></div>
      </a>
      <a href="https://t.me/HermosilloCont_bot" target="_blank" class="glass rounded-2xl p-6 flex items-center gap-4 hover:bg-white/10 transition">
        <div class="w-14 h-14 rounded-full bg-[#229ED9] flex items-center justify-center text-2xl">✈️</div>
        <div><div class="font-bold">Telegram</div><div class="text-xs text-zinc-500">bot asistente 24/7</div></div>
      </a>
      <a href="mailto:cp.nathalyhermosillo@gmail.com" class="glass rounded-2xl p-6 flex items-center gap-4 hover:bg-white/10 transition">
        <div class="w-14 h-14 rounded-full bg-white text-[#0e8a6d] flex items-center justify-center text-2xl">✉️</div>
        <div><div class="font-bold">Correo</div><div class="text-xs text-zinc-500">escríbenos cuando quieras</div></div>
      </a>
      <a href="https://www.instagram.com/" target="_blank" class="glass rounded-2xl p-6 flex items-center gap-4 hover:bg-white/10 transition">
        <div class="w-14 h-14 rounded-full bg-gradient-to-br from-[#f09433] via-[#dc2743] to-[#bc1888] flex items-center justify-center text-2xl">📷</div>
        <div><div class="font-bold">Instagram</div><div class="text-xs text-zinc-500">síguenos, publicamos cada día</div></div>
      </a>
    </div>

    <div class="text-center text-[11px] text-zinc-600 mt-10 leading-relaxed max-w-xl mx-auto">
      Aviso de privacidad: tus datos (nombre, negocio, contacto) se usan únicamente para brindarte atención y cotización de servicios de Hermosillo Contabilidad. No se comparten con terceros. Puedes solicitar su eliminación escribiendo a cp.nathalyhermosillo@gmail.com.
    </div>
  </section>
</template>

<script setup>
import { waLink } from '../composables/useChat'
</script>