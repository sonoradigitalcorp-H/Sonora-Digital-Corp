import { notFound } from "next/navigation";
import { getArtist, getArtists, getArtistKPI, type ArtistKPI } from "@/lib/abe-api";
import Navbar from "@/components/Navbar";

const FALLBACK_ARTISTS: Record<string, { name: string; streams: number; revenue: number }> = {
  "hector-rubio": { name: "Hector Rubio", streams: 115093009, revenue: 460372 },
  "jesus-urquijo": { name: "Jesus Urquijo", streams: 4635222, revenue: 18540 },
  "javier-arvayo": { name: "Javier Arvayo", streams: 50000, revenue: 200 },
};

async function getArtistData(slug: string) {
  const artist = await getArtist(slug);
  const kpi = await getArtistKPI(slug);
  return { name: artist?.name || FALLBACK_ARTISTS[slug]?.name || slug,
    streams: kpi?.total_streams || FALLBACK_ARTISTS[slug]?.streams || 0,
    revenue: kpi?.total_revenue || FALLBACK_ARTISTS[slug]?.revenue || 0 };
}

export default async function ArtistPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const data = await getArtistData(slug);
  if (!data.name) notFound();

  return (
    <div className="min-h-screen gradient-bg">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 pt-32 pb-24">
        <a href="/#artists" className="text-sm text-gray-500 hover:text-white mb-8 inline-block">← Todos los artistas</a>
        <div className="glass rounded-3xl p-8 md:p-12 mt-4">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">{data.name}</h1>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mt-8">
            <div className="glass rounded-xl p-5 text-center">
              <div className="text-3xl font-bold gradient-text" style={{ backgroundImage: "linear-gradient(135deg, #00ff88, #00ccff)" }}>
                {data.revenue >= 1000 ? `$${(data.revenue / 1000).toFixed(0)}K` : `$${data.revenue}`}
              </div>
              <div className="text-xs text-gray-500 mt-1">Revenue</div>
            </div>
            <div className="glass rounded-xl p-5 text-center">
              <div className="text-3xl font-bold text-[#FF6B35]">
                {(data.streams / 1000000).toFixed(1)}M
              </div>
              <div className="text-xs text-gray-500 mt-1">Streams</div>
            </div>
            <div className="glass rounded-xl p-5 text-center">
              <div className="text-3xl font-bold text-[#00ccff]">
                {data.streams > 0 ? ((data.revenue / data.streams) * 1000).toFixed(4) : "0"}
              </div>
              <div className="text-xs text-gray-500 mt-1">$ por 1K streams</div>
            </div>
          </div>
        </div>
      </div>
      <footer className="glass border-t border-white/5 py-6 px-4 text-center text-xs text-gray-600">
        ABE Music Group · Powered by Sonora Digital Corp
      </footer>
    </div>
  );
}
