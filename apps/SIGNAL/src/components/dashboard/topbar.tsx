'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Search, Bell, CheckCircle2, Loader2, ArrowRight, FileText, Music2, Activity, Crosshair, X, ChevronRight, Home, Sparkles, LogOut, User, Keyboard, ChevronDown } from 'lucide-react';
import { usePathname, useRouter } from 'next/navigation';
import useSWR, { mutate } from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const typeIcons: Record<string, React.ElementType> = {
  artist: Music2, page: Activity, warroom: Crosshair, workflow: FileText,
};

const typeColors: Record<string, string> = {
  artist: 'text-primary bg-primary/10',
  page: 'text-blue-400 bg-blue-400/10',
  warroom: 'text-rose-400 bg-rose-400/10',
  workflow: 'text-amber-400 bg-amber-400/10',
};

const typeLabels: Record<string, string> = {
  page: 'Modules', workflow: 'Workflows', warroom: 'War Rooms', artist: 'Artists',
};

// ── Breadcrumb helper ──
const pageLabels: Record<string, string> = {
  'dashboard': 'Mission Control',
  'command-center': 'Command Center',
  'intelligence': 'Intelligence',
  'artists': 'Artist Radar',
  'discovery': 'Discovery Engine',
  'analytics': 'Analytics',
  'alerts': 'Alerts',
  'reports': 'Reports',
  'contracts': 'Contracts',
  'signings': 'Signing Pipeline',
  'war-rooms': 'War Rooms',
  'market': 'Market Intelligence',
  'playlists': 'Playlist Monitor',
  'finance': 'Financial View',
  'settings': 'Settings',
  'agents': 'Agent Performance',
  'workflows': 'Workflows',
};

function Breadcrumbs({ pathname }: { pathname: string }) {
  const segments = pathname.split('/').filter(Boolean);

  if (segments.length === 0) return null;

  return (
    <nav className="hidden md:flex items-center gap-1 text-[11px] text-muted-foreground">
      <Home className="h-3 w-3" />
      {segments.map((seg, i) => {
        const label = pageLabels[seg] || seg.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        const isLast = i === segments.length - 1;
        return (
          <span key={seg} className="flex items-center gap-1">
            <ChevronRight className="h-3 w-3 text-muted-foreground/40" />
            <span className={isLast ? 'text-foreground font-medium' : 'hover:text-foreground transition-colors'}>
              {label}
            </span>
          </span>
        );
      })}
    </nav>
  );
}

