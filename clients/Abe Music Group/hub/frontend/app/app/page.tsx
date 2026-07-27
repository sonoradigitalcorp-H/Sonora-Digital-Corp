import Link from 'next/link'

const SERVICIOS = [
  { icon: '🎸', name: 'Sala de ensayo', desc: 'Cuartos acústicos profesionales por hora' },
  { icon: '🎙', name: 'Estudio de grabación', desc: 'Producción con ingeniero de sonido' },
  { icon: '🎓', name: 'Clases de música', desc: 'Guitarra, bajo, batería, voz, producción' },
  { icon: '🎤', name: 'Podcast Studio', desc: 'Grabación de audio y video en 4K' },
  { icon: '🥊', name: 'Zona Gym', desc: 'Fitness para mantenerte en escena' },
  { icon: '🌄', name: 'Retiros creativos', desc: 'Jornadas de composición y creatividad' },
  { icon: '🥽', name: 'VR Cabinas', desc: 'Conciertos inmersivos en realidad virtual' },
  { icon: '🎬', name: 'Content Creation', desc: 'Espacio equipado para reels profesionales' },
  { icon: '🤖', name: 'Clon IA del artista', desc: 'Avatar digital que interactúa con tus fans' },
  { icon: '🎟', name: 'Mini Shows', desc: 'Presentaciones íntimas para fans VIP' },
  { icon: '🥁', name: 'Baquetas artesanales', desc: 'Fabricación en torno, personalizadas' },
  { icon: '🔊', name: 'Renta de equipo', desc: 'PA, luces y backline para tus eventos' },
]

const EARN = [
  { accion: 'Crear meme validado del artista', reso: '+25 $RESO' },
  { accion: 'Dueto o stitch de reel', reso: '+15 $RESO' },
  { accion: 'Referido que se suscribe', reso: '+200 $RESO' },
  { accion: 'Asistir a live virtual', reso: '+50 $RESO' },
  { accion: 'Completar un curso', reso: '+150 $RESO' },
]

const BURN = [
  { accion: 'Entradas a eventos flash', reso: 'precio dinámico' },
  { accion: '1 hora extra de ensayo', reso: '100 $RESO' },
  { accion: 'Merch exclusivo', reso: 'variable' },
  { accion: 'Acceso VR cabinas', reso: 'variable' },
]

const PLANES = [
  { nombre: 'Básico', precio: '$99', reso: '100', features: ['Dashboard acceso', '5 reels IA/mes', 'Leaderboard semanal'], featured: false },
  { nombre: 'Pro', precio: '$299', reso: '400', features: ['Clon IA básico', '20 reels IA/mes', '10% dto en merch', 'Acceso anticipado eventos'], featured: true },
  { nombre: 'Élite', precio: '$999', reso: '1,200', features: ['Clon IA avanzado', 'Reels ilimitados', '20% dto en merch', 'VIP en todos los eventos', 'Backstage exclusivo'], featured: false },
]

