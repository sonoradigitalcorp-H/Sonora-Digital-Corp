import type { Metadata } from "next";
import "./globals.css";
import MystikWidget from "@/components/MystikWidget";
import VoiceWidget from "@/components/VoiceWidget";

export const metadata: Metadata = {
  title: "ABE Music Group — Ecosistema Musical Inteligente",
  description: "ABE Music Group. Gestión de carrera, producción, distribución y ventas para artistas. Hub en Hermosillo.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className="dark">
      <body className="antialiased">
        {children}
        <MystikWidget />
        <VoiceWidget tenant="abe" />
      </body>
    </html>
  );
}
