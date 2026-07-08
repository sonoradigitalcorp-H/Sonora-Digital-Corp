'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/dashboard/layout';
import { Settings, Bell, Mail, Smartphone, Users, Globe, RefreshCw, Loader2, AlertCircle, CheckCircle2, XCircle, User, Shield, CreditCard, ChevronRight } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const settingsTabs = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'team', label: 'Team', icon: Users },
  { id: 'integrations', label: 'Integrations', icon: Globe },
  { id: 'billing', label: 'Billing', icon: CreditCard },
];

function colorFromName(name: string): string {
  const colors = ['bg-primary', 'bg-emerald-500', 'bg-purple-500', 'bg-amber-500', 'bg-cyan-500', 'bg-rose-500'];
  let hash = 0;
  for (let i = 0; i < name.length; i++) { hash = name.charCodeAt(i) + ((hash << 5) - hash); }
  return colors[Math.abs(hash) % colors.length];
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile');
  const { data, error, isLoading } = useSWR('/api/v1/settings', fetcher);

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground mt-1">Account configuration and team management</p>
        </div>

        {error && <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500"><AlertCircle className="h-4 w-4" /><span className="text-sm">Failed to load settings</span></div>}
        {isLoading && <div className="flex items-center justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>}

        {data && (
          <div className="flex gap-6">
            {/* Sub-navigation */}
            <nav className="w-48 shrink-0 space-y-1">
              {settingsTabs.map(tab => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-all ${
                      activeTab === tab.id
                        ? 'bg-primary/10 text-primary font-medium'
                        : 'text-muted-foreground hover:text-foreground hover:bg-surface-hover'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>

            {/* Content */}
            <div className="flex-1 space-y-6">
              {/* Profile */}
              {activeTab === 'profile' && (
                <div className="rounded-xl border bg-card p-6">
                  <h2 className="text-lg font-semibold mb-2">Profile</h2>
                  <p className="text-sm text-muted-foreground mb-6">Your account details and preferences</p>
                  <div className="space-y-4 max-w-md">
                    {[
                      { label: 'Label', value: data.profile.labelName },
                      { label: 'Plan', value: data.profile.plan },
                      { label: 'Email', value: data.profile.email },
                      { label: 'Timezone', value: data.profile.timezone },
                      { label: 'Language', value: data.profile.language },
                    ].map((f, i) => (
                      <div key={i} className="flex items-center justify-between py-3 border-b border-border last:border-0">
                        <span className="text-sm text-muted-foreground">{f.label}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{f.value}</span>
                          <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/40" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Notifications */}
              {activeTab === 'notifications' && (
                <div className="rounded-xl border bg-card p-6">
                  <h2 className="text-lg font-semibold mb-2 flex items-center gap-2"><Bell className="h-5 w-5 text-primary" /> Notifications</h2>
                  <p className="text-sm text-muted-foreground mb-6">Configure how you receive alerts</p>
                  <div className="space-y-4 max-w-md">
                    {Object.entries(data.preferences.notifications).map(([key, val]) => (
                      <div key={key} className="flex items-center justify-between py-3 border-b border-border last:border-0">
                        <span className="text-sm capitalize">{key === 'inApp' ? 'In-App' : key}</span>
                        <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                          val ? 'bg-green-500/10 text-green-500 border border-green-500/20' : 'bg-red-500/10 text-red-500 border border-red-500/20'
                        }`}>
                          {val ? 'Enabled' : 'Disabled'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Team */}
              {activeTab === 'team' && (
                <div className="rounded-xl border bg-card p-6">
                  <h2 className="text-lg font-semibold mb-2 flex items-center gap-2"><Users className="h-5 w-5 text-primary" /> Team</h2>
                  <p className="text-sm text-muted-foreground mb-6">Manage your team members</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {data.team.map((m: any, i: number) => (
                      <div key={i} className="rounded-lg border p-4 card-hover">
                        <div className={`w-10 h-10 rounded-full ${colorFromName(m.name)} flex items-center justify-center text-sm font-bold text-white mb-3`}>
                          {m.name.split(' ').map((n: string) => n[0]).join('')}
                        </div>
                        <p className="font-medium text-sm">{m.name}</p>
                        <p className="text-xs text-muted-foreground">{m.role}</p>
                        <p className="text-xs text-muted-foreground mt-1">{m.email}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Integrations */}
              {activeTab === 'integrations' && (
                <div className="rounded-xl border bg-card p-6">
                  <h2 className="text-lg font-semibold mb-2 flex items-center gap-2"><Globe className="h-5 w-5 text-primary" /> Integrations</h2>
                  <p className="text-sm text-muted-foreground mb-6">Connected services and platforms</p>
                  <div className="space-y-3 max-w-lg">
                    {data.integrations.map((int: any, i: number) => (
                      <div key={i} className="flex items-center justify-between p-4 rounded-lg border card-hover">
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-lg ${int.status === 'connected' ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                            {int.status === 'connected' ? (
                              <CheckCircle2 className="h-5 w-5 text-green-500" />
                            ) : (
                              <XCircle className="h-5 w-5 text-red-500" />
                            )}
                          </div>
                          <div>
                            <p className="text-sm font-medium">{int.name}</p>
                            {int.lastSync && <p className="text-xs text-muted-foreground">Last sync: {int.lastSync}</p>}
                          </div>
                        </div>
                        <button className={`text-xs px-3 py-1.5 rounded-full font-medium border transition-all ${
                          int.status === 'connected'
                            ? 'bg-green-500/10 text-green-500 border-green-500/20 hover:bg-green-500/20'
                            : 'bg-muted text-muted-foreground border-border hover:bg-surface-hover'
                        }`}>
                          {int.status === 'connected' ? 'Connected' : 'Disconnected'}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Billing */}
              {activeTab === 'billing' && (
                <div className="rounded-xl border bg-card p-6">
                  <h2 className="text-lg font-semibold mb-2 flex items-center gap-2"><CreditCard className="h-5 w-5 text-primary" /> Billing</h2>
                  <p className="text-sm text-muted-foreground mb-6">Your subscription and usage</p>
                  <div className="max-w-md space-y-4">
                    <div className="rounded-lg bg-primary/5 border border-primary/10 p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium">Current Plan</p>
                          <p className="text-xs text-muted-foreground mt-0.5">Enterprise</p>
                        </div>
                        <span className="text-lg font-bold text-primary">$499/mo</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Artists tracked</span>
                        <span className="font-medium">110 / 500</span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
                        <div className="h-full rounded-full bg-primary" style={{ width: '22%' }} />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Team members</span>
                        <span className="font-medium">4 / 10</span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
                        <div className="h-full rounded-full bg-primary" style={{ width: '40%' }} />
                      </div>
                    </div>
                    <button className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity">
                      Manage Subscription
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
