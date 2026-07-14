"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { connectWS, mcpCall, type AgentEvent, type Agent } from "@/lib/client";

type Panel = "agents" | "storage" | "pipeline" | "memory" | "events";

export default function ControlCenter() {
  const [activePanel, setActivePanel] = useState<Panel>("agents");
  const [wsStatus, setWsStatus] = useState<"connecting" | "connected" | "disconnected">("disconnected");
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [storageFiles, setStorageFiles] = useState<any[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [memoryQuery, setMemoryQuery] = useState("");
  const [memoryResults, setMemoryResults] = useState<any[]>([]);
  const [pipelineRuns, setPipelineRuns] = useState<any[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const eventsEndRef = useRef<HTMLDivElement>(null);

  // Load initial data
  useEffect(() => {
    mcpCall("supabase_list_files", { bucket: "sdc-assets", folder: "content" }).then((d) => {
      const r = d?.result;
      if (Array.isArray(r)) setStorageFiles(r.slice(0, 50));
    });
    mcpCall("hasura_query", { query: "{ artists { name streams revenue } }" }).then((d) => {
      const artists = d?.result?.data?.artists || [];
      setAgents([
        { name: "ceo", tenant: "abe-music", role: "CEO — Revenue & KPIs", tools: ["hasura", "engram"], status: "idle", last_seen: new Date().toISOString() },
        { name: "marketing", tenant: "abe-music", role: "Brand & Campaigns", tools: ["rag", "llm"], status: "idle", last_seen: new Date().toISOString() },
        { name: "content", tenant: "abe-music", role: "Daily Videos", tools: ["generate_video", "ffmpeg"], status: "idle", last_seen: new Date().toISOString() },
        { name: "sales", tenant: "abe-music", role: "Payments & Merch", tools: ["stripe", "upload"], status: "idle", last_seen: new Date().toISOString() },
        { name: "support", tenant: "abe-music", role: "Customer Service", tools: ["rag", "omnivoice"], status: "idle", last_seen: new Date().toISOString() },
        { name: "voice", tenant: "abe-music", role: "Voice Assistant", tools: ["omnivoice", "whisper"], status: "idle", last_seen: new Date().toISOString() },
        { name: "creator", tenant: "sdc", role: "Company Builder", tools: ["lovable", "hasura"], status: "idle", last_seen: new Date().toISOString() },
        { name: "quality", tenant: "sdc", role: "Prompt Certification", tools: ["llm", "engram"], status: "idle", last_seen: new Date().toISOString() },
        { name: "monitor", tenant: "sdc", role: "System Watchdog", tools: ["engram"], status: "running", last_seen: new Date().toISOString() },
      ]);
    });
    mcpCall("engram_search", { tenant_id: "abe-music", query: "pipeline content", limit: 10 }).then((d) => {
      const results = d?.result?.results || [];
      setPipelineRuns(results);
    });
  }, []);

  // WebSocket connection
  useEffect(() => {
    setWsStatus("connecting");
    const ws = connectWS(
      (ev) => {
        setEvents((prev) => [ev, ...prev].slice(0, 200));
        if (ev.channel === "system:pipeline:end") {
          setPipelineRuns((prev: any[]) => [{ data: ev.data, time: new Date().toISOString() }, ...prev].slice(0, 20));
        }
        if (ev.channel === "agent:content:done") {
          mcpCall("supabase_list_files", { bucket: "sdc-assets", folder: "content" }).then((d) => {
            if (Array.isArray(d?.result)) setStorageFiles(d.result.slice(0, 50));
          });
        }
      },
      () => setWsStatus("connected"),
      () => setWsStatus("disconnected")
    );
    wsRef.current = ws;
    return () => ws.close();
  }, []);

  const searchMemory = useCallback(async () => {
    if (!memoryQuery) return;
    const d = await mcpCall("engram_search", { tenant_id: "abe-music", query: memoryQuery });
    setMemoryResults(d?.result?.results || []);
  }, [memoryQuery]);

  const panels: Record<Panel, { label: string; icon: string }> = {
    agents: { label: "Agentes", icon: "🤖" },
    storage: { label: "Archivos", icon: "📁" },
    pipeline: { label: "Pipeline", icon: "⚡" },
    memory: { label: "Memoria", icon: "🧠" },
    events: { label: "Tiempo Real", icon: "🔴" },
  };

  return (
    <div className="min-h-screen p-4 md:p-6 max-w-7xl mx-auto">
      {/* Header */}
      <header className="glass rounded-2xl p-4 mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-yellow-300 bg-clip-text text-transparent">
            SDC Control Center
          </h1>
          <p className="text-sm text-gray-500 mt-1">Agent Operating System</p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`w-2 h-2 rounded-full ${wsStatus === "connected" ? "bg-green-500" : wsStatus === "connecting" ? "bg-yellow-500" : "bg-red-500"}`} />
          <span className="text-xs text-gray-500">{wsStatus}</span>
          <span className="text-xs text-gray-600">|</span>
          <span className="text-xs text-gray-500">{events.length} eventos</span>
        </div>
      </header>

      {/* Nav Tabs */}
      <nav className="flex gap-2 mb-6 overflow-x-auto">
        {(Object.entries(panels) as [Panel, typeof panels[Panel]][]).map(([key, p]) => (
          <button
            key={key}
            onClick={() => setActivePanel(key)}
            className={`px-4 py-2 rounded-xl text-sm whitespace-nowrap transition-all ${
              activePanel === key
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                : "glass text-gray-400 hover:text-gray-200"
            }`}
          >
            {p.icon} {p.label}
          </button>
        ))}
      </nav>

      {/* Panels */}
      {activePanel === "agents" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((a) => (
            <div key={a.name} className="glass rounded-xl p-4 hover:bg-white/5 transition-all">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-amber-300">{a.name}</h3>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  a.status === "running" ? "bg-green-500/20 text-green-400" :
                  a.status === "error" ? "bg-red-500/20 text-red-400" :
                  "bg-gray-500/20 text-gray-400"
                }`}>{a.status}</span>
              </div>
              <p className="text-xs text-gray-400 mb-2">{a.role}</p>
              <p className="text-xs text-gray-600">Tenant: {a.tenant}</p>
              <div className="flex flex-wrap gap-1 mt-2">
                {a.tools.map((t) => (
                  <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-500">{t}</span>
                ))}
              </div>
              <p className="text-[10px] text-gray-700 mt-2">Última vez: {new Date(a.last_seen).toLocaleTimeString()}</p>
            </div>
          ))}
        </div>
      )}

      {activePanel === "storage" && (
        <div>
          <div className="glass rounded-xl p-4 mb-4">
            <h2 className="text-sm font-semibold text-amber-300 mb-2">📁 sdc-assets/content/</h2>
            <p className="text-xs text-gray-500">{storageFiles.length} archivos</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {storageFiles.map((f: any, i) => {
              const name = f.name || f.path || `file-${i}`;
              const isVideo = name.match(/\.(mp4|webm|mov)$/i);
              const isImage = name.match(/\.(jpg|jpeg|png|gif|webp)$/i);
              const url = `https://jibalggzudkflwzdndqz.supabase.co/storage/v1/object/public/sdc-assets/${f.name || f.path}`;
              return (
                <a key={i} href={url} target="_blank" className="glass rounded-xl p-2 hover:bg-white/5 transition-all group">
                  {isVideo ? (
                    <video src={url} className="w-full h-24 object-cover rounded-lg mb-1" />
                  ) : isImage ? (
                    <img src={url} alt={name} className="w-full h-24 object-cover rounded-lg mb-1" />
                  ) : (
                    <div className="w-full h-24 flex items-center justify-center text-2xl rounded-lg mb-1 bg-gray-900">📄</div>
                  )}
                  <p className="text-[10px] text-gray-500 truncate">{name.split("/").pop()}</p>
                  <p className="text-[10px] text-gray-700">{f.metadata?.size ? `${(f.metadata.size / 1024).toFixed(0)}KB` : ""}</p>
                </a>
              );
            })}
          </div>
        </div>
      )}

      {activePanel === "pipeline" && (
        <div>
          <div className="glass rounded-xl p-4 mb-4">
            <h2 className="text-sm font-semibold text-amber-300 mb-2">⚡ Pipeline Diario</h2>
            <p className="text-xs text-gray-500">{pipelineRuns.length} ejecuciones registradas</p>
          </div>
          <div className="space-y-2">
            {pipelineRuns.map((run: any, i) => (
              <div key={i} className="glass rounded-xl p-3">
                <p className="text-xs text-gray-300">{typeof run === "string" ? run : JSON.stringify(run).slice(0, 200)}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {activePanel === "memory" && (
        <div>
          <div className="glass rounded-xl p-4 mb-4">
            <div className="flex gap-2">
              <input
                value={memoryQuery}
                onChange={(e) => setMemoryQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && searchMemory()}
                placeholder="Buscar en memoria... ej: Hector, pipeline, video"
                className="flex-1 bg-gray-900/50 border border-gray-800 rounded-xl px-4 py-2 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-amber-500/50"
              />
              <button onClick={searchMemory} className="px-4 py-2 bg-amber-500/20 text-amber-300 rounded-xl text-sm border border-amber-500/30 hover:bg-amber-500/30">
                Buscar
              </button>
            </div>
          </div>
          <div className="space-y-2">
            {memoryResults.map((r: any, i) => (
              <div key={i} className="glass rounded-xl p-3">
                <p className="text-xs text-amber-400/80 font-mono">{r.key}</p>
                <p className="text-xs text-gray-400 mt-1">{r.value?.slice(0, 200)}</p>
                <p className="text-[10px] text-gray-700 mt-1">Score: {r.score || r.importance} | Accesos: {r.access_count}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {activePanel === "events" && (
        <div className="glass rounded-xl p-4 h-[60vh] overflow-y-auto">
          <h2 className="text-sm font-semibold text-amber-300 mb-3">🔴 Eventos en Tiempo Real</h2>
          <div className="space-y-1 font-mono text-xs">
            {events.map((ev, i) => (
              <div key={i} className={`p-1.5 rounded ${
                ev.channel?.includes("failed") || ev.channel?.includes("alert") ? "bg-red-950/30 text-red-400" :
                ev.channel?.includes("done") || ev.channel?.includes("end") ? "bg-green-950/30 text-green-400" :
                "text-gray-500"
              }`}>
                <span className="text-gray-700">{new Date().toLocaleTimeString()}</span>{" "}
                <span className="text-amber-600">{ev.channel}</span>{" "}
                <span>{JSON.stringify(ev.data).slice(0, 120)}</span>
              </div>
            ))}
            <div ref={eventsEndRef} />
          </div>
        </div>
      )}
    </div>
  );
}
