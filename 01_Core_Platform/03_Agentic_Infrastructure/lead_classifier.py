#!/usr/bin/env python3
"""lead_classifier.py — Clasificador de intención de lead con LLM + schema JSON estricto (v2).

Servicios reales de Aztrotech. OKF context inyectado. Determinista salvo clasificación LLM.
Único punto donde se usa LLM para clasificación de intención.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

BASE = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE / "01_Core_Platform" / "05_Shared_Libraries" / "SDK_Python"))

from sdc_sdk import SDC_Client


class LeadClassification(BaseModel):
    """Schema estricto de clasificación. Servicios reales Aztrotech."""
    intencion: str = Field(
        description="Tipo de intención detectada",
        pattern="^(nuevo_lead|agendar_cita|precio|info_general|tecnico_dificil|escalar_cesar|saludo|despedida|generar_asset|diagnostico)$"
    )
    campos: dict[str, str] = Field(
        description="Campos extraídos: nombre, empresa, giro, tamano_equipo, servicio, fecha, hora",
        default_factory=dict
    )
    confianza: float = Field(ge=0.0, le=1.0, description="Confianza 0-1")
    respuesta_sugerida: str = Field(description="Respuesta sugerida para el lead")
    accion_requerida: str = Field(
        description="Acción que debe ejecutar el motor determinista",
        pattern="^(capture|schedule|notify|escalar|responder|generate_asset|none)$"
    )
    asset_type: str | None = Field(
        default=None,
        description="Tipo de asset si intencion=generar_asset: imagen/video/mockup/audio"
    )


# Servicios reales de Aztrotech (desde aztrotech.mx)
SERVICIOS = {
    "empleado_digital": "Empleado Digital — Agente IA 24/7 en WhatsApp, Instagram, Facebook",
    "automatizaciones": "Automatizaciones — Flujos, reportes automáticos, integraciones (WhatsApp Business, Stripe, Shopify, SAP)",
    "plataforma_medida": "Plataforma Empresarial — CRM/ERP/Apps web y móviles a la medida con IA",
    "plataforma_juridica": "Plataforma Jurídica — Expedientes, audiencias, documentos, alertas vencimientos",
    "plataforma_inmobiliaria": "Plataforma Inmobiliaria — Inventario propiedades, prospectos, match IA, contratos",
    "academia_interna": "Academia Interna — Manuales, SOPs, asistente IA por departamento, analíticas",
    "diagnostico_ia": "Diagnóstico IA Gratuito — 30 min, 5 preguntas, resultado inmediato",
}

GIROS = [
    "comercio_retail", "servicios_profesionales", "salud_bienestar",
    "gastronomia_hospitality", "construccion_manufactura", "educacion_elearning",
    "distribucion_industrial", "e_commerce", "juridico", "inmobiliario",
    "tecnologia", "otro"
]

TAMANOS = ["solo_yo", "2-5", "6-20", "20+"]
ASSET_TYPES = ["imagen", "video", "mockup", "audio"]

CLASSIFIER_SYSTEM = """Eres el clasificador de leads de Aztrotech (César Holguín).
Analizas el mensaje y devuelves SOLO JSON válido según el schema.

SERVICIOS AZTROTECH (data real, NO inventar):
1. Empleado Digital (Agente IA): $999/$1,999/$3,999 USD — WhatsApp/Instagram/Facebook 24/7, captura leads, agenda citas
2. Automatizaciones: Flujos + reportes + integraciones — cotización según procesos
3. Plataforma Empresarial: CRM/ERP/Apps a medida — cotización por proyecto
4. Plataforma Jurídica: Expedientes, audiencias, documentos
5. Plataforma Inmobiliaria: Propiedades, prospectos, match IA
6. Academia Interna: Manuales, SOPs, asistente IA por depto
7. Diagnóstico IA: GRATIS 30 min

INTENCIONES:
- nuevo_lead: primer contacto, quieren info general
- agendar_cita: piden agendar fecha/hora
- precio: preguntan costos/paquetes/cotización
- info_general: preguntas sobre servicios
- tecnico_dificil: preguntas técnicas complejas, APIs, integraciones
- escalar_cesar: quieren hablar con humano/César/dueño
- saludo: hola, buenos días
- despedida: gracias, adiós
- generar_asset: piden imagen, video, mockup, audio
- diagnostico: quieren el diagnóstico gratuito

