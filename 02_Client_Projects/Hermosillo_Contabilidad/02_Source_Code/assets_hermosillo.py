#!/usr/bin/env python3
"""ASSETS HERMOSILLO — Catálogo de assets por servicio (fotos/beneficios).

Prompts evaluados estilo asset_generation.py de Aztrotech.
Cada servicio tiene: prompt de imagen, texto de beneficios, pregunta de calificación.
Los assets se envían al lead como imagen tras detectar el servicio de interés.
"""

ASSETS_HERMOSILLO = {
    "contabilidad": {
        "id": "img_contabilidad",
        "prompt": (
            "A modern accountant's desk in a bright Hermosillo office, no chaos, "
            "a financial dashboard on a laptop showing clean charts and balance sheets, "
            "documents neatly organized, a friendly professional accountant smiling, "
            "warm golden light, sense of order and trust, photorealistic, 8k --ar 16:9 --style raw"
        ),
        "beneficio": (
            "📊 Tu contabilidad mensual bajo control: estados financieros claros, IVA e ISR al día, "
            "sin multas ni sorpresas del SAT. Tú te enfocas en tu negocio, yo en los números."
        ),
        "pregunta": "¿Ya llevas contabilidad o estás empezando tu negocio?",
    },
    "administracion": {
        "id": "img_administracion",
        "prompt": (
            "A clean administrative control center: employee payroll chart on screen, "
            "cash flow dashboard, expense tracking, organized workflow, professional small business "
            "office in Hermosillo, blue and teal accents, photorealistic, 8k --ar 16:9"
        ),
        "beneficio": (
            "⚙️ Administración que se mueve sola: nómina, flujo de caja y control de gastos "
            "en un solo lugar. Menos errores, mejor control, más tranquilidad."
        ),
        "pregunta": "¿Manejas actualmente nómina o flujo de caja manual?",
    },
    "manifestacion_importacion": {
        "id": "img_manifestacion",
        "prompt": (
            "A shipping container at the port of Guaymas at sunset, customs paperwork "
            "with official stamps on a clean desk, import manifest document, professional "
            "logistics atmosphere, golden hour light, photorealistic, 8k --ar 16:9"
        ),
        "beneficio": (
            "🚢 Manifestación de importación sin dolores de cabeza: papeles en regla, requisitos "
            "completos, tu mercancía cruza sin retrasos ni multas."
        ),
        "pregunta": "¿Qué mercancía importas y con qué frecuencia?",
    },
    "marketing": {
        "id": "img_marketing",
        "prompt": (
            "A growing business showcase, social media campaign on multiple screens, "
            "charts showing customer growth, vibrant but professional, young entrepreneur "
            "in Hermosillo, purple and gold accents, photorealistic, 8k --ar 16:9"
        ),
        "beneficio": (
            "📈 Marketing que trae clientes: presencia profesional, campañas enfocadas y "
            "crecimiento medible para tu negocio."
        ),
        "pregunta": "¿Tienes presencia en redes hoy? ¿Qué te gustaría crecer?",
    },
    "consultas_sat": {
        "id": "img_consultas_sat",
        "prompt": (
            "A professional helping a business owner understand official tax documentation, "
            "computer screen showing SAT portal, reassuring atmosphere, Hermosillo office, "
            "trust and relief on faces, photorealistic, 8k --ar 16:9"
        ),
        "beneficio": (
            "🗂️ Consultas ante el SAT sin burocracia: aclaraciones, trámites y respuestas "
            "rápidas para que no te bloqueen ni multen."
        ),
        "pregunta": "¿Qué consulta o aclaración necesitas ante el SAT?",
    },
    "citas_sat": {
        "id": "img_citas_sat",
        "prompt": (
            "A clear calendar showing an appointment scheduled at SAT office, "
            "smartphone with confirmation notification, organized professional setting, "
            "Hermosillo, green accents, photorealistic, 8k --ar 16:9"
        ),
        "beneficio": (
            "📅 Agendamos tu cita ante el SAT: fecha y hora asegurada, sin filas, sin "
            "batallar. Tú llegas, nosotros ya hicimos el trámite."
        ),
        "pregunta": "¿Para qué trámite ante el SAT necesitas la cita?",
    },
}


def get_asset(servicio: str) -> dict | None:
    """Retorna el asset del servicio o None."""
    return ASSETS_HERMOSILLO.get(servicio, {}).get(servicio, ASSETS_HERMOSILLO.get(servicio))


def list_assets() -> list[str]:
    return list(ASSETS_HERMOSILLO.keys())