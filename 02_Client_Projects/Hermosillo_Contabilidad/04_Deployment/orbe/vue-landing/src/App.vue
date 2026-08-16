<template>
  <div class="min-h-screen">
    <div class="aurora"></div>
    <div class="blob" style="width:420px;height:420px;background:#0e8a6d;top:-80px;left:-80px"></div>
    <div class="blob" style="width:360px;height:360px;background:#6d28d9;bottom:-60px;right:-40px;animation-delay:-6s"></div>
    <div class="blob" style="width:300px;height:300px;background:#0ea5e9;top:40%;left:55%;animation-delay:-12s"></div>

    <!-- NAV -->
    <nav class="fixed top-0 inset-x-0 z-50 glass" style="border-radius:0">
      <div class="max-w-6xl mx-auto flex items-center justify-between px-5 py-3.5">
        <router-link to="/" class="flex items-center gap-2 font-bold text-lg">
          <span class="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-violet-500 flex items-center justify-center text-sm">🧮</span>
          Nathaly<span class="grad-text">.Contabilidad</span>
        </router-link>
        <div class="hidden md:flex items-center gap-5 text-sm text-zinc-300">
          <router-link to="/" class="hover:text-white transition" :class="{'text-white': $route.name==='home'}">Inicio</router-link>
          <router-link to="/servicios" class="hover:text-white transition" :class="{'text-white': $route.name==='servicios'}">Servicios</router-link>
          <router-link to="/video" class="hover:text-white transition" :class="{'text-white': $route.name==='video'}">Video</router-link>
          <router-link to="/asistente" class="hover:text-white transition" :class="{'text-white': $route.name==='asistente'}">Asistente</router-link>
          <router-link to="/faq" class="hover:text-white transition" :class="{'text-white': $route.name==='faq'}">FAQ</router-link>
          <router-link to="/contacto" class="hover:text-white transition" :class="{'text-white': $route.name==='contacto'}">Contacto</router-link>
        </div>
        <router-link to="/asistente" class="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-sm transition">🎤 Hablar</router-link>
      </div>
    </nav>

    <router-view />

    <!-- FOOTER -->
    <footer class="border-t border-white/5 py-8 text-center text-xs text-zinc-600">
      <div class="flex justify-center gap-4 mb-4">
        <a :href="waLink('contabilidad')" target="_blank" class="w-11 h-11 rounded-full bg-[#25D366] flex items-center justify-center text-xl hover:scale-110 transition" title="WhatsApp">🟢</a>
        <a href="https://t.me/HermosilloCont_bot" target="_blank" class="w-11 h-11 rounded-full bg-[#229ED9] flex items-center justify-center text-xl hover:scale-110 transition" title="Telegram">✈️</a>
        <a href="mailto:cp.nathalyhermosillo@gmail.com" class="w-11 h-11 rounded-full glass flex items-center justify-center text-xl hover:scale-110 transition" title="Correo">✉️</a>
        <a href="https://www.instagram.com/" target="_blank" class="w-11 h-11 rounded-full bg-gradient-to-br from-[#f09433] via-[#dc2743] to-[#bc1888] flex items-center justify-center text-xl hover:scale-110 transition" title="Instagram">📷</a>
      </div>
      <router-link to="/contacto" class="hover:text-zinc-400 transition">Aviso de privacidad</router-link>
      <div class="mt-1">Nathaly · Contabilidad · Hermosillo · Sonora</div>
    </footer>
  </div>
</template>

<script setup>
import { waLink } from './composables/useChat'
</script>