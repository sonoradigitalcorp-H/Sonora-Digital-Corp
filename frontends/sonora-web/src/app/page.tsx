"use client";

import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import { getArtists, getStats, getServices, type Artist } from "@/lib/abe-api";
import Navbar from "@/components/Navbar";
import { ChevronLeft, ChevronRight, Sparkles, Crown, Zap, Film, Bot, Music, Mic, Star, ArrowRight, Check } from "lucide-react";

const FOMO_PRODUCTS = [
  { icon: Crown, title: "Tu carrera en tus manos", desc: "Deja de perder tiempo gestionando. Nosotros producimos, distribuimos y vendemos por ti.", color: "#FF6B35" },
  { icon: Zap, title: "Clon digital para ventas", desc: "Un bot que actúa como tú 24/7. Vende merch, entradas, saludos. Mientras duermes.", color: "#00ccff" },
  { icon: Film, title: "ABE Films", desc: "Videos AI, conciertos virtuales, saludos personalizados para fans. Crea contenido sin moverte de tu casa.", color: "#b388ff" },
  { icon: Bot, title: "Libertad financiera", desc: "Recupera el control de tu música. Distribución global, revenue tracking, contratos justos.", color: "#00ff88" },
];

export default function ABELanding() {
  const [artists, setArtists] = useState<Artist[]>([]);
  const [services, setServices] = useState<any[]>([]);
  const [stats, setStats] = useState({ revenue: 479112, streams: 119778231, artists: 3 });
  const carouselRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getArtists().then(setArtists);
    getServices().then(setServices);
    getStats().then(s => { if (s) setStats(s); });
  }, []);

  const scrollCarousel = (dir: number) => {
    if (carouselRef.current) carouselRef.current.scrollBy({ left: dir * 320, behavior: "smooth" });
  };

  return (
    <main className="min-h-screen gradient-bg overflow-x-hidden">
      <Navbar />

      {/* Hero — Freedom First */}
      <section className="min-h-screen flex flex-col items-center justify-center px-4 text-center relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[200px] opacity-20 animate-pulse" />
          <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-[#00ccff] rounded-full blur-[200px] opacity-20" />
        </div>
        <motion.div className="relative z-10" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass text-sm mb-8">
            <Sparkles className="w-4 h-4 text-[#FF6B35]" />
            Tu música, tu negocio, tu libertad
          </div>
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            Deja de perder el tiempo.<br />
            <span className="gradient-text">Nosotros hacemos crecer tu carrera.</span>
          </h1>
          <p className="text-lg text-gray-400 max-w-xl mx-auto mb-10">
            ABE Music Group no es un sello discográfico. Es tu equipo de gestión, producción, distribución y ventas. 
            Un clon digital que vende por ti 24/7. Videos AI. Conciertos virtuales. Libertad real.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="/signup"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-full font-semibold text-lg bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black hover:scale-105 transition-transform animate-glow">
              Quiero ser libre <ArrowRight className="w-5 h-5" />
            </a>
            <a href="#productos"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-full font-semibold text-lg glass text-white hover:bg-white/10 transition-all">
              Ver productos
            </a>
          </div>
          <div className="flex items-center justify-center gap-8 mt-12 text-sm text-gray-500">
            <span>🔥 {stats.artists} artistas</span>
            <span>💰 ${(stats.revenue / 1000).toFixed(0)}K generados</span>
            <span>🎵 {(stats.streams / 1000000).toFixed(0)}M streams</span>
          </div>
        </motion.div>
      </section>

      {/* Carousel de Artistas */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold">Artistas que <span className="gradient-text">confían</span></h2>
            <div className="flex gap-2">
              <button onClick={() => scrollCarousel(-1)} className="p-2 rounded-full glass hover:bg-white/10"><ChevronLeft className="w-5 h-5" /></button>
              <button onClick={() => scrollCarousel(1)} className="p-2 rounded-full glass hover:bg-white/10"><ChevronRight className="w-5 h-5" /></button>
            </div>
          </div>
          <div ref={carouselRef} className="flex gap-6 overflow-x-auto scrollbar-hide pb-4 snap-x snap-mandatory">
            {artists.map((a, i) => (
              <motion.a key={a.id} href={`/artist/${a.id}`}
                className="min-w-[280px] snap-start glass rounded-2xl p-6 gradient-border hover:scale-[1.02] transition-all group"
                initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}>
                <div className="text-4xl mb-4">{["🎸","🎤","🎹"][i % 3]}</div>
                <h3 className="text-xl font-bold mb-2">{a.name}</h3>
                <div className="text-2xl font-bold gradient-text">${Number(a.total_revenue || 0).toLocaleString()}</div>
                <div className="text-sm text-gray-400">{(a.total_streams || 0).toLocaleString()} streams</div>
                <div className="mt-4 text-sm text-[#FF6B35] opacity-0 group-hover:opacity-100 transition-opacity">Ver perfil →</div>
              </motion.a>
            ))}
          </div>
        </div>
      </section>

      {/* FOMO Products */}
      <section id="productos" className="py-24 px-4 relative">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-1/2 left-1/3 w-96 h-96 bg-[#FF6B35] rounded-full blur-[100px]" />
        </div>
        <div className="max-w-7xl mx-auto relative">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Lo que <span className="gradient-text">necesitas</span> para triunfar</h2>
            <p className="text-gray-400 max-w-xl mx-auto">Todo lo que un artista necesita para crear, vender y crecer. En un solo lugar.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {FOMO_PRODUCTS.map((p, i) => (
              <motion.div key={p.title}
                className="glass rounded-2xl p-8 gradient-border hover:border-transparent transition-all duration-300"
                initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
                <p.icon className="w-12 h-12 mb-4" style={{ color: p.color }} />
                <h3 className="text-xl font-bold mb-3">{p.title}</h3>
                <p className="text-gray-400 leading-relaxed">{p.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ABE Films — Feature Highlight */}
      <section className="py-24 px-4">
        <div className="max-w-5xl mx-auto glass rounded-3xl p-8 md:p-16 gradient-border relative overflow-hidden">
          <div className="absolute -top-20 -right-20 w-64 h-64 bg-[#b388ff] rounded-full blur-[100px] opacity-30" />
          <div className="relative grid md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass text-xs mb-4">
                <Film className="w-3 h-3 text-[#b388ff]" /> Nuevo
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                <span className="gradient-text">ABE Films</span>
              </h2>
              <p className="text-gray-400 leading-relaxed mb-6">
                Crea videos profesionales con IA. Conciertos virtuales, saludos personalizados para fans, 
                lyric videos, contenido para redes. Todo desde tu celular. Sin estudios caros.
              </p>
              <ul className="space-y-3 mb-8">
                {["Videos AI con tu rostro y voz", "Conciertos virtuales interactivos", "Saludos personalizados para fans", "Lyric videos automáticos", "Contenido para TikTok, IG, YouTube"].map(f => (
                  <li key={f} className="flex items-center gap-2 text-sm text-gray-300"><Check className="w-4 h-4 text-[#b388ff]" />{f}</li>
                ))}
              </ul>
              <a href="/signup" className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-[#b388ff] to-[#FF6B35] text-black font-semibold hover:scale-105 transition-transform">
                Crear videos ahora <ArrowRight className="w-4 h-4" />
              </a>
              <p className="text-xs text-gray-500 mt-3">Disponible en Plan Pro ($49/mes) y Enterprise</p>
            </div>
            <div className="hidden md:block">
              <div className="aspect-[9/16] glass rounded-2xl flex items-center justify-center">
                <Film className="w-16 h-16 text-[#b388ff] opacity-50" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Clon Digital */}
      <section className="py-24 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass text-xs mb-4">
            <Bot className="w-3 h-3 text-[#00ccff]" /> Revolucionario
          </div>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Tu <span className="gradient-text">clon digital</span> vende por ti
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto mb-12">
            Un bot de Telegram con tu personalidad, tu voz, tus fotos. Atiende fans, vende merch, 
            agenda eventos, cobra saludos personalizados. Mientras tú haces música.
          </p>
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {[
              { title: "Vende 24/7", desc: "Tu clon nunca duerme. Vende mientras grabas, mientras viajas, mientras duermes.", color: "#00ccff" },
              { title: "Saludos AI", desc: "Fans pagan por videos personalizados. Tu clon los genera automáticamente.", color: "#FF6B35" },
              { title: "Eventos", desc: "Agenda conciertos, meet & greets, y livestreams. Todo desde el bot.", color: "#00ff88" },
            ].map((f, i) => (
              <motion.div key={f.title} className="glass rounded-xl p-6" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
                <h3 className="font-bold mb-2" style={{ color: f.color }}>{f.title}</h3>
                <p className="text-sm text-gray-400">{f.desc}</p>
              </motion.div>
            ))}
          </div>
          <a href="/signup" className="inline-flex items-center gap-2 px-8 py-4 rounded-full font-semibold mt-10 bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black hover:scale-105 transition-transform">
            Activar mi clon digital <Bot className="w-5 h-5" />
          </a>
        </div>
      </section>

      {/* Pricing CTA */}
      <section className="py-24 px-4">
        <div className="max-w-4xl mx-auto text-center glass rounded-3xl p-12">
          <h2 className="text-3xl font-bold mb-4">¿Listo para <span className="gradient-text">despegar</span>?</h2>
          <p className="text-gray-400 mb-8 max-w-lg mx-auto">Empieza con el Plan Starter ($0) y escala cuando quieras. Sin contratos.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="/signup" className="px-8 py-3 rounded-full font-semibold bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black">Comenzar gratis</a>
            <a href="/pricing" className="px-8 py-3 rounded-full font-semibold glass text-white">Ver planes</a>
          </div>
        </div>
      </section>

      <footer className="glass border-t border-white/5 py-8 px-4 text-center text-sm text-gray-500">
        <p>ABE Music Group · Hecho con ♥ en Hermosillo, Sonora</p>
        <p className="text-xs text-gray-600 mt-1">Powered by Sonora Digital Corp</p>
      </footer>
    </main>
  );
}
