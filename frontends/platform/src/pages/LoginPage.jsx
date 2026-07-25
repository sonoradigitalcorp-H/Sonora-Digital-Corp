import { useState } from 'react'
import { useAuth } from '../lib/auth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { signIn } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    const { error: err } = await signIn(email)
    setLoading(false)
    if (err) {
      setError(err.message)
    } else {
      setSent(true)
    }
  }

  if (sent) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-6">
        <div className="bg-[#1a1a1e] border border-[#2a2a2e] rounded-xl p-8 text-center max-w-sm w-full">
          <div className="w-14 h-14 rounded-full bg-[#22c55e]/10 flex items-center justify-center mx-auto mb-5">
            <span className="text-2xl">✓</span>
          </div>
          <h2 className="text-lg font-semibold mb-2">Sesión iniciada</h2>
          <p className="text-sm text-[#6e6e73] mb-6">
            Bienvenido <strong className="text-[#f5f5f7]">{email}</strong>
          </p>
          <a
            href="/platform/chat"
            className="inline-block px-6 py-3 rounded-full bg-[#0071e3] hover:bg-[#0066cc] transition-all text-sm font-medium"
          >
            Ir al chat
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-semibold tracking-tight">
            SONORA <span className="text-[#6e6e73]">DIGITAL</span>
          </h1>
          <p className="text-sm text-[#6e6e73] mt-2">Plataforma de Agentes IA</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-[#1a1a1e] border border-[#2a2a2e] rounded-xl p-6">
          <label className="block text-xs text-[#6e6e73] uppercase tracking-wider mb-2">
            Correo electrónico
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="tu@email.com"
            required
            className="w-full px-4 py-3 rounded-xl bg-black border border-[#2a2a2e] text-[#f5f5f7] text-sm placeholder-[#6e6e73] focus:outline-none focus:border-[#0071e3]/50 transition-colors mb-4"
          />
          {error && (
            <p className="text-xs text-[#ef4444] mb-4">{error}</p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-full bg-[#0071e3] hover:bg-[#0066cc] disabled:opacity-50 transition-all text-sm font-medium"
          >
            {loading ? 'Iniciando...' : 'Iniciar sesión'}
          </button>
          <p className="text-xs text-[#6e6e73] text-center mt-4">
            Ingresa tu email para acceder a la plataforma
          </p>
        </form>
      </div>
    </div>
  )
}
