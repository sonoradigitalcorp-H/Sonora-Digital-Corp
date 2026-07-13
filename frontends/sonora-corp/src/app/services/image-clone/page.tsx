"use client";

export default function ImageClonePage() {
  return (
    <div style={{ padding: "8rem 2rem", position: "relative", zIndex: 1, minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div className="container" style={{ maxWidth: "800px", margin: "0 auto", textAlign: "center" }}>
        <div className="section-tag">🖼️ Clonación de Imagen</div>
        <h1 className="section-title" style={{ fontSize: "clamp(2.5rem, 5vw, 3.5rem)" }}>
          Tu <span className="gradient-text">gemelo visual</span>
        </h1>
        <p className="section-sub" style={{ textAlign: "center", margin: "1.5rem auto 2rem" }}>
          Generamos imágenes hiperrealistas de tu artista o marca con IA. Contenido
          consistente, escalable y listo para redes sociales.
        </p>
        <div className="grid-3" style={{ marginTop: "3rem", textAlign: "left" }}>
          {[
            { icon: "🎨", title: "Estilo Consistente", desc: "Misma persona, mismo estilo, cualquier escenario" },
            { icon: "🤖", title: "IA Generativa (FAL)", desc: "Modelos de última generación para resultados realistas" },
            { icon: "📱", title: "Redes Sociales", desc: "Contenido optimizado para Instagram, TikTok, Twitter" },
            { icon: "🎬", title: "Talking Heads", desc: "Video con sincronía labial a partir de una sola foto" },
            { icon: "📅", title: "Galería Automática", desc: "Contenido nuevo cada semana sin esfuerzo manual" },
            { icon: "💵", title: "Vende 24/7", desc: "El clon genera leads y ventas mientras duermes" },
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
