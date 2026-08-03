<template>
  <div class="h-full flex flex-col items-center justify-center px-4 py-8">
    <!-- Orb -->
    <div class="relative mb-6 animate-float cursor-pointer" @click="$emit('action','services')">
      <div class="w-32 h-32 md:w-40 md:h-40 rounded-full bg-gradient-to-br from-aztrotech-primary/50 to-aztrotech-accent/30 shadow-[0_0_60px_rgba(0,212,255,0.3)] flex items-center justify-center">
        <span class="text-4xl md:text-5xl">✦</span>
      </div>
      <div v-for="i in 3" :key="i" class="absolute rounded-full border border-aztrotech-primary/15"
           :style="{width:`${140+i*30}px`,height:`${140+i*30}px`,top:`${50}%,left:50%`,transform:'translate(-50%,-50%)',animation:`pulse-ring 3s ease-out infinite ${i*0.5}s`}"></div>
    </div>

    <p class="text-white/50 text-sm mb-8 text-center">Hola, soy <strong class="text-aztrotech-primary">el asistente de César</strong><br>Habla conmigo o elige una opción</p>

    <!-- Carousel -->
    <div class="w-full max-w-2xl mb-8">
      <div ref="carousel" class="flex gap-4 overflow-x-auto snap-x snap-mandatory scrollbar-hide pb-4" style="scrollbar-width:none">
        <div v-for="(b,i) in benefits" :key="i" class="flex-none w-64 md:w-72 snap-center rounded-2xl border border-white/8 bg-white/[0.03] backdrop-blur-sm overflow-hidden hover:border-aztrotech-primary/30 transition-all cursor-pointer group" @click="$emit('action','schedule-view')">
          <div class="h-32 md:h-36 bg-gradient-to-br flex items-center justify-center text-5xl" :class="b.gradient">{{ b.icon }}</div>
          <div class="p-4">
            <h3 class="font-bold text-sm mb-1">{{ b.title }}</h3>
            <p class="text-white/50 text-xs leading-relaxed">{{ b.desc }}</p>
          </div>
        </div>
      </div>
      <!-- Dots -->
      <div class="flex justify-center gap-1.5 mt-3">
        <div v-for="i in benefits.length" :key="i" class="w-1.5 h-1.5 rounded-full" :class="i===currentSlide?'bg-aztrotech-primary':'bg-white/20'"></div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="flex flex-wrap justify-center gap-2">
      <button v-for="a in actions" :key="a.label" @click="$emit('action',a.event)" class="px-5 py-2.5 rounded-full bg-aztrotech-primary/10 border border-aztrotech-primary/20 text-aztrotech-primary text-sm font-medium hover:bg-aztrotech-primary hover:text-black transition-all">
        {{ a.icon }} {{ a.label }}
      </button>
    </div>

    <!-- Chat Bubbles -->
    <div ref="chatArea" class="w-full max-w-lg mt-6 space-y-3 max-h-48 overflow-y-auto">
      <div v-for="(m,i) in messages" :key="i" :class="['px-4 py-3 rounded-2xl text-sm leading-relaxed max-w-[85%] animate-fade-in', m.role==='bot'?'bg-white/5 border border-white/5 self-start':'bg-aztrotech-primary text-black self-end ml-auto']" v-html="m.text"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['action'])
const messages = ref([])
const currentSlide = ref(0)

const benefits = [
  { icon: '⏰', title: 'Libertad de tiempo', desc: 'Mientras duermes, tu agente vende y atiende 24/7', gradient: 'from-aztrotech-primary/20 to-blue-900/30' },
  { icon: '📈', title: 'Ventas sin parar', desc: 'Nunca pierdes un lead. Cada mensaje es una oportunidad', gradient: 'from-aztrotech-accent/20 to-purple-900/30' },
  { icon: '🤖', title: 'IA que trabaja por ti', desc: 'El equivalente a 3 empleados, sin sueldo ni vacaciones', gradient: 'from-aztrotech-success/20 to-emerald-900/30' },
  { icon: '🚀', title: '+50% en ventas', desc: 'Empresas reales ya escalan con sistemas Aztrotech', gradient: 'from-aztrotech-warm/20 to-amber-900/30' }
]

const actions = [
  { icon: '📅', label: 'Agendar con César', event: 'schedule-view' },
  { icon: '🤖', label: 'Ver servicios', event: 'services' },
  { icon: '💬', label: 'Hablar con asistente', event: 'services' }
]

onMounted(() => {
  addBot('¡Hola! Soy el asistente de <strong>César Holguín</strong>. Desliza para ver lo que podemos hacer por tu negocio 👇')
  window.addEventListener('user-speech', onSpeech)
  autoSlide()
})

onUnmounted(() => window.removeEventListener('user-speech', onSpeech))

function onSpeech(e) {
  addUser(e.detail)
  setTimeout(() => {
    const t = e.detail.toLowerCase()
    if (t.includes('agendar') || t.includes('cita') || t.includes('llamada')) {
      addBot('¡Perfecto! Veo la agenda de César para que elijas tu horario 👇')
      emit('action', 'schedule-view')
    } else if (t.includes('servicio') || t.includes('qué hacen') || t.includes('ofrecen')) {
      addBot('Tenemos Empleado Digital, Sistema de Ventas y Software a Medida. Te muestro los detalles 👇')
      emit('action', 'services')
    } else {
      addBot('Puedo ayudarte a <strong>agendar una llamada con César</strong> o <strong>conocer nuestros servicios</strong>. ¿Cuál prefieres?')
    }
  }, 500)
}

function addBot(t) { messages.value.push({ role: 'bot', text: t }) }
function addUser(t) { messages.value.push({ role: 'user', text: t }) }

function autoSlide() {
  setInterval(() => { currentSlide.value = (currentSlide.value + 1) % benefits.length }, 4000)
}
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
