'use client'
import { Suspense } from 'react'
import { useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Navbar from '@/components/Navbar'
import { api } from '@/lib/api'
import { useAuth } from '@/lib/auth'

const plans = [
  {
    id: 'mysteria', name: 'Mysteria', price: '$14.99', period: '/mes',
    desc: 'Para quienes inician el camino',
    features: ['Lecciones completas', 'Fotos NSFW semanales', 'Streaming grupal', 'Chat con Lilith (20 msg/día)', 'Tareas con feedback', 'Descuento en retención'],
  },
  {
    id: 'ritual', name: 'Ritual', price: '$49.99', period: '/mes',
    desc: 'Para los devotos del arte', popular: true,
    features: ['Todo de Mysteria', 'Videos NSFW exclusivos', 'Fotos NSFW diarias', 'Chat ilimitado con Lilith', 'Streaming 1:1 privado', 'Retención de contenido incluida', '15% desc en Mystika Apparel'],
  },
]

function SubscribeContent() {
  const { user } = useAuth()
  const router = useRouter()
  const searchParams = useSearchParams()
  const defaultPlan = searchParams.get('plan') === 'ritual' ? 'ritual' : 'mysteria'
  const [selected, setSelected] = useState(defaultPlan)
  const [loading, setLoading] = useState(false)

  async function handleSubscribe(gateway) {
    if (!user) { router.push('/login'); return }
    setLoading(true)
    try {
      const data = await api.checkoutSubscription({ plan: selected, gateway })
      window.open(data.checkout_url, '_blank')
    } catch (err) {
      alert(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen stars-bg">
      <Navbar />
      <div className="pt-24 pb-20">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <h1 className="font-display text-4xl text-gold mb-2">Elige tu camino</h1>
          <p className="font-serif text-white/50 mb-10 text-lg">Cada plan es un nivel de conexión con Lilith y su música</p>

          <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
            {plans.map((plan) => (
              <div key={plan.id}
                onClick={() => setSelected(plan.id)}
                className={`card-mystika cursor-pointer transition-all duration-300 text-left ${selected === plan.id ? '!border-gold ring-1 ring-gold/30' : ''} ${plan.popular ? 'relative' : ''}`}>
                {plan.popular && (
                  <span className="absolute -top-3 right-6 bg-gold text-black font-sans text-xs px-4 py-1 rounded-full uppercase tracking-wider font-semibold">
                    Más popular
                  </span>
                )}
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-display text-2xl text-gold">{plan.name}</h3>
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${selected === plan.id ? 'border-gold' : 'border-white/30'}`}>
                    {selected === plan.id && <div className="w-2.5 h-2.5 rounded-full bg-gold" />}
                  </div>
                </div>
                <p className="font-serif text-white/40 text-sm mb-4">{plan.desc}</p>
                <div className="mb-6">
                  <span className="font-display text-4xl text-white">{plan.price}</span>
                  <span className="font-sans text-white/40">{plan.period}</span>
                </div>
                <ul className="space-y-2 mb-8">
                  {plan.features.map((f) => (
                    <li key={f} className="font-serif text-white/60 flex items-center gap-2 text-sm">
                      <span className="text-gold">✦</span> {f}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="mt-10 space-y-4">
            <button onClick={() => handleSubscribe('stripe')} disabled={loading}
              className="btn-primary text-lg !px-12 !py-4 disabled:opacity-50">
              {loading ? 'Procesando...' : `Suscribirme a ${selected === 'mysteria' ? 'Mysteria' : 'Ritual'} con Stripe`}
            </button>
            <div>
              <button onClick={() => handleSubscribe('mercadopago')} disabled={loading}
                className="btn-secondary">
                Pagar con Mercado Pago
              </button>
            </div>
            <p className="font-sans text-xs text-white/30 pt-4">
              Cancela cuando quieras. El acceso se mantiene hasta el final del periodo pagado.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Subscribe() {
  return (
    <Suspense fallback={<div className="min-h-screen stars-bg"><Navbar /><div className="pt-32 text-center font-display text-2xl text-gold animate-glow">Cargando...</div></div>}>
      <SubscribeContent />
    </Suspense>
  )
}
