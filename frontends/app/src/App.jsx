import { useState, useEffect, useRef, lazy, Suspense } from 'react'
import { products, metrics, plans, team } from './data/products'

const Scene3D = lazy(() => import('./components/Scene3D'))
const Dashboard = lazy(() => import('./components/Dashboard'))

function App() {
  const [activeSection, setActiveSection] = useState('hero')

  useEffect(() => {
    const onScroll = () => {
      const sections = ['hero', 'productos', 'dashboard', 'precios', 'contacto']
      for (const s of sections) {
        const el = document.getElementById(s)
        if (el && el.getBoundingClientRect().top < 200) setActiveSection(s)
      }
    }
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div className="bg-[#0a0a0a] text-white min-h-screen antialiased selection:bg-[#7c5cfc]/30">
      <Nav activeSection={activeSection} />
      <Hero />
      <Productos />
      <Dashboard />
      <Precios />
      <Contacto />
      <Footer />
    </div>
  )
}

function Nav({ activeSection }) {
  const links = [
    { id: 'hero', label: 'Inicio' },
    { id: 'productos', label: 'Productos' },
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'precios', label: 'Precios' },
    { id: 'contacto', label: 'Contacto' },
  ]

  return (
    <nav className="fixed top-0 w-full z-50 bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-white/5">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <a href="#hero" className="text-lg font-bold tracking-tight">
          SONORA <span className="text-white/40">DIGITAL</span>{' '}
          <span className="text-[#c8a87c]">CORP</span>
        </a>
        <div className="hidden md:flex items-center gap-8 text-sm">
          {links.map((l) => (
            <a
              key={l.id}
              href={`#${l.id}`}
              className={`transition-colors ${
                activeSection === l.id ? 'text-white' : 'text-white/50 hover:text-white/80'
              }`}
            >
              {l.label}
            </a>
          ))}
        </div>
        <a
          href="#contacto"
          className="text-sm px-5 py-2.5 rounded-lg bg-[#7c5cfc] hover:bg-[#6a4ae0] transition-all font-medium"
        >
          Empezar →
        </a>
      </div>
    </nav>
  )
}

function Hero() {
  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden"
    >
      <Suspense fallback={<div className="absolute inset-0 bg-[#0a0a0a]" />}>
        <Scene3D />
      </Suspense>

      <div className="max-w-6xl mx-auto px-6 text-center relative z-10">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#22c55e]/20 bg-[#22c55e]/5 text-[#22c55e] text-xs font-medium tracking-wider mb-8">
          <span className="w-2 h-2 rounded-full bg-[#22c55e] animate-pulse" />
          Sistema de agentes IA en producción
        </div>

        <h1 className="text-5xl md:text-7xl font-black tracking-tight leading-[0.95] mb-6">
          <span className="bg-gradient-to-r from-white via-[#7c5cfc] to-[#c8a87c] bg-clip-text text-transparent">
            Agentes IA
          </span>
          <br />
          <span className="text-white/30">que trabajan por ti 24/7</span>
        </h1>

        <p className="text-lg md:text-xl text-white/40 max-w-2xl mx-auto mb-10 leading-relaxed">
          Llamadas, clones digitales y bots WhatsApp con IA — todo corriendo en
          tu infraestructura. Sin código, sin servidores que administrar.
        </p>

        <div className="flex flex-wrap gap-4 justify-center mb-20">
          <a
            href="#productos"
            className="px-8 py-3.5 rounded-xl bg-[#7c5cfc] hover:bg-[#6a4ae0] transition-all font-semibold text-sm"
          >
            Ver Productos
          </a>
          <a
            href="#contacto"
            className="px-8 py-3.5 rounded-xl border border-white/10 hover:border-[#7c5cfc]/40 transition-all font-semibold text-sm text-white/70 hover:text-white"
          >
            Agendar Demo
          </a>
        </div>

        <div className="grid grid-cols-3 gap-8 max-w-lg mx-auto">
          <div className="text-center">
            <div className="text-3xl font-black text-white">3</div>
            <div className="text-xs text-white/30 mt-1">Productos</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-black text-white">{metrics.uptime}%</div>
            <div className="text-xs text-white/30 mt-1">Uptime</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-black text-white">{metrics.tools}+</div>
            <div className="text-xs text-white/30 mt-1">Herramientas IA</div>
          </div>
        </div>
      </div>
    </section>
  )
}

