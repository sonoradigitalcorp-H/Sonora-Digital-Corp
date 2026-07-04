// ───────────────────────────────────────────────
// /providers — Provider Ecosystem Dashboard
// Shows status, latency, cache, health for all providers
// ───────────────────────────────────────────────

import { ProviderDashboard } from '@/components/providers/provider-dashboard';

export const metadata = {
  title: 'Provider Ecosystem — SIGNAL',
  description: 'Monitor all data providers connected to SIGNAL Music Intelligence Platform',
};

export default function ProvidersPage() {
  return (
    <main className="min-h-screen bg-[#080808]">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">Provider Ecosystem</h1>
          <p className="text-sm text-zinc-400 mt-1">
            Monitor status, latency, cache, and health of all connected data providers
          </p>
        </div>

        {/* Dashboard */}
        <ProviderDashboard />

        {/* Env Configuration Reference */}
        <div className="mt-8 rounded-xl border border-zinc-800 bg-[#111] p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Provider Configuration Reference</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <ConfigBlock
              provider="YouTube"
              icon="▶️"
              vars={['GOOGLE_API_KEY', 'YOUTUBE_API_KEY']}
              status="Requires API key"
            />
            <ConfigBlock
              provider="Instagram"
              icon="📷"
              vars={['META_ACCESS_TOKEN', 'INSTAGRAM_BUSINESS_ID']}
              status="Requires Meta App"
            />
            <ConfigBlock
              provider="TikTok"
              icon="🎬"
              vars={['TIKTOK_ACCESS_TOKEN']}
              status="Research API (application required)"
            />
            <ConfigBlock
              provider="Spotify"
              icon="🎵"
              vars={['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET']}
              status="Requires Premium (Feb 2026)"
            />
          </div>
        </div>

        {/* Docs Link */}
        <div className="mt-6 text-center">
          <a
            href="/docs/PROVIDER_CONFIGURATION.md"
            className="text-sm text-blue-400 hover:text-blue-300 underline"
          >
            View full provider configuration documentation →
          </a>
        </div>
      </div>
    </main>
  );
}

function ConfigBlock({
  provider,
  icon,
  vars,
  status,
}: {
  provider: string;
  icon: string;
  vars: string[];
  status: string;
}) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-[#171717] p-4">
      <div className="flex items-center gap-2 mb-2">
        <span>{icon}</span>
        <span className="font-medium text-white">{provider}</span>
        <span className="text-xs text-zinc-500">— {status}</span>
      </div>
      <div className="space-y-1">
        {vars.map(v => (
          <code key={v} className="block text-xs text-zinc-400 bg-zinc-800 px-2 py-1 rounded">
            {v}
          </code>
        ))}
      </div>
    </div>
  );
}
