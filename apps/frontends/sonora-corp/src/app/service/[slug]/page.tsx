import { notFound } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/Navbar";

const SERVICES: Record<string, {
  name: string; desc: string; long: string; icon: string; color: string;
  features: string[]; cta?: { label: string; url: string }
}> = {
  studio: {
    name: "ABE Studio", icon: "🎙️", color: "#00ff88",
    desc: "Grabación, mezcla y masterización profesional",
    long: "Estudio de grabación profesional con ingenieros de sonido certificados. Mezcla, masterización, producción musical y post-producción.",
    features: ["Grabación analógica y digital", "Mezcla 5.1 y binaural", "Masterización para streaming", "Producción musical", "Post-producción de audio"],
  },
  bot: {
    name: "ABE Bot", icon: "🤖", color: "#26a5e4",
    desc: "Bot de Telegram con 98 skills",
    long: "Bot de Telegram para gestión musical. 98 skills: reportes de revenue, contratos, distribución, CRM de fans, y más.",
    features: ["98 skills disponibles", "Reportes automáticos", "Gestión de contratos", "Revenue en tiempo real", "CRM de fans", "Artista Bot: tu propio bot que vende por ti 24/7"],
    cta: { label: "Abrir bot en Telegram →", url: "https://t.me/abe_music_bot" },
  },
  crm: {
    name: "ABE CRM", icon: "👥", color: "#FF6B35",
    desc: "CRM de fans con segmentación",
    long: "Sistema de gestión de relaciones con fans. Segmentación, campañas, analytics, y automatización de marketing musical.",
    features: ["Segmentación por comportamiento", "Campañas multi-canal", "Analytics de fans", "Automatización de marketing", "Integración con ticketera"],
  },
  token: {
    name: "Token \$RESO", icon: "💰", color: "#f59e0b",
    desc: "Token musical blockchain",
    long: "Token digital para monetización de fans. Recompensas, acceso exclusivo, y transparencia en regalías via blockchain.",
    features: ["Token ERC-20", "Rewards para fans", "Acceso exclusivo", "Regalías transparentes", "Integración con wallet"],
  },
  distribution: {
    name: "Distribución", icon: "📡", color: "#b388ff",
    desc: "Distribución multi-plataforma",
    long: "Distribución de música a todas las plataformas digitales: Spotify, Apple Music, TikTok, YouTube, Deezer, y más.",
    features: ["Distribución global", "100+ plataformas", "Reportes de regalías", "Lanzamientos programados", "ISRC/UPC incluidos"],
  },
};

export default async function ServicePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const svc = SERVICES[slug];
  if (!svc) notFound();

  return (
    <div className="min-h-screen gradient-bg">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 pt-32 pb-24">
        <a href="/#services" className="text-sm text-gray-500 hover:text-white mb-8 inline-block">← Todos los servicios</a>
        <div className="glass rounded-3xl p-8 md:p-12 mt-4">
          <div className="text-5xl mb-6">{svc.icon}</div>
          <h1 className="text-4xl font-bold mb-2" style={{ color: svc.color }}>{svc.name}</h1>
          <p className="text-lg text-gray-400 mb-8">{svc.long}</p>

          <div className="grid md:grid-cols-2 gap-3 mb-8">
            {svc.features.map((f) => (
              <div key={f} className="glass rounded-xl px-4 py-3 text-sm text-gray-300 flex items-center gap-2">
                <span style={{ color: svc.color }}>✓</span> {f}
              </div>
            ))}
          </div>

          {svc.cta && (
            <a href={svc.cta.url} target="_blank"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-[#26a5e4] to-[#00ccff] text-black font-semibold hover:scale-105 transition-transform">
              {svc.cta.label}
            </a>
          )}
        </div>
      </div>
      <footer className="glass border-t border-white/5 py-6 px-4 text-center text-xs text-gray-600">
        ABE Music Group · Powered by Sonora Digital Corp
      </footer>
    </div>
  );
}
