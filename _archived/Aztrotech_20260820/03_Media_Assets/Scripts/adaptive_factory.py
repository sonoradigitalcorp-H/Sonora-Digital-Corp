#!/usr/bin/env python3
"""Adaptive Agent Factory — Plantilla para agentes por nicho.

Crea agentes que se adaptan a cualquier industria:
- Restaurantes
- Clínicas
- Clases de música
- Inmobiliaria
- Venta de equipos
- Servicios B2B

Uso:
    python3 adaptive_factory.py --niche restaurantes --branding "Comida Rápida GDL"
    python3 adaptive_factory.py --niche clinic --brand "DentalCare MX"
"""
import os, json, subprocess
from pathlib import Path
from datetime import datetime

TEMPLATES = {
    "restaurantes": {
        "name": "Asistente de Restaurantes",
        "description": "Tomar pedidos, gestionar reservas, atender reclamos",
        "skills": ["pedidos", "reservas", "menu", "horarios", "promociones"],
        "tone": "amable_cálido",
        "packages": [
            {"name": "Básico", "price": 299, "features": ["Atiende pedidos 24/7", "Recepciona reservas"]},
            {"name": "Premium", "price": 599, "features": ["Todo el Básico", "Menú interactivo", "Promociones personalizadas"]},
            {"name": "Enterprise", "price": 999, "features": ["Todo el Premium", "Gestión pedidos múltiples", "Integración POS"]}
        ],
        "questions": [
            "¿Tienes menú online?", "¿Aceptan delivery?", "¿Horarios de atención?",
            "¿Reservas con anticipación?", "¿Tienes promociones?"
        ]
    },
    "clinicas": {
        "name": "Asistente Médico",
        "description": "Calendarizar citas, recordatorios, informaciones básicas",
        "skills": ["citas", "recordatorios", "horarios", "urgencias", "servicios"],
        "tone": "profesional_amable",
        "packages": [
            {"name": "Básico", "price": 199, "features": ["Agenda citas automáticamente", "Recordatorios SMS"]},
            {"name": "Premium", "price": 399, "features": ["Todo el Básico", "Historial paciente", "Seguro médico"]},
            {"name": "Enterprise", "price": 699, "features": ["Todo el Premium", "Múltiples especialidades", "Telemedicina"]}
        ],
        "questions": [
            "¿Qué servicios ofrecen?", "¿Tomen citas por línea?", "¿Tienen cirugía?",
            "¿Aceptan seguros?", "¿Horarios de emergencias?"
        ]
    },
    "musica": {
        "name": "Asistente de Clases de Música",
        "description": "Agenda clases, envía recordatorios, captura estudiantes",
        "skills": ["clases", "recordatorios", "materiales", "progreso", "pagos"],
        "tone": "animado_educativo",
        "packages": [
            {"name": "Individual", "price": 149, "features": ["Clase 1 a 1 estudiante", "Recordatorios semanales"]},
            {"name": "Grupal", "price": 299, "features": ["Hasta 5 estudiantes", "Materiales digitales", "Progreso mensual"]},
            {"name": "Pro", "price": 499, "features": ["Agenda ilimitada", "Música ejemplos", "Evaluaciones trimestrales"]}
        ],
        "questions": [
            "¿Qué instrumentos enseñan?", "¿Cuándo empezar?", "¿Materiales incluidos?",
            "¿Puedo practicar por casa?", "¿Lecciones para niños?"
        ]
    },
    "inmobiliaria": {
        "name": "Asistente Inmobiliario",
        "description": "Captura leads, muestra propiedades, agenda visitas",
        "skills": ["propiedades", "visitas", "lead_scoring", "comparativa", "cita_propietario"],
        "tone": "profesional_persistente",
        "packages": [
            {"name": "Básico", "price": 399, "features": ["Captura leads cualificados", "Agenda visitas"]},
            {"name": "Growth", "price": 799, "features": ["Todo el Básico", "Propiedades destacadas", "Comparativa mercado"]},
            {"name": "Enterprise", "price": 1499, "features": ["Todo el Growth", "Pipeline ventas completo", "Análisis mercado"]}
        ],
        "questions": [
            "¿Tienen propiedades en mi rango?", "¿Cuánto cuesta vender?", "¿Cuándo puedo ver?",
            "¿Proceso de cierre?", "¿Comisión?"
        ]
    }
}


def create_adaptive_agent(niche: str, brand: str, tenant: str = "custom") -> dict:
    """Crea agente adaptado a un nicho específico."""
    template = TEMPLATES.get(niche.lower())
    if not template:
        return {"error": f"Nicho '{niche}' no soportado. Nichos: {list(TEMPLATES.keys())}"}

    # Personalizar mensajes
    system_prompt = f"""
Eres {template['name']} de {brand}. Eres {template['tone']}.

Descripción: {template['description']}

Habilidades principales: {', '.join(template['skills'])}

Reglas:
- Nunca des precios exactos, menciona 'partir de ${{price}} MXN' o pregunta por presupuesto
- Si no sabes algo, di 'déjame consultar con el dueño'
- Si preguntan por precios de paquetes, menciona: {json.dumps(template['packages'])}
- Si preguntan por dudas específicas, usa: {json.dumps(template['questions'])}

Mantén las respuestas cortas, claras y orientadas a la acción.
"""

    # Crear agente en OpenClaw
    agent_id = f"{tenant}_{niche}"

    return {
        "status": "created",
        "agent_id": agent_id,
        "tenant": tenant,
        "niche": niche,
        "brand": brand,
        "system_prompt": system_prompt,
        "packages": template["packages"],
        "skills": template["skills"],
        "next_questions": template["questions"]
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Adaptive Agent Factory")
    ap.add_argument("--niche", required=True, help="Nicho (restaurantes, clinicas, musica, inmobiliaria)")
    ap.add_argument("--brand", required=True, help="Nombre de la marca/empresa")
    ap.add_argument("--tenant", default="custom", help="Tenant ID")
    args = ap.parse_args()

    result = create_adaptive_agent(args.niche, args.brand, args.tenant)
    print(json.dumps(result, indent=2, ensure_ascii=False))