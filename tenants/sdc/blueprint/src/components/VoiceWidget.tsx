"use client";
import { useState, useCallback } from "react";
import { useVoice } from "../use-voice";
import { useRag } from "../use-rag";
import { useTenant } from "../use-tenant";

export function VoiceWidget() {
  const tenant = useTenant();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; text: string }[]>([]);
  const { status, listenAndAsk, speak } = useVoice({ tenant: tenant.tenantName });
  const rag = useRag({ tenantId: tenant.tenantName.toLowerCase().replace(/\s+/g, "_") });

  const handleVoice = useCallback(async () => {
    const context = "";
    const answer = await listenAndAsk(context);
    if (answer) {
      setMessages((prev) => [...prev, { role: "assistant", text: answer }]);
      speak(answer);
    }
  }, [listenAndAsk, speak]);

  return (
    <>
      <button
        onClick={() => setOpen((o) => !o)}
        style={{
          position: "fixed", bottom: "2rem", right: "2rem", zIndex: 200,
          width: "4rem", height: "4rem", borderRadius: "50%",
          background: `linear-gradient(135deg, ${tenant.primaryColor}, ${tenant.accentColor})`,
          border: "none", cursor: "pointer",
          display: open ? "none" : "flex", alignItems: "center", justifyContent: "center",
          boxShadow: `0 4px 25px ${tenant.primaryColor}55`,
        }}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#000" strokeWidth="2">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
          <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
          <line x1="12" y1="19" x2="12" y2="23" />
          <line x1="8" y1="23" x2="16" y2="23" />
        </svg>
      </button>

      <div style={{
        position: "fixed", bottom: "7rem", right: "2rem", zIndex: 199,
        width: "380px", maxWidth: "calc(100vw - 2rem)",
        background: "rgba(10,10,15,0.92)", backdropFilter: "blur(32px)",
        border: "1px solid rgba(255,255,255,0.08)", borderRadius: "20px",
        padding: "1.5rem",
        transform: open ? "translateY(0)" : "translateY(30px)",
        opacity: open ? 1 : 0, pointerEvents: open ? "auto" : "none",
        transition: "all 0.4s",
        boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <h3 style={{ fontSize: "1rem", fontWeight: 500, margin: 0, color: tenant.primaryColor }}>
            Asistente de Voz
          </h3>
          <button onClick={() => setOpen(false)} style={{ background: "none", border: "none", color: "rgba(255,255,255,0.45)", cursor: "pointer", padding: "0.25rem" }}>
            ✕
          </button>
        </div>

        <div style={{ textAlign: "center", fontSize: "0.8rem", color: status === "listening" ? tenant.primaryColor : "rgba(255,255,255,0.45)", marginBottom: "0.8rem" }}>
          {status === "listening" ? "🎤 Escuchando..." : status === "processing" ? "⏳ Procesando..." : status === "speaking" ? "🔊 Hablando..." : "Presiona el micrófono"}
        </div>

        <div style={{ maxHeight: "200px", overflowY: "auto", marginBottom: "1rem", display: "flex", flexDirection: "column", gap: "0.6rem" }}>
          {messages.map((m, i) => (
            <div key={i} style={{
              padding: "0.7rem 1rem", borderRadius: "12px", fontSize: "0.875rem", lineHeight: 1.5,
              maxWidth: "85%",
              ...(m.role === "user"
                ? { background: `${tenant.primaryColor}1a`, alignSelf: "flex-end" as const }
                : { background: "rgba(255,255,255,0.04)", alignSelf: "flex-start" as const }),
            }}>
              {m.text}
            </div>
          ))}
        </div>

        <button onClick={handleVoice} disabled={status === "processing" || status === "speaking"}
          style={{
            width: "100%", padding: "0.7rem", borderRadius: "12px", border: "none",
            background: status === "listening" ? "#ff3b5c" : `linear-gradient(135deg, ${tenant.primaryColor}, ${tenant.accentColor})`,
            color: "#000", cursor: "pointer", fontWeight: 600, fontSize: "0.85rem",
          }}>
          {status === "listening" ? "🔴 Detener" : "🎤 Pulsa para hablar"}
        </button>
      </div>
    </>
  );
}
