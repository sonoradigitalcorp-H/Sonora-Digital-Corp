<template>
  <section class="pt-24 px-5 max-w-6xl mx-auto pb-16">
    <div class="flex items-center gap-3 mb-8">
      <button @click="$router.back()" class="w-11 h-11 rounded-xl glass hover:bg-white/10 flex items-center justify-center text-xl" title="Regresar">←</button>
      <div>
        <div class="text-emerald-400 text-xs font-bold tracking-[.25em] uppercase">Servicios</div>
        <h1 class="text-3xl font-extrabold">Toca la tarjeta, <span class="grad-text">mira los beneficios</span></h1>
      </div>
    </div>
    <p class="text-zinc-500 mb-8 max-w-xl">Nos encargamos de tus dolores de cabeza, estrés y pendientes. Cada tarjeta se voltea y muestra lo que ganas.</p>
    <div class="grid grid-cols-2 lg:grid-cols-3 gap-5">
      <div v-for="(s,i) in SVC" :key="i" class="flip h-60" :class="{on: s.on}" @click="s.on=!s.on">
        <div class="flip-in">
          <div class="flip-face glass flex flex-col justify-center p-5">
            <div class="text-3xl mb-3">{{ s.ic }}</div>
            <h3 class="font-extrabold text-lg">{{ s.t }}</h3>
            <p class="text-zinc-400 text-xs mt-2 leading-relaxed">{{ s.f }}</p>
            <div class="mt-auto text-[10px] tracking-widest text-zinc-500">TOCA PARA VER</div>
          </div>
          <div class="flip-face flip-back flex flex-col justify-center p-5" :style="'background:linear-gradient(150deg,'+s.g+');color:#fff'">
            <div class="text-2xl mb-2">{{ s.ic }}</div>
            <h4 class="font-extrabold text-sm mb-3">Nos ocupamos de tu tranquilidad</h4>
            <ul class="text-xs space-y-2">
              <li v-for="b in s.b" :key="b[0]"><b>{{ b[0] }}:</b> {{ b[1] }}</li>
            </ul>
            <a :href="waLink(s.wa)" target="_blank" class="mt-auto text-center bg-white/20 rounded-xl py-2 font-bold text-xs hover:bg-white/30 transition">Cotizar por WhatsApp</a>
          </div>
        </div>
      </div>
    </div>
    <div class="mt-10 text-center">
      <router-link to="/asistente" class="inline-block px-8 py-4 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold transition">Preguntar al asistente</router-link>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { waLink } from '../composables/useChat'

const SVC = ref([
  { ic:'🧾', t:'Contabilidad', wa:'Contabilidad mensual', f:'Estados financieros, IVA e ISR al día, sin sorpresas.', g:'#0e8a6d,#0a5f4a', b:[['Orden','contabilidad mensual, IVA e ISR'],['Tranquilidad','cero multas ni sorpresas'],['Tiempo','recuperas ~8 horas al mes']] },
  { ic:'⚙️', t:'Administración', wa:'Administración', f:'Nómina, flujo de caja y gastos bajo control.', g:'#2563eb,#1e3a8a', b:[['Orden','nómina y flujo de caja claros'],['Control','decisiones con datos'],['Tiempo','+16 horas al mes']] },
  { ic:'🚢', t:'Importaciones', wa:'Manifestación de importación', f:'Manifestación de importación y requisitos en regla.', g:'#0ea5e9,#075985', b:[['Tranquilidad','tu mercancía cruza sin retrasos'],['Orden','papeles en regla'],['Apoyo','despacho sin atascos']] },
  { ic:'📈', t:'Marketing', wa:'Marketing para mi negocio', f:'Presencia y campañas para crecer tu negocio.', g:'#f59e0b,#92400e', b:[['Crecimiento','más clientes'],['Orden','campañas enfocadas'],['Tiempo','nosotros lo gestionamos']] },
  { ic:'🗂️', t:'Consultas SAT', wa:'Consulta ante el SAT', f:'Aclaraciones y trámites ante el SAT.', g:'#6d28d9,#4c1d95', b:[['Tranquilidad','no te bloquean ni multan'],['Apoyo','trámites sin vueltas'],['Tiempo','resolvemos por ti']] },
  { ic:'📅', t:'Citas SAT', wa:'Cita ante el SAT', f:'Agendamos tu cita ante el SAT por ti.', g:'#db2777,#831843', b:[['Tiempo','sin filas ni esperas'],['Orden','fecha asegurada'],['Apoyo','te acompañamos']] },
])
</script>