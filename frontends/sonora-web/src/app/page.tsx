"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import {
  Sparkles, Music, Bot, Globe, Wallet, Mic, Zap, ChevronDown,
  ArrowRight, ExternalLink, Shield, Cpu, Cloud, Radio, CodeXml,
} from "lucide-react";
import { useRef } from "react";



// ── Productos ──
const PRODUCTS = [
  {
    id: "abe-music",
    name: "ABE Music OS",
    desc: "Gestión inteligente para la industria musical. Revenue, contratos, CRM de fans, distribución multi-plataforma.",
    icon: Music,
    color: "#00ff88",
    href: "http://149.56.46.173:5180",
    tags: ["API REST", "WebSocket", "PWA"],
  },
  {
    id: "mystik",
    name: "Mystik AI",
    desc: "Asistente de ventas con voz y texto. Multi-tenant, CRM integrado, clonación de voz, knowledge base RAG.",
    icon: Bot,
    color: "#FF6B35",
    href: "http://149.56.46.173:5200",
    tags: ["AI", "Voz", "Chat"],
  },
  {
    id: "content-studio",
    name: "Content Studio",
    desc: "Generación de contenido AI: imágenes, TTS, talking heads, OCR, edición. 20+ herramientas MCP.",
    icon: Zap,
    color: "#b388ff",
    href: "/products/content-studio",
    tags: ["MCP", "Imágenes", "TTS"],
  },
  {
    id: "omnivoice",
    name: "OmniVoice",
    desc: "Clonación de voz AI. API de síntesis multi-idioma. Perfiles de voz personalizados.",
    icon: Mic,
    color: "#00ccff",
    href: "/products/omnivoice",
    tags: ["Voz", "API", "Clonación"],
  },
  {
    id: "open-notebook",
    name: "Open Notebook",
    desc: "Alternativa open-source a NotebookLM. RAG sobre PDFs, web, documentos. Genera podcasts.",
    icon: Radio,
    color: "#ff6b6b",
    href: "/products/open-notebook",
    tags: ["RAG", "PDF", "Podcast"],
  },
  {
    id: "abe-bot",
    name: "ABE Telegram Bot",
    desc: "Bot de Telegram con 98 skills. Gestión musical, reportes, revenue, contratos desde Telegram.",
    icon: Bot,
    color: "#26a5e4",
    href: "https://t.me/abe_music_bot",
    tags: ["Telegram", "98 skills"],
  },
];

// ── Stats ──
const STATS = [
  { label: "Revenue Gestionado", value: "$479K", icon: Wallet },
  { label: "Streams Procesados", value: "120M", icon: Radio },
  { label: "Servicios Activos", value: "15+", icon: Cpu },
  { label: "Tests Pasando", value: "759", icon: Shield },
];

