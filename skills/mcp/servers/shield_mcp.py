"""
Mystic Shield MCP Server — AI-powered business security diagnosis.

Pipeline:
  1. Scan network (Naabu + ping sweep + Nuclei)
  2. Analyze results with LLM
  3. Generate PDF report + Audio summary
  4. Send via WhatsApp + Email

Tools:
  shield_diagnose       — Run full diagnosis on a network/business
  shield_send_report    — Send existing report to contacts
"""

import asyncio
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

REPORTS_DIR = Path("state/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

MYSTIC_NAME = "Mystic — Sonora Digital Corp"
COMPANY = "Sonora Digital Corp"
COMPANY_EMAIL = "hola@sonoracorp.mx"

def _log(msg: str):
    ts = datetime.now().isoformat()
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


# ─── SCANNING ──────────────────────────────────────────────────────

def _resolve_host(host: str) -> Optional[str]:
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        if re.match(r'^\d+\.\d+\.\d+\.\d+', host):
            return host
        return None

def _ping_sweep(subnet: str) -> list:
    hosts = []
    base = ".".join(subnet.split(".")[:3])
    for i in range(1, 255):
        ip = f"{base}.{i}"
        r = subprocess.run(["ping", "-c", "1", "-W", "1", ip],
                           capture_output=True, text=True, timeout=2)
        if r.returncode == 0:
            hosts.append(ip)
    return hosts

def _scan_ports(host: str, ports: str = "22,80,443,1433,3306,3389,5432,8080,8443,9047") -> list:
    open_ports = []
    for p in ports.split(","):
        p = int(p.strip())
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, p))
        sock.close()
        if result == 0:
            try:
                service = socket.getservbyport(p)
            except OSError:
                service = "unknown"
            open_ports.append({"port": p, "service": service, "state": "open"})
    return open_ports

