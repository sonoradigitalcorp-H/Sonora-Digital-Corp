import { ref, onUnmounted } from 'vue'

export const WA = '5216623498589'
export const API = 'https://sonoradigitalcorp.com/chat'
export const waLink = (servicio) => `https://wa.me/${WA}?text=${encodeURIComponent('Hola Nathaly, quiero información sobre ' + servicio)}`

const clean = (t) => (t || '').replace(/[!¡?¿*]/g, '').replace(/[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}]/gu, '').replace(/\s+/g, ' ').trim()

let sid = ''
try { sid = localStorage.getItem('naty-sid') || '' } catch (e) {}
if (!sid) { sid = 'web-' + Date.now(); try { localStorage.setItem('naty-sid', sid) } catch (e) {} }

export function useChat(initial = []) {
  const msgs = ref(initial)
  const msg = ref('')
  const busy = ref(false)
  const speaking = ref(false)
  const listening = ref(false)
  let recog = null
  let speech = null

  const scrollDown = async (el) => { await new Promise(r => setTimeout(r, 40)); if (el) el.scrollTop = el.scrollHeight }

  async function send(logEl) {
    const q = msg.value.trim(); if (!q || busy.value) return
    busy.value = true
    msgs.value.push({ who: 'user', t: clean(q) }); msg.value = ''
    await scrollDown(logEl)
    try {
      const r = await fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: q, sid }) })
      const d = await r.json()
      msgs.value.push({ who: 'bot', t: clean(d.respuesta || 'Lo sentimos, no obtuve respuesta.') })
    } catch (e) { msgs.value.push({ who: 'bot', t: 'El asistente está ocupado, intenta en un momento.' }) }
    busy.value = false
    await scrollDown(logEl); speak(msgs.value[msgs.value.length - 1].t)
  }

  function stopSpeaking() {
    try { if (window.speechSynthesis) window.speechSynthesis.cancel() } catch (e) {}
    speaking.value = false
  }

  function speak(t) {
    if (!t) return
    try {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel()
        const u = new SpeechSynthesisUtterance(t); u.lang = 'es-MX'; u.rate = 1.05; u.pitch = 1.0
        u.onend = () => speaking.value = false; u.onerror = () => speaking.value = false
        window.speechSynthesis.speak(u); speaking.value = true; return
      }
    } catch (e) {}
  }

  function stopMic() {
    listening.value = false
    if (recog) { try { recog.stop() } catch (e) {} }
    recog = null
  }

  function toggleMic() {
    if (listening.value) { stopMic(); return }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) { alert('Usa Chrome o Edge para dictado por voz'); return }
    recog = new SR(); recog.lang = 'es-MX'; recog.interimResults = false
    recog.onresult = (e) => { msg.value = e.results[e.results.length - 1][0].transcript.trim(); stopMic(); send() }
    recog.onerror = () => stopMic()
    recog.start(); listening.value = true
  }

  onUnmounted(() => { stopSpeaking(); stopMic() })
  return { msgs, msg, busy, speaking, listening, send, speak, stopSpeaking, toggleMic, scrollDown }
}

// A/B testing: variante guardada en localStorage
export function abVariant(defaultV = 'a') {
  let v = defaultV
  try {
    const params = new URLSearchParams(window.location.hash.split('?')[1] || '')
    if (params.get('ab')) { v = params.get('ab'); localStorage.setItem('naty-ab', v) }
    else v = localStorage.getItem('naty-ab') || defaultV
  } catch (e) {}
  return v
}