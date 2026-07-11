"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Navbar from "@/components/Navbar";
import { Camera, Download, Image, Video, MessageCircle, Bot, Upload, Sparkles } from "lucide-react";

const API = "https://abe.sonoradigitalcorp.com/api";

const ARTISTS: Record<string, { name: string; streams: number; revenue: number; telegram?: string }> = {
  "hector-rubio": { name: "Hector Rubio", streams: 115093009, revenue: 460372, telegram: "hectorrubiomx" },
  "jesus-urquijo": { name: "Jesus Urquijo", streams: 4635222, revenue: 18540 },
  "javier-arvayo": { name: "Javier Arvayo", streams: 50000, revenue: 200 },
};

export default function ArtistPage() {
  const params = useParams();
  const slug = params.slug as string;
  const artist = ARTISTS[slug];
  const [tab, setTab] = useState<"content" | "vender" | "bot">("content");
  const [files, setFiles] = useState<File[]>([]);
  const [training, setTraining] = useState(false);
  const [gallery, setGallery] = useState<string[]>([]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      fetch(`${API}/content/gallery`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.json()).then(d => setGallery(d.images?.map((i: any) => i.url) || [])).catch(() => {});
    }
  }, []);

  if (!artist) return <div className="min-h-screen gradient-bg flex items-center justify-center"><p className="text-gray-400">Artista no encontrado</p></div>;

  const handleTrain = async () => {
    if (files.length < 3) return;
    setTraining(true);
    const form = new FormData();
    files.forEach(f => form.append("files", f));
    form.append("name", `${slug}-style`);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API}/content/train-lora`, {
        method: "POST", headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: form,
      });
      const data = await res.json();
      alert(data.note || "Entrenamiento iniciado");
    } catch {}
    setTraining(false);
  };

  return (
    <div className="min-h-screen gradient-bg">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 pt-24 pb-24">
        <a href="/#artists" className="text-sm text-gray-500 hover:text-white mb-6 inline-block">← Todos los artistas</a>

        {/* Artist Header */}
        <div className="glass rounded-3xl p-8 md:p-12 mb-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">{artist.name}</h1>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="glass rounded-xl p-5 text-center">
              <div className="text-3xl font-bold gradient-text">${(artist.revenue / 1000).toFixed(0)}K</div>
              <div className="text-xs text-gray-500 mt-1">Revenue</div>
            </div>
            <div className="glass rounded-xl p-5 text-center">
              <div className="text-3xl font-bold text-[#FF6B35]">{(artist.streams / 1000000).toFixed(1)}M</div>
              <div className="text-xs text-gray-500 mt-1">Streams</div>
            </div>
            <div className="glass rounded-xl p-5 text-center">
              <div className="text-3xl font-bold text-[#00ccff]">{((artist.revenue / artist.streams) * 1000).toFixed(4)}</div>
              <div className="text-xs text-gray-500 mt-1">$ por 1K streams</div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-8">
          {[
            { id: "content", label: "🎨 Contenido AI", icon: Image },
            { id: "vender", label: "💰 Vender", icon: Download },
            { id: "bot", label: "🤖 Bot Telegram", icon: MessageCircle },
          ].map(t => (
            <button key={t.id} onClick={() => setTab(t.id as any)}
              className={`px-5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                tab === t.id ? "bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black" : "glass text-gray-400"
              }`}>
              {t.label}
            </button>
          ))}
        </div>

        {/* Content Tab */}
        {tab === "content" && (
          <div className="space-y-6">
            <div className="glass rounded-2xl p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Camera className="w-5 h-5 text-[#FF6B35]" /> Entrenar modelo AI</h2>
              <p className="text-sm text-gray-400 mb-4">Sube 3-5 fotos tuyas para entrenar un modelo AI. Luego podrás generar imágenes y videos con tu rostro.</p>
              <div className="border-2 border-dashed border-white/10 rounded-xl p-8 text-center hover:border-[#FF6B35] transition-colors">
                <Upload className="w-8 h-8 mx-auto mb-3 text-gray-500" />
                <p className="text-sm text-gray-400 mb-2">Arrastra tus fotos aquí o haz clic para seleccionar</p>
                <input type="file" multiple accept="image/*" className="hidden" id="photo-upload"
                  onChange={e => setFiles(Array.from(e.target.files || []))} />
                <label htmlFor="photo-upload" className="inline-block px-4 py-2 rounded-xl glass text-sm cursor-pointer hover:bg-white/10">
                  Seleccionar fotos
                </label>
                {files.length > 0 && <p className="text-xs text-[#00ff88] mt-2">{files.length} fotos seleccionadas</p>}
              </div>
              <button onClick={handleTrain} disabled={files.length < 3 || training}
                className="mt-4 px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black font-medium disabled:opacity-30">
                {training ? "Entrenando..." : "Entrenar modelo →"}
              </button>
            </div>

            <div className="glass rounded-2xl p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Sparkles className="w-5 h-5 text-[#FF6B35]" /> Generar contenido</h2>
              <div className="grid md:grid-cols-3 gap-4">
                <button className="glass rounded-xl p-5 text-center hover:bg-white/5 transition">
                  <Image className="w-8 h-8 mx-auto mb-2 text-[#b388ff]" />
                  <div className="text-sm font-medium">Imágenes</div>
                  <div className="text-xs text-gray-500">Con tu estilo AI</div>
                </button>
                <button className="glass rounded-xl p-5 text-center hover:bg-white/5 transition">
                  <Video className="w-8 h-8 mx-auto mb-2 text-[#00ccff]" />
                  <div className="text-sm font-medium">Videos</div>
                  <div className="text-xs text-gray-500">Talking heads</div>
                </button>
                <button className="glass rounded-xl p-5 text-center hover:bg-white/5 transition">
                  <Download className="w-8 h-8 mx-auto mb-2 text-[#00ff88]" />
                  <div className="text-sm font-medium">Descargar</div>
                  <div className="text-xs text-gray-500">Tu contenido generado</div>
                </button>
              </div>
            </div>

            {gallery.length > 0 && (
              <div className="glass rounded-2xl p-6">
                <h2 className="text-lg font-semibold mb-4">Tu galería</h2>
                <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                  {gallery.map((url, i) => (
                    <div key={i} className="aspect-square glass rounded-xl flex items-center justify-center text-xs text-gray-500">
                      {url.split("/").pop()}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Sell Tab */}
        {tab === "vender" && (
          <div className="glass rounded-2xl p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Download className="w-5 h-5 text-[#00ff88]" /> Vender</h2>
            <p className="text-sm text-gray-400 mb-6">Tu música y contenido pueden generar revenue. ABE Music Group gestiona la distribución y cobranza.</p>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="glass rounded-xl p-5">
                <div className="text-lg font-bold">{artist.streams.toLocaleString()}</div>
                <div className="text-xs text-gray-500">Streams totales</div>
              </div>
              <div className="glass rounded-xl p-5">
                <div className="text-lg font-bold">${artist.revenue.toLocaleString()}</div>
                <div className="text-xs text-gray-500">Revenue generado</div>
              </div>
            </div>
            <button className="mt-6 px-6 py-2.5 rounded-xl glass text-sm hover:bg-white/10 transition">Ver reporte completo</button>
          </div>
        )}

        {/* Bot Tab */}
        {tab === "bot" && (
          <div className="space-y-4">
            <div className="glass rounded-2xl p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Bot className="w-5 h-5 text-[#26a5e4]" /> Bot de Telegram</h2>
              <p className="text-sm text-gray-400 mb-6">Un bot que actúa como {artist.name}. Responde fans, comparte novedades, vende merch y entradas.</p>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="glass rounded-xl p-5">
                  <Bot className="w-6 h-6 text-[#26a5e4] mb-2" />
                  <div className="text-sm font-medium">Bot del artista</div>
                  <div className="text-xs text-gray-400 mt-1">Automatiza respuestas y ventas</div>
                </div>
                <div className="glass rounded-xl p-5">
                  <MessageCircle className="w-6 h-6 text-[#26a5e4] mb-2" />
                  <div className="text-sm font-medium">Grupo de fans</div>
                  <div className="text-xs text-gray-400 mt-1">Comunidad en Telegram</div>
                </div>
              </div>
              {artist.telegram && (
                <a href={`https://t.me/${artist.telegram}`} target="_blank"
                  className="mt-4 flex items-center gap-2 text-sm text-[#26a5e4] hover:underline">
                  <MessageCircle className="w-4 h-4" /> @{artist.telegram} en Telegram
                </a>
              )}
            </div>
          </div>
        )}
      </div>
      <footer className="glass border-t border-white/5 py-6 px-4 text-center text-xs text-gray-600">
        ABE Music Group · Powered by Sonora Digital Corp
      </footer>
    </div>
  );
}
