'use client';

import { DashboardLayout } from '@/components/dashboard/layout';
import { Settings, Bell, Mail, Smartphone, Users, Globe, RefreshCw, Loader2, AlertCircle, CheckCircle2, XCircle } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

export default function SettingsPage() {
  const { data, error, isLoading } = useSWR('/api/v1/settings', fetcher);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground mt-1">Account configuration and team management</p>
        </div>

        {error && <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500"><AlertCircle className="h-4 w-4" /><span className="text-sm">Failed to load settings</span></div>}
        {isLoading && <div className="flex items-center justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>}

        {data && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Profile */}
              <div className="rounded-xl border bg-card p-5">
                <h2 className="font-semibold mb-4">Profile</h2>
                <div className="space-y-3">
                  {[
                    { label: 'Label', value: data.profile.labelName },
                    { label: 'Plan', value: data.profile.plan },
                    { label: 'Email', value: data.profile.email },
                    { label: 'Timezone', value: data.profile.timezone },
                    { label: 'Language', value: data.profile.language },
                  ].map((f, i) => (
                    <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
                      <span className="text-sm text-muted-foreground">{f.label}</span>
                      <span className="text-sm font-medium">{f.value}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Notification Preferences */}
              <div className="rounded-xl border bg-card p-5">
                <h2 className="font-semibold mb-4 flex items-center gap-2"><Bell className="h-4 w-4 text-primary" />Notifications</h2>
                <div className="space-y-3">
                  {Object.entries(data.preferences.notifications).map(([key, val]) => (
                    <div key={key} className="flex items-center justify-between py-2">
                      <span className="text-sm capitalize">{key === 'inApp' ? 'In-App' : key}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${val ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                        {val ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Team */}
            <div className="rounded-xl border bg-card p-5">
              <h2 className="font-semibold mb-4 flex items-center gap-2"><Users className="h-4 w-4 text-primary" />Team</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {data.team.map((m: any, i: number) => (
                  <div key={i} className="rounded-lg border p-4">
                    <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-sm font-bold mb-2">
                      {m.name.split(' ').map((n: string) => n[0]).join('')}
                    </div>
                    <p className="font-medium text-sm">{m.name}</p>
                    <p className="text-xs text-muted-foreground">{m.role}</p>
                    <p className="text-xs text-muted-foreground mt-1">{m.email}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Integrations */}
            <div className="rounded-xl border bg-card p-5">
              <h2 className="font-semibold mb-4 flex items-center gap-2"><Globe className="h-4 w-4 text-primary" />Integrations</h2>
              <div className="space-y-3">
                {data.integrations.map((int: any, i: number) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg border">
                    <div className="flex items-center gap-3">
                      {int.status === 'connected' ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : <XCircle className="h-4 w-4 text-red-500" />}
                      <div>
                        <p className="text-sm font-medium">{int.name}</p>
                        {int.lastSync && <p className="text-xs text-muted-foreground">Last sync: {int.lastSync}</p>}
                      </div>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${int.status === 'connected' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                      {int.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