GIROS DISPONIBLES: comercio_retail, servicios_profesionales, salud_bienestar, gastronomia_hospitality, construccion_manufactura, educacion_elearning, distribucion_industrial, e_commerce, juridico, inmobiliario, tecnologia, otro
TAMAÑOS: solo_yo, 2-5, 6-20, 20+

REGLAS DE EXTRACCIÓN:
- nombre: nombre de la persona (si lo da)
- empresa: nombre de empresa/negocio (si lo da)
- giro: uno de los GIROS disponibles
- tamano_equipo: uno de los TAMAÑOS
- servicio: uno de los servicios de AZTROTECH
- fecha: YYYY-MM-DD (si la da)
- hora: HH:MM 24h (si la da)
- asset_type: imagen/video/mockup/audio (si pide asset)

REGLAS DE ACCIÓN:
- nuevo_lead → capture
- agendar_cita → schedule (validar disponibilidad)
- precio → responder (OKF exacto) + capture
- info_general → responder (FAQ + web) + ofrecer diagnóstico gratis
- tecnico_dificil → escalar
- escalar_cesar → escalar
- saludo → responder (bienvenida)
- despedida → none
- generar_asset → generate_asset
- diagnostico → responder (ofrecer diagnóstico gratis)

RESPUESTA_SUGERIDA: Natural, desde beneficios. NUNCA inventar precios.
Si es precio: "Los mejores precios te los doy en llamada con César. ¿Te parece si hacemos un diagnóstico gratis de 30 min?"
Si es escalar: "Te paso con César directamente."
"""


def classify_lead_intent(
    tenant: str,
    message: str,
    context: dict[str, Any] = None,
    okf_context: str = None
) -> LeadClassification:
    """Clasifica intención con LLM + schema JSON estricto + OKF context."""
    client = SDC_Client(tenant)

    system = CLASSIFIER_SYSTEM
    if okf_context:
        system += f"\n\nCONTEXTO OKF (precios exactos):\n{okf_context[:600]}"

    user_content = f"MENSAJE: {message}"
    if context:
        user_content += f"\n\nCONTEXTO PREVIO: {json.dumps(context, ensure_ascii=False)}"

    res = client.call_llm([
        {"role": "system", "content": system},
        {"role": "user", "content": f"{user_content}\n\nResponde SOLO con JSON válido (sin markdown, sin ```):\n{json.dumps(LeadClassification.model_json_schema(), ensure_ascii=False)}"}
    ], max_tokens=500)

    if res.get("status") != "success":
        return LeadClassification(
            intencion="info_general",
            campos={},
            confianza=0.3,
            respuesta_sugerida="Cuéntame más para poder ayudarte mejor. ¿Te interesa nuestro Empleado Digital o alguna automatización?",
            accion_requerida="responder"
        )

    content = res["content"]
    try:
        start = content.find("{")
        end = content.rfind("}") + 1
        data = json.loads(content[start:end]) if start >= 0 else json.loads(content)
        return LeadClassification(**data)
    except Exception as e:
        print(f"[WARN] Error parseando clasificación: {e}")
        return LeadClassification(
            intencion="info_general",
            campos={},
            confianza=0.3,
            respuesta_sugerida="Cuéntame más para poder ayudarte mejor.",
            accion_requerida="responder"
        )


def get_servicio_descripcion(servicio: str) -> str:
    """Retorna descripción legible del servicio."""
    return SERVICIOS.get(servicio, "Servicio no especificado. Diagnóstico IA gratuito para saber qué necesitas.")


def main():
    """CLI para testing."""
    import argparse
    ap = argparse.ArgumentParser(description="Lead Classifier v2 CLI")
    ap.add_argument("--tenant", default="aztrotech")
    ap.add_argument("--message", required=True)
    ap.add_argument("--context", help="JSON context")
    args = ap.parse_args()

    ctx = json.loads(args.context) if args.context else None
    result = classify_lead_intent(args.tenant, args.message, ctx)
    print(result.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
