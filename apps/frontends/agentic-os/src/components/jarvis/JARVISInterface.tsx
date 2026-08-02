import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Mic, X, Send, Sparkles, Zap, Bot, Terminal, ChevronUp, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils/helpers'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { useJARVIS } from '@/contexts/JARVISContext'
import { useMotion } from '@/contexts/MotionContext'

interface JARVISInterfaceProps {
  onClose: () => void
  tenantId: string
}

export function JARVISInterface({ onClose, tenantId }: JARVISInterfaceProps) {
  const { 
    status, 
    mode, 
    history, 
    currentAction, 
    capabilities, 
    confidence,
    sendCommand,
    speak,
    listen,
    addMessage,
    clearHistory,
    setMode,
    connectWebSocket,
    disconnectWebSocket,
  } = useJARVIS()
  const { reducedMotion } = useMotion()
  const [input, setInput] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [showCapabilities, setShowCapabilities] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    connectWebSocket(tenantId)
    return () => disconnectWebSocket()
  }, [tenantId, connectWebSocket, disconnectWebSocket])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth' })
  }, [history, reducedMotion])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return
    const cmd = input
    setInput('')
    await sendCommand(cmd)
  }

  const handleVoiceInput = async () => {
    setIsListening(true)
    const transcript = await listen()
    if (transcript) {
      setInput(transcript)
      await sendCommand(transcript)
    }
    setIsListening(false)
  }

  const statusColors = {
    offline: 'text-white/30',
    initializing: 'text-amber-400',
    listening: 'text-green-400',
    thinking: 'text-cyan-400',
    speaking: 'text-purple-400',
    executing: 'text-orange-400',
    error: 'text-red-400',
  }

  const statusIcons = {
    offline: '⭘',
    initializing: '⟳',
    listening: '🎤',
    thinking: '🧠',
    speaking: '🔊',
    executing: '⚡',
    error: '⚠',
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 400 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 400 }}
      transition={{ type: 'spring', damping: 25, stiffness: 300 }}
      className="fixed right-0 top-0 bottom-0 z-50 w-full max-w-xl md:max-w-2xl bg-cosmic-bgSecondary border-l border-cosmic-border flex flex-col"
      role="dialog"
      aria-modal="true"
      aria-label="JARVIS Interface"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-cosmic-border">
        <div className="flex items-center gap-3">
          <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center text-xl', 
            status === 'listening' && 'bg-green-500/20 animate-pulse',
            status === 'thinking' && 'bg-cyan-500/20',
            status === 'speaking' && 'bg-purple-500/20',
            status === 'executing' && 'bg-orange-500/20',
            status === 'error' && 'bg-red-500/20',
            'bg-cosmic-card'
          )}>
            {statusIcons[status]}
          </div>
          <div>
            <h2 className="font-bold text-white">JARVIS</h2>
            <p className={cn('text-xs font-mono', statusColors[status])}>
              {status.toUpperCase()} • {mode.toUpperCase()} • {(confidence * 100).toFixed(0)}%
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={() => setShowCapabilities(!showCapabilities)}>
            <Bot className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={clearHistory}>
            <Terminal className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Current Action */}
      {currentAction && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="px-4 py-2 border-b border-cosmic-border/50"
        >
          <div className="flex items-center gap-2 text-xs">
            <span className={cn('w-2 h-2 rounded-full', 
              currentAction.status === 'running' && 'bg-cyan-400 animate-pulse',
              currentAction.status === 'completed' && 'bg-green-400',
              currentAction.status === 'failed' && 'bg-red-400',
              'bg-amber-400'
            )} />
            <span className="text-white/70">{currentAction.description}</span>
            <span className="text-white/40 ml-auto font-mono">{(currentAction.confidence * 100).toFixed(0)}%</span>
          </div>
        </motion.div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={messagesEndRef}>
        {history.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-white/30">
            <Sparkles className="w-12 h-12 mb-4 opacity-20" />
            <p className="text-center max-w-xs">
              JARVIS autónomo activo. Di "Hey JARVIS" o escribe un comando.
            </p>
            <div className="mt-4 flex flex-wrap gap-2 justify-center">
              {['Provisiona tenant Abe Music', 'Despliega MCP Social', 'Analiza tendencias IG', 'Optimiza pricing $BEAT'].map((s, i) => (
                <Button key={i} variant="ghost" size="sm" onClick={() => sendCommand(s)}>
                  {s}
                </Button>
              ))}
            </div>
          </div>
        )}
        
        {history.map((msg) => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn('flex gap-3', msg.role === 'user' && 'flex-row-reverse')}
          >
            <div className={cn('w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0', 
              msg.role === 'user' ? 'bg-cosmic-primary/20' : 'bg-cosmic-card'
            )}>
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className={cn('max-w-[70%] px-4 py-3 rounded-2xl', 
              msg.role === 'user' ? 'bg-cosmic-primary/30 text-white' : 'bg-cosmic-card border border-cosmic-border text-white/90'
            )}>
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              <p className="text-xs text-white/30 mt-1 font-mono">{new Date(msg.timestamp).toLocaleTimeString()}</p>
            </div>
          </motion.div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-cosmic-border">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Button
            type="button"
            variant={isListening ? 'danger' : 'ghost'}
            size="sm"
            onClick={handleVoiceInput}
            disabled={isListening || status === 'thinking' || status === 'executing'}
            className={isListening ? 'animate-pulse' : ''}
          >
            <Mic className="w-5 h-5" />
          </Button>
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe un comando o pregunta..."
            className="flex-1 cosmic-input resize-none min-h-[44px] max-h-32"
            rows={1}
            disabled={status === 'thinking' || status === 'executing'}
          />
          <Button 
            type="submit" 
            variant="primary" 
            size="sm"
            disabled={!input.trim() || status === 'thinking' || status === 'executing'}
          >
            <Send className="w-5 h-5" />
          </Button>
        </form>

        {/* Capabilities Panel */}
        <AnimatePresence>
          {showCapabilities && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-3 p-3 cosmic-card rounded-xl"
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-white">Capacidades ({capabilities.filter(c => c.enabled).length}/{capabilities.length})</h4>
                <Button variant="ghost" size="sm" onClick={() => setShowCapabilities(false)}>
                  <ChevronUp className="w-4 h-4" />
                </Button>
              </div>
              <div className="grid gap-2 sm:grid-cols-2 max-h-60 overflow-y-auto">
                {capabilities.map(cap => (
                  <label key={cap.id} className="flex items-center gap-2 p-2 cosmic-bg rounded-lg hover:bg-cosmic-border/50 transition-colors cursor-pointer">
                    <input
                      type="checkbox"
                      checked={cap.enabled}
                      onChange={() => null} // toggleCapability(cap.id)
                      className="w-4 h-4 accent-cosmic-primary"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-white truncate">{cap.name}</p>
                      <p className="text-[10px] text-white/40 truncate">{cap.description}</p>
                    </div>
                    <span className={cn('text-[10px] font-mono', cap.requiresConfirmation ? 'text-amber-400' : 'text-green-400')}>
                      {cap.requiresConfirmation ? '⚠ Confirm' : '⚡ Auto'}
                    </span>
                  </label>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}