#!/usr/bin/env python3
"""MCP Tool: unified_brain_query — accessible from Hermes, JARVIS, OpenClaw"""
import json
import sys
from apps.brain.service import BrainService

def unified_brain_query(search_text: str, type_filter: str = None, mode: str = "auto", limit: int = 10):
    brain = BrainService()
    results = []
    mode_used = mode

    try:
        with brain.neo4j.session() as s:
            cypher = """
                MATCH (n:Knowledge)
                WHERE n.summary CONTAINS $search OR n.label CONTAINS $search
                {type_clause}
                RETURN n.id as id, n.type as type, n.label as label,
                       n.summary as summary, n.source as source
                LIMIT $limit
            """
            tc = "AND n.type = $type_filter" if type_filter else ""
            cypher = cypher.replace("{type_clause}", tc)
            params = {"search": search_text, "limit": limit}
            if type_filter:
                params["type_filter"] = type_filter

            for record in s.run(cypher, **params):
                results.append({
                    "id": record["id"],
                    "type": record["type"],
                    "label": record["label"],
                    "summary": record["summary"],
                    "source": record["source"],
                    "score": 1.0,
                })

        if not results:
            # Fallback to Qdrant semantic search
            try:
                search_result = brain.qdrant.search(
                    collection_name="brain-knowledge",
                    query_vector=[0.0] * 384,
                    limit=limit,
                )
                for point in search_result:
                    if point.payload:
                        results.append({
                            "id": point.payload.get("id", ""),
                            "type": point.payload.get("type", ""),
                            "label": point.payload.get("label", ""),
                            "summary": point.payload.get("summary", ""),
                            "source": point.payload.get("source", ""),
                            "score": point.score,
                        })
            except Exception:
                pass

    finally:
        brain.close()

    return {"results": results[:limit], "total": len(results), "mode_used": mode_used}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = unified_brain_query(" ".join(sys.argv[1:]))
        print(json.dumps(result, indent=2, default=str))
