import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sonora Digital Corp — Ecosistema AI",
  description: "Plataforma de inteligencia artificial para la industria musical y empresarial. ABE Music OS, Mystik AI, Content Studio y más.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className="dark">
      <body className="antialiased">{children}</body>
    </html>
  );
}
