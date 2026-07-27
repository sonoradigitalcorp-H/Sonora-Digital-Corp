"use client";

import { useEffect, useRef, useState } from "react";
import Hero3D from "@/components/Hero3D";
import ServiceCard from "@/components/ServiceCard";

const stats = [
  { value: "24/7", label: "Disponibilidad" },
  { value: "99.9%", label: "Uptime" },
  { value: "+50", label: "Agentes activos" },
  { value: "3s", label: "Respuesta promedio" },
];

const services = [
  {
    icon: "🎙️",
    title: "Clonación de Voz",
    description: "Tu artista o marca con voz propia 24/7. Clonamos cualquier voz con IA y la desplegamos en segundos.",
    features: [
      "Clonación con 30 segundos de audio",
      "TTS natural en español (DaliaNeural)",
      "Múltiples tonos y emociones",
      "API REST + WebSocket streaming",
      "Escalable a miles de requests/día",
    ],
    price: "$299/mes",
  },
  {
    icon: "🖼️",
    title: "Clonación de Imagen",
    description: "Gemelos digitales hiperrealistas que venden, promocionan e interactúan por ti.",
    features: [
      "Generación de imágenes con IA (FAL)",
      "Estilo consistente del artista",
      "Contenido para redes sociales",
      "Talking heads con sincronía labial",
      "Galería automática semanal",
    ],
    price: "$499/mes",
  },
  {
    icon: "🤖",
    title: "Voice Agent 24/7",
    description: "Asistente de voz con memoria contextual que vende servicios y productos automaticamente.",
    features: [
      "Memoria entre sesiones (historial completo)",
      "Automejora continua (Evolution Engine)",
      "Multi-tenant (se adapta por cliente)",
      "WebSocket streaming en tiempo real",
      "Integración con Telegram, Web, API",
    ],
    price: "$199/mes",
  },
];

const plans = [
  {
    name: "Starter",
    price: "$0",
    desc: "Prueba el poder de la IA",
    features: ["1 agente de voz", "100 requests/día", "Voz estándar", "Chat básico", "Sin memoria"],
  },
  {
    name: "Pro",
    price: "$299",
    desc: "Para marcas en crecimiento",
    features: ["3 agentes", "10K requests/día", "Clonación de voz", "Memoria contextual", "Automejora básica"],
    popular: true,
  },
  {
    name: "Enterprise",
    price: "$999",
    desc: "Solución completa",
    features: [
      "Agentes ilimitados",
      "Requests ilimitados",
      "Voz + Imagen clonadas",
      "Memoria + RAG por tenant",
      "Evolution Engine completo",
      "On-premise disponible",
    ],
  },
];

