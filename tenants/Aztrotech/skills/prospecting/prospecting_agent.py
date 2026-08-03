#!/usr/bin/env python3
"""
Prospecting Agent — Aztrotech
Automatización completa de captación de clientes high-ticket.

Uso: python3 prospecting_agent.py --action all
"""

import os
import sys
import json
import asyncio
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prospecting")

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
OBSIDIAN_DIR = BASE_DIR / "obsidian" / "prospects"
AUDIO_DIR = BASE_DIR / "obsidian" / "audio"
HTML_DIR = BASE_DIR / "obsidian" / "presentations"
PDF_DIR = BASE_DIR / "obsidian" / "pdfs"

# Companies to research
COMPANIES = [
    # RESTAURANTES
    {"name": "La Carreta", "industry": "restaurante", "location": "Hermosillo", "web": "lacarretahermosillo.com", "color": "#FF6B35", "icon": "🍽️"},
    {"name": "El Campestre", "industry": "restaurante", "location": "Hermosillo", "web": "elcampestre.com.mx", "color": "#E74C3C", "icon": "🥘"},
    {"name": "Sushi Itto Hermosillo", "industry": "restaurante", "location": "Hermosillo", "web": "sushiitto.com", "color": "#FF6B6B", "icon": "🍣"},
    
    # ARTISTAS
    {"name": "Banda El Recodo", "industry": "artista", "location": "Hermosillo/Sinaloa", "web": "bandaelrecodo.com", "color": "#9B59B6", "icon": "🎵"},
    {"name": "Festival Cervantino", "industry": "evento", "location": "Hermosillo/Guanajuato", "web": "festivalcervantino.gob.mx", "color": "#8E44AD", "icon": "🎭"},
    
    # INMOBILIARIAS
    {"name": "Inmobiliaria Horizonte", "industry": "inmobiliaria", "location": "Hermosillo", "web": "inmobiliariahorizonte.com", "color": "#3498DB", "icon": "🏠"},
    {"name": "Grupo Delaroca", "industry": "construccion", "location": "Hermosillo", "web": "delaroca.com.mx", "color": "#2980B9", "icon": "🏗️"},
    
    # AUTOS
    {"name": "Autoplan Hermosillo", "industry": "automotriz", "location": "Hermosillo", "web": "autoplanhermosillo.com", "color": "#34495E", "icon": "🚗"},
    {"name": "Kia Hermosillo", "industry": "automotriz", "location": "Hermosillo", "web": "kia.com.mx", "color": "#2C3E50", "icon": "🚙"},
    
    # GASOLINERAS
    {"name": "Gasolineras Soriana", "industry": "gasolinera", "location": "Hermosillo", "web": "soriana.com", "color": "#27AE60", "icon": "⛽"},
    
    # REHABILITACIÓN
    {"name": "Centro Rehab Hermosillo", "industry": "salud", "location": "Hermosillo", "web": "rehabhermosillo.com", "color": "#00BCD4", "icon": "🏥"},
]

