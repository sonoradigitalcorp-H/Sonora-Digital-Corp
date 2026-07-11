'use client'
import Link from 'next/link'
import Navbar from '@/components/Navbar'

const instruments = [
  { emoji: '🥁', name: 'Batería', en: 'Drums' },
  { emoji: '🎸', name: 'Guitarra', en: 'Guitar' },
  { emoji: '🎹', name: 'Piano', en: 'Piano' },
  { emoji: '🎤', name: 'Canto', en: 'Voice' },
  { emoji: '🎻', name: 'Violín', en: 'Violin' },
  { emoji: '🎛️', name: 'Producción', en: 'Production' },
]

const plans = [
  {
    name: 'Mysteria',
    price: '$14.99',
    period: '/mes',
    desc: 'Para quienes inician el camino',
    features: ['Lecciones completas', 'Fotos NSFW semanales', 'Streaming grupal', 'Chat con Lilith (20 msg/día)', 'Tareas con feedback'],
  },
  {
    name: 'Ritual',
    price: '$49.99',
    period: '/mes',
    desc: 'Para los devotos del arte',
    popular: true,
    features: ['Todo de Mysteria', 'Videos NSFW exclusivos', 'Fotos NSFW diarias', 'Chat ilimitado con Lilith', 'Streaming 1:1 privado', '15% desc en Apparel', 'Retención de contenido'],
  },
]

export default function Home() {
  return (
    <div className="min-h-screen stars-bg">
      <Navbar />

      <section className="min-h-screen flex items-center justify-center pt-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="animate-fade-in">
            <div className="w-20 h-20 mx-auto mb-8 rounded-full border-2 border-gold flex items-center justify-center">
              <span className="text-3xl">☽</span>
            </div>
            <h1 className="font-display text-6xl md:text-8xl text-gold mb-4 tracking-wider">MYSTIKA</h1>
            <p className="font-heading text-2xl md:text-3xl text-white/80 mb-2 italic">&ldquo;El Ritual Musical&rdquo;</p>
            <p className="font-serif text-xl text-white/50 mb-12">Donde el sonido despierta el alma</p>
            <div className="flex gap-4 justify-center flex-wrap">
              <Link href="/register" className="btn-primary text-lg px-10 py-4">Comenzar</Link>
              <Link href="/subscribe" className="btn-secondary text-lg px-10 py-4">Ver Planes</Link>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="font-heading text-3xl text-center text-gold mb-16">¿Qué instrumento quieres dominar?</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {instruments.map((inst) => (
              <Link key={inst.name} href={`/lessons?instrument=${inst.name.toLowerCase()}`}
                className="card-mystika text-center py-8 hover:-translate-y-1 transition-transform">
                <div className="text-4xl mb-3">{inst.emoji}</div>
                <div className="font-heading text-gold">{inst.name}</div>
                <div className="font-sans text-xs text-white/40 mt-1">{inst.en}</div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 gradient-hero">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="font-heading text-3xl text-center text-gold mb-4">Conoce a Lilith</h2>
          <p className="font-serif text-xl text-center text-white/60 mb-12 max-w-2xl mx-auto">
            Tu maestra, tu musa, tu ritual. Entre la lección y la tentación,
            la línea se desvanece.
          </p>
          <div className="flex flex-col md:flex-row items-center gap-12">
            <div className="w-64 h-80 rounded-lg border border-gold/30 bg-gradient-to-b from-purple-shadow to-black flex items-center justify-center">
              <span className="text-8xl opacity-60">🌙</span>
            </div>
            <div className="flex-1">
              <h3 className="font-display text-2xl text-gold mb-4">Lilith Mystika</h3>
              <p className="font-serif text-lg text-white/70 leading-relaxed mb-6">
                Bienvenido, iniciado. Soy Lilith, y Mystika es mi templo.
                Aquí la música no solo se aprende: se siente, se vive, se convierte en ritual.
                Cada lección es un viaje. Cada nota, un susurro del alma.
              </p>
              <p className="font-serif text-lg text-white/70 leading-relaxed">
                ¿Estás listo para tu primer ritual?
              </p>
            </div>
          </div>
        </div>
      </section>

      <section id="planes" className="py-20">
        <div className="max-w-5xl mx-auto px-6">
          <h2 className="font-heading text-3xl text-center text-gold mb-4">Planes de iniciación</h2>
          <p className="font-serif text-center text-white/50 mb-12">Elige tu camino</p>
          <div className="grid md:grid-cols-2 gap-8">
            {plans.map((plan) => (
              <div key={plan.name} className={`card-mystika relative ${plan.popular ? 'border-gold/60' : ''}`}>
                {plan.popular && (
                  <span className="absolute -top-3 right-6 bg-gold text-black font-sans text-xs px-4 py-1 rounded-full uppercase tracking-wider font-semibold">
                    Más popular
                  </span>
                )}
                <h3 className="font-display text-2xl text-gold mb-1">{plan.name}</h3>
                <p className="font-serif text-white/50 mb-4">{plan.desc}</p>
                <div className="mb-6">
                  <span className="font-display text-4xl text-white">{plan.price}</span>
                  <span className="font-sans text-white/40">{plan.period}</span>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((f) => (
                    <li key={f} className="font-serif text-white/70 flex items-center gap-2">
                      <span className="text-gold">✦</span> {f}
                    </li>
                  ))}
                </ul>
                <Link href={`/subscribe?plan=${plan.name.toLowerCase()}`}
                  className={`block text-center py-3 rounded font-sans text-sm uppercase tracking-wider transition-all ${plan.popular ? 'btn-primary' : 'btn-secondary'}`}>
                  Elegir {plan.name}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="py-12 border-t border-gold/10">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <div className="font-display text-gold text-xl tracking-wider mb-4">MYSTIKA</div>
          <p className="font-serif text-white/30 text-sm">&copy; 2026 Mystika. El Ritual Musical.</p>
        </div>
      </footer>
    </div>
  )
}
