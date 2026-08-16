<template>
  <section class="pt-24 px-5 max-w-3xl mx-auto pb-16">
    <div class="flex items-center gap-3 mb-8">
      <button @click="$router.back()" class="w-11 h-11 rounded-xl glass hover:bg-white/10 flex items-center justify-center text-xl" title="Regresar">←</button>
      <div>
        <div class="text-emerald-400 text-xs font-bold tracking-[.25em] uppercase">FAQ</div>
        <h1 class="text-3xl font-extrabold">Preguntas frecuentes</h1>
      </div>
    </div>
    <div class="space-y-3">
      <details v-for="f in FAQ" :key="f.q" class="glass rounded-2xl px-5 py-4 group">
        <summary class="flex justify-between items-center cursor-pointer font-semibold text-sm list-none">{{ f.q }}<span class="text-emerald-400 text-xl transition group-open:rotate-45">+</span></summary>
        <p class="text-zinc-400 text-sm mt-3 leading-relaxed">{{ f.a }}</p>
      </details>
    </div>
    <div class="mt-8 glass rounded-2xl p-5 text-center">
      <p class="text-sm text-zinc-400 mb-3">¿No encuentras tu respuesta? Pregunta al asistente o escríbenos.</p>
      <div class="flex flex-wrap gap-3 justify-center">
        <router-link to="/asistente" class="px-5 py-3 rounded-xl bg-emerald-500 text-black font-bold text-sm transition">Preguntar</router-link>
        <a :href="waLink('Tengo una duda sobre contabilidad')" target="_blank" class="px-5 py-3 rounded-xl glass font-bold text-sm hover:bg-white/10 transition">WhatsApp</a>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { waLink } from '../composables/useChat'
const FAQ = ref([
  { q:'¿Cuánto cuesta la contabilidad mensual?', a:'El costo exacto te lo da Nathaly por WhatsApp o correo según el tamaño de tu negocio. El diagnóstico inicial es gratis.' },
  { q:'¿Qué necesito para empezar?', a:'En el diagnóstico inicial (15 min) revisamos tu situación: si ya llevas contabilidad, tu actividad y qué necesitas cumplir ante el SAT.' },
  { q:'¿Agendan citas ante el SAT?', a:'Sí, agendamos tu cita por ti y te acompañamos en el trámite.' },
  { q:'¿Manejan importaciones?', a:'Sí, manifestación de importación, pedimento y requisitos en regla para que tu mercancía cruce sin retrasos.' },
  { q:'¿Me ayudan a entender las nuevas tecnologías?', a:'Sí, te acompañamos y educamos en herramientas digitales y fiscales para que tu negocio crezca seguro.' },
  { q:'¿Cómo funciona el asistente por voz?', a:'Tocas el micrófono, hablas con naturalidad y el asistente responde al instante, en texto y voz. También puedes escribir.' },
])
</script>