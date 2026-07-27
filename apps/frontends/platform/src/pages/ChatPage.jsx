import { useState, useRef, useEffect, useCallback } from 'react'
import { createChatSocket } from '../lib/ws'

export default function ChatPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [connected, setConnected] = useState(false)
  const [streaming, setStreaming] = useState('')
  const wsRef = useRef(null)
  const msgEnd = useRef(null)

  useEffect(() => {
    scrollToBottom()
  }, [messages, streaming])

  function scrollToBottom() {
    msgEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    const socket = createChatSocket((data) => {
      switch (data.type) {
        case 'connected':
          setConnected(true)
          break
        case 'disconnected':
          setConnected(false)
          break
        case 'orb.state':
          break
        case 'token':
          setStreaming((prev) => prev + (data.text || ''))
          break
        case 'result': {
          const text = data.text || data.content || ''
          setMessages((prev) => [...prev, { role: 'assistant', text }])
          setStreaming('')
          break
        }
        default:
          if (data.text) {
            setMessages((prev) => [...prev, { role: 'assistant', text: data.text }])
            setStreaming('')
          }
      }
    })

    wsRef.current = socket
    return () => socket.close()
  }, [])

  const send = useCallback(() => {
    const text = input.trim()
    if (!text || !connected) return
    setMessages((prev) => [...prev, { role: 'user', text }])
    wsRef.current?.send(text)
    setInput('')
    setStreaming('')
  }, [input, connected])

  return (
    <div className="flex-1 flex flex-col h-screen">
      <header className="px-6 py-4 border-b border-[#2a2a2e] flex items-center justify-between shrink-0">
        <div>
          <h2 className="text-lg font-semibold">Chat</h2>
          <p className="text-xs text-[#6e6e73] mt-0.5">Asistente IA — Sonora Digital</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-[#6e6e73]">
          <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-[#22c55e]' : 'bg-[#ef4444]'}`} />
          {connected ? 'Conectado' : 'Reconectando...'}
        </div>
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
        {messages.length === 0 && !streaming && (
          <div className="flex items-center justify-center h-full text-[#6e6e73] text-sm">
            Pregúntame lo que necesites sobre Sonora Digital
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
              m.role === 'user'
                ? 'bg-[#0071e3] text-white rounded-br-md'
                : 'bg-[#1a1a1e] text-[#f5f5f7] rounded-bl-md border border-[#2a2a2e]'
            }`}>
              {m.text}
            </div>
          </div>
        ))}
        {streaming && (
          <div className="flex justify-start">
            <div className="max-w-[75%] px-4 py-2.5 rounded-2xl bg-[#1a1a1e] text-[#f5f5f7] rounded-bl-md border border-[#2a2a2e] text-sm leading-relaxed">
              {streaming}
              <span className="inline-block w-1.5 h-4 bg-[#0071e3] ml-0.5 animate-pulse" />
            </div>
          </div>
        )}
        <div ref={msgEnd} />
      </div>

      <div className="px-6 py-4 border-t border-[#2a2a2e] shrink-0">
        <div className="flex gap-2 max-w-3xl">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
            placeholder="Escribe tu mensaje..."
            className="flex-1 px-4 py-3 rounded-full bg-[#1a1a1e] border border-[#2a2a2e] text-[#f5f5f7] text-sm placeholder-[#6e6e73] focus:outline-none focus:border-[#0071e3]/50 transition-colors"
          />
          <button
            onClick={send}
            disabled={!connected || !input.trim()}
            className="px-6 py-3 rounded-full bg-[#0071e3] hover:bg-[#0066cc] disabled:opacity-30 disabled:cursor-not-allowed transition-all text-sm font-medium shrink-0"
          >
            Enviar
          </button>
        </div>
      </div>
    </div>
  )
}
