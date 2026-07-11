"use client";

import { useState } from "react";
import { Menu, X } from "lucide-react";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  return (
    <nav className="fixed top-0 w-full z-50 backdrop-blur-xl bg-black/40 border-b border-white/5">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <a href="/" className="flex items-center gap-2">
          <span className="text-xl font-bold text-[#00ff88]">♫ ABE<span className="text-white"> Music</span></span>
        </a>
        <div className="hidden md:flex items-center gap-6 text-sm">
          <a href="/#artists" className="text-gray-400 hover:text-white transition">Artistas</a>
          <a href="/#services" className="text-gray-400 hover:text-white transition">Servicios</a>
          <a href="/pricing" className="text-gray-400 hover:text-white transition">Planes</a>
          <a href="/pwa" className="text-gray-400 hover:text-white transition">PWA</a>
          <span className="text-xs text-gray-600 border-l border-white/10 pl-6">Powered by SDC</span>
        </div>
        <button className="md:hidden text-gray-400" onClick={() => setOpen(!open)}>
          {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>
      {open && (
        <div className="md:hidden glass border-t border-white/10 px-4 py-4 flex flex-col gap-3 text-sm">
          <a href="/#artists" className="text-gray-400" onClick={() => setOpen(false)}>Artistas</a>
          <a href="/#services" className="text-gray-400" onClick={() => setOpen(false)}>Servicios</a>
          <a href="/pricing" className="text-gray-400" onClick={() => setOpen(false)}>Planes</a>
          <a href="/pwa" className="text-gray-400" onClick={() => setOpen(false)}>PWA</a>
        </div>
      )}
    </nav>
  );
}
