"""
JARVIS Graph Builder — Entity extraction and relationship linking.
Extracts entities from messages and links them in Neo4j knowledge graph.
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional

log = logging.getLogger("jarvis.graph")

ENTITY_PATTERNS = {
    "technology": r"\b(Python|JavaScript|TypeScript|Rust|Go|Java|Kotlin|Swift|C\+\+|C#|PHP|Ruby|React|Vue|Angular|Svelte|Next\.?js|Node\.?js|Deno|Bun|Django|Flask|FastAPI|Spring|Laravel|Rails|Docker|Kubernetes|Terraform|AWS|GCP|Azure|Neo4j|Qdrant|Redis|PostgreSQL|MySQL|MongoDB|GraphQL|REST|gRPC|WebSocket|MCP|LLM|OpenAI|Claude|Gemini|DeepSeek|Ollama|LangChain|LlamaIndex|Haystack)\b",
    "concept": r"\b(arquitectura|patr[oó]n|diseño|API|base de datos|algoritmo|protocolo|framework|librer[ií]a|servicio|microservicio|contenedor|orquestador|evento|streaming|cache|escalabilidad|seguridad|autenticación|autorización|worker|col[aá]|webhook|SSE|RESTful|serverless|edge|cloud|híbrido|monolito|funcionalidad|implementación|despliegue|migración|refactor|deuda técnica|cobertura|integración|entrega continua|CI/CD|DevOps)\b",
    "person": r"@\w+",
    "project": r"\b(proyecto|app|sistema|módulo|componente)\s+(\w+)\b",
}

RELATION_PATTERNS = [
    (r"\b(usa|utiliza|implementa|corre\s*con|built\s*with)\b", "USES"),
    (r"\b(depende\s*de|requires|necesita)\b", "DEPENDS_ON"),
    (r"\b(extiende|hereda|extends|based\s*on)\b", "EXTENDS"),
    (r"\b(comunica\s*con|interactúa\s*con|connect|talks\s*to)\b", "COMMUNICATES_WITH"),
    (r"\b(reemplaza|sustituye|replaces|migrates\s*from)\b", "REPLACES"),
    (r"\bes\s*(parte\s*de|componente\s*de)\b", "PART_OF"),
]

EXTRACTION_PROMPT = """Extrae entidades y relaciones de este texto en español.
Devuelve SOLO JSON válido con este formato exacto:
{{"entities": [{{"name": "...", "type": "technology|concept|person|project", "context": "..."}}], "relationships": [{{"source": "...", "target": "...", "type": "RELATION_TYPE"}}]}}

Si no hay entidades, devuelve {{"entities": [], "relationships": []}}.

Texto: {text}"""


def extract_entities_local(text: str) -> List[Dict[str, str]]:
    entities = []
    seen = set()
    for etype, pattern in ENTITY_PATTERNS.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(0).strip().lower()
            if name not in seen and len(name) > 1:
                seen.add(name)
                entities.append(
                    {
                        "name": match.group(0),
                        "type": etype,
                        "context": text[
                            max(0, match.start() - 40) : match.end() + 40
                        ].strip(),
                    }
                )
    return entities


def extract_relations_local(
    text: str, entities: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    relations = []
    ent_names = [e["name"].lower() for e in entities]
    text_lower = text.lower()
    for pattern, rel_type in RELATION_PATTERNS:
        for match in re.finditer(pattern, text_lower):
            pre = text[: match.start()]
            post = text[match.end() :]
            source = None
            target = None
            for name in ent_names:
                if name in pre.lower():
                    source = name
                if name in post.lower():
                    target = name
            if source and target and source != target:
                relations.append(
                    {
                        "source": source.title(),
                        "target": target.title(),
                        "type": rel_type,
                    }
                )
    return relations


def extract_with_llm(text: str, llm_client) -> Dict[str, Any]:
    try:
        from src.core.llm import ask

        prompt = EXTRACTION_PROMPT.format(text=text[:4000])
        result = ask(prompt)
        cleaned = re.sub(r"```(?:json)?\s*", "", result).strip()
        parsed = json.loads(cleaned)
        entities = parsed.get("entities", [])
        relationships = parsed.get("relationships", [])
        return {"entities": entities, "relationships": relationships, "source": "llm"}
    except Exception as e:
        log.warning(f"LLM extraction failed: {e}, falling back to local")
        entities = extract_entities_local(text)
        relationships = extract_relations_local(text, entities)
        return {"entities": entities, "relationships": relationships, "source": "local"}


def store_in_neo4j(
    entities: List[Dict[str, str]], relationships: List[Dict[str, str]], neo4j_store
):
    if not neo4j_store:
        log.warning("Neo4j not available, skipping graph storage")
        return False
    try:
        driver = neo4j_store.get_driver()
        if not driver:
            return False
        with driver.session() as session:
            for ent in entities:
                session.run(
                    """
                    MERGE (e:Concept {name: $name})
                    SET e.type = $type, e.updated_at = datetime()
                    """,
                    name=ent["name"].lower(),
                    type=ent.get("type", "concept"),
                )
            for rel in relationships:
                session.run(
                    """
                    MATCH (a:Concept {name: $source})
                    MATCH (b:Concept {name: $target})
                    MERGE (a)-[r:RELATED {type: $rel_type}]->(b)
                    SET r.updated_at = datetime()
                    """,
                    source=rel["source"].lower(),
                    target=rel["target"].lower(),
                    rel_type=rel.get("type", "RELATED"),
                )
        log.info(
            f"Stored {len(entities)} entities and {len(relationships)} relationships in Neo4j"
        )
        return True
    except Exception as e:
        log.warning(f"Neo4j graph store error: {e}")
        return False


def query_related(
    concept_name: str, neo4j_store, depth: int = 2
) -> List[Dict[str, Any]]:
    try:
        driver = neo4j_store.get_driver()
        if not driver:
            return []
        with driver.session() as session:
            result = session.run(
                """
                MATCH (c:Concept {name: $name})-[r:RELATED*1..$depth]-(related)
                RETURN DISTINCT related.name as name, related.type as type
                LIMIT 50
                """,
                name=concept_name.lower(),
                depth=depth,
            )
            return [
                {"name": record["name"], "type": record["type"]}
                for record in result
                if record["name"]
            ]
    except Exception as e:
        log.warning(f"Graph query error: {e}")
        return []


def process_message(message: str, neo4j_store, use_llm: bool = True) -> Dict[str, Any]:
    if use_llm:
        extraction = extract_with_llm(message, None)
    else:
        entities = extract_entities_local(message)
        relationships = extract_relations_local(message, entities)
        extraction = {
            "entities": entities,
            "relationships": relationships,
            "source": "local",
        }
    stored = store_in_neo4j(
        extraction["entities"], extraction["relationships"], neo4j_store
    )
    return {**extraction, "stored": stored}
