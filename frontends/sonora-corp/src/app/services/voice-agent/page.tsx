"use client";

export default function VoiceAgentPage() {
  return (
    <div style={{ padding: "8rem 2rem", position: "relative", zIndex: 1, minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div className="container" style={{ maxWidth: "800px", margin: "0 auto", textAlign: "center" }}>
        <div className="section-tag">🤖 Voice Agent 24/7</div>
        <h1 className="section-title" style={{ fontSize: "clamp(2.5rem, 5vw, 3.5rem)" }}>
          Tu <span className="gradient-text">asistente que vende</span> solo
        </h1>
        <p className="section-sub" style={{ textAlign: "center", margin: "1.5rem auto 2rem" }}>
          Un agente de voz con memoria, que aprende de cada conversación y mejora solo.
          Atiende clientes, califica leads y cierra ventas 24/7.
        </p>
        <div className="grid-3" style={{ marginTop: "3rem", textAlign: "left" }}>
          {[
            { icon: "💾", title: "Memoria Persistente", desc: "Recuerda cada conversación, usuario y preferencia entre sesiones" },
            { icon: "🔄", title: "Automejora", desc: "Evolution Engine evalúa y optimiza respuestas automaticamente" },
            { icon: "👥", title: "Multi-Tenant", desc: "Personalidad y tono adaptado por cliente, detectado por dominio" },
            { icon: "🎯", title: "Ventas 24/7", desc: "Califica leads, respresa precios, ofrece demos, cierra ventas" },
            { icon: "📊", title: "Analítica", desc: "Dashboard con métricas: conversión, satisfacción, areas de mejora" },
            { icon: "🔌", title: "Integración Total", desc: "WebSocket, REST, Telegram, WhatsApp. Un backend, todos los canales" },
          ].map((f) => (
            <div key={f.title} className="card" style={{ padding: "1.5rem", background: "rgba(255,255,255,0.03)", borderRadius: "16px", border: "1px solid rgba(255,255,255,0.06)" }}>
              <div style={{ fontSize: "1.8rem", marginBottom: "0.8rem" }}>{f.icon}</div>
              <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "0.3rem", fontFamily: "'Outfit', sans-serif" }}>{f.title}</h3>
              <p style={{ color: "rgba(255,255,255,0.45)", fontSize: "0.85rem", lineHeight: 1.6, fontWeight: 300 }}>{f.desc}</p>
            </div>
          ))}
        </div>
        <a href="/pricing" className="btn btn-primary" style={{ marginTop: "3rem" }}>Ver Precios</a>
      </div>
    </div>
  );
}
