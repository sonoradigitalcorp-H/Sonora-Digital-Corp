import { lazy, Suspense, useState } from 'react'
import StreamingChat from './components/StreamingChat'

const Scene3D = lazy(() => import('./components/Scene3D'))

const BENEFITS = [
  { icon: '🤖', title: 'Agentes IA 24/7', desc: 'Tus clientes reciben atención al instante, sin importar la hora o el día. Sin esperas, sin horarios.' },
  { icon: '📞', title: 'Llamadas que venden', desc: 'Agentes telefónicos que califican leads, manejan objeciones y cierran citas. Como tener un vendedor adicional.' },
  { icon: '💬', title: 'WhatsApp automatizado', desc: 'Chats, pedidos y pagos desde tu número de WhatsApp. Todo automatico, sin intervención.' },
  { icon: '🎭', title: 'Clone digital', desc: 'Tu imagen y voz generando contenido promocional. Fotos, videos y locuciones con tu identidad.' },
  { icon: '🔐', title: 'Ciberseguridad', desc: 'Diagnóstico automático de vulnerabilidades en tu dominio. Reporte con audio explicativo.' },
  { icon: '📊', title: 'Dashboard en vivo', desc: 'Métricas de tus agentes, clientes atendidos, ingresos generados. Todo en tiempo real.' },
]

function App() {
  const [showChat, setShowChat] = useState(false)

  return (
    <div className="bg-[#0a0a0a] text-white min-h-screen antialiased">
      {/* Nav */}
      <nav className="fixed top-0 w-full z-50 bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <span className="text-lg font-bold tracking-tight">
            SONORA <span className="text-white/40">DIGITAL</span> <span className="text-[#c8a87c]">CORP</span>
          </span>
          <div className="flex items-center gap-4 text-sm">
            <button
              onClick={() => setShowChat(!showChat)}
              className="px-5 py-2 rounded-lg bg-[#7c5cfc] hover:bg-[#6a4ae0] transition-all font-medium"
            >
              {showChat ? 'Cerrar Chat' : 'Habla con Mystic'}
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden">
        <Suspense fallback={<div className="absolute inset-0 bg-[#0a0a0a]" />}>
          <Scene3D />
        </Suspense>
        <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
          <h1 className="text-5xl md:text-7xl font-black tracking-tight leading-[0.95] mb-6">
            <span className="bg-gradient-to-r from-white via-[#7c5cfc] to-[#c8a87c] bg-clip-text text-transparent">
              Agentes IA
            </span>
            <br />
            <span className="text-white/20">que trabajan 24/7</span>
          </h1>
          <p className="text-lg md:text-xl text-white/40 max-w-2xl mx-auto mb-8 leading-relaxed">
            Atención al cliente, ventas, contenido y seguridad — todo automatico con IA.
            Sin código, sin servidores que administrar.
          </p>
          <button
            onClick={() => setShowChat(true)}
            className="px-8 py-3.5 rounded-xl bg-[#7c5cfc] hover:bg-[#6a4ae0] transition-all font-semibold text-sm"
          >
            Pregúntale a Mystic →
          </button>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-24 bg-white/[0.01] border-y border-white/[0.04]">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            Lo que puedes lograr
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {BENEFITS.map((b, i) => (
              <div key={i} className="p-8 rounded-2xl bg-white/[0.02] border border-white/[0.06] hover:border-[#7c5cfc]/20 transition-all">
                <div className="text-3xl mb-4">{b.icon}</div>
                <h3 className="text-lg font-semibold mb-2">{b.title}</h3>
                <p className="text-sm text-white/40 leading-relaxed">{b.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Chat */}
      {showChat && (
        <section className="py-24">
          <div className="max-w-3xl mx-auto px-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">Habla con Mystic</h2>
              <button
                onClick={() => setShowChat(false)}
                className="text-sm text-white/40 hover:text-white transition-colors"
              >
                ✕ Cerrar
              </button>
            </div>
            <StreamingChat />
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="py-8 border-t border-white/[0.04]">
        <div className="max-w-7xl mx-auto px-6 text-center text-xs text-white/20">
          <p>Sonora Digital Corp — <a href="https://wa.me/5216625383272" className="hover:text-white/40">WhatsApp</a></p>
        </div>
      </footer>
    </div>
  )
}

export default App
