import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SDC Control Center",
  description: "Agent Operating System — Dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className="dark">
      <body className="bg-gray-950 text-gray-100 antialiased">{children}</body>
    </html>
  );
}
