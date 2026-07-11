import { Mic, Music, Headphones } from "lucide-react";
import type { Artist } from "@/lib/abe-api";

const ICONS = [Mic, Music, Headphones];

export default function ArtistCard({ artist, index }: { artist: Artist; index: number }) {
  const Icon = ICONS[index % ICONS.length];
  return (
    <a href={`/artist/${artist.id}`}
      className="group glass rounded-2xl p-6 gradient-border hover:border-transparent transition-all duration-300 block">
      <div className="text-3xl mb-4">
        <Icon className="w-8 h-8" style={{ color: ["#00ff88", "#FF6B35", "#00ccff"][index % 3] }} />
      </div>
      <h3 className="text-lg font-semibold mb-1">{artist.name}</h3>
      <div className="flex items-baseline gap-2 mt-3">
        <span className="text-2xl font-bold gradient-text">
          ${(artist.revenue || 0).toLocaleString()}
        </span>
        <span className="text-xs text-gray-500">revenue</span>
      </div>
      <div className="text-sm text-gray-400 mt-1">
        {(artist.streams || 0).toLocaleString()} streams
      </div>
      <div className="mt-4 text-xs text-[#00ff88] opacity-0 group-hover:opacity-100 transition-opacity">
        Ver perfil →
      </div>
    </a>
  );
}
