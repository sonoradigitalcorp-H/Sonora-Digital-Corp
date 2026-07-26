"""Engram Bridge — Conexión directa entre Mystic Voice y Engram (sin MCP Gateway).

Guarda interacciones de voz como memorias en Engram SQLite y recupera
contexto relevante antes de cada respuesta del LLM.

Capas de memoria usadas:
  - layer=1 (task): interacciones de voz individuales
  - layer=2 (project): sesiones completas (promovido al cerrar sesión)
"""

import json
import logging
import os
import time
from typing import Any

from core.engram import Engram

logger = logging.getLogger("voice-realtime.engram_bridge")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAULT_ENGRAM_PATH = os.path.join(BASE_DIR, "state", "engram-data", "engram.db")


class EngramBridge:
    """Puente directo entre Mystic Voice y Engram.

    No depende del MCP Gateway. Conecta directamente a la DB SQLite
    de Engram y expone métodos para guardar y recuperar memoria.
    """

    def __init__(self, db_path: str | None = None):
        resolved = db_path or os.environ.get("ENGRAM_DB_PATH") or DEFAULT_ENGRAM_PATH
        logger.info("EngramBridge -> %s", resolved)
        self._engram = Engram(db_path=resolved)

    # ─── Save ────────────────────────────────────────────────────────────────

    def save_interaction(
        self,
        user_text: str,
        response: str | None,
        intent_id: str,
        destination: str | None = None,
        tone: str = "warm",
        session_id: str = "",
        importance: str = "medium",
        tags: str = "voice",
    ) -> int | None:
        """Guarda una interacción de voz como memoria en Engram.

        Returns:
            ID de la memoria creada, o None si falla.
        """
        try:
            summary = f"[Voice] {intent_id}: {user_text[:120]}"
            context = json.dumps({
                "user_text": user_text[:500],
                "response": response[:500] if response else "",
                "intent": intent_id,
                "destination": destination or "",
                "tone": tone,
                "session_id": session_id,
                "source": "mystic_voice",
            }, ensure_ascii=False)
            mem_id = self._engram.store_learning(
                spec_id=f"voice:{session_id}:{int(time.time())}",
                tag=tags,
                summary=summary,
                context=context,
                importance=importance,
                layer="task",
            )
            logger.debug("Engram save OK: id=%s intent=%s", mem_id, intent_id)
            return mem_id
        except Exception as e:
            logger.warning("Engram save failed (non-critical): %s", e)
            return None

    def save_session_summary(
        self,
        session_id: str,
        history: list[dict],
        tone: str = "warm",
        interaction_count: int = 0,
    ) -> int | None:
        """Guarda un resumen de sesión completa al cerrar (promovido a project)."""
        try:
            last_few = history[-4:] if len(history) > 4 else history
            summary_lines = []
            for msg in last_few:
                role = msg.get("role", "?")
                content = msg.get("content", "")[:100]
                summary_lines.append(f"{role}: {content}")
            summary = f"[Session] {session_id[:8]} — {interaction_count} interacciones\n"
            summary += "\n".join(summary_lines)

            context = json.dumps({
                "session_id": session_id,
                "interaction_count": interaction_count,
                "tone": tone,
                "source": "mystic_voice",
            }, ensure_ascii=False)

            mem_id = self._engram.store_learning(
                spec_id=f"session:{session_id}",
                tag="voice,session",
                summary=summary,
                context=context,
                importance="high",
                layer="project",
            )
            logger.info("Engram session summary saved: id=%s", mem_id)
            return mem_id
        except Exception as e:
            logger.warning("Engram session summary failed: %s", e)
            return None

    # ─── Retrieve ────────────────────────────────────────────────────────────

    def get_relevant_context(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Busca memorias relevantes en Engram dada una consulta.

        Returns:
            Lista de dicts con summary, context, importance, layer.
        """
        try:
            results = self._engram.query_context(query, limit=limit)
            return results
        except Exception as e:
            logger.warning("Engram query failed: %s", e)
            return []

    def format_memory_context(self, results: list[dict[str, Any]]) -> str:
        """Formatea resultados de memoria como texto para inyectar en prompt del LLM."""
        if not results:
            return ""
        parts = ["📜 MEMORIA DE INTERACCIONES ANTERIORES:"]
        for r in results:
            summary = r.get("summary", "")
            ctx_raw = r.get("context", "{}")
            try:
                ctx = json.loads(ctx_raw) if isinstance(ctx_raw, str) else ctx_raw
            except (json.JSONDecodeError, TypeError):
                ctx = {}
            user_prev = ctx.get("user_text", "")
            response_prev = ctx.get("response", "")
            imp = r.get("importance", 0)
            parts.append(
                f"  [Importancia {imp}] {summary}\n"
                f"    Usuario dijo: {user_prev[:200]}\n"
                f"    Mystic respondió: {response_prev[:200]}"
            )
        return "\n".join(parts)

    # ─── Qdrant integration (vector search stub) ─────────────────────────────

    def format_qdrant_context(self, results: list[dict]) -> str:
        """Formatea resultados de Qdrant para inyectar en prompt."""
        if not results:
            return ""
        parts = ["🔍 CONTEXTO VECTORIAL (Qdrant):"]
        for r in results:
            payload = r.get("payload", {})
            text = payload.get("text", payload.get("summary", ""))
            score = r.get("score", 0)
            parts.append(f"  [Similitud: {score:.2f}] {text[:200]}")
        return "\n".join(parts)


# ─── Singleton ───────────────────────────────────────────────────────────────
_bridge: EngramBridge | None = None


def get_engram_bridge(db_path: str | None = None) -> EngramBridge:
    global _bridge
    if _bridge is None:
        _bridge = EngramBridge(db_path=db_path)
    return _bridge
