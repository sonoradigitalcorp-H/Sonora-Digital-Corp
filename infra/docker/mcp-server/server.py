"""
JARVIS MCP Server
Model Context Protocol server for JARVIS AI Assistant
Now with real embeddings instead of [0.0]*384 placeholders.
"""

from fastmcp import FastMCP
from typing import Optional
import json
import os
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s"
)
log = logging.getLogger("mcp.server")

# Importar clientes de servicios
try:
    from neo4j import GraphDatabase

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    from qdrant_client import QdrantClient

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

try:
    from embeddings import embed_text, EMBED_DIM

    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

# Inicializar MCP Server
mcp = FastMCP("jarvis")

# Configuración desde variables de entorno
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "jarvis2026")
QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
EMBEDDING_DIM = int(os.environ.get("EMBEDDING_DIM", "768"))  # nomic-embed-text

# Colecciones Qdrant que realmente existen
QDRANT_COLLECTIONS = [
    "conversations",
    "documents",
    "tasks",
    "jarvis_knowledge",
]

# Clientes (inicializar si están disponibles)
neo4j_driver = None
qdrant_client = None

if NEO4J_AVAILABLE:
    try:
        neo4j_driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        log.info("Neo4j driver initialized")
    except Exception as e:
        log.warning(f"Could not connect to Neo4j: {e}")

if QDRANT_AVAILABLE:
    try:
        qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        log.info("Qdrant client initialized")
    except Exception as e:
        log.warning(f"Could not connect to Qdrant: {e}")


# Rate limiter
_rate_store: dict = {}


def _check_rate_limit(key: str, max_req: int = 10, window: int = 60) -> bool:
    now = time.time()
    if key not in _rate_store:
        _rate_store[key] = []
    _rate_store[key] = [t for t in _rate_store[key] if now - t < window]
    if len(_rate_store[key]) >= max_req:
        return False
    _rate_store[key].append(now)
    return True


def _get_vector(text: str) -> list:
    """Get embedding vector for text. Falls back to zero vector."""
    if EMBEDDINGS_AVAILABLE:
        vec = embed_text(text)
        if vec:
            return vec
    log.warning(f"Using zero vector fallback for: {text[:50]}...")
    return [0.0] * EMBEDDING_DIM


@mcp.tool()
def jarvis_search(query: str, limit: int = 10) -> dict:
    """
    Buscar en la memoria de JARVIS (Neo4j + Qdrant)

    Args:
        query: Texto a buscar
        limit: Número máximo de resultados

    Returns:
        Dict con resultados de búsqueda
    """
    results = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "graph_results": [],
        "vector_results": [],
    }

    # Búsqueda en Neo4j (grafo)
    if neo4j_driver:
        try:
            with neo4j_driver.session() as session:
                # Buscar nodos que contengan el texto
                cypher = """
                MATCH (n)
                WHERE n.name CONTAINS $query OR n.text CONTAINS $query
                RETURN n LIMIT $limit
                """
                graph_results = session.run(cypher, query=query, limit=limit)
                results["graph_results"] = [dict(record) for record in graph_results]
        except Exception as e:
            results["graph_error"] = str(e)

    # Búsqueda en Qdrant (vectores) con embeddings reales
    if qdrant_client:
        try:
            vector = _get_vector(query)
            for col in QDRANT_COLLECTIONS:
                try:
                    hits = qdrant_client.search(
                        collection_name=col,
                        query_vector=vector,
                        limit=limit // len(QDRANT_COLLECTIONS) or 1,
                    )
                    for hit in hits:
                        results["vector_results"].append(
                            {
                                "collection": col,
                                "id": str(hit.id),
                                "score": round(hit.score, 4),
                                "payload": hit.payload,
                            }
                        )
                except Exception as col_err:
                    log.warning(f"Qdrant search in {col}: {col_err}")
                    continue
        except Exception as e:
            results["vector_error"] = str(e)

    return results


@mcp.tool()
def jarvis_remember(content: str, metadata: Optional[dict] = None) -> dict:
    """
    Guardar información en la memoria de JARVIS

    Args:
        content: Texto/contenido a recordar
        metadata: Metadata adicional (opcional)

    Returns:
        Dict con resultado de la operación
    """
    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "stored_in": [],
    }

    # Guardar en Neo4j
    if neo4j_driver:
        try:
            with neo4j_driver.session() as session:
                cypher = """
                CREATE (c:Conversation {
                    text: $content,
                    timestamp: datetime(),
                    metadata: $metadata
                })
                RETURN c
                """
                session.run(cypher, content=content, metadata=metadata or {})
                result["stored_in"].append("neo4j")
        except Exception as e:
            result["neo4j_error"] = str(e)
            result["status"] = "partial"

    # Guardar en Qdrant con embeddings reales
    if qdrant_client:
        try:
            vector = _get_vector(content)
            if vector:
                from qdrant_client.models import PointStruct
                import uuid

                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "text": content,
                        "metadata": metadata or {},
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                qdrant_client.upsert(
                    collection_name="jarvis_knowledge",
                    points=[point],
                )
                result["stored_in"].append("qdrant")
                log.info(f"Stored in Qdrant: {content[:60]}...")
        except Exception as e:
            result["qdrant_error"] = str(e)
            result["status"] = "partial"

    return result


