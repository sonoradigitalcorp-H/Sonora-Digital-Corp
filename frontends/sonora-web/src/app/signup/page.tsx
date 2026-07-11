"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { UserPlus, Mail, Lock, User, Sparkles, ArrowRight } from "lucide-react";

const API = "https://abe.sonoradigitalcorp.com/api";

export default function SignupPage() {
  const [plans, setPlans] = useState<Record<string, any>>({});
  const [form, setForm] = useState({ name: "", email: "", password: "", plan: "starter" });
  const [status, setStatus] = useState<"idle" | "loading" | "error" | "success">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    fetch(`${API}/plans`).then(r => r.json()).then(d => setPlans(d.plans || {})).catch(() => {});
  }, []);

  const handleSignup = async () => {
    setStatus("loading");
    setErrorMsg("");
    try {
      const res = await fetch(`${API}/auth/signup`, {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ email: form.email, password: form.password, name: form.name, plan: form.plan }),
      });
      const data = await res.json();
      if (data.token) {
        localStorage.setItem("token", data.token);
        window.location.href = "/onboarding";
      } else {
        setStatus("error");
        setErrorMsg(data.detail || "Error al crear cuenta");
      }
    } catch {
      setStatus("error");
      setErrorMsg("Error de conexión");
    }
  };

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center px-4 py-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-8 max-w-md w-full">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#FF6B35] to-[#00ccff] flex items-center justify-center text-black font-bold mx-auto mb-4">
            <Sparkles className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold">Crear cuenta</h1>
          <p className="text-sm text-gray-400 mt-1">Empieza con {form.plan === "starter" ? "el plan gratuito" : "tu plan profesional"}</p>
        </div>

        <div className="flex gap-2 mb-8 justify-center">
          {["starter", "pro", "enterprise"].map(p => (
            <button key={p} onClick={() => setForm({...form, plan: p})}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                form.plan === p ? "bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black" : "glass text-gray-400 hover:text-white"
              }`}>
              {plans[p]?.name || p}
            </button>
          ))}
        </div>

        <form onSubmit={e => { e.preventDefault(); handleSignup(); }} className="space-y-4">
          <div>
            <label className="text-sm text-gray-400 block mb-1">Nombre</label>
            <input value={form.name} onChange={e => setForm({...form, name: e.target.value})}
              className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-[#FF6B35]"
              placeholder="Tu nombre" required />
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Email</label>
            <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})}
              className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-[#FF6B35]"
              placeholder="tu@email.com" required />
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Contraseña</label>
            <input type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})}
              className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-[#FF6B35]"
              placeholder="••••••••" required minLength={6} />
          </div>
          {status === "error" && <p className="text-sm text-red-400">{errorMsg}</p>}
          <button type="submit" disabled={status === "loading"}
            className="w-full py-3 rounded-xl font-semibold bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black hover:scale-[1.02] transition-all disabled:opacity-50 flex items-center justify-center gap-2">
            {status === "loading" ? "Creando cuenta..." : "Comenzar ahora"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      </motion.div>
    </div>
  );
}
