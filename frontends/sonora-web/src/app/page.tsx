"use client";

import { useEffect, useState } from "react";
import { getArtists, getServices, type Artist } from "@/lib/abe-api";
import Navbar from "@/components/Navbar";
import ArtistCard from "@/components/ArtistCard";
import ServiceCard from "@/components/ServiceCard";
import StatsBar from "@/components/StatsBar";

export default function ABELanding() {
  const [artists, setArtists] = useState<Artist[]>([]);
  const [services, setServices] = useState<any[]>([]);

  useEffect(() => {
    getArtists().then(setArtists);
    getServices().then(setServices);
  }, []);

  return (
    <main className="min-h-screen gradient-bg">
      <Navbar />

      <section className="min-h-screen flex flex-col items-center justify-center px-4 text-center relative overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#00ff88] rounded-full blur-[128px]" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#00ccff] rounded-full blur-[128px]" />
        </div>
        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass text-sm text-gray-300 mb-8">
            <span className="w-2 h-2 rounded-full bg-[#00ff88] animate-pulse" />
            Hub físico y digital para músicos
          </div>
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            El ecosistema musical<br />
            <span className="gradient-text" style={{ backgroundImage: "linear-gradient(135deg, #00ff88, #00ccff)" }}>
              inteligente
            </span>
          </h1>
          <p className="text-lg text-gray-400 max-w-xl mx-auto mb-10">
            ABE Music Group — gestión de artistas, revenue, contratos, distribución.
            Token <strong>$RESO</strong> · CRM de fans · Bot Telegram · Studio.
          </p>
          <StatsBar />
        </div>
      </section>

      <section id="artists" className="py-24 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold mb-2 text-center">
            <span className="gradient-text" style={{ backgroundImage: "linear-gradient(135deg, #00ff88, #00ccff)" }}>
              Artistas
            </span>
          </h2>
          <p className="text-gray-400 text-center mb-12 max-w-md mx-auto">
            Artistas gestionados por ABE Music Group
          </p>
          <div className="grid md:grid-cols-3 gap-6">
            {artists.map((artist, i) => (
              <ArtistCard key={artist.id} artist={artist} index={i} />
            ))}
          </div>
        </div>
      </section>

      <section id="services" className="py-24 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold mb-2 text-center">
            <span className="gradient-text" style={{ backgroundImage: "linear-gradient(135deg, #00ff88, #00ccff)" }}>
              Servicios
            </span>
          </h2>
          <p className="text-gray-400 text-center mb-12 max-w-md mx-auto">
            Todo lo que ABE Music ofrece a sus artistas
          </p>
          <div className="grid md:grid-cols-3 lg:grid-cols-5 gap-4">
            {services.map((svc, i) => (
              <ServiceCard key={svc.id} service={svc} index={i} />
            ))}
          </div>
        </div>
      </section>

      <footer className="glass border-t border-white/5 py-8 px-4 text-center">
        <p className="text-sm text-gray-500">
          ABE Music Group · Hecho con ♥ en Hermosillo, Sonora
        </p>
        <p className="text-xs text-gray-600 mt-1">
          Powered by <a href="https://abe.sonoradigitalcorp.com" className="text-gray-500 hover:text-white">Sonora Digital Corp</a>
        </p>
      </footer>
    </main>
  );
}
