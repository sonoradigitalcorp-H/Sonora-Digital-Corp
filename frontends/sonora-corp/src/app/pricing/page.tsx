"use client";

export default function PricingPage() {
  return (
    <div style={{ padding: "8rem 2rem", position: "relative", zIndex: 1 }}>
      <div className="container" style={{ maxWidth: "1200px", margin: "0 auto", textAlign: "center" }}>
        <div className="section-tag">💰 Precios</div>
        <h1 className="section-title" style={{ fontSize: "clamp(2.5rem, 5vw, 3.5rem)" }}>
          Planes para cada <span className="gradient-text">etapa</span>
        </h1>
        <p className="section-sub" style={{ textAlign: "center", margin: "1.5rem auto 3rem" }}>
          Elige el plan que mejor se adapte a tus necesidades. Todos incluyen actualizaciones.
        </p>
        <div className="grid-3" style={{ marginTop: "2rem" }}>
          {[
            { name: "Starter", price: "$0", desc: "Prueba el poder de la IA", features: ["1 agente", "100 req/día", "Voz estándar", "Chat básico", "Sin memoria"], popular: false },
            { name: "Pro", price: "$299", desc: "Para marcas en crecimiento", features: ["3 agentes", "10K req/día", "Clonación de voz", "Memoria contextual", "Automejora"], popular: true },
            { name: "Enterprise", price: "$999", desc: "Solución completa", features: ["Agentes ilimitados", "Requests ilimitados", "Voz + imagen clonadas", "RAG por tenant", "On-premise"], popular: false },
          ].map((plan) => (
            <div key={plan.name} className="card" style={{
              background: plan.popular ? "rgba(139,92,246,0.08)" : "rgba(255,255,255,0.03)",
              borderRadius: "20px",
              border: plan.popular ? "1px solid rgba(139,92,246,0.3)" : "1px solid rgba(255,255,255,0.06)",
              padding: "2.5rem 2rem",
              position: "relative",
            }}>
              {plan.popular && <div style={{ position: "absolute", top: "1rem", right: "-2rem", background: "var(--gradient-primary)", color: "#000", padding: "0.25rem 3rem", fontSize: "0.75rem", fontWeight: 700, transform: "rotate(45deg)" }}>POPULAR</div>}
              <h3 style={{ fontSize: "1.3rem", fontWeight: 600, fontFamily: "'Outfit', sans-serif" }}>{plan.name}</h3>
              <p style={{ color: "rgba(255,255,255,0.45)", fontSize: "0.85rem", margin: "0.5rem 0 1rem" }}>{plan.desc}</p>
              <div className="gradient-text" style={{ fontSize: "2.5rem", fontWeight: 600, fontFamily: "'Outfit', sans-serif" }}>{plan.price}<span style={{ fontSize: "1rem", color: "rgba(255,255,255,0.45)", fontWeight: 300, marginLeft: "0.3rem" }}>/mes</span></div>
              <ul style={{ marginTop: "1.5rem", listStyle: "none", padding: 0 }}>
                {plan.features.map((f) => (
                  <li key={f} style={{ padding: "0.4rem 0", fontSize: "0.875rem", color: "rgba(255,255,255,0.45)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <span style={{ color: "#34d399" }}>✓</span> {f}
                  </li>
                ))}
              </ul>
              <a href="/contact" className={`btn ${plan.popular ? "btn-primary" : "btn-outline"}`} style={{ marginTop: "1.5rem", width: "100%", textAlign: "center", display: "inline-block" }}>{plan.name === "Starter" ? "Empezar Gratis" : "Contratar"}</a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
