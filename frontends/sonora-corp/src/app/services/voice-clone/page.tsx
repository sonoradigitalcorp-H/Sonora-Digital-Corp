"use client";

export default function VoiceClonePage() {
  return (
    <div style={{ padding: "8rem 2rem", position: "relative", zIndex: 1, minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div className="container" style={{ maxWidth: "800px", margin: "0 auto", textAlign: "center" }}>
        <div className="section-tag">🎙️ Clonación de Voz</div>
        <h1 className="section-title" style={{ fontSize: "clamp(2.5rem, 5vw, 3.5rem)" }}>
          Tu voz, <span className="gradient-text">siempre presente</span>
        </h1>
        <p className="section-sub" style={{ textAlign: "center", margin: "1.5rem auto 2rem" }}>
          Clonamos cualquier voz con solo 30 segundos de audio. Luego, tu artista o marca
          puede hablar 24/7 en cualquier canal: web, Telegram, WhatsApp, o API.
        </p>
        <div className="grid-3" style={{ marginTop: "3rem", textAlign: "left" }}>
          {[
            { icon: "⚡", title: "30 segundos", desc: "Suficiente para clonar cualquier voz con alta fidelidad" },
            { icon: "🎭", title: "Múltiples tonos", desc: "Alegre, serio, energético. El tono correcto para cada ocasión" },
            { icon: "📡", title: "Streaming en vivo", desc: "WebSocket con latencia &lt;500ms para respuestas en tiempo real" },
            { icon: "🔊", title: "TTS Natural", desc: "Edge TTS con voz DaliaNeural en español mexicano" },
            { icon: "📱", title: "Multi-canal", desc: "Web, Telegram, WhatsApp, REST API, WebSocket" },
            { icon: "📊", title: "Analíticas", desc: "Dashboard con uso, calidad y retroalimentación" },
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
