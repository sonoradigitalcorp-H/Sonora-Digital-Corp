#!/usr/bin/env python3
"""lead_classifier_hermosillo.py — Clasificador de intención con LLM + schema JSON estricto
para Hermosillo Contabilidad (Nathaly).

Servicios reales de Nathaly (OKF hermosillo-cont.servicios). OKF context inyectado.
Único punto donde se usa LLM: clasificación de intención y extracción de campos.
NUNCA inventa precios (no existen en OKF → deriva a Nathaly).
"""

import json
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE / "01_Core_Platform" / "05_Shared_Libraries" / "SDK_Python"))

from sdc_sdk import SDC_Client  # noqa: E402


class LeadClassificationHC(BaseModel):
    """Schema estricto de clasificación. Servicios reales Hermosillo Contabilidad."""
    intencion: str = Field(
        description="Tipo de intención detectada",
        pattern="^(nuevo_lead|agendar_cita_sat|precio|info_general|tecnico_dificil|escalar_nathaly|saludo|despedida|diagnostico)$"
    )
    campos: dict[str, str] = Field(
        description="Campos extraídos: nombre, negocio, servicio, fecha, hora",
        default_factory=dict
    )
    confianza: float = Field(ge=0.0, le=1.0, description="Confianza 0-1")
    respuesta_sugerida: str = Field(description="Respuesta sugerida para el lead")
    accion_requerida: str = Field(
        description="Acción que debe ejecutar el motor determinista",
        pattern="^(capture|schedule|notify|escalar|responder|none)$"
    )


# Servicios reales de Nathaly (OKF hermosillo-cont.servicios)
SERVICIOS = {
    "contabilidad": "Contabilidad — llevar contabilidad mensual, estados financieros, IVA e ISR, cumplimiento SAT",
    "administracion": "Administración — gestión administrativa: nómina, flujo de caja, control de gastos",
    "manifestacion_importacion": "Manifestación de Importación — trámite de pedimento/importación, papeles y requisitos",
    "marketing": "Marketing — presencia, campañas y crecimiento para negocios",
    "consultas_sat": "Consultas ante el SAT — consultas, aclaraciones y trámites SAT",
    "citas_sat": "Citas ante el SAT — agendar citas SAT a nombre del cliente",
}

CLASSIFIER_SYSTEM = """Eres el clasificador de leads de Hermosillo Contabilidad (Nathaly, contadora en Hermosillo).
Analizas el mensaje y devuelves SOLO JSON válido según el schema.

SERVICIOS DE NATHALY (data real, NO inventar precios):
1. Contabilidad — llevar contabilidad mensual, estados financieros, IVA/ISR
2. Administración — nómina, flujo de caja, gestión administrativa
3. Manifestación de Importación — trámite de pedimento/importación
4. Marketing — presencia y campañas para negocios
5. Consultas ante el SAT — consultas y aclaraciones
6. Citas ante el SAT — agendar citas SAT

INTENCIONES:
- nuevo_lead: primer contacto, quieren info general
- agendar_cita_sat: piden agendar cita (SAT o consulta) con fecha/hora
- precio: preguntan costos/honorarios/cotización
- info_general: preguntas sobre servicios
- tecnico_dificil: preguntas fiscales/legales técnicas complejas
- escalar_nathaly: quieren hablar con Nathaly/humano/contadora
- saludo: hola, buenos días
- despedida: gracias, adiós
- diagnostico: quieren el diagnóstico inicial gratis

REGLAS DE EXTRACCIÓN:
- nombre: nombre de la persona (si lo da)
- negocio: nombre de su negocio/empresa (si lo da)
- servicio: uno de los servicios de NATHALY (contabilidad, administracion, manifestacion_importacion, marketing, consultas_sat, citas_sat)
- fecha: YYYY-MM-DD (si la da)
- hora: HH:MM 24h (si la da)

REGLAS DE ACCIÓN:
- nuevo_lead → capture
- agendar_cita_sat → schedule (validar disponibilidad)
- precio → responder (NUNCA inventar precios: derivar a Nathaly) + capture
- info_general → responder (FAQ) + ofrecer diagnóstico gratis
- tecnico_dificil → escalar
- escalar_nathaly → escalar
- saludo → responder (bienvenida)
- despedida → none
- diagnostico → responder (ofrecer diagnóstico gratis)

RESPUESTA_SUGERIDA: Natural, cálida, desde beneficios. NUNCA inventar precios.
Si es precio: "El costo exacto te lo da Nathaly en una llamada o WhatsApp. ¿Te agendo una consulta rápida? ¡Es gratis el diagnóstico inicial!"
Si es escalar: "Te paso con Nathaly directamente, en un momento te contacta."
Si es cita SAT: "Claro, te agendo tu cita ante el SAT. ¿Qué fecha y hora te acomoda?"
"""


