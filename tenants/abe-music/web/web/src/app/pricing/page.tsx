"use client";

import { motion } from "framer-motion";
import { Check, ArrowRight, Sparkles } from "lucide-react";

const PLANS = [
  { id: "starter", name: "Starter", price: "$0", period: "/mes", desc: "Perfecto para empezar",
    features: ["1 agente AI", "100 chats/mes", "API REST", "1 tenant", "Community support"],
    cta: "Comenzar gratis" },
  { id: "pro", name: "Pro", price: "$49", period: "/mes", desc: "Para negocios en crecimiento",
    features: ["3 agentes AI", "10,000 chats/mes", "Voz + TTS", "CRM integrado", "Multi-tenant", "Soporte prioritario"],
    cta: "Elegir Pro", popular: true },
  { id: "enterprise", name: "Enterprise", price: "$199", period: "/mes", desc: "Para empresas",
    features: ["Agentes ilimitados", "Chats ilimitados", "Voz clonada", "CRM + ERP", "Multi-tenant aislado", "On-premise", "Soporte 24/7", "SLA 99.9%"],
    cta: "Contactar" },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen gradient-bg">
      <nav className="glass border-b border-white/5 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <a href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#FF6B35] to-[#00ccff] flex items-center justify-center text-black font-bold text-sm">SD</div>
            <span className="font-bold">Sonora<span className="text-[#FF6B35]">.</span></span>
          </a>
          <a href="/login" className="text-sm text-gray-400 hover:text-white transition">Iniciar sesión</a>
        </div>
      </nav>
      <div className="max-w-6xl mx-auto px-4 py-24">
        <motion.div className="text-center mb-16" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-5xl font-bold mb-4">Planes <span className="gradient-text">Flexibles</span></h1>
          <p className="text-gray-400 max-w-xl mx-auto">Todos los planes incluyen API, SSL, y multi-tenant. Sin contratos.</p>
        </motion.div>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {PLANS.map((plan, i) => (
            <motion.div key={plan.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
              className={`relative rounded-2xl p-8 ${plan.popular ? 'gradient-border' : 'glass'}`}>
              {plan.popular && <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black text-xs font-semibold">Más popular</div>}
              <h3 className="text-xl font-bold mb-1">{plan.name}</h3>
              <div className="mt-4 mb-2"><span className="text-4xl font-bold">{plan.price}</span><span className="text-gray-500">{plan.period}</span></div>
              <p className="text-sm text-gray-400 mb-6">{plan.desc}</p>
              <ul className="space-y-3 mb-8">
                {plan.features.map(f => (
                  <li key={f} className="flex items-start gap-2 text-sm text-gray-300">
                    <Check className="w-4 h-4 text-[#00ff88] mt-0.5 shrink-0" />{f}
                  </li>
                ))}
              </ul>
              <a href="/signup" className={`block text-center py-3 rounded-xl font-semibold text-sm transition-all ${
                plan.popular ? 'bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black hover:scale-105' : 'glass text-white hover:bg-white/10'}`}>
                {plan.cta}
              </a>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
