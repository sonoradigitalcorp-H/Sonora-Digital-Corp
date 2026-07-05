'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useMemo } from 'react';
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
  ChevronDown,
  ChevronRight,
  PanelLeftClose,
  PanelLeft,
  Sparkles,
  Eye,
  Target,
  Activity,
} from 'lucide-react';

// ── Navigation sections with hierarchy ──
interface NavSection {
  label: string;
  items: { href: string; label: string; icon: React.ElementType; badge?: string }[];
}

const navSections: NavSection[] = [
  {
    label: 'Monitor',
    items: [
      { href: '/dashboard', label: 'Mission Control', icon: LayoutDashboard },
      { href: '/command-center', label: 'Command Center', icon: Command },
      { href: '/dashboard/intelligence', label: 'Intelligence', icon: BrainCircuit },
      { href: '/alerts', label: 'Alerts', icon: Bell, badge: 'Live' },
    ],
  },
  {
    label: 'Discover',
    items: [
      { href: '/artists', label: 'Artist Radar', icon: Users },
      { href: '/discovery', label: 'Discovery Engine', icon: Search },
      { href: '/market', label: 'Market Intelligence', icon: TrendingUp },
    ],
  },
  {
    label: 'Analyze',
    items: [
      { href: '/analytics', label: 'Analytics', icon: BarChart3 },
      { href: '/reports', label: 'Reports', icon: FileText },
      { href: '/playlists', label: 'Playlist Monitor', icon: Radio },
    ],
  },
  {
    label: 'Operate',
    items: [
      { href: '/workflows', label: 'Workflows', icon: Workflow },
      { href: '/agents', label: 'Agent Performance', icon: BrainCircuit },
      { href: '/war-rooms', label: 'War Rooms', icon: Crosshair },
      { href: '/contracts', label: 'Contracts', icon: Scale },
      { href: '/signings', label: 'Signing Pipeline', icon: Star },
    ],
  },
  {
    label: 'Finance',
    items: [
      { href: '/finance', label: 'Financial View', icon: Wallet },
    ],
  },
  {
    label: 'Admin',
    items: [
      { href: '/settings', label: 'Settings', icon: Settings },
    ],
  },
];

// Flatten for search
const allNavItems = navSections.flatMap(s => s.items);

