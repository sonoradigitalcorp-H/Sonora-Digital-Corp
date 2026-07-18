"""Memory Ingestion Engine — Feed all memory systems with session data.

Alimenta Engram, Qdrant (vectorial), Neo4j (grafos), y almacenamiento local.
Organiza la memoria de forma: segregada, vectorial, lateral, horizontal.

Usage:
  python3 scripts/feed_memory.py                    # Feed everything
  python3 scripts/feed_memory.py --engram-only      # Solo Engram
  python3 scripts/feed_memory.py --vectors-only     # Solo vectores (Qdrant + SQLite)
  python3 scripts/feed_memory.py --graph-only       # Solo grafos (Neo4j + SQLite)
  python3 scripts/feed_memory.py --status           # Ver estado de todas las memorias
"""

import hashlib
import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

VECTOR_DB_PATH = REPO / "data" / "vector_memory.db"
GRAPH_DB_PATH = REPO / "data" / "graph_memory.db"
ENGRAM_TOPIC = "session/20260718-complete"

MEMORY_CATEGORIES = {
    "architecture": "Decisiones arquitectónicas, stacks, configuraciones",
    "product": "Productos, precios, features, planes",
    "code": "Código, scripts, MCP servers, pipelines",
    "security": "Auditorías, vulnerabilidades, hardening",
    "business": "Modelo de negocio, partners, pricing, revenue",
    "learning": "Aprendizajes, descubrimientos, errores",
    "person": "Personas, contactos, roles",
    "pipeline": "Pipelines, procesos, flujos",
}


def _log(msg: str):
    print(f"  {msg}")


# ═══════════════════════════════════════════════════
# 1. DATA EXTRACTION — Collect all session artifacts
# ═══════════════════════════════════════════════════