# Agents by industry
AGENTS = {
    "restaurante": [
        {"name": "Agente Reservaciones", "function": "Agenda citas, confirma, recuerda", "channel": "WhatsApp"},
        {"name": "Agente Pedidos", "function": "Toma pedidos, procesa, confirma", "channel": "WhatsApp"},
    ],
    "artista": [
        {"name": "Agente Merch", "function": "Venta de mercancía, envíos", "channel": "WhatsApp + Web"},
        {"name": "Agente Bookings", "function": "Agenda presentaciones, cobros", "channel": "WhatsApp"},
    ],
    "evento": [
        {"name": "Agente Boletos", "function": "Venta de boletos, información", "channel": "WhatsApp + Web"},
        {"name": "Agente Info", "function": "Información del evento", "channel": "WhatsApp"},
    ],
    "inmobiliaria": [
        {"name": "Agente Leads", "function": "Califica, nurture, convierte", "channel": "WhatsApp + Web"},
        {"name": "Agente Propiedades", "function": "Muestra propiedades, agenda visitas", "channel": "WhatsApp"},
    ],
    "construccion": [
        {"name": "Agente Cotizaciones", "function": "Genera cotizaciones, sigue up", "channel": "WhatsApp"},
        {"name": "Agente Proyectos", "function": "Información de proyectos", "channel": "WhatsApp"},
    ],
    "automotriz": [
        {"name": "Agente Ventas Auto", "function": "Leads de ventas, cotizaciones", "channel": "WhatsApp + Web"},
        {"name": "Agente Servicio", "function": "Recordatorios de servicio", "channel": "WhatsApp"},
    ],
    "gasolinera": [
        {"name": "Agente Precios", "function": "Informa precios, ubicaciones", "channel": "WhatsApp"},
        {"name": "Agente Facturación", "function": "Envía facturas, recordatorios", "channel": "WhatsApp"},
    ],
    "salud": [
        {"name": "Agente Citas", "function": "Agenda citas, confirma", "channel": "WhatsApp"},
        {"name": "Agente Seguimiento", "function": "Recordatorios, follow-up", "channel": "WhatsApp"},
    ],
}

# Speech templates
SPEECH_TEMPLATE = """Hola {name}, soy de Aztrotech, la empresa de tecnología de Sonora Digital Corp.

Analiqué la página de {company} y vi una oportunidad increíble para ti.

{pain_point}

¿Y si tuvieras un asistente inteligente que {solution}?

Te envié un link para que hables con nuestro asistente y veas cómo funciona. Es como tener un empleado que nunca duerme.

¿Te parece si agendamos una consultoría gratuita de 30 minutos para ver cómo podemos ayudarte a {company}?

Link al asistente: {orb_link}

¡Hasta pronto!"""

PAIN_POINTS = {
    "restaurante": "Tus clientes te escriben por WhatsApp pero nadie les responde al instante. Cada mensaje perdido es una venta que se va.",
    "artista": "Tu merchandise se vende manual y los bookings se pierden por emails no respondidos.",
    "evento": "La información está fragmentada y los boletos se agotan sin aviso a tus seguidores.",
    "inmobiliaria": "Tienes leads fríos que nunca se siguen y propiedades que nadie ve porque no están actualizadas.",
    "construccion": "Las cotizaciones toman días y los proyectos no tienen seguimiento adecuado.",
    "automotriz": "Los leads de ventas se pierden y el servicio post-venta no tiene recordatorios.",
    "gasolinera": "La facturación es manual y no tienes programa de fidelidad para retener clientes.",
    "salud": "Las citas se agenda manualmente y los pacientes no regresan porque nadie les recuerda.",
}

SOLUTIONS = {
    "restaurante": "atendiera 24/7 y convirtiera cada mensaje en una venta automática",
    "artista": "gestionara tu merch y bookings automáticamente mientras tú creas",
    "evento": "informara a tus seguidores en tiempo real y vendiera boletos sin interrupciones",
    "inmobiliaria": "calificara leads y mostrara propiedades automáticamente 24/7",
    "construccion": "generara cotizaciones al instante y diera seguimiento a cada proyecto",
    "automotriz": "atendiera leads de ventas y recordara servicios pendientes automáticamente",
    "gasolinera": "facturara automáticamente y tuviera un programa de fidelidad que retiene clientes",
    "salud": "agendara citas y diera seguimiento a cada paciente para que nunca se olviden de ti",
}