function isActivePath(pathname: string, href: string): boolean {
  if (href === '/dashboard') return pathname === '/dashboard';
  if (href === '/dashboard/intelligence') return pathname.startsWith('/dashboard/intelligence');
  return pathname === href || pathname.startsWith(href + '/');
}

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [navSearch, setNavSearch] = useState('');

  const filteredItems = useMemo(() => {
    if (!navSearch.trim()) return null; // null = show sections
    const q = navSearch.toLowerCase().trim();
    return allNavItems.filter(
      i => i.label.toLowerCase().includes(q) || i.href.toLowerCase().includes(q)
    );
  }, [navSearch]);

  return (
    <aside className={`flex flex-col bg-background border-r border-border transition-all duration-200 ${collapsed ? 'w-14' : 'w-60'} flex-shrink-0`}>
      {/* ── Brand Header ── */}
      <div className={`px-4 pt-5 pb-4 ${collapsed ? 'flex justify-center px-0' : ''}`}>
        {collapsed ? (
          <div className="h-7 w-7 rounded-lg signal-gradient flex items-center justify-center mx-auto">
            <span className="text-white text-xs font-black tracking-tight">S</span>
          </div>
        ) : (
          <div className="flex items-center gap-2.5">
            <div className="h-7 w-7 rounded-lg signal-gradient flex items-center justify-center shrink-0">
              <span className="text-white text-xs font-black tracking-tight">S</span>
            </div>
            <div>
              <span className="font-semibold text-sm tracking-tight text-foreground">SIGNAL</span>
              <p className="text-[10px] text-muted-foreground leading-none mt-0.5 tracking-wide">
                Music Intelligence
              </p>
            </div>
          </div>
        )}
      </div>

      {/* ── Collapse toggle (desktop) ── */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="hidden lg:flex items-center justify-center h-8 mx-2 mb-1 rounded-md text-muted-foreground hover:text-foreground hover:bg-surface-hover transition-colors"
        title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <PanelLeft className="h-3.5 w-3.5" /> : <PanelLeftClose className="h-3.5 w-3.5" />}
      </button>

      {/* ── Nav Search ── */}
      {!collapsed && (
        <div className="px-3 mb-2">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground" />
            <input
              type="text"
              placeholder="Find page..."
              value={navSearch}
              onChange={e => setNavSearch(e.target.value)}
              className="w-full bg-muted/50 rounded-md pl-7 pr-2 py-1.5 text-[11px] text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:ring-1 focus:ring-primary/30 transition-all"
            />
            {navSearch && (
              <button
                onClick={() => setNavSearch('')}
                className="absolute right-1.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <span className="text-[10px]">✕</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* ── Navigation ── */}
      <nav className="flex-1 overflow-y-auto scrollbar-thin px-2 pb-2">
        {filteredItems !== null ? (
          /* Search results — flat list */
          <div className="space-y-0.5">
            <div className="px-2 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/40">
              Results
            </div>
            {filteredItems.map(item => {
              const Icon = item.icon;
              const active = isActivePath(pathname, item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setNavSearch('')}
                  className={`relative flex items-center gap-2.5 px-3 py-1.5 rounded-md text-[13px] transition-all duration-150 group ${
                    active
                      ? 'text-primary font-medium bg-primary/5'
                      : 'text-muted-foreground hover:text-foreground hover:bg-surface-hover'
                  }`}
                >
                  {active && (
                    <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 rounded-full bg-gradient-to-b from-primary to-primary/60 shadow-[0_0_6px_rgba(59,130,246,0.4)]" />
                  )}
                  <Icon className={`h-4 w-4 shrink-0 ${active ? 'text-primary' : ''}`} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
        ) : (
          /* Sectioned navigation */
          navSections.map(section => (
            <div key={section.label} className="mb-3">
              {!collapsed && (
                <div className="px-2 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/40">
                  {section.label}
                </div>
              )}
              <div className="space-y-0.5">
                {section.items.map(item => {
                  const Icon = item.icon;
                  const active = isActivePath(pathname, item.href);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`relative flex items-center gap-2.5 px-3 py-1.5 rounded-md text-[13px] transition-all duration-150 group ${
                        collapsed ? 'justify-center px-0 py-2' : ''
                      } ${
                        active
                          ? 'text-primary font-medium bg-primary/5'
                          : 'text-muted-foreground hover:text-foreground hover:bg-surface-hover'
                      }`}
                      title={collapsed ? item.label : undefined}
                    >
                      {/* Active indicator — gradient left bar with glow */}
                      {active && !collapsed && (
                        <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 rounded-full bg-gradient-to-b from-primary to-primary/60 shadow-[0_0_6px_rgba(59,130,246,0.4)]" />
                      )}
                      {active && collapsed && (
                        <span className="absolute left-0 top-0 bottom-0 w-0.5 rounded-full bg-gradient-to-b from-primary to-primary/60" />
                      )}

                      <Icon className={`h-4 w-4 shrink-0 ${active ? 'text-primary' : ''}`} />

                      {!collapsed && (
                        <>
                          <span className="flex-1">{item.label}</span>
                          {item.badge && (
                            <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 font-medium uppercase tracking-wider">
                               {item.badge}
                             </span>
                           )}
                        </>
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))
        )}
      </nav>

      {/* ── Footer — User / Org ── */}
      {!collapsed && (
        <div className="px-4 py-3 border-t border-border">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-md bg-gradient-to-br from-primary/80 to-primary/40 flex items-center justify-center text-[10px] font-bold text-white shrink-0">
              AM
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-foreground truncate">Abe Music Group</p>
              <p className="text-[10px] text-muted-foreground truncate">Enterprise Plan</p>
            </div>
            <div className="flex items-center gap-0.5">
              <span className="status-dot status-dot-green" />
            </div>
          </div>
        </div>
      )}

      {collapsed && (
        <div className="px-2 py-3 border-t border-border flex justify-center">
          <div className="w-7 h-7 rounded-md bg-gradient-to-br from-primary/80 to-primary/40 flex items-center justify-center text-[10px] font-bold text-white">
            AM
          </div>
        </div>
      )}
    </aside>
  );
}
