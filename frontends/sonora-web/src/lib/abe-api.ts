const ABE_API = "https://abe.sonoradigitalcorp.com/api";

export interface Artist {
  id: string;
  name: string;
  image?: string;
  genre?: string;
  streams?: number;
  revenue?: number;
  monthly_listeners?: number;
  social?: { platform: string; url: string }[];
}

export interface Release {
  id: string;
  title: string;
  type: "single" | "album" | "ep";
  release_date: string;
  cover?: string;
}

export interface ArtistKPI {
  artist_id: string;
  total_streams: number;
  total_revenue: number;
  monthly_listeners: number;
  followers: number;
  growth: number;
}

export interface Revenue {
  total: number;
  by_artist: { artist_id: string; name: string; revenue: number }[];
  by_platform: { platform: string; revenue: number }[];
}

async function fetchAPI<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(`${ABE_API}${path}`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function getArtists(): Promise<Artist[]> {
  const data = await fetchAPI<{ artists?: Artist[] }>("/artists");
  return data?.artists || [
    { id: "hector-rubio", name: "Hector Rubio", streams: 115093009, revenue: 460372 },
    { id: "jesus-urquijo", name: "Jesus Urquijo", streams: 4635222, revenue: 18540 },
    { id: "javier-arvayo", name: "Javier Arvayo", streams: 50000, revenue: 200 },
  ];
}

export async function getArtist(slug: string): Promise<Artist | null> {
  const data = await fetchAPI<{ artist?: Artist }>(`/artists/${slug}`);
  return data?.artist || null;
}

export async function getArtistKPI(slug: string): Promise<ArtistKPI | null> {
  return await fetchAPI<ArtistKPI>(`/artists/${slug}/kpi`);
}

export async function getRevenue(): Promise<Revenue | null> {
  return await fetchAPI<Revenue>("/revenue");
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