// ── Cmd+K palette component ──
function CommandPalette({ onClose }: { onClose: () => void }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    if (query.length < 2) { setResults([]); return; }
    setLoading(true);
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/v1/search?q=${encodeURIComponent(query)}`);
        if (res.ok) {
          const data = await res.json();
          setResults(data.results ?? []);
        }
      } catch { /* ignore */ }
      setLoading(false);
    }, 200);
    return () => clearTimeout(timer);
  }, [query]);

  const navigate = (href: string) => {
    router.push(href);
    onClose();
  };

  const groupedResults: Record<string, any[]> = {};
  results.forEach((r: any) => {
    const type = r.type || 'page';
    if (!groupedResults[type]) groupedResults[type] = [];
    groupedResults[type].push(r);
  });

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh]" onClick={onClose}>
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

      {/* Palette */}
      <div
        className="relative w-full max-w-lg glass-heavy rounded-xl shadow-2xl overflow-hidden animate-fade-scale-in"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 px-4 py-3 border-b border-border">
          <Search className="h-4 w-4 text-muted-foreground shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search pages, artists, workflows..."
            className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground/40 focus:outline-none"
          />
          <kbd className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground font-mono">ESC</kbd>
        </div>

        <div className="max-h-[40vh] overflow-y-auto">
          {loading && (
            <div className="flex items-center justify-center py-6">
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
            </div>
          )}

          {!loading && query.length >= 2 && results.length === 0 && (
            <div className="py-8 text-center text-xs text-muted-foreground">
              No results for &ldquo;{query}&rdquo;
            </div>
          )}

          {!loading && Object.entries(groupedResults).map(([type, items]) => (
            <div key={type}>
              <div className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/40">
                {typeLabels[type] || type}
              </div>
              {items.map((result: any, i: number) => {
                const Icon = typeIcons[result.type] || FileText;
                const colorClass = typeColors[result.type] || 'bg-primary/10 text-primary';
                return (
                  <button
                    key={`${result.type}-${result.id}-${i}`}
                    onClick={() => navigate(result.href)}
                    className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-surface-hover transition-colors text-left group"
                  >
                    {result.type === 'artist' && result.image ? (
                      <div className="w-7 h-7 rounded-md overflow-hidden shrink-0 ring-1 ring-border">
                        <img src={result.image} alt="" className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                      </div>
                    ) : (
                      <div className={`p-1 rounded-md ${colorClass} shrink-0`}>
                        <Icon className="h-3.5 w-3.5" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-xs font-medium truncate">{result.label}</p>
                        {result.score && (
                          <span className="text-[10px] font-bold text-primary shrink-0">{result.score}</span>
                        )}
                      </div>
                      <p className="text-[11px] text-muted-foreground truncate">{result.description}</p>
                    </div>
                    <ArrowRight className="h-3.5 w-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                );
              })}
            </div>
          ))}

          {!loading && !query && (
            <div className="py-6 px-4 text-center text-xs text-muted-foreground">
              <Sparkles className="h-5 w-5 mx-auto mb-2 text-primary/60" />
              <p className="font-medium text-foreground/60">Quick navigation</p>
              <p className="mt-1">Type at least 2 characters to search</p>
              <div className="flex items-center justify-center gap-3 mt-3 text-[10px] text-muted-foreground/60">
                <span><kbd className="px-1 py-0.5 rounded bg-muted font-mono">↑↓</kbd> navigate</span>
                <span><kbd className="px-1 py-0.5 rounded bg-muted font-mono">↵</kbd> open</span>
                <span><kbd className="px-1 py-0.5 rounded bg-muted font-mono">ESC</kbd> close</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function TopBar() {
  const pathname = usePathname();
  const router = useRouter();
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearch, setShowSearch] = useState(false);
  const [showPalette, setShowPalette] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { data: notifData, isLoading: notifLoading } = useSWR('/api/v1/notifications', fetcher, { refreshInterval: 30000 });
  const { data: searchData, isLoading: searchLoading } = useSWR(
    searchQuery.length >= 2 ? `/api/v1/search?q=${encodeURIComponent(searchQuery)}` : null,
    fetcher,
  );

  // Cmd+K / Ctrl+K global handler
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setShowPalette(true);
      }
      if (e.key === 'Escape') {
        setShowPalette(false);
        setShowNotifications(false);
        setShowUserMenu(false);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) setShowNotifications(false);
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) setShowSearch(false);
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) setShowUserMenu(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setShowSearch(value.length >= 2);
    }, 200);
  }, []);

  const navigateTo = (href: string) => {
    setShowSearch(false);
    setSearchQuery('');
    router.push(href);
  };

  const markAllRead = async () => {
    await fetch('/api/v1/notifications', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'mark_all_read' }) });
    mutate('/api/v1/notifications');
  };

  const unread = notifData?.unread ?? 0;
  const notifications = notifData?.notifications ?? [];
  const searchResults = searchData?.results ?? [];

  // Group notifications by time
  const groupedNotifs: Record<string, any[]> = {};
  notifications.forEach((n: any) => {
    const group = n.time?.includes('m') ? 'Recent' : n.time?.includes('h') ? 'Today' : 'Earlier';
    if (!groupedNotifs[group]) groupedNotifs[group] = [];
    groupedNotifs[group].push(n);
  });
  const groupOrder = ['Recent', 'Today', 'Yesterday', 'Earlier'];

  return (
    <>
      <header className="h-14 bg-background border-b border-border flex items-center justify-between px-5 gap-4">
        {/* Left: Breadcrumbs */}
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <Breadcrumbs pathname={pathname} />

          {/* System status */}
          <div className="hidden lg:flex items-center gap-1.5 text-[10px] text-muted-foreground ml-2">
            <span className="status-dot status-dot-green" />
            <span>All nominal</span>
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-2">
          {/* Cmd+K hint */}
          <button
            onClick={() => setShowPalette(true)}
            className="hidden sm:flex items-center gap-2 px-2.5 py-1.5 rounded-md bg-surface border border-border text-[11px] text-muted-foreground hover:text-foreground hover:border-primary/20 transition-all"
          >
            <Search className="h-3 w-3" />
            <span className="hidden md:inline">Quick search...</span>
            <kbd className="text-[9px] px-1 py-0.5 rounded bg-muted text-muted-foreground/60 font-mono">⌘K</kbd>
          </button>

          {/* Notifications */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-md hover:bg-surface-hover transition-colors touch-target"
              aria-label={`Notifications (${unread} unread)`}
            >
              <Bell className="h-4 w-4 text-muted-foreground" />
              {unread > 0 && (
                <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-[16px] bg-primary text-primary-foreground text-[9px] font-bold rounded-full flex items-center justify-center px-0.5 shadow-lg">
                  {unread}
                </span>
              )}
            </button>

            {showNotifications && (
              <div className="absolute right-0 top-full mt-1.5 w-80 rounded-xl glass-heavy shadow-xl z-50 max-h-[70vh] flex flex-col animate-fade-scale-in">
                <div className="flex items-center justify-between px-4 py-3 border-b border-border">
                  <div>
                    <p className="text-xs font-semibold">Notifications</p>
                    <p className="text-[10px] text-muted-foreground">{unread} unread</p>
                  </div>
                  {unread > 0 && (
                    <button onClick={markAllRead} className="flex items-center gap-1 text-[11px] text-primary hover:underline">
                      <CheckCircle2 className="h-3 w-3" />
                      Mark all read
                    </button>
                  )}
                </div>
                <div className="overflow-y-auto flex-1">
                  {notifLoading ? (
                    <div className="flex items-center justify-center py-10"><Loader2 className="h-4 w-4 animate-spin text-muted-foreground" /></div>
                  ) : notifications.length === 0 ? (
                    <div className="text-center py-10 text-xs text-muted-foreground">
                      <CheckCircle2 className="h-6 w-6 mx-auto mb-2 text-green-500" />
                      All caught up
                    </div>
                  ) : (
                    <div>
                      {groupOrder.map(group => {
                        const items = groupedNotifs[group];
                        if (!items || items.length === 0) return null;
                        return (
                          <div key={group}>
                            <div className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/40">
                              {group}
                            </div>
                            {items.map((n: any) => (
                              <div key={n.id} className={`px-4 py-3 hover:bg-surface-hover transition-colors ${!n.read ? 'bg-primary/[0.03] border-l-2 border-l-primary' : ''}`}>
                                <div className="flex items-start gap-2.5">
                                  <div className="flex-1 min-w-0">
                                    <p className="text-xs font-medium">{n.title}</p>
                                    <p className="text-[11px] text-muted-foreground mt-0.5">{n.description}</p>
                                    <p className="text-[10px] text-muted-foreground mt-1">{n.time}</p>
                                  </div>
                                  {!n.read && <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0 mt-1.5" />}
                                </div>
                              </div>
                            ))}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
                <div className="p-2 border-t border-border">
                  <button
                    onClick={() => { setShowNotifications(false); router.push('/alerts'); }}
                    className="w-full text-center text-[11px] text-muted-foreground hover:text-foreground py-1.5 rounded-md hover:bg-surface-hover transition-colors"
                  >
                    View all alerts →
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* User Menu */}
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="p-1 rounded-md hover:bg-surface-hover transition-colors touch-target flex items-center gap-1.5"
            >
              <div className="w-7 h-7 rounded-md bg-gradient-to-br from-primary/80 to-primary/40 flex items-center justify-center text-[10px] font-bold text-white">
                IM
              </div>
              <ChevronDown className="h-3 w-3 text-muted-foreground hidden sm:block" />
            </button>

            {showUserMenu && (
              <div className="absolute right-0 top-full mt-1.5 w-48 rounded-xl glass-heavy shadow-xl z-50 animate-fade-scale-in">
                <div className="p-2 border-b border-border">
                  <p className="text-xs font-medium px-2 py-1">Ignacio M.</p>
                  <p className="text-[10px] text-muted-foreground px-2 pb-1">ignacio@sonora.digital</p>
                </div>
                <div className="p-1">
                  <button className="w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-xs text-muted-foreground hover:text-foreground hover:bg-surface-hover transition-colors">
                    <User className="h-3.5 w-3.5" />
                    Profile
                  </button>
                  <button className="w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-xs text-muted-foreground hover:text-foreground hover:bg-surface-hover transition-colors">
                    <Keyboard className="h-3.5 w-3.5" />
                    Keyboard shortcuts
                  </button>
                  <div className="divider my-1" />
                  <button className="w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/5 transition-colors">
                    <LogOut className="h-3.5 w-3.5" />
                    Sign out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Command Palette (Cmd+K) */}
      {showPalette && <CommandPalette onClose={() => setShowPalette(false)} />}
    </>
  );
}