export default function Home() {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouse = (e: MouseEvent) => {
      setMousePos({ x: e.clientX / window.innerWidth, y: e.clientY / window.innerHeight });
    };
    window.addEventListener("mousemove", handleMouse);
    return () => window.removeEventListener("mousemove", handleMouse);
  }, []);

  return (
    <>
      <Hero3D />

      <style jsx global>{`
        .fade-in {
          opacity: 0;
          transform: translateY(24px);
          transition: all 0.8s cubic-bezier(.25,.46,.45,.94);
        }
        .fade-in.visible {
          opacity: 1;
          transform: translateY(0);
        }
        section {
          position: relative;
          z-index: 1;
          padding: 6rem 2rem;
        }
        .container {
          max-width: 1200px;
          margin: 0 auto;
          position: relative;
          z-index: 1;
        }
        .section-tag {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.35rem 1.1rem;
          background: rgba(139,92,246,0.08);
          border: 1px solid rgba(139,92,246,0.2);
          border-radius: 50px;
          font-size: 0.75rem;
          color: #c4b5fd;
          margin-bottom: 1rem;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          font-weight: 600;
        }
        .section-title {
          font-family: 'Outfit', sans-serif;
          font-size: clamp(2.2rem, 4.5vw, 3.2rem);
          font-weight: 600;
          margin-bottom: 1rem;
          line-height: 1.15;
          letter-spacing: -0.02em;
        }
        .section-sub {
          color: rgba(255,255,255,0.45);
          font-size: 1.1rem;
          max-width: 600px;
          margin-bottom: 3.5rem;
          font-weight: 300;
          line-height: 1.7;
        }
        .grid-3 {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
        }
        .grid-4 {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
          gap: 1.5rem;
        }
        .btn {
          padding: 0.75rem 1.75rem;
          border-radius: 50px;
          border: none;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.4s cubic-bezier(.25,.46,.45,.94);
          text-decoration: none;
          display: inline-block;
          font-size: 0.9rem;
        }
        .btn-primary {
          background: var(--gradient-primary);
          color: #000;
        }
        .btn-primary:hover {
          transform: translateY(-3px);
          box-shadow: 0 12px 35px rgba(139,92,246,0.25);
        }
        .btn-outline {
          background: transparent;
          border: 1px solid rgba(139,92,246,0.3);
          color: #c4b5fd;
        }
        .btn-outline:hover {
          background: rgba(139,92,246,0.08);
          border-color: #8b5cf6;
        }
        .hero-section {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 8rem 2rem 4rem;
        }
        .hero-section h1 {
          font-family: 'Outfit', sans-serif;
          font-size: clamp(2.8rem, 6vw, 5rem);
          font-weight: 700;
          line-height: 1.08;
          margin-bottom: 1rem;
        }
        @media (max-width: 768px) {
          section { padding: 4rem 1.5rem; }
        }
      `}</style>

      {/* Hero */}
      <section className="hero-section">
        <div className="container">
          <div className="section-tag">🎯 IA para tu negocio</div>
          <h1>
            Tu <span className="gradient-text">gemelo digital</span>
            <br />
            vende por ti 24/7
          </h1>
          <p className="section-sub" style={{ maxWidth: "640px", margin: "1.5rem auto 2.5rem", textAlign: "center" }}>
            Clonación de voz e imagen con IA. Agentes con memoria que aprenden y mejoran solos.
            Tu marca siempre activa, siempre vendiendo.
          </p>
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
            <a href="#services" className="btn btn-primary">Ver Servicios</a>
            <a href="#pricing" className="btn btn-outline">Ver Precios</a>
          </div>

          <div className="grid-4" style={{ marginTop: "4rem" }}>
            {stats.map((s) => (
              <div key={s.label} style={{ textAlign: "center", padding: "1.5rem" }}>
                <div className="gradient-text" style={{ fontSize: "2.2rem", fontWeight: 700, fontFamily: "'Outfit', sans-serif" }}>
                  {s.value}
                </div>
                <div style={{ color: "rgba(255,255,255,0.45)", fontSize: "0.85rem", fontWeight: 300, marginTop: "0.3rem" }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Voice Demo - a live demo section showing the voice agent */}
      <section style={{ background: "rgba(139,92,246,0.02)" }} id="demo">
        <div className="container">
          <div className="section-tag">🔊 Demo en vivo</div>
          <h2 className="section-title">
            Escucha a <span className="gradient-text">Sona</span> en acción
          </h2>
          <p className="section-sub">
            Prueba el voice agent desde el boton flotante abajo a la derecha. {">"}
            Habla con el asistente, haz preguntas sobre servicios, precios, o contratación.
          </p>
          <div
            style={{
              background: "rgba(255,255,255,0.03)",
              borderRadius: "20px",
              border: "1px solid rgba(255,255,255,0.06)",
              padding: "3rem",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🎤</div>
            <h3 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.4rem", fontWeight: 600, marginBottom: "1rem" }}>
              Presiona el boton morado <span className="gradient-text">Sona</span>
            </h3>
            <p style={{ color: "rgba(255,255,255,0.45)", maxWidth: "500px", margin: "0 auto", lineHeight: 1.7 }}>
              El voice agent aparece en todas las páginas. Tiene memoria, entiende contexto,
              y puede ayudarte a contratar cualquier servicio.
            </p>
          </div>
        </div>
      </section>

      {/* Services */}
      <section id="services">
        <div className="container">
          <div className="section-tag">🚀 Servicios</div>
          <h2 className="section-title">
            Todo lo que necesitas para tu <span className="gradient-text">gemelo digital</span>
          </h2>
          <p className="section-sub">
            Desde clonación de voz hasta agentes con memoria y automejora. Tu negocio escala solo.
          </p>
          <div className="grid-3">
            {services.map((s) => (
              <ServiceCard key={s.title} {...s} />
            ))}
          </div>
        </div>
      </section>

      {/* Voice Agent feature details */}
      <section style={{ background: "rgba(139,92,246,0.02)" }}>
        <div className="container">
          <div className="section-tag">🧠 Memoria + Automejora</div>
          <h2 className="section-title">
            Tu agente <span className="gradient-text">recuerda todo</span> y mejora solo
          </h2>
          <p className="section-sub">
            Cada interacción queda guardada. El agente aprende de cada conversación y optimiza sus respuestas.
          </p>
          <div className="grid-3">
            {[
              {
                icon: "💾",
                title: "Memoria Persistente",
                desc: "Cada conversación se guarda en Hasura. El agente recuerda quien eres, que pediste y tus preferencias entre sesiones.",
              },
              {
                icon: "🔄",
                title: "Automejora Continua",
                desc: "El Evolution Engine evalúa cada interacción. Las respuestas exitosas se refuerzan, las fallidas se corrigen.",
              },
              {
                icon: "👥",
                title: "Multi-Tenant",
                desc: "Cada cliente tiene su propio agente con personalidad, tono y conocimiento adaptado. Se detecta automáticamente por dominio.",
              },
              {
                icon: "🎯",
                title: "Ventas 24/7",
                desc: "El agente califica leads, responde preguntas de precios, ofrece demos y cierra ventas sin intervención humana.",
              },
              {
                icon: "📊",
                title: "Analítica en Tiempo Real",
                desc: "Dashboard con métricas de conversación, tasa de conversión, satisfacción y áreas de mejora.",
              },
              {
                icon: "🔌",
                title: "Integración Total",
                desc: "WebSocket, REST API, Telegram, WhatsApp, Web. Un solo backend para todos los canales.",
              },
            ].map((f) => (
              <div
                key={f.title}
                className="card"
                style={{
                  background: "rgba(255,255,255,0.03)",
                  borderRadius: "20px",
                  border: "1px solid rgba(255,255,255,0.06)",
                  padding: "2rem",
                }}
              >
                <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>{f.icon}</div>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "0.5rem", fontFamily: "'Outfit', sans-serif" }}>
                  {f.title}
                </h3>
                <p style={{ color: "rgba(255,255,255,0.45)", fontSize: "0.875rem", lineHeight: 1.7, fontWeight: 300 }}>
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing">
        <div className="container">
          <div className="section-tag">💰 Precios</div>
          <h2 className="section-title">
            Planes para cada <span className="gradient-text">etapa</span>
          </h2>
          <p className="section-sub">
            Desde probar hasta escalar. Todos los planes incluyen actualizaciones gratuitas.
          </p>
          <div className="grid-3">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className="card"
                style={{
                  background: plan.popular ? "rgba(139,92,246,0.08)" : "rgba(255,255,255,0.03)",
                  borderRadius: "20px",
                  border: plan.popular ? "1px solid rgba(139,92,246,0.3)" : "1px solid rgba(255,255,255,0.06)",
                  padding: "2.5rem 2rem",
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                {plan.popular && (
                  <div
                    style={{
                      position: "absolute",
                      top: "1rem",
                      right: "-2rem",
                      background: "var(--gradient-primary)",
                      color: "#000",
                      padding: "0.25rem 3rem",
                      fontSize: "0.75rem",
                      fontWeight: 700,
                      transform: "rotate(45deg)",
                    }}
                  >
                    POPULAR
                  </div>
                )}
                <h3 style={{ fontSize: "1.3rem", fontWeight: 600, fontFamily: "'Outfit', sans-serif" }}>{plan.name}</h3>
                <p style={{ color: "rgba(255,255,255,0.45)", fontSize: "0.85rem", margin: "0.5rem 0 1rem" }}>{plan.desc}</p>
                <div className="gradient-text" style={{ fontSize: "2.5rem", fontWeight: 600, fontFamily: "'Outfit', sans-serif" }}>
                  {plan.price}
                  <span style={{ fontSize: "1rem", color: "rgba(255,255,255,0.45)", fontWeight: 300, marginLeft: "0.3rem" }}>/mes</span>
                </div>
                <ul style={{ marginTop: "1.5rem", listStyle: "none", padding: 0 }}>
                  {plan.features.map((f) => (
                    <li key={f} style={{ padding: "0.4rem 0", fontSize: "0.875rem", color: "rgba(255,255,255,0.45)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <span style={{ color: "#34d399" }}>✓</span> {f}
                    </li>
                  ))}
                </ul>
                <a
                  href="/contact"
                  className={`btn ${plan.popular ? "btn-primary" : "btn-outline"}`}
                  style={{ marginTop: "1.5rem", width: "100%", textAlign: "center" }}
                >
                  {plan.name === "Starter" ? "Empezar Gratis" : "Contratar"}
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section" style={{ textAlign: "center", padding: "8rem 2rem" }}>
        <div className="container">
          <h2 className="section-title" style={{ maxWidth: "700px", margin: "0 auto 1rem" }}>
            ¿Listo para tu <span className="gradient-text">gemelo digital</span>?
          </h2>
          <p className="section-sub" style={{ textAlign: "center", margin: "0 auto 2.5rem" }}>
            Agenda una llamada con nuestro equipo. Te mostramos cómo funciona en 15 minutos.
          </p>
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
            <a href="/contact" className="btn btn-primary">Agendar Demo</a>
            <a
              href="#"
              className="btn btn-outline"
              onClick={(e) => {
                e.preventDefault();
                const fab = document.querySelector(".voice-fab") as HTMLElement;
                if (fab) fab.click();
              }}
            >
              🎤 Hablar con Sona ahora
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer
        style={{
          borderTop: "1px solid rgba(255,255,255,0.06)",
          padding: "3rem 2rem",
          textAlign: "center",
          position: "relative",
          zIndex: 1,
        }}
      >
        <div className="container">
          <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.3rem", fontWeight: 700, marginBottom: "0.5rem" }}>
            <span className="gradient-text">Sonora</span> Digital Corp
          </div>
          <p style={{ color: "rgba(255,255,255,0.3)", fontSize: "0.85rem", fontWeight: 300 }}>
            Inteligencia Artificial para tu Negocio &mdash; Hermosillo, Sonora, México
          </p>
          <p style={{ color: "rgba(255,255,255,0.2)", fontSize: "0.75rem", fontWeight: 300, marginTop: "1rem" }}>
            &copy; {new Date().getFullYear()} Sonora Digital Corp. Todos los derechos reservados.
          </p>
        </div>
      </footer>
    </>
  );
}
