"""Conversation Engine — Orquestador RAG-first del MVP.

Pipeline completo por mensaje:
  1. Resolver identidad (cross-canal)
  2. Recuperar memoria emerge (contexto previo del cliente)
  3. RAG-first: buscar conocimiento en Qdrant ANTES de llamar al LLM
  4. Analizar emoción (multi-idioma)
  5. Clasificar lead (híbrido)
  6. Construir prompt (guardrails anti-venta)
  7. Llamar LLM + token tracking
  8. Guardrails post-LLM (re-escribir si viola)
  9. Persistir dual (Postgres + Engram) + promover emerge
  10. Notificar si lead hot

Permite reusar el MISMO pipeline para Telegram y WhatsApp.
"""

import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://sdc:sdc_local_dev@localhost:5432/sdc"
)
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")


@dataclass
class EngineConfig:
    tenant_id: str = "aztrotech"
    database_url: str = DATABASE_URL
    qdrant_url: str = QDRANT_URL
    use_llm_classify: bool = True
    use_llm_emotion: bool = True
    max_history_turns: int = 8
    notify_hot_leads: bool = True


@dataclass
class TurnResult:
    reply: str
    lead_type: str = "cold"
    lead_confidence: float = 0.0
    dominant_emotion: str = "neutral"
    emotion_flags: Dict[str, bool] = field(default_factory=dict)
    rag_chunks: int = 0
    rag_context: str = ""
    model: str = ""
    cost_usd: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    guardrail_pass: bool = True
    guardrail_note: str = ""
    internal_user_id: str = ""
    language: str = "es"


