#!/usr/bin/env python3
"""lead_scoring.py — Motor determinista de scoring cold/warm/hot.

Cero LLM. Solo reglas de negocio + OKF.
Cada factor tiene peso. Score total → clasificación.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScoringResult:
    score: int
    classification: str  # COLD / WARM / HOT
    factores: list[str]
    next_action: str
    prioridad: int  # 1=urgente, 2=seguimiento, 3=nurturing


# Pesos por factor (máximo 100)
WEIGHTS = {
    # Datos básicos (max 30)
    "tiene_nombre": 5,
    "tiene_empresa": 10,
    "tiene_giro": 5,
    "tiene_tamano_equipo": 5,
    "tiene_servicio": 5,

    # Intención clara (max 25)
    "cita_agendada": 15,
    "fecha_tentativa": 8,
    "presupuesto_mencionado": 10,

    # Urgencia/Autoridad (max 25)
    "urgencia_alta": 15,
    "es_tomador_decisiones": 10,

    # Engagement (max 20)
    "respondio_voz": 5,
    "pidio_asset": 5,
    "click_diagnostico": 10,
}

# Servicios Aztrotech (data real)
SERVICIOS_AZTROTECH = [
    "empleado_digital",      # Starter/Growth/Enterprise AI Agent
    "automatizaciones",       # Flujos + reportes + integraciones
    "plataforma_medida",     # CRM/ERP/Apps a medida
    "plataforma_juridica",   # Despachos jurídicos
    "plataforma_inmobiliaria", # Inmobiliarias
    "academia_interna",       # Manuales + SOPs + IA por depto
    "diagnostico_ia",         # Gratuito 30 min
]

# Giros de ejemplo (para validación)
GIROS = [
    "comercio_retail", "servicios_profesionales", "salud_bienestar",
    "gastronomia_hospitality", "construccion_manufactura", "educacion_elearning",
    "distribucion_industrial", "e_commerce", "juridico", "inmobiliario",
    "tecnologia", "otro"
]


def calculate_lead_score(
    lead: dict[str, Any],
    interacciones: list[dict] = None
) -> ScoringResult:
    """
    Calcula score determinista del lead.
    Solo reglas de negocio, cero LLM.

    Args:
        lead: dict con campos del lead (nombre, empresa, giro, tamano_equipo, servicio, etc.)
        interacciones: lista de interacciones previas [{tipo, timestamp, duracion, etc.}]

    Returns:
        ScoringResult con score, clasificación, factores, next_action, prioridad
    """
    score = 0
    factores = []

    # --- Datos básicos (max 30) ---
    if lead.get("nombre"):
        score += WEIGHTS["tiene_nombre"]
        factores.append(f"nombre:+{WEIGHTS['tiene_nombre']}")
    if lead.get("empresa"):
        score += WEIGHTS["tiene_empresa"]
        factores.append(f"empresa:+{WEIGHTS['tiene_empresa']}")
    if lead.get("giro"):
        score += WEIGHTS["tiene_giro"]
        factores.append(f"giro:+{WEIGHTS['tiene_giro']}")
    if lead.get("tamano_equipo"):
        score += WEIGHTS["tiene_tamano_equipo"]
        factores.append(f"tamano:+{WEIGHTS['tiene_tamano_equipo']}")
    if lead.get("servicio"):
        score += WEIGHTS["tiene_servicio"]
        factores.append(f"servicio:+{WEIGHTS['tiene_servicio']}")

    # --- Intención clara (max 25) ---
    if lead.get("fecha") and lead.get("hora"):
        score += WEIGHTS["cita_agendada"]
        factores.append(f"cita_agendada:+{WEIGHTS['cita_agendada']}")
    elif lead.get("fecha"):
        score += WEIGHTS["fecha_tentativa"]
        factores.append(f"fecha_tentativa:+{WEIGHTS['fecha_tentativa']}")
    if lead.get("presupuesto_mencionado"):
        score += WEIGHTS["presupuesto_mencionado"]
        factores.append(f"presupuesto:+{WEIGHTS['presupuesto_mencionado']}")

    # --- Urgencia/Autoridad (max 25) ---
    if lead.get("urgencia_alta"):
        score += WEIGHTS["urgencia_alta"]
        factores.append(f"urgencia:+{WEIGHTS['urgencia_alta']}")
    if lead.get("es_tomador_decisiones"):
        score += WEIGHTS["es_tomador_decisiones"]
        factores.append(f"autoridad:+{WEIGHTS['es_tomador_decisiones']}")

    # --- Engagement (max 20) ---
    if lead.get("respondio_voz"):
        score += WEIGHTS["respondio_voz"]
        factores.append(f"voz:+{WEIGHTS['respondio_voz']}")
    if lead.get("pidio_asset"):
        score += WEIGHTS["pidio_asset"]
        factores.append(f"asset:+{WEIGHTS['pidio_asset']}")
    if lead.get("click_diagnostico"):
        score += WEIGHTS["click_diagnostico"]
        factores.append(f"diagnostico:+{WEIGHTS['click_diagnostico']}")

    # --- Bonus por interacciones previas ---
    if interacciones:
        total_interacciones = len(interacciones)
        if total_interacciones >= 5:
            bonus = min(10, total_interacciones * 2)
            score += bonus
            factores.append(f"engagement_bonus:+{bonus}")

    # --- Bonuses especiales ---
    # Enterprise potential: empresa + 20+ empleados + servicio complejo
    if (lead.get("empresa") and
        lead.get("tamano_equipo") in ["20+", "6-20"] and
        lead.get("servicio") in ["plataforma_medida", "academia_interna", "automatizaciones"]):
        bonus = 10
        score += bonus
        factores.append(f"enterprise_potential:+{bonus}")

    # Diagnóstico hecho = lead calentado
    if lead.get("diagnostico_completado"):
        bonus = 15
        score += bonus
        factores.append(f"diagnostico_hecho:+{bonus}")

    # Limitar score a 0-100
    score = max(0, min(100, score))

    # Clasificación
    if score >= 70:
        classification = "HOT"
        prioridad = 1
        next_action = _next_action_hot(lead)
    elif score >= 40:
        classification = "WARM"
        prioridad = 2
        next_action = _next_action_warm(lead)
    else:
        classification = "COLD"
        prioridad = 3
        next_action = _next_action_cold(lead)

    return ScoringResult(
        score=score,
        classification=classification,
        factores=factores,
        next_action=next_action,
        prioridad=prioridad
    )


def _next_action_hot(lead: dict) -> str:
    """Acción concreta para lead HOT."""
    if lead.get("fecha") and lead.get("hora"):
        return f"Llamar HOY a las {lead['hora']} - Lead HOT con cita confirmada"
    return "Llamar HOY - Lead HOT sin cita: agendar diagnóstico inmediato"


def _next_action_warm(lead: dict) -> str:
    """Acción concreta para lead WARM."""
    servicio = lead.get("servicio", "general")
    if servicio == "empleado_digital":
        return "Enviar caso Suministros Palominos + Jewelry Remate MX como prueba social"
    elif servicio == "automatizaciones":
        return "Enviar diagnóstico IA gratuito + preguntar procesos actuales"
    elif servicio in ["plataforma_medida", "plataforma_juridica", "plataforma_inmobiliaria"]:
        return "Enviar demo de plataforma especializada + agendar diagnóstico"
    return "Enviar diagnóstico IA gratuito (30 min, gratis)"


def _next_action_cold(lead: dict) -> str:
    """Acción concreta para lead COLD."""
    return "Nurturing: enviar contenido de valor + ofrecer diagnóstico IA gratis"


def classify_by_giro(giro: str) -> dict[str, Any]:
    """Clasifica servicio recomendado por giro (determinista)."""
    giro_map = {
        "comercio_retail": {"servicio_recomendado": "empleado_digital", "caso": "Jewelry Remate MX"},
        "e_commerce": {"servicio_recomendado": "empleado_digital + automatizaciones", "caso": "Jewelry Remate MX (+50% ventas)"},
        "servicios_profesionales": {"servicio_recomendado": "plataforma_juridica", "caso": "Plataforma Jurídica"},
        "juridico": {"servicio_recomendado": "plataforma_juridica", "caso": "Plataforma Jurídica (expedientes, audiencias, documentos)"},
        "inmobiliario": {"servicio_recomendado": "plataforma_inmobiliaria", "caso": "Plataforma Inmobiliaria (propiedades, prospectos, match IA)"},
        "salud_bienestar": {"servicio_recomendado": "empleado_digital + academia_interna", "caso": "Agenda citas + recuerda mediciones"},
        "gastronomia_hospitality": {"servicio_recomendado": "empleado_digital", "caso": "Agente toma pedidos 24/7, reserva mesas"},
        "construccion_manufactura": {"servicio_recomendado": "plataforma_medida + automatizaciones", "caso": "Suministros Palominos (ERP completo)"},
        "distribucion_industrial": {"servicio_recomendado": "plataforma_medida + academia_interna", "caso": "Suministros Palominos (ERP + GPTs + Academia)"},
        "educacion_elearning": {"servicio_recomendado": "academia_interna + empleado_digital", "caso": "Academia Interna (manuales, SOPs, asistente IA)"},
        "tecnologia": {"servicio_recomendado": "plataforma_medida + automatizaciones", "caso": "Desarrollo software a medida"},
    }
    return giro_map.get(giro, {"servicio_recomendado": "diagnostico_ia", "caso": "Empezar con diagnóstico gratuito"})


def get_objeciones_por_servicio(servicio: str) -> list[dict[str, str]]:
    """Retorna objeciones comunes y contraargumentos evaluados por servicio."""
    objeciones = {
        "empleado_digital": [
            {"objecion": "Es muy caro", "contraargumento": "El paquete Starter es $999 USD. Un empleado humano cuesta $1,500+/mes. El agente trabaja 24/7 sin vacaciones. ROI en 2-3 meses."},
            {"objecion": "No confío en la IA", "contraargumento": "Puedes verlo funcionando HOY. Diagnosticamos gratis y te mostramos cómo atiende. Sin compromiso."},
            {"objecion": "Ya tengo WhatsApp", "contraargumento": "El agente NO reemplaza WhatsApp, lo potencia. Responde en segundos 24/7, captura leads, agenda solo. Tú duermes, él vende."},
            {"objecion": "No sé si funciona para mi industria", "contraargumento": "Ya lo tenemos funcionando en joyería (+50% ventas), distribución industrial y servicios. Diagnóstico gratis y te decimos si aplica."},
            {"objecion": "Necesito pensarlo", "contraargumento": "Perfecto, toma tu tiempo. El diagnóstico es gratis y sin compromiso. ¿Te parece mañana a las 10? Mientras tanto te mando info."},
        ],
        "automatizaciones": [
            {"objecion": "No tengo tiempo para implementar", "contraargumento": "Nosotros lo implementamos todo. Tú solo nos dices qué procesos te quitan tiempo. En 2-6 semanas está operando."},
            {"objecion": "Mi negocio es muy pequeño", "contraargumento": "El diagnóstico es gratis. Te decimos exactamente qué automatizar primero. No necesitas ser grande, necesitas ser inteligente."},
            {"objecion": "Ya tengo un sistema", "contraargumento": "Integramos con lo que ya tienes. No reemplazamos, conectamos. WhatsApp + Excel + tu sistema actual = todo unido."},
        ],
        "plataforma_medida": [
            {"objecion": "Es muy complejo", "contraargumento": "Nosotros lo construimos. Tú describes tu proceso, nosotros lo digitalizamos. 5 pasos: diagnóstico → arquitectura → construcción → implementación → optimización."},
            {"objecion": "No tengo presupuesto", "contraargumento": "Cotización por proyecto con alcance definido. Sin sorpresas. Empiezas con el diagnóstico (gratis) y decides."},
            {"objecion": "Otros cotizaron más barato", "contraargumento": "No vendemos herramientas, construimos SISTEMAS que operan tu negocio. La diferencia es que funciona, no que es bonito."},
        ],
    }

    # Servicio base
    base = objeciones.get(servicio, objeciones["empleado_digital"])

    # Agregar objeciones generales
    base.extend([
        {"objecion": "No tengo tiempo ahora", "contraargumento": "El diagnóstico dura 30 min y es gratis. Mañana a las 10?"},
        {"objecion": "Déjame consultarlo", "contraargumento": "Claro, ¿con quién lo consultas? Te preparo un resumen que le sirva."},
    ])

    return base


def get_template_notificacion_cesar(lead: dict, scoring: ScoringResult, intelligence: dict = None) -> str:
    """Genera template de notificación para César con formato CRM."""
    servicio_map = {
        "empleado_digital": "Empleado Digital (Agente IA)",
        "automatizaciones": "Automatizaciones",
        "plataforma_medida": "Plataforma a medida (CRM/ERP/App)",
        "plataforma_juridica": "Plataforma Jurídica",
        "plataforma_inmobiliaria": "Plataforma Inmobiliaria",
        "academia_interna": "Academia Interna",
        "diagnostico_ia": "Diagnóstico IA (solo info)",
    }

    servicio_display = servicio_map.get(lead.get("servicio", ""), lead.get("servicio", "No especificado"))

    lines = [
        f"{'🔥' if scoring.classification == 'HOT' else '🟡' if scoring.classification == 'WARM' else '🔵'} LEAD {scoring.classification} ({scoring.score}/100)",
        f"",
        f"👤 {lead.get('nombre', 'Sin nombre')}",
        f"🏢 {lead.get('empresa', 'Sin empresa')} — {lead.get('giro', 'Sin giro')}",
        f"👥 {lead.get('tamano_equipo', 'Sin tamaño')} empleados",
        f"🎯 Servicio: {servicio_display}",
        f"📅 Cita: {lead.get('fecha', 'Pendiente')} {lead.get('hora', '')}",
        f"💬 Canal: {lead.get('canal', 'telegram')}",
        f"",
    ]

    if intelligence:
        lines.append(f"📊 RESUMEN: {intelligence.get('resumen_empresa', 'Pendiente')}")
        objeciones = intelligence.get("objeciones", [])
        if objeciones:
            lines.append(f"⚠️ OBJECIONES: {'; '.join(objeciones[:3])}")
        lines.append(f"🎯 NEXT: {intelligence.get('next_action', scoring.next_action)}")
    else:
        lines.append(f"🎯 NEXT: {scoring.next_action}")

    lines.extend([
        f"",
        f"📋 Score factores: {', '.join(scoring.factores[:5])}",
        f"",
        f"👉 Responder con: /llamar {lead.get('chat_id', '?')} | /reagendar {lead.get('chat_id', '?')} | /cerrar {lead.get('chat_id', '?')}",
    ])

    return "\n".join(lines)
