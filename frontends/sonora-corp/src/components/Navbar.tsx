"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";

const links = [
  { href: "/", label: "Inicio" },
  { href: "/services/voice-clone", label: "Clonación de Voz" },
  { href: "/services/image-clone", label: "Clonación de Imagen" },
  { href: "/services/voice-agent", label: "Voice Agent" },
  { href: "/pricing", label: "Precios" },
  { href: "/contact", label: "Contacto" },
];

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav
      style={{
        position: "fixed",
        top: 0,
        width: "100%",
        zIndex: 100,
        background: "rgba(10,10,15,0.75)",
        backdropFilter: "blur(32px)",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        padding: "1rem 2rem",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      <Link href="/" style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.3rem", fontWeight: 700, color: "#f0f0f0", textDecoration: "none", letterSpacing: "-0.02em" }}>
        <span className="gradient-text">Sonora</span> Corp
      </Link>

      <div style={{ display: "flex", gap: "2rem", alignItems: "center" }}>
        {links.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            style={{
              color: "rgba(255,255,255,0.45)",
              textDecoration: "none",
              fontSize: "0.875rem",
              fontWeight: 400,
              transition: "color 0.3s",
              letterSpacing: "0.02em",
              display: "none",
            }}
            className="nav-link"
            onMouseEnter={(e) => (e.currentTarget.style.color = "#c4b5fd")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "rgba(255,255,255,0.45)")}
          >
            {l.label}
          </Link>
        ))}
        <Link
          href="/contact"
          style={{
            padding: "0.6rem 1.5rem",
            borderRadius: "50px",
            border: "none",
            fontWeight: 600,
            cursor: "pointer",
            fontSize: "0.85rem",
            background: "var(--gradient-primary)",
            color: "#000",
            textDecoration: "none",
            transition: "all 0.3s",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "translateY(-2px)";
            e.currentTarget.style.boxShadow = "0 8px 25px rgba(139,92,246,0.3)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "translateY(0)";
            e.currentTarget.style.boxShadow = "none";
          }}
        >
          Comenzar
        </Link>
      </div>

      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        style={{ background: "none", border: "none", color: "#f0f0f0", cursor: "pointer", display: "none" }}
        className="mobile-menu-btn"
      >
        {mobileOpen ? <X size={24} /> : <Menu size={24} />}
      </button>
    </nav>
  );
}
