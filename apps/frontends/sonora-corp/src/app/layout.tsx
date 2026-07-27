import type { Metadata } from "next";
import "./globals.css";
import VoiceWidget from "@/components/VoiceWidget";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Sonora Digital Corp — Inteligencia Artificial para tu Negocio",
  description:
    "Clonación de voz e imagen, asistentes de IA 24/7, memoria contextual y mejora continua. Sonora Digital Corp.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className="dark">
      <body className="antialiased">
        <Navbar />
        {children}
        <VoiceWidget tenant="sonora" />
      </body>
    </html>
  );
}
