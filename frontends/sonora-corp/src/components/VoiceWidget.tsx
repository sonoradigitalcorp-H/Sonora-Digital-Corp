"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Mic, MicOff, X, MessageSquare, Trash2, Send } from "lucide-react";
import AudioViz from "./AudioViz";

type Message = { role: "user" | "assistant"; text: string };

const CONFIG: Record<string, { name: string; color: string }> = {
  abe: { name: "Abe", color: "#FFD700" },
  sonora: { name: "Sona", color: "#8b5cf6" },
};

export default function VoiceWidget({ tenant = "abe" }: { tenant?: string }) {
  const cfg = CONFIG[tenant] || CONFIG.abe;
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState("Presiona el micrófono y dime algo");
  const [listening, setListening] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [showInput, setShowInput] = useState(false);
  const [inputText, setInputText] = useState("");
  const wsRef = useRef<WebSocket | null>(null);
  const sessionRef = useRef(`web-${Date.now()}-${Math.random().toString(36).slice(2)}`);
  const convRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  const connectWS = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    setConnecting(true);
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${proto}//${location.host}/ws`);
    ws.onopen = () => {
      setConnecting(false);
      setStatus("Conectado. Presiona el micrófono");
    };
    ws.onmessage = (e) => {
      try {
        const d = JSON.parse(e.data);
        if (d.type === "chat_response" || d.type === "audio_response") {
          if (d.text) setMessages((prev) => [...prev, { role: "user", text: d.text }]);
          if (d.response) setMessages((prev) => [...prev, { role: "assistant", text: d.response }]);
          if (d.audio) {
            new Audio(`data:audio/mp3;base64,${d.audio}`).play().catch(() => {});
          }
          setStatus("Presiona el micrófono");
        }
        if (d.type === "error") setStatus(`Error: ${d.error}`);
      } catch {}
    };
    ws.onclose = () => {
      wsRef.current = null;
      setStatus("Desconectado");
    };
    ws.onerror = () => setStatus("Error de conexión");
    wsRef.current = ws;
  }, []);

  useEffect(() => {
    if (open && !wsRef.current) connectWS();
  }, [open, connectWS]);

  useEffect(() => {
    if (convRef.current) {
      convRef.current.scrollTop = convRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if (showInput && inputRef.current) inputRef.current.focus();
  }, [showInput]);

  const sendMessage = useCallback((text: string) => {
    if (!text.trim()) return;
    setMessages((prev) => [...prev, { role: "user", text: text.trim() }]);
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "chat", text: text.trim(), session_id: sessionRef.current }));
    }
    setShowInput(false);
    setInputText("");
  }, []);

  const toggleRecording = useCallback(() => {
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      setStatus("Procesando...");
      return;
    }

    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SR) {
      setStatus("Tu navegador no soporta voz. Usa 'Escribir'.");
      return;
    }

    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) connectWS();

    const r = new SR();
    r.lang = "es-MX";
    r.interimResults = false;
    r.continuous = false;

    r.onstart = () => {
      setListening(true);
      setStatus("Escuchando...");
    };

    r.onresult = (e: any) => {
      const text = e.results[0][0].transcript;
      sendMessage(text);
    };

    r.onerror = () => setStatus("Presiona el micrófono");
    r.onend = () => {
      setListening(false);
      recognitionRef.current = null;
    };

    recognitionRef.current = r;
    r.start();
  }, [listening, connectWS, sendMessage]);

  const clearConversation = useCallback(() => {
    setMessages([]);
    sessionRef.current = `web-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    setStatus("Presiona el micrófono y dime algo");
  }, []);

  return (
    <>
      <button
        onClick={() => setOpen((o) => !o)}
        style={{
          position: "fixed",
          bottom: "2rem",
          right: "2rem",
          zIndex: 200,
          width: "4rem",
          height: "4rem",
          borderRadius: "50%",
          background: `linear-gradient(135deg, ${cfg.color}, ${cfg.color}dd)`,
          border: "none",
          cursor: "pointer",
          display: open ? "none" : "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: `0 4px 25px ${cfg.color}55`,
          transition: "all 0.4s cubic-bezier(.25,.46,.45,.94)",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = "scale(1.12)";
          e.currentTarget.style.boxShadow = `0 8px 40px ${cfg.color}77`;
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = "scale(1)";
          e.currentTarget.style.boxShadow = `0 4px 25px ${cfg.color}55`;
        }}
      >
        <Mic size={24} color="#000" />
      </button>

      <div
        style={{
          position: "fixed",
          bottom: "7rem",
          right: "2rem",
          zIndex: 199,
          width: "400px",
          maxWidth: "calc(100vw - 2rem)",
          background: "rgba(10,10,15,0.92)",
          backdropFilter: "blur(32px)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: "20px",
          padding: "1.5rem",
          transform: open ? "translateY(0)" : "translateY(30px)",
          opacity: open ? 1 : 0,
          pointerEvents: open ? "auto" : "none",
          transition: "all 0.4s cubic-bezier(.25,.46,.45,.94)",
          boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <h3 style={{ fontSize: "1rem", fontWeight: 500, margin: 0 }}>
            <span className="gradient-text">{cfg.name}</span> &mdash; Asistente de Voz
          </h3>
          <button
            onClick={() => { setOpen(false); setShowInput(false); }}
            style={{ background: "none", border: "none", color: "rgba(255,255,255,0.45)", cursor: "pointer", fontSize: "1.2rem", padding: "0.25rem" }}
          >
            <X size={18} />
          </button>
        </div>

        <AudioViz isActive={listening} color={cfg.color} />

        <div
          style={{
            textAlign: "center",
            fontSize: "0.8rem",
            color: listening ? cfg.color : "rgba(255,255,255,0.45)",
            marginBottom: "0.8rem",
            fontWeight: 300,
          }}
        >
          {connecting ? "Conectando..." : status}
        </div>

        <div
          ref={convRef}
          style={{
            maxHeight: "200px",
            overflowY: "auto",
            marginBottom: "1rem",
            display: "flex",
            flexDirection: "column",
            gap: "0.6rem",
            paddingRight: "0.25rem",
          }}
        >
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                padding: "0.7rem 1rem",
                borderRadius: "12px",
                fontSize: "0.875rem",
                lineHeight: 1.5,
                fontWeight: 300,
                maxWidth: "85%",
                ...(msg.role === "user"
                  ? { background: `${cfg.color}1a`, alignSelf: "flex-end" as const }
                  : { background: "rgba(255,255,255,0.04)", alignSelf: "flex-start" as const }),
              }}
            >
              {msg.role === "assistant" && (
                <div style={{ color: cfg.color, fontWeight: 600, fontSize: "0.75rem", marginBottom: "0.2rem" }}>
                  {cfg.name}
                </div>
              )}
              {msg.text}
            </div>
          ))}
        </div>

        {showInput ? (
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <input
              ref={inputRef}
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") sendMessage(inputText); if (e.key === "Escape") setShowInput(false); }}
              placeholder="Escribe tu mensaje..."
              style={{
                flex: 1,
                padding: "0.7rem 1rem",
                borderRadius: "12px",
                border: "1px solid rgba(255,255,255,0.08)",
                background: "rgba(255,255,255,0.04)",
                color: "#f0f0f0",
                fontSize: "0.85rem",
                outline: "none",
              }}
            />
            <button
              onClick={() => sendMessage(inputText)}
              style={{
                padding: "0.7rem",
                borderRadius: "12px",
                border: "none",
                background: `linear-gradient(135deg, ${cfg.color}, ${cfg.color}dd)`,
                color: "#000",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Send size={16} />
            </button>
          </div>
        ) : (
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button
              onClick={toggleRecording}
              style={{
                flex: 1,
                padding: "0.7rem",
                borderRadius: "12px",
                border: listening ? "none" : "1px solid rgba(255,255,255,0.08)",
                background: listening
                  ? "#ff3b5c"
                  : `linear-gradient(135deg, ${cfg.color}, ${cfg.color}dd)`,
                color: listening ? "#fff" : "#000",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "0.85rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "0.4rem",
                transition: "all 0.3s",
              }}
            >
              {listening ? <MicOff size={16} /> : <Mic size={16} />}
              {listening ? "Detener" : "Hablar"}
            </button>
            <button
              onClick={() => setShowInput(true)}
              style={{
                flex: 1,
                padding: "0.7rem",
                borderRadius: "12px",
                border: "1px solid rgba(255,255,255,0.08)",
                background: "rgba(255,255,255,0.04)",
                color: "rgba(255,255,255,0.9)",
                cursor: "pointer",
                fontSize: "0.85rem",
                fontWeight: 400,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "0.3rem",
                transition: "all 0.3s",
              }}
            >
              <MessageSquare size={14} /> Escribir
            </button>
            <button
              onClick={clearConversation}
              style={{
                padding: "0.7rem",
                borderRadius: "12px",
                border: "1px solid rgba(255,255,255,0.08)",
                background: "rgba(255,255,255,0.04)",
                color: "rgba(255,255,255,0.45)",
                cursor: "pointer",
                fontSize: "0.85rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                transition: "all 0.3s",
              }}
            >
              <Trash2 size={16} />
            </button>
          </div>
        )}
      </div>
    </>
  );
}
