import { useState, useEffect } from 'react'
import { products, metrics, plans, team } from './data/products'

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
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {Array.from({ length: 40 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-[#7c5cfc]/20 rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 20}s`,
              animationDuration: `${15 + Math.random() * 20}s`,
              opacity: 0.3 + Math.random() * 0.5,
            }}
          />
        ))}
      </div>

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

function Dashboard() {
  const liveMetrics = [
    { label: 'Agentes', value: metrics.agents, icon: '🤖' },
    { label: 'Capacidades', value: metrics.capabilities, icon: '⚡' },
    { label: 'MCP Tools', value: metrics.tools, icon: '🔧' },
    { label: 'Skills', value: metrics.skills, icon: '📚' },
    { label: 'Eventos', value: metrics.events.total, icon: '📡' },
    { label: 'Uptime', value: `${metrics.uptime}%`, icon: '✅' },
  ]

  const statusItems = [
    { name: 'AI Call Engine', status: 'operational' },
    { name: 'Clone Service', status: 'operational' },
    { name: 'WhatsApp Agent', status: 'operational' },
    { name: 'Hermes Gateway', status: 'operational' },
    { name: 'Neo4j Graph DB', status: 'operational' },
    { name: 'Qdrant Vector', status: 'operational' },
  ]

  return (
    <section id="dashboard" className="py-32 relative bg-white/[0.01] border-y border-white/[0.04]">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-20">
          <span className="text-[#22c55e] text-sm font-medium tracking-widest uppercase">
            Sistema en vivo
          </span>
          <h2 className="text-4xl md:text-5xl font-bold mt-3">Dashboard</h2>
          <p className="text-white/30 mt-4 max-w-xl mx-auto">
            Métricas reales del ecosistema SDC.
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-12">
          {liveMetrics.map((m) => (
            <div
              key={m.label}
              className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.06] text-center hover:border-[#7c5cfc]/20 transition-all"
            >
              <div className="text-2xl mb-2">{m.icon}</div>
              <div className="text-2xl font-black text-white">{m.value}</div>
              <div className="text-xs text-white/30 mt-1">{m.label}</div>
            </div>
          ))}
        </div>

        <div className="max-w-2xl mx-auto">
          <h3 className="text-lg font-semibold mb-4 text-center">Estado de Servicios</h3>
          <div className="rounded-2xl bg-white/[0.02] border border-white/[0.06] divide-y divide-white/[0.06]">
            {statusItems.map((s) => (
              <div key={s.name} className="flex items-center justify-between px-6 py-4">
                <span className="text-sm text-white/70">{s.name}</span>
                <span className="flex items-center gap-2 text-xs">
                  <span className="w-2 h-2 rounded-full bg-[#22c55e] animate-pulse" />
                  Operational
                </span>
              </div>
            ))}
          </div>
        </div>
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
          action="https://formsubmit.co/hello@sonoradigitalcorp.com"
          method="POST"
          className="max-w-md mx-auto space-y-4 text-left"
        >
          <input type="hidden" name="_subject" value="Lead desde sdc.app" />
          <input type="hidden" name="_next" value="https://sonoradigitalcorp.com" />
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
