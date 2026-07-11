"use client";

import { useEffect, useState, useRef, lazy, Suspense } from "react";
import { motion } from "framer-motion";
import { getArtists, getStats, getServices, type Artist } from "@/lib/abe-api";
import Navbar from "@/components/Navbar";
import RotatingPhrases from "@/components/RotatingPhrases";
import SplitHeadline from "@/components/SplitHeadline";
import Reveal from "@/components/Reveal";
import SectionTitle from "@/components/SectionTitle";
import ClickableCard from "@/components/ClickableCard";
import { ChevronLeft, ChevronRight, Sparkles, Trophy, Camera, Calendar, Users, Heart, Music2, Film, Bot, Crown, ArrowRight, Star, Check } from "lucide-react";

const Hero3D = lazy(() => import("@/components/Hero3D"));

const BENEFICIOS = [
  { icon: <Sparkles className="w-7 h-7" />, title: "Más tiempo para crear", tagline: "Nosotros simplificamos lo demás.", bullets: ["Tu enfoque vuelve a ser ensayar, escribir y cantar.", "Menos vueltas, menos correos, menos improvisación.", "Equipo detrás de ti que sí entiende tu carrera."], cta: "Ver cómo funciona" },
  { icon: <Trophy className="w-7 h-7" />, title: "Más prestigio alrededor de tu nombre", tagline: "Que tu nombre se vea, se escuche y se respete.", bullets: ["Presencia constante en escenarios y redes.", "Material visual a la altura de tu talento.", "Acompañamiento que se nota desde fuera."], cta: "Ver beneficios" },
  { icon: <Camera className="w-7 h-7" />, title: "Contenido listo para publicar", tagline: "Sin batallar, sin perder días enteros.", bullets: ["Fotos, clips y frases pensadas para tu público.", "Ideas visuales que mantienen tu cuenta viva.", "Producción creativa asistida por nuestro equipo."], cta: "Ver ejemplo" },
  { icon: <Calendar className="w-7 h-7" />, title: "Más escenarios y mini shows", tagline: "Espacios reales para tocar y vender experiencia.", bullets: ["Mini presentaciones en el Hub de Hermosillo.", "Fechas curadas con comunidad y fans cerca.", "Logística resuelta. Tú solo subes y cantas."], cta: "Quiero entrar" },
  { icon: <Users className="w-7 h-7" />, title: "Una comunidad que te empuja", tagline: "Cerca de artistas con camino recorrido.", bullets: ["Networking real con músicos, equipo y aliados.", "Espacios para convivir, aprender y crear juntos.", "Talento del ecosistema como Héctor Rubio cerca."], cta: "Ver círculo ABE" },
  { icon: <Heart className="w-7 h-7" />, title: "Tu carrera acompañada", tagline: "Ordenada, rentable y con dirección clara.", bullets: ["Seguimiento claro de cómo vas creciendo.", "Decisiones con cabeza, no por suerte.", "Cada paso pensado para sumar al siguiente."], cta: "Aplicar" },
];

const FOMO_BULLETS = [
  "Primer grupo fundador ABE Music Hub.",
  "Acceso preferente a espacios y experiencias.",
  "Prioridad en producción de contenido.",
  "Invitaciones a mini shows y sesiones privadas.",
  "Posibilidad de convivir y aprender de artistas del ecosistema.",
];

