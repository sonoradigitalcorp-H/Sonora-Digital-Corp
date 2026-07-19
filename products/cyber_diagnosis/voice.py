"""Mystic Voice — Generación de audio hiperrealista con edge-tts.
Voz: es-MX-DaliaNeural (Mexicana, femenina, cálida, humana).
Efectos: pausas dramáticas, énfasis, ritmo conversacional.
"""
import json
import subprocess
import hashlib
from datetime import datetime, timedelta
from pathlib import Path


VOICE = "es-MX-DaliaNeural"


def generate_script(result: dict, company_name: str = None) -> str:
    """Genera guión persuasivo con FOMO para Mystic."""
    grade = result["grade"]
    domain = result["domain"]
    s = result["summary"]
    score = result["score"]
    company = company_name or domain

    # Timeline
    expires = (datetime.now() + timedelta(hours=48)).strftime("%A, %d de %B a las %H:%M")
    slots = "5" if score < 60 else "3" if score < 80 else "2"

    grade_phrase = {
        "A": "excelente, estás muy bien protegido... pero siempre hay margen de mejora.",
        "B": "buena, pero hay detalles que podrían costarte caro si no los atiendes a tiempo.",
        "C": "preocupante. Tienes vulnerabilidades que un atacante podría explotar esta misma semana.",
        "D": "crítica. Necesitas actuar ya. Tu dominio tiene riesgos activos.",
        "F": "extremadamente crítica. Es urgente que tomes medidas hoy mismo.",
    }.get(grade, "regular. Hay cosas que revisar.")

    criticos_text = ""
    if s["criticos"]:
        criticos_text = f" Los puntos más urgentes son: {', '.join(s['criticos'])}. "
        criticos_text += "Esto no es algo que puedas dejar para después."

    return f"""
Hola. Soy Mystic, la asistente de inteligencia artificial de Sonora Digital Corp.

Acabo de completar el análisis de ciberseguridad para {company}. Y tengo que ser honesta contigo...

Tu calificación es {grade}. Un score de {score} sobre 100. Eso significa que tu postura de seguridad es {grade_phrase}

De {s['total']} verificaciones que realizamos, solo {s['ok']} están en orden. {s['warning']} tienen advertencias. Y {s['error']} requieren acción inmediata.{criticos_text}

Pero déjame decirte algo importante: esto es solo la radiografía superficial. Un atacante real no se detiene en lo que yo revisé. Ellos buscan más profundo. Y cuando encuentran una entrada, en promedio, tardan menos de 24 horas en comprometer todo el sistema.

La buena noticia es que esto tiene solución. Y tengo a las personas correctas para ayudarte.

Mi equipo de ciberseguridad está listo para presentarte un plan de acción detallado, con tiempos, costos y prioridades. Pero escucha bien... Esta evaluación gratuita tiene un cupo limitado. De hecho, solo estamos ofreciendo {slots} diagnósticos esta semana, y el tuyo expira en 48 horas.

Si quieres que tu equipo te presente el plan completo de remediación y cómo podemos proteger tu empresa, responde a este mensaje o agenda una llamada con ellos hoy.

No dejes esto para después. En ciberseguridad, el después nunca llega... hasta que es demasiado tarde.

Gracias por confiar en Sonora Digital Corp. Nos vemos del otro lado. 🛡️
"""


def generate_audio(script: str, output_path: str = None) -> str:
    """Genera audio con edge-tts y voz Mystic (Dalia Neural).
    Produce voz hiperrealista con ritmo conversacional.
    """
    if output_path is None:
        hash_id = hashlib.md5(script.encode()).hexdigest()[:8]
        output_path = f"/tmp/mystic-cyber-{hash_id}.wav"

    text = script.strip()

    try:
        # Edge TTS con parámetros de voz natural
        cmd = [
            "edge-tts",
            "--voice", VOICE,
            "--text", text[:1500],
            "--write-media", output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        return output_path

    except subprocess.TimeoutExpired:
        print("⚠️  TTS timeout — generando versión corta...")
        # Fallback: texto más corto
        short_script = text[:500]
        try:
            subprocess.run(
                ["edge-tts", "--voice", VOICE,
                 "--text", short_script, "--write-media", output_path],
                check=True, capture_output=True, text=True, timeout=60,
            )
            return output_path
        except Exception:
            return None

    except Exception as e:
        print(f"⚠️  Error generando audio: {e}")
        return None


def generate_whatsapp_message(result: dict) -> str:
    """Genera mensaje de WhatsApp para enviar el diagnóstico."""
    return (
        f"🛡️ *Diagnóstico de Ciberseguridad - {result['domain']}*\n\n"
        f"Calificación: {result['grade']} ({result['score']}/100)\n"
        f"✅ {result['summary']['ok']} seguras  ⚠️ {result['summary']['warning']} advertencias  "
        f"❌ {result['summary']['error']} críticas\n\n"
        f"🔊 Escucha el resumen de Mystic (IA de SDC):\n"
        f"🎵 Audio adjunto\n\n"
        f"📄 Reporte completo:\n"
        f"🔗 [URL del reporte]\n\n"
        f"⏳ *Esta evaluación gratuita expira en 48h.*\n"
        f"¿Agendamos una llamada para revisar los resultados?"
    )