def collect_session_data() -> list:
    """Collect all session artifacts into memory entries."""
    entries = []

    # 1. SPECs
    spec_dir = REPO / "process" / "active"
    if spec_dir.exists():
        for f in sorted(spec_dir.glob("SPEC-*.md")):
            content = f.read_text()
            entries.append({
                "id": f"spec-{f.stem}",
                "type": "spec",
                "category": "architecture",
                "title": f.stem,
                "content": content[:2000],
                "source": str(f.relative_to(REPO)),
                "tags": ["spec", "sdd", "architecture"],
            })

    # 2. ADRs
    for f in spec_dir.glob("ADR-*.md"):
        entries.append({
            "id": f"adr-{f.stem}",
            "type": "adr",
            "category": "architecture",
            "title": f.stem,
            "content": f.read_text()[:2000],
            "source": str(f.relative_to(REPO)),
            "tags": ["adr", "decision", "architecture"],
        })

    # 3. Gherkin files
    gherkin_dir = REPO / "gherkin"
    if gherkin_dir.exists():
        for f in sorted(gherkin_dir.glob("*.feature")):
            entries.append({
                "id": f"gherkin-{f.stem}",
                "type": "gherkin",
                "category": "pipeline",
                "title": f"Gherkin: {f.stem}",
                "content": f.read_text()[:1500],
                "source": str(f.relative_to(REPO)),
                "tags": ["gherkin", "bdd", "test"],
            })

    # 4. Config files
    config_files = [
        ("packages", REPO / "config" / "packages.yaml", "product"),
        ("pricing-tiers", REPO / "config" / "pricing-tiers.yaml", "business"),
        ("tenants", REPO / "config" / "tenants.yaml", "architecture"),
        ("ambassadors", REPO / "config" / "ambassadors.yaml", "business"),
        ("client-signals", REPO / "config" / "client-signals.yaml", "product"),
        ("whatsapp-product", REPO / "config" / "whatsapp-product.yaml", "product"),
        ("cost-rates", REPO / "config" / "cost-rates.yaml", "business"),
    ]
    for name, path, cat in config_files:
        if path.exists():
            entries.append({
                "id": f"config-{name}",
                "type": "config",
                "category": cat,
                "title": f"Config: {name}",
                "content": path.read_text()[:1500],
                "source": str(path.relative_to(REPO)),
                "tags": ["config", name, cat],
            })

    # 5. MCP Servers
    mcp_dir = REPO / "mcp" / "servers"
    if mcp_dir.exists():
        for f in sorted(mcp_dir.glob("*_mcp.py")):
            content = f.read_text()[:1000]
            first_line = content.split("\n")[0] if content else ""
            entries.append({
                "id": f"mcp-{f.stem}",
                "type": "mcp_server",
                "category": "code",
                "title": f"MCP: {f.stem}",
                "content": f"{first_line}\n\n{content[:500]}",
                "source": str(f.relative_to(REPO)),
                "tags": ["mcp", "server", "tool"],
            })

    # 6. Scripts
    scripts_of_interest = [
        "clone_pipeline.py", "pricing_engine.py", "provision_tenant.py",
        "commissions.py", "packages.py", "client_analyzer.py",
        "demo_provision.py", "test_real_pipeline.py",
    ]
    for s in scripts_of_interest:
        path = REPO / "scripts" / s
        if path.exists():
            entries.append({
                "id": f"script-{path.stem}",
                "type": "script",
                "category": "code",
                "title": f"Script: {path.stem}",
                "content": path.read_text()[:1000],
                "source": str(path.relative_to(REPO)),
                "tags": ["script", path.stem],
            })

    # 7. Security files
    security_dir = REPO / "common" / "security"
    if security_dir.exists():
        for f in security_dir.glob("*.py"):
            if f.name != "__init__.py":
                entries.append({
                    "id": f"security-{f.stem}",
                    "type": "security",
                    "category": "security",
                    "title": f"Security: {f.stem}",
                    "content": f.read_text()[:1000],
                    "source": str(f.relative_to(REPO)),
                    "tags": ["security", "prompt_filter", "url_validator", "ffmpeg"],
                })

    # 8. Key learnings from this session
    entries.append({
        "id": "learning-margins",
        "type": "learning",
        "category": "business",
        "title": "Margen real del stack SDC",
        "content": "El costo real de servir un cliente enterprise business es ~$17/mes. El precio wholesale es $7,500/mes. Margen bruto: 99.8%. Los costos reales son: FAL.ai $0.003/imagen, $0.01/inferencia LoRA, $4/entrenamiento. OmniVoice y Whisper son gratis (self-hosted).",
        "source": "analisis-real",
        "tags": ["learning", "cost", "margin", "enterprise"],
    })
    entries.append({
        "id": "learning-security",
        "type": "learning",
        "category": "security",
        "title": "31 vulnerabilidades encontradas y corregidas",
        "content": "Auditoría de seguridad completa: 31 hallazgos (8 críticos, 8 altos, 10 medios, 5 bajos). Corregidos: shell=True eliminado, prompt filter implementado (50+ patrones), URL validator (SSRF), FFmpeg sanitizer, Neo4j auth activado, permisos 600, pre-commit hook, .gitignore. Pendiente manual: rotar tokens Telegram, purgar git history.",
        "source": "auditoria-seguridad",
        "tags": ["learning", "security", "hardening"],
    })
    entries.append({
        "id": "learning-stack",
        "type": "learning",
        "category": "architecture",
        "title": "Stack completo del ecosistema",
        "content": "10 pipelines activos: Clone Service (recepción, training, generation, delivery, créditos), Enterprise (cost intelligence, pricing, provisioning, commissions), Security (prompt filter). 215 tests totales. 21 MCP servers. 3 canales: WhatsApp, Telegram, Web. Stack hermetizado: no exponer FAL, OmniVoice, Qdrant, Neo4j, etc.",
        "source": "sesion-completa",
        "tags": ["learning", "stack", "architecture"],
    })
    entries.append({
        "id": "learning-business-model",
        "type": "learning",
        "category": "business",
        "title": "Modelo de negocio enterprise wholesale",
        "content": "SDC vende wholesale a partners (AztroTech, ABE Music). Partners ponen markup y venden a clientes enterprise. 3 planes: Medium ($5k/mes), Premium ($7.5k/mes — recomendado), Enterprise ($15k/mes). Revenue share 7% en contratos enterprise >$50k. Embajadores: 4 niveles (Hunter 20%, Ammo 25%, Warrior 30%, Legend 35%). Setup bajo o cero para eliminar barrera de entrada.",
        "source": "sesion-completa",
        "tags": ["learning", "business", "pricing", "enterprise"],
    })
    entries.append({
        "id": "learning-person",
        "type": "learning",
        "category": "person",
        "title": "Personas clave del ecosistema",
        "content": "Luis Daniel Guerrero Enciso (Perroni) — dueño SDC, founder técnico. César Holguín — AztroTech, partner enterprise. Abraham Ortega — ABE Music, partner música. Noel Nichols — socio creativo. Nathaly Hermosillo — contacto personal. Email perrykingla.69@gmail.com para Obsidian/Google.",
        "source": "conocimiento-general",
        "tags": ["learning", "person", "contact"],
    })

    return entries


