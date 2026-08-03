<template>
  <div class="px-4 md:px-6 py-3 bg-black/40 backdrop-blur-xl border-t border-white/5 flex items-center justify-between">
    <div class="text-[11px] text-white/30">
      <span class="text-aztrotech-primary">●</span> En línea · Disponible 24/7
    </div>
    <button @click="$emit('mic')" :class="['w-14 h-14 rounded-full border-none flex items-center justify-center text-xl transition-all shadow-lg', isRecording ? 'bg-red-500 text-white shadow-red-500/40 animate-pulse' : 'bg-aztrotech-primary text-black shadow-aztrotech-primary/40 hover:scale-105']">
      {{ isRecording ? '🔴' : '🎤' }}
    </button>
    <div class="text-[11px] text-white/30 text-right">
      Powered by <span class="text-aztrotech-primary">Sonora Digital Corp</span>
    </div>
  </div>
</template>

<script setup>
defineProps({ isRecording: Boolean })
defineEmits(['mic'])
</script>
