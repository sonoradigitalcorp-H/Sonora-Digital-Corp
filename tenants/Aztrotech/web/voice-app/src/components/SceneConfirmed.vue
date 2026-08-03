<template>
  <div class="h-full flex flex-col items-center justify-center px-4 py-8 animate-fade-in">
    <!-- Check Animation -->
    <div class="w-24 h-24 rounded-full bg-aztrotech-success/20 flex items-center justify-center mb-6 shadow-[0_0_60px_rgba(16,185,129,0.3)]">
      <span class="text-5xl">✅</span>
    </div>

    <h2 class="text-2xl font-bold mb-2">¡Cita confirmada!</h2>
    <p class="text-white/50 text-sm mb-8 text-center max-w-md">
      <strong class="text-white">{{ data.name }}</strong>, tu llamada con César está agendada.
    </p>

    <!-- Appointment Card -->
    <div class="bg-white/[0.03] border border-aztrotech-success/20 rounded-2xl p-6 mb-8 max-w-sm w-full">
      <div class="flex items-center gap-4 mb-4">
        <div class="w-12 h-12 rounded-full bg-gradient-to-br from-aztrotech-primary to-aztrotech-accent flex items-center justify-center text-lg font-bold">CH</div>
        <div>
          <div class="font-semibold">César Holguín</div>
          <div class="text-white/40 text-xs">Fundador de Aztrotech</div>
        </div>
      </div>
      <div class="space-y-2 text-sm">
        <div class="flex justify-between"><span class="text-white/40">📅 Fecha</span><span class="font-semibold">{{ formatDate(data.date) }}</span></div>
        <div class="flex justify-between"><span class="text-white/40">🕐 Hora</span><span class="font-semibold text-aztrotech-primary">{{ data.time }}</span></div>
        <div class="flex justify-between"><span class="text-white/40">⏱️ Duración</span><span class="font-semibold">15 minutos</span></div>
        <div class="flex justify-between"><span class="text-white/40">👤 Cliente</span><span class="font-semibold">{{ data.name }}</span></div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex flex-wrap gap-3 justify-center mb-8">
      <a href="https://wa.me/5216621072254" target="_blank" class="px-5 py-3 rounded-xl bg-[#25D366]/20 border border-[#25D366]/30 text-[#25D366] text-sm font-medium hover:bg-[#25D366]/30 transition-all">
        📱 WhatsApp con César
      </a>
      <a href="https://instagram.com/cesarholguin" target="_blank" class="px-5 py-3 rounded-xl bg-[#E4405F]/20 border border-[#E4405F]/30 text-[#E4405F] text-sm font-medium hover:bg-[#E4405F]/30 transition-all">
        📸 Instagram
      </a>
      <a href="https://linkedin.com/in/cesarholguin" target="_blank" class="px-5 py-3 rounded-xl bg-[#0A66C2]/20 border border-[#0A66C2]/30 text-[#0A66C2] text-sm font-medium hover:bg-[#0A66C2]/30 transition-all">
        💼 LinkedIn
      </a>
    </div>

    <div class="flex gap-3">
      <button @click="$emit('action','home')" class="px-5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-sm hover:bg-white/10 transition-all">🏠 Volver al inicio</button>
      <button @click="$emit('action','services')" class="px-5 py-2.5 rounded-xl bg-aztrotech-primary/10 border border-aztrotech-primary/20 text-aztrotech-primary text-sm hover:bg-aztrotech-primary/20 transition-all">🤖 Ver servicios</button>
    </div>

    <!-- Chat -->
    <div class="w-full max-w-lg mt-6 space-y-3">
      <div v-for="(m,i) in messages" :key="i" :class="['px-4 py-3 rounded-2xl text-sm leading-relaxed max-w-[85%] animate-fade-in', m.role==='bot'?'bg-white/5 border border-white/5 self-start':'bg-aztrotech-primary text-black self-end ml-auto']" v-html="m.text"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const props = defineProps({ data: Object })
const emit = defineEmits(['action'])
const messages = ref([])

onMounted(() => {
  addBot(`¡Listo <strong>${props.data.name}</strong>! Recibirás un recordatorio antes de tu llamada. César se comunicará contigo al WhatsApp para confirmar. ¡Nos vemos pronto! 👋`)
  // Notify backend
  fetch('/api/schedule', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(props.data)
  }).catch(() => {})
})

function formatDate(d) {
  if (!d) return 'Hoy'
  const dt = new Date(d + 'T12:00:00')
  return dt.toLocaleDateString('es-MX', { weekday: 'long', day: 'numeric', month: 'long' })
}

function addBot(t) { messages.value.push({ role: 'bot', text: t }) }
</script>
