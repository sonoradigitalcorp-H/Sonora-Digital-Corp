"use client";

import { motion } from "framer-motion";
import Navbar from "@/components/Navbar";
import Reveal from "@/components/Reveal";
import { Film, Video, Image, Mic, Bot, Music, Sparkles, Crown, Check, ArrowRight, Star, Gift, Phone, Shirt, Ticket, Calendar } from "lucide-react";

const ARTIST_FEATURES = [
  { icon: Video, title: "Videos AI", desc: "Crea videos profesionales con tu rostro y voz. Lyric videos, conciertos virtuales, saludos para fans." },
  { icon: Image, title: "Imágenes con IA", desc: "Fotos promocionales, portadas de discos, contenido para redes. Todo generado con Flux AI." },
  { icon: Mic, title: "Clonación de voz", desc: "Tu voz clonada para generar contenido sin tener que grabar. Saludos, narraciones, canciones." },
  { icon: Bot, title: "Clon digital", desc: "Un bot que actúa como tú 24/7. Vende merch, agenda eventos, cobra saludos personalizados." },
  { icon: Music, title: "Distribución", desc: "Tu música en todas las plataformas: Spotify, Apple Music, TikTok, YouTube." },
  { icon: Star, title: "Landing automática", desc: "Al suscribirte, tu página de artista se crea automáticamente con tus datos." },
];

const WHAT_YOU_CAN_SELL = [
  { icon: Video, name: "Saludos personalizados", price: "$29-49" },
  { icon: Image, name: "Fotos dedicadas", price: "$19-29" },
  { icon: Mic, name: "Canciones personalizadas", price: "$99-199" },
  { icon: Gift, name: "Mensajes de voz", price: "$9-19" },
  { icon: Phone, name: "Video llamadas", price: "$99-149" },
  { icon: Shirt, name: "Merch (playeras, gorras)", price: "$10-60" },
  { icon: Ticket, name: "Boletos para eventos", price: "$15-65" },
  { icon: Calendar, name: "Booking para eventos", price: "A consultar" },
];

