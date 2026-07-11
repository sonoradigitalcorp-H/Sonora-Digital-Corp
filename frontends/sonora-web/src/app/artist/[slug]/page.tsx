"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Navbar from "@/components/Navbar";
import { getArtist, getArtistKPI } from "@/lib/abe-api";
import { motion } from "framer-motion";
import {
  ShoppingBag, Music2, Calendar, Video, Image, Send, Star,
  Shirt, Ticket, Globe, Music, Camera,
  Sparkles, Gift, Phone, Mic, Crown, Trophy,
} from "lucide-react";

const FALLBACK = { id: "", name: "", total_streams: 0, total_revenue: 0, telegram_handle: "", genre: "", bio: "" };

const MERCH_ITEMS = [
  { name: "Playera edición limitada", price: "$35", img: "👕", colors: ["Negra", "Dorada", "Blanca"] },
  { name: "Gorra bordada", price: "$25", img: "🧢", colors: ["Negra", "Roja"] },
  { name: "Poster firmado", price: "$15", img: "🖼️", colors: ["Tamaño carta", "Tamaño póster"] },
  { name: "Pulsera exclusiva", price: "$10", img: "📿", colors: ["Oro", "Plata"] },
  { name: "Hoodie edición tur", price: "$60", img: "🧥", colors: ["Negra", "Gris"] },
  { name: "Tote bag", price: "$20", img: "👜", colors: ["Natural", "Negro"] },
];

const FAN_SERVICES = [
  { icon: Video, name: "Video personalizado", desc: "El artista te graba un saludo, felicitación o mensaje especial", price: "$49", popular: true },
  { icon: Image, name: "Foto dedicada", desc: "Foto impresa con dedicatoria real del artista", price: "$29" },
  { icon: Mic, name: "Canción personalizada", desc: "Una canción original basada en tu historia (letra + voz)", price: "$199" },
  { icon: Gift, name: "Saludo de cumpleaños", desc: "Video saludo de cumpleaños personalizado", price: "$39" },
  { icon: Phone, name: "Video llamada", desc: "5 minutos de video llamada con el artista", price: "$149" },
  { icon: Star, name: "Mensaje de voz", desc: "Nota de voz personalizada del artista para ti", price: "$19" },
];

const UPCOMING_EVENTS = [
  { date: "15 Ago", name: "Concierto Hermosillo", venue: "ABE Music Hub", price: "$25", tickets: 120 },
  { date: "22 Sep", name: "Festival Sonora", venue: "Palacio de los Deportes", price: "$45", tickets: 340 },
  { date: "10 Oct", name: "Tour CDMX", venue: "Auditorio Nacional", price: "$65", tickets: 78 },
];