CLASSIFIER_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"  # modelo free MÁS GRANDE disponible
CLASSIFIER_FALLBACK_MODEL = "deepseek/deepseek-v4-flash-0731"  # pagado, SOLO si el free falla


def classify_intent_hermosillo(
    tenant: str,
    message: str,
    context: dict[str, Any] = None,
    okf_context: str = None
) -> LeadClassificationHC:
    """Clasifica intención con LLM + schema JSON estricto + OKF context."""
    client = SDC_Client(tenant)

    system = CLASSIFIER_SYSTEM
    if okf_context:
        system += f"\n\nCONTEXTO OKF (servicios exactos):\n{okf_context[:600]}"

    user_content = f"MENSAJE: {message}"
    if context:
        user_content += f"\n\nCONTEXTO PREVIO: {json.dumps(context, ensure_ascii=False)}"

    res = client.call_llm([
        {"role": "system", "content": system},
        {"role": "user", "content": f"{user_content}\n\nResponde SOLO con JSON válido (sin markdown, sin ```):\n{json.dumps(LeadClassificationHC.model_json_schema(), ensure_ascii=False)}"}
    ], model=CLASSIFIER_MODEL, max_tokens=1500)

    # Fallback: si el modelo free falla o devuelve content vacío → pagado (solo razonamiento grande)
    if res.get("status") != "success" or not res.get("content"):
        res = client.call_llm([
            {"role": "system", "content": system},
            {"role": "user", "content": f"{user_content}\n\nResponde SOLO con JSON válido (sin markdown, sin ```):\n{json.dumps(LeadClassificationHC.model_json_schema(), ensure_ascii=False)}"}
        ], model=CLASSIFIER_FALLBACK_MODEL, max_tokens=1500)

    if res.get("status") != "success":
        return LeadClassificationHC(
            intencion="info_general",
            campos={},
            confianza=0.3,
            respuesta_sugerida="Cuéntame más para poder ayudarte. ¿Te interesa contabilidad, administración, importaciones, marketing o algo del SAT?",
            accion_requerida="responder"
        )

    content = res["content"]
    try:
        start = content.find("{")
        end = content.rfind("}") + 1
        data = json.loads(content[start:end]) if start >= 0 else json.loads(content)
        return LeadClassificationHC(**data)
    except Exception as e:
        print(f"[WARN] Error parseando clasificación: {e}")
        return LeadClassificationHC(
            intencion="info_general",
            campos={},
            confianza=0.3,
            respuesta_sugerida="Cuéntame más para poder ayudarte. ¿Te interesa contabilidad, administración, importaciones, marketing o algo del SAT?",
            accion_requerida="responder"
        )


def main():
    """CLI para testing."""
    import argparse
    ap = argparse.ArgumentParser(description="Lead Classifier Hermosillo Cont CLI")
    ap.add_argument("--tenant", default="hermosillo-cont")
    ap.add_argument("--message", required=True)
    args = ap.parse_args()
    res = classify_intent_hermosillo(args.tenant, args.message)
    print(json.dumps(res.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()