<template>
  <div class="h-full flex flex-col items-center justify-center px-4 py-8">
    <h2 class="text-xl font-bold mb-2">Qué construimos</h2>
    <p class="text-white/50 text-sm mb-8 text-center max-w-md">Diagnosticamos, diseñamos, construimos y implementamos. No entregamos recomendaciones — entregamos sistemas funcionando.</p>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl w-full mb-8">
      <div v-for="(s,i) in services" :key="i" class="rounded-2xl border border-white/8 bg-white/[0.03] p-5 hover:border-aztrotech-primary/30 transition-all cursor-pointer group" @click="selectService(i)">
        <div class="text-3xl mb-3">{{ s.icon }}</div>
        <h3 class="font-bold text-sm mb-2">{{ s.title }}</h3>
        <p class="text-white/40 text-xs leading-relaxed mb-3">{{ s.desc }}</p>
        <div class="flex flex-wrap gap-1.5">
          <span v-for="t in s.tags" :key="t" class="px-2 py-0.5 rounded-full bg-aztrotech-primary/10 text-aztrotech-primary text-[10px]">{{ t }}</span>
        </div>
      </div>
    </div>

    <button @click="$emit('action','schedule-view')" class="px-6 py-3 rounded-full bg-aztrotech-primary text-black font-semibold hover:scale-105 transition-all shadow-lg shadow-aztrotech-primary/30">
      📅 Agendar llamada con César
    </button>

    <button @click="$emit('action','home')" class="mt-4 text-white/40 text-sm hover:text-white transition-colors">⬅️ Volver al inicio</button>

    <!-- Chat -->
    <div class="w-full max-w-lg mt-6 space-y-3">
      <div v-for="(m,i) in messages" :key="i" :class="['px-4 py-3 rounded-2xl text-sm leading-relaxed max-w-[85%] animate-fade-in', m.role==='bot'?'bg-white/5 border border-white/5 self-start':'bg-aztrotech-primary text-black self-end ml-auto']" v-html="m.text"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
const emit = defineEmits(['action'])
const messages = ref([])

const services = [
  { icon: '🤖', title: 'Empleado Digital', desc: 'Agente IA que atiende y vende en WhatsApp, Instagram y Facebook — 24/7.', tags: ['WhatsApp', 'Instagram', 'Facebook', '24/7'] },
  { icon: '⚡', title: 'Automatizaciones', desc: 'Flujos que eliminan trabajo repetitivo y reportes automáticos para decidir con datos.', tags: ['CRM', 'Reportes', 'Integraciones'] },
  { icon: '🏗️', title: 'Software a Medida', desc: 'CRM, ERP o plataforma exacta para tu operación, con IA integrada.', tags: ['Apps', 'APIs', 'Dashboards'] }
]

onMounted(() => {
  addBot('Estos son nuestros tres pilares. <strong>¿Cuál te interesa más?</strong> Puedo contarte los detalles o agendar una llamada con César para un diagnóstico gratuito.')
  window.addEventListener('user-speech', onSpeech)
})
onUnmounted(() => window.removeEventListener('user-speech', onSpeech))

function selectService(i) {
  const s = services[i]
  addBot(`<strong>${s.title}</strong>: ${s.desc} ¿Te gustaría agendar una llamada para conocer más?`)
}

function onSpeech(e) {
  const t = e.detail.toLowerCase()
  if (t.includes('agendar') || t.includes('cita')) {
    addBot('¡Genial! Te muestro la agenda de César 👇')
    emit('action', 'schedule-view')
  } else {
    addBot('¿Te interesa alguno de estos servicios? Puedo contarte más o agendar con César.')
  }
}

function addBot(t) { messages.value.push({ role: 'bot', text: t }) }
function addUser(t) { messages.value.push({ role: 'user', text: t }) }
</script>