@mcp.tool()
def jarvis_forget(conversation_id: str) -> dict:
    """
    Eliminar información de la memoria de JARVIS

    Args:
        conversation_id: ID de la conversación a eliminar

    Returns:
        Dict con resultado de la operación
    """
    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "deleted_from": [],
    }

    # Eliminar de Neo4j
    if neo4j_driver:
        try:
            with neo4j_driver.session() as session:
                cypher = """
                MATCH (c:Conversation)
                WHERE id(c) = $id
                DELETE c
                RETURN count(c) as deleted
                """
                session.run(cypher, id=int(conversation_id))
                result["deleted_from"].append("neo4j")
        except Exception as e:
            result["neo4j_error"] = str(e)
            result["status"] = "partial"

    # Eliminar de Qdrant por ID
    if qdrant_client:
        try:
            for col in QDRANT_COLLECTIONS:
                try:
                    qdrant_client.delete(
                        collection_name=col,
                        points_selector=[conversation_id],
                    )
                    result["deleted_from"].append(f"qdrant.{col}")
                except Exception:
                    continue
        except Exception as e:
            result["qdrant_error"] = str(e)
            result["status"] = "partial"

    return result


@mcp.tool()
def jarvis_status() -> dict:
    """
    Obtener estado del sistema JARVIS

    Returns:
        Dict con estado de todos los servicios
    """
    status = {
        "timestamp": datetime.now().isoformat(),
        "services": {"mcp_server": "running", "neo4j": "unknown", "qdrant": "unknown"},
        "capabilities": {
            "graph_search": NEO4J_AVAILABLE and neo4j_driver is not None,
            "vector_search": QDRANT_AVAILABLE and qdrant_client is not None,
            "memory_persistence": True,
        },
    }

    # Verificar Neo4j
    if neo4j_driver:
        try:
            with neo4j_driver.session() as session:
                result = session.run("RETURN 1 as test")
                if result.single():
                    status["services"]["neo4j"] = "running"
        except Exception as e:
            status["services"]["neo4j"] = f"error: {str(e)}"

    # Verificar Qdrant
    if qdrant_client:
        try:
            collections = qdrant_client.get_collections()
            status["services"]["qdrant"] = "running"
            status["qdrant_collections"] = len(collections.collections)
        except Exception as e:
            status["services"]["qdrant"] = f"error: {str(e)}"

    return status


@mcp.tool()
def jarvis_execute(command: str) -> dict:
    """
    Ejecutar comandos del sistema (con restricciones de seguridad)

    Args:
        command: Comando a ejecutar

    Returns:
        Dict con resultado del comando
    """
    import subprocess

    # Lista blanca de comandos permitidos
    ALLOWED_COMMANDS = [
        "ls",
        "pwd",
        "date",
        "whoami",
        "uptime",
        "docker ps",
        "systemctl status",
    ]

    # Verificar si el comando está permitido
    base_command = command.split()[0] if command else ""
    if base_command not in [cmd.split()[0] for cmd in ALLOWED_COMMANDS]:
        return {
            "status": "error",
            "message": f"Command not allowed: {base_command}",
            "allowed_commands": ALLOWED_COMMANDS,
        }

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=10
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Command timed out"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ===================== TOOLS EXPANDED =====================


