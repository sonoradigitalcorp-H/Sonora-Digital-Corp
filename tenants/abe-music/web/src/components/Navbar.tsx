"use client";

import { useState } from "react";
import { Menu, X } from "lucide-react";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  return (
    <nav className="fixed top-0 w-full z-50 backdrop-blur-xl bg-black/60 border-b border-gold/10">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <a href="/" className="flex items-center gap-3">
          <img src="/images/logo/abe-logo-1.webp" alt="ABE Music" className="h-8 w-8 rounded-full object-cover" />
          <span className="font-display text-xl font-medium text-gold">ABE<span className="text-foreground"> Music</span></span>
        </a>
        <div className="hidden md:flex items-center gap-6 text-sm">
          <a href="/#beneficios" className="text-muted-foreground hover:text-gold transition">Beneficios</a>
          <a href="/#artistas" className="text-muted-foreground hover:text-gold transition">Artistas</a>
          <a href="/#servicios" className="text-muted-foreground hover:text-gold transition">Servicios</a>
          <a href="https://t.me/abeassistant_bot" target="_blank" className="text-muted-foreground hover:text-gold transition">Bot</a>
          <a href="/signup"
            className="px-4 py-2 rounded-full bg-gradient-gold text-black font-semibold text-sm hover:opacity-90 transition-all">
            Comenzar
          </a>
        </div>
        <button className="md:hidden text-muted-foreground" onClick={() => setOpen(!open)}>
          {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>
      {open && (
        <div className="md:hidden glass border-t border-white/10 px-4 py-4 flex flex-col gap-3 text-sm">
          <a href="/#beneficios" className="text-muted-foreground" onClick={() => setOpen(false)}>Beneficios</a>
          <a href="/#artistas" className="text-muted-foreground" onClick={() => setOpen(false)}>Artistas</a>
          <a href="/#servicios" className="text-muted-foreground" onClick={() => setOpen(false)}>Servicios</a>
          <a href="https://t.me/abeassistant_bot" target="_blank" className="text-muted-foreground">Bot</a>
          <a href="/signup" className="px-4 py-2 rounded-full bg-gradient-gold text-black font-semibold text-sm text-center">Comenzar</a>
        </div>
      )}
    </nav>
  );
}