const NIVELES = [
  { icon: '🌱', nombre: 'EMERGENTE', pts: '0 — 499 pts' },
  { icon: '⭐', nombre: 'LOCAL', pts: '500 — 1,999 pts' },
  { icon: '🔥', nombre: 'REGIONAL', pts: '2,000 — 4,999 pts' },
  { icon: '👑', nombre: 'NACIONAL', pts: '5,000+ pts' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-dark text-[#F0EDE8]">
      {/* NAV */}
      <nav className="sticky top-0 z-50 flex items-center justify-between px-8 py-4 border-b border-[#1a1a1a] bg-dark/95 backdrop-blur-sm">
        <span className="text-xl font-bold text-gold">🎸 Abe Music Hub</span>
        <div className="hidden md:flex gap-6 text-sm text-[#888]">
          <a href="#servicios" className="hover:text-gold transition-colors">Servicios</a>
          <a href="#reso" className="hover:text-gold transition-colors">$RESO</a>
          <a href="#planes" className="hover:text-gold transition-colors">Planes</a>
          <a href="#contacto" className="hover:text-gold transition-colors">Contacto</a>
        </div>
        <div className="flex gap-3">
          <a href="https://t.me/AbeMusicHubBot" className="text-sm bg-gold text-black px-4 py-2 rounded-lg font-semibold hover:bg-gold-dark transition-colors">
            🤖 Únete
          </a>
          <Link href="/login" className="text-sm border border-[#333] px-4 py-2 rounded-lg text-[#888] hover:border-gold hover:text-gold transition-colors">
            Acceso
          </Link>
        </div>
      </nav>

      {/* HERO */}
      <section className="min-h-[90vh] flex flex-col items-center justify-center text-center px-6 py-20"
        style={{ background: 'radial-gradient(ellipse at 50% 0%, rgba(212,175,55,0.10) 0%, transparent 65%)' }}>
        <span className="inline-flex items-center gap-2 bg-gold/10 border border-gold/30 text-gold text-xs font-bold tracking-wider px-4 py-1.5 rounded-full mb-6 uppercase">
          🎵 Hermosillo, Sonora
        </span>
        <h1 className="text-5xl md:text-7xl font-black tracking-tight leading-none mb-5">
          El hogar del<br /><span className="text-gold">músico sonorense</span>
        </h1>
        <p className="text-lg text-[#888] max-w-xl leading-relaxed mb-10">
          Salas de ensayo, estudio de grabación, VR cabinas, clases, eventos y mucho más. Todo premium, todo en un lugar.
        </p>
        <div className="flex gap-4 flex-wrap justify-center">
          <a href="https://t.me/AbeMusicHubBot" className="bg-gold text-black px-8 py-3.5 rounded-xl font-bold text-base hover:bg-gold-dark transition-colors">
            🤖 Hablar con el Bot
          </a>
          <a href="#servicios" className="border border-[#333] px-8 py-3.5 rounded-xl font-semibold text-base hover:border-gold hover:text-gold transition-colors">
            Ver servicios
          </a>
        </div>
        {/* Stats */}
        <div className="grid grid-cols-4 mt-16 border border-[#222] rounded-2xl overflow-hidden max-w-2xl w-full">
          {[['20+','Servicios'],['$RESO','Token musical'],['24/7','Bot activo'],['4','Niveles de fan']].map(([n,l]) => (
            <div key={l} className="text-center py-5 border-r border-[#222] last:border-r-0">
              <div className="text-2xl font-black text-gold">{n}</div>
              <div className="text-xs text-[#888] mt-1">{l}</div>
            </div>
          ))}
        </div>
      </section>

      {/* SERVICIOS */}
      <section id="servicios" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-xs font-bold tracking-widest uppercase text-gold mb-3">Servicios</div>
          <h2 className="text-4xl font-black tracking-tight mb-3">Todo lo que necesitas para crear</h2>
          <p className="text-[#888] mb-12 max-w-xl">Espacios físicos y herramientas digitales para artistas en todas las etapas de su carrera.</p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {SERVICIOS.map(s => (
              <div key={s.name} className="bg-dark2 border border-[#1a1a1a] rounded-xl p-5 hover:border-gold/40 transition-colors">
                <div className="text-3xl mb-3">{s.icon}</div>
                <div className="font-bold text-sm mb-1">{s.name}</div>
                <div className="text-xs text-[#888]">{s.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* $RESO */}
      <section id="reso" className="py-24 px-6 bg-dark2">
        <div className="max-w-6xl mx-auto">
          <div className="text-xs font-bold tracking-widest uppercase text-gold mb-3">Gamificación</div>
          <h2 className="text-4xl font-black tracking-tight mb-3">El token <span className="text-gold">$RESO</span></h2>
          <p className="text-[#888] mb-12">Gana tokens por crear, aprender y participar. Úsalos para beneficios exclusivos.</p>
          <div className="grid md:grid-cols-2 gap-6 mb-12">
            <div className="bg-dark border border-[#1a1a1a] rounded-xl p-6">
              <h3 className="font-bold text-base mb-4">💰 Gana $RESO</h3>
              {EARN.map(e => (
                <div key={e.accion} className="flex justify-between items-center py-2.5 border-b border-[#111] last:border-0 text-sm">
                  <span className="text-[#ccc]">{e.accion}</span>
                  <span className="bg-gold/10 text-gold px-2.5 py-0.5 rounded-md text-xs font-bold ml-3 shrink-0">{e.reso}</span>
                </div>
              ))}
            </div>
            <div className="bg-dark border border-[#1a1a1a] rounded-xl p-6">
              <h3 className="font-bold text-base mb-4">🔥 Usa $RESO</h3>
              {BURN.map(b => (
                <div key={b.accion} className="flex justify-between items-center py-2.5 border-b border-[#111] last:border-0 text-sm">
                  <span className="text-[#ccc]">{b.accion}</span>
                  <span className="bg-gold/10 text-gold px-2.5 py-0.5 rounded-md text-xs font-bold ml-3 shrink-0">{b.reso}</span>
                </div>
              ))}
            </div>
          </div>
          <h3 className="font-bold text-lg mb-5">Niveles de fan</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {NIVELES.map(n => (
              <div key={n.nombre} className="bg-dark border border-[#1a1a1a] rounded-xl p-5 text-center">
                <div className="text-3xl mb-2">{n.icon}</div>
                <div className="font-bold text-gold text-sm mb-1">{n.nombre}</div>
                <div className="text-xs text-[#888]">{n.pts}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PLANES */}
      <section id="planes" className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-xs font-bold tracking-widest uppercase text-gold mb-3">Membresías</div>
          <h2 className="text-4xl font-black tracking-tight mb-3">Elige tu plan</h2>
          <p className="text-[#888] mb-12">Suscripción mensual, cancela cuando quieras.</p>
          <div className="grid md:grid-cols-3 gap-6">
            {PLANES.map(p => (
              <div key={p.nombre} className={`bg-dark2 rounded-2xl p-7 relative ${p.featured ? 'border-2 border-gold' : 'border border-[#1a1a1a]'}`}>
                {p.featured && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gold text-black text-xs font-bold px-3 py-1 rounded-full">⭐ Popular</span>
                )}
                <div className="font-bold text-lg mb-1">{p.nombre}</div>
                <div className="text-4xl font-black text-gold">{p.precio}</div>
                <div className="text-xs text-[#888] mb-1">MXN / mes</div>
                <div className="text-sm text-[#888] mb-6">+ <span className="text-gold font-bold">{p.reso} $RESO</span> mensuales</div>
                <ul className="space-y-2 mb-7">
                  {p.features.map(f => (
                    <li key={f} className="flex gap-2 text-sm text-[#ccc]">
                      <span className="text-gold font-bold">✓</span>{f}
                    </li>
                  ))}
                </ul>
                <a href="https://t.me/AbeMusicHubBot"
                  className={`block text-center py-2.5 rounded-xl font-semibold text-sm transition-colors ${p.featured ? 'bg-gold text-black hover:bg-gold-dark' : 'border border-[#333] hover:border-gold hover:text-gold'}`}>
                  Suscribirme
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="contacto" className="py-28 px-6 text-center"
        style={{ background: 'radial-gradient(ellipse at 50% 50%, rgba(212,175,55,0.07) 0%, transparent 65%)' }}>
        <div className="max-w-2xl mx-auto">
          <div className="text-xs font-bold tracking-widest uppercase text-gold mb-3">Únete</div>
          <h2 className="text-4xl font-black tracking-tight mb-4">Empieza hoy en el hub</h2>
          <p className="text-[#888] mb-10 leading-relaxed">Habla con nuestro bot en Telegram o contáctanos por WhatsApp con Abraham directamente.</p>
          <div className="flex gap-4 justify-center flex-wrap">
            <a href="https://t.me/AbeMusicHubBot" className="bg-gold text-black px-8 py-3.5 rounded-xl font-bold hover:bg-gold-dark transition-colors">🤖 Bot Telegram</a>
            <a href="https://wa.me/13238192000" className="border border-[#333] px-8 py-3.5 rounded-xl font-semibold hover:border-gold hover:text-gold transition-colors">💬 WhatsApp Abraham</a>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-[#111] py-8 text-center text-sm text-[#555]">
        <p>🎸 <strong className="text-[#888]">Abe Music Hub</strong> — Hermosillo, Sonora · Powered by Sonora Digital Corp</p>
      </footer>
    </div>
  )
}
