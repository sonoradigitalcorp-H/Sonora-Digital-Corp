#!/usr/bin/env python3
"""Puente CLI/MCP para que Hermes y cualquier IA naveguen el conocimiento OKF."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okf_navigator import retrieve_context, load_concepts, get_concept, concept_context

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        print(json.dumps([c["id"] for c in load_concepts()], ensure_ascii=False))
    elif cmd == "get":
        print(concept_context(get_concept(sys.argv[2])))
    elif cmd == "query":
        print(json.dumps(retrieve_context(sys.argv[3], sys.argv[2]), ensure_ascii=False))
    else:
        print("Uso: okf_mcp.py [list|get <id>|query <Tenant> '<pregunta>']")