function Productos() {
  return (
    <section id="productos" className="py-32 relative">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-20">
          <span className="text-[#7c5cfc] text-sm font-medium tracking-widest uppercase">
            Productos
          </span>
          <h2 className="text-4xl md:text-5xl font-bold mt-3">
            Listos para usar hoy
          </h2>
          <p className="text-white/30 mt-4 max-w-xl mx-auto">
            Tres productos en producción. Sin setup, sin esperas.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {products.map((p) => (
            <article
              key={p.id}
              className="group p-8 rounded-2xl bg-white/[0.02] border border-white/[0.06] hover:border-[#7c5cfc]/20 transition-all hover:bg-white/[0.03]"
            >
              <div
                className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-5"
                style={{ backgroundColor: `${p.color}15` }}
              >
                {p.icon}
              </div>
              <h3 className="text-xl font-bold mb-1">{p.name}</h3>
              <p className="text-sm text-[#c8a87c] mb-4">{p.tagline}</p>
              <p className="text-sm text-white/40 leading-relaxed mb-6">
                {p.description}
              </p>
              <ul className="space-y-2 mb-6" role="list">
                {p.features.map((f, i) => (
                  <li key={i} className="flex items-center gap-2 text-xs text-white/50">
                    <span style={{ color: p.color }}>✓</span> {f}
                  </li>
                ))}
              </ul>
              <div className="flex gap-4 text-xs text-white/30 border-t border-white/[0.06] pt-4">
                {Object.entries(p.metrics).map(([k, v]) => (
                  <div key={k}>
                    <span className="text-white font-medium">{v}</span>{' '}
                    <span className="text-white/20">{k}</span>
                  </div>
                ))}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}

function DashboardWrapper() {
  return (
    <section id="dashboard" className="py-32 relative bg-white/[0.01] border-y border-white/[0.04]">
      <div className="max-w-7xl mx-auto px-6">
        <Suspense fallback={<div className="text-center py-20 text-white/30">Cargando dashboard...</div>}>
      <DashboardWrapper />
        </Suspense>
      </div>
    </section>
  )
}

function Precios() {
  return (
    <section id="precios" className="py-32 relative">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-20">
          <span className="text-[#c8a87c] text-sm font-medium tracking-widest uppercase">
            Precios
          </span>
          <h2 className="text-4xl md:text-5xl font-bold mt-3">Planes Simples</h2>
          <p className="text-white/30 mt-4 max-w-xl mx-auto">
            Sin contratos anuales. Cancelas cuando quieras.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {plans.map((p) => (
            <div
              key={p.name}
              className={`relative p-8 rounded-2xl border transition-all ${
                p.popular
                  ? 'bg-gradient-to-b from-[#7c5cfc]/10 to-transparent border-[#7c5cfc]/30'
                  : 'bg-white/[0.02] border-white/[0.06] hover:border-white/10'
              }`}
            >
              {p.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-[#7c5cfc] text-xs font-bold">
                  MÁS POPULAR
                </div>
              )}
              <h3 className="text-lg font-bold mb-1">{p.name}</h3>
              <div className="text-4xl font-black mb-1">
                ${p.price}
                <span className="text-sm font-normal text-white/30">/mes</span>
              </div>
              <p className="text-xs text-white/30 mb-6">{p.description}</p>
              <ul className="space-y-3 text-sm text-white/60 mb-8">
                {p.features.map((f, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="text-[#22c55e]">✓</span> {f}
                  </li>
                ))}
              </ul>
              <a
                href="#contacto"
                className={`block text-center py-3 rounded-xl text-sm font-medium transition-all ${
                  p.popular
                    ? 'bg-[#7c5cfc] hover:bg-[#6a4ae0]'
                    : 'border border-white/10 hover:border-[#7c5cfc]/40'
                }`}
              >
                {p.name === 'Enterprise' ? 'Contactar' : 'Empezar'}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function Contacto() {
  const [turnstileToken, setTurnstileToken] = useState('')
  const turnstileRef = useRef(null)

  useEffect(() => {
    if (window.turnstile && turnstileRef.current) {
      window.turnstile.render(turnstileRef.current, {
        sitekey: '0x4AAAAAAAXx8o3BmBTxQq1t',
        callback: (token) => setTurnstileToken(token),
        theme: 'dark',
      })
    }
  }, [])

  return (
    <section id="contacto" className="py-32 relative bg-white/[0.01] border-t border-white/[0.04]">
      <div className="max-w-3xl mx-auto px-6 text-center">
        <span className="text-[#7c5cfc] text-sm font-medium tracking-widest uppercase">
          Contacto
        </span>
        <h2 className="text-4xl md:text-5xl font-bold mt-3 mb-6">
          ¿Listo para automatizar?
        </h2>
        <p className="text-white/30 mb-10 max-w-lg mx-auto">
          Te contactamos en menos de 24h para activar tu primer agente.
        </p>

        <form
          className="max-w-md mx-auto space-y-4 text-left"
          onSubmit={async (e) => {
            e.preventDefault()
            if (!turnstileToken) {
              alert('Por favor completa la verificación anti-bot')
              return
            }
            const fd = new FormData(e.target)
            const data = Object.fromEntries(fd)
            try {
              await fetch('/api/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...data, 'cf-turnstile-response': turnstileToken }),
              })
              alert('✅ Mensaje recibido. Te contactamos pronto.')
              e.target.reset()
            } catch {
              alert('Error al enviar. Intenta de nuevo.')
            }
          }}
        >
          <input
            type="text"
            name="name"
            placeholder="Nombre"
            required
            aria-label="Nombre"
            className="w-full px-5 py-3.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white placeholder-white/20 focus:outline-none focus:border-[#7c5cfc]/40 transition-all text-sm"
          />
          <input
            type="email"
            name="email"
            placeholder="Email"
            required
            aria-label="Email"
            className="w-full px-5 py-3.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white placeholder-white/20 focus:outline-none focus:border-[#7c5cfc]/40 transition-all text-sm"
          />
          <input
            type="tel"
            name="phone"
            placeholder="WhatsApp"
            aria-label="WhatsApp"
            className="w-full px-5 py-3.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white placeholder-white/20 focus:outline-none focus:border-[#7c5cfc]/40 transition-all text-sm"
          />
          <select
            name="producto"
            aria-label="Producto de interés"
            className="w-full px-5 py-3.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white/60 focus:outline-none focus:border-[#7c5cfc]/40 transition-all text-sm"
          >
            <option value="">Producto que te interesa...</option>
            <option value="call-engine">AI Call Engine</option>
            <option value="clone">Clone Publicitario</option>
            <option value="whatsapp">WhatsApp AI Agent</option>
            <option value="todo">Todo el paquete</option>
          </select>
          <div ref={turnstileRef} className="flex justify-center" />
          <button
            type="submit"
            className="w-full py-3.5 rounded-xl bg-[#7c5cfc] hover:bg-[#6a4ae0] transition-all font-semibold text-sm"
          >
            Enviar →
          </button>
        </form>

        <div className="mt-8 text-sm text-white/30">
          O escríbenos directo:{' '}
          <a
            href="https://wa.me/5216625383272"
            className="text-[#22c55e] hover:underline"
          >
            WhatsApp
          </a>
        </div>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="py-12 border-t border-white/[0.04]">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="text-sm font-bold tracking-tight">
            SONORA <span className="text-white/40">DIGITAL</span>{' '}
            <span className="text-[#c8a87c]">CORP</span>
          </span>
          <div className="flex gap-6 text-xs text-white/30">
            <a href="https://wa.me/5216625383272" className="hover:text-white/60 transition-colors">
              WhatsApp
            </a>
            <a href="https://status.sonoradigitalcorp.com" className="hover:text-white/60 transition-colors">
              Status
            </a>
            <a href="https://api.sonoradigitalcorp.com" className="hover:text-white/60 transition-colors">
              API
            </a>
          </div>
          <span className="text-xs text-white/20">
            &copy; {new Date().getFullYear()} Sonora Digital Corp
          </span>
        </div>
      </div>
    </footer>
  )
}

export default App
