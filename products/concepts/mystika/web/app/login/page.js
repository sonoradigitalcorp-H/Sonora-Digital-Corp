'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Navbar from '@/components/Navbar'
import { useAuth } from '@/lib/auth'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const router = useRouter()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      router.push('/lessons')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen stars-bg">
      <Navbar />
      <div className="min-h-screen flex items-center justify-center pt-20">
        <div className="w-full max-w-md mx-auto px-6">
          <div className="card-mystika p-8">
            <h1 className="font-display text-3xl text-gold text-center mb-2">Iniciar sesión</h1>
            <p className="font-serif text-center text-white/50 mb-8">Tu ritual te espera</p>

            {error && (
              <div className="bg-red-900/30 border border-red-800 text-red-300 font-sans text-sm px-4 py-3 rounded mb-6">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="font-sans text-xs uppercase tracking-wider text-white/50 block mb-2">Email</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                  className="input-mystika" placeholder="luna@ejemplo.com" required />
              </div>
              <div>
                <label className="font-sans text-xs uppercase tracking-wider text-white/50 block mb-2">Contraseña</label>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                  className="input-mystika" placeholder="••••••••" required />
              </div>
              <button type="submit" disabled={loading}
                className="btn-primary w-full !py-3">
                {loading ? 'Entrando...' : 'Entrar al templo'}
              </button>
            </form>

            <p className="font-sans text-sm text-center text-white/40 mt-6">
              ¿No tienes cuenta?{' '}
              <Link href="/register" className="text-gold hover:text-gold-light">Regístrate</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
