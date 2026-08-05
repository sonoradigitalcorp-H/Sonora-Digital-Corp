"""Emerge Memory Layer — Promoción y recuperación multi-capa de memoria.

Capas:
  0 = working    (turno actual)
  1 = task       (sesión activa)
  2 = project    (proyectos en curso)
  3 = customer   (perfil de cliente)
  4 = business   (métricas de negocio)
  5 = historical (resúmenes pasados)
  6 = strategic  (patrones a largo plazo)

Promoción automática:
  L0 → L1 : al cerrar sesión / timeout de inactividad
  L1 → L2 : al detectar "acción concreta" o "próximos pasos"
  L2 → L3 : al clasificar lead warm/hot + datos de perfil
  L1/L2 → L5 : job nocturno resume >7 días
  L3/L4 → L6 : job semanal detecta patrones cross-clientes

Usa la misma base SQLite engram (ops/state/engram_{tenant}.db).
"""

import json
import os
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = None
try:
    import logging
    logger = logging.getLogger(__name__)
except Exception:
    pass

# Capa → (nombre, descripción)
LAYERS = {
    0: ("working", "Contexto de la sesión actual"),
    1: ("task", "Tareas y su estado"),
    2: ("project", "Proyectos en curso"),
    3: ("customer", "Perfil del cliente"),
    4: ("business", "Métricas y KPIs del negocio"),
    5: ("historical", "Resúmenes de sesiones pasadas"),
    6: ("strategic", "Patrones y objetivos de largo plazo"),
}

INACTIVITY_PROMOTE_SECONDS = int(os.getenv("EMERGE_INACTIVITY", "1800"))  # 30 min
SESSION_CLOSE_PATTERNS = [
    r"\b(gracias|adios|bye|hasta luego|nos vemos|listo|perfecto)\b",
    r"\b(hablar con cesar|me contacta|me contacte|agendar|programar llamada)\b",
]
ACTION_PATTERNS = [
    r"\b(contratar|comprar|empezar|agendar|agenda|comenzar|registrarme)\b",
    r"\b(presupuesto|timeline|fecha|cotización|cotizacion|empezamos)\b",
]


