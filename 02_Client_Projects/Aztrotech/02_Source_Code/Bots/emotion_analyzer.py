"""Emotion Analyzer Multi-Idioma — Heurísticas multilingüe + LLM para análisis fino.

MVP: Sin dependencia pesada (no XLM-R ~1GB). Usa:
  1. Lexicón multi-idioma (es/en/pt/fr) para detección rápida de señales.
  2. LLM (OpenRouter) para análisis fino con cache (evita costo por turno).
  3. Flags de negocio: frustración, urgencia, interés, objeción-precio, buying signal.

El pipeline detecta el idioma y aplica reglas; el LLM solo se llama cuando
la conversación es ambigua o para generar razón explicativa.
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Lexicón multi-idioma por emoción/signal
LEXICON = {
    "frustracion": {
        "es": [r"\b(odio|detesto|molesto|molesta|frustr|fastidi|hart\w*|que\s+mal\b|peor)\b",
               r"\b(no\s+funciona|no\s+responde|falla|bug|lento|lenta|terrible|horrible)\b"],
        "en": [r"\b(hate|annoyed|frustrat|tired\s+of|terrible|horrible|worst|broken|not\s+working)\b"],
        "pt": [r"\b(odeio|irritado|frustrad|cansad\w*\s+de|terrível|quebrado|não\s+funciona)\b"],
        "fr": [r"\b(déteste|agacé|frustr|fatigué\s+de|terrible|horrible|ne\s+marche\s+pas)\b"],
    },
    "urgencia": {
        "es": [r"\b(ya\b|urgente|inmediato|cuanto\s+antes|necesito\s+ya|lo\s+antes\s+posible|hoy\b|mañana)\b"],
        "en": [r"\b(now\b|urgent|immediately|asap|right\s+away|today|tomorrow|asap)\b"],
        "pt": [r"\b(agora|urgente|imediatamente|quanto\s+antes|hoje|amanhã)\b"],
        "fr": [r"\b(maintenant|urgent|immédiatement|aujourd'hui|demain|dès\s+que\s+possible)\b"],
    },
    "interes_genuino": {
        "es": [r"\b(me\s+interesa|me\s+encanta|excelente|perfecto|justo\s+lo\s+que\s+necesito|genial|suena\s+bien)\b"],
        "en": [r"\b(interested|love\s+it|excellent|perfect|just\s+what\s+i\s+need|great|sounds\s+good)\b"],
        "pt": [r"\b(interessad|adoro|excelente|perfeito|exatamente\s+o\s+que\s+preciso|ótimo|parece\s+bom)\b"],
        "fr": [r"\b(intéressé|j'adore|excellent|parfait|exactement\s+ce\s+dont\s+j'ai\s+besoin|génial|ça\s+semble\s+bien)\b"],
    },
    "objecion_precio": {
        "es": [r"\b(caro|costoso|no\s+me\s+alcanza|no\s+tengo\s+presupuesto|muy\s+costo|está\s+costoso)\b"],
        "en": [r"\b(expensive|too\s+much|out\s+of\s+budget|can't\s+afford|pricey)\b"],
        "pt": [r"\b(caro|muito\s+custo|não\s+tenho\s+orçamento|fora\s+do\s+orçamento)\b"],
        "fr": [r"\b(cher|trop\s+couteux|hors\s+budget|je\s+ne\s+peux\s+pas\s+me\s+permettre)\b"],
    },
    "buying_signal": {
        "es": [r"\b(contratar|comprar|empezar|firmar|contrato|presupuesto|aprobad|listos|vamos\s+pa\s+adelante)\b"],
        "en": [r"\b(hire|buy|start|sign|contract|budget|approved|ready|let's\s+go)\b"],
        "pt": [r"\b(contratar|comprar|começar|assinar|contrato|orçamento|aprovad|prontos|vamos)\b"],
        "fr": [r"\b(engager|acheter|commencer|signer|contrat|budget|approuvé|prêts|on\s+y\s+va)\b"],
    },
    "alegria": {
        "es": [r"\b(genial|excelente|perfecto|me\s+alegra|fantástico|me\s+encanta)\b"],
        "en": [r"\b(great|excellent|perfect|fantastic|love\s+it|awesome)\b"],
        "pt": [r"\b(ótimo|excelente|perfeito|fantástico|adoro|incrível)\b"],
        "fr": [r"\b(super|excellent|parfait|fantastique|j'adore|génial)\b"],
    },
    "duda": {
        "es": [r"\b(no\s+se\s+si|no\s+estoy\s+seguro|dud\w*|quizá|tal\s+vez|a\s+ver|no\s+sé)\b"],
        "en": [r"\b(not\s+sure|doubt|maybe|perhaps|i\s+don't\s+know|uncertain)\b"],
        "pt": [r"\b(não\s+sei|dúvida|talvez|incerto)\b"],
        "fr": [r"\b(je\s+ne\s+sais\s+pas|doute|peut-être|incertain)\b"],
    },
}

# Detección de idioma por señales simples
LANG_HINTS = {
    "es": [r"\b(hola|gracias|negocio|precio|quiero|necesito|servicio|tienda|cliente)\b"],
    "en": [r"\b(hello|thanks|business|price|want|need|service|store|client)\b"],
    "pt": [r"\b(olá|obrigado|negócio|preço|quero|preciso|serviço|loja|cliente)\b"],
    "fr": [r"\b(bonjour|merci|affaire|prix|veux|besoin|service|magasin|client)\b"],
}

ALL_EMOTIONS = [
    "frustracion", "urgencia", "interes_genuino", "objecion_precio",
    "buying_signal", "alegria", "duda",
]


@dataclass
class EmotionResult:
    scores: Dict[str, float] = field(default_factory=dict)
    dominant: str = "neutral"
    flags: Dict[str, bool] = field(default_factory=dict)
    language: str = "es"
    explanation: str = ""
    method: str = "heuristics"  # heuristics | llm | hybrid

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scores": {k: round(v, 3) for k, v in self.scores.items()},
            "dominant": self.dominant,
            "flags": self.flags,
            "language": self.language,
            "explanation": self.explanation,
            "method": self.method,
        }


class EmotionAnalyzer:
    def __init__(
        self,
        llm_call=None,
        use_llm: bool = True,
        cache_size: int = 256,
    ):
        """
        llm_call: async callable (messages: list) -> dict (OpenRouter-style).
        use_llm: si True, para análisis fino cuando es ambiguo.
        """
        self.llm_call = llm_call
        self.use_llm = use_llm
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_order: List[str] = []
        self._cache_size = cache_size

    def _detect_language(self, text: str) -> str:
        t = text.lower()
        scores = {lang: 0 for lang in LANG_HINTS}
        for lang, patterns in LANG_HINTS.items():
            for pat in patterns:
                if re.search(pat, t):
                    scores[lang] += 1
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "es"

    def _heuristic_scores(self, text: str, lang: str) -> Dict[str, float]:
        t = text.lower()
        scores = {}
        for emotion in ALL_EMOTIONS:
            patterns = LEXICON.get(emotion, {}).get(lang, []) + LEXICON.get(emotion, {}).get("es", [])
            count = sum(1 for pat in patterns if re.search(pat, t))
            scores[emotion] = min(1.0, count * 0.4)
        return scores

    def _build_llm_prompt(self, text: str, lang: str) -> List[Dict[str, str]]:
        system = (
            "Eres un analizador de emociones en conversaciones comerciales. "
            "Analiza el sentimiento del CLIENTE. "
            'Responde SOLO JSON: {"scores":{"frustracion":0.0,"urgencia":0.0,'
            '"interes_genuino":0.0,"objecion_precio":0.0,"buying_signal":0.0,'
            '"alegria":0.0,"duda":0.0},"dominant":"...","explanation":"..."}. '
            f"Idioma de análisis: {lang}. Respuesta en español."
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Mensajes del cliente:\n{text}"},
        ]

    async def _llm_analyze(self, text: str, lang: str) -> Optional[Dict[str, Any]]:
        cache_key = text[-300:]
        if cache_key in self._cache:
            return self._cache[cache_key]
        if not self.llm_call:
            return None
        try:
            messages = self._build_llm_prompt(text, lang)
            result = await self.llm_call(messages)
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            m = re.search(r"\{.*\}", content, re.DOTALL)
            if not m:
                return None
            data = json.loads(m.group(0))
            scores = {k: float(v) for k, v in data.get("scores", {}).items()}
            if scores:
                self._cache_put(cache_key, data)
                return data
            return None
        except Exception as e:
            logger.warning(f"LLM emotion falló: {e}")
            return None

    def _cache_put(self, key: str, value: Dict[str, Any]):
        self._cache[key] = value
        self._cache_order.append(key)
        if len(self._cache_order) > self._cache_size:
            old = self._cache_order.pop(0)
            self._cache.pop(old, None)

    def _merge(self, heur: Dict[str, float], llm_data: Optional[Dict[str, Any]]) -> Dict[str, float]:
        if not llm_data:
            return heur
        llm_scores = {k: float(v) for k, v in llm_data.get("scores", {}).items()}
        merged = {}
        for k in ALL_EMOTIONS:
            h = heur.get(k, 0.0)
            l = llm_scores.get(k, 0.0)
            merged[k] = round(h * 0.5 + l * 0.5, 3)
        return merged

    def _dominant(self, scores: Dict[str, float]) -> str:
        if not scores:
            return "neutral"
        best = max(scores, key=scores.get)
        if scores[best] < 0.15:
            return "neutral"
        return best

    async def analyze(self, text: str) -> EmotionResult:
        if not text.strip():
            return EmotionResult(
                scores={e: 0.0 for e in ALL_EMOTIONS}, dominant="neutral",
                language=self._detect_language(text or ""),
            )
        lang = self._detect_language(text)
        heur = self._heuristic_scores(text, lang)
        max_heur = max(heur.values()) if heur else 0

        llm_data = None
        method = "heuristics"
        # LLM solo si ambiguo o bajo score (para no gastar en cada turno)
        if self.use_llm and max_heur < 0.4:
            llm_data = await self._llm_analyze(text, lang)
            if llm_data:
                method = "hybrid"

        scores = self._merge(heur, llm_data)
        dominant = self._dominant(scores)
        flags = {
            "frustrated": scores.get("frustracion", 0) >= 0.5,
            "urgent": scores.get("urgencia", 0) >= 0.5,
            "interested": scores.get("interes_genuino", 0) >= 0.5,
            "price_objection": scores.get("objecion_precio", 0) >= 0.5,
            "buying": scores.get("buying_signal", 0) >= 0.5,
            "positive": scores.get("alegria", 0) >= 0.5,
            "doubtful": scores.get("duda", 0) >= 0.5,
        }
        explanation = (llm_data or {}).get("explanation", "")
        return EmotionResult(
            scores=scores,
            dominant=dominant,
            flags=flags,
            language=lang,
            explanation=explanation,
            method=method,
        )


def create_emotion_analyzer(llm_call=None, use_llm: bool = True) -> EmotionAnalyzer:
    return EmotionAnalyzer(llm_call=llm_call, use_llm=use_llm)


if __name__ == "__main__":
    import asyncio

    a = create_emotion_analyzer(use_llm=False)

    async def run():
        casos = [
            "No puedo creer lo lento que es, ya perdí clientes, necesito esto YA",
            "Me interesa mucho, suena perfecto para mi tienda",
            "Está muy caro, no me alcanza para eso",
            "Hola, solo quería más información",
            "I love it, exactly what my business needs, let's start now",
        ]
        for c in casos:
            r = await a.analyze(c)
            print(f"[{r.language}] {r.dominant:12} flags={r.flags} | {c[:35]}")

    asyncio.run(run())