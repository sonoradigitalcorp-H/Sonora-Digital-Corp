"use client";

import { motion } from "framer-motion";
import Navbar from "@/components/Navbar";
import { Bot, MessageCircle, DollarSign, Users, Calendar, Sparkles, Check, ArrowRight } from "lucide-react";

export default function DigitalClonePage() {
  return (
    <div className="min-h-screen gradient-bg">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 pt-24 pb-24">
        <a href="/#productos" className="text-sm text-gray-500 hover:text-white mb-6 inline-block">← Todos los servicios</a>

        <div className="glass rounded-3xl p-8 md:p-12 mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Bot className="w-8 h-8 text-[#00ccff]" />
            <span className="text-xs px-3 py-1 rounded-full glass text-[#00ccff]">Enterprise</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Tu <span className="gradient-text">clon digital</span>
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mb-8">
            Un bot de Telegram con tu personalidad, tu voz y tus fotos. Atiende fans, vende merch, 
            agenda eventos y cobra saludos personalizados. Mientras tú haces música.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {[
            { icon: DollarSign, title: "Vende 24/7", desc: "Tu clon nunca duerme. Vende merch, entradas, saludos. Automáticamente.", color: "#00ccff" },
            { icon: MessageCircle, title: "Chat con fans", desc: "Responde preguntas, comparte novedades, genera FOMO. Como tú, pero sin descanso.", color: "#FF6B35" },
            { icon: Calendar, title: "Agenda eventos", desc: "Conciertos, meet & greets, livestreams. Todo desde el bot.", color: "#00ff88" },
            { icon: Users, title: "CRM de fans", desc: "Segmenta, envía campañas, ofrece descuentos. Convierte fans en clientes.", color: "#b388ff" },
            { icon: Sparkles, title: "Saludos AI", desc: "Fans pagan por videos personalizados. Tu clon los genera al instante.", color: "#FF6B35" },
            { icon: Bot, title: "Multi-plataforma", desc: "Telegram, WhatsApp, web. Tu clon donde están tus fans.", color: "#00ccff" },
          ].map((f, i) => (
            <motion.div key={f.title} className="glass rounded-xl p-6" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
              <f.icon className="w-8 h-8 mb-3" style={{ color: f.color }} />
              <h3 className="font-semibold mb-2">{f.title}</h3>
              <p className="text-sm text-gray-400">{f.desc}</p>
            </motion.div>
          ))}
        </div>

        <div className="glass rounded-2xl p-8 text-center">
          <h2 className="text-2xl font-bold mb-4">¿Cuánto puedes ganar?</h2>
          <div className="grid md:grid-cols-3 gap-4 max-w-3xl mx-auto mb-8">
            {[
              { item: "Saludos personalizados", price: "$5-20", per: "c/u" },
              { item: "Merch vendido", price: "$25-50", per: "unidad" },
              { item: "Entradas eventos", price: "$10-100", per: "c/u" },
            ].map(s => (
              <div key={s.item} className="glass rounded-xl p-4">
                <div className="text-2xl font-bold text-[#00ff88]">{s.price}</div>
                <div className="text-xs text-gray-400">{s.item}</div>
                <div className="text-xs text-gray-500">{s.per}</div>
              </div>
            ))}
          </div>
          <a href="/signup" className="inline-flex items-center gap-2 px-8 py-3 rounded-full font-semibold bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black hover:scale-105 transition-transform">
            Activar mi clon digital <Bot className="w-5 h-5" />
          </a>
          <p className="text-xs text-gray-500 mt-3">Disponible en Plan Enterprise ($199/mes)</p>
        </div>
      </div>
    </div>
  );
}