export default function ABEFilmsPage() {
  return (
    <div className="min-h-screen gradient-bg">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 pt-24 pb-24">
        {/* HERO */}
        <Reveal>
          <div className="glass rounded-3xl p-8 md:p-16 mb-12 relative overflow-hidden gradient-border">
            <div className="absolute -top-20 -right-20 w-80 h-80 bg-gold/10 rounded-full blur-[120px]" />
            <div className="relative">
              <div className="flex items-center gap-3 mb-4">
                <Film className="w-8 h-8 text-gold" />
                <span className="text-xs px-3 py-1 rounded-full glass text-gold">ABE Films</span>
              </div>
              <h1 className="font-display text-4xl md:text-6xl font-light mb-6">
                Todo lo que obtienes al <span className="text-gradient-gold italic">integrarte</span>
              </h1>
              <p className="text-lg text-muted-foreground max-w-2xl mb-8">
                Al suscribirte a ABE Music Group, no solo obtienes herramientas de creación. 
                Obtienes una máquina de generar ingresos.
              </p>
              <div className="flex flex-wrap gap-4">
                <a href="/signup" className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-gold text-black font-semibold">
                  Suscribirme ahora <ArrowRight className="w-4 h-4" />
                </a>
                <a href="https://t.me/abeassistant_bot" target="_blank" className="inline-flex items-center gap-2 px-6 py-3 rounded-full border border-gold/30 text-gold hover:bg-gold/10 transition-all">
                  Hablar con ABE Assistant
                </a>
              </div>
            </div>
          </div>
        </Reveal>

        {/* DEMO GALLERY */}
        <Reveal delay={0.1}>
          <div className="mb-16">
            <h2 className="font-display text-3xl font-light mb-6">Contenido generado con <span className="text-gradient-gold italic">ABE Films</span></h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { src: "/images/gallery/hector-rubio/flux-0.jpg", label: "Concierto" },
                { src: "/images/gallery/hector-rubio/flux-1.jpg", label: "Studio" },
                { src: "/images/demo/merch/flux-0.jpg", label: "Merch" },
                { src: "/images/demo/concert/flux-0.jpg", label: "Evento" },
              ].map((img, i) => (
                <div key={i} className="glass rounded-xl overflow-hidden aspect-[4/3]">
                  <img src={img.src} alt={img.label}
                    className="w-full h-full object-cover"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                </div>
              ))}
            </div>
          </div>
        </Reveal>

        {/* FEATURES GRID */}
        <Reveal delay={0.2}>
          <h2 className="font-display text-3xl font-light mb-8">Lo que incluye tu membresía</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-16">
            {ARTIST_FEATURES.map((f, i) => (
              <motion.div key={f.title} initial={{opacity:0, y:20}} whileInView={{opacity:1, y:0}} viewport={{once: true}} transition={{delay: i*0.05}}
                className="glass rounded-xl p-6 hover:border-gold/30 transition-all">
                <f.icon className="w-8 h-8 text-gold mb-3" />
                <h3 className="font-semibold mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </Reveal>

        {/* WHAT YOU CAN SELL */}
        <Reveal delay={0.2}>
          <div className="glass rounded-3xl p-8 md:p-12 mb-12">
            <h2 className="font-display text-3xl font-light mb-4 flex items-center gap-2"><Crown className="w-6 h-6 text-gold" /> Lo que puedes vender</h2>
            <p className="text-muted-foreground mb-8">Como artista de ABE Music, puedes ofrecer todo esto a tus fans y generar ingresos.</p>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {WHAT_YOU_CAN_SELL.map((item, i) => (
                <div key={item.name} className="glass rounded-xl p-4 text-center">
                  <item.icon className="w-6 h-6 text-gold mx-auto mb-2" />
                  <div className="text-sm font-semibold mb-1">{item.name}</div>
                  <div className="text-xs text-muted-foreground">{item.price}</div>
                </div>
              ))}
            </div>
          </div>
        </Reveal>

        {/* PRICING */}
        <Reveal delay={0.3}>
          <div className="text-center">
            <h2 className="font-display text-3xl font-light mb-8">Planes</h2>
            <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              {[
                { name: "Starter", price: "$0", features: ["Landing automática", "1 video/mes", "Chat con fans"], cta: "Comenzar" },
                { name: "Pro", price: "$49", features: ["Todo Starter", "10 videos/mes", "Clon digital", "Tienda online", "Booking"], cta: "Elegir Pro", popular: true },
                { name: "Enterprise", price: "$199", features: ["Todo Pro", "Videos ilimitados", "Distribución global", "CRM de fans", "Soporte 24/7"], cta: "Elegir Enterprise" },
              ].map((p, i) => (
                <div key={p.name} className={`glass rounded-2xl p-6 ${p.popular ? 'gradient-border' : ''}`}>
                  {p.popular && <div className="text-xs text-gold font-semibold mb-2">MÁS POPULAR</div>}
                  <h3 className="font-display text-xl font-medium mb-1">{p.name}</h3>
                  <div className="text-3xl font-bold text-gold mb-4">{p.price}<span className="text-sm text-muted-foreground">/mes</span></div>
                  <ul className="space-y-2 mb-6">
                    {p.features.map(f => (
                      <li key={f} className="flex items-center gap-2 text-sm text-muted-foreground"><Check className="w-4 h-4 text-gold shrink-0" />{f}</li>
                    ))}
                  </ul>
                  <a href="/signup" className={`block text-center py-2.5 rounded-full font-semibold text-sm ${p.popular ? 'bg-gradient-gold text-black' : 'glass text-foreground hover:bg-white/10'}`}>{p.cta}</a>
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      </div>

      <footer className="border-t border-gold/10 py-6 px-4 text-center text-xs text-muted-foreground">
        <p>© 2026 ABE Music Group</p>
      </footer>
    </div>
  );
}
