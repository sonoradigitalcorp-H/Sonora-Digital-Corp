'use client';

import { DashboardLayout } from '@/components/dashboard/layout';
import { Radio, TrendingUp, TrendingDown, Users, ListMusic, Loader2, AlertCircle } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

export default function PlaylistsPage() {
  const { data, error, isLoading } = useSWR('/api/v1/playlists', fetcher);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Playlist Monitor</h1>
          <p className="text-muted-foreground mt-1">Editorial and algorithmic playlist performance tracking</p>
        </div>

        {error && <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500"><AlertCircle className="h-4 w-4" /><span className="text-sm">Failed to load playlist data</span></div>}
        {isLoading && <div className="flex items-center justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>}

        {data && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[
                { label: 'Tracked Playlists', value: data.stats.totalPlaylists, icon: ListMusic },
                { label: 'Total Followers', value: data.stats.totalFollowers, icon: Users },
                { label: 'Tracks Added', value: data.stats.tracksAdded, icon: Radio },
                { label: 'Weekly Growth', value: data.stats.weeklyGrowth, icon: TrendingUp },
              ].map((s, i) => {
                const Icon = s.icon;
                return (
                  <div key={i} className="rounded-xl border bg-card p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-muted-foreground">{s.label}</span>
                      <Icon className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <p className="text-xl font-bold">{s.value}</p>
                  </div>
                );
              })}
            </div>

            <div className="rounded-xl border bg-card overflow-hidden">
              <div className="p-4 border-b"><h2 className="font-semibold flex items-center gap-2"><Radio className="h-4 w-4 text-primary" />Curated Playlists</h2></div>
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    {['Playlist', 'Platform', 'Followers', 'Tracks', 'Added Artists', 'Reach'].map(h => (
                      <th key={h} className="text-left text-xs font-medium text-muted-foreground p-4">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {data.playlists.map((p: any, i: number) => (
                    <tr key={i} className="hover:bg-accent/50 transition-colors cursor-pointer">
                      <td className="p-4"><span className="text-sm font-medium">{p.name}</span></td>
                      <td className="p-4"><span className="text-xs text-muted-foreground">{p.platform}</span></td>
                      <td className="p-4 text-sm">{p.followers}</td>
                      <td className="p-4 text-sm text-muted-foreground">{p.tracks}</td>
                      <td className="p-4">
                        <div className="flex gap-1 flex-wrap">
                          {p.addedArtists.map((a: string, j: number) => (
                            <span key={j} className="text-xs px-1.5 py-0.5 rounded bg-primary/10 text-primary">{a}</span>
                          ))}
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-1">
                          {p.trend === 'up' ? <TrendingUp className="h-3 w-3 text-green-500" /> : <TrendingDown className="h-3 w-3 text-red-500" />}
                          <span className={`text-xs font-medium ${p.trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>{p.reach}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
