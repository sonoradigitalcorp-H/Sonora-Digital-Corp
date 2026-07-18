#!/usr/bin/env python3
"""Seed Neo4j con la arquitectura completa del sistema.

Inyecta:
- Personas (Luis Daniel, Noel, Abraham)
- Servicios (cada contenedor con sus puertos)
- Relaciones entre servicios
- Agentes y sus capacidades

Uso: python3 scripts/seed-neo4j-arquitectura.py [--recreate]
"""
import argparse
import logging
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("seed-neo4j")

BASE = Path(__file__).resolve().parent.parent

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "jarvis2026"


def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


def seed(tx, recreate: bool = False):
    if recreate:
        tx.run("MATCH (n) DETACH DELETE n")
        log.info("Database cleared")

    # ── Personas ──
    people = {
        "luis-daniel": {
            "name": "Luis Daniel Guerrero Enciso",
            "role": "dueno del sistema",
            "type": "Person",
        },
        "noel": {
            "name": "Noel Nichols",
            "role": "socio creativo colaborativo",
            "type": "Person",
        },
        "abraham": {
            "name": "Abraham Ortega",
            "role": "CEO de ABE Music",
            "type": "Person",
        },
    }

    for pid, p in people.items():
        tx.run(
            "MERGE (n:Person {id: $id}) SET n.name = $name, n.role = $role",
            id=pid, name=p["name"], role=p["role"],
        )
    log.info(f"Seeded {len(people)} persons")

    # ── Servicios ──
    services = [
        {"id": "jarvis-webui", "name": "JARVIS Web UI", "port": 5174, "type": "Service"},
        {"id": "abe-service", "name": "ABE Music OS", "port": 5180, "type": "Service"},
        {"id": "hermes-mcp", "name": "Hermes MCP Gateway", "port": 8000, "type": "Service"},
        {"id": "openclaw", "name": "OpenClaw Gateway", "port": 18789, "type": "Service"},
        {"id": "langfuse", "name": "LangFuse", "port": 3000, "type": "Service"},
        {"id": "n8n", "name": "n8n Workflows", "port": 5678, "type": "Service"},
        {"id": "qdrant", "name": "Qdrant Vector DB", "port": 6333, "type": "Database"},
        {"id": "neo4j", "name": "Neo4j Graph DB", "port": 7687, "type": "Database"},
        {"id": "redis", "name": "Redis Cache", "port": 6379, "type": "Database"},
        {"id": "postgres", "name": "PostgreSQL", "port": 5432, "type": "Database"},
        {"id": "playwright", "name": "Playwright MCP", "port": 8931, "type": "Service"},
        {"id": "telegram-bot", "name": "Telegram Bot", "port": 3003, "type": "Service"},
        {"id": "ollama", "name": "Ollama LLM", "port": 11434, "type": "AI"},
    ]

    for s in services:
        tx.run(
            "MERGE (n:Service {id: $id}) SET n.name = $name, n.port = $port, n.type = $type",
            id=s["id"], name=s["name"], port=s["port"], type=s["type"],
        )
    log.info(f"Seeded {len(services)} services")

    # ── Relaciones ──
    relationships = [
        ("luis-daniel", "OWNS", "neo4j"),
        ("luis-daniel", "OWNS", "qdrant"),
        ("luis-daniel", "OWNS", "ollama"),
        ("luis-daniel", "MANAGES", "abe-service"),
        ("noel", "COLLABORATES_ON", "abe-service"),
        ("noel", "COLLABORATES_ON", "jarvis-webui"),
        ("abraham", "USES", "abe-service"),
        ("abe-service", "DEPENDS_ON", "qdrant"),
        ("abe-service", "DEPENDS_ON", "neo4j"),
        ("abe-service", "DEPENDS_ON", "redis"),
        ("jarvis-webui", "DEPENDS_ON", "ollama"),
        ("jarvis-webui", "DEPENDS_ON", "qdrant"),
        ("jarvis-webui", "DEPENDS_ON", "neo4j"),
        ("jarvis-webui", "DEPENDS_ON", "redis"),
        ("jarvis-webui", "CONNECTS_VIA", "hermes-mcp"),
        ("hermes-mcp", "ROUTES_TO", "openclaw"),
        ("n8n", "TRIGGERS", "hermes-mcp"),
        ("telegram-bot", "NOTIFIES", "abe-service"),
        ("langfuse", "MONITORS", "ollama"),
    ]

    for src, rel, dst in relationships:
        tx.run(
            f"MATCH (a {{id: $src}}) MATCH (b {{id: $dst}}) MERGE (a)-[:{rel}]->(b)",
            src=src, dst=dst,
        )
    log.info(f"Seeded {len(relationships)} relationships")

    # ── Capabilities ──
    capabilities = [
        {"id": "acquire-metadata", "name": "Acquire Artist Metadata", "providers": 2},
        {"id": "search-artist", "name": "Search Artist", "providers": 2},
        {"id": "browse-artist", "name": "Browse Artist Profile", "providers": 4},
    ]

    for c in capabilities:
        tx.run(
            "MERGE (n:Capability {id: $id}) SET n.name = $name, n.providers = $providers",
            id=c["id"], name=c["name"], providers=c["providers"],
        )

    # ── Contar resultados ──
    result = tx.run("MATCH (n) RETURN count(n) as total, count(DISTINCT labels(n)) as label_types")
    for rec in result:
        log.info(f"Graph: {rec['total']} nodes, {rec['label_types']} label types")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--recreate", action="store_true", help="Borra todo antes de seedear")
    args = parser.parse_args()

    driver = get_driver()
    with driver.session() as session:
        session.execute_write(seed, args.recreate)
    driver.close()
    log.info("✅ Grafo del sistema listo en Neo4j")


if __name__ == "__main__":
    main()
