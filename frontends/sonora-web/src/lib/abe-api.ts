const ABE_API = "https://abe.sonoradigitalcorp.com/api";

export interface Artist {
  id: string; name: string; genre?: string;
  total_streams: number; total_revenue: number;
  monthly_listeners?: number; spotify_followers?: number;
  telegram_handle?: string;
}

export async function getArtists(): Promise<Artist[]> {
  try {
    const res = await fetch(`${ABE_API}/abe/artists`);
    if (!res.ok) throw new Error("API error");
    const data = await res.json();
    return data.artists || [];
  } catch {
    return [];
  }
}

export async function getArtist(slug: string): Promise<Artist | null> {
  try {
    const res = await fetch(`${ABE_API}/abe/artists/${slug}`);
    if (!res.ok) return null;
    const data = await res.json();
    return data.artist || null;
  } catch { return null; }
}

export async function getArtistKPI(slug: string) {
  try {
    const res = await fetch(`${ABE_API}/abe/artists/${slug}/kpi`);
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}

export async function getRevenue() {
  try {
    const res = await fetch(`${ABE_API}/abe/revenue`);
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}

export async function getStats() {
  try {
    const res = await fetch(`${ABE_API}/abe/stats`);
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}

export async function getServices() {
  return [
    { id: "studio", name: "ABE Studio", desc: "Grabación, mezcla y masterización profesional", icon: "🎙️", color: "#00ff88" },
    { id: "bot", name: "ABE Bot", desc: "Bot de Telegram con 98 skills para gestión musical", icon: "🤖", color: "#26a5e4" },
    { id: "crm", name: "ABE CRM", desc: "CRM de fans con segmentación y campañas", icon: "👥", color: "#FF6B35" },
    { id: "token", name: "Token \$RESO", desc: "Token musical blockchain para monetización de fans", icon: "💰", color: "#f59e0b" },
    { id: "distribution", name: "Distribución", desc: "Distribución multi-plataforma (Spotify, Apple, TikTok)", icon: "📡", color: "#b388ff" },
  ];
}
