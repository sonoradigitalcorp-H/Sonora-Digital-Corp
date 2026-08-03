<template>
  <div class="h-screen flex flex-col relative overflow-hidden">
    <!-- Dynamic Background -->
    <div class="fixed inset-0 z-0 transition-all duration-1000" :class="bgClass"></div>
    
    <!-- Three.js Canvas -->
    <ThreeBG ref="threeBg" class="fixed inset-0 z-0" />

    <!-- Header -->
    <HeaderBar @navigate="goTo" class="relative z-10" />

    <!-- Main Content -->
    <main class="flex-1 relative z-10 overflow-y-auto">
      <Transition name="scene" mode="out-in">
        <SceneGreeting v-if="scene==='greeting'" key="greeting" @action="handleAction" />
        <SceneServices v-else-if="scene==='services'" key="services" @action="handleAction" />
        <SceneSchedule v-else-if="scene==='schedule'" key="schedule" @action="handleAction" />
        <SceneConfirmed v-else-if="scene==='confirmed'" key="confirmed" :data="scheduleData" @action="handleAction" />
      </Transition>
    </main>

    <!-- Bottom Bar -->
    <BottomBar :is-recording="isRecording" @mic="toggleMic" class="relative z-10" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ThreeBG from './components/ThreeBG.vue'
import HeaderBar from './components/HeaderBar.vue'
import BottomBar from './components/BottomBar.vue'
import SceneGreeting from './components/SceneGreeting.vue'
import SceneServices from './components/SceneServices.vue'
import SceneSchedule from './components/SceneSchedule.vue'
import SceneConfirmed from './components/SceneConfirmed.vue'
import { useVoice } from './composables/useVoice'

const scene = ref('greeting')
const isRecording = ref(false)
const scheduleData = ref({})
const threeBg = ref(null)

const { startRecording, stopRecording } = useVoice(onSpeech)

const bgClass = computed(() => ({
  'bg-gradient-to-br from-[#0a0a12] via-[#0d1525] to-[#0a0a12]': scene.value==='greeting',
  'bg-gradient-to-br from-[#0a0a12] via-[#0d1a2d] to-[#0a0a12]': scene.value==='services',
  'bg-gradient-to-br from-[#0a0a12] via-[#1a1520] to-[#0a0a12]': scene.value==='schedule',
  'bg-gradient-to-br from-[#0a0a12] via-[#0d2018] to-[#0a0a12]': scene.value==='confirmed'
}))

function goTo(s) { scene.value = s }

function handleAction(type, data) {
  if (type==='schedule') { scheduleData.value = data || {}; scene.value = 'confirmed' }
  else if (type==='services') scene.value = 'services'
  else if (type==='schedule-view') scene.value = 'schedule'
  else if (type==='home') scene.value = 'greeting'
}

function toggleMic() {
  if (isRecording.value) { stopRecording(); isRecording.value = false }
  else { startRecording(); isRecording.value = true }
}

function onSpeech(text) {
  // Emit to current scene
  window.dispatchEvent(new CustomEvent('user-speech', { detail: text }))
}
</script>

<style>
.scene-enter-active { animation: fade-in 0.4s ease; }
.scene-leave-active { animation: fade-in 0.3s ease reverse; }
</style>
