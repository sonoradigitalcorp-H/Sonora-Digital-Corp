import { useState, useRef, useCallback, useEffect } from 'react'

const WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/chat/ws`

export default function StreamingChat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [connected, setConnected] = useState(false)
  const ws = useRef(null)
  const msgEnd = useRef(null)
  const [streamingText, setStreamingText] = useState('')

  useEffect(() => {
    connect()
    return () => ws.current?.close()
  }, [])

  useEffect(() => {
    msgEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingText])

  function connect() {
    try {
      ws.current = new WebSocket(WS_URL)
      ws.current.onopen = () => setConnected(true)
      ws.current.onmessage = (e) => {
        const data = JSON.parse(e.data)
        if (data.type === 'token') {
          setStreamingText((prev) => prev + data.text)
        } else if (data.type === 'done') {
          setMessages((prev) => [...prev, { role: 'assistant', text: data.text }])
          setStreamingText('')
        } else if (data.type === 'error') {
          setMessages((prev) => [...prev, { role: 'system', text: '⚠️ ' + data.text }])
          setStreamingText('')
        }
      }
      ws.current.onclose = () => {
        setConnected(false)
        setTimeout(connect, 3000)
      }
      ws.current.onerror = () => ws.current?.close()
    } catch {
      setTimeout(connect, 3000)
    }
  }

  const send = useCallback(() => {
    const text = input.trim()
    if (!text || !ws.current || ws.current.readyState !== WebSocket.OPEN) return
    setMessages((prev) => [...prev, { role: 'user', text }])
    ws.current.send(JSON.stringify({ type: 'message', text }))
    setInput('')
    setStreamingText('')
  }, [input])

  return (
    <div className="flex flex-col h-[500px] bg-[#161b22] rounded-2xl border border-[#30363d] overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-[#30363d]">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${connected ? 'bg-[#22c55e]' : 'bg-[#ef4444]'}`} />
          <span className="text-sm text-white/70">Mystic — Asistente IA</span>
        </div>
        <span className="text-xs text-white/30">{connected ? '🟢 En vivo' : '🔴 Reconectando...'}</span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && !streamingText && (
          <div className="text-center py-12 text-white/30 text-sm">
            Pregúntame sobre nuestros productos o cómo podemos ayudarte.
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] px-4 py-2.5 rounded-2xl text-sm ${
              m.role === 'user'
                ? 'bg-[#7c5cfc] text-white rounded-br-md'
                : m.role === 'system'
                ? 'bg-[#f59e0b]/10 text-[#f59e0b] border border-[#f59e0b]/20'
                : 'bg-[#1c2128] text-[#c9d1d9] rounded-bl-md'
            }`}>
              {m.text}
            </div>
          </div>
        ))}
        {streamingText && (
          <div className="flex justify-start">
            <div className="max-w-[85%] px-4 py-2.5 rounded-2xl bg-[#1c2128] text-[#c9d1d9] rounded-bl-md text-sm">
              {streamingText}
              <span className="inline-block w-1.5 h-4 bg-[#7c5cfc] ml-0.5 animate-pulse" />
            </div>
          </div>
        )}
        <div ref={msgEnd} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-[#30363d]">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
            placeholder="Escribe tu mensaje..."
            className="flex-1 px-4 py-2.5 rounded-xl bg-[#0a0a0a] border border-[#30363d] text-white text-sm placeholder-white/20 focus:outline-none focus:border-[#7c5cfc]/40"
          />
          <button
            onClick={send}
            disabled={!connected || !input.trim()}
            className="px-5 py-2.5 rounded-xl bg-[#7c5cfc] hover:bg-[#6a4ae0] disabled:opacity-30 transition-all text-sm font-medium"
          >
            Enviar
          </button>
        </div>
      </div>
    </div>
  )
}
