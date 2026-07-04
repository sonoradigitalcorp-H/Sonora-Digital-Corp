'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
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

const navItems = [
  { href: '/dashboard', label: 'Mission Control', icon: LayoutDashboard },
  { href: '/command-center', label: 'Command Center', icon: Command },
  { href: '/workflows', label: 'Workflows', icon: Workflow },
  { href: '/agents', label: 'Agent Performance', icon: BrainCircuit },
  { href: '/dashboard/intelligence', label: 'Intelligence', icon: BrainCircuit },
  { href: '/artists', label: 'Artist Radar', icon: Users },
  { href: '/discovery', label: 'Discovery Engine', icon: Search },
  { href: '/analytics', label: 'Analytics', icon: BarChart3 },
  { href: '/alerts', label: 'Alerts', icon: Bell },
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

  return (
    <aside className="w-56 flex flex-col bg-background">
      {/* Brand Header */}
      <div className="px-4 pt-5 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="h-7 w-7 rounded-lg signal-gradient flex items-center justify-center">
            <span className="text-white text-xs font-black tracking-tight">S</span>
          </div>
          <div>
            <span className="font-semibold text-sm tracking-tight text-foreground">SIGNAL</span>
            <p className="text-[10px] text-muted-foreground leading-none mt-0.5 tracking-wide">
              Music Intelligence
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 space-y-0.5 overflow-y-auto">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`relative flex items-center gap-2.5 px-3 py-1.5 rounded-md text-[13px] transition-all duration-150 ${
                isActive
                  ? 'text-primary font-medium'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {/* Active indicator bar — electric blue, left side */}
              {isActive && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 rounded-full bg-primary" />
              )}

              <Icon className={`h-4 w-4 shrink-0 ${isActive ? 'text-primary' : ''}`} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4">
        <div className="divider-subtle mb-4" />
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md bg-surface flex items-center justify-center text-[10px] font-bold text-muted-foreground">
            AM
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-foreground truncate">Abe Music Group</p>
            <p className="text-[10px] text-muted-foreground truncate">Enterprise</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