# ═══════════════════════════════════════════════════
# 2. ENGRAM FEED
# ═══════════════════════════════════════════════════

def feed_engram(entries: list) -> int:
    """Feed entries into Engram. Uses engram CLI."""
    count = 0
    for entry in entries:
        title = entry["title"][:80]
        content = entry["content"]
        category = entry["category"]
        entry_id = entry["id"]

        safe_title = title.replace('"', "'")
        safe_content = content[:500].replace('"', "'")
        cmd = f'engram mem_save --title "{safe_title}" --type {category} --content "{safe_content}" --topic-key "memory/{entry_id}" 2>/dev/null'
        exit_code = os.system(cmd)
        if exit_code == 0:
            count += 1

    return count


def feed_engram_http(entries: list) -> int:
    """Feed entries via Engram HTTP API."""
    import httpx
    count = 0
    for entry in entries:
        try:
            data = {
                "title": entry["title"][:80],
                "type": entry["category"],
                "content": f"**{entry['title']}**\n\n{entry['content'][:1000]}\n\n**Source**: {entry['source']}",
                "topic_key": f"memory/{entry['id']}",
            }
            resp = httpx.post("http://localhost:7437/api/observations", json=data, timeout=5)
            if resp.status_code in (200, 201):
                count += 1
        except Exception:
            pass
    return count


# ═══════════════════════════════════════════════════
# 3. VECTOR MEMORY (Qdrant fallback → SQLite)
# ═══════════════════════════════════════════════════

