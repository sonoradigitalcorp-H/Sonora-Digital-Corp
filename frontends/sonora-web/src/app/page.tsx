"use client";

import { motion } from "framer-motion";
import { Bot, Mic, Image, Radio, Music, Cloud, LogIn, UserPlus, Check, Star, ArrowRight } from "lucide-react";

const PLANS = [
  {
    name: "Starter",
    price: "$0",
    period: "/mes",
    desc: "Perfecto para probar las capacidades de SDC.",
    features: ["1 agente AI", "100 chats/mes", "API REST", "Community support"],
    cta: "Comenzar gratis",
    popular: false,
  },
  {
    name: "Pro",
    price: "$49",
    period: "/mes",
    desc: "Para negocios que quieren automatizar ventas.",
    features: ["3 agentes AI", "10,000 chats/mes", "Voz + TTS", "CRM integrado", "Multi-tenant", "Soporte prioritario"],
    cta: "Elegir Pro",
    popular: true,
  },
  {
    name: "Enterprise",
    price: "$199",
    period: "/mes",
    desc: "Para empresas con necesidades avanzadas.",
    features: ["Agentes ilimitados", "Chats ilimitados", "Voz clonada", "CRM + ERP", "Multi-tenant aislado", "On-premise option", "Soporte 24/7", "SLA 99.9%"],
    cta: "Contactar",
    popular: false,
  },
];

const SERVICES = [
  {
    id: "mystik-ai",
    name: "Mystik AI",
    tagline: "Asistente de ventas con voz",
    desc: "AI conversacional que califica leads, presenta productos y cierra ventas. Multi-tenant, CRM integrado, voz natural.",
    icon: Bot,
    color: "#FF6B35",
    features: ["Chat con IA", "Voz (STT + TTS)", "CRM multi-tenant", "Knowledge base RAG", "Analytics"],
    starter: true, pro: true, enterprise: true,
  },
  {
    id: "content-studio",
    name: "Content Studio",
    tagline: "Generación de contenido AI",
    desc: "Crea imágenes, TTS, talking heads, OCR y edición via MCP. 20+ herramientas de generación.",
    icon: Image,
    color: "#b388ff",
    features: ["Imágenes AI", "Text-to-Speech", "Talking Heads", "OCR", "20+ MCP tools"],
    starter: false, pro: true, enterprise: true,
  },
  {
    id: "omnivoice",
    name: "OmniVoice",
    tagline: "Clonación de voz profesional",
    desc: "Clona cualquier voz con 10 segundos de audio. Síntesis multi-idioma con API REST.",
    icon: Mic,
    color: "#00ccff",
    features: ["Clonación zero-shot", "Multi-idioma", "API REST", "Perfiles de voz"],
    starter: false, pro: true, enterprise: true,
  },
  {
    id: "open-notebook",
    name: "Open Notebook",
    tagline: "Knowledge base con RAG",
    desc: "Alternativa open-source a NotebookLM. Sube PDFs, URLs, documentos. Chat con tu knowledge base.",
    icon: Radio,
    color: "#ff6b6b",
    features: ["RAG sobre PDFs", "Web scraping", "Generación de podcasts", "API REST"],
    starter: false, pro: false, enterprise: true,
  },
  {
    id: "abe-music",
    name: "ABE Music OS",
    tagline: "Gestión para industria musical",
    desc: "Plataforma completa para sellos discográficos: revenue, contratos, CRM de fans, distribución.",
    icon: Music,
    color: "#00ff88",
    features: ["Revenue ledger", "Contratos inteligentes", "CRM de fans", "Distribución", "Bot Telegram"],
    starter: false, pro: false, enterprise: true,
  },
];

function Navbar() {
  return (
    <nav className="fixed top-0 w-full z-50 glass">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <a href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#FF6B35] to-[#00ccff] flex items-center justify-center text-black font-bold text-sm">SD</div>
          <span className="font-bold">Sonora<span className="text-[#FF6B35]">.</span></span>
        </a>
        <div className="hidden md:flex items-center gap-6 text-sm">
          <a href="#servicios" className="text-gray-400 hover:text-white transition">Servicios</a>
          <a href="#planes" className="text-gray-400 hover:text-white transition">Planes</a>
          <a href="/login" className="text-gray-400 hover:text-white transition flex items-center gap-1"><LogIn className="w-4 h-4" /> Iniciar sesión</a>
          <a href="/signup" className="px-4 py-2 rounded-full bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black font-semibold text-sm hover:scale-105 transition-transform flex items-center gap-1">
            <UserPlus className="w-4 h-4" /> Crear cuenta
          </a>
        </div>
      </div>
    </nav>
  );
}

