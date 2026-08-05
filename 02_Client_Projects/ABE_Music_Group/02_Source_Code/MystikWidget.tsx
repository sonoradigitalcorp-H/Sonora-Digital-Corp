"use client";

import { useState } from "react";
import { Bot, X, Send } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const API = "https://abe.sonoradigitalcorp.com/api";
const QUICK_ACTIONS = [
  "Qué servicios ofrecen?",
  "Cuánto cuesta?",
  "Quiero crear contenido",
  "Cómo vender mi música?",
];

export default function ABEAssistantWidget() {
  const [sessionId] = useState(() => `web-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`);
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<{role:string; content:string}[]>([
    {role:"assistant", content:"🎵 ¡Hola! Soy el asistente de ABE Music Group.\n\n¿En qué puedo ayudarte?\n\n• Conocer nuestros **servicios**\n• Ver **planes y precios**\n• Información sobre **artistas**\n• Crear **contenido** con IA\n• **Vender** tu música\n\nSolo dime qué necesitas."},
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async (text?: string) => {
    const msg = text || input;
    if (!msg.trim() || loading) return;
    setInput("");
    setMessages(prev => [...prev, {role:"user", content: msg}]);
    setLoading(true);
    try {
      const res = await fetch(`${API}/chat`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({message: msg, session_id: sessionId}),
      });
      const data = await res.json();
      setMessages(prev => [...prev, {role:"assistant", content: data.response || "Lo siento, no pude procesar eso."}]);
    } catch {
      setMessages(prev => [...prev, {role:"assistant", content:"Disculpa, tengo problemas de conexión."}]);
    }
    setLoading(false);
  };

  return (
    <>
      <button onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-gold text-black flex items-center justify-center shadow-lg hover:scale-110 transition-transform animate-glow">
        <Bot className="w-6 h-6" />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div initial={{opacity:0, y:20, scale:0.95}} animate={{opacity:1, y:0, scale:1}} exit={{opacity:0, y:20, scale:0.95}}
            className="fixed bottom-24 right-6 z-50 w-80 sm:w-96 h-[500px] glass rounded-2xl flex flex-col overflow-hidden border border-gold/20 shadow-2xl">
            <div className="flex items-center justify-between px-4 py-3 border-b border-gold/10">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gold animate-pulse" />
                <span className="font-semibold text-sm text-gold">ABE Assistant</span>
              </div>
              <button onClick={() => setOpen(false)} className="text-muted-foreground hover:text-gold"><X className="w-4 h-4" /></button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm ${
                    m.role === 'user' ? 'bg-gradient-gold text-black' : 'glass'
                  }`}>
                    <div className="whitespace-pre-line leading-relaxed">{m.content}</div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="glass rounded-2xl px-4 py-2"><div className="flex gap-1">
                    {[0,1,2].map(i => <motion.div key={i} animate={{y:[0,-3,0]}} transition={{repeat:Infinity, duration:1, delay:i*0.2}} className="w-1.5 h-1.5 rounded-full bg-gold" />)}
                  </div></div>
                </div>
              )}
            </div>

            {messages.length === 1 && (
              <div className="px-4 pb-2 flex flex-wrap gap-1.5">
                {QUICK_ACTIONS.map(q => (
                  <button key={q} onClick={() => handleSend(q)}
                    className="text-xs px-2.5 py-1.5 rounded-full glass text-muted-foreground hover:text-gold transition">{q}</button>
                ))}
              </div>
            )}

            <div className="px-4 py-3 border-t border-gold/10 flex gap-2">
              <input value={input} onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                className="flex-1 px-4 py-2 rounded-xl bg-white/5 border border-gold/20 text-white text-sm focus:outline-none focus:border-gold"
                placeholder="Escribe tu mensaje..." />
              <button onClick={() => handleSend()} disabled={loading || !input.trim()}
                className="px-3 py-2 rounded-xl bg-gradient-gold text-black disabled:opacity-30">
                <Send className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