class EmergeMemory:
    def __init__(
        self,
        tenant_id: str,
        engram_dir: Optional[str] = None,
        inactivity_seconds: int = INACTIVITY_PROMOTE_SECONDS,
    ):
        self.tenant_id = tenant_id
        if engram_dir is None:
            repo = Path(__file__).resolve().parent.parent.parent.parent  # tenants/.. → repo? adjust
            # bot/ está en tenants/Aztrotech/bot → repo = ../../../.. 
            repo = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
            engram_dir = str(repo / "ops" / "state")
        self.engram_dir = engram_dir
        self.inactivity_seconds = inactivity_seconds
        self.db_path = os.path.join(engram_dir, f"engram_{tenant_id}.db")
        Path(engram_dir).mkdir(parents=True, exist_ok=True)
        self._init_db()

    # ── DB init ─────────────────────────────────────────────────
    def _init_db(self):
        conn = self._connect()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT '',
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                layer INTEGER NOT NULL DEFAULT 0,
                importance INTEGER NOT NULL DEFAULT 1,
                tags TEXT NOT NULL DEFAULT '',
                access_count INTEGER NOT NULL DEFAULT 0,
                promoted_from INTEGER,
                promoted_at REAL,
                summary_of TEXT,
                created_at REAL NOT NULL,
                accessed_at REAL NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_user_layer ON memories(user_id, layer)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key)")
        conn.commit()
        conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _now(self) -> float:
        return time.time()

    # ── Save / retrieve ─────────────────────────────────────────
    def save(
        self,
        user_id: str,
        key: str,
        value: str,
        layer: int = 0,
        importance: int = 1,
        tags: str = "",
        promoted_from: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Guardar memoria en capa explícita (upsert por user+key)."""
        conn = self._connect()
        now = self._now()
        existing = conn.execute(
            "SELECT id FROM memories WHERE user_id=? AND key=? AND layer=?",
            (user_id, key, layer),
        ).fetchone()
        if existing:
            conn.execute(
                """UPDATE memories SET value=?, importance=?, tags=?, 
                   promoted_from=COALESCE(promoted_from, ?), accessed_at=? WHERE id=?""",
                (value, importance, tags, promoted_from, now, existing["id"]),
            )
            mem_id = existing["id"]
        else:
            cur = conn.execute(
                """INSERT INTO memories 
                   (user_id, key, value, layer, importance, tags, promoted_from, created_at, accessed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, key, value, layer, importance, tags, promoted_from, now, now),
            )
            mem_id = cur.lastrowid
        conn.commit()
        conn.close()
        return {"saved": True, "id": mem_id, "key": key, "layer": layer}

    def get(self, user_id: str, key: str, layer: Optional[int] = None) -> Optional[Dict[str, Any]]:
        conn = self._connect()
        if layer is not None:
            row = conn.execute(
                "SELECT * FROM memories WHERE user_id=? AND key=? AND layer=?",
                (user_id, key, layer),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM memories WHERE user_id=? AND key=? ORDER BY layer DESC LIMIT 1",
                (user_id, key),
            ).fetchone()
        if row:
            conn.execute(
                "UPDATE memories SET access_count=access_count+1, accessed_at=? WHERE id=?",
                (self._now(), row["id"]),
            )
            conn.commit()
            result = self._row_to_dict(row)
            conn.close()
            return result
        conn.close()
        return None

    def search(
        self,
        user_id: str,
        query: str,
        layers: Optional[List[int]] = None,
        limit: int = 10,
        min_importance: int = 0,
    ) -> List[Dict[str, Any]]:
        """Búsqueda cross-layer ponderada (keyword sobre key/value/tags)."""
        conn = self._connect()
        q = query.lower()
        terms = [t for t in re.findall(r"[\wáéíóúñü]+", q) if len(t) > 1]
        if not terms:
            conn.close()
            return []
        layer_filter = ""
        params: List[Any] = []
        if layers:
            placeholders = ",".join("?" * len(layers))
            layer_filter = f"AND layer IN ({placeholders})"
            params.extend(layers)
        if min_importance:
            layer_filter += " AND importance >= ?"
            params.append(min_importance)

        rows = conn.execute(
            f"""SELECT * FROM memories 
                WHERE user_id=? {layer_filter} AND (key LIKE ? OR value LIKE ? OR tags LIKE ?)
                ORDER BY importance DESC, accessed_at DESC LIMIT ?""",
            [user_id] + params + [f"%{terms[0]}%", f"%{terms[0]}%", f"%{terms[0]}%", limit],
        ).fetchall()
        results = [self._row_to_dict(r) for r in rows]
        conn.close()
        return results

    def search_cross_layer(
        self,
        user_id: str,
        query: str,
        layers: Optional[List[int]] = None,
        weights: Optional[Dict[int, float]] = None,
        limit: int = 8,
    ) -> List[Dict[str, Any]]:
        """Búsqueda multi-capa con pesos por capa (L3 customer pesa más que L0 working)."""
        weights = weights or {0: 0.5, 1: 0.7, 2: 0.9, 3: 1.0, 4: 0.8, 5: 0.6, 6: 0.8}
        results = self.search(user_id, query, layers=layers, limit=limit * 2)
        for r in results:
            w = weights.get(r["layer"], 0.5)
            r["weighted_score"] = r["importance"] * w + r["access_count"] * 0.01
        results.sort(key=lambda r: r["weighted_score"], reverse=True)
        return results[:limit]

    def get_context_for_prompt(
        self,
        user_id: str,
        query: str,
        max_chars: int = 1200,
        include_layers: Optional[List[int]] = None,
    ) -> str:
        """Contexto compacto de memoria para el prompt."""
        layers = include_layers or [0, 1, 2, 3, 5]
        results = self.search_cross_layer(user_id, query, layers=layers, limit=6)
        if not results:
            return ""
        parts = []
        total = 0
        for r in results:
            layer_name, _ = LAYERS.get(r["layer"], (f"L{r['layer']}", ""))
            block = f"[Memoria {layer_name}] {r['value'][:200]}"
            if total + len(block) > max_chars:
                break
            parts.append(block)
            total += len(block)
        return "\n".join(parts)

    # ── Promotion logic ─────────────────────────────────────────
    def promote(self, user_id: str, from_layer: int, to_layer: int, criteria: str = "") -> List[Dict[str, Any]]:
        """Promover memorias de una capa a otra (mantiene key original con sufijo)."""
        conn = self._connect()
        now = self._now()
        rows = conn.execute(
            "SELECT * FROM memories WHERE user_id=? AND layer=?",
            (user_id, from_layer),
        ).fetchall()
        promoted = []
        for row in rows:
            new_key = f"{row['key']}::L{to_layer}"
            existing = conn.execute(
                "SELECT id FROM memories WHERE user_id=? AND key=? AND layer=?",
                (user_id, new_key, to_layer),
            ).fetchone()
            if existing:
                continue
            cur = conn.execute(
                """INSERT INTO memories 
                   (user_id, key, value, layer, importance, tags, promoted_from, promoted_at, summary_of, created_at, accessed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, new_key, row["value"], to_layer, row["importance"],
                 row["tags"], from_layer, now, row["key"], now, now),
            )
            promoted.append({"id": cur.lastrowid, "key": new_key, "layer": to_layer, "from": from_layer})
        conn.commit()
        conn.close()
        return promoted

    def session_end(self, user_id: str) -> Dict[str, Any]:
        """Al cerrar sesión: L0 → L1."""
        promoted = self.promote(user_id, 0, 1, criteria="session_end")
        return {"session_end": True, "promoted": len(promoted)}

    def detect_action_and_promote(self, user_id: str, last_user_text: str) -> Dict[str, Any]:
        """Si hay acción concreta: L1 → L2."""
        if any(re.search(p, last_user_text.lower()) for p in ACTION_PATTERNS):
            promoted = self.promote(user_id, 1, 2, criteria="action_detected")
            return {"action_detected": True, "promoted": len(promoted)}
        return {"action_detected": False, "promoted": 0}

    def promote_customer(self, user_id: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        """L2 → L3 (customer) cuando hay perfil de cliente (lead warm/hot)."""
        if not profile:
            return {"promoted": 0}
        conn = self._connect()
        now = self._now()
        promoted = 0
        for key, value in profile.items():
            if not value:
                continue
            mem_key = f"profile:{key}"
            existing = conn.execute(
                "SELECT id FROM memories WHERE user_id=? AND key=? AND layer=3",
                (user_id, mem_key),
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE memories SET value=?, accessed_at=? WHERE id=?",
                    (str(value), now, existing["id"]),
                )
            else:
                conn.execute(
                    """INSERT INTO memories 
                       (user_id, key, value, layer, importance, tags, created_at, accessed_at)
                       VALUES (?, ?, ?, 3, 3, 'customer,profile', ?, ?)""",
                    (user_id, mem_key, str(value), now, now),
                )
                promoted += 1
        conn.commit()
        conn.close()
        return {"promoted": promoted, "layers_updated": 3}

    def list_layers(self) -> Dict[str, Dict[str, Any]]:
        return {
            str(k): {"id": k, "name": name, "description": desc}
            for k, (name, desc) in LAYERS.items()
        }

    def stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        conn = self._connect()
        if user_id:
            rows = conn.execute(
                "SELECT layer, COUNT(*) as count FROM memories WHERE user_id=? GROUP BY layer",
                (user_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT layer, COUNT(*) as count FROM memories GROUP BY layer"
            ).fetchall()
        stats = {str(k): {"name": v[0], "count": 0} for k, v in LAYERS.items()}
        for r in rows:
            stats[str(r["layer"])]["count"] = r["count"]
        conn.close()
        return {"layers": stats, "total": sum(v["count"] for v in stats.values())}

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "key": row["key"],
            "value": row["value"],
            "layer": row["layer"],
            "layer_name": LAYERS.get(row["layer"], (f"L{row['layer']}", ""))[0],
            "importance": row["importance"],
            "tags": row["tags"],
            "access_count": row["access_count"],
            "promoted_from": row["promoted_from"],
            "promoted_at": row["promoted_at"],
            "summary_of": row["summary_of"],
            "created_at": row["created_at"],
            "accessed_at": row["accessed_at"],
        }


def create_emerge(tenant_id: str, engram_dir: Optional[str] = None) -> EmergeMemory:
    return EmergeMemory(tenant_id=tenant_id, engram_dir=engram_dir)


if __name__ == "__main__":
    import sys

    m = create_emerge("aztrotech")
    print("Layers:", m.list_layers())
    uid = "test-6623538272"
    m.save(uid, "conv:session1", "Cliente pregunta por empleado digital", layer=0, tags="conv")
    m.save(uid, "profile:business_type", "tienda de ropa", layer=3, importance=3, tags="customer,profile")
    print("Stats:", m.stats(uid))
    print("Promote L0→L1:", m.session_end(uid))
    print("Context:", m.get_context_for_prompt(uid, "empleado digital"))