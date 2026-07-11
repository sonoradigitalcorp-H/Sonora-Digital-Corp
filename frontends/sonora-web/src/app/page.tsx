"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, Send, Sparkles, Mic, LogIn, UserPlus, ArrowRight, Check } from "lucide-react";

const API = "https://abe.sonoradigitalcorp.com/api";

const WELCOME_MSG = {
  role: "assistant",
  content: "¡Hola! Soy **Mystik**, tu asistente de Sonora Digital Corp. 🚀\n\nPuedo ayudarte a:\n\n• Conocer nuestros **servicios AI** (chat, voz, imágenes, RAG)\n• Elegir el **plan** ideal para tu negocio\n• **Crear una cuenta** y empezar a usar las herramientas\n\n¿Por dónde quieres empezar?"
};

const QUICK_REPLIES = [
  "¿Qué servicios tienen?",
  "¿Cuánto cuesta?",
  "Quiero crear una cuenta",
  "¿Qué es Mystik AI?",
];

const QUICK_RESPONSES: Record<string, string> = {
  "¿Qué servicios tienen?": "Tenemos **5 servicios** principales:\n\n1. **Mystik AI** — Asistente de ventas con voz y texto\n2. **Content Studio** — Generación de imágenes, TTS, video\n3. **OmniVoice** — Clonación de voz profesional\n4. **Open Notebook** — Knowledge base con RAG\n5. **ABE Music OS** — Gestión para industria musical\n\n¿Quieres ver los planes y precios?",
  "¿Cuánto cuesta?": "Tenemos **3 planes**:\n\n| Plan | Precio | Servicios |\n|------|--------|-----------|\n| **Starter** | **$0/mes** | Mystik AI |\n| **Pro** | **$49/mes** | Mystik AI + Content Studio + OmniVoice |\n| **Enterprise** | **$199/mes** | Todos los servicios |\n\n👉 [Ver planes completos](/pricing) o [crear cuenta gratis](/signup)",
  "Quiero crear una cuenta": "¡Excelente decisión! 🎉\n\nCrea tu cuenta gratis y empieza con Mystik AI:\n\n👉 [Crear cuenta gratis →](/signup)\n\nYa incluye:\n✓ Asistente AI con voz\n✓ 100 chats/mes\n✓ API REST\n✓ Multi-tenant",
  "¿Qué es Mystik AI?": "Soy **Mystik AI** 🤖 — un asistente de ventas inteligente con:\n\n• **Chat** con IA en tiempo real\n• **Voz** natural (STT + TTS) 🎤\n• **CRM** integrado multi-tenant\n• **Knowledge base** con RAG 🧠\n• **Integración** con Mercado Pago 💳\n\nEstoy aquí para ayudarte a vender más. ¿Empezamos?",
};