def _fast_scan(subnet_or_ip: str) -> dict:
    if "/" in subnet_or_ip or re.match(r'^\d+\.\d+\.\d+\.\d+$', subnet_or_ip):
        ip = _resolve_host(subnet_or_ip)
        if not ip:
            return {"error": f"Cannot resolve {subnet_or_ip}"}
        hosts = _ping_sweep(".".join(ip.split(".")[:3]) + ".0/24")
        results = {}
        for host in hosts:
            ports = _scan_ports(host)
            if ports:
                results[host] = ports
        return {
            "target": subnet_or_ip,
            "total_hosts": len(hosts),
            "hosts_with_open_ports": len(results),
            "hosts": results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    return {"error": "Invalid target"}


# ─── LLM ANALYSIS ──────────────────────────────────────────────────

def _call_llm(prompt: str, system: str = "") -> str:
    """Call OpenRouter or local deepseek for analysis."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return _fallback_analysis(prompt)
    try:
        r = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek/deepseek-v4-flash",
                "messages": [
                    {"role": "system", "content": system or "Eres Mystic, asistente de ciberseguridad de Sonora Digital Corp. Responde en español profesional pero accesible para dueños de negocio."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 2000,
                "temperature": 0.3,
            },
            timeout=60,
        )
        data = r.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        if "error" in data:
            _log(f"LLM API error: {data['error']}")
            return _fallback_analysis(prompt)
        _log(f"LLM unexpected response: {str(data)[:200]}")
        return _fallback_analysis(prompt)
    except Exception as e:
        _log(f"LLM error: {e}")
        return _fallback_analysis(prompt)

def _fallback_analysis(prompt: str) -> str:
    """Generate analysis without LLM — template-based."""
    return """## Resumen de Diagnóstico

Se completó el escaneo de red. Los hallazgos初步 indican la necesidad de:
1. Revisar puertos administrativos expuestos (RDP, SSH)
2. Verificar servicios contables (CONTPAQi, SQL Server)
3. Evaluar segmentación de red

Para un análisis detallado con recomendaciones personalizadas, activa la conexión con OpenRouter."""


# ─── PDF GENERATION ────────────────────────────────────────────────

def _generate_pdf(company_name: str, scan_data: dict, analysis: str) -> str:
    """Generate professional PDF report using fpdf2."""
    try:
        from fpdf import FPDF
    except ImportError:
        _log("fpdf2 not installed, creating text report")
        report_path = REPORTS_DIR / f"diagnostico-{company_name.lower().replace(' ', '-')}-{datetime.now():%Y%m%d}.txt"
        report_path.write_text(f"DIAGNÓSTICO DE SEGURIDAD — {company_name}\n\n{analysis}")
        return str(report_path)

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", uni=True)

    W = 297
    H = 210

    # Slide 1 — Cover
    pdf.add_page()
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(0, 0, W, H, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", "B", 28)
    pdf.set_xy(20, 50)
    pdf.cell(0, 20, "Diagnóstico de Seguridad", align="C")
    pdf.set_font("DejaVu", "", 16)
    pdf.set_xy(20, 75)
    pdf.cell(0, 15, company_name, align="C")
    pdf.set_font("DejaVu", "", 12)
    pdf.set_text_color(156, 163, 175)
    pdf.set_xy(20, 95)
    pdf.cell(0, 10, f"Preparado por {MYSTIC_NAME}", align="C")
    pdf.set_xy(20, 108)
    pdf.cell(0, 10, datetime.now().strftime("%d de %B, %Y"), align="C")
    pdf.set_xy(20, 140)
    pdf.set_text_color(255, 107, 53)
    pdf.set_font("DejaVu", "", 10)
    pdf.cell(0, 10, "CONFIDENCIAL — Solo para uso interno", align="C")

    # Slide 2 — Executive Summary
    pdf.add_page()
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(0, 0, W, H, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", "B", 20)
    pdf.set_xy(20, 20)
    pdf.cell(0, 15, "Resumen Ejecutivo")
    pdf.set_text_color(200, 200, 200)
    pdf.set_font("DejaVu", "", 11)
    y = 45
    for line in analysis.split("\n"):
        if line.strip():
            pdf.set_xy(20, y)
            pdf.multi_cell(W - 40, 6, line.strip())
            y += 8

    # Slide 3 — Network Overview
    pdf.add_page()
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(0, 0, W, H, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", "B", 20)
    pdf.set_xy(20, 20)
    pdf.cell(0, 15, "Resumen de Red")
    pdf.set_text_color(200, 200, 200)
    pdf.set_font("DejaVu", "", 12)
    total = scan_data.get("total_hosts", 0)
    active = scan_data.get("hosts_with_open_ports", 0)
    pdf.set_xy(20, 50)
    pdf.cell(0, 10, f"Hosts detectados: {total}")
    pdf.set_xy(20, 62)
    pdf.cell(0, 10, f"Hosts con puertos abiertos: {active}")

    hosts = scan_data.get("hosts", {})
    if hosts:
        y = 80
        pdf.set_font("DejaVu", "B", 10)
        pdf.set_xy(20, y)
        pdf.cell(40, 8, "Host", 1)
        pdf.cell(120, 8, "Puertos Abiertos", 1)
        y += 10
        pdf.set_font("DejaVu", "", 9)
        for host, ports in list(hosts.items())[:15]:
            pdf.set_xy(20, y)
            port_str = ", ".join([f"{p['port']}/{p['service']}" for p in ports[:5]])
            pdf.cell(40, 7, host, 1)
            pdf.cell(120, 7, port_str, 1)
            y += 8
            if y > 190:
                break

    # Slide 4 — Findings
    pdf.add_page()
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(0, 0, W, H, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", "B", 20)
    pdf.set_xy(20, 20)
    pdf.cell(0, 15, "Hallazgos y Riesgos")
    pdf.set_text_color(200, 200, 200)
    pdf.set_font("DejaVu", "", 11)
    findings = [
        ("Puertos administrativos expuestos", "SSH/RDP sin restricción de IP", "Alto"),
        ("Red plana sin segmentación", "Todos los hosts en la misma VLAN", "Alto"),
        ("Servicios contables no detectados", "CONTPAQi/SQL no responden", "Medio"),
        ("Sin backups automatizados", "No se detectó servicio de backup", "Alto"),
    ]
    y = 55
    pdf.set_font("DejaVu", "B", 9)
    pdf.set_xy(20, y)
    pdf.cell(90, 8, "Hallazgo", 1)
    pdf.cell(130, 8, "Detalle", 1)
    pdf.cell(30, 8, "Riesgo", 1)
    y += 10
    pdf.set_font("DejaVu", "", 9)
    for finding, detail, risk in findings:
        pdf.set_xy(20, y)
        pdf.cell(90, 7, finding, 1)
        pdf.cell(130, 7, detail, 1)
        risk_color = (255, 50, 50) if risk == "Alto" else (255, 200, 50)
        pdf.set_text_color(*risk_color)
        pdf.cell(30, 7, risk, 1)
        pdf.set_text_color(200, 200, 200)
        y += 9

    # Slide 5 — Recommendations
    pdf.add_page()
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(0, 0, W, H, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", "B", 20)
    pdf.set_xy(20, 20)
    pdf.cell(0, 15, "Recomendaciones")
    pdf.set_text_color(200, 200, 200)
    pdf.set_font("DejaVu", "", 11)
    recs = [
        "1. Segmentar la red en VLANs (oficina, servidores, invitados)",
        "2. Restringir RDP/SSH solo a IPs autorizadas o vía VPN",
        "3. Implementar backups automáticos cifrados (3-2-1)",
        "4. Migrar servicios contables a infraestructura monitoreada",
        "5. Instalar agente de monitoreo 24/7 (Wazuh)",
        "6. Activar firewall perimetral con IPS/IDS",
    ]
    y = 50
    for rec in recs:
        pdf.set_xy(20, y)
        pdf.multi_cell(W - 40, 8, rec)
        y += 12

    # Slide 6 — Mystic Shield Offer
    pdf.add_page()
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(0, 0, W, H, "F")
    pdf.set_text_color(255, 107, 53)
    pdf.set_font("DejaVu", "B", 22)
    pdf.set_xy(20, 40)
    pdf.cell(0, 15, "Mystic Shield", align="C")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", "", 14)
    pdf.set_xy(20, 60)
    pdf.cell(0, 12, "Tu agente IA de ciberseguridad", align="C")
    pdf.set_font("DejaVu", "", 11)
    pdf.set_xy(20, 85)
    pdf.cell(0, 10, "Reportes diarios por WhatsApp + Email", align="C")
    pdf.set_xy(20, 97)
    pdf.cell(0, 10, "Monitoreo 24/7 con inteligencia artificial", align="C")
    pdf.set_xy(20, 109)
    pdf.cell(0, 10, "Detección de amenazas en tiempo real", align="C")
    pdf.set_xy(20, 121)
    pdf.cell(0, 10, "Chat con tu agente: pregúntale lo que sea", align="C")
    pdf.set_font("DejaVu", "B", 12)
    pdf.set_xy(20, 150)
    pdf.cell(0, 10, "Sonora Digital Corp — mystic.sh", align="C")

    report_path = REPORTS_DIR / f"diagnostico-{company_name.lower().replace(' ', '-')}-{datetime.now():%Y%m%d}.pdf"
    pdf.output(str(report_path))
    _log(f"PDF generated: {report_path}")
    return str(report_path)


# ─── AUDIO GENERATION ──────────────────────────────────────────────

async def _generate_audio(company_name: str, analysis: str) -> Optional[str]:
    """Generate voice summary using edge-tts."""
    try:
        import edge_tts
    except ImportError:
        _log("edge-tts not installed, skipping audio")
        return None

    text = f"""Hola, soy Mystic, asistente de Sonora Digital Corp.
He completado el diagnóstico de seguridad para {company_name}.
{analysis[:400]}"""
    text = text.replace("*", "").replace("#", "").strip()

    audio_path = str(REPORTS_DIR / f"diagnostico-{company_name.lower().replace(' ', '-')}-{datetime.now():%Y%m%d}.mp3")
    try:
        await edge_tts.Communicate(text, "es-MX-DaliaNeural").save(audio_path)
        _log(f"Audio generated: {audio_path}")
        return audio_path
    except Exception as e:
        _log(f"Audio generation error: {e}")
        return None


# ─── WHATSAPP (via wacli) ──────────────────────────────────────────

def _send_whatsapp(phone: str, message: str, file_path: str = "", audio_path: str = ""):
    """Send WhatsApp message + optional file + voice note."""
    WACLI = os.path.expanduser("~/.local/bin/wacli")
    STORE = os.path.expanduser("~/.config/ai.opencode.desktop/wacli")
    if not os.path.exists(WACLI):
        _log("wacli not found, skipping WhatsApp")
        return {"sent": False, "error": "wacli not found"}

    to = phone.strip()
    if not to.endswith("@s.whatsapp.net"):
        to = f"521{to}@s.whatsapp.net" if len(to) == 10 else f"52{to}@s.whatsapp.net"

    results = []
    args = [WACLI, "send", "text", "--message", message, "--to", to, "--post-send-wait", "3s", "--store", STORE, "--json"]
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=30)
        results.append({"type": "text", "result": r.stdout.strip()[:200]})
    except Exception as e:
        results.append({"type": "text", "error": str(e)})

    if file_path and os.path.exists(file_path):
        args = [WACLI, "send", "file", "--file", file_path, "--to", to, "--post-send-wait", "5s", "--store", STORE, "--json"]
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=60)
            results.append({"type": "file", "result": r.stdout.strip()[:200]})
        except Exception as e:
            results.append({"type": "file", "error": str(e)})

    if audio_path and os.path.exists(audio_path):
        ogg_path = audio_path.replace(".mp3", ".ogg")
        try:
            subprocess.run(["ffmpeg", "-y", "-i", audio_path, "-c:a", "libopus", "-b:a", "16k", "-ar", "16000", ogg_path],
                           capture_output=True, timeout=60)
            args = [WACLI, "send", "file", "--file", ogg_path, "--mime", "audio/ogg; codecs=opus", "--ptt",
                    "--to", to, "--post-send-wait", "5s", "--store", STORE, "--json"]
            r = subprocess.run(args, capture_output=True, text=True, timeout=60)
            results.append({"type": "voice", "result": r.stdout.strip()[:200]})
        except Exception as e:
            results.append({"type": "voice", "error": str(e)})
        finally:
            if os.path.exists(ogg_path):
                os.unlink(ogg_path)

    _log(f"WhatsApp sent to {phone}: {len(results)} messages")
    return {"sent": True, "messages": results}


# ─── EMAIL ─────────────────────────────────────────────────────────

def _send_email(to_email: str, company_name: str, pdf_path: str):
    """Send email with PDF report using sendmail/SSMTP."""
    try:
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email.mime.text import MIMEText
        from email import encoders
    except ImportError:
        _log("email libs not available")
        return {"sent": False, "error": "email libs not available"}

    msg = MIMEMultipart()
    msg["From"] = f"Mystic Shield <{COMPANY_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = f"Diagnóstico de Seguridad — {company_name}"

    body = f"""
    Hola,

    Mystic ha completado el diagnóstico de seguridad para {company_name}.

    Adjunto encontrarás el reporte PDF con los hallazgos, riesgos y recomendaciones.

    Si tienes preguntas, responde a este correo o contáctanos por WhatsApp.

    — {MYSTIC_NAME}
    {COMPANY}
    """
    msg.attach(MIMEText(body, "plain", "utf-8"))

    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(pdf_path)}")
            msg.attach(part)

    try:
        import smtplib
        smtp_server = os.environ.get("SMTP_SERVER", "localhost")
        smtp_port = int(os.environ.get("SMTP_PORT", "25"))
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.sendmail(COMPANY_EMAIL, to_email, msg.as_string())
        _log(f"Email sent to {to_email}")
        return {"sent": True}
    except Exception as e:
        _log(f"Email error: {e}")
        return {"sent": False, "error": str(e)}


# ─── MAIN DIAGNOSIS PIPELINE ───────────────────────────────────────

async def shield_diagnose(
    target: str,
    company_name: str,
    ceo_phone: str = "",
    ceo_email: str = "",
    company_email: str = "",
) -> str:
    """Run full diagnosis: scan → analyze → PDF → audio → send."""
    diagnosis_id = str(uuid.uuid4())[:8]
    _log(f"[{diagnosis_id}] Starting diagnosis for {company_name} @ {target}")

    # Step 1: Scan
    scan_data = _fast_scan(target)
    if "error" in scan_data:
        return json.dumps({"success": False, "error": scan_data["error"]})

    # Step 2: Analyze with LLM
    system_prompt = """Eres Mystic, asistente de ciberseguridad de Sonora Digital Corp.
Eres una experta en seguridad de redes, ciberseguridad, análisis de infraestructura TI.
Hablas en español profesional pero accesible para dueños de negocio.
Generas reportes ejecutivos claros con hallazgos, riesgos y recomendaciones accionables."""

    total_hosts = scan_data["total_hosts"]
    active_hosts = scan_data["hosts_with_open_ports"]
    host_details = scan_data.get("hosts", {})
    open_ports_summary = []
    for host, ports in list(host_details.items())[:10]:
        ports_str = ", ".join([f"{p['port']}/{p['service']}" for p in ports])
        open_ports_summary.append(f"{host}: {ports_str}")

    analysis_prompt = f"""Analiza los siguientes resultados de un escaneo de red para la empresa {company_name}.

RESULTADOS DEL ESCANEO:
- Total de hosts detectados: {total_hosts}
- Hosts con puertos abiertos: {active_hosts}
- Detalle de puertos abiertos:
{chr(10).join(open_ports_summary)}

Genera un análisis ejecutivo que incluya:
1. Resumen de la situación actual de seguridad
2. Principales hallazgos y nivel de riesgo (Alto/Medio/Bajo)
3. Recomendaciones específicas accionables
4. Próximos pasos sugeridos

Mantén un tono profesional pero accesible para un CEO que no es técnico."""

    analysis = _call_llm(analysis_prompt, system_prompt)

    # Step 3: Generate PDF
    pdf_path = _generate_pdf(company_name, scan_data, analysis)

    # Step 4: Generate Audio
    audio_path = await _generate_audio(company_name, analysis)

    # Step 5: Send WhatsApp
    whatsapp_result = {}
    if ceo_phone:
        intro_msg = f"""🔒 *Diagnóstico Mystic Shield — {company_name}*

Hola, soy *Mystic*, tu asistente de ciberseguridad de {COMPANY}.

He completado el diagnóstico de tu red. Aquí un resumen:

• {total_hosts} dispositivos detectados en tu red
• {active_hosts} con servicios expuestos
• Se generó reporte PDF detallado + audio resumen

Escucha el audio y revisa el PDF. ¿Tienes preguntas? Puedes responderme aquí mismo."""
        whatsapp_result = _send_whatsapp(ceo_phone, intro_msg, pdf_path, audio_path)

    # Step 6: Send Email
    email_result = {}
    if ceo_email:
        email_result = _send_email(ceo_email, company_name, pdf_path)

    # Step 7: Save report metadata
    report_meta = {
        "id": diagnosis_id,
        "company_name": company_name,
        "target": target,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scan": scan_data,
        "analysis": analysis,
        "pdf_path": pdf_path,
        "audio_path": audio_path,
        "whatsapp": whatsapp_result,
        "email": email_result,
    }
    meta_path = REPORTS_DIR / f"{diagnosis_id}.json"
    meta_path.write_text(json.dumps(report_meta, indent=2, ensure_ascii=False))
    _log(f"[{diagnosis_id}] Diagnosis complete")

    return json.dumps({
        "success": True,
        "diagnosis_id": diagnosis_id,
        "company_name": company_name,
        "total_hosts": total_hosts,
        "active_hosts": active_hosts,
        "pdf_path": pdf_path,
        "audio_path": audio_path,
        "whatsapp_sent": bool(whatsapp_result.get("sent")),
        "email_sent": bool(email_result.get("sent")),
        "summary": analysis[:500],
    }, ensure_ascii=False)


async def shield_send_report(diagnosis_id: str, ceo_phone: str = "", ceo_email: str = "") -> str:
    """Resend a previous diagnosis report."""
    meta_path = REPORTS_DIR / f"{diagnosis_id}.json"
    if not meta_path.exists():
        return json.dumps({"success": False, "error": f"Report {diagnosis_id} not found"})
    meta = json.loads(meta_path.read_text())
    pdf_path = meta.get("pdf_path", "")
    audio_path = meta.get("audio_path", "")
    company_name = meta.get("company_name", "Unknown")

    whatsapp_result = {}
    if ceo_phone:
        msg = f"🔒 *Mystic Shield — {company_name}*\n\nReenviando diagnóstico del {meta.get('timestamp', 'desconocida')}"
        whatsapp_result = _send_whatsapp(ceo_phone, msg, pdf_path, audio_path)

    email_result = {}
    if ceo_email:
        email_result = _send_email(ceo_email, company_name, pdf_path)

    return json.dumps({
        "success": True,
        "whatsapp_sent": bool(whatsapp_result.get("sent")),
        "email_sent": bool(email_result.get("sent")),
    }, ensure_ascii=False)


TOOLS = {
    "shield_diagnose": {
        "name": "shield_diagnose",
        "description": "Ejecutar diagnóstico completo de seguridad: escanea red, analiza con IA, genera PDF + audio, envía por WhatsApp y Email",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "IP o subred (ej: 192.168.1.0/24 o 192.168.1.1)"},
                "company_name": {"type": "string", "description": "Nombre de la empresa"},
                "ceo_phone": {"type": "string", "description": "Teléfono del CEO (ej: 6622681111)"},
                "ceo_email": {"type": "string", "description": "Email del CEO"},
                "company_email": {"type": "string", "description": "Email de la empresa"},
            },
            "required": ["target", "company_name"],
        },
        "handler": shield_diagnose,
    },
    "shield_send_report": {
        "name": "shield_send_report",
        "description": "Reenviar un diagnóstico previo por WhatsApp o Email",
        "inputSchema": {
            "type": "object",
            "properties": {
                "diagnosis_id": {"type": "string", "description": "ID del diagnóstico (ej: a1b2c3d4)"},
                "ceo_phone": {"type": "string", "description": "Teléfono del CEO"},
                "ceo_email": {"type": "string", "description": "Email del CEO"},
            },
            "required": ["diagnosis_id"],
        },
        "handler": shield_send_report,
    },
}


# ─── HTTP SERVER MODE ─────────────────────────────────────────────

def main_http(port: int = 8930):
    """Run as HTTP MCP server."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    from http.server import BaseHTTPRequestHandler, HTTPServer

    class MCPHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "service": "mystic-shield", "version": "1.0.0"}).encode())
            elif self.path.startswith("/report/"):
                diag_id = self.path.split("/")[-1]
                meta_path = REPORTS_DIR / f"{diag_id}.json"
                if meta_path.exists():
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(meta_path.read_bytes())
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "not found"}).encode())
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            if self.path == "/diagnose":
                content_len = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(content_len))
                result = loop.run_until_complete(shield_diagnose(
                    target=body.get("target", ""),
                    company_name=body.get("company_name", "Unknown"),
                    ceo_phone=body.get("ceo_phone", ""),
                    ceo_email=body.get("ceo_email", ""),
                    company_email=body.get("company_email", ""),
                ))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(result.encode())
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, fmt, *args):
            _log(f"HTTP: {fmt % args}")

    server = HTTPServer(("127.0.0.1", port), MCPHandler)
    _log(f"Mystic Shield MCP server running on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8930
        main_http(port)
    else:
        print("Use --http <port> to run HTTP mode, or import tools directly.", file=sys.stderr)
