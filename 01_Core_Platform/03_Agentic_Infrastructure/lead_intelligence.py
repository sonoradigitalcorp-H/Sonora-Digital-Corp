#!/usr/bin/env python3
"""lead_intelligence.py — Genera resumen empresa + objeciones + next_action.

Único punto donde se usa LLM para intelligence (no para routing/scoring).
Inyecta OKF context + plantillas evaluadas. Determinista salvo síntesis.
"""

import json
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

BASE = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE / "01_Core_Platform" / "05_Shared_Libraries" / "SDK_Python"))

from sdc_sdk import SDC_Client
from lead_scoring import get_objeciones_por_servicio, classify_by_giro


class LeadIntelligence(BaseModel):
    resumen_empresa: str = Field(description="Resumen 2-3 líneas de la empresa y su situación")
    objeciones_probables: list[str] = Field(description="Top 3 objeciones que probablemente tendrá")
    contraargumentos: list[str] = Field(description="Contraargumentos específicos para cada objeción")
    dolor_detectado: str = Field(description="El dolor principal que puede resolver Aztrotech")
    presupuesto_estimado: str = Field(description="Rango de presupuesto estimado: bajo/medio/alto/unknown")
    autoridad: str = Field(description="Es tomador de decisiones: si/no/unknown")
    urgency_level: str = Field(description="Urgencia: baja/media/alta")
    servicio_recomendado: str = Field(description="Servicio Aztrotech más alineado")
    caso_exito_relevante: str = Field(description="Caso de éxito más relevante de Aztrotech")
    diagnostico_recomendado: str = Field(description="Tipo de diagnóstico: general/especializado")
    next_action: str = Field(description="Siguiente acción concreta para César")
    nota_para_cesar: str = Field(description="Nota personalizada para César sobre cómo abordar este lead")


INTELLIGENCE_SYSTEM = """Eres el analista de intelligence de Aztrotech (César Holguín).
Analizas leads capturados y generas inteligencia accionable para César.

CONTEXTO AZTROTECH (servicios reales):
1. Empleado Digital (Agente IA): $999/$1,999/$3,999 USD. Atiende WhatsApp/Instagram/Facebook 24/7, captura leads, agenda citas.
2. Automatizaciones: Flujos + reportes + integraciones (cotización según procesos).
3. Plataformas Empresariales: CRM/ERP/Apps a medida (cotización por proyecto).
4. Plataformas Especializadas: Jurídica, Inmobiliaria, Academia Interna (ya construidas, adaptables).
5. Diagnóstico IA: GRATIS 30 min.

CASOS DE ÉXITO REALES:
- Suministros Palominos: ERP completo + Academia + GPTs + Starter pack IA. AztroTech = socio tecnológico.
- Jewelry Remate MX: Dashboard financiero + CRM + Agente IA. +50% ventas.

DOLORES COMUNES DE EMPRESAS:
- Leads sin seguimiento (se enfrían en WhatsApp)
- Todo depende de personas (cuello de botella)
- Información regada (WhatsApp + Excel + sistemas que no se hablan)

INSTRUCCIONES:
- Resumen empresa: 2-3 líneas, factual, sin inventar.
- Objeciones: usar las más probables según servicio/giro.
- Contraargumentos: específicos, con datos reales de Aztrotech.
- Next action: CONCRETA (quién, qué, cuándo).
- Para leads COLD: nurturing + diagnóstico gratis.
- Para leads WARM: prueba social + diagnóstico.
- Para leads HOT: llamada directa + demo rápida.
"""


def generate_lead_intelligence(
    tenant: str,
    lead: dict[str, Any],
    scoring_result: dict = None
) -> LeadIntelligence:
    """
    Genera inteligencia del lead usando LLM + OKF + plantillas.
    Inyecta contexto real de Aztrotech para evitar alucinaciones.
    """
    client = SDC_Client(tenant)

    # Pre-computar datos deterministas
    giro_info = classify_by_giro(lead.get("giro", "otro"))
    objeciones_base = get_objeciones_por_servicio(lead.get("servicio", "empleado_digital"))

    user_content = f"""LEAD A ANALIZAR:
- Nombre: {lead.get('nombre', 'No especificado')}
- Empresa: {lead.get('empresa', 'No especificado')}
- Giro: {lead.get('giro', 'No especificado')}
- Tamaño equipo: {lead.get('tamano_equipo', 'No especificado')}
- Servicio interés: {lead.get('servicio', 'No especificado')}
- Canal: {lead.get('canal', 'No especificado')}
- Score: {scoring_result.get('score', 0) if scoring_result else 'Sin score'}
- Clasificación: {scoring_result.get('classification', 'SIN_CLASIFICAR') if scoring_result else 'Sin clasificar'}
- Cita agendada: {lead.get('fecha', 'No')} {lead.get('hora', '')}

SERVICIO RECOMENDADO POR GIRO: {giro_info.get('servicio_recomendado', 'diagnostico_ia')}
CASO DE ÉXITO RELEVANTE: {giro_info.get('caso', 'No especificado')}

OBJECIONES BASE PARA ESTE SERVICIO:
{json.dumps(objeciones_base, ensure_ascii=False, indent=2)}

Genera inteligencia accionable para César."""

    res = client.call_llm([
        {"role": "system", "content": INTELLIGENCE_SYSTEM},
        {"role": "user", "content": f"{user_content}\n\nResponde SOLO con JSON válido (sin markdown, sin ```):\n{json.dumps(LeadIntelligence.model_json_schema(), ensure_ascii=False)}"}
    ], max_tokens=600)

    if res.get("status") != "success":
        # Fallback determinista
        return _fallback_intelligence(lead, giro_info, objeciones_base)

    content = res["content"]
    try:
        start = content.find("{")
        end = content.rfind("}") + 1
        data = json.loads(content[start:end]) if start >= 0 else json.loads(content)
        return LeadIntelligence(**data)
    except Exception as e:
        print(f"[WARN] Error parseando intelligence: {e}")
        return _fallback_intelligence(lead, giro_info, objeciones_base)