export default function Home() {
  const [messages, setMessages] = useState<{role: string; content: string}[]>([WELCOME_MSG]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const handleSend = async (text: string) => {
    const msg = text || input;
    if (!msg.trim() || loading) return;
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: msg }]);
    setLoading(true);

    // Check quick responses first
    if (QUICK_RESPONSES[msg]) {
      setTimeout(() => {
        setMessages(prev => [...prev, { role: "assistant", content: QUICK_RESPONSES[msg] }]);
        setLoading(false);
      }, 500);
      return;
    }

    // Fallback to API
    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ message: msg }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", content: data.response || "Lo siento, no pude procesar eso." }]);
    } catch {
      setMessages(prev => [...prev, { role: "assistant", content: "Lo siento, tengo problemas de conexión. ¿Puedes intentar de nuevo?" }]);
    }
    setLoading(false);
  };

  // Hero section with Mystik
  if (!showChat) {
    return (
      <div className="min-h-screen gradient-bg flex flex-col">
        <nav className="glass border-b border-white/5 px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#FF6B35] to-[#00ccff] flex items-center justify-center text-black font-bold text-sm">SD</div>
              <span className="font-bold">Sonora<span className="text-[#FF6B35]">.</span></span>
            </div>
            <div className="flex items-center gap-4">
              <a href="/login" className="text-sm text-gray-400 hover:text-white transition flex items-center gap-1"><LogIn className="w-4 h-4" /> Entrar</a>
              <a href="/signup" className="px-4 py-2 rounded-full bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black font-semibold text-sm hover:scale-105 transition-transform flex items-center gap-1">
                <UserPlus className="w-4 h-4" /> Crear cuenta
              </a>
            </div>
          </div>
        </nav>

        <div className="flex-1 flex items-center justify-center px-4">
          <motion.div className="text-center max-w-3xl" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <motion.div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass text-sm mb-8"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
              <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 3, ease: "linear" }}>
                <Sparkles className="w-4 h-4 text-[#FF6B35]" />
              </motion.div>
              Asistente AI · Voz · Imágenes · RAG
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              Tu <span className="gradient-text">asistente AI</span> para<br />
              hacer crecer tu negocio
            </h1>

            <p className="text-lg md:text-xl text-gray-400 mb-10 max-w-xl mx-auto">
              Mystik te guía, responde y te ayuda a elegir el plan ideal. Desde el primer clic.
            </p>

            <motion.button onClick={() => setShowChat(true)}
              className="inline-flex items-center gap-3 px-8 py-4 rounded-full font-semibold text-lg
              bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black hover:scale-105 transition-transform animate-glow"
              whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Bot className="w-6 h-6" /> Hablar con Mystik
            </motion.button>

            <div className="flex items-center justify-center gap-8 mt-12 text-sm text-gray-500">
              <span className="flex items-center gap-1"><Check className="w-4 h-4 text-[#00ff88]" /> Sin tarjeta</span>
              <span className="flex items-center gap-1"><Check className="w-4 h-4 text-[#00ff88]" /> Multi-tenant</span>
              <span className="flex items-center gap-1"><Check className="w-4 h-4 text-[#00ff88]" /> API incluida</span>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  // Chat interface
  return (
    <div className="min-h-screen gradient-bg flex flex-col">
      <nav className="glass border-b border-white/5 px-6 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <button onClick={() => setShowChat(false)} className="flex items-center gap-2 text-gray-400 hover:text-white transition">
            <Bot className="w-5 h-5 text-[#FF6B35]" />
            <span className="font-semibold">Mystik AI</span>
          </button>
          <div className="flex items-center gap-3">
            <a href="/signup" className="px-4 py-1.5 rounded-full bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black font-semibold text-xs flex items-center gap-1">
              <UserPlus className="w-3 h-3" /> Crear cuenta
            </a>
          </div>
        </div>
      </nav>

      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-4">
          <AnimatePresence>
            {messages.map((msg, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[85%] rounded-2xl px-5 py-3 ${
                  msg.role === "user"
                    ? "bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black"
                    : "glass"
                }`}>
                  <div className="text-sm leading-relaxed whitespace-pre-line [&_a]:text-[#FF6B35] [&_a]:underline">
                    {msg.role === "assistant" ? parseMarkdown(msg.content) : msg.content}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {loading && (
            <div className="flex justify-start">
              <div className="glass rounded-2xl px-5 py-3">
                <div className="flex gap-1">
                  <motion.div animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 1.5 }}>
                    <div className="w-2 h-2 rounded-full bg-[#FF6B35]" />
                  </motion.div>
                  <motion.div animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.2 }}>
                    <div className="w-2 h-2 rounded-full bg-[#FF6B35]" />
                  </motion.div>
                  <motion.div animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.4 }}>
                    <div className="w-2 h-2 rounded-full bg-[#FF6B35]" />
                  </motion.div>
                </div>
              </div>
            </div>
          )}

          {/* Quick replies */}
          {messages.length === 1 && (
            <div className="flex flex-wrap gap-2 justify-center mt-4">
              {QUICK_REPLIES.map((q) => (
                <button key={q} onClick={() => handleSend(q)}
                  className="px-4 py-2 rounded-xl glass text-sm text-gray-300 hover:text-white hover:bg-white/10 transition-all">
                  {q}
                </button>
              ))}
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      <div className="glass border-t border-white/5 px-4 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSend(input)}
            className="flex-1 px-5 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-[#FF6B35] transition-colors"
            placeholder="Escribe tu mensaje..." disabled={loading} />
          <button onClick={() => handleSend(input)} disabled={loading || !input.trim()}
            className="px-5 py-3 rounded-xl bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black disabled:opacity-30 transition-all">
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

function parseMarkdown(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i} className="font-semibold text-white">{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("|") && part.includes("---")) return null;
    if (part.startsWith("|")) {
      const cells = part.split("|").filter(Boolean).map(c => c.trim());
      return <span key={i} className="block text-sm">{cells.join(" · ")}</span>;
    }
    if (part.startsWith("•")) {
      return <span key={i} className="block text-sm ml-2">{part}</span>;
    }
    if (part.startsWith("👉") || part.startsWith("!")) {
      return <span key={i} className="block text-sm">{part}</span>;
    }
    if (part.startsWith("\n")) return <br key={i} />;
    return <span key={i}>{part}</span>;
  });
}
