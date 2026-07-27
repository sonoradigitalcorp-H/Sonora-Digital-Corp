'use client'
import { useState } from 'react'

const ARTISTAS = [
  { id: '6727f51e', nombre: 'Héctor Rubio', genero: 'Regional Mexicano', emoji: '🎸' },
  { id: 'f23cab60', nombre: 'Jesús Urquijo', genero: 'Regional Mexicano', emoji: '🎤' },
  { id: '00cf4992', nombre: 'Javier Arvayo', genero: 'Pop Latino', emoji: '🎵' },
]

const MODOS = [
  { id: 'text-to-video', label: 'Prompt Reel', icon: '✍️', desc: 'Describe y crea' },
  { id: 'image-to-video', label: 'Foto Reel', icon: '📷', desc: 'Tu foto cobra vida' },
  { id: 'reference-to-video', label: 'Clone Studio', icon: '🎭', desc: 'Consistencia total' },
]

const API = process.env.NEXT_PUBLIC_STUDIO_API_URL || 'http://localhost:3020'

export default function StudioPage() {
  const [artist, setArtist] = useState('')
  const [mode, setMode] = useState('text-to-video')
  const [prompt, setPrompt] = useState('')
  const [status, setStatus] = useState<'idle' | 'generating' | 'done' | 'error'>('idle')
  const [result, setResult] = useState<string | null>(null)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [error, setError] = useState('')

  async function handleGenerate() {
    setStatus('generating'); setError('')
    try {
      const r = await fetch(`${API}/studio/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'seedance-2-0',
          callback_url: `${API}/studio/webhook`,
          input: {
            prompt: prompt || `${ARTISTAS.find(a => a.id === artist)?.nombre || 'artista'} cinematic video`,
            generation_type: mode,
            duration: 5,
            aspect_ratio: '9:16',
            resolution: '720p',
            generate_audio: true,
            watermark: false,
          }
        })
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.detail || 'Error')
      setTaskId(data.taskId)
      pollTask(data.taskId)
    } catch (e: any) {
      setError(e.message); setStatus('error')
    }
  }

  async function pollTask(id: string) {
    for (let i = 0; i < 30; i++) {
      await new Promise(r => setTimeout(r, 2000))
      try {
        const r = await fetch(`${API}/studio/tasks/${id}`)
        const data = await r.json()
        if (data.status === 'completed') {
          setResult(data.resultUrl)
          setStatus('done')
          return
        }
        if (data.status === 'failed') {
          setError(data.failedReason || 'Falló')
          setStatus('error')
          return
        }
      } catch { /* retry */ }
    }
    setError('Timeout esperando el video')
    setStatus('error')
  }

  return (
    <div className="min-h-screen bg-dark text-[#F0EDE8] p-6">
      <div className="max-w-4xl mx-auto">

        <div className="tag gold">🎬 ABE Studio</div>
        <h1 className="text-3xl font-black tracking-tight mb-2">Generador de Reels IA</h1>
        <p className="text-[#888] mb-8">De la canción al video, sin estudio.</p>

        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Artistas */}
          <div className="bg-dark2 border border-[#1a1a1a] rounded-2xl p-5">
            <h2 className="text-xs font-bold tracking-widest uppercase text-gold mb-4">1. Artista</h2>
            <div className="flex flex-wrap gap-2">
              {ARTISTAS.map(a => (
                <button key={a.id} onClick={() => setArtist(a.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-semibold transition-all ${
                    artist === a.id
                      ? 'bg-gold/20 border border-gold text-gold'
                      : 'bg-[#1a1a1a] border border-transparent text-[#888] hover:border-gold/40'
                  }`}>
                  <span>{a.emoji}</span>
                  <div className="text-left">
                    <div className="text-xs">{a.nombre}</div>
                    <div className="text-[10px] opacity-60">{a.genero}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Modos */}
          <div className="bg-dark2 border border-[#1a1a1a] rounded-2xl p-5">
            <h2 className="text-xs font-bold tracking-widest uppercase text-gold mb-4">2. Modo</h2>
            <div className="space-y-2">
              {MODOS.map(m => (
                <button key={m.id} onClick={() => setMode(m.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all ${
                    mode === m.id
                      ? 'bg-purple/10 border border-purple text-purple'
                      : 'bg-[#1a1a1a] border border-transparent text-[#888] hover:border-purple/40'
                  }`}>
                  <span className="text-lg">{m.icon}</span>
                  <div className="text-left">
                    <div className="text-xs font-semibold">{m.label}</div>
                    <div className="text-[10px] opacity-60">{m.desc}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Créditos */}
          <div className="bg-dark2 border border-[#1a1a1a] rounded-2xl p-5">
            <h2 className="text-xs font-bold tracking-widest uppercase text-gold mb-4">3. Créditos</h2>
            <div className="text-center py-4">
              <div className="text-3xl font-black text-gold">60</div>
              <div className="text-xs text-[#888] mt-1">créditos por video</div>
              <div className="mt-3 text-xs text-[#666]">
                Plan <span className="text-gold font-bold">Pro</span> · 18/20 reels este mes
              </div>
            </div>
          </div>
        </div>

        {/* Prompt */}
        <div className="bg-dark2 border border-[#1a1a1a] rounded-2xl p-5 mb-6">
          <h2 className="text-xs font-bold tracking-widest uppercase text-gold mb-3">4. Describe tu video</h2>
          <textarea value={prompt} onChange={e => setPrompt(e.target.value)}
            placeholder="atardecer en Sinaloa, cámara lenta, estilo cinemático..."
            className="w-full bg-[#0A0A0A] border border-[#1a1a1a] rounded-xl p-4 text-sm text-[#F0EDE8] placeholder:text-[#555] resize-none focus:border-gold/40 focus:outline-none transition-colors"
            rows={3} maxLength={5000} />
          <div className="flex justify-between items-center mt-3">
            <span className="text-[10px] text-[#555]">{prompt.length}/5000</span>
            <button onClick={handleGenerate} disabled={status === 'generating'}
              className="bg-gold text-black px-6 py-2.5 rounded-xl font-bold text-sm hover:bg-gold-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
              {status === 'generating' ? (
                <><span className="animate-spin">⏳</span> Generando...</>
              ) : '🎬 Generar Reel'}
            </button>
          </div>
        </div>

        {/* Resultado */}
        {status !== 'idle' && (
          <div className={`rounded-2xl p-6 border ${
            status === 'generating' ? 'bg-purple/5 border-purple/20' :
            status === 'done' ? 'bg-green/5 border-green/20' :
            'bg-red/5 border-red/20'
          }`}>
            {status === 'generating' && (
              <div className="text-center py-4">
                <div className="animate-spin text-3xl mb-3">⏳</div>
                <div className="font-bold text-purple">Generando tu reel...</div>
                <div className="text-xs text-[#888] mt-1">Seedance 2.0 · 720p · 5s</div>
              </div>
            )}
            {status === 'done' && result && (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-green text-lg">✅</span>
                  <span className="font-bold text-green">¡Reel listo!</span>
                </div>
                <video src={result} controls className="w-full max-w-md rounded-xl mx-auto mb-4" />
                <div className="flex gap-3 justify-center">
                  <a href={result} download
                    className="bg-gold text-black px-5 py-2 rounded-xl font-bold text-sm hover:bg-gold-dark transition-colors">
                    ⬇ Descargar
                  </a>
                  <button onClick={() => { setStatus('idle'); setPrompt(''); setResult(null) }}
                    className="border border-[#333] px-5 py-2 rounded-xl font-semibold text-sm hover:border-gold hover:text-gold transition-colors">
                    🆕 Nuevo Reel
                  </button>
                </div>
              </div>
            )}
            {status === 'error' && (
              <div className="text-center py-4">
                <div className="text-red text-3xl mb-2">❌</div>
                <div className="font-bold text-red mb-1">Error</div>
                <div className="text-xs text-[#888]">{error}</div>
                <button onClick={() => setStatus('idle')}
                  className="mt-4 border border-[#333] px-5 py-2 rounded-xl font-semibold text-sm hover:border-gold hover:text-gold transition-colors">
                  Intentar de nuevo
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