@mcp.tool()
def jarvis_search_semantic(
    query: str,
    limit: int = 5,
    threshold: float = 0.7,
    collection: str = "jarvis_knowledge",
) -> dict:
    """
    Búsqueda semántica vectorial en la memoria de JARVIS.

    Args:
        query: Texto de búsqueda
        limit: Número máximo de resultados
        threshold: Umbral de similitud (0-1)
        collection: Colección Qdrant a buscar

    Returns:
        Resultados con score de similitud y metadata
    """
    if not qdrant_client:
        return {"status": "error", "message": "Qdrant not available"}

    try:
        vector = _get_vector(query)
        if not vector:
            return {
                "status": "error",
                "message": "Could not generate embedding for query",
            }
        results = qdrant_client.search(
            collection_name=collection,
            query_vector=vector,
            limit=limit,
            score_threshold=threshold,
        )
        return {
            "status": "success",
            "collection": collection,
            "results": [
                {"id": str(r.id), "score": r.score, "payload": r.payload}
                for r in results
            ],
            "count": len(results),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def jarvis_get_context(query: str, max_tokens: int = 2000) -> dict:
    """
    Obtener contexto relevante de la memoria para enriquecer prompts del LLM.
    Combina búsqueda en grafo + vectorial.

    Args:
        query: Query para buscar contexto
        max_tokens: Máximo de tokens en el contexto

    Returns:
        Contexto combinado de todas las fuentes
    """
    context_parts = []
    sources = {"graph": [], "vector": []}

    # Búsqueda vectorial en todas las colecciones reales
    if qdrant_client:
        vector = _get_vector(query)
        if vector:
            for col in QDRANT_COLLECTIONS:
                try:
                    results = qdrant_client.search(
                        collection_name=col, query_vector=vector, limit=2
                    )
                    for r in results:
                        context_parts.append(str(r.payload))
                        sources["vector"].append(
                            {"collection": col, "score": r.score, "payload": r.payload}
                        )
                except Exception:
                    pass

    context = "\n\n".join(context_parts) if context_parts else "No context found"

    return {
        "context": context[: max_tokens * 4],  # Approximate char-to-token ratio
        "sources": sources,
        "source_count": len(context_parts),
    }


@mcp.tool()
def jarvis_list_skills(category: str = None) -> list:
    """
    Listar skills disponibles en el sistema JARVIS.

    Args:
        category: Filtrar por categoría (opcional)

    Returns:
        Lista de skills disponibles
    """
    skills = [
        {
            "name": "search",
            "description": "Búsqueda en memoria (Neo4j)",
            "category": "memory",
        },
        {
            "name": "search_semantic",
            "description": "Búsqueda semántica (Qdrant)",
            "category": "memory",
        },
        {
            "name": "remember",
            "description": "Guardar información en memoria",
            "category": "memory",
        },
        {
            "name": "get_context",
            "description": "Obtener contexto relevante",
            "category": "memory",
        },
        {
            "name": "analyze_code",
            "description": "Análisis estático de código",
            "category": "development",
        },
        {
            "name": "web_fetch",
            "description": "Fetch de URLs con resumen",
            "category": "web",
        },
        {
            "name": "execute",
            "description": "Ejecutar comandos del sistema",
            "category": "system",
        },
        {"name": "status", "description": "Estado del sistema", "category": "system"},
    ]

    if category:
        skills = [s for s in skills if s["category"] == category]

    return skills


@mcp.tool()
def jarvis_analyze_code(file_path: str, analysis_type: str = "lint") -> dict:
    """
    Análisis estático de código.

    Args:
        file_path: Ruta del archivo a analizar
        analysis_type: Tipo de análisis (lint/security/complexity/structure)

    Returns:
        Resultados del análisis
    """
    import os
    import ast
    import statistics

    if not os.path.exists(file_path):
        return {"status": "error", "message": f"File not found: {file_path}"}

    try:
        with open(file_path) as f:
            content = f.read()

        tree = ast.parse(content)

        # Análisis básico de estructura
        functions = [
            n
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        imports = [
            n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))
        ]

        # Complejidad ciclomática básica
        complexities = []
        for func in functions:
            complexity = 1
            for node in ast.walk(func):
                if isinstance(
                    node,
                    (
                        ast.If,
                        ast.While,
                        ast.For,
                        ast.ExceptHandler,
                        ast.And,
                        ast.Or,
                        ast.Assert,
                    ),
                ):
                    complexity += 1
            complexities.append(complexity)

        return {
            "status": "success",
            "file": file_path,
            "language": "python" if file_path.endswith(".py") else "unknown",
            "metrics": {
                "lines_of_code": len(content.splitlines()),
                "functions": len(functions),
                "classes": len(classes),
                "imports": len(imports),
                "avg_complexity": (
                    round(statistics.mean(complexities), 2) if complexities else 0
                ),
                "max_complexity": max(complexities) if complexities else 0,
            },
        }
    except SyntaxError as e:
        return {"status": "error", "message": f"Syntax error: {e}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def jarvis_web_fetch(
    url: str, format: str = "markdown", max_length: int = 5000
) -> dict:
    """
    Fetch de contenido web con resumen (rate limited: 10 req/min por dominio).

    Args:
        url: URL a fetchear
        format: Formato de salida (markdown/text)
        max_length: Longitud máxima del contenido

    Returns:
        Contenido de la URL
    """
    import requests
    from urllib.parse import urlparse

    domain = urlparse(url).netloc
    if not _check_rate_limit(f"web_fetch:{domain}", max_req=10, window=60):
        return {
            "status": "error",
            "message": f"Rate limit exceeded for {domain} (10 req/min)",
        }

    try:
        resp = requests.get(
            url, timeout=10, headers={"User-Agent": "JARVIS/2.0 (AI Assistant)"}
        )
        resp.raise_for_status()

        content = resp.text[:max_length]

        return {
            "status": "success",
            "url": url,
            "status_code": resp.status_code,
            "content_type": resp.headers.get("content-type", ""),
            "content_length": len(resp.text),
            "content": content[:max_length],
        }
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    print("Starting JARVIS MCP Server...")
    print(f"Neo4j available: {NEO4J_AVAILABLE}")
    print(f"Qdrant available: {QDRANT_AVAILABLE}")
    mcp.run()
