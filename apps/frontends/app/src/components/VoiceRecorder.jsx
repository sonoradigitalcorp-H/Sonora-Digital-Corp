import { useState, useRef, useCallback } from 'react'

const MIME_TYPE = 'audio/webm'

export default function VoiceRecorder({ onTranscript, onError, tenantId = 'default' }) {
  const [recording, setRecording] = useState(false)
  const [processing, setProcessing] = useState(false)
  const mediaRecorder = useRef(null)
  const chunks = useRef([])
  const stream = useRef(null)

  const startRecording = useCallback(async () => {
    try {
      chunks.current = []
      stream.current = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder.current = new MediaRecorder(stream.current, { mimeType: MIME_TYPE })

      mediaRecorder.current.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.current.push(e.data)
      }

      mediaRecorder.current.onstop = async () => {
        setProcessing(true)
        const blob = new Blob(chunks.current, { type: MIME_TYPE })
        const reader = new FileReader()
        reader.readAsDataURL(blob)
        reader.onloadend = async () => {
          const base64audio = reader.result.split(',')[1]
          try {
            const res = await fetch('/api/voice/stt', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ audio: base64audio, tenant_id: tenantId }),
            })
            const data = await res.json()
            if (data.text) {
              onTranscript?.(data.text)
            } else {
              onError?.(data.error || 'No se pudo transcribir el audio')
            }
          } catch (e) {
            onError?.('Error al enviar audio')
          }
          setProcessing(false)
        }
        // Cleanup
        stream.current?.getTracks().forEach(t => t.stop())
      }

      mediaRecorder.current.start()
      setRecording(true)
    } catch (e) {
      onError?.('Permiso de micrófono denegado')
    }
  }, [tenantId, onTranscript, onError])

  const stopRecording = useCallback(() => {
    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
      mediaRecorder.current.stop()
      setRecording(false)
    }
  }, [])

  const playAudio = useCallback(async (text) => {
    try {
      const res = await fetch('/api/voice/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, tenant_id: tenantId }),
      })
      const data = await res.json()
      if (data.audio_b64) {
        const audio = new Audio(`data:audio/wav;base64,${data.audio_b64}`)
        await audio.play()
      } else if (data.status === 'fallback' && window.speechSynthesis) {
        const utter = new SpeechSynthesisUtterance(text)
        utter.lang = 'es-MX'
        window.speechSynthesis.speak(utter)
      }
    } catch {
      // Fallback al browser TTS
      if (window.speechSynthesis) {
        const utter = new SpeechSynthesisUtterance(text.slice(0, 200))
        utter.lang = 'es-MX'
        window.speechSynthesis.speak(utter)
      }
    }
  }, [tenantId])

  return {
    isRecording: recording,
    isProcessing: processing,
    startRecording,
    stopRecording,
    playAudio,
    VoiceButton: () => (
      <button
        type="button"
        onClick={recording ? stopRecording : startRecording}
        disabled={processing}
        className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
          recording
            ? 'bg-[#ef4444] animate-pulse shadow-lg shadow-[#ef4444]/40'
            : processing
            ? 'bg-[#f59e0b]'
            : 'bg-white/[0.06] hover:bg-white/[0.1]'
        }`}
        title={recording ? 'Detener grabación' : 'Grabar audio'}
      >
        {processing ? (
          <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : recording ? (
          <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
            <rect x="6" y="4" width="4" height="16" rx="1" />
            <rect x="14" y="4" width="4" height="16" rx="1" />
          </svg>
        ) : (
          <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
          </svg>
        )}
      </button>
    ),
  }
}
