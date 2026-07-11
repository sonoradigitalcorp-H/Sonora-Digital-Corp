'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import { api } from '@/lib/api'
import { useAuth } from '@/lib/auth'

export default function Portal() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && !user) router.push('/login')
    if (user) {
      api.getProfile()
        .then(setProfile)
        .catch(() => router.push('/login'))
        .finally(() => setLoading(false))
    }
  }, [user, authLoading])

  if (authLoading || loading) {
    return <div className="min-h-screen stars-bg"><Navbar />
      <div className="pt-32 text-center font-display text-2xl text-gold animate-glow">Cargando...</div>
    </div>
  }

  return (
    <div className="min-h-screen stars-bg">
      <Navbar />
      <div className="pt-24 pb-20">
        <div className="max-w-5xl mx-auto px-6">
          <h1 className="font-display text-4xl text-gold mb-2">Mi altar</h1>
          <p className="font-serif text-white/50 mb-10 text-lg">Bienvenido, {profile?.user?.first_name || profile?.user?.username}</p>

          {profile?.subscription && (
            <div className="card-mystika border-gold/40 mb-8">
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-sans text-xs uppercase text-gold tracking-wider">Plan activo</span>
                  <h2 className="font-display text-2xl text-white mt-1">{profile.subscription.plan}</h2>
                  <p className="font-sans text-xs text-white/40 mt-1">
                    Válido hasta {new Date(profile.subscription.current_period_end).toLocaleDateString()}
                  </p>
                </div>
                <span className="text-gold text-3xl">✦</span>
              </div>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-6 mb-10">
            <div className="card-mystika">
              <h3 className="font-heading text-gold text-lg mb-4">Mis lecciones</h3>
              {profile?.purchases?.length > 0 ? (
                <div className="space-y-3">
                  {profile.purchases.map((p) => (
                    <div key={p.id} className="flex items-center justify-between">
                      <span className="font-serif text-white/70">{p.lesson_title}</span>
                      <span className="font-sans text-xs text-gold">${p.amount_usd}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="font-serif text-white/30 text-sm">Aún no has comprado lecciones</p>
              )}
            </div>

            <div className="card-mystika">
              <h3 className="font-heading text-gold text-lg mb-4">Mi altar (retenido)</h3>
              {profile?.retained?.length > 0 ? (
                <div className="space-y-3">
                  {profile.retained.map((r) => (
                    <div key={r.id} className="flex items-center justify-between">
                      <span className="font-serif text-white/70">{r.lesson_title}</span>
                      <span className="font-sans text-xs text-gold uppercase">{r.retention_type}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="font-serif text-white/30 text-sm">Nada en tu altar aún. Cuando retengas o descargues contenido, aparecerá aquí.</p>
              )}
            </div>
          </div>

          <div className="card-mystika">
            <h3 className="font-heading text-gold text-lg mb-4">Mi progreso</h3>
            {profile?.progress?.length > 0 ? (
              <div className="space-y-2">
                {profile.progress.map((p) => (
                  <div key={p.lesson_id} className="flex items-center justify-between">
                    <span className="font-serif text-white/70">{p.title}</span>
                    <span className={`font-sans text-xs ${p.is_completed ? 'text-green-400' : 'text-yellow-400'}`}>
                      {p.is_completed ? 'Completado' : 'En progreso'}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="font-serif text-white/30 text-sm">Empieza tu primer ritual</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