class ProspectingAgent:
    def __init__(self):
        self.companies = COMPANIES
        self.results = []
    
    async def run_all(self):
        """Execute all prospecting tasks."""
        logger.info("Starting prospecting agent...")
        
        # Create directories
        for d in [OBSIDIAN_DIR, AUDIO_DIR, HTML_DIR, PDF_DIR]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Process each company
        for company in self.companies:
            logger.info(f"Processing: {company['name']}")
            await self.process_company(company)
        
        # Generate summary
        self.generate_summary()
        
        logger.info("Prospecting complete!")
    
    async def process_company(self, company: dict):
        """Process a single company."""
        name = company["name"]
        industry = company["industry"]
        
        # Create Obsidian profile
        self.create_profile(company)
        
        # Generate TTS audio
        await self.generate_audio(company)
        
        # Create HTML presentation
        self.create_html(company)
        
        # Create PDF content
        self.create_pdf_content(company)
        
        logger.info(f"  ✓ {name} processed")
    
    def create_profile(self, company: dict):
        """Create Obsidian profile for company."""
        name = company["name"]
        profile_dir = OBSIDIAN_DIR / name
        profile_dir.mkdir(exist_ok=True)
        
        # Main profile
        profile = f"""# {company['name']}

## Datos Generales
- **Industria**: {company['industry']}
- **Ubicación**: {company['location']}
- **Web**: {company['web']}
- **Color de marca**: {company['color']}
- **Icono**: {company['icon']}

## Investigación
- **Estado**: Pendiente de investigación
- **Contacto**: Pendiente
- **Empleados**: Pendiente
- **Facturación estimada**: Pendiente

## Análisis Web
- **Estado**: Pendiente de análisis
- **Problemas identificados**: Pendiente
- **Oportunidades**: Pendiente

## Agentes Propuestos
"""
        
        agents = AGENTS.get(company["industry"], [])
        for agent in agents:
            profile += f"- **{agent['name']}**: {agent['function']} ({agent['channel']})\n"
        
        profile += f"""
## Audio Enviado
- **Fecha**: Pendiente
- **Estado**: Pendiente
- **Respuesta**: Pendiente

## Próximos Pasos
1. Investigación profunda
2. Análisis de web
3. Generación de audio
4. Envío por WhatsApp
5. Seguimiento
"""
        
        (profile_dir / "perfil.md").write_text(profile)
        
        # Pain points
        pain = PAIN_POINTS.get(company["industry"], "Necesita automatización")
        solution = SOLUTIONS.get(company["industry"], "mejorar su atención al cliente")
        
        pain_file = f"""# Problemas Identificados - {company['name']}

## Dolor Principal
{pain}

## Solución Propuesta
{solution}

## Beneficios
- Atención 24/7
- Calificación automática de leads
- Respuesta inmediata
- Seguimiento automático
- Dashboard en tiempo real
"""
        (profile_dir / "problemas.md").write_text(pain_file)
    
    async def generate_audio(self, company: dict):
        """Generate TTS audio for company CEO."""
        name = company["name"]
        industry = company["industry"]
        
        pain = PAIN_POINTS.get(industry, "Necesita automatización")
        solution = SOLUTIONS.get(industry, "mejorar su atención al cliente")
        
        script = SPEECH_TEMPLATE.format(
            name="CEO de " + name,
            company=name,
            pain_point=pain,
            solution=solution,
            orb_link="https://aztrotech.mx/voice"
        )
        
        # Save script
        audio_dir = AUDIO_DIR / name
        audio_dir.mkdir(exist_ok=True)
        (audio_dir / "script.txt").write_text(script)
        
        # Generate TTS
        output_mp3 = audio_dir / "audio.mp3"
        output_ogg = audio_dir / "audio.ogg"
        
        try:
            # Generate MP3
            result = subprocess.run([
                "/home/mystic/.local/bin/edge-tts",
                "--voice", "es-MX-DaliaNeural",
                "--text", script,
                "--write-media", str(output_mp3)
            ], capture_output=True, timeout=60)
            
            if result.returncode == 0 and output_mp3.exists():
                # Convert to OGG
                ffmpeg = "/home/mystic/.local/lib/python3.10/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
                subprocess.run([
                    ffmpeg, "-y", "-i", str(output_mp3),
                    "-c:a", "libopus", "-b:a", "32k",
                    str(output_ogg)
                ], capture_output=True, timeout=30)
                
                logger.info(f"  ✓ Audio generated: {output_ogg}")
            else:
                logger.error(f"  ✗ TTS failed for {name}")
        except Exception as e:
            logger.error(f"  ✗ Audio error for {name}: {e}")
    
    def create_html(self, company: dict):
        """Create HTML presentation for company."""
        name = company["name"]
        color = company["color"]
        icon = company["icon"]
        industry = company["industry"]
        
        pain = PAIN_POINTS.get(industry, "Necesita automatización")
        solution = SOLUTIONS.get(industry, "mejorar su atención al cliente")
        agents = AGENTS.get(industry, [])
        
        agents_html = ""
        for agent in agents:
            agents_html += f"""
            <div class="agent-card">
                <div class="agent-icon">{icon}</div>
                <h3>{agent['name']}</h3>
                <p>{agent['function']}</p>
                <span class="channel">{agent['channel']}</span>
            </div>"""
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Aztrotech para {name}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',sans-serif;background:#09090b;color:#fff;overflow-x:hidden}}
.hero{{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;background:linear-gradient(135deg,{color}15,#09090b);position:relative}}
.hero::before{{content:'';position:absolute;top:-50%;right:-20%;width:600px;height:600px;background:radial-gradient(circle,{color}20,transparent 70%);border-radius:50%}}
.hero h1{{font-size:4em;font-weight:800;margin-bottom:20px;background:linear-gradient(135deg,#fff,{color});-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.hero p{{font-size:1.2em;color:rgba(255,255,255,.6);max-width:600px;margin:0 auto 40px}}
.section{{padding:100px 20px;max-width:1200px;margin:0 auto}}
.section h2{{font-size:2.5em;text-align:center;margin-bottom:60px}}
.problem{{background:linear-gradient(135deg,rgba(239,68,68,.1),transparent);border-radius:20px;padding:60px;margin:40px auto;max-width:800px}}
.solution{{background:linear-gradient(135deg,{color}15,transparent);border-radius:20px;padding:60px;margin:40px auto;max-width:800px}}
.agents-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;margin-top:40px}}
.agent-card{{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:30px;transition:all .3s}}
.agent-card:hover{{border-color:{color};transform:translateY(-5px)}}
.agent-icon{{font-size:2em;margin-bottom:15px}}
.agent-card h3{{font-size:1.2em;margin-bottom:10px}}
.agent-card p{{color:rgba(255,255,255,.6);font-size:.9em}}
.channel{{display:inline-block;padding:4px 12px;border-radius:20px;background:{color}20;color:{color};font-size:.8em;margin-top:10px}}
.cta{{text-align:center;padding:100px 20px;background:linear-gradient(135deg,{color}10,transparent)}}
.cta h2{{font-size:3em;margin-bottom:20px}}
.btn{{display:inline-block;padding:16px 40px;border-radius:30px;background:{color};color:#000;text-decoration:none;font-weight:600;font-size:1.1em;transition:all .3s}}
.btn:hover{{transform:scale(1.05);box-shadow:0 0 30px {color}60}}
</style>
</head>
<body>
<div class="hero">
<div>
<h1>{icon} {name}</h1>
<p>Transformamos tu negocio con inteligencia artificial. Atención 24/7, ventas automáticas, clientes felices.</p>
<a href="#problema" class="btn">Descubre Cómo</a>
</div>
</div>

<div class="section" id="problema">
<h2>El Problema</h2>
<div class="problem">
<h3 style="color:#ef4444;font-size:1.5em;margin-bottom:20px">⚠️ Lo que está pasando en {name}</h3>
<p style="font-size:1.2em;line-height:1.8;color:rgba(255,255,255,.8)">{pain}</p>
</div>
</div>

<div class="section">
<h2>Nuestra Solución</h2>
<div class="solution">
<h3 style="color:{color};font-size:1.5em;margin-bottom:20px">✅ {solution}</h3>
<p style="font-size:1.2em;line-height:1.8;color:rgba(255,255,255,.8)">Con Aztrotech, tu negocio trabaja mientras tú duermes. Nuestros agentes IA atienden, venden y fidelizan automáticamente.</p>
</div>
</div>

<div class="section">
<h2>Agentes para {name}</h2>
<div class="agents-grid">
{agents_html}
</div>
</div>

<div class="cta">
<h2>¿Listo para transformar {name}?</h2>
<p style="color:rgba(255,255,255,.6);margin-bottom:40px">Agenda una consultoría gratuita de 30 minutos</p>
<a href="https://wa.me/5216621072254?text=Hola%20César,%20quiero%20una%20consultoría%20gratuita%20para%20{name.replace(' ','%20')}" class="btn">📱 Hablar con César</a>
<br><br>
<a href="https://aztrotech.mx/voice" class="btn" style="background:transparent;border:2px solid {color};color:{color}">🤖 Hablar con Asistente</a>
</div>

<footer style="text-align:center;padding:40px;color:rgba(255,255,255,.3);font-size:.8em">
<p>Aztrotech — Inteligencia Artificial para Negocios</p>
<p>Sonora Digital Corp · Hermosillo, Sonora</p>
</footer>
</body>
</html>"""
        
        html_path = HTML_DIR / f"{name.lower().replace(' ', '-')}.html"
        html_path.write_text(html)
        logger.info(f"  ✓ HTML created: {html_path}")
    
    def create_pdf_content(self, company: dict):
        """Create PDF content (markdown to be converted)."""
        name = company["name"]
        industry = company["industry"]
        
        pain = PAIN_POINTS.get(industry, "Necesita automatización")
        solution = SOLUTIONS.get(industry, "mejorar su atención al cliente")
        agents = AGENTS.get(industry, [])
        
        content = f"""# Aztrotech para {name}

## Problema Identificado
{pain}

## Nuestra Solución
{solution}

## Agentes Incluidos
"""
        for agent in agents:
            content += f"- **{agent['name']}**: {agent['function']}\n"
        
        content += f"""
## Beneficios
- Atención 24/7 sin interrupciones
- Calificación automática de leads
- Respuesta inmediata a clientes
- Seguimiento automático
- Dashboard en tiempo real
- Marketing automatizado

## Próximos Pasos
1. Consultoría gratuita de 30 minutos
2. Demo del Empleado Digital
3. Propuesta personalizada
4. Activación inmediata

## Contacto
- **César Holguín**: CEO de Aztrotech
- **WhatsApp**: wa.me/5216621072254
- **Web**: aztrotech.mx
- **Asistente**: aztrotech.mx/voice
"""
        
        pdf_path = PDF_DIR / f"{name.lower().replace(' ', '-')}.md"
        pdf_path.write_text(content)
        logger.info(f"  ✓ PDF content created: {pdf_path}")
    
    def generate_summary(self):
        """Generate summary of all prospects."""
        summary = f"""# Resumen de Prospección — Aztrotech
## Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}

### Compañías Investigadas: {len(self.companies)}

"""
        for company in self.companies:
            summary += f"- **{company['name']}** ({company['industry']}) — {company['location']}\n"
        
        summary += f"""
### Archivos Generados
- **Perfiles Obsidian**: {OBSIDIAN_DIR}
- **Audios TTS**: {AUDIO_DIR}
- **Presentaciones HTML**: {HTML_DIR}
- **Contenido PDF**: {PDF_DIR}

### Próximos Pasos
1. Revisar perfiles en Obsidian
2. Verificar audios generados
3. Enviar audios por WhatsApp
4. Seguimiento a leads
"""
        
        (OBSIDIAN_DIR / "RESUMEN.md").write_text(summary)
        logger.info(f"✓ Summary created: {OBSIDIAN_DIR / 'RESUMEN.md'}")


async def main():
    agent = ProspectingAgent()
    await agent.run_all()


if __name__ == "__main__":
    asyncio.run(main())
