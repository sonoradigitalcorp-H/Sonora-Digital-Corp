'use client';

import { useState, useEffect, useCallback } from 'react';
import { DashboardLayout } from '@/components/dashboard/layout';
import {
  AlertTriangle, Info, CheckCircle, XCircle, RefreshCw,
  Loader2, Bell, MailOpen, Activity,
} from 'lucide-react';

interface Notification {
  id: string;
  type: 'critical' | 'warning' | 'info' | 'success';
  title: string;
  description: string;
  time: string;
  read: boolean;
  agent: string;
}

interface NotificationsResponse {
  notifications: Notification[];
  unread: number;
  total: number;
}

const TYPE_ORDER: Record<string, number> = { critical: 0, warning: 1, info: 2, success: 3 };

const TYPE_STYLES: Record<string, { border: string; bg: string; icon: typeof AlertTriangle; badge: string }> = {
  critical: { border: 'border-red-500/30', bg: 'bg-red-500/5', icon: XCircle, badge: 'bg-red-500/10 text-red-500' },
  warning: { border: 'border-amber-500/30', bg: 'bg-amber-500/5', icon: AlertTriangle, badge: 'bg-amber-500/10 text-amber-500' },
  info: { border: 'border-blue-500/30', bg: 'bg-blue-500/5', icon: Info, badge: 'bg-blue-500/10 text-blue-500' },
  success: { border: 'border-green-500/30', bg: 'bg-green-500/5', icon: CheckCircle, badge: 'bg-green-500/10 text-green-500' },
};

const AGENTS = ['Cortex', 'Thalamus', 'Analyst', 'Writer', 'Legal'];

export default function AlertsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unread, setUnread] = useState(0);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/v1/notifications');
      if (!res.ok) throw new Error('Failed to fetch notifications');
      const json: NotificationsResponse = await res.json();
      setNotifications(json.notifications);
      setUnread(json.unread);
      setTotal(json.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const res = await fetch('/api/v1/notifications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'refresh' }),
      });
      if (!res.ok) throw new Error('Failed to refresh notifications');
      const json: NotificationsResponse = await res.json();
      setNotifications(json.notifications);
      setUnread(json.unread);
      setTotal(json.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh');
    } finally {
      setRefreshing(false);
    }
  };

  const handleMarkRead = async (id: string) => {
    try {
      const res = await fetch('/api/v1/notifications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'mark_read', id }),
      });
      if (!res.ok) throw new Error('Failed to mark as read');
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
      setUnread((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      const res = await fetch('/api/v1/notifications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'mark_all_read' }),
      });
      if (!res.ok) throw new Error('Failed to mark all as read');
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
      setUnread(0);
    } catch (err) {
      console.error(err);
    }
  };

  const sorted = [...notifications].sort((a, b) => {
    const typeDiff = TYPE_ORDER[a.type] - TYPE_ORDER[b.type];
    if (typeDiff !== 0) return typeDiff;
    return Number(a.read) - Number(b.read);
  });

  return (
    <DashboardLayout>
      <div className="p-6 flex gap-6">
        <div className="flex-1 space-y-6 min-w-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div>
                <h1 className="text-3xl font-bold tracking-tight">Alerts</h1>
                <p className="text-muted-foreground mt-1">Intelligence alerts requiring attention</p>
              </div>
              {!loading && unread > 0 && (
                <span className="px-2.5 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">
                  {unread} unread
                </span>
              )}
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="flex items-center gap-2 px-4 py-2 rounded-lg border bg-card text-sm hover:bg-accent transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              <button
                onClick={handleMarkAllRead}
                disabled={unread === 0}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                <MailOpen className="h-4 w-4" />
                Mark All Read
              </button>
            </div>
          </div>

          {loading && (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-6 text-center">
              <XCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
              <p className="text-red-500 font-medium">{error}</p>
              <button onClick={fetchNotifications} className="mt-2 text-sm text-muted-foreground hover:text-foreground underline">
                Try again
              </button>
            </div>
          )}

          {!loading && !error && sorted.length === 0 && (
            <div className="rounded-xl border bg-card p-12 text-center text-muted-foreground">
              <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="font-medium">No alerts</p>
              <p className="text-sm mt-1">All caught up — nothing requires attention</p>
            </div>
          )}

          {!loading && !error && sorted.length > 0 && (
            <div className="space-y-2">
              {sorted.map((alert) => {
                const styles = TYPE_STYLES[alert.type];
                const Icon = styles.icon;
                return (
                  <div
                    key={alert.id}
                    onClick={() => !alert.read && handleMarkRead(alert.id)}
                    className={`rounded-xl border p-4 ${styles.border} ${styles.bg} ${
                      alert.read ? 'opacity-60' : 'cursor-pointer hover:shadow-md transition-all'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <div className={`p-2 rounded-lg ${styles.badge}`}>
                        <Icon className="h-5 w-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4">
                          <div className="min-w-0">
                            <h3 className="font-medium truncate">{alert.title}</h3>
                            <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{alert.description}</p>
                          </div>
                          <div className="flex items-center gap-2 shrink-0">
                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${styles.badge}`}>{alert.agent}</span>
                            <span className="text-xs text-muted-foreground whitespace-nowrap">{alert.time}</span>
                          </div>
                        </div>
                        {alert.read && <p className="text-xs text-muted-foreground/60 mt-2">Read</p>}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="w-64 shrink-0 hidden lg:block">
          <div className="rounded-xl border bg-card p-4 sticky top-6">
            <h3 className="font-semibold text-sm mb-4 flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Agent Activity
            </h3>
            <div className="space-y-3">
              {AGENTS.map((agent) => {
                const active = notifications.some((n) => n.agent === agent);
                const alertCount = notifications.filter((n) => n.agent === agent).length;
                return (
                  <div key={agent} className="flex items-center gap-3">
                    <div className="relative">
                      <span className={`block w-2 h-2 rounded-full ${active ? 'bg-green-500' : 'bg-muted-foreground/30'}`} />
                      {active && <span className="absolute inset-0 w-2 h-2 rounded-full bg-green-500 animate-ping opacity-30" />}
                    </div>
                    <span className="text-sm">{agent}</span>
                    {alertCount > 0 && (
                      <span className="ml-auto text-xs text-muted-foreground">{alertCount} alert{alertCount > 1 ? 's' : ''}</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
