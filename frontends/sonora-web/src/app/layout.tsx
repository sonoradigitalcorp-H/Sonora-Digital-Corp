import type { Metadata } from "next";
import "./globals.css";
import MystikWidget from "@/components/MystikWidget";

export const metadata: Metadata = {
  title: "ABE Music Group — Ecosistema Musical Inteligente",
  description: "Plataforma de inteligencia artificial para la industria musical. ABE Music Group, Mystik AI, generación de contenido.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className="dark">
      <body className="antialiased">
        {children}
        <MystikWidget />
      </body>
    </html>
  );
}
