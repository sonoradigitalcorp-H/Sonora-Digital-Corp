"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { LogIn, Mail, Lock, ArrowRight } from "lucide-react";

const API = "https://abe.sonoradigitalcorp.com/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "error" | "success">("idle");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("loading");
    try {
      const res = await fetch(`${API}/auth/login`, {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (data.token) {
        localStorage.setItem("token", data.token);
        window.location.href = "/dashboard";
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  };

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center px-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-8 max-w-md w-full">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#FF6B35] to-[#00ccff] flex items-center justify-center text-black font-bold mx-auto mb-4">SD</div>
          <h1 className="text-2xl font-bold">Iniciar sesión</h1>
          <p className="text-sm text-gray-400 mt-1">Accede a tu panel de servicios</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm text-gray-400 block mb-1">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-[#FF6B35]"
                placeholder="tu@email.com" required />
            </div>
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Contraseña</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input type="password" value={password} onChange={e => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-[#FF6B35]"
                placeholder="••••••••" required />
            </div>
          </div>
          {status === "error" && <p className="text-sm text-red-400">Credenciales inválidas</p>}
          <button type="submit" disabled={status === "loading"}
            className="w-full py-3 rounded-xl font-semibold bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black hover:scale-[1.02] transition-all disabled:opacity-50 flex items-center justify-center gap-2">
            {status === "loading" ? "Entrando..." : "Entrar"}
            <LogIn className="w-4 h-4" />
          </button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-6">
          ¿No tienes cuenta? <a href="/signup" className="text-[#FF6B35] hover:underline">Crear cuenta</a>
        </p>
      </motion.div>
    </div>
  );
}
