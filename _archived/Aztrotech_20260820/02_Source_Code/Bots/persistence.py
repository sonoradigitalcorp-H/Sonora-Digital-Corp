"""Dual Persistence Writer — Engram (SQLite) + Postgres en paralelo, asíncrono.

Escribe cada turno en:
  1. Postgres: messages + conversations (para analytics, dashboards)
  2. Engram: memoria emerge (L0 raw + L3 profile + tags)

Batch asíncrono: acumula mensajes y hace flush cada N o cada T segundos,
para no bloquear la respuesta del bot.
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4

import asyncpg

logger = logging.getLogger(__name__)

FLUSH_INTERVAL = float(os.getenv("PERSIST_FLUSH_SECONDS", "2.0"))
FLUSH_BATCH = int(os.getenv("PERSIST_FLUSH_BATCH", "10"))


@dataclass
class TurnData:
    internal_user_id: str
    platform: str
    platform_conversation_id: str
    role: str  # user | assistant
    content: str
    turn_number: int
    model: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    emotion_scores: Dict[str, Any] = field(default_factory=dict)
    rag_chunks_used: List[Any] = field(default_factory=list)
    emerge_layers_used: Dict[str, Any] = field(default_factory=dict)
    language: str = "es"
    lead_type: Optional[str] = None
    lead_confidence: float = 0.0
    engagement_score: float = 0.0
    servicios_requeridos: List[str] = field(default_factory=list)
    cita_intent: Optional[str] = None


class PersistenceWriter:
    def __init__(self, database_url: str, engram_dir: Optional[str] = None):
        self.database_url = database_url
        self._pool: Optional[asyncpg.Pool] = None
        self._queue: asyncio.Queue = asyncio.Queue()
        self._worker: Optional[asyncio.Task] = None
        self._running = False
        # Engram se importa lazy para evitar dependencias circulares
        self._emerge = None
        self.engram_dir = engram_dir

    async def start(self):
        self._pool = await asyncpg.create_pool(self.database_url, min_size=2, max_size=8)
        self._running = True
        self._worker = asyncio.create_task(self._run())
        logger.info("PersistenceWriter started")

    async def stop(self):
        self._running = False
        if self._worker:
            self._worker.cancel()
            try:
                await self._worker
            except asyncio.CancelledError:
                pass
        if self._pool:
            await self._pool.close()

    def _get_emerge(self):
        if self._emerge is None:
            from emerge_memory import EmergeMemory
            self._emerge = EmergeMemory("aztrotech", engram_dir=self.engram_dir)
        return self._emerge

    # ── Public API ──────────────────────────────────────────────
    async def persist_turn(self, turn: TurnData):
        """Encola un turno para escritura dual (no bloquea)."""
        await self._queue.put(turn)

    async def flush_now(self):
        """Flush inmediato (para cierre de sesión)."""
        items = []
        while not self._queue.empty():
            try:
                items.append(self._queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        if items:
            await self._write_batch(items)

    # ── Worker ──────────────────────────────────────────────────
    async def _run(self):
        batch: List[TurnData] = []
        last_flush = time.monotonic()
        while self._running:
            try:
                turn = await asyncio.wait_for(self._queue.get(), timeout=0.5)
                batch.append(turn)
            except asyncio.TimeoutError:
                pass
            if len(batch) >= FLUSH_BATCH or (batch and time.monotonic() - last_flush >= FLUSH_INTERVAL):
                await self._write_batch(batch)
                batch = []
                last_flush = time.monotonic()

    async def _write_batch(self, batch: List[TurnData]):
        try:
            await self._write_postgres(batch)
        except Exception as e:
            logger.error(f"Postgres write falló: {e}")
        try:
            self._write_engram(batch)
        except Exception as e:
            logger.error(f"Engram write falló: {e}")

    # ── Postgres ────────────────────────────────────────────────
    async def _write_postgres(self, batch: List[TurnData]):
        if not self._pool:
            return
        async with self._pool.acquire() as conn:
            for turn in batch:
                conv_id = await self._get_or_create_conversation(conn, turn)
                await conn.execute(
                    """INSERT INTO messages
                       (id, conversation_id, turn_number, role, content, tokens_in, tokens_out,
                        model, cost_usd, emotion_scores, rag_chunks_used, emerge_layers_used, language)
                       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)""",
                    uuid4(), conv_id, turn.turn_number, turn.role, turn.content,
                    turn.tokens_in, turn.tokens_out, turn.model, turn.cost_usd,
                    json.dumps(turn.emotion_scores), json.dumps(turn.rag_chunks_used),
                    json.dumps(turn.emerge_layers_used), turn.language,
                )
                # Batch UPDATE conversations with latest analytics per user
                await self._update_conversation_analytics(conn, conv_id, turn)
            # Update daily metrics
            await self._update_daily_metrics(conn, batch)

    async def _get_or_create_conversation(self, conn: asyncpg.Connection, turn: TurnData) -> str:
        """Busca o crea la conversación para (user, platform_conv_id)."""
        row = await conn.fetchrow(
            """SELECT id FROM conversations
               WHERE internal_user_id=$1 AND platform_conversation_id=$2 AND closed_at IS NULL""",
            uuid_from_str(turn.internal_user_id), turn.platform_conversation_id,
        )
        if row:
            return row["id"]
        conv_id = uuid4()
        await conn.execute(
            """INSERT INTO conversations (id, internal_user_id, platform, platform_conversation_id, language)
               VALUES ($1,$2,$3,$4,$5)""",
            conv_id, uuid_from_str(turn.internal_user_id), turn.platform,
            turn.platform_conversation_id, turn.language,
        )
        return conv_id

    async def _update_conversation_analytics(self, conn: asyncpg.Connection, conv_id, turn: TurnData):
        """Update conversation row with lead_type, engagement, services, cita intent."""
        set_parts = ["updated_at = NOW()"]
        params: List[Any] = []

        if turn.lead_type:
            params.append(turn.lead_type)
            set_parts.append(f"lead_type = ${len(params)}")
            params.append(turn.lead_confidence)
            set_parts.append(f"lead_confidence = ${len(params)}")

        if turn.engagement_score:
            params.append(turn.engagement_score)
            set_parts.append(f"engagement_score = ${len(params)}")

        if turn.servicios_requeridos:
            params.append(json.dumps(turn.servicios_requeridos))
            set_parts.append(f"servicios_requeridos = ${len(params)}::jsonb")

        if turn.cita_intent:
            params.append(datetime.utcnow())
            set_parts.append(f"cita_agendada = ${len(params)}")

        if len(params) == 0:
            return

        params.append(conv_id)
        await conn.execute(
            f"UPDATE conversations SET {', '.join(set_parts)} WHERE id = ${len(params)}",
            *params,
        )

    async def _update_daily_metrics(self, conn: asyncpg.Connection, batch: List[TurnData]):
        import datetime as _dt
        today = _dt.date.today()
        total_tokens_in = sum(t.tokens_in for t in batch)
        total_tokens_out = sum(t.tokens_out for t in batch)
        total_cost = sum(t.cost_usd for t in batch)
        leads = {}
        for t in batch:
            if t.lead_type:
                leads[t.lead_type] = leads.get(t.lead_type, 0) + 1
        await conn.execute(
            """INSERT INTO daily_metrics (day, total_messages, tokens_in, tokens_out, cost_usd)
               VALUES ($1, $2, $3, $4, $5)
               ON CONFLICT (day) DO UPDATE SET
                 total_messages = daily_metrics.total_messages + EXCLUDED.total_messages,
                 tokens_in = daily_metrics.tokens_in + EXCLUDED.tokens_in,
                 tokens_out = daily_metrics.tokens_out + EXCLUDED.tokens_out,
                 cost_usd = daily_metrics.cost_usd + EXCLUDED.cost_usd,
                 updated_at = NOW()""",
            today, len(batch), total_tokens_in, total_tokens_out, total_cost,
        )
        for lt, count in leads.items():
            col = {"cold": "leads_cold", "warm": "leads_warm", "hot": "leads_hot"}.get(lt)
            if col:
                await conn.execute(
                    f"UPDATE daily_metrics SET {col} = {col} + $1 WHERE day = $2",
                    count, today,
                )

    # ── Engram ──────────────────────────────────────────────────
    def _write_engram(self, batch: List[TurnData]):
        emerge = self._get_emerge()
        for turn in batch:
            uid = turn.internal_user_id
            ts = int(time.time())
            # L0: turno crudo
            emerge.save(
                uid, f"conv:{turn.platform_conversation_id}:{ts}",
                f"{turn.role}: {turn.content[:500]}",
                layer=0,
                importance=2 if turn.role == "user" else 1,
                tags=f"conv,{turn.platform},{turn.language}",
            )
            # L3: actualizar perfil con señales detectadas
            if turn.emotion_scores:
                flags = {k for k, v in turn.emotion_scores.get("flags", {}).items() if v}
                if flags:
                    emerge.save(
                        uid, "profile:emotion_signals",
                        ", ".join(flags), layer=3, importance=2,
                        tags="customer,profile,emotion",
                    )
            if turn.lead_type:
                emerge.save(
                    uid, "profile:lead_type",
                    turn.lead_type, layer=3, importance=3,
                    tags="customer,profile,lead",
                )


def uuid_from_str(s: str):
    """Convierte string a UUID; si falla, genera UUID5 determinista."""
    from uuid import UUID, uuid3, NAMESPACE_OID
    try:
        return UUID(s)
    except (ValueError, TypeError):
        return uuid3(NAMESPACE_OID, str(s))


def create_persistence_writer(database_url: str, engram_dir: Optional[str] = None) -> PersistenceWriter:
    return PersistenceWriter(database_url=database_url, engram_dir=engram_dir)


if __name__ == "__main__":
    import sys

    async def main():
        db_url = os.getenv("DATABASE_URL", "postgresql://sdc:sdc2026prod@localhost:5432/sdc")
        w = create_persistence_writer(db_url)
        await w.start()
        await w.persist_turn(TurnData(
            internal_user_id="test-user-1", platform="telegram",
            platform_conversation_id="test-conv-1", role="user",
            content="Hola, prueba de persistencia", turn_number=1,
            emotion_scores={"dominant": "neutral", "flags": {}},
        ))
        await w.flush_now()
        await w.stop()
        print("Persistencia OK")

    asyncio.run(main())