export default function ArtistPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [artist, setArtist] = useState(FALLBACK);
  const [tab, setTab] = useState<"shop" | "videos" | "eventos" | "bio">("shop");
  const [selectedMerch, setSelectedMerch] = useState<number | null>(null);
  const [cartCount, setCartCount] = useState(0);

  useEffect(() => {
    getArtist(slug).then(a => { if (a) setArtist(a as any); });
    getArtistKPI(slug).then(k => { if (k) setArtist(p => ({...p, ...k})); });
  }, [slug]);

  return (
    <div className="min-h-screen gradient-bg">
      <Navbar />

      {/* ARTIST HERO */}
      <section className="relative pt-24 pb-12 px-4 overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-0 right-0 w-96 h-96 bg-gold/10 rounded-full blur-[120px]" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-red-abe/10 rounded-full blur-[100px]" />
        </div>
        <div className="max-w-6xl mx-auto relative">
          <div className="flex flex-col md:flex-row gap-8 items-center">
            <div className="w-48 h-48 md:w-64 md:h-64 rounded-full glass overflow-hidden shrink-0">
              <img src={`/images/artists/${slug}/portrait.webp`} alt={artist.name}
                className="w-full h-full object-cover"
                onError={(e) => { (e.target as HTMLImageElement).src = ''; }} />
            </div>
            <div className="text-center md:text-left">
              <h1 className="font-display text-4xl md:text-6xl font-light mb-2">{artist.name || slug}</h1>
              <p className="text-gold text-sm uppercase tracking-widest mb-4">{artist.genre || "Artista"}</p>
              <div className="flex flex-wrap gap-6 justify-center md:justify-start mb-6">
                <div><span className="text-2xl font-bold text-gradient-gold">${Number(artist.total_revenue || 0).toLocaleString()}</span><span className="text-xs text-muted-foreground ml-2">revenue</span></div>
                <div><span className="text-2xl font-bold text-foreground">{(Number(artist.total_streams || 0) / 1000000).toFixed(1)}M</span><span className="text-xs text-muted-foreground ml-2">streams</span></div>
              </div>
              <div className="flex flex-wrap gap-3 justify-center md:justify-start">
                {[
                  { icon: Music, url: `https://open.spotify.com/artist/${slug}`, label: "Spotify" },
                  { icon: Camera, url: `https://instagram.com/${slug}`, label: "Instagram" },
                  { icon: Globe, url: `https://facebook.com/${slug}`, label: "Facebook" },
                ].map(s => (
                  <a key={s.label} href={s.url} target="_blank"
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-full glass text-xs text-muted-foreground hover:text-gold transition">
                    <s.icon className="w-3 h-3" /> {s.label}
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* TABS */}
      <section className="px-4 mb-8">
        <div className="max-w-6xl mx-auto flex gap-2 overflow-x-auto scrollbar-hide">
          {[
            { id: "shop", label: "🛍️ Tienda", desc: "Merch, fotos, saludos" },
            { id: "videos", label: "🎬 Contenido", desc: "Videos, canciones" },
            { id: "eventos", label: "📅 Eventos", desc: "Conciertos, booking" },
            { id: "bio", label: "📖 Biografía", desc: "Historia, logros" },
          ].map(t => (
            <button key={t.id} onClick={() => setTab(t.id as any)}
              className={`px-5 py-3 rounded-xl text-sm font-medium transition-all whitespace-nowrap ${
                tab === t.id ? "bg-gradient-gold text-black" : "glass text-muted-foreground hover:text-foreground"
              }`}>
              <div className="font-semibold">{t.label}</div>
              <div className="text-[10px] opacity-70">{t.desc}</div>
            </button>
          ))}
          {/* Cart */}
          <div className="ml-auto flex items-center">
            <div className="glass rounded-xl px-4 py-3 text-sm flex items-center gap-2">
              <ShoppingBag className="w-4 h-4 text-gold" />
              <span className="text-gold">{cartCount}</span>
            </div>
          </div>
        </div>
      </section>

      {/* SHOP TAB */}
      {tab === "shop" && (
        <section className="px-4 pb-24">
          <div className="max-w-6xl mx-auto">

            {/* Fan Services */}
            <div className="mb-12">
              <h2 className="font-display text-2xl font-light mb-6 flex items-center gap-2"><Sparkles className="w-5 h-5 text-gold" /> Experiencias exclusivas</h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {FAN_SERVICES.map((svc, i) => (
                  <motion.div key={svc.name} initial={{opacity:0, y:20}} animate={{opacity:1, y:0}} transition={{delay: i*0.05}}
                    className={`glass rounded-xl p-5 ${svc.popular ? 'gradient-border' : ''}`}>
                    <svc.icon className="w-6 h-6 text-gold mb-3" />
                    <h3 className="font-semibold mb-1">{svc.name}</h3>
                    <p className="text-xs text-muted-foreground mb-3">{svc.desc}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-lg font-bold text-gradient-gold">{svc.price}</span>
                      <button className="px-3 py-1.5 rounded-full bg-gradient-gold text-black text-xs font-medium hover:opacity-90">Solicitar</button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Merch Store */}
            <div className="mb-12">
              <h2 className="font-display text-2xl font-light mb-6 flex items-center gap-2"><ShoppingBag className="w-5 h-5 text-gold" /> Tienda oficial</h2>
              <div className="grid md:grid-cols-3 lg:grid-cols-6 gap-3">
                {MERCH_ITEMS.map((item, i) => (
                  <motion.div key={item.name} initial={{opacity:0, y:20}} animate={{opacity:1, y:0}} transition={{delay: i*0.05}}
                    className="glass rounded-xl p-4 text-center hover:scale-[1.02] transition-all cursor-pointer"
                    onClick={() => setSelectedMerch(i)}>
                    <div className="text-3xl mb-2">{item.img}</div>
                    <h3 className="text-xs font-semibold mb-1">{item.name}</h3>
                    <div className="text-gold font-bold text-sm">{item.price}</div>
                    <div className="text-[10px] text-muted-foreground mt-1">{item.colors.length} colores</div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Upcoming Events */}
            <div>
              <h2 className="font-display text-2xl font-light mb-6 flex items-center gap-2"><Calendar className="w-5 h-5 text-gold" /> Próximos eventos</h2>
              <div className="space-y-3">
                {UPCOMING_EVENTS.map((ev, i) => (
                  <div key={i} className="glass rounded-xl p-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="text-center">
                        <div className="text-lg font-bold text-gold">{ev.date.split(" ")[0]}</div>
                        <div className="text-xs text-muted-foreground">{ev.date.split(" ")[1]}</div>
                      </div>
                      <div>
                        <div className="font-semibold">{ev.name}</div>
                        <div className="text-xs text-muted-foreground">{ev.venue}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className="font-bold text-gold">{ev.price}</div>
                        <div className="text-[10px] text-muted-foreground">{ev.tickets} disponibles</div>
                      </div>
                      <button className="px-4 py-2 rounded-full bg-gradient-gold text-black text-xs font-semibold">Comprar</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* VIDEOS / CONTENT TAB */}
      {tab === "videos" && (
        <section className="px-4 pb-24">
          <div className="max-w-6xl mx-auto">
            <h2 className="font-display text-2xl font-light mb-6">Contenido exclusivo</h2>
            <p className="text-muted-foreground mb-8">Todo el contenido es generado con ABE Films + IA.</p>
            <div className="grid md:grid-cols-3 gap-4">
              {[
                { type: "Video saludo", desc: "El artista te dedica un saludo", price: "$49", icon: Video },
                { type: "Canción personalizada", desc: "Basada en tu historia", price: "$199", icon: Mic },
                { type: "Video colaborativo", desc: "Tú y el artista en un video", price: "$299", icon: Star },
              ].map((v, i) => (
                <div key={i} className="glass rounded-xl p-6 gradient-border">
                  <v.icon className="w-8 h-8 text-gold mb-3" />
                  <h3 className="font-semibold mb-1">{v.type}</h3>
                  <p className="text-xs text-muted-foreground mb-3">{v.desc}</p>
                  <div className="text-lg font-bold text-gradient-gold mb-3">{v.price}</div>
                  <button className="w-full py-2 rounded-full bg-gradient-gold text-black text-xs font-semibold">Solicitar</button>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* EVENTS TAB */}
      {tab === "eventos" && (
        <section className="px-4 pb-24">
          <div className="max-w-6xl mx-auto">
            <h2 className="font-display text-2xl font-light mb-6">Eventos y booking</h2>
            <p className="text-muted-foreground mb-8">Contrata al artista para tu evento o compra boletos para sus conciertos.</p>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="glass rounded-2xl p-8">
                <h3 className="font-semibold mb-4">Contratar para evento</h3>
                <p className="text-sm text-muted-foreground mb-4">Llena el formulario y el equipo de ABE Music se pondrá en contacto.</p>
                <div className="space-y-3">
                  <input placeholder="Tu nombre" className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-gold/20 text-sm" />
                  <input placeholder="Tu email" className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-gold/20 text-sm" />
                  <input placeholder="Tipo de evento" className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-gold/20 text-sm" />
                  <button className="w-full py-2.5 rounded-full bg-gradient-gold text-black font-semibold text-sm">Enviar solicitud</button>
                </div>
              </div>
              <div className="glass rounded-2xl p-8">
                <h3 className="font-semibold mb-4">Próximas fechas</h3>
                <div className="space-y-3">
                  {UPCOMING_EVENTS.map((ev, i) => (
                    <div key={i} className="flex items-center justify-between p-3 glass rounded-xl">
                      <div>
                        <div className="text-sm font-semibold">{ev.name}</div>
                        <div className="text-xs text-muted-foreground">{ev.date} · {ev.venue}</div>
                      </div>
                      <button className="px-4 py-1.5 rounded-full bg-gradient-gold text-black text-xs font-semibold">Boletos</button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* BIO TAB */}
      {tab === "bio" && (
        <section className="px-4 pb-24">
          <div className="max-w-4xl mx-auto">
            <div className="glass rounded-2xl p-8 mb-8">
              <h2 className="font-display text-2xl font-light mb-4">Biografía</h2>
              <p className="text-muted-foreground leading-relaxed">
                {artist.name || slug} es un artista del ecosistema ABE Music Group. 
                Con {(Number(artist.total_streams || 0) / 1000000).toFixed(1)}M streams y 
                ${Number(artist.total_revenue || 0).toLocaleString()} en revenue generado, 
                forma parte de la nueva generación de música regional mexicana.
              </p>
            </div>

            <div className="glass rounded-2xl p-8 mb-8">
              <h2 className="font-display text-2xl font-light mb-6 flex items-center gap-2"><Trophy className="w-5 h-5 text-gold" /> Logros</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: "Streams", value: `${(Number(artist.total_streams || 0) / 1000000).toFixed(1)}M` },
                  { label: "Revenue", value: `$${Number(artist.total_revenue || 0).toLocaleString()}` },
                  { label: "Canciones", value: "5+" },
                  { label: "Fans", value: "10K+" },
                ].map(s => (
                  <div key={s.label} className="text-center glass rounded-xl p-4">
                    <div className="text-xl font-bold text-gold">{s.value}</div>
                    <div className="text-xs text-muted-foreground">{s.label}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass rounded-2xl p-8">
              <h2 className="font-display text-2xl font-light mb-4">Redes</h2>
              <div className="flex flex-wrap gap-3">
                <a href={`https://open.spotify.com/artist/${slug}`} target="_blank"
                  className="flex items-center gap-2 px-4 py-2 rounded-full glass text-sm hover:text-gold transition">
                  <Music className="w-4 h-4" /> Spotify
                </a>
                <a href={`https://instagram.com/${slug}`} target="_blank"
                  className="flex items-center gap-2 px-4 py-2 rounded-full glass text-sm hover:text-gold transition">
                  <Camera className="w-4 h-4" /> Instagram
                </a>
                <a href={`https://facebook.com/${slug}`} target="_blank"
                  className="flex items-center gap-2 px-4 py-2 rounded-full glass text-sm hover:text-gold transition">
                  <Globe className="w-4 h-4" /> Facebook
                </a>
                <a href={`https://t.me/${artist.telegram_handle || 'abeassistant_bot'}`} target="_blank"
                  className="flex items-center gap-2 px-4 py-2 rounded-full glass text-sm hover:text-gold transition">
                  <Send className="w-4 h-4" /> Telegram
                </a>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* FOOTER */}
      <footer className="border-t border-gold/10 py-6 px-4 text-center text-xs text-muted-foreground">
        <p>© 2026 ABE Music Group</p>
      </footer>
    </div>
  );
}
