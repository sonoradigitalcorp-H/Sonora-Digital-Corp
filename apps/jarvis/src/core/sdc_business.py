"""
SDC Business Layer — Planes, suscripciones, onboarding y CRM.
Conecta la infraestructura JARVIS con el modelo de negocio de Sonora Digital Corp.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any

log = logging.getLogger("jarvis.sdc")

PLANS = {
    "explorador": {
        "name": "Explorador",
        "price": 0,
        "features": ["mystic_basic", "photos_5", "videos_2", "web_1", "community_read"],
        "limits": {"photos": 5, "videos": 2, "webs": 1, "tokens": 0, "automations": 0},
    },
    "conquistador": {
        "name": "Conquistador",
        "price": 39,
        "features": [
            "mystic_247",
            "photos_150",
            "videos_50",
            "webs_3",
            "store_pod",
            "clon_text",
            "tokens_300",
            "analytics_basic",
            "automations_5",
            "community_chat",
        ],
        "limits": {
            "photos": 150,
            "videos": 50,
            "webs": 3,
            "tokens": 300,
            "automations": 5,
        },
    },
    "agente_ia": {
        "name": "Agente IA",
        "price": 69,
        "features": [
            "mystic_priority",
            "photos_750",
            "videos_250",
            "webs_10",
            "store_pod_printful",
            "clon_voice_video",
            "tokens_1500",
            "crm_kpi",
            "automations_30",
            "community_own",
            "no_branding",
            "affiliate_7",
        ],
        "limits": {
            "photos": 750,
            "videos": 250,
            "webs": 10,
            "tokens": 1500,
            "automations": 30,
        },
    },
    "imperio": {
        "name": "Imperio",
        "price": 149,
        "features": [
            "mystic_dedicated",
            "photos_unlimited",
            "videos_unlimited",
            "webs_unlimited",
            "store_marketplace",
            "clon_premium",
            "tokens_7500",
            "crm_full",
            "automations_unlimited",
            "community_moderated",
            "white_label",
            "affiliate_15",
            "kyc_legal",
            "api_public",
            "beta_features",
        ],
        "limits": {
            "photos": -1,
            "videos": -1,
            "webs": -1,
            "tokens": 7500,
            "automations": -1,
        },
    },
}

ADULT_MULTIPLIER = 2.0

NICHO_PROFILES = {
    "musica": {"skills": ["fal-ai-video", "music-gen"], "agents": ["code", "research"]},
    "fitness": {"skills": ["content-fitness"], "agents": ["voice", "skill"]},
    "educacion": {"skills": ["course-creator"], "agents": ["research", "code"]},
    "ecommerce": {"skills": ["shopify", "printful"], "agents": ["skill"]},
    "creativo": {"skills": ["fal-ai", "meme-maker"], "agents": ["skill", "voice"]},
    "adulto": {
        "skills": ["sdc-digital-twin", "sdc-content-adult", "kyc"],
        "agents": ["hermes", "voice"],
        "multiplier": ADULT_MULTIPLIER,
    },
    "empresa": {
        "skills": ["crm", "kpi-dashboard", "legal-docs"],
        "agents": ["gbrain", "review", "openclaw"],
    },
}


def get_plan(plan_id: str) -> Optional[Dict]:
    return PLANS.get(plan_id)


def list_plans() -> List[Dict]:
    return [{"id": k, **v} for k, v in PLANS.items()]


def calculate_price(plan_id: str, nicho: str = "general") -> float:
    plan = get_plan(plan_id)
    if not plan:
        return 0
    price = plan["price"]
    profile = NICHO_PROFILES.get(nicho, {})
    multiplier = profile.get("multiplier", 1.0)
    return round(price * multiplier, 2)


def recommend_plan(tipo: str, necesidad: str, nicho: str = "general") -> str:
    if tipo == "empresa":
        return "imperio"
    if necesidad in ("todo", "automatizar"):
        return "agente_ia"
    if necesidad in ("vender", "contenido", "web"):
        return "conquistador"
    return "explorador"


def get_features(plan_id: str, nicho: str = "general") -> List[str]:
    plan = get_plan(plan_id)
    if not plan:
        return []
    features = list(plan["features"])
    profile = NICHO_PROFILES.get(nicho, {})
    if profile.get("multiplier", 1.0) > 1:
        features.append("adult_multiplier_x2")
    return features


def get_nicho_profile(nicho: str) -> Dict:
    return NICHO_PROFILES.get(nicho, {"skills": [], "agents": []})


class SDCCustomer:
    def __init__(self, neo4j_store=None):
        self.neo4j = neo4j_store

    def create(self, data: Dict) -> Optional[Dict]:
        customer_id = str(uuid.uuid4())
        customer = {
            "id": customer_id,
            "nombre": data.get("nombre", ""),
            "email": data.get("email", ""),
            "telefono": data.get("telefono", ""),
            "tipo": data.get("tipo", "persona"),
            "nicho": data.get("nicho", "general"),
            "plan": data.get("plan", "explorador"),
            "status": "trial",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if self.neo4j:
            try:
                driver = self.neo4j.get_driver()
                if driver:
                    with driver.session() as session:
                        session.run(
                            "CREATE (c:Customer {id: $id, nombre: $nombre, email: $email, "
                            "telefono: $telefono, tipo: $tipo, nicho: $nicho, plan: $plan, "
                            "status: $status, created_at: $created_at, updated_at: $updated_at})",
                            **customer,
                        )
                        log.info(f"Customer created in Neo4j: {customer_id}")
            except Exception as e:
                log.warning(f"Neo4j customer creation failed: {e}")
        return customer

    def get(self, customer_id: str) -> Optional[Dict]:
        if self.neo4j:
            try:
                driver = self.neo4j.get_driver()
                if driver:
                    with driver.session() as session:
                        result = session.run(
                            "MATCH (c:Customer {id: $id}) RETURN c", id=customer_id
                        )
                        record = result.single()
                        if record:
                            return dict(record["c"])
            except Exception as e:
                log.warning(f"Neo4j customer get failed: {e}")
        return None


class SDCOnboarding:
    def __init__(self, neo4j_store=None):
        self.customers = SDCCustomer(neo4j_store)

    def process(self, answers: Dict) -> Dict:
        tipo = answers.get("tipo", "persona")
        nicho = answers.get("nicho", "general")
        necesidad = answers.get("necesidad", "explorar")

        plan = recommend_plan(tipo, necesidad, nicho)
        price = calculate_price(plan, nicho)
        features = get_features(plan, nicho)
        profile = get_nicho_profile(nicho)

        customer = self.customers.create(
            {
                "nombre": answers.get("nombre", ""),
                "email": answers.get("email", ""),
                "telefono": answers.get("telefono", ""),
                "tipo": tipo,
                "nicho": nicho,
                "plan": plan,
            }
        )

        return {
            "status": "onboarded",
            "customer_id": customer["id"] if customer else None,
            "plan": plan,
            "plan_name": get_plan(plan)["name"] if get_plan(plan) else plan,
            "price": price,
            "features": features,
            "nicho_profile": profile,
            "stripe_checkout_url": None,  # Se genera al conectar Stripe
        }