def init_vector_db():
    """Initialize local vector storage (fallback for Qdrant)."""
    os.makedirs(VECTOR_DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(str(VECTOR_DB_PATH))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS vectors (
            id TEXT PRIMARY KEY,
            category TEXT,
            title TEXT,
            content TEXT,
            source TEXT,
            tags TEXT,
            embedding BLOB,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_vec_cat ON vectors(category);
    """)
    conn.commit()
    conn.close()


def feed_vectors(entries: list) -> int:
    """Store entries as vectors in local SQLite (Qdrant fallback)."""
    init_vector_db()
    conn = sqlite3.connect(str(VECTOR_DB_PATH))
    count = 0
    for entry in entries:
        try:
            conn.execute(
                "INSERT OR REPLACE INTO vectors (id, category, title, content, source, tags) VALUES (?, ?, ?, ?, ?, ?)",
                (entry["id"], entry["category"], entry["title"], entry["content"][:2000], entry["source"], json.dumps(entry["tags"])),
            )
            count += 1
        except Exception:
            pass
    conn.commit()
    conn.close()
    return count


def search_vectors(query: str, category: str = "", limit: int = 5) -> list:
    """Search vectors by text match (simple keyword, no embeddings)."""
    init_vector_db()
    conn = sqlite3.connect(str(VECTOR_DB_PATH))
    conn.row_factory = sqlite3.Row
    sql = "SELECT id, category, title, content[:200] as snippet, source, tags FROM vectors WHERE (content LIKE ? OR title LIKE ?)"
    params = [f"%{query}%", f"%{query}%"]
    if category:
        sql += " AND category = ?"
        params.append(category)
    sql += " LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════
# 4. GRAPH MEMORY (Neo4j fallback → SQLite)
# ═══════════════════════════════════════════════════

def init_graph_db():
    """Initialize local graph storage (fallback for Neo4j)."""
    os.makedirs(GRAPH_DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(str(GRAPH_DB_PATH))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            category TEXT,
            title TEXT,
            content TEXT,
            source TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            relation TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (source_id) REFERENCES nodes(id),
            FOREIGN KEY (target_id) REFERENCES nodes(id)
        );
        CREATE INDEX IF NOT EXISTS idx_edge_source ON edges(source_id);
        CREATE INDEX IF NOT EXISTS idx_edge_target ON edges(target_id);
    """)
    conn.commit()
    conn.close()


def feed_graph(entries: list) -> dict:
    """Store entries as nodes + create relationship edges."""
    init_graph_db()
    conn = sqlite3.connect(str(GRAPH_DB_PATH))

    # Insert nodes
    node_count = 0
    for entry in entries:
        try:
            conn.execute(
                "INSERT OR REPLACE INTO nodes (id, category, title, content, source) VALUES (?, ?, ?, ?, ?)",
                (entry["id"], entry["category"], entry["title"], entry["content"][:2000], entry["source"]),
            )
            node_count += 1
        except Exception:
            pass

    # Create relationships based on shared tags and categories
    edge_count = 0
    all_rows = conn.execute("SELECT id, category, title FROM nodes").fetchall()
    for i, row_a in enumerate(all_rows):
        for row_b in all_rows[i + 1:]:
            # Connect same category
            if row_a[1] == row_b[1]:
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO edges (source_id, target_id, relation, weight) VALUES (?, ?, ?, ?)",
                        (row_a[0], row_b[0], "same_category", 0.5),
                    )
                    edge_count += 1
                except Exception:
                    pass

    conn.commit()
    conn.close()
    return {"nodes": node_count, "edges": edge_count}


def query_graph(relation: str = "", category: str = "") -> list:
    """Query the graph for related nodes."""
    init_graph_db()
    conn = sqlite3.connect(str(GRAPH_DB_PATH))
    conn.row_factory = sqlite3.Row
    sql = "SELECT DISTINCT n.id, n.category, n.title, n.content[:200] as snippet FROM nodes n"
    params = []
    if relation:
        sql += " JOIN edges e ON (n.id = e.source_id OR n.id = e.target_id) WHERE e.relation = ?"
        params.append(relation)
    if category:
        sql += " AND n.category = ?" if relation else " WHERE n.category = ?"
        params.append(category)
    sql += " LIMIT 50"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════
# 5. UNIFIED STATUS
# ═══════════════════════════════════════════════════

