import json
import os

NICHES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "tests", "promptfoo", "niches")

OBJECTION_PHRASES = {
    "precio": ["muy caro", "no tengo presupuesto", "cuánto cuesta", "no me alcanza"],
    "satisfecho": ["ya tengo", "estoy bien así", "ya trabajo con", "estoy contento con", "estoy satisfecho"],
    "tiempo": ["después", "ahorita no", "no tengo tiempo", "estoy ocupado", "lo pienso", "te aviso"],
    "interes": ["no me interesa", "no necesito", "no sirve", "no gracias"],
    "confianza": ["no sé si sirva", "no conozco", "es la primera vez", "quién eres"],
}


def detect_objection(text):
    text_lower = text.lower()
    for category, phrases in OBJECTION_PHRASES.items():
        for phrase in phrases:
            if phrase in text_lower:
                return category, phrase
    return None, None


def get_niche_for_company(company, tenant_niche=None):
    if tenant_niche and tenant_niche in os.listdir(NICHES_DIR):
        return tenant_niche
    company_lower = company.lower()
    niche_map = {
        "barber": "agencies",
        "barbería": "agencies",
        "music": "music",
        "música": "music",
        "artista": "music",
        "abogado": "prof_services",
        "bufete": "prof_services",
        "restaurant": "ecommerce",
        "tacos": "ecommerce",
        "comida": "ecommerce",
        "tienda": "ecommerce",
    }
    for kw, niche in niche_map.items():
        if kw in company_lower:
            return niche
    return "general"
