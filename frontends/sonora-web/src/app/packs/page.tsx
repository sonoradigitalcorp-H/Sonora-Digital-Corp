use client;

import { motion } from framer-motion;
import Navbar from @/components/Navbar;
import Reveal from @/components/Reveal;
import { Music, Users, Camera, Sparkles, Check, ArrowRight, Building2 } from lucide-react;

const PACKS = [
  {
    id: abe-music, icon: Music, name: ABE Music OS, tagline: Sello discográfico agent-native,
    price: 99, setup: 99,
    description: Transforma tu sello en una empresa con IA. 3 agentes inteligentes que gestionan booking, marketing, finanzas y releases 24/7.,
    features: [3 agentes: Ejecutivo, Marketing, Booking, 5 skills: streams, releases, promotion, booking, finance, Canales: WhatsApp + Voz + Telegram, Dashboard en tiempo real, Daily briefing 8:00 AM, Migraciones automáticas],
    href: /packs/abe-music, color: from-purple-500 to-pink-500,
  },
  {
    id: agent-crm, icon: Users, name: Agent CRM, tagline: CRM con agentes de IA,
    price: 49, setup: 99,
    description: Un CRM que no necesita clicks. Tus agentes gestionan leads, ventas, soporte y seguimiento automáticamente.,
    features: [Neo4j graph CRM, Agente de ventas 24/7, Soporte multi-canal, Pipeline automático, Reportes semanales, Integración WhatsApp],
    href: #, color: from-blue-500 to-cyan-500, coming: true,
  },
  {
    id: content-factory, icon: Camera, name: Content Factory, tagline: Fábrica de contenido AI,
    price: 99, setup: 99,
    description: Genera videos, imágenes y texto para redes sociales sin intervención humana. Pipeline automatizado 24/7.,
    features: [Generación de video AI, Imágenes Flux AI, Redacción automática, Publicación multi-red, Calendario editorial, Análisis de tendencias],
    href: #, color: from-orange-500 to-red-500, coming: true,
  },
];

export default function PacksPage() {
  return (
    <div className=min-h-screen gradient-bg>
      <Navbar />
      <div className=max-w-6xl mx-auto px-4 pt-24 pb-24>
        <Reveal>
          <div className=text-center mb-16>
            <div className=inline-flex items-center gap-2 glass px-4 py-2 rounded-full text-sm text-muted-foreground mb-6>
              <Sparkles className=w-4 h-4 text-gold /> SDC Agent OS
            </div>
            <h1 className=font-display text-4xl md:text-6xl font-light mb-4>
              Packs <span className=text-gradient-gold italic>Agent-Native</span>
            </h1>
            <p className=text-lg text-muted-foreground max-w-2xl mx-auto>
              Empresas completas con IA. Cada pack incluye infraestructura, agentes, skills y dashboard listos para usar en minutos.
            </p>
          </div>
        </Reveal>
        <div className=grid md:grid-cols-3 gap-6>
          {PACKS.map((pack, i) => (
            <Reveal key={pack.id} delay={i * 0.1}>
              <motion.div whileHover={{ y: -4 }} className=glass rounded-3xl p-8 relative overflow-hidden group>
                {pack.coming && <div className=absolute top-4 right-4 text-xs px-3 py-1 rounded-full glass text-muted-foreground>Próximamente</div>}
                <div className={w-14 h-14 rounded-2xl bg-gradient-to-br  + pack.color +  flex items-center justify-center mb-6}>
                  <pack.icon className=w-7 h-7 text-white />
                </div>
                <h2 className=font-display text-2xl font-medium mb-1>{pack.name}</h2>
                <p className=text-sm text-muted-foreground mb-4>{pack.tagline}</p>
                <div className=flex items-baseline gap-1 mb-6>
                  <span className=text-4xl font-bold text-gold>{pack.price}</span>
                  <span className=text-sm text-muted-foreground>/mes</span>
                  <span className=text-xs text-muted-foreground ml-2>+{pack.setup} setup</span>
                </div>
                <p className=text-sm text-muted-foreground mb-6 leading-relaxed>{pack.description}</p>
                <ul className=space-y-2.5 mb-8>
                  {pack.features.map((f) => (
                    <li key={f} className=flex items-start gap-2 text-sm><Check className=w-4 h-4 text-gold mt-0.5 shrink-0 /><span>{f}</span></li>
                  ))}
                </ul>
                <a href={pack.href} onClick={(e) => pack.coming && e.preventDefault()}
                  className={flex items-center justify-center gap-2 w-full py-3 rounded-full font-semibold text-sm transition-all  + (pack.coming ? glass text-muted-foreground cursor-not-allowed : bg-gradient-gold text-black hover:opacity-90)}>
                  {pack.coming ? Próximamente : Ver pack} <ArrowRight className=w-4 h-4 />
                </a>
              </motion.div>
            </Reveal>
          ))}
        </div>
        <Reveal delay={0.3}>
          <div className=glass rounded-3xl p-8 md:p-12 mt-16 text-center>
            <Building2 className=w-10 h-10 text-gold mx-auto mb-4 />
            <h2 className=font-display text-2xl font-light mb-4>¿Necesitas un pack personalizado?</h2>
            <p className=text-muted-foreground mb-6 max-w-xl mx-auto>Cada negocio es único. Creamos packs a la medida con los agentes, skills y canales que necesitas.</p>
            <a href=https://t.me/abeassistant_bot target=_blank className=inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-gold text-black font-semibold>Contactar <ArrowRight className=w-4 h-4 /></a>
          </div>
        </Reveal>
      </div>
      <footer className=border-t border-gold/10 py-6 px-4 text-center text-xs text-muted-foreground><p>© 2026 Sonora Digital Corp</p></footer>
    </div>
  );
}
