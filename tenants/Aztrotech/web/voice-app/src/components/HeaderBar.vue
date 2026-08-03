<template>
  <header class="flex items-center justify-between px-4 md:px-6 py-3 bg-black/40 backdrop-blur-xl border-b border-white/5">
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-aztrotech-primary to-aztrotech-accent flex items-center justify-center text-sm font-bold shadow-lg shadow-aztrotech-primary/20">A</div>
      <div>
        <h1 class="text-sm font-bold">Aztrotech <span class="text-aztrotech-primary font-light">AI</span></h1>
        <p class="text-[10px] text-white/40">Asistente de César Holguín</p>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <a v-for="link in social" :key="link.url" :href="link.url" target="_blank"
         class="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 border border-white/8 text-xs text-white/70 hover:bg-aztrotech-primary/20 hover:text-aztrotech-primary hover:border-aztrotech-primary/30 transition-all">
        <span>{{ link.icon }}</span>
        <span class="hidden lg:inline">{{ link.label }}</span>
      </a>
    </div>
  </header>
</template>

<script setup>
const emit = defineEmits(['navigate'])
const social = [
  { icon: '📱', label: 'WhatsApp', url: 'https://wa.me/5216621072254' },
  { icon: '📸', label: 'Instagram', url: 'https://instagram.com/cesarholguin' },
  { icon: '💼', label: 'LinkedIn', url: 'https://linkedin.com/in/cesarholguin' },
  { icon: '🤖', label: 'Telegram', url: 'https://t.me/AztroTechBot' },
  { icon: '🌐', label: 'Web', url: 'https://aztrotech.mx' }
]
</script>
