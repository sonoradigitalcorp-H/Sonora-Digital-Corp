'use client';

import { useState } from 'react';
import useSWR, { mutate } from 'swr';
import { Video, Calendar, Clock, Users, Plus, Loader2, AlertCircle, X, MapPin, Phone } from 'lucide-react';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const statusColors: Record<string, string> = {
  scheduled: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
  completed: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  cancelled: 'bg-red-500/10 text-red-500 border-red-500/20',
};

const modeIcons: Record<string, any> = {
  video: Video,
  'in-person': MapPin,
  phone: Phone,
};

export function MeetingsRoom({ warRoomId }: { warRoomId: string }) {
  const [showSchedule, setShowSchedule] = useState(false);
  const [scheduling, setScheduling] = useState(false);
  type Mode = 'video' | 'in-person' | 'phone';
  const [form, setForm] = useState<{ title: string; date: string; time: string; attendees: string; mode: Mode }>({
    title: '', date: '', time: '', attendees: '', mode: 'video',
  });

  const { data, error, isLoading } = useSWR(`/api/v1/war-rooms/${warRoomId}/meetings`, fetcher, { refreshInterval: 15000 });
  const meetings = data?.meetings ?? [];

  const schedule = async () => {
    if (!form.title || !form.date || !form.time) return;
    setScheduling(true);
    await fetch(`/api/v1/war-rooms/${warRoomId}/meetings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: form.title,
        date: form.date,
        time: form.time,
        attendees: form.attendees.split(',').map((s: string) => s.trim()).filter(Boolean),
        mode: form.mode,
      }),
    });
    setScheduling(false);
    setShowSchedule(false);
    setForm({ title: '', date: '', time: '', attendees: '', mode: 'video' });
    mutate(`/api/v1/war-rooms/${warRoomId}/meetings`);
  };

  return (
    <div className="p-6 max-w-[1600px] mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Meetings Room</h1>
          <p className="text-muted-foreground mt-1">Schedule, join, and manage war room meetings</p>
        </div>
        <button onClick={() => setShowSchedule(true)} className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-all">
          <Plus className="h-4 w-4" /> Schedule Meeting
        </button>
      </div>

      {error && <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500"><AlertCircle className="h-4 w-4" /><span className="text-sm">Failed to load meetings</span></div>}

      {isLoading ? (
        <div className="flex items-center justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : meetings.length === 0 ? (
        <div className="text-center py-20 text-muted-foreground">
          <Calendar className="h-12 w-12 mx-auto mb-3 opacity-30" />
          <p className="text-lg font-medium">No meetings scheduled</p>
          <p className="text-sm mt-1">Schedule your first meeting to coordinate the team.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {meetings.map((m: any) => {
            const Icon = modeIcons[m.mode] || Video;
            return (
              <div key={m.id} className="rounded-xl border bg-card p-5 hover:shadow-md hover:border-primary/30 transition-all">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-lg bg-primary/10 text-primary"><Icon className="h-5 w-5" /></div>
                    <div>
                      <h3 className="font-semibold">{m.title}</h3>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {Array.isArray(m.attendees) ? m.attendees.map((a: any) => a.name).join(', ') : m.attendees}
                      </p>
                    </div>
                  </div>
                  <span className={`text-xs px-2.5 py-1 rounded-full border font-medium capitalize ${statusColors[m.status] || statusColors.scheduled}`}>
                    {m.status}
                  </span>
                </div>
                <div className="flex items-center gap-6 text-sm text-muted-foreground flex-wrap">
                  <span className="flex items-center gap-1.5"><Calendar className="h-3.5 w-3.5" /> {m.date}</span>
                  <span className="flex items-center gap-1.5"><Clock className="h-3.5 w-3.5" /> {m.time}</span>
                  <span className="flex items-center gap-1.5"><Users className="h-3.5 w-3.5" /> {Array.isArray(m.attendees) ? m.attendees.length : 0} participants</span>
                  <span className="flex items-center gap-1.5 capitalize">{m.mode === 'in-person' ? '📍' : m.mode === 'phone' ? '📞' : '🎥'} {m.mode}</span>
                </div>
                {Array.isArray(m.attendees) && m.attendees.length > 0 && (
                  <div className="flex flex-wrap items-center gap-2 mt-3">
                    {m.attendees.map((a: any, i: number) => (
                      <span key={i} className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium ${a.isAgent ? 'bg-primary/10 text-primary' : 'bg-accent text-muted-foreground'}`}>
                        <span className="w-4 h-4 rounded-full bg-muted flex items-center justify-center text-[10px] font-bold">{a.avatar}</span>
                        {a.name}
                        {a.isAgent && <span className="text-[10px] opacity-70">AI</span>}
                      </span>
                    ))}
                  </div>
                )}
                <div className="flex items-center gap-2 mt-4">
                  {m.status === 'scheduled' && (
                    <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:opacity-90 transition-all">
                      <Video className="h-3.5 w-3.5" /> Join Now
                    </button>
                  )}
                  <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-accent text-xs font-medium hover:bg-accent/80 transition-colors">
                    <Calendar className="h-3.5 w-3.5" /> Add to Calendar
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Schedule Modal */}
      {showSchedule && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => !scheduling && setShowSchedule(false)}>
          <div className="rounded-xl border bg-card p-6 max-w-lg w-full mx-4 shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Schedule Meeting</h3>
              <button onClick={() => setShowSchedule(false)} disabled={scheduling} className="p-1 rounded-lg hover:bg-accent transition-colors disabled:opacity-50"><X className="h-5 w-5" /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Meeting Title</label>
                <input type="text" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} placeholder="e.g., Draft Review — Week 24" className="w-full px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Date</label>
                  <input type="date" value={form.date} onChange={e => setForm({ ...form, date: e.target.value })} className="w-full px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Time</label>
                  <input type="time" value={form.time} onChange={e => setForm({ ...form, time: e.target.value })} className="w-full px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Mode</label>
                <div className="flex gap-2">
                  {( [
                    { id: 'video', label: 'Video', icon: Video },
                    { id: 'in-person', label: 'In Person', icon: MapPin },
                    { id: 'phone', label: 'Phone', icon: Phone },
                  ] as { id: Mode; label: string; icon: any }[] ).map(opt => {
                    const Icon = opt.icon;
                    return (
                      <button key={opt.id} onClick={() => setForm({ ...form, mode: opt.id })}
                        className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm transition-all ${form.mode === opt.id ? 'border-primary bg-primary/5 text-primary' : 'hover:bg-accent'}`}
                      >
                        <Icon className="h-3.5 w-3.5" /> {opt.label}
                      </button>
                    );
                  })}
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Attendees (comma-separated emails)</label>
                <input type="text" value={form.attendees} onChange={e => setForm({ ...form, attendees: e.target.value })} placeholder="e.g., a&r@abe.music, legal@abe.music" className="w-full px-3 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
              </div>
            </div>
            <div className="flex items-center justify-end gap-3 mt-6">
              <button onClick={() => setShowSchedule(false)} disabled={scheduling} className="px-4 py-2 rounded-lg border bg-card text-sm hover:bg-accent transition-colors disabled:opacity-50">Cancel</button>
              <button onClick={schedule} disabled={scheduling || !form.title || !form.date || !form.time} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-all disabled:opacity-50">
                {scheduling ? <Loader2 className="h-4 w-4 animate-spin" /> : <Calendar className="h-4 w-4" />}
                {scheduling ? 'Scheduling...' : 'Schedule Meeting'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
