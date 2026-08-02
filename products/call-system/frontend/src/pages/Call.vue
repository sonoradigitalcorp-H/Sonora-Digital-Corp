<template>
  <div class="min-h-screen bg-[#08090f] text-white font-sans flex flex-col">
    <!-- Simple nav -->
    <nav class="flex items-center justify-between px-6 py-4 border-b border-white/5">
      <a href="/" class="flex items-center gap-2 text-sm">
        <span class="text-[#CD8D5D]">⟵</span> Volver
      </a>
      <div class="flex items-center gap-3 text-xs text-white/40">
        <span :class="statusClass">{{ statusText }}</span>
        <span>{{ timer }}</span>
      </div>
    </nav>

    <!-- Orbe + Chat -->
    <div class="flex-1 flex flex-col items-center justify-center p-6 gap-8">
      <!-- Orbe -->
      <div class="w-48 h-48 rounded-full bg-gradient-to-br from-[#AC6D3E]/20 to-[#CD8D5D]/5 flex items-center justify-center cursor-pointer relative"
           :class="{ 'animate-pulse-slow': isCalling }" @click="toggleCall">
        <div class="absolute inset-4 rounded-full bg-gradient-to-br from-[#AC6D3E]/10 to-transparent animate-spin-slow"></div>
        <span class="text-4xl opacity-60">{{ isCalling ? '◉' : '📞' }}</span>
        <div v-if="!isCalling" class="absolute -bottom-6 text-xs text-white/30">Toca para llamar</div>
        <div v-if="isCalling" class="absolute -bottom-6 text-xs text-[#4ade80]">En llamada...</div>
      </div>

      <!-- Chat -->
      <div class="w-full max-w-md">
        <div ref="chatLog" class="h-64 overflow-y-auto space-y-3 p-4 rounded-xl bg-white/[0.02] border border-white/5 mb-4">
          <div v-for="(m, i) in messages" :key="i"
               :class="m.type === 'user' ? 'text-right' : 'text-left'">
            <div :class="m.type === 'user'
              ? 'inline-block bg-[#AC6D3E]/20 text-white/90 px-4 py-2 rounded-2xl rounded-br-md text-sm'
              : 'inline-block bg-white/5 text-white/70 px-4 py-2 rounded-2xl rounded-bl-md text-sm'">
              {{ m.text }}
            </div>
          </div>
          <div v-if="isTyping" class="text-left">
            <div class="inline-block bg-white/5 px-4 py-2 rounded-2xl rounded-bl-md">
              <span class="text-white/40 text-sm">Mystica está escribiendo</span>
            </div>
          </div>
        </div>
        <div class="flex gap-2">
          <input v-model="inputText" @keyup.enter="sendText"
                 placeholder="Escribe un mensaje..."
                 class="flex-1 bg-white/[0.03] border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-white/20 outline-none focus:border-[#AC6D3E]/50 transition" />
          <button @click="sendText"
                  class="px-4 py-3 rounded-xl bg-[#AC6D3E] text-black text-sm font-semibold hover:bg-[#CD8D5D] transition disabled:opacity-30"
                  :disabled="!inputText.trim() || !ws">➤</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const messages = ref([{ type: 'bot', text: 'Haz clic en el orbe para llamar o escribe un mensaje.' }])
const inputText = ref('')
const isCalling = ref(false)
const isTyping = ref(false)
const statusText = ref('Desconectado')
const statusClass = ref('text-white/30')
const timer = ref('00:00')
const chatLog = ref(null)
let ws = null, pc = null, callTimer = null, callStart = null

async function toggleCall() {
  if (isCalling.value) { hangUp(); return }
  isCalling.value = true
  statusText.value = 'Conectando...'
  statusClass.value = 'text-yellow-400'

  try {
    const wsProto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    ws = new WebSocket(`${wsProto}//${location.host}/ws`)
    ws.onopen = async () => {
      pc = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] })
      pc.ontrack = (e) => { const a = document.createElement('audio'); a.srcObject = e.streams[0]; a.autoplay = true }
      const s = await navigator.mediaDevices.getUserMedia({ audio: true })
      s.getTracks().forEach(t => pc.addTrack(t, s))
      pc.onicecandidate = (e) => { if (e.candidate) ws.send(JSON.stringify({ type: 'candidate', candidate: e.candidate })) }
      const o = await pc.createOffer(); await pc.setLocalDescription(o)
      ws.send(JSON.stringify({ type: 'offer', sdp: o.sdp }))
    }
    ws.onmessage = (e) => {
      const m = JSON.parse(e.data)
      if (m.type === 'answer') {
        pc.setRemoteDescription(new RTCSessionDescription({ type: 'answer', sdp: m.sdp }))
        statusText.value = 'En llamada'; statusClass.value = 'text-[#4ade80]'
        callStart = Date.now()
        callTimer = setInterval(() => {
          const sec = Math.floor((Date.now() - callStart) / 1000)
          timer.value = String(Math.floor(sec / 60)).padStart(2, '0') + ':' + String(sec % 60).padStart(2, '0')
        }, 1000)
      }
      if (m.type === 'candidate' && pc?.remoteDescription) pc.addIceCandidate(new RTCIceCandidate(m.candidate)).catch(() => {})
      if (m.type === 'transcript') { messages.value.push({ type: 'user', text: m.text }); scrollChat() }
      if (m.type === 'response') { isTyping.value = false; messages.value.push({ type: 'bot', text: m.text }); scrollChat() }
      if (m.type === 'close') hangUp()
    }
    ws.onclose = () => { if (isCalling.value) hangUp() }
  } catch (e) { messages.value.push({ type: 'bot', text: 'Error: ' + e.message }); isCalling.value = false; statusText.value = 'Error'; statusClass.value = 'text-red-400' }
}

function hangUp() {
  if (pc) { pc.close(); pc = null }
  if (ws) { ws.close(); ws = null }
  if (callTimer) { clearInterval(callTimer); callTimer = null }
  isCalling.value = false; statusText.value = 'Desconectado'; statusClass.value = 'text-white/30'; timer.value = '00:00'
}

function sendText() {
  const t = inputText.value.trim()
  if (!t || !ws) return
  messages.value.push({ type: 'user', text: t })
  ws.send(JSON.stringify({ type: 'text', text: t }))
  inputText.value = ''
  isTyping.value = true
  scrollChat()
}

function scrollChat() { setTimeout(() => { if (chatLog.value) chatLog.value.scrollTop = chatLog.value.scrollHeight }, 100) }

onUnmounted(() => hangUp())
</script>
