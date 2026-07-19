"""Generador de reportes HTML con FOMO + Risk Management Plan + Pricing."""
from datetime import datetime, timedelta
import json

FOMO_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Diagnóstico de Ciberseguridad — {domain}</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*{{font-family:'Inter',sans-serif}}
body{{background:#0a0a0a;color:#c9d1d9}}
.grade-{grade} {{color:{grade_color}}}
.fomo-timer{{background:linear-gradient(135deg,rgba(239,68,68,0.1),rgba(239,68,68,0.02));border:1px solid rgba(239,68,68,0.3);border-radius:16px;padding:24px;text-align:center;animation:pulse-border 2s ease-in-out infinite}}
@keyframes pulse-border{{0%,100%{{border-color:rgba(239,68,68,0.3)}}50%{{border-color:rgba(239,68,68,0.6)}}}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
.fade-in{{animation:fadeIn 0.5s ease forwards;opacity:0}}
.check-ok{{border-left:3px solid #22c55e}}
.check-warning{{border-left:3px solid #f59e0b}}
.check-error{{border-left:3px solid #ef4444}}
</style>
</head>
<body class="antialiased">
<div class="max-w-4xl mx-auto px-6 py-12">

  <!-- FOMO Banner -->
  <div class="fomo-timer fade-in mb-8">
    <div class="text-2xl mb-2">⏳ <span id="countdown" class="font-bold text-[#ef4444]"></span></div>
    <p class="text-sm text-white/60">Esta evaluación gratuita expira pronto. Solo {slots} cupos disponibles esta semana.</p>
  </div>

  <!-- Header -->
  <div class="text-center mb-8 fade-in">
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#7c5cfc]/20 bg-[#7c5cfc]/5 text-[#7c5cfc] text-xs font-medium tracking-wider mb-4">
      🛡️ Diagnóstico Express
    </div>
    <h1 class="text-4xl md:text-5xl font-black tracking-tight mb-2">
      <span class="bg-gradient-to-r from-white via-[#7c5cfc] to-[#c8a87c] bg-clip-text text-transparent">Ciberseguridad</span>
    </h1>
    <p class="text-lg text-white/40 mb-1">{domain}</p>
    <p class="text-sm text-white/20">Escaneado: {scanned_at} · Validez: {expires_at}</p>
  </div>

  <!-- Score -->
  <div class="text-center mb-8 fade-in" style="animation-delay:0.1s">
    <div class="inline-flex items-center justify-center w-36 h-36 rounded-full border-4 border-[#30363d] mb-3" style="border-top-color:{grade_color}">
      <div>
        <div class="text-4xl font-black grade-{grade}">{grade}</div>
        <div class="text-xs text-white/30">{score}/100</div>
      </div>
    </div>
    <div class="flex justify-center gap-6 text-sm">
      <div><span class="text-[#22c55e] font-bold">{ok_count}</span> <span class="text-white/30">seguras</span></div>
      <div><span class="text-[#f59e0b] font-bold">{warn_count}</span> <span class="text-white/30">advertencias</span></div>
      <div><span class="text-[#ef4444] font-bold">{err_count}</span> <span class="text-white/30">críticas</span></div>
    </div>
  </div>

  <!-- Risk Level -->
  <div class="text-center mb-8 fade-in" style="animation-delay:0.15s">
    <div class="inline-block px-6 py-3 rounded-2xl {risk_bg}">
      <span class="text-sm font-semibold">{risk_label}</span>
      <p class="text-xs text-white/50 mt-1">{risk_desc}</p>
    </div>
  </div>

  <!-- Checks -->
  <div class="space-y-2 mb-8">
    {checks_html}
  </div>

  <!-- CTA -->
  <div class="text-center fade-in" style="animation-delay:0.5s">
    <div class="inline-block p-8 rounded-2xl bg-white/[0.02] border border-white/[0.06] max-w-lg">
      <h3 class="text-lg font-bold mb-2">¿Quieres proteger tu empresa?</h3>
      <p class="text-sm text-white/40 mb-4">Solicita un plan de remediación personalizado con nuestro equipo de ciberseguridad.</p>
      <a href="https://wa.me/5216625383272?text=Quiero%20el%20plan%20de%20seguridad%20para%20{domain}" 
         class="inline-block px-8 py-3.5 rounded-xl bg-[#22c55e] hover:bg-[#16a34a] transition-all font-semibold text-sm">
        💬 Contactar por WhatsApp
      </a>
    </div>
  </div>

  <!-- Footer -->
  <div class="mt-12 text-center text-xs text-white/20 border-t border-white/[0.06] pt-6">
    <p>Generado por <strong>Sonora Digital Corp</strong> — Sistema de Diagnóstico Automatizado Mystic</p>
    <p class="mt-1">ID: {report_id} · {scanned_at}</p>
  </div>
</div>

<script>
(function(){{
  var target = new Date("{expires_iso}").getTime();
  function update() {{
    var now = new Date().getTime();
    var diff = target - now;
    if (diff <= 0) {{ document.getElementById('countdown').innerHTML = '🕐 ¡Expirado!'; return; }}
    var h = Math.floor(diff / (1000*60*60));
    var m = Math.floor((diff % (1000*60*60)) / (1000*60));
    var s = Math.floor((diff % (1000*60)) / 1000);
    document.getElementById('countdown').innerHTML = h + 'h ' + m + 'm ' + s + 's';
  }}
  setInterval(update, 1000); update();
}})();
</script>
</body>
</html>"""


def risk_config(score: int):
    if score >= 85: return ("bg-[#22c55e]/10 border border-[#22c55e]/20", "✅ Bajo Riesgo", "Tu dominio está bien protegido. Mantenimiento preventivo recomendado.")
    if score >= 65: return ("bg-[#7c5cfc]/10 border border-[#7c5cfc]/20", "🔒 Riesgo Moderado", "Algunas áreas requieren atención. Revisión recomendada.")
    if score >= 45: return ("bg-[#f59e0b]/10 border border-[#f59e0b]/20", "⚠️ Riesgo Alto", "Vulnerabilidades importantes detectadas. Se recomienda acción inmediata.")
    return ("bg-[#ef4444]/10 border border-[#ef4444]/20", "🚨 Riesgo Crítico", "Múltiples vulnerabilidades críticas. Se requiere intervención urgente.")


def generate_html(result: dict) -> str:
    domain = result["domain"]
    score = result["score"]
    grade = result["grade"]
    s = result["summary"]

    grade_colors = {"A": "#22c55e", "B": "#7c5cfc", "C": "#f59e0b", "D": "#ef4444", "F": "#dc2626"}

    now = datetime.now()
    expires = now + timedelta(hours=48)
    slots = "3" if score < 60 else "5" if score < 80 else "8"

    risk_bg, risk_label, risk_desc = risk_config(score)

    checks_html = ""
    for i, check in enumerate(result["checks"]):
        icon = {"ok": "✅", "warning": "⚠️", "error": "❌"}.get(check["status"], "❓")
        sev = {"critica": "🔴", "alta": "🟠", "media": "🟡"}.get(check["severity"], "⚪")
        status_color = "#22c55e" if check["status"] == "ok" else "#f59e0b" if check["status"] == "warning" else "#ef4444"
        checks_html += f"""
        <div class="check-{check['status']} p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] fade-in" style="animation-delay:{0.2 + i*0.04}s">
          <div class="flex items-start justify-between gap-3">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-0.5">
                <span class="text-sm font-semibold">{icon} {check['name']}</span>
                <span class="text-xs text-white/20">{sev} {check['severity']}</span>
              </div>
              <p class="text-xs text-white/40 mt-1">{check['detail']}</p>
            </div>
            <span class="text-xs font-semibold uppercase" style="color:{status_color}">{check['status']}</span>
          </div>
        </div>"""

    return FOMO_HTML.format(
        domain=domain, score=score, grade=grade,
        grade_color=grade_colors.get(grade, "#7c5cfc"),
        ok_count=s["ok"], warn_count=s["warning"], err_count=s["error"],
        risk_bg=risk_bg, risk_label=risk_label, risk_desc=risk_desc,
        checks_html=checks_html, slots=slots,
        scanned_at=now.strftime("%d/%m/%Y %H:%M"),
        expires_at=expires.strftime("%d/%m/%Y %H:%M"),
        expires_iso=expires.isoformat(),
        report_id=f"SDC-CYBER-{now.strftime('%Y%m%d%H%M%S')}",
    )


def generate_rmp(result: dict) -> str:
    """Risk Management Plan — documento post-auditoría para vender servicios."""
    from datetime import datetime
    now = datetime.now()
    domain = result["domain"]
    score = result["score"]
    grade = result["grade"]
    s = result["summary"]

    action_items = ""
    for c in result["checks"]:
        if c["status"] != "ok":
            priority = "🔴 Crítica" if c["severity"] == "critica" else "🟠 Alta" if c["severity"] == "alta" else "🟡 Media"
            days = "24h" if c["severity"] == "critica" else "7 días" if c["severity"] == "alta" else "30 días"
            effort = "2-4h" if c["severity"] == "critica" else "1-2h" if c["severity"] == "alta" else "30min"
            action_items += f"""
        <div class="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06]">
          <div class="flex items-start justify-between gap-3">
            <div>
              <span class="text-sm font-semibold">{priority}</span>
              <p class="text-sm text-white/80 mt-1">{c['name']}</p>
              <p class="text-xs text-white/40 mt-0.5">{c['detail']}</p>
            </div>
            <div class="text-right text-xs text-white/30 flex-shrink-0">
              <div>⏱ {effort}</div>
              <div>📅 {days}</div>
            </div>
          </div>
        </div>"""

    grade_color = "#22c55e" if grade in ("A", "B") else "#f59e0b" if grade == "C" else "#ef4444"
    rmp_id = f"SDC-RMP-{now.strftime('%Y%m%d%H%M%S')}"
    date_fmt = now.strftime('%d/%m/%Y')

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Plan de Gestión de Riesgos — {domain}</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');*{{font-family:'Inter',sans-serif}}body{{background:#0a0a0a;color:#c9d1d9}}</style>
</head>
<body class="antialiased">
<div class="max-w-4xl mx-auto px-6 py-12">

  <h1 class="text-3xl font-black mb-2">Plan de Gestión de Riesgos</h1>
  <p class="text-white/40 mb-8">{domain} · {date_fmt} · ID: {rmp_id}</p>

  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
    <div class="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] text-center">
      <div class="text-2xl font-black" style="color:{grade_color}">{grade}</div>
      <div class="text-xs text-white/30 mt-1">Calificacion</div>
    </div>
    <div class="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] text-center">
      <div class="text-2xl font-black">{score}/100</div>
      <div class="text-xs text-white/30 mt-1">Score</div>
    </div>
    <div class="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] text-center">
      <div class="text-2xl font-black text-[#ef4444]">{s['error']}</div>
      <div class="text-xs text-white/30 mt-1">Criticas</div>
    </div>
    <div class="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] text-center">
      <div class="text-2xl font-black text-[#22c55e]">{s['ok']}</div>
      <div class="text-xs text-white/30 mt-1">Seguras</div>
    </div>
  </div>

  <h2 class="text-xl font-bold mb-4">🔧 Plan de Acción (Priorizado)</h2>
  <div class="space-y-3 mb-8">{action_items}</div>

  <h2 class="text-xl font-bold mb-4">💰 Propuesta de Valor — Sonora Digital Corp</h2>
  <div class="grid md:grid-cols-3 gap-4 mb-8">
    <div class="p-5 rounded-xl bg-white/[0.02] border border-white/[0.06]">
      <h3 class="font-semibold mb-2">🔍 Diagnóstico Continuo</h3>
      <p class="text-xs text-white/40">Monitoreo semanal automatizado de tu dominio con alertas en tiempo real.</p>
    </div>
    <div class="p-5 rounded-xl bg-white/[0.02] border border-white/[0.06]">
      <h3 class="font-semibold mb-2">🛡️ Remediación</h3>
      <p class="text-xs text-white/40">Implementamos las correcciones por ti. DNS, SSL, headers, email security.</p>
    </div>
    <div class="p-5 rounded-xl bg-white/[0.02] border border-white/[0.06]">
      <h3 class="font-semibold mb-2">🤖 Agente IA 24/7</h3>
      <p class="text-xs text-white/40">Un agente de SDC monitorea y responde incidentes automáticamente.</p>
    </div>
  </div>

  <h2 class="text-xl font-bold mb-4">💵 Inversión</h2>
  <div class="grid md:grid-cols-3 gap-4 mb-8">
    <div class="p-5 rounded-xl border border-white/[0.06]">
      <h3 class="font-semibold">Starter</h3>
      <div class="text-2xl font-black mt-1">$299<span class="text-sm font-normal text-white/30">/mes</span></div>
      <ul class="text-xs text-white/50 mt-3 space-y-1">
        <li>✅ Diagnóstico mensual</li>
        <li>✅ 1 dominio</li>
        <li>✅ Reporte + Audio</li>
      </ul>
    </div>
    <div class="p-5 rounded-xl bg-[#7c5cfc]/10 border border-[#7c5cfc]/30">
      <div class="text-xs text-[#7c5cfc] font-bold mb-1">MÁS POPULAR</div>
      <h3 class="font-semibold">Pro</h3>
      <div class="text-2xl font-black mt-1">$499<span class="text-sm font-normal text-white/30">/mes</span></div>
      <ul class="text-xs text-white/50 mt-3 space-y-1">
        <li>✅ Diagnóstico semanal</li>
        <li>✅ Hasta 3 dominios</li>
        <li>✅ Agente IA + Alertas</li>
        <li>✅ Remediación incluida</li>
      </ul>
    </div>
    <div class="p-5 rounded-xl border border-white/[0.06]">
      <h3 class="font-semibold">Enterprise</h3>
      <div class="text-2xl font-black mt-1">$999<span class="text-sm font-normal text-white/30">/mes</span></div>
      <ul class="text-xs text-white/50 mt-3 space-y-1">
        <li>✅ Diagnóstico continuo</li>
        <li>✅ Dominios ilimitados</li>
        <li>✅ Agente dedicado 24/7</li>
        <li>✅ SLA 99.99%</li>
      </ul>
    </div>
  </div>

  <div class="text-center">
    <a href="https://wa.me/5216625383272?text=Quiero%20el%20plan%20{domain}" 
       class="inline-block px-8 py-3.5 rounded-xl bg-[#22c55e] hover:bg-[#16a34a] transition-all font-semibold text-sm">
      💬 Contratar Protección
    </a>
  </div>

  <div class="mt-8 text-center text-xs text-white/20 border-t border-white/[0.06] pt-4">
    Generado por Sonora Digital Corp · Sistema Mystic · {now.strftime('%Y-%m-%d %H:%M'):s}
  </div>
</div>
</body>
</html>"""


def generate_slides(result: dict) -> str:
    """Presentación reveal.js para mostrar en vivo."""
    from datetime import datetime
    now = datetime.now()
    domain = result["domain"]
    grade = result["grade"]
    score = result["score"]
    s = result["summary"]

    checks_rows = ""
    for c in result["checks"]:
        icon = {"ok": "✅", "warning": "⚠️", "error": "❌"}.get(c["status"], "❓")
        color = "#22c55e" if c["status"] == "ok" else "#f59e0b" if c["status"] == "warning" else "#ef4444"
        checks_rows += f"<tr><td style='padding:8px;border-bottom:1px solid #30363d;font-size:0.7em'>{icon}</td><td style='padding:8px;border-bottom:1px solid #30363d;font-size:0.7em'>{c['name']}</td><td style='padding:8px;border-bottom:1px solid #30363d;font-size:0.7em;color:{color}'>{c['status'].upper()}</td></tr>"

    return f"""<!DOCTYPE html><html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Cyber Diagnosis — {domain}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/theme/dracula.css">
</head><body><div class="reveal"><div class="slides">

<section data-background="#0a0a0a">
  <div style="font-size:4em;margin-bottom:20px">🛡️</div>
  <h2 style="background:linear-gradient(135deg,#fff 30%,#7c5cfc 70%,#c8a87c);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2.2em">Diagnóstico de Ciberseguridad</h2>
  <p style="color:#8b949e;font-size:1.1em">{domain}</p>
  <p style="color:#484f58;font-size:0.7em;margin-top:30px">Presentado por Sonora Digital Corp</p>
</section>

<section data-background="#0a0a0a">
  <h3>Resumen Ejecutivo</h3>
  <div style="display:flex;justify-content:center;gap:30px;margin:20px 0">
    <div><div style="font-size:3em;font-weight:900;color:#22c55e">{s['ok']}</div><div style="color:#8b949e;font-size:0.7em">Seguro</div></div>
    <div><div style="font-size:3em;font-weight:900;color:#f59e0b">{s['warning']}</div><div style="color:#8b949e;font-size:0.7em">Advertencia</div></div>
    <div><div style="font-size:3em;font-weight:900;color:#ef4444">{s['error']}</div><div style="color:#8b949e;font-size:0.7em">Crítico</div></div>
  </div>
  <p style="font-size:1.2em;margin-top:20px">Score: <strong>{score}/100</strong> — Calificación: <strong style="font-size:2em">{grade}</strong></p>
</section>

<section data-background="#0a0a0a">
  <h3>Resultados</h3>
  <table style="width:100%;border-collapse:collapse;margin-top:15px">{checks_rows}</table>
</section>

<section data-background="#0a0a0a">
  <h3>¿Qué sigue?</h3>
  <ul style="list-style:none;font-size:0.8em;text-align:left;display:inline-block">
    <li style="margin:12px 0">📋 <strong>Plan de Riesgos personalizado</strong></li>
    <li style="margin:12px 0">🔧 <strong>Remediación completa</strong> (DNS, SSL, headers)</li>
    <li style="margin:12px 0">🤖 <strong>Agente IA 24/7</strong> monitoreando tu dominio</li>
    <li style="margin:12px 0">📊 <strong>Dashboard en vivo</strong> con alertas</li>
  </ul>
</section>

<section data-background="#0a0a0a">
  <h3>Sonora Digital Corp</h3>
  <p style="color:#8b949e;margin-bottom:15px">Tu socio de ciberseguridad</p>
  <p style="color:#7c5cfc;font-size:0.8em">https://sonoradigitalcorp.com</p>
  <p style="color:#22c55e;font-size:0.8em">WhatsApp: 5216625383272</p>
</section>

</div></div>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.js"></script>
<script>Reveal.initialize({{hash:true,controls:true,progress:true,center:true}});</script>
</body></html>"""
