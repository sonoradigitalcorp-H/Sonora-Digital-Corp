"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { UserPlus, Mail, Lock, User, Building, Check, ArrowRight, Sparkles } from "lucide-react";

const API = "https://abe.sonoradigitalcorp.com/api";

export default function SignupPage() {
  const [step, setStep] = useState(0);
  const [plans, setPlans] = useState<Record<string, any>>({});
  const [form, setForm] = useState({ name: "", email: "", password: "", company: "", plan: "starter" });
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
      if (data.status === "ok") {
        setStatus("success");
        setTimeout(() => window.location.href = `/login?registered=true`, 2000);
      } else {
        setStatus("error");
        setErrorMsg(data.detail || "Error al crear cuenta");
      }
    } catch {
      setStatus("error");
      setErrorMsg("Error de conexión");
    }
  };

  if (status === "success") {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center px-4">
        <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="text-center">
          <div className="w-16 h-16 rounded-full bg-[#00ff88]/20 flex items-center justify-center mx-auto mb-4">
            <Check className="w-8 h-8 text-[#00ff88]" />
          </div>
          <h2 className="text-2xl font-bold mb-2">Cuenta creada</h2>
          <p className="text-gray-400">Redirigiendo al inicio de sesión...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center px-4 py-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-8 max-w-lg w-full">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#FF6B35] to-[#00ccff] flex items-center justify-center text-black font-bold mx-auto mb-4">
            <Sparkles className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold">Crear cuenta</h1>
          <p className="text-sm text-gray-400 mt-1">Empieza con tu plan {form.plan === "starter" ? "gratis" : "profesional"}</p>
        </div>

        <div className="flex gap-2 mb-8 justify-center">
          {["starter", "pro", "enterprise"].map(p => (
            <button key={p} onClick={() => setForm({...form, plan: p})}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                form.plan === p
                  ? "bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black"
                  : "glass text-gray-400 hover:text-white"
              }`}>
              {plans[p]?.name || p}
            </button>
          ))}
        </div>

        <form onSubmit={e => { e.preventDefault(); handleSignup(); }} className="space-y-4">
          <div>
            <label className="text-sm text-gray-400 block mb-1">Nombre</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-[#FF6B35]"
                placeholder="Tu nombre" required />
            </div>
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})}
                className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-[#FF6B35]"
                placeholder="tu@email.com" required />
            </div>
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Contraseña</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})}
                className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-[#FF6B35]"
                placeholder="••••••••" required minLength={6} />
            </div>
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Empresa (opcional)</label>
            <div className="relative">
              <Building className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input value={form.company} onChange={e => setForm({...form, company: e.target.value})}
                className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-[#FF6B35]"
                placeholder="Tu empresa" />
            </div>
          </div>

          {status === "error" && <p className="text-sm text-red-400">{errorMsg}</p>}

          <button type="submit" disabled={status === "loading"}
            className="w-full py-3 rounded-xl font-semibold bg-gradient-to-r from-[#FF6B35] to-[#00ccff] text-black hover:scale-[1.02] transition-all disabled:opacity-50 flex items-center justify-center gap-2">
            {status === "loading" ? "Creando cuenta..." : "Crear cuenta gratis"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {form.plan !== "starter" && (
          <div className="mt-6 p-4 rounded-xl glass">
            <p className="text-xs text-gray-400 mb-2">Plan {plans[form.plan]?.name} — ${plans[form.plan]?.price}/mes</p>
            <div className="flex flex-wrap gap-2">
              {plans[form.plan]?.services?.map((s: any) => (
                <span key={s.id} className="text-xs px-2 py-1 rounded-full bg-white/5 text-gray-300">{s.name}</span>
              ))}
            </div>
          </div>
        )}

        <p className="text-center text-sm text-gray-500 mt-6">
          ¿Ya tienes cuenta? <a href="/login" className="text-[#FF6B35] hover:underline">Iniciar sesión</a>
        </p>
      </motion.div>
    </div>
  );
}
