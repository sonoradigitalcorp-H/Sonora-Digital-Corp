"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Bot, Mic, Image, ArrowRight, ArrowLeft, Sparkles, Radio, Music } from "lucide-react";

const API = "https://abe.sonoradigitalcorp.com/api";

const STEPS = [
  { title: "Tu empresa", desc: "Cuéntanos sobre tu negocio" },
  { title: "Servicios", desc: "Elige los servicios que necesitas" },
  { title: "API Key", desc: "Tu llave de acceso" },
];

const ALL_SERVICES = [
  { id: "mystik-ai", name: "Mystik AI", icon: Bot, color: "#FF6B35", desc: "Asistente de ventas con voz" },
  { id: "content-studio", name: "Content Studio", icon: Image, color: "#b388ff", desc: "Generación de contenido AI" },
  { id: "omnivoice", name: "OmniVoice", icon: Mic, color: "#00ccff", desc: "Clonación de voz" },
  { id: "open-notebook", name: "Open Notebook", icon: Radio, color: "#ff6b6b", desc: "Knowledge base RAG" },
  { id: "abe-music", name: "ABE Music OS", icon: Music, color: "#00ff88", desc: "Gestión musical" },
];

export default function OnboardingPage() {
  const [step, setStep] = useState(0);
  const [token, setToken] = useState("");
  const [company, setCompany] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [apiKey, setApiKey] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const t = localStorage.getItem("token");
    if (!t) { window.location.href = "/login"; return; }
    setToken(t);
    fetch(`${API}/dashboard`, { headers: { "Authorization": `Bearer ${t}` } })
      .then(r => r.json()).then(d => {
        setCompany(d?.tenant?.name || "");
        setApiKey(d?.tenant?.id ? `sdc_${d.tenant.id}_${Math.random().toString(36).substring(2, 10)}` : "");
      }).catch(() => {});
  }, []);

  const finish = () => {
    setLoading(true);
    setTimeout(() => window.location.href = "/dashboard", 1000);
  };

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center px-4 py-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-8 max-w-2xl w-full">
        <div className="flex items-center justify-between mb-8">
          {STEPS.map((s, i) => (
            <div key={i} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                i <= step ? "bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black" : "glass text-gray-500"
              }`}>{i + 1}</div>
              {i < STEPS.length - 1 && <div className={`w-16 h-0.5 mx-2 ${i < step ? "bg-[#FF6B35]" : "bg-white/10"}`} />}
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {step === 0 && (
            <motion.div key="step0" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <h2 className="text-2xl font-bold mb-2">{STEPS[0].title}</h2>
              <p className="text-gray-400 mb-6">{STEPS[0].desc}</p>
              <div>
                <label className="text-sm text-gray-400 block mb-2">Nombre de la empresa</label>
                <input value={company} onChange={e => setCompany(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-[#FF6B35]"
                  placeholder="Mi Empresa SA de CV" />
              </div>
            </motion.div>
          )}

          {step === 1 && (
            <motion.div key="step1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <h2 className="text-2xl font-bold mb-2">{STEPS[1].title}</h2>
              <p className="text-gray-400 mb-6">{STEPS[1].desc}</p>
              <div className="grid gap-3">
                {ALL_SERVICES.map(s => {
                  const active = selected.includes(s.id);
                  return (
                    <button key={s.id} onClick={() => setSelected(prev => prev.includes(s.id) ? prev.filter(x => x !== s.id) : [...prev, s.id])}
                      className={`flex items-center gap-4 p-4 rounded-xl text-left transition-all ${
                        active ? "bg-white/10 border border-[#FF6B35]" : "glass hover:bg-white/5"
                      }`}>
                      <s.icon className="w-8 h-8" style={{ color: s.color }} />
                      <div className="flex-1">
                        <div className="font-semibold">{s.name}</div>
                        <div className="text-sm text-gray-400">{s.desc}</div>
                      </div>
                      {active && <Check className="w-5 h-5 text-[#00ff88]" />}
                    </button>
                  );
                })}
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <h2 className="text-2xl font-bold mb-2">{STEPS[2].title}</h2>
              <p className="text-gray-400 mb-6">{STEPS[2].desc}</p>
              <div className="glass rounded-xl p-6 text-center">
                <Sparkles className="w-10 h-10 text-[#FF6B35] mx-auto mb-3" />
                <div className="font-mono text-sm bg-black/30 rounded-lg p-3 mb-4 break-all">{apiKey || "Generando..."}</div>
                <p className="text-xs text-gray-500">Guarda esta llave. La necesitarás para conectarte a la API.</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex justify-between mt-8">
          <button onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0}
            className="flex items-center gap-2 px-4 py-2 rounded-xl glass text-gray-400 disabled:opacity-30">
            <ArrowLeft className="w-4 h-4" /> Anterior
          </button>
          {step < STEPS.length - 1 ? (
            <button onClick={() => setStep(step + 1)}
              className="flex items-center gap-2 px-6 py-2 rounded-xl bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black font-semibold">
              Siguiente <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button onClick={finish} disabled={loading}
              className="flex items-center gap-2 px-6 py-2 rounded-xl bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black font-semibold disabled:opacity-50">
              {loading ? "Finalizando..." : "Ir al panel"} <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
}
