from fastapi import APIRouter, HTTPException

router = APIRouter()

from src.core.sdc_business import (
    SDCOnboarding,
    calculate_price,
    get_features,
    get_nicho_profile,
    get_plan,
    list_plans,
    recommend_plan,
)

_sdc_onboarding = None


def get_sdc_onboarding():
    global _sdc_onboarding
    if _sdc_onboarding is None:
        try:
            from src.core.neo4j_store import get_driver

            _sdc_onboarding = SDCOnboarding(get_driver())
        except Exception:
            _sdc_onboarding = SDCOnboarding()
    return _sdc_onboarding


@router.get("/api/sdc/plans")
async def sdc_list_planes():
    return {"plans": list_plans()}


@router.get("/api/sdc/plan/{plan_id}")
async def sdc_get_plan(plan_id: str, nicho: str = "general"):
    plan = get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    price = calculate_price(plan_id, nicho)
    features = get_features(plan_id, nicho)
    return {
        "id": plan_id,
        **plan,
        "effective_price": price,
        "effective_features": features,
    }


@router.get("/api/sdc/nicho/{nicho}")
async def sdc_nicho_profile(nicho: str):
    return {"nicho": nicho, "profile": get_nicho_profile(nicho)}


@router.post("/api/sdc/onboarding")
async def sdc_onboarding(data: dict):
    return get_sdc_onboarding().process(data)


@router.post("/api/sdc/onboarding/mystic")
async def sdc_mystic_onboarding(data: dict):
    message = data.get("message", "").lower()
    step = data.get("step", 0)
    if step == 0:
        return {
            "step": 1,
            "question": "Cuéntame, ¿eres una persona creativa que quiere brillar, o representas a una empresa que busca crecer?",
            "options": [
                {"id": "persona", "label": "💪 Soy persona (creador, artista)"},
                {"id": "empresa", "label": "🏢 Soy empresa o agencia"},
                {"id": "no_se", "label": "🔍 No estoy seguro todavía"},
            ],
        }
    if step == 1:
        tipo = (
            "persona"
            if any(w in message for w in ["persona", "creador", "artista"])
            else "empresa"
        )
        return {
            "step": 2,
            "tipo": tipo,
            "question": "¡Qué emocionante! ¿Y en qué nicho te mueves?",
            "options": [
                {"id": "musica", "label": "🎵 Música"},
                {"id": "fitness", "label": "🏋️ Fitness"},
                {"id": "educacion", "label": "📚 Educación"},
                {"id": "ecommerce", "label": "🛍️ Ecommerce"},
                {"id": "creativo", "label": "🎨 Creativo"},
                {"id": "adulto", "label": "🔞 Adulto (+18)"},
                {"id": "otro", "label": "🌟 Otro"},
            ],
        }
    if step == 2:
        return {
            "step": 3,
            "nicho": message,
            "question": "Perfecto. ¿Qué es lo que más necesitas hoy?",
            "options": [
                {"id": "vender", "label": "💰 Vender más"},
                {"id": "contenido", "label": "📸 Crear contenido"},
                {"id": "automatizar", "label": "🤖 Automatizar procesos"},
                {"id": "web", "label": "🌐 Tener presencia web"},
                {"id": "todo", "label": "🔄 Todo lo anterior"},
            ],
        }
    if step == 3:
        tipo = data.get("tipo", "persona")
        nicho = data.get("nicho", "general")
        plan = recommend_plan(tipo, message, nicho)
        price = calculate_price(plan, nicho)
        plan_names = {
            "explorador": "🌘 Explorador",
            "conquistador": "⚔️ Conquistador",
            "agente_ia": "🛡️ Agente IA",
            "imperio": "🏆 Imperio",
        }
        return {
            "step": 4,
            "completed": True,
            "plan": plan,
            "plan_display": plan_names.get(plan, plan),
            "price": price,
            "message": f"Basado en lo que me contaste, tu plan ideal es **{plan_names.get(plan, plan)}** (${price}/mes). ¿Quieres que te lleve al checkout?",
            "next_url": f"/api/sdc/plan/{plan}",
        }
    return {"step": 0, "question": "Hola, soy Mystic. ¿En qué puedo ayudarte?"}
