'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import useSWR from 'swr';
import {
  LayoutDashboard,
  Users,
  Search,
  BarChart3,
  Bell,
  FileText,
  Settings,
  Music2,
  TrendingUp,
  Star,
  Radio,
  Wallet,
  Command,
  Workflow,
  BrainCircuit,
  Crosshair,
  Scale,
} from 'lucide-react';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const navItems = [
  { href: '/dashboard', label: 'Mission Control', icon: LayoutDashboard },
  { href: '/command-center', label: 'Command Center', icon: Command },
  { href: '/workflows', label: 'Workflows', icon: Workflow },
  { href: '/agents', label: 'Agent Performance', icon: BrainCircuit },
  { href: '/artists', label: 'Artist Radar', icon: Users },
  { href: '/discovery', label: 'Discovery Engine', icon: Search },
  { href: '/analytics', label: 'Analytics', icon: BarChart3 },
  { href: '/alerts', label: 'Alerts', icon: Bell, badge: 'notifications' as const },
  { href: '/reports', label: 'Reports', icon: FileText },
  { href: '/contracts', label: 'Contracts', icon: Scale },
  { href: '/signings', label: 'Signing Pipeline', icon: Star },
  { href: '/war-rooms', label: 'War Rooms', icon: Crosshair },
  { href: '/market', label: 'Market Intelligence', icon: TrendingUp },
  { href: '/playlists', label: 'Playlist Monitor', icon: Radio },
  { href: '/finance', label: 'Financial View', icon: Wallet },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { data: notifData } = useSWR('/api/v1/notifications', fetcher, { refreshInterval: 30000 });
  const notificationBadge = notifData?.unread ?? 0;

  return (
    <aside className="w-64 border-r bg-card/95 backdrop-blur-xl flex flex-col">
      {/* Brand Header */}
      <div className="p-5 border-b border-border/50">
        <div className="flex items-center gap-2.5">
          <div className="h-7 w-7 rounded-lg signal-gradient flex items-center justify-center shadow-lg shadow-amber-500/20">
            <span className="text-white text-xs font-black tracking-tight">S</span>
          </div>
          <div>
            <span className="font-bold text-base tracking-tight">SIGNAL</span>
            <p className="text-[10px] text-muted-foreground leading-none mt-0.5">Music Intelligence Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200 ${
                isActive
                  ? 'bg-primary/10 text-primary font-medium shadow-sm'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
              }`}
            >
              <Icon className={`h-4 w-4 ${isActive ? 'text-primary' : ''}`} />
              <span>{item.label}</span>
              {item.badge === 'notifications' && notificationBadge > 0 && (
                <span className="ml-auto bg-destructive text-destructive-foreground text-[10px] font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1">
                  {notificationBadge}
                </span>
              )}
              {/* Active indicator */}
              {isActive && <span className="ml-auto w-1 h-4 rounded-full bg-primary" />}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border/50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500/20 to-rose-600/20 flex items-center justify-center text-xs font-bold text-amber-500 border border-amber-500/10">
            AM
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">Abe Music Group</p>
            <p className="text-[10px] text-muted-foreground truncate">Enterprise · SIGNAL v2</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
