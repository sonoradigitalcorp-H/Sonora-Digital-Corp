import { ref } from 'vue'

export function useVoice(onResult) {
  const isRecording = ref(false)
  let recognition = null

  function startRecording() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.warn('Speech recognition not supported')
      return
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    recognition = new SR()
    recognition.lang = 'es-MX'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onresult = (e) => {
      const text = e.results[0][0].transcript
      isRecording.value = false
      if (onResult) onResult(text)
    }

    recognition.onerror = () => { isRecording.value = false }
    recognition.onend = () => { isRecording.value = false }

    recognition.start()
    isRecording.value = true
  }

  function stopRecording() {
    if (recognition) try { recognition.stop() } catch (e) {}
    isRecording.value = false
  }

  function speak(text) {
    if (!window.speechSynthesis) return
    const u = new SpeechSynthesisUtterance(text.replace(/<[^>]*>/g, ''))
    u.lang = 'es-MX'
    u.rate = 1.1
    u.pitch = 1
    window.speechSynthesis.cancel()
    window.speechSynthesis.speak(u)
  }

  return { isRecording, startRecording, stopRecording, speak }
}