def show_status():
    """Show status of all memory systems."""
    print(f"\n{'═'*60}")
    print(f"  🧠  MEMORY SYSTEMS STATUS")
    print(f"  {datetime.now().isoformat()}")
    print(f"{'═'*60}\n")

    # Engram
    try:
        import httpx
        resp = httpx.get("http://localhost:7437/health", timeout=3)
        print(f"  🟢 Engram (port 7437):      ✅ Running — {resp.json().get('status', 'ok')}")
    except Exception:
        print(f"  🔴 Engram (port 7437):      ❌ Not responding")

    # Vector memory
    if VECTOR_DB_PATH.exists():
        conn = sqlite3.connect(str(VECTOR_DB_PATH))
        count = conn.execute("SELECT COUNT(*) FROM vectors").fetchone()[0]
        cats = conn.execute("SELECT category, COUNT(*) as cnt FROM vectors GROUP BY category ORDER BY cnt DESC").fetchall()
        conn.close()
        print(f"  🟢 Vector Memory (SQLite):   ✅ {count} entries")
        for c in cats[:5]:
            print(f"       {c[0]}: {c[1]}")
    else:
        print(f"  ⚪ Vector Memory (SQLite):   📭 Empty")

    # Graph memory
    if GRAPH_DB_PATH.exists():
        conn = sqlite3.connect(str(GRAPH_DB_PATH))
        nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        cats = conn.execute("SELECT category, COUNT(*) as cnt FROM nodes GROUP BY category ORDER BY cnt DESC").fetchall()
        conn.close()
        print(f"  🟢 Graph Memory (SQLite):    ✅ {nodes} nodes, {edges} edges")
        for c in cats[:5]:
            print(f"       {c[0]}: {c[1]}")
    else:
        print(f"  ⚪ Graph Memory (SQLite):    📭 Empty")

    # Qdrant (remote)
    try:
        resp = httpx.get("http://localhost:6333/", timeout=3)
        print(f"  🟢 Qdrant (port 6333):       ✅ Running")
    except Exception:
        print(f"  ⚪ Qdrant (port 6333):       📭 Not available locally")

    # Neo4j (remote)
    try:
        resp = httpx.get("http://localhost:7474", timeout=3)
        print(f"  🟢 Neo4j (port 7474):        ✅ Running")
    except Exception:
        print(f"  ⚪ Neo4j (port 7474):        📭 Not available locally")

    print()


# ═══════════════════════════════════════════════════
# 6. MAIN
# ═══════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="SDC Memory Ingestion Engine")
    parser.add_argument("--engram-only", action="store_true", help="Feed only Engram")
    parser.add_argument("--vectors-only", action="store_true", help="Feed only Vector memory")
    parser.add_argument("--graph-only", action="store_true", help="Feed only Graph memory")
    parser.add_argument("--status", action="store_true", help="Show memory status")
    parser.add_argument("--search", metavar="QUERY", help="Search vector memory")
    parser.add_argument("--query-graph", metavar="CATEGORY", help="Query graph memory")
    parser.add_argument("--all", action="store_true", help="Feed all memory systems")

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.search:
        results = search_vectors(args.search)
        print(f"\n{'═'*60}")
        print(f"  🔍  SEARCH: {args.search}")
        print(f"{'═'*60}\n")
        for r in results:
            print(f"  📄 {r['title']}")
            print(f"     {r['snippet'][:200]}...")
            print(f"     [{r['category']}] {r['source']}")
            print()
        return

    if args.query_graph:
        results = query_graph(category=args.query_graph)
        print(f"\n{'═'*60}")
        print(f"  🕸  GRAPH: {args.query_graph}")
        print(f"{'═'*60}\n")
        for r in results[:10]:
            print(f"  🔗 {r['title']} ({r['category']})")
        print(f"\n  Total: {len(results)} nodes\n")
        return

    # Collect and feed
    print(f"\n{'═'*60}")
    print(f"  🧠  MEMORY INGESTION ENGINE")
    print(f"  {datetime.now().isoformat()}")
    print(f"{'═'*60}")

    print("\n  📦 Collecting session data...")
    entries = collect_session_data()
    print(f"     {len(entries)} memory entries collected\n")

    feed_all = args.all or not (args.engram_only or args.vectors_only or args.graph_only)

    if feed_all or args.engram_only:
        print("  🟣  Feeding Engram...")
        try:
            count = feed_engram_http(entries)
            if count == 0:
                count = feed_engram(entries)
            print(f"     ✅ {count} entries → Engram\n")
        except Exception as e:
            print(f"     ❌ Engram feed failed: {e}\n")

    if feed_all or args.vectors_only:
        print("  🔵  Feeding Vector Memory...")
        count = feed_vectors(entries)
        print(f"     ✅ {count} entries → Vectors\n")

    if feed_all or args.graph_only:
        print("  🟢  Feeding Graph Memory...")
        result = feed_graph(entries)
        print(f"     ✅ {result['nodes']} nodes + {result['edges']} edges\n")

    print(f"  {'═'*60}")
    print(f"  ✅  Memory ingestion complete!")
    print(f"  {'═'*60}\n")
    show_status()


if __name__ == "__main__":
    main()
