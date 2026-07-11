"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Navbar from "@/components/Navbar";
import { Film, Video, Mic, Music, Sparkles, Download, Upload, Crown, ArrowRight, Check } from "lucide-react";

const API = "https://abe.sonoradigitalcorp.com/api";

export default function ABEFilmsPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (files.length === 0) return;
    setGenerating(true);
    // Simulate generation - real implementation connects to Mystik API
    setTimeout(() => {
      setResult("tu-video-123.mp4");
      setGenerating(false);
    }, 3000);
  };

  return (
    <div className="min-h-screen gradient-bg">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 pt-24 pb-24">
        <a href="/#productos" className="text-sm text-gray-500 hover:text-white mb-6 inline-block">← Todos los servicios</a>

        <div className="glass rounded-3xl p-8 md:p-12 mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Film className="w-8 h-8 text-[#b388ff]" />
            <span className="text-xs px-3 py-1 rounded-full glass text-[#b388ff]">Pro · Enterprise</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">ABE <span className="gradient-text">Films</span></h1>
          <p className="text-lg text-gray-400 max-w-2xl mb-8">
            Crea videos profesionales con IA. Conciertos virtuales, saludos personalizados, 
            lyric videos, y contenido para redes. Todo desde tu navegador.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="glass rounded-2xl p-6">
            <h3 className="font-semibold mb-4 flex items-center gap-2"><Video className="w-5 h-5 text-[#b388ff]" /> Crear video</h3>
            <div className="border-2 border-dashed border-white/10 rounded-xl p-8 text-center hover:border-[#b388ff] transition-colors mb-4">
              <Upload className="w-10 h-10 mx-auto mb-3 text-gray-500" />
              <p className="text-sm text-gray-400 mb-2">Sube una foto o video corto</p>
              <input type="file" accept="image/*,video/*" className="hidden" id="film-upload" multiple
                onChange={e => setFiles(Array.from(e.target.files || []))} />
              <label htmlFor="film-upload" className="inline-block px-4 py-2 rounded-xl glass text-sm cursor-pointer hover:bg-white/10">
                Seleccionar archivos
              </label>
              {files.length > 0 && <p className="text-xs text-[#b388ff] mt-2">{files.length} archivo(s)</p>}
            </div>

            <div className="grid grid-cols-2 gap-3 mb-4">
              {[{icon: Music, label: "Concierto virtual"}, {icon: Mic, label: "Saludo personalizado"}, {icon: Sparkles, label: "Lyric video"}, {icon: Download, label: "Contenido redes"}].map(t => (
                <button key={t.label} className="glass rounded-xl p-3 text-center text-xs hover:bg-white/5 transition">
                  <t.icon className="w-5 h-5 mx-auto mb-1 text-[#b388ff]" />
                  {t.label}
                </button>
              ))}
            </div>

            <button onClick={handleGenerate} disabled={files.length === 0 || generating}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-[#b388ff] to-[#FF6B35] text-black font-semibold disabled:opacity-30 hover:scale-[1.02] transition-all flex items-center justify-center gap-2">
              {generating ? "Generando..." : "Generar video"}
              <Sparkles className="w-4 h-4" />
            </button>
          </div>

          <div className="glass rounded-2xl p-6">
            <h3 className="font-semibold mb-4 flex items-center gap-2"><Crown className="w-5 h-5 text-[#b388ff]" /> Planes</h3>
            <p className="text-sm text-gray-400 mb-6">ABE Films está disponible en los planes Pro y Enterprise.</p>
            <div className="space-y-3">
              {[
                { plan: "Starter", price: "$0", videos: "❌ No disponible" },
                { plan: "Pro", price: "$49/mes", videos: "✅ 10 videos/mes", popular: true },
                { plan: "Enterprise", price: "$199/mes", videos: "✅ Videos ilimitados" },
              ].map(p => (
                <div key={p.plan} className={`glass rounded-xl p-4 ${p.popular ? 'gradient-border' : ''}`}>
                  <div className="flex justify-between items-center">
                    <div>
                      <span className="font-semibold">{p.plan}</span>
                      <span className="text-xs text-gray-500 ml-2">{p.price}</span>
                    </div>
                    <span className="text-xs">{p.videos}</span>
                  </div>
                </div>
              ))}
              <a href="/signup" className="block text-center py-3 rounded-xl bg-gradient-to-r from-[#b388ff] to-[#FF6B35] text-black font-semibold mt-4">
                Suscribirse ahora
              </a>
            </div>
          </div>
        </div>

        {result && (
          <div className="glass rounded-2xl p-6 text-center">
            <Check className="w-10 h-10 text-[#00ff88] mx-auto mb-3" />
            <p className="font-semibold mb-2">Video generado</p>
            <p className="text-sm text-gray-400 mb-4">{result}</p>
            <button className="px-6 py-2 rounded-xl glass text-sm hover:bg-white/10">Descargar</button>
          </div>
        )}
      </div>
    </div>
  );
}
