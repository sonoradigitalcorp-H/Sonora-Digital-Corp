'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Search, Bell, Moon, Sun, CheckCircle2, AlertTriangle, Info, X, Loader2, ArrowRight, FileText, Users, Music2, Activity, Crosshair } from 'lucide-react';
import { useTheme } from 'next-themes';
import useSWR, { mutate } from 'swr';
import { useRouter } from 'next/navigation';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const typeIcons: Record<string, any> = {
  critical: AlertTriangle, warning: AlertTriangle, info: Info, success: CheckCircle2,
};

const typeColors: Record<string, string> = {
  critical: 'text-red-500 bg-red-500/10 border-red-500/20',
  warning: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
  info: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  success: 'text-green-500 bg-green-500/10 border-green-500/20',
};

const typeIcons_search: Record<string, any> = {
  artist: Music2, page: Activity, warroom: Crosshair, workflow: FileText,
};

const typeColors_search: Record<string, string> = {
  artist: 'text-purple-500 bg-purple-500/10',
  page: 'text-blue-500 bg-blue-500/10',
  warroom: 'text-red-500 bg-red-500/10',
  workflow: 'text-amber-500 bg-amber-500/10',
};

export function TopBar() {
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearch, setShowSearch] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { data: notifData, isLoading: notifLoading } = useSWR('/api/v1/notifications', fetcher, { refreshInterval: 30000 });
  const { data: searchData, isLoading: searchLoading } = useSWR(
    searchQuery.length >= 2 ? `/api/v1/search?q=${encodeURIComponent(searchQuery)}` : null,
    fetcher,
  );

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) setShowNotifications(false);
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) setShowSearch(false);
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

  return (
    <header className="h-16 border-b border-border/50 bg-card/80 backdrop-blur-xl flex items-center justify-between px-6">
      <div className="flex items-center gap-4 flex-1 max-w-md">
        <div className="relative w-full" ref={searchRef}>
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search SIGNAL — artists, modules, intelligence..."
            value={searchQuery}
            onChange={e => handleSearchChange(e.target.value)}
            onFocus={() => searchQuery.length >= 2 && setShowSearch(true)}
            className="w-full pl-10 pr-4 py-2 rounded-xl border border-border/50 bg-muted/30 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/30 transition-all duration-200 placeholder:text-muted-foreground/50"
          />
          {searchQuery && (
            <button onClick={() => { setSearchQuery(''); setShowSearch(false); }} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
              <X className="h-3.5 w-3.5" />
            </button>
          )}

          {/* Search Results Dropdown */}
          {showSearch && (
            <div className="absolute top-full mt-2 left-0 right-0 rounded-xl border bg-card shadow-2xl z-50 overflow-hidden backdrop-blur-xl">
              {searchLoading ? (
                <div className="flex items-center justify-center py-8"><Loader2 className="h-5 w-5 animate-spin text-muted-foreground" /></div>
              ) : searchResults.length === 0 ? (
                <div className="py-8 text-center text-sm text-muted-foreground">No results found for &quot;{searchQuery}&quot;</div>
              ) : (
                <div className="divide-y max-h-[60vh] overflow-y-auto">
                  {/* Group by type */}
                  {['page', 'workflow', 'warroom', 'artist'].map(type => {
                    const items = searchResults.filter((r: any) => r.type === type);
                    if (items.length === 0) return null;
                    const typeLabel: Record<string, string> = { page: 'Modules', workflow: 'Workflows', warroom: 'War Rooms', artist: 'Artists' };
                    return (
                      <div key={type}>
                        <div className="px-4 py-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground bg-muted/30">
                          {typeLabel[type]}
                        </div>
                        {items.map((result: any, i: number) => {
                          const Icon = typeIcons_search[result.type] || FileText;
                          const colorClass = typeColors_search[result.type] || 'bg-primary/10 text-primary';
                          return (
                            <button
                              key={`${result.type}-${result.id}-${i}`}
                              onClick={() => navigateTo(result.href)}
                              className="w-full flex items-center gap-3 px-4 py-3 hover:bg-accent/50 transition-colors text-left group"
                            >
                              {result.type === 'artist' && result.image ? (
                                <div className="w-8 h-8 rounded-lg overflow-hidden shrink-0 ring-1 ring-border">
                                  <img src={result.image} alt="" className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                                </div>
                              ) : (
                                <div className={`p-1.5 rounded-lg ${colorClass} shrink-0`}>
                                  <Icon className="h-4 w-4" />
                                </div>
                              )}
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                  <p className="text-sm font-medium truncate">{result.label}</p>
                                  {result.score && (
                                    <span className="text-[10px] font-bold text-amber-500 shrink-0">{result.score}</span>
                                  )}
                                  {result.growth && (
                                    <span className={`text-[10px] font-medium shrink-0 ${result.growth >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                      {result.growth >= 0 ? '+' : ''}{result.growth}%
                                    </span>
                                  )}
                                </div>
                                <p className="text-xs text-muted-foreground truncate">{result.description}</p>
                              </div>
                              <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                            </button>
                          );
                        })}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} className="p-2 rounded-lg hover:bg-accent transition-colors">
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>

        <div className="relative" ref={dropdownRef}>
          <button onClick={() => setShowNotifications(!showNotifications)} className="relative p-2 rounded-lg hover:bg-accent transition-colors">
            <Bell className="h-4 w-4" />
            {unread > 0 && (
              <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 bg-destructive text-destructive-foreground text-[10px] font-bold rounded-full flex items-center justify-center px-1">
                {unread}
              </span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 top-full mt-2 w-96 rounded-xl border bg-card shadow-2xl z-50 max-h-[75vh] flex flex-col">
              <div className="flex items-center justify-between p-4 border-b">
                <div>
                  <h3 className="font-semibold text-sm">Notifications</h3>
                  <p className="text-xs text-muted-foreground">{unread} unread</p>
                </div>
                {unread > 0 && (
                  <button onClick={markAllRead} className="text-xs text-primary hover:underline">Mark all read</button>
                )}
              </div>
              <div className="overflow-y-auto flex-1">
                {notifLoading ? (
                  <div className="flex items-center justify-center py-12"><Loader2 className="h-5 w-5 animate-spin text-muted-foreground" /></div>
                ) : notifications.length === 0 ? (
                  <div className="text-center py-12 text-sm text-muted-foreground">
                    <CheckCircle2 className="h-8 w-8 mx-auto mb-2 text-green-500" />
                    All caught up!
                  </div>
                ) : (
                  <div className="divide-y">
                    {notifications.map((n: any) => {
                      const Icon = typeIcons[n.type] || Info;
                      const colorClass = typeColors[n.type] || typeColors.info;
                      return (
                        <div key={n.id} className={`p-4 hover:bg-accent/50 transition-colors cursor-pointer ${!n.read ? 'bg-primary/5' : ''}`}>
                          <div className="flex items-start gap-3">
                            <div className={`p-1.5 rounded-lg ${colorClass} shrink-0`}><Icon className="h-3.5 w-3.5" /></div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium">{n.title}</p>
                              <p className="text-xs text-muted-foreground mt-0.5">{n.description}</p>
                              <p className="text-[10px] text-muted-foreground mt-1">{n.time}</p>
                            </div>
                            {!n.read && <span className="w-2 h-2 rounded-full bg-primary shrink-0 mt-1" />}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 pl-3 border-l">
          <div className="text-right">
            <p className="text-xs font-medium">Executive Access</p>
            <p className="text-[10px] text-muted-foreground">Live Data</p>
          </div>
        </div>
      </div>
    </header>
  );
}
