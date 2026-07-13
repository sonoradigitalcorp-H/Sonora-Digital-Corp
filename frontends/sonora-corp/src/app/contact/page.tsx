"use client";

export default function ContactPage() {
  return (
    <div style={{ padding: "8rem 2rem", position: "relative", zIndex: 1, minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div className="container" style={{ maxWidth: "600px", margin: "0 auto", textAlign: "center" }}>
        <div className="section-tag">📞 Contacto</div>
        <h1 className="section-title" style={{ fontSize: "clamp(2rem, 4vw, 2.8rem)" }}>
          Hablemos de tu <span className="gradient-text">gemelo digital</span>
        </h1>
        <p className="section-sub" style={{ textAlign: "center", margin: "1rem auto 2rem" }}>
          Te mostramos cómo funciona en 15 minutos. Sin compromiso.
        </p>
        <div
          style={{
            background: "rgba(255,255,255,0.03)",
            borderRadius: "20px",
            border: "1px solid rgba(255,255,255,0.06)",
            padding: "2.5rem",
            textAlign: "left",
          }}
        >
          <div style={{ marginBottom: "1.5rem" }}>
            <label style={{ display: "block", fontSize: "0.85rem", color: "rgba(255,255,255,0.45)", marginBottom: "0.4rem", fontWeight: 400 }}>Nombre</label>
            <input type="text" placeholder="Tu nombre" style={{ width: "100%", padding: "0.8rem 1rem", borderRadius: "12px", border: "1px solid rgba(255,255,255,0.08)", background: "rgba(255,255,255,0.04)", color: "#f0f0f0", fontSize: "0.9rem", outline: "none" }} />
          </div>
          <div style={{ marginBottom: "1.5rem" }}>
            <label style={{ display: "block", fontSize: "0.85rem", color: "rgba(255,255,255,0.45)", marginBottom: "0.4rem", fontWeight: 400 }}>Email</label>
            <input type="email" placeholder="tu@email.com" style={{ width: "100%", padding: "0.8rem 1rem", borderRadius: "12px", border: "1px solid rgba(255,255,255,0.08)", background: "rgba(255,255,255,0.04)", color: "#f0f0f0", fontSize: "0.9rem", outline: "none" }} />
          </div>
          <div style={{ marginBottom: "1.5rem" }}>
            <label style={{ display: "block", fontSize: "0.85rem", color: "rgba(255,255,255,0.45)", marginBottom: "0.4rem", fontWeight: 400 }}>Mensaje</label>
            <textarea placeholder="Cuéntanos sobre tu proyecto..." rows={4} style={{ width: "100%", padding: "0.8rem 1rem", borderRadius: "12px", border: "1px solid rgba(255,255,255,0.08)", background: "rgba(255,255,255,0.04)", color: "#f0f0f0", fontSize: "0.9rem", outline: "none", resize: "vertical" }} />
          </div>
          <button className="btn btn-primary" style={{ width: "100%", textAlign: "center" }}>Enviar</button>
        </div>
      </div>
    </div>
  );
}
