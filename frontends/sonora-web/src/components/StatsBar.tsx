"use client";

import { useEffect, useState } from "react";
import { getRevenue, getArtists } from "@/lib/abe-api";

export default function StatsBar() {
  const [stats, setStats] = useState({ revenue: 479112, streams: 120000000, artists: 3 });

  useEffect(() => {
    Promise.all([getRevenue(), getArtists()]).then(([rev, arts]) => {
      if (rev?.total) setStats(s => ({ ...s, revenue: rev.total }));
      if (arts?.length) setStats(s => ({ ...s, artists: arts.length }));
    });
  }, []);

  return (
    <div className="grid grid-cols-3 gap-6 max-w-lg mx-auto mt-12">
      {[
        { label: "Revenue", value: `$${(stats.revenue / 1000).toFixed(0)}K`, color: "#00ff88" },
        { label: "Streams", value: `${(stats.streams / 1000000).toFixed(0)}M`, color: "#FF6B35" },
        { label: "Artistas", value: String(stats.artists), color: "#00ccff" },
      ].map((s) => (
        <div key={s.label} className="text-center">
          <div className="text-3xl font-bold" style={{ color: s.color }}>{s.value}</div>
          <div className="text-xs text-gray-500 mt-1">{s.label}</div>
        </div>
      ))}
    </div>
  );
}
