#!/usr/bin/env python3
"""tubandera_scoring.py — Clasificación de Leads y Diagnóstico de Urgencia para Tu Bandera A.C.

Reglas de negocio:
1. Perfil del Contacto:
   - DIRECTO: Quien escribe busca ayuda para sí mismo.
   - FAMILIAR: Busca ayuda para un hijo, hermano, cónyuge o conocido.
   - INSTITUCION: Empresa, escuela o institución que solicita pláticas de prevención/talleres.

2. Diagnóstico de Urgencia (sin juicio de valor):
   - ATENCION_INMEDIATA: Crisis de consumo activa, desintoxicación urgente, solicitud de rescate/traslado ya.
   - ALTA: Consumo recurrente con deterioro familiar/laboral, interés en internamiento inmediato.
   - MODERADA: Consultas de información general, pláticas preventivas institucionales.

3. Notificación a Roberto Lara (CEO):
   - Teléfono: 6623645186 / 5216623645186@s.whatsapp.net
"""

import re
from typing import Dict, Any


def classify_user_profile(message: str) -> str:
    """Clasifica el tipo de contacto en DIRECTO, FAMILIAR o INSTITUCION."""
    msg = message.lower()
    
    # Palabras clave de Institución
    inst_keywords = ["empresa", "escuela", "plática", "platicas", "taller", "conferencia", "institución", "institucion", "prevención", "prevencion", "alumnos", "empleados"]
    if any(k in msg for k in inst_keywords):
        return "INSTITUCION"
        
    # Palabras clave de Familiar
    fam_keywords = ["mi hijo", "mi hija", "mi hermano", "mi hermana", "mi esposo", "mi esposa", "mi pareja", "mi familiar", "un amigo", "un conocido", "mi papa", "mi mama", "mi nieto"]
    if any(k in msg for k in fam_keywords):
        return "FAMILIAR"
        
    return "DIRECTO"


def evaluate_urgency(message: str) -> Dict[str, Any]:
    """Determina la urgencia y si requiere traslado de urgencia sin juicios de valor."""
    msg = message.lower()
    
    urgency = "MODERADA"
    requiere_traslado = False
    motivo = "Consulta de información"

    # Palabras clave de Atención Inmediata / Traslado
    inmediata_keywords = ["urgente", "ahora", "hoy mismo", "vengan por el", "vengan por mi", "vayan por", "rescate", "crisis", "desintoxicación", "desintoxicacion", "traslado"]
    if any(k in msg for k in inmediata_keywords):
        urgency = "ATENCION_INMEDIATA"
        requiere_traslado = True
        motivo = "Solicitud de traslado / rescate o atención clínica urgente"
    elif any(k in msg for k in ["ayuda", "internar", "internamiento", "ingresar", "cuanto cuesta", "donde estan"]):
        urgency = "ALTA"
        motivo = "Interés en internamiento y evaluación terapéutica"

    return {
        "urgencia": urgency,
        "requiere_traslado": requiere_traslado,
        "motivo": motivo
    }


def format_roberto_notification(
    full_name: str,
    phone_or_user: str,
    perfil: str,
    urgencia: str,
    servicio_requerido: str,
    mensaje_original: str
) -> str:
    """Formatea la ficha de lead para enviarla a Roberto Lara vía WhatsApp wacli."""
    
    emoji_urgencia = "🚨" if urgencia == "ATENCION_INMEDIATA" else ("🔴" if urgencia == "ALTA" else "🟡")
    
    text = (
        f"🚨 *NUEVO LEAD DE TU BANDERA A.C.*\n"
        f"====================================\n"
        f"👤 *Contacto*: {full_name} ({phone_or_user})\n"
        f"🏷 *Perfil*: {perfil}\n"
        f"{emoji_urgencia} *Diagnóstico de Urgencia*: {urgencia}\n"
        f"🩺 *Servicio Solicitado*: {servicio_requerido}\n\n"
        f"💬 *Mensaje Original*:\n\"{mensaje_original[:250]}\"\n"
        f"====================================\n"
        f"📲 *Acción sugerida*: Contactar inmediatamente."
    )
    return text