class ConversationEngine:
    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig()
        self._lazy = {}

    # ── Lazy deps ───────────────────────────────────────────────
    def _get(self, name: str):
        if name not in self._lazy:
            if name == "rag":
                from rag_retriever import create_retriever
                self._lazy[name] = create_retriever(self.config.tenant_id, self.config.qdrant_url)
            elif name == "emerge":
                from emerge_memory import create_emerge
                self._lazy[name] = create_emerge(self.config.tenant_id)
            elif name == "classifier":
                from lead_classifier import create_classifier
                self._lazy[name] = create_classifier(
                    llm_call=self._llm_raw_call,
                    use_llm=self.config.use_llm_classify,
                )
            elif name == "emotion":
                from emotion_analyzer import create_emotion_analyzer
                self._lazy[name] = create_emotion_analyzer(
                    llm_call=self._llm_raw_call,
                    use_llm=self.config.use_llm_emotion,
                )
            elif name == "prompt":
                from prompt_builder import create_prompt_builder
                self._lazy[name] = create_prompt_builder()
            elif name == "tracker":
                from token_tracker import create_token_tracker
                self._lazy[name] = create_token_tracker()
            elif name == "identity":
                from identity_resolver import create_identity_resolver
                from models.identity import Platform
                self._lazy[name] = {"resolver": None, "Platform": Platform}
            elif name == "persistence":
                from persistence import create_persistence_writer
                self._lazy[name] = create_persistence_writer(self.config.database_url)
        return self._lazy[name]

    async def start(self):
        """Inicializar dependencias asíncronas (identity pool, persistence)."""
        # Persistence
        writer = self._get("persistence")
        await writer.start()

    async def stop(self):
        writer = self._get("persistence")
        await writer.stop()

    # ── LLM call (reusable por classifier/emotion) ──────────────
    async def _llm_raw_call(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Wrapper sobre router (evita dependencia circular)."""
        router = getattr(self, "_router", None)
        if not router:
            return {"choices": [{"message": {"content": ""}}]}
        try:
            return await router.call(messages)
        except Exception as e:
            logger.warning(f"LLM raw call falló: {e}")
            return {"choices": [{"message": {"content": ""}}]}

    # ── Identity (cross-canal) ──────────────────────────────────
    async def resolve_user(
        self,
        platform: str,
        platform_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Resuelve/crea usuario canónico → internal_id (string)."""
        ident = self._get("identity")
        resolver = ident["resolver"]
        Platform = ident["Platform"]
        if resolver is None:
            # Crear resolver con pool propio si no se inició
            from identity_resolver import IdentityResolver
            import asyncpg
            pool = await asyncpg.create_pool(self.config.database_url, min_size=1, max_size=4)
            resolver = IdentityResolver(pool)
            self._lazy["identity"]["resolver"] = resolver
        try:
            plat = Platform(platform)
        except ValueError:
            plat = Platform.TELEGRAM
        result = await resolver.resolve_user(plat, str(platform_id), metadata or {})
        return str(result.user.internal_id)

    # ── Main pipeline ───────────────────────────────────────────
    async def process(
        self,
        user_message: str,
        internal_user_id: str,
        platform: str,
        platform_conversation_id: str,
        history: Optional[List[Dict[str, str]]] = None,
        user_metadata: Optional[Dict[str, Any]] = None,
        router=None,
    ) -> TurnResult:
        """Procesa un mensaje completo RAG-first."""
        self._router = router or getattr(self, "_router", None)
        t0 = time.monotonic()

        # 1. Memoria emerge: contexto del cliente
        emerge = self._get("emerge")
        memoria_ctx = emerge.get_context_for_prompt(internal_user_id, user_message)

        # 2. RAG-FIRST: buscar conocimiento antes del LLM
        rag = self._get("rag")
        rag_context = rag.get_context_for_prompt(user_message, max_chunks=3)
        rag_chunks = len(rag.search(user_message, top_k=3))

        # 3. Emoción (multi-idioma)
        emotion = self._get("emotion")
        emo = await emotion.analyze(user_message)

        # 4. Clasificar lead (híbrido: reglas + LLM)
        classifier = self._get("classifier")
        conv_texts = [h["content"] for h in (history or [])] + [user_message]
        lead = await classifier.classify(conv_texts, rag_context=rag_context)

        # 5. Construir prompt con guardrails
        prompt = self._get("prompt")
        from prompt_builder import PromptContext
        ctx = PromptContext(
            user_message=user_message,
            rag_context=rag_context,
            memoria_context=memoria_ctx,
            emotion_context=json.dumps(emo.to_dict(), ensure_ascii=False),
            lead_context=json.dumps(lead.to_dict(), ensure_ascii=False),
            history=history or [],
            locale=emo.language,
            max_history_turns=self.config.max_history_turns,
        )
        messages = prompt.build(ctx)

        # 6. Llamar LLM + tokens
        if not router:
            return TurnResult(
                reply="(motor LLM no configurado)", lead_type=lead.tipo,
                lead_confidence=lead.confianza, dominant_emotion=emo.dominant,
                emotion_flags=emo.flags, rag_chunks=rag_chunks,
                rag_context=rag_context, internal_user_id=internal_user_id,
                language=emo.language,
            )
        try:
            result = await router.call(messages)
        except Exception as e:
            logger.error(f"LLM call falló: {e}")
            return TurnResult(
                reply="Disculpa, tengo un problema. Le avisaré a César para que te contacte.",
                lead_type=lead.tipo, lead_confidence=lead.confianza,
                dominant_emotion=emo.dominant, emotion_flags=emo.flags,
                rag_chunks=rag_chunks, internal_user_id=internal_user_id,
                language=emo.language,
            )

        usage = result.get("usage", {})
        model = result.get("model", "")
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        tracker = self._get("tracker")
        tok = tracker.track(model, usage)

        # 7. Guardrails post-LLM: si viola, re-escribir
        guardrail = prompt.check_guardrails(content)
        if not guardrail["pass"]:
            logger.warning(f"Guardrail: {guardrail['message']} → re-escritura")
            content = await self._regenerate_safe(prompt, ctx, content)

        # 8. Persistir dual + promover emerge
        await self._persist(
            internal_user_id, platform, platform_conversation_id,
            user_message, content, emo, lead, rag_chunks, model, tok,
        )
        self._promote_emerge(emerge, internal_user_id, user_message, lead)

        return TurnResult(
            reply=content,
            lead_type=lead.tipo,
            lead_confidence=lead.confianza,
            dominant_emotion=emo.dominant,
            emotion_flags=emo.flags,
            rag_chunks=rag_chunks,
            rag_context=rag_context,
            model=model,
            cost_usd=tok["cost_usd"],
            tokens_in=tok["prompt_tokens"],
            tokens_out=tok["completion_tokens"],
            guardrail_pass=guardrail["pass"],
            guardrail_note=guardrail["message"],
            internal_user_id=internal_user_id,
            language=emo.language,
        )

    async def _regenerate_safe(
        self, prompt, ctx, original: str
    ) -> str:
        """Re-escribe la respuesta para que cumpla guardrails."""
        try:
            from prompt_builder import PromptContext
            ctx2 = PromptContext(
                user_message=ctx.user_message,
                rag_context=ctx.rag_context,
                memoria_context=ctx.memoria_context,
                emotion_context=ctx.emotion_context,
                lead_context=ctx.lead_context,
                history=ctx.history,
                locale=ctx.locale,
                max_history_turns=2,
            )
            messages = prompt.build(ctx2)
            messages.append({
                "role": "user",
                "content": (
                    "Tu respuesta anterior violó las reglas (no dar precios, no revelar SDC, "
                    "no tono agresivo). Reescribe la respuesta cumpliendo TODAS las reglas. "
                    f"Respuesta anterior: {original[:300]}"
                ),
            })
            result = await self._router.call(messages)
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content if content else "Le pasaré tu información a César y te contactará pronto."
        except Exception as e:
            logger.warning(f"Re-escritura falló: {e}")
            return "Le pasaré tu información a César y te contactará pronto."

    async def _persist(
        self, internal_user_id, platform, platform_conv_id,
        user_msg, reply, emo, lead, rag_chunks, model, tok,
    ):
        """Persistir turno dual (Postgres + Engram)."""
        try:
            from persistence import TurnData
            writer = self._get("persistence")
            for role, content in (("user", user_msg), ("assistant", reply)):
                await writer.persist_turn(TurnData(
                    internal_user_id=internal_user_id,
                    platform=platform,
                    platform_conversation_id=platform_conv_id,
                    role=role,
                    content=content,
                    turn_number=0,
                    model=model,
                    tokens_in=tok["prompt_tokens"] if role == "user" else 0,
                    tokens_out=tok["completion_tokens"] if role == "assistant" else 0,
                    cost_usd=tok["cost_usd"] if role == "assistant" else 0.0,
                    emotion_scores=emo.to_dict(),
                    rag_chunks_used=[{"count": rag_chunks}],
                    language=emo.language,
                    lead_type=lead.tipo,
                    lead_confidence=lead.confianza,
                ))
        except Exception as e:
            logger.error(f"Persistencia falló: {e}")

    def _promote_emerge(self, emerge, internal_user_id, user_msg, lead):
        """Promover memorias según lógica emerge."""
        try:
            emerge.save(
                internal_user_id, f"conv:{time.time()}",
                f"user: {user_msg[:300]}", layer=0, importance=2, tags="conv",
            )
            # Detectar acción → L1→L2
            emerge.detect_action_and_promote(internal_user_id, user_msg)
            # Si lead warm/hot → promover perfil L2→L3
            if lead.tipo in ("warm", "hot"):
                emerge.promote_customer(internal_user_id, {
                    "lead_type": lead.tipo,
                    "lead_confidence": round(lead.confianza, 2),
                })
        except Exception as e:
            logger.warning(f"Promote emerge falló: {e}")


def create_engine(config: Optional[EngineConfig] = None) -> ConversationEngine:
    return ConversationEngine(config)


if __name__ == "__main__":
    import asyncio

    async def main():
        eng = create_engine()
        await eng.start()
        uid = "test-6623538272"
        r = await eng.process(
            "¿Cuánto cuesta el empleado digital?",
            uid, "telegram", "test-conv-1",
            router=None,  # sin router para test de pipeline
        )
        print(json.dumps(r.__dict__, ensure_ascii=False, indent=2, default=str))
        await eng.stop()

    asyncio.run(main())