function Hero() {
  return (
    <section className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden gradient-bg px-4">
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-1/3 left-1/3 w-96 h-96 bg-[#FF6B35] rounded-full blur-[128px]" />
        <div className="absolute bottom-1/3 right-1/3 w-96 h-96 bg-[#00ccff] rounded-full blur-[128px]" />
      </div>
      <motion.div className="relative z-10 text-center max-w-4xl"
        initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass text-sm text-gray-300 mb-8">
          <Star className="w-4 h-4 text-[#FF6B35]" />
          Plataforma AI para empresas
        </div>
        <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
          Inteligencia Artificial para <br />
          <span className="gradient-text">tu negocio</span>
        </h1>
        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10">
          Asistentes AI, generación de contenido, clonación de voz y más.
          Todo en una plataforma multi-tenant, segura y lista para empresas.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a href="/signup"
            className="inline-flex items-center gap-2 px-8 py-3 rounded-full font-semibold
            bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black hover:scale-105 transition-transform">
            Crear cuenta gratis <ArrowRight className="w-4 h-4" />
          </a>
          <a href="#servicios"
            className="inline-flex items-center gap-2 px-8 py-3 rounded-full font-semibold glass text-white hover:bg-white/10 transition-all">
            Ver servicios
          </a>
        </div>
      </motion.div>
    </section>
  );
}

function ServicesSection() {
  return (
    <section id="servicios" className="py-32 px-4">
      <div className="max-w-7xl mx-auto">
        <motion.div className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <h2 className="text-4xl font-bold mb-4">Nuestros <span className="gradient-text">Servicios</span></h2>
          <p className="text-gray-400 max-w-xl mx-auto">Cada servicio funciona independientemente o integrado. Todos via API, MCP o web.</p>
        </motion.div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {SERVICES.map((svc, i) => (
            <motion.div key={svc.id}
              className="glass rounded-2xl p-6 gradient-border hover:border-transparent transition-all duration-300"
              initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
              <svc.icon className="w-10 h-10 mb-4" style={{ color: svc.color }} />
              <h3 className="text-lg font-semibold mb-1">{svc.name}</h3>
              <p className="text-sm text-gray-500 mb-1">{svc.tagline}</p>
              <p className="text-sm text-gray-400 mb-4 leading-relaxed">{svc.desc}</p>
              <div className="flex flex-wrap gap-1.5 mb-4">
                {svc.features.map((f) => (
                  <span key={f} className="text-xs px-2 py-1 rounded-full bg-white/5 text-gray-300">{f}</span>
                ))}
              </div>
              <div className="flex gap-2 text-xs text-gray-500">
                {svc.starter && <span className="text-gray-400">✓ Starter</span>}
                {svc.pro && <span className="text-[#FF6B35]">✓ Pro</span>}
                {svc.enterprise && <span className="text-[#00ccff]">✓ Enterprise</span>}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function PlansSection() {
  return (
    <section id="planes" className="py-32 px-4 relative">
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-0 w-96 h-96 bg-[#00ff88] rounded-full blur-[100px]" />
      </div>
      <div className="max-w-7xl mx-auto relative">
        <motion.div className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <h2 className="text-4xl font-bold mb-4">Planes <span className="gradient-text">Flexibles</span></h2>
          <p className="text-gray-400 max-w-xl mx-auto">Todos los planes incluyen API, SSL, y multi-tenant. Escala cuando quieras.</p>
        </motion.div>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {PLANS.map((plan, i) => (
            <motion.div key={plan.name}
              className={`relative rounded-2xl p-8 ${plan.popular ? 'gradient-border' : 'glass'}`}
              initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black text-xs font-semibold">
                  Más popular
                </div>
              )}
              <div className={plan.popular ? '' : ''}>
                <h3 className="text-xl font-bold">{plan.name}</h3>
                <div className="mt-4 mb-6">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="text-gray-500">{plan.period}</span>
                </div>
                <p className="text-sm text-gray-400 mb-6">{plan.desc}</p>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-gray-300">
                      <Check className="w-4 h-4 text-[#00ff88] mt-0.5 shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
                <a href={plan.name === "Enterprise" ? "/contact" : "/signup"}
                  className={`block text-center py-3 rounded-xl font-semibold text-sm transition-all ${
                    plan.popular
                      ? 'bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black hover:scale-105'
                      : 'glass text-white hover:bg-white/10'
                  }`}>
                  {plan.cta}
                </a>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="glass border-t border-white/5 py-12 px-4">
      <div className="max-w-7xl mx-auto text-center">
        <div className="flex items-center justify-center gap-2 mb-4">
          <div className="w-6 h-6 rounded bg-gradient-to-br from-[#FF6B35] to-[#00ccff] flex items-center justify-center text-black font-bold text-xs">SD</div>
          <span className="font-bold">Sonora<span className="text-[#FF6B35]">.</span></span>
        </div>
        <p className="text-sm text-gray-500 mb-4">© 2026 Sonora Digital Corp. All rights reserved.</p>
        <div className="flex justify-center gap-4 text-sm text-gray-600">
          <a href="/login" className="hover:text-white transition">Iniciar sesión</a>
          <a href="/signup" className="hover:text-white transition">Crear cuenta</a>
          <a href="/terms" className="hover:text-white transition">Términos</a>
          <a href="/privacy" className="hover:text-white transition">Privacidad</a>
        </div>
      </div>
    </footer>
  );
}

export default function Home() {
  return (
    <main className="min-h-screen">
      <Navbar />
      <Hero />
      <ServicesSection />
      <PlansSection />
      <Footer />
    </main>
  );
}
