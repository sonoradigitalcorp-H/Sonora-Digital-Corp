'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Navbar from '@/components/Navbar'
import { useAuth } from '@/lib/auth'

export default function Register() {
  const [form, setForm] = useState({ email: '', password: '', username: '', first_name: '', age_verified: false })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const router = useRouter()

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.age_verified) { setError('Debes ser mayor de 18 años'); return }
    setError('')
    setLoading(true)
    try {
      await register(form)
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
            <h1 className="font-display text-3xl text-gold text-center mb-2">Tu iniciación</h1>
            <p className="font-serif text-center text-white/50 mb-8">Crea tu cuenta y comienza el camino</p>

            {error && (
              <div className="bg-red-900/30 border border-red-800 text-red-300 font-sans text-sm px-4 py-3 rounded mb-6">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="font-sans text-xs uppercase tracking-wider text-white/50 block mb-2">Email</label>
                <input type="email" value={form.email} onChange={(e) => update('email', e.target.value)}
                  className="input-mystika" placeholder="luna@ejemplo.com" required />
              </div>
              <div>
                <label className="font-sans text-xs uppercase tracking-wider text-white/50 block mb-2">Nombre (opcional)</label>
                <input type="text" value={form.first_name} onChange={(e) => update('first_name', e.target.value)}
                  className="input-mystika" placeholder="Tu nombre" />
              </div>
              <div>
                <label className="font-sans text-xs uppercase tracking-wider text-white/50 block mb-2">Usuario (opcional)</label>
                <input type="text" value={form.username} onChange={(e) => update('username', e.target.value)}
                  className="input-mystika" placeholder="@usuario" />
              </div>
              <div>
                <label className="font-sans text-xs uppercase tracking-wider text-white/50 block mb-2">Contraseña</label>
                <input type="password" value={form.password} onChange={(e) => update('password', e.target.value)}
                  className="input-mystika" placeholder="••••••••" required minLength={6} />
              </div>
              <label className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" checked={form.age_verified}
                  onChange={(e) => update('age_verified', e.target.checked)}
                  className="w-4 h-4 accent-gold" />
                <span className="font-sans text-sm text-white/60">Soy mayor de 18 años</span>
              </label>
              <button type="submit" disabled={loading || !form.age_verified}
                className="btn-primary w-full !py-3 disabled:opacity-50">
                {loading ? 'Iniciando...' : 'Comenzar mi ritual'}
              </button>
            </form>

            <p className="font-sans text-sm text-center text-white/40 mt-6">
              ¿Ya tienes cuenta?{' '}
              <Link href="/login" className="text-gold hover:text-gold-light">Inicia sesión</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