def _fallback_intelligence(
    lead: dict,
    giro_info: dict,
    objeciones_base: list
) -> LeadIntelligence:
    """Fallback determinista cuando LLM falla."""
    servicio = lead.get("servicio", "empleado_digital")
    servicio_display = {
        "empleado_digital": "Empleado Digital (Agente IA 24/7)",
        "automatizaciones": "Automatizaciones de procesos",
        "plataforma_medida": "Plataforma CRM/ERP a medida",
        "plataforma_juridica": "Plataforma Jurídica",
        "plataforma_inmobiliaria": "Plataforma Inmobiliaria",
        "academia_interna": "Academia Interna",
    }.get(servicio, "Diagnóstico IA")

    return LeadIntelligence(
        resumen_empresa=f"{lead.get('empresa', 'Empresa')} del giro {lead.get('giro', 'general')}, con {lead.get('tamano_equipo', '?')} empleados. Interés en {servicio_display}.",
        objeciones_probables=[o["objecion"] for o in objeciones_base[:3]],
        contraargumentos=[o["contraargumento"] for o in objeciones_base[:3]],
        dolor_detectado="Leads sin seguimiento + proceso manual",
        presupuesto_estimado="unknown",
        autoridad="unknown",
        urgency_level="media",
        servicio_recomendado=servicio_display,
        caso_exito_relevante=giro_info.get("caso", "Suministros Palominos / Jewelry Remate MX"),
        diagnostico_recomendado="general",
        next_action="Llamar y agendar diagnóstico IA gratuito (30 min)",
        nota_para_cesar=f"Lead interesado en {servicio_display}. Ofrecer diagnóstico gratis como primer paso."
    )


def generate_cesar_audio_script(lead: dict, intelligence: LeadIntelligence) -> str:
    """
    Genera guion para audio de abordaje personalizado (voz César).
    Determinista: plantilla + datos del lead.
    """
    servicio = lead.get("servicio", "general")
    nombre = lead.get("nombre", "")
    empresa = lead.get("empresa", "")

    templates = {
        "empleado_digital": (
            f"Hola {nombre}, soy César de Aztrotech. "
            f"Me dijiste que {empresa} les interesa tener un empleado digital que atienda 24/7. "
            f"Te cuento que ya tenemos casos funcionando: en joyería aumentaron ventas un 50 por ciento. "
            f"¿Te parece si hacemos un diagnóstico rápido, gratis, de 30 minutos? "
            f"Te digo exactamente qué necesitas y cuánto cuesta. ¿A qué hora te viene bien?"
        ),
        "automatizaciones": (
            f"Hola {nombre}, soy César de Aztrotech. "
            f"Me comentaste que {empresa} tiene procesos manuales que te quitan tiempo. "
            f"Nosotros automatizamos eso: reportes, seguimiento, integraciones. "
            f"En Suministros Palominos ya tenemos un sistema completo funcionando. "
            f"Hagamos un diagnóstico gratis de 30 minutos. ¿Qué día te acomoda?"
        ),
        "plataforma_medida": (
            f"Hola {nombre}, soy César de Aztrotech. "
            f"Me dijiste que {empresa} necesita un sistema a su medida. "
            f"Construimos CRM, ERP, apps web y móviles exactamente como tú los necesitas. "
            f"Empezamos con un diagnóstico gratis donde vemos tu operación completa. "
            f"¿Te parece mañana a las 10?"
        ),
    }

    template = templates.get(servicio, (
        f"Hola {nombre}, soy César de Aztrotech. "
        f"Gracias por tu interés. "
        f"¿Te parece si hacemos un diagnóstico rápido, gratis, de 30 minutos? "
        f"Te digo exactamente qué necesitas para {empresa}. ¿A qué hora te viene bien?"
    ))

    return template