// ── Componentes ──
function Navbar() {
  return (
    <nav className="fixed top-0 w-full z-50 glass">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <a href="/" className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-[#FF6B35]" />
          <span className="font-bold text-lg">Sonora<span className="text-[#FF6B35]">.</span>Digital</span>
        </a>
        <div className="hidden md:flex items-center gap-6 text-sm text-gray-400">
          <a href="#productos" className="hover:text-white transition">Productos</a>
          <a href="#ecosistema" className="hover:text-white transition">Ecosistema</a>
          <a href="http://149.56.46.173:5200" className="hover:text-white transition">Mystik AI</a>
          <a href="http://149.56.46.173:5180" className="hover:text-white transition">ABE Music</a>
          <a href="https://github.com/sonoradigitalcorp-H" className="hover:text-white transition flex items-center gap-1">
            <CodeXml className="w-4 h-4" /> GitHub
          </a>
        </div>
      </div>
    </nav>
  );
}

function Hero() {
  return (
    <section className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden gradient-bg">
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#FF6B35] rounded-full blur-[128px]" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#00ccff] rounded-full blur-[128px]" />
      </div>
      <motion.div
        className="relative z-10 text-center px-4 max-w-4xl"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <motion.div
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass text-sm text-gray-300 mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <Sparkles className="w-4 h-4 text-[#FF6B35]" />
          Ecosistema AI open-source
        </motion.div>
        <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
          El futuro de la{" "}
          <span className="gradient-text">música y los negocios</span>
          <br />con Inteligencia Artificial
        </h1>
        <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10">
          Sonora Digital Corp construye sistemas anti-frágiles, auto-mejorables y multi-tenant
          para la industria musical y empresarial. 100% open-source.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a href="#productos"
            className="inline-flex items-center justify-center gap-2 px-8 py-3 rounded-full font-semibold
            bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black hover:scale-105 transition-transform">
            Ver productos <ArrowRight className="w-4 h-4" />
          </a>
          <a href="http://149.56.46.173:5200"
            className="inline-flex items-center justify-center gap-2 px-8 py-3 rounded-full font-semibold
            glass text-white hover:bg-white/10 transition-all">
            Hablar con Mystik <Bot className="w-4 h-4" />
          </a>
        </div>
      </motion.div>

      {/* Stats */}
      <motion.div
        className="relative z-10 grid grid-cols-2 md:grid-cols-4 gap-6 mt-20 max-w-4xl mx-auto px-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.6 }}
      >
        {STATS.map((stat) => (
          <div key={stat.label} className="glass rounded-xl p-4 text-center">
            <stat.icon className="w-5 h-5 mx-auto mb-2 text-[#FF6B35]" />
            <div className="text-xl font-bold gradient-text">{stat.value}</div>
            <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
          </div>
        ))}
      </motion.div>

      <motion.div className="absolute bottom-8" animate={{ y: [0, 8, 0] }} transition={{ repeat: Infinity, duration: 2 }}>
        <ChevronDown className="w-6 h-6 text-gray-500" />
      </motion.div>
    </section>
  );
}

function ProductsSection() {
  return (
    <section id="productos" className="py-32 px-4">
      <div className="max-w-7xl mx-auto">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl font-bold mb-4">Productos del <span className="gradient-text">Ecosistema</span></h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            Cada producto es una capability independiente. Todos se comunican via MCP, Redis y APIs REST.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {PRODUCTS.map((product, i) => (
            <motion.a
              key={product.id}
              href={product.href}
              target={product.href.startsWith("http") ? "_blank" : undefined}
              className="card-3d group"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <div className="card-3d-inner glass rounded-2xl p-6 h-full gradient-border hover:border-transparent transition-all duration-300">
                <product.icon className="w-10 h-10 mb-4" style={{ color: product.color }} />
                <h3 className="text-lg font-semibold mb-2">{product.name}</h3>
                <p className="text-sm text-gray-400 mb-4 leading-relaxed">{product.desc}</p>
                <div className="flex flex-wrap gap-2">
                  {product.tags.map((tag) => (
                    <span key={tag} className="text-xs px-2 py-1 rounded-full" style={{
                      background: `${product.color}15`,
                      color: product.color,
                    }}>
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </motion.a>
          ))}
        </div>
      </div>
    </section>
  );
}

function EcosystemSection() {
  return (
    <section id="ecosistema" className="py-32 px-4 relative overflow-hidden">
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-0 right-0 w-64 h-64 bg-[#00ff88] rounded-full blur-[100px]" />
      </div>
      <div className="max-w-7xl mx-auto relative">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl font-bold mb-4">Arquitectura del <span className="gradient-text">Sistema</span></h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            7 kernels cognitivos · MCP nativo · Redis Agent Bus · 759 tests · Todo open-source
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {[
            { icon: Cpu, title: "7 Kernels Cognitivos", desc: "L1 Observe → L7 Control. Pipeline completo de datos, decisiones, acciones y aprendizaje." },
            { icon: Cloud, title: "MCP Nativo", desc: "188 tools MCP expuestas via Gateway. Mystik, Hermes, OpenClaw y más como tools." },
            { icon: Radio, title: "Redis Agent Bus", desc: "4 canales: messages, context, events, commands. Agentes se comunican en tiempo real." },
            { icon: Shield, title: "Seguridad por Capas", desc: "Rate limiting, CORS restrictivo, PostgreSQL scram-sha-256, Redis ACL, prompt injection guard." },
            { icon: Globe, title: "Multi-Tenant", desc: "Cada cliente aislado en su propio tenant. CRM, config, y knowledge base independientes." },
            { icon: Zap, title: "Auto-Mejora", desc: "Founder Dependency Index (81/100), Enterprise Score (60/100), Weekly Reports automáticos." },
          ].map((item, i) => (
            <motion.div
              key={item.title}
              className="glass rounded-xl p-6"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <item.icon className="w-8 h-8 text-[#FF6B35] mb-3" />
              <h3 className="font-semibold mb-2">{item.title}</h3>
              <p className="text-sm text-gray-400">{item.desc}</p>
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
          <Sparkles className="w-5 h-5 text-[#FF6B35]" />
          <span className="font-bold">Sonora<span className="text-[#FF6B35]">.</span>Digital</span>
        </div>
        <p className="text-sm text-gray-500 mb-4">
          Hecho con ♥ en Hermosillo, Sonora · 100% open-source · Apache 2.0
        </p>
        <div className="flex justify-center gap-4 text-sm text-gray-600">
          <a href="https://github.com/sonoradigitalcorp-H" className="hover:text-white transition">GitHub</a>
          <a href="http://149.56.46.173:5200" className="hover:text-white transition">Mystik AI</a>
          <a href="http://149.56.46.173:5180" className="hover:text-white transition">ABE Music</a>
          <a href="http://149.56.46.173:8001" className="hover:text-white transition">Coolify</a>
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
      <ProductsSection />
      <EcosystemSection />
      <Footer />
    </main>
  );
}
