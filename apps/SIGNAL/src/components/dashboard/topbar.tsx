'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Search, Bell, CheckCircle2, Loader2, ArrowRight, FileText, Music2, Activity, Crosshair, X } from 'lucide-react';
import useSWR, { mutate } from 'swr';
import { useRouter } from 'next/navigation';

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

export function TopBar() {
  const router = useRouter();
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
    <header className="h-14 bg-background border-b border-border flex items-center justify-between px-5">
      {/* Search */}
      <div className="flex items-center gap-4 flex-1 max-w-sm" ref={searchRef}>
        <div className="relative w-full">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search SIGNAL..."
            value={searchQuery}
            onChange={e => handleSearchChange(e.target.value)}
            onFocus={() => searchQuery.length >= 2 && setShowSearch(true)}
            className="w-full pl-8 pr-3 py-1.5 rounded-md bg-surface text-[13px] placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-primary/40 transition-all duration-150"
          />
          {searchQuery && (
            <button onClick={() => { setSearchQuery(''); setShowSearch(false); }} className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
              <X className="h-3 w-3" />
            </button>
          )}

          {/* Search Results Dropdown */}
          {showSearch && (
            <div className="absolute top-full mt-1.5 left-0 right-0 rounded-lg glass shadow-lg z-50 overflow-hidden">
              {searchLoading ? (
                <div className="flex items-center justify-center py-6"><Loader2 className="h-4 w-4 animate-spin text-muted-foreground" /></div>
              ) : searchResults.length === 0 ? (
                <div className="py-6 text-center text-xs text-muted-foreground">No results for &ldquo;{searchQuery}&rdquo;</div>
              ) : (
                <div className="max-h-[50vh] overflow-y-auto">
                  {['page', 'workflow', 'warroom', 'artist'].map(type => {
                    const items = searchResults.filter((r: any) => r.type === type);
                    if (items.length === 0) return null;
                    return (
                      <div key={type}>
                        <div className="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60">
                          {typeLabels[type]}
                        </div>
                        {items.map((result: any, i: number) => {
                          const Icon = typeIcons[result.type] || FileText;
                          const colorClass = typeColors[result.type] || 'bg-primary/10 text-primary';
                          return (
                            <button
                              key={`${result.type}-${result.id}-${i}`}
                              onClick={() => navigateTo(result.href)}
                              className="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-surface-hover transition-colors text-left group"
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
                                  {result.growth && (
                                    <span className={`text-[10px] font-medium shrink-0 ${result.growth >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                      {result.growth >= 0 ? '+' : ''}{result.growth}%
                                    </span>
                                  )}
                                </div>
                                <p className="text-[11px] text-muted-foreground truncate">{result.description}</p>
                              </div>
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

      {/* Right side — notifications only */}
      <div className="flex items-center">
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-1.5 rounded-md hover:bg-surface-hover transition-colors"
          >
            <Bell className="h-4 w-4 text-muted-foreground" />
            {unread > 0 && (
              <span className="absolute -top-0.5 -right-0.5 min-w-[15px] h-[15px] bg-primary text-primary-foreground text-[9px] font-bold rounded-full flex items-center justify-center px-0.5">
                {unread}
              </span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 top-full mt-1.5 w-80 rounded-lg glass shadow-lg z-50 max-h-[70vh] flex flex-col">
              <div className="flex items-center justify-between px-4 py-3 border-b border-border">
                <div>
                  <p className="text-xs font-semibold">Notifications</p>
                  <p className="text-[10px] text-muted-foreground">{unread} unread</p>
                </div>
                {unread > 0 && (
                  <button onClick={markAllRead} className="text-[11px] text-primary hover:underline">Mark all read</button>
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
                    {notifications.map((n: any) => (
                      <div key={n.id} className={`px-4 py-3 hover:bg-surface-hover transition-colors ${!n.read ? 'bg-primary/5' : ''}`}>
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
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
