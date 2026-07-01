'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function LoginForm() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      if (res.ok) {
        router.push('/dashboard')
        router.refresh()
      } else {
        const data = await res.json()
        setError(data.error || 'Credenciales incorrectas')
      }
    } catch {
      setError('Error de conexión')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-dark flex items-center justify-center px-4"
      style={{ background: 'radial-gradient(ellipse at 50% 30%, rgba(212,175,55,0.08) 0%, transparent 65%)' }}>
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="text-3xl mb-2">🎸</div>
          <h1 className="text-2xl font-black text-gold">Abe Music Hub</h1>
          <p className="text-[#888] text-sm mt-1">Acceso administrativo</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-dark2 border border-[#1a1a1a] rounded-2xl p-8 space-y-5">
          <div>
            <label className="block text-xs text-[#888] uppercase tracking-wider mb-2">Correo electrónico</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="abraham@abemusic.com"
              required
              className="w-full bg-dark3 border border-[#2a2a2a] rounded-xl px-4 py-3 text-sm text-[#F0EDE8] placeholder:text-[#444] focus:outline-none focus:border-gold transition-colors"
            />
          </div>
          <div>
            <label className="block text-xs text-[#888] uppercase tracking-wider mb-2">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••••"
              required
              className="w-full bg-dark3 border border-[#2a2a2a] rounded-xl px-4 py-3 text-sm text-[#F0EDE8] placeholder:text-[#444] focus:outline-none focus:border-gold transition-colors"
            />
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-sm text-red-400">
              ❌ {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gold text-black py-3 rounded-xl font-bold text-sm hover:bg-gold-dark transition-colors disabled:opacity-60">
            {loading ? 'Ingresando...' : 'Ingresar al Hub'}
          </button>
        </form>

        <p className="text-center text-xs text-[#555] mt-6">
          ← <a href="/" className="hover:text-gold transition-colors">Volver al sitio</a>
        </p>
      </div>
    </div>
  )
}
