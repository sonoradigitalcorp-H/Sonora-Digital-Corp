<template>
  <div class="h-full flex flex-col items-center justify-center px-4 py-8">
    <h2 class="text-xl font-bold mb-1">📅 Agenda de César</h2>
    <p class="text-white/50 text-sm mb-6">Selecciona el horario que mejor te acomode</p>

    <!-- Period Selection -->
    <div v-if="!selectedPeriod" class="flex gap-3 mb-8">
      <button @click="selectPeriod('morning')" class="px-6 py-4 rounded-2xl bg-aztrotech-warm/10 border border-aztrotech-warm/20 hover:border-aztrotech-warm/50 transition-all text-center">
        <div class="text-2xl mb-1">☀️</div>
        <div class="font-semibold text-sm">Mañana</div>
        <div class="text-white/40 text-xs">8am - 12pm</div>
      </button>
      <button @click="selectPeriod('afternoon')" class="px-6 py-4 rounded-2xl bg-aztrotech-accent/10 border border-aztrotech-accent/20 hover:border-aztrotech-accent/50 transition-all text-center">
        <div class="text-2xl mb-1">🌙</div>
        <div class="font-semibold text-sm">Tarde</div>
        <div class="text-white/40 text-xs">1pm - 6pm</div>
      </button>
      <button @click="selectPeriod('any')" class="px-6 py-4 rounded-2xl bg-aztrotech-primary/10 border border-aztrotech-primary/20 hover:border-aztrotech-primary/50 transition-all text-center">
        <div class="text-2xl mb-1">🕐</div>
        <div class="font-semibold text-sm">Lo que haya</div>
        <div class="text-white/40 text-xs">8am - 6pm</div>
      </button>
    </div>

    <!-- Time Grid -->
    <div v-if="selectedPeriod" class="w-full max-w-lg mb-6">
      <button @click="selectedPeriod=null" class="text-white/40 text-sm mb-4 hover:text-white">⬅️ Cambiar período</button>
      
      <div class="text-sm font-semibold mb-3" :class="selectedPeriod==='morning'?'text-aztrotech-warm':'text-aztrotech-accent'">
        {{ selectedPeriod==='morning'?'☀️ Mañana':'🌙 Tarde' }} — Horarios disponibles
      </div>
      
      <div class="grid grid-cols-3 md:grid-cols-4 gap-2">
        <button v-for="h in filteredHours" :key="h" @click="selectTime(h)" :class="['p-3 rounded-xl border text-center transition-all', selectedTime===h ? 'bg-aztrotech-success border-aztrotech-success text-white scale-105' : 'bg-white/[0.03] border-white/8 hover:border-aztrotech-primary/40 hover:bg-aztrotech-primary/10']">
          <div class="font-bold text-sm">{{ h }}</div>
        </button>
      </div>
    </div>

    <!-- Name Input -->
    <div v-if="selectedTime && !userName" class="w-full max-w-lg animate-fade-in">
      <p class="text-white/60 text-sm mb-3 text-center">Horario: <strong class="text-aztrotech-primary">{{ selectedTime }}</strong> — ¿Cómo te llamas?</p>
      <div class="flex gap-2">
        <input v-model="nameInput" placeholder="Tu nombre" class="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white text-sm outline-none focus:border-aztrotech-primary" @keyup.enter="confirmName" />
        <button @click="confirmName" class="px-5 py-3 rounded-xl bg-aztrotech-primary text-black font-semibold text-sm hover:scale-105 transition-all">→</button>
      </div>
    </div>

    <!-- Confirm -->
    <div v-if="userName" class="animate-fade-in text-center">
      <p class="text-white/60 text-sm mb-4">¿Confirmar cita?</p>
      <div class="bg-white/[0.03] border border-white/8 rounded-2xl p-5 mb-6 inline-block">
        <div class="text-lg font-bold mb-1">{{ userName }}</div>
        <div class="text-aztrotech-primary font-semibold">{{ selectedTime }}</div>
        <div class="text-white/40 text-xs mt-1">Llamada con César Holguín · 15 min</div>
      </div>
      <div class="flex gap-3 justify-center">
        <button @click="reset" class="px-5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-sm hover:bg-white/10 transition-all">Cancelar</button>
        <button @click="confirm" class="px-6 py-2.5 rounded-xl bg-aztrotech-success text-white font-semibold text-sm hover:scale-105 transition-all shadow-lg shadow-aztrotech-success/30">✅ Confirmar</button>
      </div>
    </div>

    <!-- Chat -->
    <div class="w-full max-w-lg mt-6 space-y-3">
      <div v-for="(m,i) in messages" :key="i" :class="['px-4 py-3 rounded-2xl text-sm leading-relaxed max-w-[85%] animate-fade-in', m.role==='bot'?'bg-white/5 border border-white/5 self-start':'bg-aztrotech-primary text-black self-end ml-auto']" v-html="m.text"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
const emit = defineEmits(['action'])

const selectedPeriod = ref(null)
const selectedTime = ref(null)
const userName = ref('')
const nameInput = ref('')
const messages = ref([])

const morningHours = ['8:00 AM','9:00 AM','10:00 AM','11:00 AM']
const afternoonHours = ['1:00 PM','2:00 PM','3:00 PM','4:00 PM','5:00 PM']

const filteredHours = computed(() => {
  if (selectedPeriod.value === 'morning') return morningHours
  if (selectedPeriod.value === 'afternoon') return afternoonHours
  return [...morningHours, ...afternoonHours]
})

onMounted(() => {
  addBot('¿Te queda mejor por la <strong>mañana</strong> o por la <strong>tarde</strong>? César está disponible de 8am a 6pm.')
  window.addEventListener('user-speech', onSpeech)
})
onUnmounted(() => window.removeEventListener('user-speech', onSpeech))

function selectPeriod(p) {
  selectedPeriod.value = p
  const label = p === 'morning' ? 'la mañana' : p === 'afternoon' ? 'la tarde' : 'cualquier horario'
  addBot(`Perfecto, selecciona el horario en <strong>${label}</strong> que mejor te acomode 👆`)
}

function selectTime(t) { selectedTime.value = t }

function confirmName() {
  if (!nameInput.value.trim()) return
  userName.value = nameInput.value.trim()
  addBot(`Listo <strong>${userName.value}</strong>, ¿confirmas tu cita para las <strong>${selectedTime.value}</strong>?`)
}

function confirm() {
  emit('action', 'schedule', {
    name: userName.value,
    time: selectedTime.value,
    date: new Date().toISOString().split('T')[0]
  })
}

function reset() {
  selectedPeriod.value = null
  selectedTime.value = null
  userName.value = ''
  nameInput.value = ''
}

function onSpeech(e) {
  const t = e.detail.toLowerCase()
  if (t.includes('mañana') || t.includes('manana')) selectPeriod('morning')
  else if (t.includes('tarde')) selectPeriod('afternoon')
  else if (!selectedPeriod.value) selectPeriod('any')
  else if (t.includes('confirmar') || t.includes('confirmo')) confirm()
  else if (!userName.value && t.length < 30) { nameInput.value = e.detail; confirmName() }
}

function addBot(t) { messages.value.push({ role: 'bot', text: t }) }
function addUser(t) { messages.value.push({ role: 'user', text: t }) }
</script>