export default function ABELanding() {
  const [artists, setArtists] = useState<Artist[]>([]);
  const [stats, setStats] = useState({ revenue: 479112, streams: 119778231, artists: 3 });
  const carouselRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getArtists().then(setArtists);
    getStats().then(s => { if (s) setStats(s); });
  }, []);

  const scrollCarousel = (dir: number) => {
    carouselRef.current?.scrollBy({ left: dir * 320, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen overflow-x-hidden">
      <Navbar />

      {/* HERO */}
      <section className="relative min-h-screen flex items-center pt-24 pb-16 overflow-hidden">
        <Suspense fallback={null}><Hero3D /></Suspense>
        <div className="absolute inset-0 spotlight" />
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-black" />

        <motion.div className="absolute top-32 right-10 w-72 h-72 rounded-full bg-gold/10 blur-[120px]" animate={{ scale: [1, 1.2, 1], opacity: [0.4, 0.7, 0.4] }} transition={{ duration: 6, repeat: Infinity }} />
        <motion.div className="absolute bottom-20 left-10 w-96 h-96 rounded-full bg-red-abe/10 blur-[140px]" animate={{ scale: [1.1, 1, 1.1], opacity: [0.3, 0.6, 0.3] }} transition={{ duration: 7, repeat: Infinity }} />

        <div className="container relative z-10 px-4 max-w-7xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 mb-8 rounded-full border border-gold/30 bg-gold/5 text-xs uppercase tracking-[0.25em] text-gold">
            <span className="w-1.5 h-1.5 rounded-full bg-gold animate-pulse" /> ABE Music Group
          </motion.div>

          <SplitHeadline
            className="text-5xl md:text-7xl lg:text-8xl font-light leading-[0.95] max-w-5xl"
            parts={[
              { text: "Tu", from: "left" },
              { text: "carrera", from: "up" },
              { text: "merece", from: "right" },
              { text: "estructura.", from: "down", className: "text-gradient-gold italic" },
            ]}
          />

          <div className="mt-8 max-w-2xl">
            <p className="text-lg md:text-2xl text-muted-foreground font-light">
              <RotatingPhrases phrases={["Más tiempo para crear.", "Más ingresos sin perseguir oportunidades.", "Más prestigio alrededor de tu nombre.", "Más escenarios, contenido y comunidad.", "Menos desgaste. Más libertad."]} />
            </p>
          </div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 1 }}
            className="mt-12 flex flex-wrap gap-4">
            <a href="/signup"
              className="inline-flex items-center gap-2 px-8 py-3 rounded-full bg-gradient-gold text-black font-semibold hover:opacity-90 transition-all text-base">
              Aplicar al círculo ABE <ArrowRight className="w-4 h-4" />
            </a>
            <a href="https://t.me/abeassistant_bot" target="_blank"
              className="inline-flex items-center gap-2 px-8 py-3 rounded-full border border-gold/30 text-gold hover:bg-gold/10 transition-all text-base">
              Conocer el Hub
            </a>
          </motion.div>

          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.4, duration: 1 }}
            className="mt-20 grid grid-cols-3 max-w-2xl gap-8">
            {[
              { k: `${stats.artists}`, v: "Artistas" },
              { k: "1", v: "Hub en Hermosillo" },
              { k: "∞", v: "Oportunidades" },
            ].map(s => (
              <div key={s.v}>
                <div className="font-display text-4xl md:text-5xl text-gradient-gold">{s.k}</div>
                <div className="text-xs uppercase tracking-widest text-muted-foreground mt-2">{s.v}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* EMPATÍA */}
      <section className="py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <Reveal><p className="text-xs uppercase tracking-[0.3em] text-gold mb-6">Lo entendemos</p></Reveal>
          <Reveal dir="up" delay={0.1}>
            <p className="font-display text-3xl md:text-5xl font-light leading-tight">
              Sabemos que <span className="text-gradient-gold italic">no basta con tener talento</span>.
              No queremos que pierdas oportunidades por falta de equipo, contenido o contactos.
            </p>
          </Reveal>
          <Reveal dir="up" delay={0.3}>
            <p className="mt-8 text-muted-foreground text-lg max-w-2xl mx-auto">
              Tu tiempo debe estar en crear, ensayar, cantar y conectar con tu gente. Nosotros nos encargamos del resto.
            </p>
          </Reveal>
        </div>
      </section>

      {/* BENEFICIOS */}
      <section id="beneficios" className="py-24 px-4">
        <div className="max-w-7xl mx-auto">
          <SectionTitle eyebrow="Por qué ABE Music" title={<>Beneficios <span className="text-gradient-gold italic">desde tu lado</span></>} subtitle="Cada bloque abre con un clic." />
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {BENEFICIOS.map((b, i) => <ClickableCard key={b.title} {...b} index={i} />)}
          </div>
        </div>
      </section>

      {/* ARTISTAS */}
      <section id="artistas" className="py-24 px-4">
        <div className="max-w-7xl mx-auto">
          <SectionTitle eyebrow="Talento real" title={<>Artistas del <span className="text-gradient-gold italic">ecosistema</span></>} subtitle="Conoce a los artistas que confían en ABE Music Group." />

          <div className="flex items-center gap-2 justify-end mb-4">
            <button onClick={() => scrollCarousel(-1)} className="p-2 rounded-full glass hover:bg-white/10"><ChevronLeft className="w-4 h-4" /></button>
            <button onClick={() => scrollCarousel(1)} className="p-2 rounded-full glass hover:bg-white/10"><ChevronRight className="w-4 h-4" /></button>
          </div>

          <div ref={carouselRef} className="flex gap-6 overflow-x-auto scrollbar-hide pb-4 snap-x snap-mandatory">
            {artists.map((a, i) => (
              <motion.a key={a.id} href={`/artist/${a.id}`}
                className="min-w-[300px] snap-start glass rounded-2xl p-6 gradient-border hover:scale-[1.02] transition-all group"
                initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}>
                <div className="w-full aspect-square glass rounded-xl mb-4 flex items-center justify-center overflow-hidden">
                  <img src={`/images/artists/${a.id}/portrait.webp`} alt={a.name}
                    className="w-full h-full object-cover"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                </div>
                <h3 className="font-display text-xl font-medium mb-2">{a.name}</h3>
                <div className="text-2xl font-bold text-gradient-gold">${Number(a.total_revenue || 0).toLocaleString()}</div>
                <div className="text-sm text-muted-foreground">{(a.total_streams || 0).toLocaleString()} streams</div>
                <div className="mt-4 text-sm text-gold opacity-0 group-hover:opacity-100 transition-opacity">Ver perfil →</div>
              </motion.a>
            ))}
          </div>

          {/* Hector Rubio destacado */}
          {artists.filter(a => a.id === "hector-rubio").map(hr => (
            <Reveal key="hr-section" dir="up" className="mt-16">
              <div className="glass rounded-3xl p-8 md:p-12 grid md:grid-cols-2 gap-12 items-center gradient-border">
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-gold mb-4">Talento del ecosistema</p>
                  <h2 className="font-display text-4xl md:text-5xl font-light leading-tight mb-6">
                    Cerca de <span className="text-gradient-gold italic">talento con camino recorrido</span>.
                  </h2>
                  <p className="text-muted-foreground text-lg mb-6">
                    La comunidad ABE Music ya cuenta con talento reconocido como <span className="text-foreground font-medium">Héctor Rubio</span>, con más de <strong>115M streams</strong> y <strong>$460K</strong> en revenue.
                  </p>
                  <ul className="space-y-3 mb-8">
                    {["Eventos y sesiones con artistas del ecosistema.", "Mini shows y experiencias especiales.", "Comunidad ordenada, exclusiva y selecta."].map(t => (
                      <li key={t} className="flex items-start gap-3 text-foreground/85"><Music2 className="w-4 h-4 text-gold mt-1 shrink-0" />{t}</li>
                    ))}
                  </ul>
                  <a href="/signup" className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-gold text-black font-semibold">
                    Quiero formar parte del círculo ABE
                  </a>
                </div>
                <div className="aspect-[4/5] glass rounded-2xl overflow-hidden">
                  <img src="/images/artists/hector-rubio/portrait.webp" alt="Hector Rubio"
                    className="w-full h-full object-cover"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* FOMO CÍRCULO ABE */}
      <section className="py-24 px-4">
        <div className="max-w-5xl mx-auto">
          <Reveal>
            <div className="relative overflow-hidden rounded-3xl border border-gold/30 bg-gradient-to-br from-secondary via-card to-secondary p-10 md:p-16">
              <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-gold/20 blur-3xl" />
              <div className="relative">
                <p className="text-xs uppercase tracking-[0.3em] text-gold mb-4">Cupo limitado</p>
                <h2 className="font-display text-4xl md:text-5xl font-light leading-tight max-w-3xl">
                  Para artistas que <span className="text-gradient-gold italic">quieren tomarse en serio</span>.
                </h2>
                <div className="mt-10 grid md:grid-cols-2 gap-x-12 gap-y-3 max-w-3xl">
                  {FOMO_BULLETS.map((b, i) => (
                    <Reveal key={b} delay={i * 0.08}>
                      <div className="flex items-start gap-3"><span className="w-1.5 h-1.5 mt-2.5 rounded-full bg-gold shrink-0" /><span className="text-foreground/90">{b}</span></div>
                    </Reveal>
                  ))}
                </div>
                <a href="/signup" className="inline-flex items-center gap-2 mt-10 px-8 py-3 rounded-full bg-gradient-gold text-black font-semibold">
                  Aplicar al grupo fundador <ArrowRight className="w-4 h-4" />
                </a>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ABE FILMS */}
      <section className="py-24 px-4">
        <div className="max-w-5xl mx-auto glass rounded-3xl p-8 md:p-12 gradient-border relative overflow-hidden">
          <div className="absolute -top-20 -right-20 w-64 h-64 bg-red-abe/20 rounded-full blur-[100px]" />
          <div className="relative grid md:grid-cols-2 gap-8 items-center">
            <div>
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass text-xs mb-4"><Film className="w-3 h-3 text-gold" /> ABE Films</span>
              <h2 className="font-display text-3xl md:text-4xl font-light mb-4">Crea contenido con <span className="text-gradient-gold italic">IA</span></h2>
              <p className="text-muted-foreground mb-6">Videos profesionales, conciertos virtuales, saludos para fans. Todo desde tu navegador.</p>
              <ul className="space-y-2 mb-6">
                {["Videos AI con tu rostro", "Conciertos virtuales", "Saludos personalizados"].map(f => (
                  <li key={f} className="flex items-center gap-2 text-sm"><Check className="w-4 h-4 text-gold" />{f}</li>
                ))}
              </ul>
              <a href="/service/abe-films" className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-gold text-black font-semibold">Comenzar <ArrowRight className="w-4 h-4" /></a>
            </div>
            <div className="aspect-video glass rounded-2xl flex items-center justify-center"><Film className="w-12 h-12 text-gold opacity-50" /></div>
          </div>
        </div>
      </section>

      {/* CLON DIGITAL */}
      <section className="py-24 px-4 text-center">
        <div className="max-w-4xl mx-auto">
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass text-xs mb-4"><Bot className="w-3 h-3 text-gold" /></span>
          <h2 className="font-display text-4xl md:text-5xl font-light mb-4">Tu <span className="text-gradient-gold italic">clon digital</span> vende por ti</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto mb-10">Un bot con tu personalidad, voz y fotos. Vende 24/7, genera ingresos mientras haces música.</p>
          <a href="https://t.me/abeassistant_bot" target="_blank" className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-gold text-black font-semibold">Activar mi clon <Bot className="w-4 h-4" /></a>
        </div>
      </section>

      {/* CTA FINAL */}
      <section className="py-24 px-4 text-center">
        <div className="max-w-3xl mx-auto">
          <Reveal>
            <h2 className="font-display text-4xl md:text-6xl font-light">Menos vueltas. <span className="text-gradient-gold italic">Más resultados.</span></h2>
          </Reveal>
          <Reveal delay={0.2}>
            <div className="mt-10 flex flex-wrap gap-4 justify-center">
              <a href="/signup" className="px-8 py-3 rounded-full bg-gradient-gold text-black font-semibold">Comenzar ahora</a>
              <a href="https://t.me/abeassistant_bot" target="_blank" className="px-8 py-3 rounded-full border border-gold/30 text-gold hover:bg-gold/10 transition-all">Hablar con ABE Assistant</a>
            </div>
          </Reveal>
        </div>
      </section>

      <footer className="border-t border-gold/10 py-8 px-4 text-center">
        <div className="flex items-center justify-center gap-3 mb-4">
          <img src="/images/logo/abe-logo-1.webp" alt="ABE Music" className="w-6 h-6 rounded-full" />
          <span className="font-display text-lg text-gold">ABE Music Group</span>
        </div>
        <p className="text-xs text-muted-foreground">© 2026 ABE Music Group. Todos los derechos reservados.</p>
        <div className="flex justify-center gap-4 mt-3 text-xs text-muted-foreground">
          <a href="https://t.me/abeassistant_bot" target="_blank" className="hover:text-gold">Bot</a>
          <a href="https://t.me/abemusicgroup_bot" target="_blank" className="hover:text-gold">Canal</a>
        </div>
      </footer>
    </div>
  );
}
