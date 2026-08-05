"use client";

import { motion } from "framer-motion";
import { Bot, Mic, MessageCircle, Users, Database, Shield } from "lucide-react";

export default function MystikPage() {
  return (
    <div className="min-h-screen gradient-bg">
      <div className="max-w-6xl mx-auto px-4 py-24">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <a href="/" className="text-sm text-gray-500 hover:text-white mb-8 inline-block">← Volver</a>
          <h1 className="text-5xl font-bold mb-4">
            <span className="gradient-text">Mystik AI</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mb-12">
            Asistente de ventas inteligente con voz y texto. Multi-tenant, CRM integrado, clonación de voz.
          </p>

          <div className="grid md:grid-cols-3 gap-6 mb-16">
            {[
              { icon: MessageCircle, title: "Chat con IA", desc: "Responde preguntas sobre productos, califica leads, agenda demos." },
              { icon: Mic, title: "Voz Natural", desc: "TTS con voz mexicana femenina. Whisper STT + edge-tts + OpenVoice cloning." },
              { icon: Users, title: "Multi-Tenant", desc: "Cada empresa cliente aislada con su propio CRM, config y knowledge base." },
              { icon: Database, title: "Knowledge Base", desc: "ChromaDB RAG con documentación de todos los productos SDC." },
              { icon: Bot, title: "MCP Nativo", desc: "6 MCP tools expuestas. Redis Agent Bus para comunicación entre agentes." },
              { icon: Shield, title: "Seguro", desc: "Rate limiting, prompt injection guard, CORS restrictivo, Redis ACL." },
            ].map((f, i) => (
              <motion.div key={f.title} className="glass rounded-xl p-6"
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
                <f.icon className="w-8 h-8 text-[#FF6B35] mb-3" />
                <h3 className="font-semibold mb-2">{f.title}</h3>
                <p className="text-sm text-gray-400">{f.desc}</p>
              </motion.div>
            ))}
          </div>

          <div className="glass rounded-2xl p-8">
            <h2 className="text-2xl font-bold mb-4">Probar Mystik</h2>
            <div className="grid md:grid-cols-2 gap-4">
              <a href="http://149.56.46.173:5200" className="glass rounded-xl p-4 text-center hover:border-[#FF6B35] transition-all">
                <Bot className="w-6 h-6 mx-auto mb-2 text-[#FF6B35]" />
                <div className="font-semibold">API</div>
                <div className="text-xs text-gray-500">:5200/api/chat</div>
              </a>
              <a href="http://149.56.46.173:5200/api/voice/speak?text=Hola" className="glass rounded-xl p-4 text-center hover:border-[#FF6B35] transition-all">
                <Mic className="w-6 h-6 mx-auto mb-2 text-[#FF6B35]" />
                <div className="font-semibold">Voz</div>
                <div className="text-xs text-gray-500">TTS en vivo</div>
              </a>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
