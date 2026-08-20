"""Lead Classifier Híbrido — Reglas determinísticas + LLM few-shot para ambiguos.

Estrategia:
  1. Aplicar reglas (rápidas, 0 tokens) → si match claro (score alto), devolver.
  2. Si ambiguo → LLM few-shot con 10 ejemplos cold/warm/hot.
  3. Fusión: rule_score * 0.6 + llm_score * 0.4 (si LLM disponible).
  4. Output: tipo, confianza, razones, proxima_accion, datos_faltantes.
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

# Umbrales de decisión
CLEAR_THRESHOLD = 0.85
AMBIGUOUS_RANGE = (0.35, 0.85)


@dataclass
class LeadClassification:
    tipo: str  # cold | warm | hot
    confianza: float
    razones: List[str] = field(default_factory=list)
    proxima_accion: str = ""
    datos_faltantes: List[str] = field(default_factory=list)
    metodo: str = "rules"  # rules | llm | hybrid

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tipo": self.tipo,
            "confianza": round(self.confianza, 3),
            "razones": self.razones,
            "proxima_accion": self.proxima_accion,
            "datos_faltantes": self.datos_faltantes,
            "metodo": self.metodo,
        }


# ── Reglas determinísticas ──────────────────────────────────────
RULES = {
    "hot": {
        "intencion": [
            r"\b(contratar|comprar|empezar|registrarme|quiero\s+ya|necesito\s+ya)\b",
            r"\b(firmar|contrato|listos|aprobad|mandar.*contrato)\b",
            r"\b(empezamos|lunes|mañana|esta\s+semana|cuanto\s+antes)\b",
        ],
        "budget": [
            r"\b(presupuesto\s+(de|es)?\s*\$?\s*\d+|al\s+mes\s*\$?\s*\d+|tenemos\s+\$\d+)\b",
            r"\b(budget|approved|money\s+ready|we\s+have\s+\$\d+)\b",
        ],
        "urgencia": [
            r"\b(ya|urgente|inmediato|perdi\w*\s+clientes|no\s+(puedo|aguanto))\b",
            r"\b(now|asap|urgent|immediately|today|this\s+week|right\s+away|losing\s+customers)\b",
        ],
    },
    "warm": {
        "interes": [
            r"\b(me\s+interesa|me\s+gustaría|quisiera|quiero\s+saber\s+de)\b",
            r"\b(cuánto\s+cuesta|precio|cuanto\s+cuesta|cotizaci\w+|costo)\b",
            r"\b(comparar|alternativa|actualmente\s+uso|ya\s+tengo)\b",
            r"\b(i'?m\s+interested|want\s+to|i\s+would\s+like|how\s+much|price|quote|cost)\b",
            r"\b(automate|interested|recommend)\b",
        ],
        "contexto": [
            r"\b(tengo\s+una|tengo\s+un|mi\s+negocio|mi\s+empresa|trabajo\s+con|atiendo)\b",
            r"\b(tienda|restaurante|clínica|consultorio|estudio|agencia|consultora|barber|café|salón)\b",
            r"\b(i\s+have|my\s+business|my\s+company|i\s+own|clinic|restaurant|store|agency|consulting)\b",
        ],
        "dolor": [
            r"\b(no\s+(responde|contesta)|tardo|pierdo|no\s+alcanzo|mucho\s+tiempo|clientes\s+que\s+se\s+van)\b",
            r"\b(doesn'?t\s+(answer|respond)|slow|losing|miss|customers\s+leave|no\s+time)\b",
        ],
    },
    "cold": {
        "explorando": [
            r"\b(hola|buenas|buenos\s+días|qué\s+hacen|qué\s+ofrecen|qué\s+es)\b",
            r"\b(info|información|catálogo|más\s+información|solo\s+viendo|solo\s+estoy\s+viendo)\b",
            r"\b(gracias|ok|no\s+gracias)\b",
            r"\b(hello|hi|what\s+do\s+you\s+do|what\s+services|just\s+looking|information)\b",
            r"\b(thank\s*you|no\s+thanks)\b",
        ],
        "sin_compromiso": [
            r"\b(todavía\s+no|aún\s+no|no\s+tengo\s+negocio|apenas\s+empiezo|solo\s+consulto)\b",
            r"\b(not\s+yet|i\s+don'?t\s+have\s+a\s+business|just\s+checking)\b",
        ],
    },
}

# Proxima acción por tipo
NEXT_ACTIONS = {
    "hot": "Contactar a César INMEDIATAMENTE con datos completos del prospecto",
    "warm": "Calificar con preguntas BANT y agendar llamada con César",
    "cold": "Nutrir con educación sobre el servicio y capturar al menos nombre/teléfono",
}

MISSING_FOR_CLOSE = ["phone", "business_type", "budget"]


class LeadClassifier:
    def __init__(
        self,
        llm_call=None,
        fewshot_path: Optional[str] = None,
        use_llm: bool = True,
        locale: str = "es",
    ):
        """
        llm_call: callable async (messages: list) -> dict (OpenRouter-style, con choices[0].message.content)
        use_llm: si False, solo reglas determinísticas.
        """
        self.llm_call = llm_call
        self.use_llm = use_llm
        self.locale = locale
        if fewshot_path is None:
            fewshot_path = os.path.join(
                os.path.dirname(__file__), "prompts", "lead_classifier_fewshot.yaml"
            )
        self.fewshot = self._load_fewshot(fewshot_path)

    def _load_fewshot(self, path: str) -> List[Dict[str, Any]]:
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            return data.get("examples", [])
        except Exception as e:
            logger.warning(f"No se pudo cargar few-shot {path}: {e}")
            return []

    # ── Reglas ──────────────────────────────────────────────────
    def _rule_score(self, text: str) -> Dict[str, float]:
        scores = {"cold": 0.0, "warm": 0.0, "hot": 0.0}
        t = text.lower()
        for tipo, groups in RULES.items():
            total = 0
            for group, patterns in groups.items():
                for pat in patterns:
                    if re.search(pat, t):
                        total += 1
            if total:
                scores[tipo] = min(1.0, total * 0.3)
        return scores

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extrae business_type, budget, timeline de texto libre."""
        meta = {}
        business_types = {
            "restaurante": "restaurante", "tienda": "tienda", "clínica": "clinica",
            "consultorio": "consultorio", "barber": "barberia", "salón": "salon",
            "café": "cafe", "agencia": "agencia", "consultora": "consultoria",
            "estudio": "estudio", "médic": "salud",
        }
        t = text.lower()
        for kw, val in business_types.items():
            if kw in t:
                meta["business_type"] = val
                break
        m = re.search(r"\$?\s*(\d[\d,]*)\s*(k|mil|mxn|usd)?\s*(al\s*mes|/mes|mensual)?", t)
        if m:
            meta["budget_hint"] = m.group(0).strip()
        if re.search(r"\b(lunes|mañana|esta\s+semana|próximos\s+días|ya)\b", t):
            meta["timeline"] = "inmediato"
        return meta

    # ── LLM few-shot ────────────────────────────────────────────
    def _build_llm_prompt(self, conversation: List[str]) -> List[Dict[str, str]]:
        system = (
            "Eres un clasificador de leads B2B. Clasifica la conversación como "
            "cold, warm o hot. Responde SOLO con JSON: "
            '{"tipo":"cold|warm|hot","confianza":0.0-1.0,"razones":["..."],"datos_faltantes":["..."]}. '
            "Idioma: responde en español."
        )
        fewshot_msgs = []
        for ex in self.fewshot[:6]:
            conv_text = "\n".join(f"Cliente: {m}" for m in ex["conversation"])
            fewshot_msgs.append({"role": "user", "content": conv_text})
            fewshot_msgs.append({
                "role": "assistant",
                "content": json.dumps({
                    "tipo": ex["tipo"],
                    "confianza": 0.9,
                    "razones": ex["razones"],
                    "datos_faltantes": [],
                }),
            })
        conv_text = "\n".join(f"Cliente: {m}" for m in conversation)
        fewshot_msgs.append({"role": "user", "content": conv_text})
        return [{"role": "system", "content": system}] + fewshot_msgs

    async def _llm_classify(self, conversation: List[str]) -> Optional[Dict[str, Any]]:
        if not self.llm_call:
            return None
        try:
            messages = self._build_llm_prompt(conversation)
            result = await self.llm_call(messages)
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            # Extraer JSON del contenido
            m = re.search(r"\{.*\}", content, re.DOTALL)
            if not m:
                return None
            data = json.loads(m.group(0))
            if data.get("tipo") not in ("cold", "warm", "hot"):
                return None
            return data
        except Exception as e:
            logger.warning(f"LLM classify falló: {e}")
            return None

    # ── Main API ────────────────────────────────────────────────
    async def classify(
        self,
        conversation: List[str],
        rag_context: str = "",
    ) -> LeadClassification:
        """Clasifica conversación → LeadClassification."""
        if not conversation:
            return LeadClassification(tipo="cold", confianza=0.0, razones=["sin conversación"])

        full_text = " ".join(conversation)
        rule_scores = self._rule_score(full_text)
        meta = self._extract_metadata(full_text)

        # Determinar tipo dominante por reglas
        best_tipo = max(rule_scores, key=rule_scores.get)
        best_score = rule_scores[best_tipo]

        # Si reglas dan resultado claro
        if best_score >= CLEAR_THRESHOLD:
            razones = self._build_reasons(best_tipo, conversation)
            return LeadClassification(
                tipo=best_tipo,
                confianza=min(0.95, best_score + 0.1),
                razones=razones,
                proxima_accion=NEXT_ACTIONS.get(best_tipo, ""),
                datos_faltantes=self._missing_data(meta),
                metodo="rules",
            )

        # Ambiguo → LLM few-shot
        llm_data = None
        if self.use_llm:
            llm_data = await self._llm_classify(conversation)

        if llm_data:
            llm_score = float(llm_data.get("confianza", 0.5))
            llm_tipo = llm_data["tipo"]
            # Fusión híbrida
            if best_score > 0:
                fused = {
                    "cold": rule_scores["cold"] * 0.6 + (llm_score if llm_tipo == "cold" else 0) * 0.4,
                    "warm": rule_scores["warm"] * 0.6 + (llm_score if llm_tipo == "warm" else 0) * 0.4,
                    "hot": rule_scores["hot"] * 0.6 + (llm_score if llm_tipo == "hot" else 0) * 0.4,
                }
                final_tipo = max(fused, key=fused.get)
                final_conf = fused[final_tipo]
            else:
                final_tipo = llm_tipo
                final_conf = llm_score
            razones = llm_data.get("razones") or self._build_reasons(final_tipo, conversation)
            return LeadClassification(
                tipo=final_tipo,
                confianza=min(0.97, final_conf),
                razones=razones,
                proxima_accion=NEXT_ACTIONS.get(final_tipo, ""),
                datos_faltantes=llm_data.get("datos_faltantes") or self._missing_data(meta),
                metodo="hybrid" if best_score > 0 else "llm",
            )

        # Solo reglas (sin LLM)
        return LeadClassification(
            tipo=best_tipo,
            confianza=min(0.7, best_score + 0.2),
            razones=self._build_reasons(best_tipo, conversation),
            proxima_accion=NEXT_ACTIONS.get(best_tipo, ""),
            datos_faltantes=self._missing_data(meta),
            metodo="rules",
        )

    def _build_reasons(self, tipo: str, conversation: List[str]) -> List[str]:
        full = " ".join(conversation).lower()
        reasons = []
        for group, patterns in RULES.get(tipo, {}).items():
            for pat in patterns:
                if re.search(pat, full):
                    reasons.append(f"patrón: {group}")
                    break
        return reasons or [f"score de {tipo} por reglas"]

    def _missing_data(self, meta: Dict[str, Any]) -> List[str]:
        missing = []
        if "business_type" not in meta:
            missing.append("business_type")
        if "budget" not in meta and "budget_hint" not in meta:
            missing.append("budget")
        return missing


def create_classifier(llm_call=None, use_llm: bool = True, locale: str = "es") -> LeadClassifier:
    return LeadClassifier(llm_call=llm_call, use_llm=use_llm, locale=locale)


if __name__ == "__main__":
    import asyncio

    c = create_classifier(use_llm=False)

    async def run():
        casos = [
            ["Hola", "Qué servicios tienen?", "gracias"],
            ["Buenas, tengo una tienda de ropa en Hermosillo", "Me interesa el empleado digital"],
            ["Quiero contratar YA", "Mi presupuesto es 15k al mes", "Empezamos el lunes"],
            ["Ya uso otra herramienta pero es lenta", "Quiero comparar precios"],
        ]
        for conv in casos:
            r = await c.classify(conv)
            print(f"{r.tipo:5} conf={r.confianza:.2f} via={r.metodo} | {conv[0][:40]}")

    asyncio.run(run())