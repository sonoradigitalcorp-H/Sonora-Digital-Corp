import os

TOKEN = os.getenv("NATHY_CONTA_TOKEN", "8720440822:AAHAZcdNd1cZg1QI6GB48t27blhe2bkD-Hw")
BOT_USERNAME = "Nathy_Conta_bot"

WEBHOOK_URL = os.getenv("NATHY_CONTA_WEBHOOK_URL", "")

PRICING = {
    "esencial": {
        "name": "Plan Esencial",
        "price": "$1,499/mes",
        "features": [
            "Contabilidad mensual",
            "Declaraciones bimestrales",
            "Facturación CFDI ilimitada",
            "Asesoría vía Telegram",
        ],
        "for": "Freelancers y startups",
    },
    "profesional": {
        "name": "Plan Profesional",
        "price": "$3,999/mes",
        "features": [
            "Todo lo de Esencial",
            "Nóminas (hasta 10 empleados)",
            "Estados financieros mensuales",
            "Dashboard contable",
            "Declaración anual",
        ],
        "for": "Empresas en crecimiento",
    },
    "enterprise": {
        "name": "Plan Enterprise",
        "price": "$9,999/mes",
        "features": [
            "Todo lo de Profesional",
            "Nóminas ilimitadas",
            "Consolidación financiera",
            "Auditoría preventiva",
            "Manager dedicado",
        ],
        "for": "Corporaciones y grupos",
    },
}
