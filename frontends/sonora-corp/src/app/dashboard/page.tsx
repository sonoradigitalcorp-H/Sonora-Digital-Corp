"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Bot, Image, Mic, Radio, Music, LogOut, User, Settings, BarChart3, Sparkles } from "lucide-react";

const API = "https://abe.sonoradigitalcorp.com/api";

const ICONS: Record<string, any> = { "mystik-ai": Bot, "content-studio": Image, "omnivoice": Mic, "open-notebook": Radio, "abe-music": Music };

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { window.location.href = "/login"; return; }
    fetch(`${API}/dashboard`, { headers: { "Authorization": `Bearer ${token}` } })
      .then(r => r.json()).then(d => { setDashboard(d); setUser(d.user); setLoading(false); })
      .catch(() => { localStorage.removeItem("token"); window.location.href = "/login"; });
  }, []);

  const logout = () => { localStorage.removeItem("token"); window.location.href = "/login"; };

  if (loading) return (
    <div className="min-h-screen gradient-bg flex items-center justify-center">
      <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 2 }} className="w-8 h-8 border-2 border-[#FF6B35] border-t-transparent rounded-full" />
    </div>
  );

  return (
    <div className="min-h-screen gradient-bg">
      <nav className="glass border-b border-white/5 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#FF6B35] to-[#00ccff] flex items-center justify-center text-black font-bold text-sm">SD</div>
          <span className="font-semibold">Panel de control</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-400">{user?.name}</span>
          <button onClick={logout} className="text-sm text-gray-500 hover:text-white transition flex items-center gap-1">
            <LogOut className="w-4 h-4" /> Salir
          </button>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold">Bienvenido, {user?.name}</h1>
            <span className="text-xs px-3 py-1 rounded-full glass text-[#FF6B35] capitalize">{dashboard?.tenant?.plan}</span>
          </div>
          <p className="text-gray-400 mb-8">{dashboard?.tenant?.name}</p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
            {[
              { label: "Servicios activos", value: dashboard?.services?.length || 0, icon: Sparkles },
              { label: "API calls", value: dashboard?.stats?.api_calls || 0, icon: BarChart3 },
              { label: "Almacenamiento", value: `${dashboard?.stats?.storage_mb || 0} MB`, icon: Settings },
              { label: "Chats activos", value: dashboard?.stats?.active_chats || 0, icon: Bot },
            ].map((s, i) => (
              <motion.div key={s.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
                className="glass rounded-xl p-4">
                <s.icon className="w-5 h-5 text-[#FF6B35] mb-2" />
                <div className="text-2xl font-bold">{s.value}</div>
                <div className="text-xs text-gray-500">{s.label}</div>
              </motion.div>
            ))}
          </div>

          <h2 className="text-lg font-semibold mb-4">Mis servicios</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dashboard?.services?.map((svc: any, i: number) => {
              const Icon = ICONS[svc.id] || Bot;
              return (
                <motion.div key={svc.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
                  className="glass rounded-xl p-5 gradient-border">
                  <Icon className="w-8 h-8 mb-3" style={{ color: svc.id === "mystik-ai" ? "#FF6B35" : svc.id === "content-studio" ? "#b388ff" : svc.id === "omnivoice" ? "#00ccff" : svc.id === "open-notebook" ? "#ff6b6b" : "#00ff88" }} />
                  <h3 className="font-semibold mb-1">{svc.name}</h3>
                  <p className="text-sm text-gray-400 mb-4">{svc.tagline}</p>
                  <div className="flex gap-2">
                    <a href={`/dashboard/${svc.id}`} className="text-xs px-3 py-1.5 rounded-full glass text-gray-300 hover:text-white transition">Abrir</a>
                    <a href={`${API}/${svc.id}`} className="text-xs px-3 py-1.5 rounded-full glass text-gray-300 hover:text-white transition">API</a>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
